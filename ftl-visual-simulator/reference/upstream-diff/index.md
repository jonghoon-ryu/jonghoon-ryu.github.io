---
layout: default
title: 원본 MQSim 대비 변경 사항 — 코드 비교
permalink: /ftl-visual-simulator/reference/upstream-diff/
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

# 원본 MQSim 대비 변경 사항 — 코드 비교

이 프로젝트의 시뮬레이션 엔진은 [MQSim](https://github.com/CMU-SAFARI/MQSim) C++ 원본을 그대로 가져와(vendoring) WebAssembly 로 컴파일한 것이다. 이 문서는 **처음 가져온 원본**과 **지금 이 프로젝트의 엔진**을 파일 단위로 비교해서, 무엇이 왜 바뀌었는지를 종류별로 정리한다. 특히 원본 코드에 있던 버그는 "원본이 어떻게 되어 있었고, 무엇이 틀렸고, 어떤 증상으로 드러났고, 어떻게 고쳤는지"를 한곳에 모아 설명한다.

버그 하나하나의 발견 경위와 디버깅 과정은 [버그 목록](/ftl-visual-simulator/reference/bug-list/)의 각 문서에 있다 — 이 문서는 그 버그들을 **코드 변경의 관점에서** 다시 묶은 것이고, 버그가 아닌 변경(계측 hook, 라이브러리화, 의도적 동작 변경, 새 기능)까지 포함한 전체 그림이다.

<div style="margin-top: 60px;"></div>

## 1. 비교 기준

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>항목</th><th>내용</th></tr>
<tr><td>원본</td><td>앱 저장소의 첫 커밋 <code>90b0fb1</code>(2026-09-05) 에 들어간 <code>engine/mqsim/src</code> — upstream MQSim 을 수정 없이 그대로 복사한 상태</td></tr>
<tr><td>현재</td><td>2026-09-24 기준 <code>dd8746d</code></td></tr>
<tr><td>규모</td><td><code>engine/mqsim/src</code> 39개 파일, <b>+2,579 / −432 줄</b> (그중 약 800줄은 새 파일 <code>MQSim_Interface.*</code>, <code>Simulation_Events.*</code>, <code>wasm/bindings.cpp</code>). 테스트는 별도로 <code>engine/tests</code> 9개 파일 +2,173 줄</td></tr>
<tr><td>직접 비교하는 법</td><td><code>git diff 90b0fb1..HEAD -- engine/mqsim/src</code> (앱 저장소에서). 코드 안의 변경 지점에는 <code>BUG FIX (this project, upstream MQSim)</code>, <code>DEVIATION FROM UPSTREAM MQSim</code>, <code>SCALE TWEAK</code>, <code>Not in upstream MQSim</code> 주석이 달려 있어 <code>grep</code> 으로 찾을 수 있다</td></tr>
</table>
</div>

**결과가 바뀌었는지를 어떻게 아나** — upstream MQSim 이 함께 배포하는 샘플 시나리오 3개를 네이티브로 돌린 결과를 9/6 에 "골든" 파일로 저장해두고(`npm run test:engine`), 이후의 모든 엔진 변경마다 결과를 **바이트 단위로** 비교했다. 골든 파일은 그 뒤로 한 번도 다시 만들지 않았다. 그래서 아래에서 "골든 불변"이라고 적은 변경은, 적어도 upstream 샘플 시나리오 3개에 대해서는 원본과 결과가 완전히 같다는 뜻이다. (단, 샘플 시나리오는 block 수가 수천 개인 큰 구성이라, 작은 데모 규모에서만 드러나는 경로는 이 테스트로 가려지지 않는다 — 그런 경우는 따로 적었다.)

<div style="margin-top: 60px;"></div>

## 2. 한눈에 보기 — 종류별 요약

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>종류</th><th>개수</th><th>시뮬레이션 결과에 영향</th><th>주로 바뀐 파일</th></tr>
<tr><td>A. 원본의 버그 수정</td><td>28개(버그 목록표) + 표에 따로 없는 수정 4건</td><td>대부분 골든 불변. 작은 규모·특정 설정에서만 결과가 달라짐(원래는 크래시/멈춤/잘못된 값)</td><td><code>GC_and_WL_Unit_*</code>, <code>Address_Mapping_Unit_Page_Level</code>, <code>Flash_Block_Manager*</code>, <code>TSU_*</code>, <code>NVM_PHY_ONFI_NVDDR2</code>, <code>utils/</code></td></tr>
<tr><td>B. 의도적으로 upstream 과 다르게 바꾼 동작</td><td>4건</td><td>있음 — 데모 규모에서 원본 동작이 의미가 없거나 멈추는 경우만</td><td><code>GC_and_WL_Unit_Base</code>, <code>Flash_Block_Manager_Base</code>, <code>Address_Mapping_Unit_Page_Level</code></td></tr>
<tr><td>C. 데모 규모 튜닝</td><td>1건</td><td>있음(의도)</td><td><code>SSD_Device.cpp</code></td></tr>
<tr><td>D. 새 기능 (upstream 에 없음)</td><td>2건 + 통계/조회 추가</td><td>없음(기본값 꺼짐) — 앱이 켤 때만</td><td><code>GC_and_WL_Unit_Page_Level</code>, <code>Device_Parameter_Set</code></td></tr>
<tr><td>E. 시각화를 위한 계측·라이브러리화·WASM</td><td>새 파일 3개 + 여러 hook</td><td>없음(골든 불변)</td><td><code>MQSim_Interface.*</code>, <code>Simulation_Events.*</code>, <code>wasm/bindings.cpp</code>, <code>main.cpp</code>, <code>sim/Engine.cpp</code></td></tr>
<tr><td>F. 테스트</td><td>골든 3개 + GMock 유닛 14개</td><td>—</td><td><code>engine/tests/</code></td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 3. A — 원본의 버그 수정

번호는 [버그 목록표](/ftl-visual-simulator/reference/bug-list/table/)와 같다. 성격이 비슷한 것끼리 7묶음으로 나눴다.

<div style="margin-top: 40px;"></div>

### A1. 이식성·메모리 안전성 — "같은 코드가 네이티브와 WASM 에서 다르게 돈다"

MQSim 원본은 리눅스 네이티브 CLI 한 번 실행(설정 읽기 → 끝까지 실행 → 결과 쓰기 → 종료)만 가정하고 만들어졌다. 이 프로젝트는 같은 코드를 WASM 으로 컴파일하고, 한 프로세스 안에서 여러 번 설정을 바꿔 다시 만들고, 중간에 멈춘다. 그 두 가지가 원본이 한 번도 밟지 않은 경로를 드러냈다.

- **#1 RNG 정수 오버플로우** (`utils/CMRRandomGenerator.h`) — 난수 생성기(MRG32k3a 계열)의 행렬 곱 `mm_mul`/`mv_mul` 이 `a[i][j] * u[j]` 를 부호 있는 `int64_t` 로 계산했다. 두 값이 각각 2³² 가까이 될 수 있어 곱이 `INT64_MAX` 를 넘는데, 부호 있는 정수 오버플로우는 C++ 표준상 undefined behavior 라 컴파일러(g++ vs Emscripten/clang)마다 다른 값을 냈다. (m−1)² 가 안전하게 들어가는 `uint64_t` 로 누적하도록 고쳤다.
- **#2 소멸자가 virtual 이 아닌 6개 베이스 클래스** (`NVM_Transaction`, `NVM_Firmware`, `NVM_PHY_Base`, `NVM_Channel_Base`, `IO_Flow_Base`, `GC_and_WL_Unit_Base`) — 파생 객체를 베이스 포인터로 `delete` 하는데(예: 모든 flash 트랜잭션은 `NVM_Transaction_Flash*` 로 지워짐) 베이스 소멸자가 virtual 이 아니었다. 표준상 UB 이고, 파생 소멸자가 안 불리며 `operator delete` 에 틀린 크기가 넘어간다. AddressSanitizer 가 `new-delete-type-mismatch` 로 확인해줬고, 실제로 Emscripten 의 할당기에서만 상태를 망가뜨렸다. `virtual ~…() {}` 추가.
- **#3 `IO_Flow_Synthetic` 의 초기화 안 된 포인터** (`host/IO_Flow_Synthetic.h`) — 소멸자가 `RandomGenerator*` 6개를 무조건 `delete` 하는데, 그중 4개는 생성자에서 조건이 맞을 때만 `new` 된다. 조건이 안 맞으면 쓰레기 값 포인터를 지우다가 SEGV. #2 를 고치자 파생 소멸자가 처음으로 실제 호출되면서 드러났다. 전부 `= nullptr` 로 초기화.
- **#4 `std::multimap::find()` 에 대한 잘못된 가정 — 네이티브/WASM 결과 차이의 근본 원인** (`Address_Mapping_Unit_Page_Level.cpp`, 매핑 page 읽기 완료 처리) — 원본은 `find(key)` 로 찾은 위치부터 앞으로만 걸으며 같은 key 를 처리했다. 하지만 표준은 `find()` 가 같은 key 중 **아무거나** 돌려준다고만 보장한다. libstdc++(네이티브)는 맨 앞 것을, libc++(WASM)는 중간 것을 돌려줘서, WASM 에서는 그 앞의 대기 쓰기들이 영원히 처리되지 않았다. `equal_range()` 로 같은 key 전체를 돌도록 고쳤다.
- **#7 DRAM 캐시 대기열의 use-after-free** (`Data_Cache_Manager_Flash_Advanced.cpp` 소멸자) — DRAM 이 가득 차서 기다리는 요청(`User_Request`)을 캐시 매니저 소멸자가 `delete` 했는데, 그 객체의 진짜 주인인 입력 스트림도 자기 소멸자에서 또 지웠다(이중 소유). 원본 CLI 는 항상 끝까지 실행한 뒤 종료해서 대기열이 비어 있으니 한 번도 안 터졌지만, 실행 도중에 설정을 바꾸는 순간 크래시. 캐시 매니저는 목록만 비우고 삭제는 주인에게 맡기도록 수정.
- **#8 초기화 안 된 `Bandwidth` 필드** (`exec/IO_Flow_Parameter_Set.h`) — `BANDWIDTH` 생성기에서만 쓰는 값이라 XML 에 태그가 없으면 초기화되지 않는다. 새 프로세스에서는 우연히 0 이라 괜찮았지만, 같은 프로세스에서 재구성을 반복하면 이전 힙 값이 남아 `Host_System.cpp` 의 나눗셈이 0 으로 나누기가 됐다. 기본값 0 을 명시.
- **(표에 없음) 주소 분할 유닛의 static 카운터가 재설정 안 됨** (`utils/Logical_Address_Partitioning_Unit.cpp`) — `Reset()` 이 `total_pda_no`/`total_lha_no` 를 0 으로 되돌리지 않아, 한 프로세스에서 두 번째 시뮬레이션을 만들면 이전 값이 누적됐다. 원본은 프로세스당 한 번만 실행하니 무관했던 문제. `Reset()` 에 두 줄 추가.

<div style="margin-top: 40px;"></div>

### A2. 설정값이 엔진까지 전달되지 않음

- **#9 마모평준화 설정 3개가 무시됨** (`exec/SSD_Device.cpp`) — XML 에서 `Dynamic_Wearleveling_Enabled`, `Static_Wearleveling_Enabled`, `Static_Wearleveling_Threshold` 를 정상적으로 읽어놓고는, GC/WL 유닛 생성자에 **넘기지 않았다**. 그래서 생성자의 컴파일 타임 기본값(true, true, 100)이 항상 쓰였다. upstream 예제들이 우연히 같은 값(100)을 써서 티가 안 났고, 이 프로젝트가 threshold 를 1 로 바꿔봤는데도 전혀 반응이 없어서 발견. 세 인자를 전달하도록 수정.

<div style="margin-top: 40px;"></div>

### A3. 빌드/링크

- **#10 `.cpp` 에만 붙은 `inline`** (`GC_and_WL_Unit_Base.cpp`) — 헤더에는 없는 `inline` 이 두 protected 메서드 정의에 붙어 있어, 다른 파일에서 부르면 링크 에러가 났다. 원본에서는 같은 파일 안에서만 불려서 문제가 없었고, 유닛 테스트가 처음으로 밖에서 불렀다. `inline` 제거 — 동작은 완전히 동일.

<div style="margin-top: 40px;"></div>

### A4. GC victim(청소 대상) 선정

GC 는 "다 쓴(full) block 중에서, 지금 쓰기 중이 아니고(write frontier 아님), 진행 중인 쓰기가 없는" 안전한 block 을 골라야 한다. 원본의 선정 코드는 정책마다 이 확인이 조금씩 빠져 있었다. 수천 개 block 규모에서는 대부분의 block 이 안전해서 거의 드러나지 않지만, 작은 규모에서는 바로 크래시·무한 루프·멈춤이 된다.

- **#11 GC 이동 쓰기의 "진행 중 쓰기" 카운트 누락** (`Flash_Block_Manager.cpp`, `GC_and_WL_Unit_Base.cpp`) — 사용자 쓰기·매핑 쓰기 할당 함수는 page 를 할당하면서 그 block 의 `Ongoing_user_program_count` 를 올리는데, GC 이동 쓰기 할당 함수만 올리지 않았다. 그래서 GC 가 옮겨 넣는 중인 block 을 다른 GC 가 "진행 중 쓰기 없음"으로 보고 victim 으로 골라 크래시(자기 자신과의 경쟁). 할당 시 올리고, GC 쓰기 완료 시 내리도록 짝을 맞췄다.
- **#12 RGA 후보 탐색 루프에 반복 상한 없음** — 안전한 후보가 하나도 없으면 무작위 추첨을 영원히 반복했다(멀티 칩 + block 8개에서 실제 재현). 상한을 두고, 후보가 없으면 이번 GC 기회를 건너뛴다.
- **#13 RGA 가 다 안 쓴 block 도 후보로 뽑음** — RANDOM_P/RANDOM_PP 는 "다 쓴 block 인가"를 확인하는데 RGA 만 빠져 있어, 빈 block 이 뽑히면 청소할 게 없어서 GC 기회를 낭비했다. 같은 조건 추가.
- **(표에 없음) GREEDY 의 첫 후보가 검증되지 않음** — "지금까지 가장 좋은 후보"의 초기값(block 0, 진행 중이면 1)을 안전한지 확인하지 않고 시작해서, 더 좋은 후보가 없으면 write frontier 를 victim 으로 골랐다(`Inconsistency in the global mapping table when locking an LPA!`). 처음부터 모든 block 을 검사해 안전한 것 중에서만 고르도록 수정.
- **(표에 없음) FIFO 가 빈 큐·위험한 block 을 확인하지 않음** — 할당 순서 큐의 맨 앞을 무조건 꺼냈다: 큐가 비었는지 확인하지 않았고(`std::queue::front()` UB), 그 block 이 안전한지도 보지 않았다. 큐를 돌며 안전한 것만 고르도록 수정.
- **#25 FIFO 가 꺼낸 후보를 잃어버림** — FIFO 가 후보를 큐에서 꺼낸 뒤, 공통 코드가 "invalid page 가 없다"며 거절하면 그 block 은 큐에 다시 들어가지 않았다. 나중에 그 block 이 유일한 청소 대상이 되면 FIFO 는 영원히 못 찾아 멈춤. 거절될 조건을 꺼내기 전에 확인하도록 수정.
- **#26 RANDOM 계열이 검증 안 된 마지막 후보를 사용** — 조건에 맞는 block 이 나올 때까지 block 수만큼 다시 뽑다가, 실패하면 **마지막에 뽑은 것을 조건과 무관하게** 썼다. frontier 가 뽑히면 크래시. 최종 후보를 검증하고 아니면 건너뛰기.
- **#27 FIFO 큐가 끝없이 커짐** (`Flash_Block_Manager_Base.cpp`) — block 이 할당될 때마다 큐에 넣고 FIFO GC 가 고를 때만 뺐다. 정적 WL 이나 다른 정책의 GC 로 지워진 block 은 옛 항목이 남은 채 또 들어가, 24 block 평면에서 83개까지 커졌고, 옛 항목 때문에 FIFO 순서도 틀어졌다. 항목에 할당 번호(`Allocation_seq`)를 붙여 지난 항목은 버림.

<div style="margin-top: 40px;"></div>

### A5. 명령 스케줄러(TSU)와 일시정지(suspend)

flash 의 program(쓰기)·erase(지우기)는 read 보다 수십~수백 배 오래 걸린다. MQSim 은 기다리는 read 를 위해 진행 중인 program/erase 를 잠깐 멈추는(suspend) 기능을 모델링하는데, 이 경로는 원본에서 **한 번도 제대로 동작한 적이 없었다**. 버그 여러 개가 서로를 가리고 있었다.

- **#14 `break` 누락으로 suspend 가 항상 무력화** (`TSU_OutofOrder.cpp`, `TSU_Priority_OutOfOrder.cpp`, 6곳) — 칩 상태 switch 에서 `suspensionRequired = true;` 뒤에 `break` 가 없어 다음 case 로, 결국 `default: return false;` 로 떨어졌다. suspend 조건을 만족해도 명령을 내리는 코드에 도달하지 못했다.
- **#15 생성자 인자 순서 뒤바뀜** — `TSU_Base(…, bool erase, bool program, time, time, time)` 를 파생 클래스가 `(…, time, time, time, bool, bool)` 순서로 불렀다. 둘 다 정수 계열이라 컴파일 에러 없이 변환돼, `programSuspensionEnabled` 는 나노초 값(0 이 아님)을 받아 **설정과 무관하게 항상 true** 였다.
- **#16 suspend 시 활성 다이 카운터가 리셋 안 됨** (`NVM_PHY_ONFI_NVDDR2.cpp`) — `PrepareSuspend()` 호출이 멀티 다이 전용 조건 뒤에 있어서, 다이가 1개인 구성에서는 불리지 않았다.
- **#17 resume 시 카운터를 복원 안 함** (`NVM_PHY_ONFI_NVDDR2.h`) — resume 된 명령이 끝날 때 `unsigned` 카운터가 0 에서 한 번 더 빠져 언더플로, 이후 칩이 영원히 idle 로 돌아오지 못함(멈춤).
- **#28 "suspend 할 가치가 있나" 판단의 unsigned 언더플로** (`TSU_Priority_OutOfOrder.cpp`, 3곳) — `Expected_finish_time(chip) - Time() < 기준` 이면 "곧 끝나니 멈추지 말자"인데, `sim_time_type` 이 unsigned 라 종료 시각이 이미 지났으면(그 명령의 완료 처리 도중에 스케줄러가 다시 불린 경우) 뺄셈이 아주 큰 수가 되어 가드가 무력화됐다. 이미 끝난 명령을 suspend 하려다 NULL 이벤트 참조 segfault, erase suspend 에서는 오히려 read 를 크게 느리게 만듦. "종료 시각 ≤ 지금이면 suspend 안 함" 추가.

#14 가 막고 있어서 #15~17 은 실행될 기회조차 없었고, #14 를 고치자 #15, #15 를 고치자 #16·#17 이 드러났다. #28 은 그 모든 수정 뒤에 읽기를 섞어 모드별로 측정하다 나왔다.

<div style="margin-top: 40px;"></div>

### A6. 마모평준화(wear-leveling)

- **#5 block ID 를 주소로 착각** (`run_static_wearleveling()`) — 대상 block 을 "GC/WL 진행 중"으로 표시하는 함수에 block 주소 대신 block ID 정수를 넘겨, 엉뚱한 메모리를 건드렸다. 올바른 주소 객체를 넘기도록 수정.
- **#6 "erase 횟수 차이"가 실제로는 "block 번호 차이"** (`Get_min_max_erase_difference()`) — 가장 많이/적게 지워진 block 의 erase 횟수 차이를 돌려줘야 하는데 **두 block 의 번호** 차이를 돌려줬고, unsigned 라 음수가 되면 40억 근처로 넘어갔다. 정적 WL 발동 여부가 실제 마모와 거의 무관했다.
- **#18 정적 WL 대상이 평생 한 번만 발동** (`run_static_wearleveling()`, `check_static_wl_required()`) — 평면 전체에서 erase 횟수가 가장 적은 block 을 대상으로 삼았는데, 그건 거의 항상 **한 번도 안 쓰이는 write frontier**(매핑 테이블이 DRAM 에 다 들어가서 영원히 erase 0 인 매핑용 frontier 등)였다. 안전하지 않다고 거절되면 다음 후보를 찾지 않고 포기 — 그 frontier 의 erase 횟수는 영원히 0 이니 **이후 영원히** 발동 불가. "데이터가 있고 안전한 block" 중에서만 최소를 고르도록 수정.
- **#19, #20 WL 이 GC 로 집계됨** — 대기했다 재개된 WL 실행과 WL 의 page 이동을 GC 통계로 셌다(`Average_Page_Movement_For_WL` 이 항상 0). WL 쪽으로 나눠 세도록 수정.

<div style="margin-top: 40px;"></div>

### A7. 조용히 멈추는 버그 — 요청이 영원히 끝나지 않음

에러 메시지 없이 이벤트 큐가 비고, 요청 몇 개(대개 큐 깊이인 4개)가 영원히 미완료로 남는 증상. 하나를 고치면 다음 것이 드러나는 사슬이었다.

- **#21 barrier 에서 풀려난 요청의 완료가 알려지지 않음** (`Address_Mapping_Unit_Page_Level.cpp`) — GC 가 어떤 LPA 의 page 를 옮기는 동안 그 LPA 로 온 요청은 barrier 뒤에서 기다린다. 이동이 끝나면 원본은 이 요청들을 매핑 유닛 **자기 핸들러에만** 알리고 지웠는데, 그 핸들러는 매핑 트랜잭션이 아니면 바로 return 한다. 결국 DRAM 캐시 매니저가 완료를 몰라 back-pressure 카운터가 새다가 모든 쓰기가 막혔다. 진짜 flash 완료와 같은 broadcast 로 모든 구성요소에 알리도록 수정.
- **#22 대기했다 재개된 GC/WL 이 erase 를 제출하지 않음** (`GC_and_WL_Unit_Base.cpp`) — 진행 중인 요청 때문에 기다렸다 재개하는 경로만 erase 트랜잭션을 만들고 스케줄러에 **넣지 않았다**. block 이 영원히 "GC 중"으로 남아 평면이 block 을 잃음. `Submit_transaction` 한 줄 추가.
- **#23 평면 대기열에서 풀려난 write 가 LPA barrier 를 무시** — 빈 page 가 없어 기다리던 write 를 풀어줄 때만 barrier 확인이 빠져, 옮기는 중인 LPA 가 다시 매핑돼 크래시. 다른 경로처럼 barrier 뒤로 보내도록 수정.
- **#24 GC 재검사할 계기가 없음** — GC 검사는 frontier 교체나 erase 완료 때만 실행된다. 검사가 아무것도 못 했는데(예: RGA 의 무작위 표본이 청소할 block 을 전부 빗나감) 그 평면의 쓰기가 전부 대기 중이면, 다시 검사를 부를 사건이 영영 없다. 첫 쓰기가 대기열에 들어갈 때 검사를 요청하고, 회수할 block 이 있는 한 짧은 간격으로 재시도(최대 1000번, 넘으면 경고 출력 — 무한 루프 대신 멈춤이 되도록).

<div style="margin-top: 40px;"></div>

### A 에 딸린 보조 수정 (이 프로젝트 자신의 수정과 맞물린 것)

- **트랜잭션 "주소 결정됨" 플래그를 일관되게 설정** (`Address_Mapping_Unit_Page_Level.cpp`, 4곳) — 원본은 `Physical_address_determined` 를 번역 경로에서만 세우고, block 카운터를 올리는 다른 4곳(부분 쓰기의 update read, 매핑 read 2곳, 매핑 write)에서는 세우지 않았다. #21 수정 후 "주소가 정해진 적 없는 요청은 block 회계에서 빼기" 위해 이 플래그를 쓰게 되면서 필요해졌다. (#21 수정이 처음에 block 0 의 카운터를 음수로 만든 이 프로젝트 자신의 회귀를 고친 것.)

<div style="margin-top: 60px;"></div>

## 4. B — 의도적으로 upstream 과 다르게 바꾼 동작

버그는 아니지만, 원본 동작이 이 프로젝트의 작은 데모 규모에서는 의미가 없거나 멈추기 때문에 일부러 다르게 바꾼 것. 코드에는 `DEVIATION FROM UPSTREAM MQSim` 주석이 달려 있다.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>변경</th><th>원본</th><th>이 프로젝트</th><th>이유</th></tr>
<tr><td>정적 WL 대상 선정 (<code>get_static_wl_erase_info()</code>)</td><td>평면 전체의 최소 erase block 하나만 보고, 안 되면 포기</td><td>데이터가 있고 안전한 block 중 최소를 대상으로</td><td>A6 의 #18 과 같은 수정. 원본대로면 평생 한 번만 발동</td></tr>
<tr><td>GC/WL 시작 전 이동 공간 확인 (<code>has_room_to_migrate()</code>)</td><td>확인 없음 — 사용자 쓰기 차단 하한(동시 GC 수와 같은 값)이 여유를 보장한다고 가정</td><td>진행 중 GC 들이 옮길 page + 이번 victim 의 valid page 를 빈 block 이 담을 수 있을 때만 시작</td><td>이 프로젝트가 그 하한을 10 → 3 으로 낮춘 탓(C 참고)에, 2-flow 에서 valid 가 많은 victim 을 고르는 정책(RANDOM_P/PP)이 빈 block 을 바닥내 크래시</td></tr>
<tr><td>GC 재검사 재시도 (<code>gc_retry_needed()</code>)</td><td>없음</td><td>A7 #24 참고 — 최대 1000번 재시도 후 경고</td><td>작은 규모에서 GC 가 영영 다시 검사되지 않는 멈춤 방지</td></tr>
<tr><td>한 번도 안 쓴 LPA 읽기 (<code>Unmapped_Reads_Return_Zeros</code>, 선택 사항)</td><td>읽기가 그 LPA 에 실제 page 를 하나 잡아 valid 로 만들고(쓰기 없이), 그 page 를 flash 에서 읽음 — preconditioning 을 대신하는 지연 방식</td><td>flash 를 거치지 않고 바로 완료(실제 SSD 가 0 을 돌려주듯), page 를 잡지 않음</td><td>이 데모 규모에서는 preconditioning 을 쓸 수 없고(원본의 배치 모델이 작은 block 수에서 실패), 원본 방식으로는 읽기가 장치를 가짜 page 로 채움. <b>기본값 false</b> 라 upstream 동작·골든 불변, 앱 설정만 true</td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 5. C — 데모 규모 튜닝

- **`max_ongoing_gc_reqs_per_plane` 10 → 3** (`SSD_Device.cpp`, `SCALE TWEAK` 주석) — 평면당 동시 GC 수이자, 빈 block 이 이보다 적으면 사용자 쓰기를 막는 하한. 원본이 가정하는 수천 block 규모에서는 10 이 무시할 만한 값이지만, 화면에 다 보이도록 block 을 12~64개로 줄인 이 프로젝트에서는 GC 임계값과 겹쳐 "GC 시연"을 영구 교착시켰다. 자세한 경위는 [튜닝된 코드](/ftl-visual-simulator/reference/tweaked-code/) 참고. 이 값을 낮춘 부작용이 B 의 "이동 공간 확인"이다.

<div style="margin-top: 60px;"></div>

## 6. D — 새 기능 (upstream 에 없음)

- **Cost-Benefit GC 정책** (`GC_Block_Selection_Policy_Type::COST_BENEFIT`, 설정값 `COST_BENEFIT`) — LFS(Rosenblum & Ousterhout, 1991)의 정책: `(1 − u) / (2u) × age` 가 가장 큰 block 을 고른다(u = valid 비율, age = 그 block 이 write frontier 로 할당된 뒤 지난 시간). 이를 위해 block 에 `Allocation_time` 필드를 추가했다. 새 enum 값이라 기존 설정의 동작은 불변.
- **`Unmapped_Reads_Return_Zeros` 설정** — B 표 참고. `Device_Parameter_Set` 의 새 파라미터(기본 false).
- **조회·통계 추가** (동작 불변) — UI 가 필요한 값을 읽을 수 있도록: 평면별 빈 block 수와 GC 임계값, 빈 page 를 기다리는 쓰기 수(장치 가득 참 판단), 처리된 호스트 요청 수, 읽기 지연 누적값과 "마지막 조회 이후 가장 느린 읽기", GC 재시도 한도 도달 횟수(`Stats::Gc_retry_limit_hits`), block 스냅샷의 `Stream_id`(어느 flow 의 데이터인지).

<div style="margin-top: 60px;"></div>

## 7. E — 시각화를 위한 계측·라이브러리화·WASM

시뮬레이션이 계산하는 값은 바꾸지 않고(골든 불변), **밖에서 보고 조종할 수 있게** 만든 변경들.

- **라이브러리화** (`exec/MQSim_Interface.*` 새 파일, `main.cpp` −261줄) — 원본 `main.cpp` 에 통째로 있던 "설정 읽기 → 시나리오 만들기 → 끝까지 실행 → 결과 쓰기"를 `Load_workload` / `Initialize_scenario` / `Run_step` / `Run_to_completion` / `Write_results` / `Finalize_scenario` 함수로 쪼갰다. `main.cpp` 는 이것들을 순서대로 부르는 얇은 CLI 가 됐다(그래서 골든 테스트가 같은 코드를 네이티브로 돌릴 수 있다).
- **한 단계씩 실행** (`sim/Engine.cpp`) — 원본 `Start_simulation()` 의 while 루프 한 바퀴를 `Run_next_event_group()` 으로 꺼내고, 준비 단계를 `Setup_simulation()` 으로 분리. 재생 ▶ / "1 step" 버튼이 이걸 부른다.
- **이벤트 hook** (`exec/Simulation_Events.*` 새 파일) — 매핑 갱신, GC 시작/page 이동/erase, 정적 WL 시작/이동/erase, 동적 WL block 할당/반납 시점에 콜백을 부른다. 콜백이 없으면 아무 일도 안 한다. GC 시작 이벤트에는 victim 의 valid/invalid 수와 빈 block·임계값을 담는다("왜 이 block?" 설명용).
- **상태 스냅샷** — 매핑 테이블(`Get_mapping_table_snapshot`), 전체 block/page 상태(`Get_block_state_snapshot`) 조회 함수.
- **UI 한 단계가 의미 있는 단위가 되도록 미룬 호출** — 원본은 어떤 쓰기가 frontier 를 넘기는 순간 그 안에서 바로 GC 검사를 하고, 요청 완료 처리 안에서 바로 대기 GC 를 실행했다. 이러면 "쓰기 한 번"과 "GC 시작"이 한 이벤트 묶음에 섞여 화면의 "1 step" 으로 나눌 수 없어서, 이런 호출들을 별도의 시뮬레이터 이벤트로 미뤘다(`GC_Deferred_Event_Type`, 대기 쓰기를 한 번에 하나씩 푸는 `RELEASE_WAITING_WRITE`). 골든 불변으로 결과에 영향 없음을 확인.
- **WASM 바인딩** (`wasm/bindings.cpp` 새 파일) — `init` / `configure` / `step` / `run` / `stepEvent`(로그 한 줄 단위) / `runEvents` / `getState` / `setEventCallback` 을 JavaScript 로 노출. 설정 XML 은 Emscripten 메모리 파일시스템에 써서 **원본의 XML 파서 그대로** 읽힌다.

<div style="margin-top: 60px;"></div>

## 8. F — 테스트 (원본에는 테스트가 전혀 없음)

- **골든 회귀 테스트** (`engine/tests/golden/`, `npm run test:engine`) — upstream 샘플 시나리오 3개의 결과를 바이트 단위로 비교. 9/6 이후 한 번도 다시 만들지 않음.
- **GMock/GTest 유닛 테스트 14개** (`engine/tests/unit/`, `npm run test:engine:unit`) — 매핑 유닛·block 매니저·GC/WL 유닛·스케줄러를 가짜 협력 객체로 떼어내, 특정 조건(erase 차이, 임계값, 대상 선정)을 수백만 이벤트를 돌리지 않고 바로 검사.
- 그 밖에 이 프로젝트가 직접 돌린 구성 스윕(세 프리셋 × 모든 파라미터 극단값 × GC 정책, 최대 112가지)은 코드로 저장하지 않은 임시 하니스라 여기엔 포함하지 않았다 — 결과는 [정적 마모 평준화 대상 선정 버그와 조용히 멈추던 버그들](/ftl-visual-simulator/reference/bug-list/wl-target-and-stall-bugs/) 12~13절에.

<div style="margin-top: 60px;"></div>

## 9. 정리

- 원본 MQSim 은 **큰 SSD 를 한 번 끝까지 돌리는** 연구용 도구로서는 대부분 문제없이 동작한다 — 이 프로젝트가 찾은 버그 28개 중 상당수는 (a) 이식성(다른 컴파일러/표준 라이브러리), (b) 한 프로세스에서 반복 실행·중간 정지, (c) 수십 개 block 수준의 작은 규모, (d) 한 번도 켜본 적 없는 기능(suspend, 정적 WL 설정) 중 하나를 건드려야 드러났다.
- 그래도 "결과가 조용히 틀리는" 버그도 있었다 — 정적 WL 이 실제 마모와 무관하게 발동하거나(#6) 평생 한 번만 발동한 것(#18), suspend 가 한 번도 동작하지 않은 것(#14~17), WL 통계가 GC 로 섞인 것(#19~20). 이런 것들은 원본으로 논문 수치를 낸 경우에도 영향이 있을 수 있는 종류다.
- 이 프로젝트의 변경은 대부분 upstream 샘플 결과를 바꾸지 않는다(골든 불변). 바꾸는 것은 B·C·D 의 의도적 변경뿐이고, 모두 코드 주석과 이 문서에 이유를 적었다.

<div style="margin-top: 60px;"></div>

## 참고

- [버그 목록](/ftl-visual-simulator/reference/bug-list/) · [버그 목록표](/ftl-visual-simulator/reference/bug-list/table/) — 버그별 발견 경위와 디버깅 기록
- [튜닝된 코드](/ftl-visual-simulator/reference/tweaked-code/) — C 의 규모 튜닝 상세
- [WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/) — 원본을 그대로 컴파일해서 쓰는 이유
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — `git diff 90b0fb1..HEAD -- engine/mqsim/src`
