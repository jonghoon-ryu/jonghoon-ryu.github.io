---
layout: default
title: 재구성 크래시 버그 — DRAM 캐시 대기열의 이중 소유권
permalink: /ftl-visual-simulator/reference/reconfigure-crash-bug/
---
<style>
table.plan-calendar {
  width: 100% !important;
  table-layout: fixed !important;
  border-collapse: collapse;
  font-size: 0.85rem;
  margin: 1rem 0;
}
table.plan-calendar th, table.plan-calendar td {
  border: 1px solid #ddd;
  padding: 6px 10px;
  text-align: left;
  overflow-wrap: break-word;
  word-break: break-word;
}
table.plan-calendar th {
  background: #f5f5f5;
  color: #333;
}
pre {
  background: #f5f5f5;
  padding: 12px 14px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.85rem;
}
</style>

# 재구성 크래시 버그 — DRAM 캐시 대기열의 이중 소유권

Session 9("GC 시연" 프리셋을 실제 엔진에 연동하려고 워크로드를 크게 튜닝하던 중)에 원본 MQSim 코드에서 **힙 use-after-free(해제된 메모리 참조) 버그**를 발견했다. [MQSim 버그 헌트](/ftl-visual-simulator/reference/mqsim-bug-hunt/)의 이식성 버그들과도, [마모 평준화 버그](/ftl-visual-simulator/reference/wl-bug-deviation/)와도 성격이 다르다 — 이번 건 **"시뮬레이션이 끝까지 다 돌기 전에 중간에 정리(teardown)하면" 크래시하는 버그**다. 이 문서는 발견 경위, 정확한 원인, 왜 지금까지 아무도 이 버그에 부딪힌 적이 없는지, 그리고 어떻게 고쳤는지를 기록한다.

<div style="margin-top: 60px;"></div>

## 1. 어쩌다 발견했나

Session 8까지는 "매핑 기본" 프리셋 하나만 실제 엔진에 연동돼 있었는데, 이 워크로드는 `Stop_Time`이 아주 작게 설정돼 있어서(원래 목적: 매핑 테이블을 몇 스텝 안에 바로 보여주기) 항상 요청 6개만 생성되고 **항상 끝까지 다 처리된 뒤에** 멈춘다. 즉 이 프리셋만 갖고는 "실행 도중에 멈춘 상태"를 한 번도 만들어본 적이 없었다.

Session 9에서 "GC 시연" 프리셋을 만들려고 블록 개수를 8~16개로 줄이고 워크로드 요청 수를 수백 개로 늘려서(GC가 실제로 발동하려면 블록이 거의 다 차야 한다 — 3절 참고) 네이티브 CLI로 직접 돌려봤더니:

```
MQSim finished at ...
Writing results to output file .......
Flow ... - total requests generated: 48 total requests serviced: 44
Segmentation fault (core dumped)
```

**시뮬레이션 자체는 정상적으로 끝나고 결과 파일도 다 쓴 뒤에, 프로세스 종료 직전(객체 소멸자들이 실행되는 동안) 크래시**했다. 결과에는 영향이 없지만, 이 프로젝트의 WASM 바인딩(`bindings.cpp`)은 사용자가 파라미터를 바꾸거나 재생하다 멈출 때마다 정확히 이 코드 경로(`Finalize_scenario()`)를 반복 호출하므로 — 브라우저에서는 "결과 파일을 쓰고 조용히 종료"가 아니라 "그 자리에서 다시 씀직한" 상황이 될 수 있었다.

<div style="margin-top: 60px;"></div>

## 2. 원인 확정 — AddressSanitizer

Segfault만으로는 정확한 위치를 알 수 없어서, 엔진을 AddressSanitizer(`-fsanitize=address`)를 켜서 디버그 빌드로 다시 컴파일해 재현했다.

```
==ERROR: AddressSanitizer: heap-use-after-free
READ of size 8 ...
    #0 std::_List_base<NVM_Transaction*>::_M_clear()
    #1 ... ~User_Request()
    #3 SSD_Components::Input_Stream_NVMe::~Input_Stream_NVMe()
    ...
    #12 SSD_Device::~SSD_Device()
    #13 MQSim_Interface::Finalize_scenario(...)

freed by thread T0 here:
    #1 SSD_Components::Data_Cache_Manager_Flash_Advanced::~Data_Cache_Manager_Flash_Advanced()
    #3 SSD_Device::~SSD_Device()
```

`SSD_Device`의 소멸자(`SSD_Device.cpp`)를 보면 멤버들을 이 순서로 지운다:

```cpp
SSD_Device::~SSD_Device()
{
	...
	delete this->Cache_manager;      // ← 먼저
	delete this->Host_interface;     // ← 나중
}
```

`Cache_manager`(=`Data_Cache_Manager_Flash_Advanced`)가 먼저 지워지면서 어떤 `User_Request*`를 `delete`하는데, **그 객체를 `Host_interface`(=`Input_Stream_NVMe`)가 여전히 자기 리스트에 들고 있다가**, 나중에 자기 차례가 되어 소멸자를 돌리면서 이미 죽은 메모리를 또 건드린다.

<div style="margin-top: 60px;"></div>

## 3. 왜 두 곳이 같은 객체를 들고 있었나

`User_Request`는 NVMe 쓰기 요청이 도착하면 `Request_Fetch_Unit_NVMe::Process_pcie_read_message()`에서 `new`로 딱 한 번 생성된다. 이 객체를 참조하는 곳은 정상적으로는 **한 곳뿐이어야** 한다 — 만든 사람(`Input_Stream_NVMe`)이 끝까지 들고 있다가 완전히 처리되면 자기가 지운다.

문제는 DRAM 캐시가 꽉 찼을 때다. `Data_Cache_Manager_Flash_Advanced`는 캐시에 자리가 날 때까지 요청을 `waiting_user_requests_queue_for_dram_free_slot`라는 자기 대기열에 "잠깐 세워둔다":

```cpp
// 정상 흐름 - Process_dram_execution_list() 안, DRAM 이 비면:
waiting_user_requests_queue_for_dram_free_slot[sharing_id].erase(user_request++);
// → erase 만 하지 delete 는 안 함. 소유권은 계속 Input_Stream_NVMe 에 있다는 뜻.
```

그런데 이 클래스의 **소멸자**는 달랐다:

```cpp
// 수정 전 - Data_Cache_Manager_Flash_Advanced.cpp
for (auto &req : waiting_user_requests_queue_for_dram_free_slot[0]) {
	delete req;   // ← 자기가 만들지도, 소유하지도 않은 객체를 지움
}
```

평상시(`erase`)에는 소유권을 안 가져가다가, **소멸자에서만 갑자기 자기 것인 양 `delete`**해버린 것 — 그것도 `Input_Stream_NVMe`가 그 객체를 여전히 참조 중인 상태에서. 시뮬레이션이 끝까지 돌아서 모든 요청이 이 대기열을 완전히 빠져나간 뒤라면 이 루프는 그냥 빈 리스트를 돌아서 아무 일도 안 생긴다 — **DRAM이 꽉 차서 이 대기열에 뭔가 남아있는 채로 소멸자가 불릴 때만** 터지는 이중 소유권 버그였다.

<div style="margin-top: 60px;"></div>

## 4. 왜 지금까지 아무도 못 봤나

MQSim은 2018년부터 여러 연구에서 쓰인 도구인데 왜 이런 버그가 지금까지 살아있었는지 확인해봤다. 답은 간단했다 — **원본 CLI(`main.cpp`)는 이 코드 경로를 절대 만들지 않는다.**

```cpp
// main.cpp
MQSim_Interface::Run_to_completion(instance);  // 큐가 완전히 빌 때까지 무조건 다 돈다
...
MQSim_Interface::Finalize_scenario(instance);  // 그 다음에야 정리
```

`Run_to_completion()`은 이벤트 큐가 완전히 빌 때까지 멈추지 않고 도는 함수라, **모든 요청이 반드시 끝까지 처리되고 대기열에서 다 빠져나온 뒤에만** `Finalize_scenario()`가 호출된다. 즉 stock MQSim을 배치 실행(설정 파일 주고 결과 기다리는 방식)으로 쓰는 한, `waiting_user_requests_queue_for_dram_free_slot`가 비어있지 않은 채로 소멸자가 불릴 일이 **원천적으로 없다.**

이 프로젝트의 WASM UI는 다르다 — 재생/일시정지/스텝/파라미터 변경(재구성) 같은 **인터랙티브 컨트롤**을 만들면서, `step()`을 몇 번만 부르고 멈추거나, 다 끝나기 전에 `configure()`로 새 설정을 밀어 넣는(=`Finalize_scenario()` 호출) 상황을 처음으로 만들어냈다. 이런 사용 패턴 자체가 원본 CLI에는 없었기 때문에, 이 버그도 지금까지 아무에게도 발견되지 않았던 것으로 보인다.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th></th><th>MQSim 버그 헌트(4개)</th><th>마모평준화 버그(2개)</th><th>이 문서의 버그</th></tr>
<tr><td>성격</td><td>이식성 버그(WASM 전용)</td><td>로직 버그(트리거 조건 계산)</td><td>메모리 안전성 버그(소유권)</td></tr>
<tr><td>네이티브 CLI로 재현되는가</td><td>아니오 (WASM 전용)</td><td>예 (계산은 항상 틀림)</td><td>예 (ASan으로 확인)</td></tr>
<tr><td>왜 안 보였나</td><td>네이티브/WASM 라이브러리 차이</td><td>짧은 워크로드에서는 영향이 안 드러남</td><td>CLI가 항상 완주 후에만 정리하기 때문</td></tr>
<tr><td>이 프로젝트가 처음 겪은 이유</td><td>WASM 컴파일을 처음 시도</td><td>-</td><td>인터랙티브(일시정지/재구성) UI를 처음 만듦</td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 5. 수정

`Data_Cache_Manager_Flash_Advanced`의 소멸자에서 `waiting_user_requests_queue_for_dram_free_slot`에 남은 항목을 `delete`하던 두 곳(SHARED / EQUAL_PARTITIONING 모드)을 제거했다 — 그냥 리스트만 정리하고, 객체 자체는 원래 주인인 `Input_Stream_NVMe`/`Input_Stream_SATA`의 소멸자(`Waiting_user_requests`를 순회하며 `delete`)가 처리하도록 맡긴다.

```cpp
// 수정 후
case SSD_Components::Cache_Sharing_Mode::SHARED:
{
	delete per_stream_cache[0];
	while (dram_execution_queue[0].size()) {
		delete dram_execution_queue[0].front();
		dram_execution_queue[0].pop();
	}
	// waiting_user_requests_queue_for_dram_free_slot 는 여기서 delete 하지 않음
	break;
}
```

(`dram_execution_queue`는 다른 얘기다 — 여기 담기는 `Memory_Transfer_Info`는 캐시 매니저가 직접 `new`한, 진짜 자기 소유 객체라 그대로 `delete`하는 게 맞다. 문제는 오직 `User_Request*`를 담는 대기열 하나였다.)

<div style="margin-top: 60px;"></div>

## 6. 검증

- **회귀 테스트**: `npm run test:engine`의 golden 시나리오 3개 모두 수정 전/후 결과 완전 동일 — 이 수정은 정리(teardown) 시점의 메모리 해제 순서만 바꿀 뿐, 시뮬레이션이 실제로 계산하는 값에는 전혀 관여하지 않는다(결과는 이미 `Finalize_scenario()` 호출 전에 다 계산·기록됨).
- **크래시 재현 테스트**: `Load_workload → Initialize_scenario → Run_step 을 N번만 → Finalize_scenario`를 그대로 흉내내는 작은 테스트 하니스를 만들어, 수정 전에는 다음 조건에서 **항상** 크래시했다:
  - 기본 "매핑 기본" 지오메트리(32 block)도 워크로드를 키우면(20스텝 이상) 크래시 — GC나 작은 블록 수와 무관한 **일반적인** 버그였다.
  - "GC 시연"용으로 튜닝한 작은 지오메트리(8 block)는 더 적은 스텝에서부터 크래시.
- 수정 후에는 같은 테스트를 스텝 20~800까지, WRITE_CACHE 를 켠 채로 돌려도 **한 번도 크래시하지 않았다.**

<div style="margin-top: 60px;"></div>

## 7. 요약

- **수정해서 유지한다.** 롤백하지 않는다 — 메모리 안전성 문제라 이견의 여지가 없다.
- upstream MQSim 자체의 버그이고, 커밋된 golden 시나리오에는 영향이 없다(항상 완주하는 배치 실행이라 애초에 이 코드 경로를 안 탐).
- 이 프로젝트처럼 **일시정지·재구성 같은 인터랙티브 컨트롤을 얹는 순간부터** 실제 위험이 된다 — Session 9 파라미터 패널, 그리고 앞으로 만들 GC/마모평준화 시연 프리셋 모두 이 수정이 없으면 크래시할 수 있었다.

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [MQSim 버그 헌트](/ftl-visual-simulator/reference/mqsim-bug-hunt/), [마모 평준화 버그와 동작 변경](/ftl-visual-simulator/reference/wl-bug-deviation/)
- [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) — Session 9
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — 실제 코드
