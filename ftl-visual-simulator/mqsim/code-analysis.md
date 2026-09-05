---
layout: default
title: MQSim 코드 분석
permalink: /ftl-visual-simulator/mqsim/code-analysis/
---
# MQSim 코드 분석

`/home/ryuj/Ryu/MQSim` 소스를 직접 뜯어보고 정리한 기록. WASM 으로 컴파일해서 그대로 쓸 코드라서, hook 을 어디에 심을지 판단하려면 이 정도는 알아야 한다.

<div style="margin-top: 60px;"></div>

## 1. 코드 구조

`src/` 아래 6개 디렉터리, 61개 `.cpp` 파일( 헤더 포함 ~19,300줄 ).

```
src/
├── exec/         실행 진입점 — 설정 파싱, SSD_Device/Host_System 조립
├── host/         호스트 쪽 — I/O 요청 생성기, PCIe 링크
├── nvm_chip/     NAND 물리 모델 — Chip/Die/Plane/Block/Page
│   └── flash_memory/
├── sim/          이산 이벤트 시뮬레이션 엔진 (Engine, EventTree, Sim_Object)
├── ssd/          SSD 내부 전체 — Host Interface, Cache, FTL, GC, TSU, PHY, Channel
└── utils/        XML 파싱(rapidxml), 난수 생성기, 문자열 유틸
```

SSD_Device.h 주석에 파이프라인이 그대로 적혀 있다.

```
Host_Interface <-> Data_Cache_Manager <-> NVM_Firmware(FTL) <-> NVM_PHY <-> NVM_Channel <-> Chips
```

<div style="margin-top: 60px;"></div>

## 2. 각 클래스 역할

### 시뮬레이션 엔진 ( `sim/` )

- **`Sim_Object`** : 모든 시뮬레이션 구성요소의 베이스 클래스. `Execute_simulator_event()` 를 구현해야 하고, 다른 객체가 보낸 이벤트를 이 함수로 받는다.
- **`Engine`** ( 싱글턴, 매크로 `Simulator` ) : 전체 시뮬레이션의 시계 역할. `EventTree` 에 이벤트를 등록(`Register_sim_event`)하고, 시간 순서대로 꺼내서 해당 `Sim_Object` 의 `Execute_simulator_event` 를 호출한다.
- **`EventTree`** : 이벤트를 발생 시각 순으로 정렬해 보관하는 자료구조.

즉 MQSim 은 "누가 언제 무슨 일을 하는지"를 이벤트 단위로 스케줄링하는 **이산 이벤트 시뮬레이터**다. 우리가 시각화를 위해 hook 을 심을 지점도 대부분 각 클래스의 `Execute_simulator_event` 안이 될 것이다.

### 실행/조립 ( `exec/` )

- **`Execution_Parameter_Set`** : `ssdconfig.xml` 전체를 담는 최상위 설정 객체 ( Host + Device 설정 ).
- **`SSD_Device`** : Host_Interface, Data_Cache_Manager, NVM_Firmware(FTL), PHY, Channel 을 실제로 생성하고 연결하는 조립 클래스. "SSD 한 대"에 해당.
- **`Host_System`** : workload 정의(`workload.xml`)를 읽어 IO_Flow 들을 만들고, SSD_Device 에 요청을 흘려보내는 역할.

### 호스트 쪽 ( `host/` )

- **`IO_Flow_Base`** → **`IO_Flow_Synthetic`**( 파라미터 기반 랜덤/시퀀셜 요청 생성 ) / **`IO_Flow_Trace_Based`**( 실제 trace 파일 재생, 예 : `tpcc-small.trace` )
- **`PCIe_Root_Complex` / `PCIe_Switch` / `PCIe_Link`** : NVMe 가 얹히는 PCIe 링크 계층 지연시간 모델

### FTL 전체 ( `ssd/FTL.h` 가 중심 )

`FTL` 클래스( `NVM_Firmware` 상속 )가 아래 4개를 멤버로 들고 있다 — **우리가 시각화하려는 것들이 정확히 이 4개다.**

| 멤버 | 클래스 | 역할 |
|---|---|---|
| `Address_Mapping_Unit` | `Address_Mapping_Unit_Base` → `_Page_Level` / `_Hybrid` | LPA(논리 페이지) → PPA(물리 페이지) 매핑. `Translate_lpa_to_ppa_and_dispatch()` 가 요청 처리의 실제 진입점 |
| `BlockManager` | `Flash_Block_Manager_Base` → `Flash_Block_Manager` | block/page 의 free·valid·invalid 상태, erase count, write frontier(쓰기 중인 block) 관리 |
| `GC_and_WL_Unit` | `GC_and_WL_Unit_Base` → `_Page_Level` | `Check_gc_required()` 로 GC 트리거 판단, victim block 선정, 마모 평준화 |
| `TSU` | `TSU_Base` → `_FLIN` / `_OutofOrder` / `_Priority_OutOfOrder` | 여러 채널/칩에 대해 어떤 flash transaction(R/W/E)을 언제 실행할지 스케줄링 |

- **`Address_Mapping_Unit_Page_Level`** 내부에는 CMT(Cached Mapping Table) 관련 메서드( `Exists`, `Retrieve_ppa`, `Reserve_slot_for_lpn` )가 따로 있다 — 매핑 테이블 전체를 메모리에 두지 않고 일부만 캐싱하는 DFTL 류의 구조가 이미 구현되어 있다는 뜻.
- **`Flash_Block_Manager_Base`** 안의 `Block_Pool_Slot_Type` 이 진짜 "block 상태"를 들고 있다 — `Invalid_page_bitmap`( 페이지별 valid/invalid ), `Erase_count`, `Current_status`( IDLE/GC_WL/USER/GC_USER 등 상태 머신 ). 우리 시각화의 grid 색상은 결국 이 구조체를 읽으면 된다.
- **`PlaneBookKeepingType`** 은 plane 단위로 free/valid/invalid page 개수와 **Data_wf / GC_wf / Translation_wf**( double write frontier — 사용자 쓰기용 block 과 GC 쓰기용 block 을 분리하는 기법 )를 관리한다.

### 물리 계층 ( `nvm_chip/`, `ssd/NVM_PHY_*`, `ssd/ONFI_Channel_*` )

- **`Flash_Chip`**( `NVM_Chip` 상속 ) → **`Die`** → **`Plane`** → **`Block`** → **`Page`** : 물리적 NAND 계층 구조 그대로. `Page` 는 사실 LPA 하나만 들고 있는 아주 얇은 클래스이고, 진짜 상태 관리는 위의 `Flash_Block_Manager` 쪽에서 함.
- **`NVM_PHY_ONFI` / `NVM_PHY_ONFI_NVDDR2`** : ONFI 프로토콜 타이밍 모델( read/program/erase 지연시간 )
- **`ONFI_Channel_Base` / `_NVDDR2`** : 채널 하나에 여러 칩이 붙는 버스 경합 모델

### 캐시 / 호스트 인터페이스

- **`Data_Cache_Manager_Base`** → `_Flash_Simple` / `_Flash_Advanced` : SSD 내부 DRAM 쓰기 캐시
- **`Host_Interface_Base`** → **`Host_Interface_NVMe`** / **`Host_Interface_SATA`** : 호스트 프로토콜별 큐 관리( NVMe 는 multi-queue, SATA 는 단일 큐 )

<div style="margin-top: 60px;"></div>

## 3. 동작 방식

### 3-1. 프로그램 시작부터 끝까지 ( `main.cpp` )

1. `-i`(설정), `-w`(워크로드) 인자로 `ssdconfig.xml`, `workload.xml` 경로를 받음
2. `read_configuration_parameters()` — XML 을 `Execution_Parameter_Set` 으로 파싱( 파일이 없으면 기본값으로 새로 생성 )
3. `read_workload_definitions()` — workload XML 을 시나리오 목록으로 파싱( synthetic / trace-based 혼합 가능 )
4. **시나리오별 루프** :
   - `Simulator->Reset()` — 이산 이벤트 엔진 초기화
   - `SSD_Device ssd(...)` 생성 — Host_Interface 부터 Channel 까지 전체 조립
   - `Host_System host(...)` 생성 — workload 로부터 IO_Flow 들 생성, `host.Attach_ssd_device(&ssd)`
   - `Simulator->Start_simulation()` — **여기서부터 진짜 시뮬레이션 시작**
   - `collect_results()` — 결과를 `workload_scenario_N.xml` 로 기록

### 3-2. 이산 이벤트 루프 ( `Engine::Start_simulation` )

`EventTree` 에서 가장 이른 시각의 이벤트를 꺼내 해당 `Sim_Object` 의 `Execute_simulator_event()` 를 호출 → 그 안에서 필요하면 또 다른 이벤트를 등록 → 이벤트가 없거나 종료 조건을 만나면 정지. 실시간 개념이 없는, 순수하게 "다음 이벤트 시각"만 따라가는 구조라서 시뮬레이션 자체는 아주 빠르다( 9/4 에 90만 건 요청 처리하는 시나리오도 몇 초 내 종료 ).

### 3-3. Write 요청 하나의 실제 경로

1. `Host_Interface`( NVMe/SATA )가 호스트의 write 요청을 큐에서 꺼냄
2. `Data_Cache_Manager` 를 거쳐 필요하면 SSD 내부 DRAM 캐시에 먼저 반영
3. `FTL.Address_Mapping_Unit.Translate_lpa_to_ppa_and_dispatch()` — LPA 를 조회(CMT hit/miss), 새 PPA 를 `Flash_Block_Manager` 에서 할당받아 매핑 갱신, 기존 PPA 가 있었다면 invalid 로 표시
4. `TSU.Schedule()` — 이 flash transaction 을 어느 채널/칩에 언제 실행시킬지 스케줄링( FLIN/out-of-order/priority 정책 중 설정된 것 )
5. `NVM_PHY_ONFI` + `ONFI_Channel` 이 실제 program 명령의 타이밍(지연시간)을 시뮬레이션
6. write frontier 블록이 가득 차서( `Current_page_write_index == pages_no_per_block` ) `Flash_Block_Manager` 가 free pool 에서 새 블록을 배정할 때마다( 매 쓰기가 아니라 **블록 하나를 다 썼을 때만** ) `GC_and_WL_Unit.Check_gc_required()` 가 불려서 GC 트리거 여부 판단 → 필요하면 victim block 선정, valid page migration, block erase 순으로 GC 실행

이 6단계가 바로 우리 계획의 Session 3~6 에서 hook 을 심을 지점들과 정확히 대응한다.

<div style="margin-top: 60px;"></div>

## 4. 테스트 방식

**MQSim 자체에는 자동화된 테스트 스위트가 없다** — `test/` 디렉터리도 없고, README 에도 테스트 관련 언급이 전혀 없음( 직접 확인 ). 논문 기반 연구용 시뮬레이터답게, 검증은 사실상 다음 방식으로 이루어진다.

- 샘플 `ssdconfig.xml` + `workload.xml` 로 빌드/실행
- 결과 XML 의 통계( IOPS, 응답시간, `Total_GC_Executions`, CMT hit/miss 등 )가 상식적인 범위인지 사람이 눈으로 확인
- 실제로 9/4 에 우리가 한 것도 이 방식 그대로였음 — g++13 으로 수정 없이 빌드, 3개 시나리오 실행, 결과 XML 을 열어 응답시간·요청 수·GC 실행 여부를 확인

**우리 프로젝트에서 hook 을 추가할 때도 같은 방식을 따른다** :

1. hook 추가 전/후로 **같은 설정·워크로드**를 돌려서 최종 통계( 요청 수, 응답시간, WAF 등 )가 **완전히 동일한지** 비교 — hook 은 상태를 JS 로 "보고"만 해야지, 시뮬레이션 결과 자체를 바꾸면 안 됨( 회귀 테스트 )
2. hook 이 보내는 이벤트 로그를 최종 통계와 대조 — 예를 들어 hook 이 카운트한 GC 실행 횟수가 결과 XML 의 `Total_GC_Executions` 와 정확히 일치해야 함( Session 5 에서 실제로 검증할 항목 )
3. WASM 빌드 자체가 원본 네이티브 빌드와 동일한 결과를 내는지도 별도로 확인( Emscripten 컴파일 과정에서 부동소수점/타입 크기 차이로 결과가 미묘하게 달라질 수 있음 )

### Google Test / Google Mock 으로 TDD 가 가능한가

가능하다 — 그것도 꽤 잘 맞는 편이다.

- **왜 되는가** : `Address_Mapping_Unit_Base`, `Flash_Block_Manager_Base`, `GC_and_WL_Unit_Base`, `TSU_Base` 가 전부 순수 가상 함수로만 이루어진 추상 베이스 클래스다. 즉 처음부터 "인터페이스"로 설계돼 있어서, Google Mock 으로 예를 들어 `Flash_Block_Manager_Base` 를 mock 으로 갈아끼우고 `GC_and_WL_Unit_Page_Level` 의 victim 선정 로직만 떼어내 단위 테스트하는 게 구조적으로 가능하다. 지금까지 아무도 그렇게 안 썼을 뿐.
- **걸림돌** : `main()` 이 `main.cpp` 안에 그대로 박혀 있어서 테스트 바이너리가 링크할 라이브러리가 없다. 다만 이건 우리가 WASM 임베딩을 위해 어차피 해야 하는 리팩터링( CLI 진입점을 라이브러리 형태로 분리 )과 정확히 같은 작업이라, 테스트 스위트 추가가 별도 비용이 아니라 같은 리팩터링을 두 번 활용하는 셈이 된다.
- **두 단계로 나눌 수 있다** :
  1. **골든/회귀 테스트**( GMock 불필요 ) — 고정 시나리오를 실행해 결과 통계가 기존과 완전히 같은지 스냅샷 비교. hook 추가로 인한 부작용을 잡는 용도로, 지금 이 문서의 회귀 테스트 방식을 GTest 프레임워크 위에 올리는 정도.
  2. **진짜 단위 테스트**( GMock 필요 ) — 위 4개 베이스 클래스를 mock 으로 갈아끼워 매핑/GC 로직만 격리해서 테스트. Cost-Benefit GC 확장 기능처럼 새로 짜는 로직을 검증할 때 특히 유용.
- **( 시간이 여유로울 때 ) 목표로 채택** — [FTL Visual Simulator 목표](/ftl-visual-simulator/) 7번 항목으로 등록.
- **언제 추가하는 게 가장 좋은가 : Session 4 가 최적** — 이유는 단순하다. GTest/GMock 을 쓰려면 테스트 바이너리가 링크할 라이브러리가 있어야 하는데, `main()` 이 `main.cpp` 안에 그대로 있는 지금 구조로는 불가능하다. 그런데 **Session 4 에서 우리가 어차피 하는 일**( WASM 임베딩을 위해 CLI 진입점을 라이브러리 형태로 분리하는 리팩터링 )이 정확히 이 문제를 해결한다. 즉 :
  - Session 4 **이전** 에 시도하면 → 같은 리팩터링을 두 번 해야 함( 낭비 )
  - Session 4 **이후** 로 미루면 → 테스트 없이 GC/hybrid( Session 5~6 )를 먼저 구현하게 되어, 회귀를 놓칠 위험이 가장 큰 세션을 테스트 없이 지나감
  - 그래서 **Session 4 에서 라이브러리 분리 작업을 할 때 GTest 프레임워크 연결까지 같이 끝내두고**, Session 5( GC )부터는 새 로직을 짤 때마다 테스트를 같이 쌓아가는 것이 가장 효율적
- 시간이 부족하면 Session 4 에서는 골든/회귀 테스트만 먼저 걸어두고, GMock 을 이용한 진짜 단위 테스트는 13~16번 버퍼 기간( Cost-Benefit GC 구현과 같은 시기 )으로 미뤄도 됨.

<div style="margin-top: 60px;"></div>

## 5. 시각화에 가져갈 부분 vs 단순화할 부분

Session 2 결과물 중 하나 — 지금까지 읽은 구조에서 뭘 그대로 화면에 옮기고 뭘 걷어낼지 미리 정리해둔다( MVP 범위 확정 자체는 Session 3 에서 ).

**그대로 가져갈 것 ( hook 을 심어 실시간으로 노출할 대상 )**

- `Flash_Block_Manager` 의 `Block_Pool_Slot_Type`( valid/invalid/free, erase count ) → flash grid 색상 그 자체
- `Address_Mapping_Unit_Page_Level` 의 매핑 갱신 → 매핑 테이블 패널
- `GC_and_WL_Unit_Page_Level` 의 트리거/victim 선정/migration/erase → GC 애니메이션 + 이벤트 로그
- `Stats` 의 핵심 카운터( `Total_GC_Executions`, WAF 관련 값 ) → 통계 대시보드

**단순화하거나 뒤로 미룰 것**

- TSU 의 채널/칩 스케줄링 세부( 어떤 정책이 어떤 순서로 트랜잭션을 고르는지 )와 `ONFI_Channel` 버스 경합 타이밍 — MVP 에서는 "요청이 실행된다" 정도로만 보여주고, 채널별 타이밍 시각화는 확장 목표로 미룸
- PCIe 링크 지연시간, SATA 호스트 인터페이스 — 데모는 NVMe 하나로 고정, SATA 비교는 다루지 않음
- CMT( Cached Mapping Table ) 의 partial caching( hit/miss ) — 초기 MVP 는 "매핑 테이블 전체"를 보여주는 것으로 단순화하고, DFTL 류 캐시 hit/miss 시각화는 확장 기능으로 미룸
- `Data_Cache_Manager` 의 DRAM 캐시 세부( row size, tRCD/tCL/tRP 등 타이밍 ) — 시뮬레이션 정확도 유지에만 쓰고 화면에는 노출 안 함

이 구분은 Session 3( 설계 )에서 MVP 범위·파라미터 패널 구성을 확정할 때 그대로 기준이 된다.

<div style="margin-top: 60px;"></div>

## 6. 파일별 상세 설명

`/home/ryuj/Ryu/MQSim/src` 아래 61개 파일 중, 이 프로젝트가 직접 만지거나 이해해야 하는 파일들을 디렉터리별로 정리. 사소한 타입 정의/유틸리티 파일은 마지막에 묶어서 처리.

> **범위 안내( 9/5 확정 )** — 이 프로젝트에서 깊이 읽는 대상은 **FTL 코드( 주소 매핑 · 블록 관리 · GC/WL · TSU 스케줄링 )뿐**이다. Host 계층( `host/` 디렉터리 전체, `Host_Interface_*` )은 "NVMe 가 multi-queue, SATA 가 단일 큐"라는 개념만 파악하면 되고, 코드를 줄 단위로 따라 읽을 필요는 없다 — 아래 표에서도 그렇게 다르게 다룬다.
>
> **FTL 관련 코드 규모( `wc -l` 실측, 9/5 )** — `FTL.h/cpp` + 4대 클래스(주소 매핑/블록 관리/GC·WL/TSU) 총 **6,709줄**, MQSim 전체 소스(19,309줄)의 **약 35%**.
> 참고로 Host 계층( `host/` + `Host_Interface_*` )은 3,640줄( 약 19% ) — 이 프로젝트에서는 개념만 보면 되는 부분이 전체의 5분의 1 정도 된다는 뜻.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>파일</th><th>설명</th></tr>
<tr><td colspan="2" style="background:#2c3e50;color:#fff;font-weight:700;">exec/ — 조립 · 설정</th></tr>
<tr><td><code>main.cpp</code></td><td>진입점. 인자 파싱 → <code>Execution_Parameter_Set</code> 로드 → workload XML 파싱 → 시나리오별로 <code>Simulator-&gt;Reset()</code> → <code>SSD_Device</code>/<code>Host_System</code> 생성 → <code>Simulator-&gt;Start_simulation()</code> → 결과 XML 기록을 반복한다.</td></tr>
<tr><td><code>SSD_Device.h/cpp</code></td><td>"SSD 한 대"에 해당하는 조립 클래스. <code>Host_interface</code>, <code>Cache_manager</code>, <code>Firmware</code>(FTL), <code>PHY</code>, <code>Channels</code> 를 실제로 new 해서 서로 연결한다. 헤더 주석에 파이프라인 전체가 한 줄로 적혀 있다.</td></tr>
<tr><td><code>Host_System.h/cpp</code></td><td>workload 정의로부터 <code>IO_Flow</code> 들을 만들고 <code>SSD_Device</code> 에 붙이는(<code>Attach_ssd_device</code>) 역할.</td></tr>
<tr><td><code>Execution_Parameter_Set.h/cpp</code></td><td><code>ssdconfig.xml</code> 전체를 담는 최상위 컨테이너. <code>Host_Configuration</code>(Host_Parameter_Set) + <code>SSD_Device_Configuration</code>(Device_Parameter_Set) 두 덩어리로 나뉜다.</td></tr>
<tr><td><code>Device_Parameter_Set.h/cpp</code>, <code>Flash_Parameter_Set.h/cpp</code>, <code>Host_Parameter_Set.h/cpp</code>, <code>IO_Flow_Parameter_Set.h/cpp</code></td><td>XML 태그 하나하나를 그대로 멤버 변수로 들고 있는 설정 구조체 + <code>XML_serialize</code>/<code>XML_deserialize</code>. [MQSim 개요](/ftl-visual-simulator/mqsim/overview/)의 파라미터 표가 바로 이 파일들의 필드 목록이다.</td></tr>
<tr><td colspan="2" style="background:#2c3e50;color:#fff;font-weight:700;">sim/ — 이산 이벤트 엔진</th></tr>
<tr><td><code>Sim_Object.h</code></td><td>모든 시뮬레이션 구성요소의 베이스. 순수 가상 함수 <code>Execute_simulator_event()</code>( 이벤트 수신 진입점 ), <code>Start_simulation()</code>, <code>Validate_simulation_config()</code> 를 강제한다.</td></tr>
<tr><td><code>Sim_Event.h</code></td><td>이벤트 하나 = <code>{Fire_time, Target_sim_object, Parameters, Type}</code>. <code>Next_event</code> 포인터로 같은 시각 이벤트를 연결 리스트로 묶는다.</td></tr>
<tr><td><code>Engine.h/cpp</code></td><td>싱글턴( <code>Simulator</code> 매크로 ). <code>Register_sim_event()</code> 로 이벤트 등록, <code>Start_simulation()</code> 이 "가장 이른 이벤트 pop → 해당 객체의 <code>Execute_simulator_event</code> 호출"을 반복하는 메인 루프.</td></tr>
<tr><td><code>EventTree.h/cpp</code></td><td>Red-Black 트리로 구현된 이벤트 큐. 시각(<code>sim_time_type</code>)을 key 로 정렬해서 <code>Get_min_value()</code> 로 항상 가장 빠른 이벤트를 O(log n)에 꺼낸다.</td></tr>
<tr><td colspan="2" style="background:#475569;color:#fff;font-weight:700;">host/ + ssd/Host_Interface_* — Host 계층 ( 🔹 개념만 파악, 코드는 깊이 안 읽음 )</th></tr>
<tr><td colspan="2">
호스트가 요청을 SSD 에 전달하는 방식 — <b>이 프로젝트에서는 다음 개념만 알면 충분</b>.<br><br>
· <b>NVMe</b>(<code>Host_Interface_NVMe</code>) 는 스트림마다 독립된 SQ/CQ 링버퍼를 갖는 <b>multi-queue</b> 구조라서 여러 큐가 동시에 처리된다. <b>SATA</b>(<code>Host_Interface_SATA</code>) 는 큐가 하나뿐이다 — 이 차이 때문에 이 프로젝트는 NVMe 만 시연 대상으로 삼는다.<br>
· 워크로드는 <code>IO_Flow_Synthetic</code>(파라미터로 요청을 즉석 생성 — 주소분포/read비율/hot region 등)과 <code>IO_Flow_Trace_Based</code>(<code>tpcc-small.trace</code> 같은 실제 trace 재생)로 나뉘고, 둘 다 <code>Generate_next_request()</code> 라는 같은 인터페이스로 수렴한다.<br>
· <code>PCIe_Root_Complex/Switch/Link</code>, <code>SATA_HBA</code> 는 각 프로토콜의 물리 링크 지연시간 모델 — FTL 로직과 무관.<br><br>
<span style="color:#94a3b8;font-size:11px;">( 해당 파일 : IO_Flow_Base/Synthetic/Trace_Based, PCIe_Root_Complex/Switch/Link, SATA_HBA, Host_Interface_Base/NVMe/SATA — 총 3,640줄, 자세히 안 읽어도 됨 )</span>
</td></tr>
<tr><td colspan="2" style="background:#0d9488;color:#fff;font-weight:700;">ssd/ — FTL 4대 클래스 ( 🔸 이 프로젝트의 핵심, 줄 단위로 읽는 대상 )</th></tr>
<tr><td><code>FTL.h/cpp</code></td><td><code>NVM_Firmware</code> 를 상속하는 조립 클래스. <code>Address_Mapping_Unit</code>/<code>BlockManager</code>/<code>GC_and_WL_Unit</code>/<code>TSU</code>/<code>PHY</code> 5개 포인터를 멤버로 들고 생성자에서 순서대로 new 한다.<br><span style="color:#0d9488;font-weight:700;">📏 55 + 908 = 963줄</span></td></tr>
<tr><td><code>Address_Mapping_Unit_Base.h/cpp</code></td><td>매핑 계층의 추상 인터페이스. <code>Translate_lpa_to_ppa_and_dispatch()</code>( 요청 처리 진입점 )와, GC 가 LPA/블록에 거는 barrier 관련 함수( <code>Set_barrier_for_accessing_*</code> )들이 순수 가상으로 선언되어 있다.<br><span style="color:#0d9488;font-weight:700;">📏 118 + 46 = 164줄</span></td></tr>
<tr><td><code>Address_Mapping_Unit_Page_Level.h/cpp</code></td><td>실제로 쓰이는 매핑 구현( DFTL 스타일 ). <code>Cached_Mapping_Table</code>( LRU CMT ), <code>AddressMappingDomain</code>( 스트림별 GMT/GTD ), <code>query_cmt()</code>( CMT hit/miss 판정 ), <code>translate_lpa_to_ppa()</code>( 실제 PPA 할당/조회 )가 핵심.<br><span style="color:#0d9488;font-weight:700;">📏 204 + 1,935 = 2,139줄</span> — FTL 전체의 약 32%, 가장 큰 파일</td></tr>
<tr><td><code>Address_Mapping_Unit_Hybrid.h/cpp</code></td><td>⚠️ <b>모든 메서드가 빈 스텁이다</b>( <code>{}</code> 또는 <code>return 0</code> 뿐 ). log-block merge 로직이 실제로는 구현되어 있지 않음 — 아래 "정확성 노트" 참고.<br><span style="color:#0d9488;font-weight:700;">📏 52 + 53 = 105줄</span>(전부 빈 스텁)</td></tr>
<tr><td><code>Flash_Block_Manager_Base.h/cpp</code>, <code>Flash_Block_Manager.h/cpp</code></td><td>block/page 상태 관리. <code>Block_Pool_Slot_Type</code>(erase count, invalid bitmap, 상태 머신), <code>PlaneBookKeepingType</code>(free/valid/invalid 개수, Data_wf/GC_wf/Translation_wf, <code>Free_block_pool</code>).<br><span style="color:#0d9488;font-weight:700;">📏 114 + 244 + 30 + 152 = 540줄</span></td></tr>
<tr><td><code>GC_and_WL_Unit_Base.h/cpp</code>, <code>GC_and_WL_Unit_Page_Level.h/cpp</code></td><td><code>Check_gc_required()</code>(트리거 판단), <code>GC_is_in_urgent_mode()</code>(preemptible GC), victim 선정( GREEDY/RGA/RANDOM 계열/FIFO 6가지 정책의 실제 switch-case ), <code>run_static_wearleveling()</code>.<br><span style="color:#0d9488;font-weight:700;">📏 102 + 303 + 33 + 192 = 630줄</span></td></tr>
<tr><td><code>TSU_Base.h/cpp</code>, <code>TSU_FLIN.h/cpp</code>, <code>TSU_OutofOrder.h/cpp</code>, <code>TSU_Priority_OutOfOrder.h/cpp</code></td><td><code>Prepare_for_transaction_submit()</code>→<code>Submit_transaction()</code>→<code>Schedule()</code> 3단계 API. <code>Schedule()</code> 이 트랜잭션을 채널/칩별 큐에 분류하고, read&gt;write&gt;erase 우선순위로 실행시킨다( 정책별 세부 규칙만 다름 — 우리 설정은 <code>PRIORITY_OUT_OF_ORDER</code> ).<br><span style="color:#0d9488;font-weight:700;">📏 120+140 + 93+591 + 60+421 + 66+555 = 2,046줄</span> — 정책 4개 중 실제 쓰는 건 Priority_OutOfOrder 하나뿐이라 나머지는 참고용</td></tr>
<tr><td><code>Flash_Transaction_Queue.h/cpp</code></td><td>TSU 가 채널/칩/우선순위별로 들고 있는 실제 트랜잭션 큐 자료구조.<br><span style="color:#0d9488;font-weight:700;">📏 31 + 91 = 122줄</span></td></tr>
<tr><td colspan="2" style="text-align:right;font-weight:700;background:#ecfccb;color:#365314;">FTL 관련 코드 합계 → 963+164+2,139+105+540+630+2,046+122 = <span style="font-size:14px;">6,709줄</span>( MQSim 전체 19,309줄의 약 35% )</td></tr>
<tr><td colspan="2" style="background:#2c3e50;color:#fff;font-weight:700;">ssd/ — 그 밖의 지원 클래스 ( 참고용, FTL 은 아님 )</th></tr>
<tr><td><code>Data_Cache_Manager_Base.h/cpp</code></td><td>SSD 내부 DRAM 캐시 공통 로직. <code>estimate_dram_access_time()</code> 이 tRCD/tCL/tRP 기반으로 DRAM 접근 지연을 계산한다.</td></tr>
<tr><td><code>Data_Cache_Manager_Flash_Simple.h/cpp</code>, <code>_Flash_Advanced.h/cpp</code>, <code>Data_Cache_Flash.h/cpp</code></td><td>Simple 은 캐시 없이 바로 통과에 가까운 구현, Advanced 는 실제 캐시 라인 관리( 우리 설정의 <code>Caching_Mechanism=ADVANCED</code> ）가 쓰는 쪽.</td></tr>
<tr><td><code>NVM_PHY_Base.h/cpp</code>, <code>NVM_PHY_ONFI.h/cpp</code>, <code>NVM_PHY_ONFI_NVDDR2.h/cpp</code></td><td>FTL 과 물리 칩 사이의 컨트롤러. <code>Send_command_to_chip()</code> 이 실제 커맨드를 내려보내고, 완료 시 <code>ConnectToTransactionServicedSignal</code> 로 등록된 콜백( AMU/GC/TSU 각자 )을 깨운다.</td></tr>
<tr><td><code>ONFI_Channel_Base.h/cpp</code>, <code>ONFI_Channel_NVDDR2.h/cpp</code></td><td>채널 하나의 버스 점유 상태(<code>BusChannelStatus</code>) 관리 — 같은 채널의 여러 칩이 동시에 전송할 수 없는 이유가 여기.</td></tr>
<tr><td><code>NVM_Transaction.h</code>, <code>NVM_Transaction_Flash.h/cpp</code>, <code>_RD/_WR/_ER.h/cpp</code></td><td>flash 트랜잭션 하나의 데이터 모델. <code>Source</code>(USERIO/CACHE/MAPPING/GC_WL), <code>Type</code>(READ/WRITE/ERASE), <code>Address</code>, <code>LPA</code>/<code>PPA</code> — TSU 의 큐 분류·우선순위가 전부 이 두 필드(Source, Type) 기준.</td></tr>
<tr><td><code>Stats.h/cpp</code></td><td>전역 정적 카운터 모음. <code>Total_gc_executions</code>, <code>CMT_hits</code>/<code>CMT_miss</code>, <code>Total_page_movements_for_gc</code> 등 — hook 이 잡아야 할 이벤트와 최종 카운터를 1:1로 대조할 때 기준이 되는 파일.</td></tr>
<tr><td><code>User_Request.h/cpp</code></td><td>호스트 요청 하나( 여러 섹터에 걸칠 수 있음 )가 여러 개의 <code>NVM_Transaction_Flash</code> 로 쪼개지기 전의 상위 단위.</td></tr>
<tr><td colspan="2" style="background:#2c3e50;color:#fff;font-weight:700;">nvm_chip/flash_memory/ — 물리 NAND 모델</th></tr>
<tr><td><code>Flash_Chip.h/cpp</code></td><td>칩 하나. <code>Get_command_execution_latency()</code> 가 MLC/TLC 기술과 페이지 위치(LSB/CSB/MSB)에 따라 다른 지연시간을 반환. <code>Suspend()</code>/<code>Resume()</code> 으로 erase/program suspend 를 지원.</td></tr>
<tr><td><code>Die.h/cpp</code>, <code>Plane.h/cpp</code>, <code>Block.h/cpp</code>, <code>Page.h</code></td><td>Chip→Die→Plane→Block→Page 물리 계층 그대로. <code>Page</code> 는 <code>Metadata.LPA</code> 하나만 들고 있는 아주 얇은 클래스 — 실제 valid/invalid 상태는 <code>Block_Pool_Slot_Type.Invalid_page_bitmap</code>( <code>Flash_Block_Manager</code> 쪽 )에서 관리된다는 점이 처음 읽을 때 헷갈리는 부분.</td></tr>
<tr><td><code>Physical_Page_Address.h/cpp</code></td><td>{ChannelID, ChipID, DieID, PlaneID, BlockID, PageID} 6-tuple. 이 프로젝트의 모든 물리 주소가 이 구조체 하나로 표현된다.</td></tr>
<tr><td colspan="2" style="background:#2c3e50;color:#fff;font-weight:700;">utils/ · 기타</th></tr>
<tr><td><code>XMLWriter.h/cpp</code></td><td>결과를 <code>workload_scenario_N.xml</code> 로 직렬화. <code>Write_open_tag</code>/<code>Write_close_tag</code> 스타일의 최소 XML writer.</td></tr>
<tr><td><code>Logical_Address_Partitioning_Unit.h/cpp</code></td><td>여러 I/O 스트림에 채널/칩/다이/플레인을 어떻게 나눠줄지 계산 — preconditioning 때 스트림별 물리 공간 배분에 쓰인다.</td></tr>
<tr><td><code>RandomGenerator.h/cpp</code>, <code>CMRRandomGenerator.h/cpp</code>, <code>DistributionTypes.h</code></td><td>시드 기반 난수 생성기( workload 주소/크기/도착시간 분포, GC 의 RANDOM 계열 정책이 모두 이걸 사용 ).</td></tr>
<tr><td><code>Workload_Statistics.h</code>, <code>StringTools.h/cpp</code>, <code>Helper_Functions.h/cpp</code>, <code>Sim_Defs.h</code>, <code>Sim_Reporter.h</code>, <code>FlashTypes.h</code>, <code>NVM_Types.h</code>, <code>NVM_Chip.h</code>, <code>Flash_Command.h</code>, <code>Host_IO_Request.h</code>, <code>Host_Interface_Defs.h</code>, <code>PCIe_Message.h</code>, <code>ASCII_Trace_Definition.h</code>, <code>Queue_Probe.h/cpp</code></td><td>타입 정의/문자열 파싱/난수 시드 관리용 보조 파일. 로직이 아니라 자료구조·상수 선언 위주라 hook 대상은 아님.</td></tr>
</table>
</div>

### ⚠️ 정확성 노트 — Hybrid 매핑은 실제로 구현되어 있지 않다

`Address_Mapping_Unit_Hybrid.cpp` 전체( 53줄 )를 직접 열어 확인한 결과, **모든 메서드 본문이 비어 있거나(`{}`) 고정값만 반환한다(`return 0`)**. 즉 log-block 방식(FAST, switch/partial/full merge)이 코드로 존재하지 않고, 클래스 골격( `Address_Mapping_Unit_Base` 를 상속하는 자리표시자 )만 있다.

- 기존 [개발 계획](/ftl-visual-simulator/plan/) Session 6 과 [코드 분석 계획](/ftl-visual-simulator/mqsim/code-analysis-plan/) Session 6 은 "hybrid 매핑이 이미 구현되어 있으니 hook 만 추가하면 된다"고 전제하고 있었는데, 이 전제가 **틀렸다**.
- 실제로 hybrid 매핑을 시각화하려면 Cost-Benefit GC( 확장 목표 7번 )처럼 **직접 구현**해야 하는 작업이 된다 — page-level 매핑처럼 "이미 있는 로직에 hook만 추가"가 아니라 새로운 기능 개발.
- 두 가지 선택지가 있다 : (1) Session 6 범위를 hybrid 매핑 없이 wear-leveling( 이건 `GC_and_WL_Unit_Page_Level.cpp` 에 실제로 구현되어 있음, 확인됨 )만으로 축소하고 hybrid 매핑은 13~16번 버퍼( Cost-Benefit GC 와 같은 성격의 확장 목표 )로 미룬다, 또는 (2) 애초 계획대로 Session 6 에서 hybrid 매핑을 직접 구현한다. 시간이 빠듯한 1차 마감(10/11) 사정을 고려하면 (1)이 안전하다 — 계획 수정은 [개발 계획](/ftl-visual-simulator/plan/) 문서에서 별도로 반영 필요.

<div style="margin-top: 60px;"></div>

## 7. 주요 콜 플로우

지금까지의 클래스별 설명을 실제 실행 순서로 다시 엮은 것. 색상은 어느 서브시스템을 지나는지 표시( <span style="color:#2563eb;font-weight:700;">파랑=Host/NVMe</span> · <span style="color:#7c3aed;font-weight:700;">보라=Cache</span> · <span style="color:#0d9488;font-weight:700;">청록=Address Mapping</span> · <span style="color:#d97706;font-weight:700;">주황=Block Manager</span> · <span style="color:#e11d48;font-weight:700;">빨강=GC</span> · <span style="color:#16a34a;font-weight:700;">초록=Wear-Leveling</span> · <span style="color:#4f46e5;font-weight:700;">남색=TSU</span> · <span style="color:#475569;font-weight:700;">회색=PHY/Channel/Chip</span> ).

<div style="margin-top: 40px;"></div>

### 7-1. Write 요청 전체 흐름

<div style="overflow-x:auto;">
<svg viewBox="0 0 1180 320" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs>
    <marker id="arrow-ca1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker>
  </defs>
  <style>
    .t-ca1{font-size:13px;font-weight:700;text-anchor:middle;}
    .b-ca1{font-size:10.5px;text-anchor:middle;}
    .n-ca1{font-size:11px;font-weight:700;text-anchor:middle;fill:#fff;}
    .f-ca1{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-ca1);fill:none;}
  </style>

  <rect x="10" y="30" width="150" height="70" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <circle cx="30" cy="45" r="10" fill="#2563eb"/><text x="30" y="49" class="n-ca1">1</text>
  <text x="90" y="55" class="t-ca1" fill="#1e3a8a">Host_Interface_NVMe</text>
  <text x="90" y="72" class="b-ca1" fill="#1e3a8a">SQE fetch, WRITE 요청</text>
  <text x="90" y="87" class="b-ca1" fill="#1e3a8a">User_Request 생성</text>

  <line x1="160" y1="65" x2="200" y2="65" class="f-ca1"/>

  <rect x="200" y="30" width="150" height="70" rx="8" fill="#ede9fe" stroke="#7c3aed" stroke-width="2"/>
  <circle cx="220" cy="45" r="10" fill="#7c3aed"/><text x="220" y="49" class="n-ca1">2</text>
  <text x="280" y="55" class="t-ca1" fill="#4c1d95">Data_Cache_Manager</text>
  <text x="280" y="72" class="b-ca1" fill="#4c1d95">DRAM 캐시에 먼저</text>
  <text x="280" y="87" class="b-ca1" fill="#4c1d95">반영 (WRITE_CACHE)</text>

  <line x1="350" y1="65" x2="390" y2="65" class="f-ca1"/>

  <rect x="390" y="10" width="190" height="110" rx="8" fill="#ccfbf1" stroke="#0d9488" stroke-width="2"/>
  <circle cx="410" cy="25" r="10" fill="#0d9488"/><text x="410" y="29" class="n-ca1">3</text>
  <text x="485" y="35" class="t-ca1" fill="#134e4a">Address_Mapping_Unit</text>
  <text x="485" y="55" class="b-ca1" fill="#134e4a">query_cmt() — CMT hit?</text>
  <text x="485" y="70" class="b-ca1" fill="#134e4a">miss면 Waiting_unmapped_</text>
  <text x="485" y="83" class="b-ca1" fill="#134e4a">program_transactions 대기</text>
  <text x="485" y="100" class="b-ca1" fill="#134e4a" font-style="italic">translate_lpa_to_ppa()</text>

  <line x1="580" y1="65" x2="620" y2="65" class="f-ca1"/>

  <rect x="620" y="30" width="160" height="70" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <circle cx="640" cy="45" r="10" fill="#d97706"/><text x="640" y="49" class="n-ca1">4</text>
  <text x="700" y="55" class="t-ca1" fill="#78350f">Flash_Block_Manager</text>
  <text x="700" y="72" class="b-ca1" fill="#78350f">allocate_page_in_plane</text>
  <text x="700" y="87" class="b-ca1" fill="#78350f">_for_user_write()</text>

  <line x1="700" y1="100" x2="700" y2="150" class="f-ca1"/>
  <text x="835" y="140" class="b-ca1" fill="#e11d48">write frontier 블록이 다 차면 →</text>
  <rect x="620" y="150" width="240" height="70" rx="8" fill="#ffe4e6" stroke="#e11d48" stroke-width="2"/>
  <circle cx="640" cy="165" r="10" fill="#e11d48"/><text x="640" y="169" class="n-ca1">4b</text>
  <text x="740" y="175" class="t-ca1" fill="#881337">GC_and_WL_Unit</text>
  <text x="740" y="192" class="b-ca1" fill="#881337">Check_gc_required() 트리거</text>
  <text x="740" y="207" class="b-ca1" fill="#881337">(7-3절 GC 흐름으로 분기)</text>

  <line x1="780" y1="65" x2="820" y2="65" class="f-ca1"/>

  <rect x="820" y="30" width="140" height="70" rx="8" fill="#e0e7ff" stroke="#4f46e5" stroke-width="2"/>
  <circle cx="840" cy="45" r="10" fill="#4f46e5"/><text x="840" y="49" class="n-ca1">5</text>
  <text x="890" y="55" class="t-ca1" fill="#312e81">TSU</text>
  <text x="890" y="72" class="b-ca1" fill="#312e81">Submit_transaction()</text>
  <text x="890" y="87" class="b-ca1" fill="#312e81">→ Schedule()</text>

  <line x1="960" y1="65" x2="1000" y2="65" class="f-ca1"/>

  <rect x="1000" y="30" width="170" height="70" rx="8" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>
  <circle cx="1020" cy="45" r="10" fill="#475569"/><text x="1020" y="49" class="n-ca1">6</text>
  <text x="1085" y="55" class="t-ca1" fill="#1e293b">ONFI_Channel + Chip</text>
  <text x="1085" y="72" class="b-ca1" fill="#1e293b">CMD_PROGRAM_PAGE</text>
  <text x="1085" y="87" class="b-ca1" fill="#1e293b">program latency 경과</text>

  <line x1="1085" y1="100" x2="1085" y2="260" class="f-ca1"/>
  <line x1="1085" y1="260" x2="90" y2="260" class="f-ca1"/>
  <text x="600" y="252" class="b-ca1" fill="#475569">완료 시 ConnectToTransactionServicedSignal 콜백 → AMU 매핑 확정, 이전 PPA invalidate(7절 후반)</text>
  <rect x="10" y="240" width="150" height="40" rx="8" fill="#ecfccb" stroke="#65a30d" stroke-width="2"/>
  <text x="85" y="264" class="t-ca1" fill="#365314">Stats 갱신</text>
</svg>
</div>

**단계별 설명**

1. `Host_Interface_NVMe::Request_Fetch_Unit_NVMe::Fetch_next_request()` 가 NVMe 제출 큐(SQ)에서 명령을 DMA 로 읽어와 `User_Request` 를 만든다.
2. `Data_Cache_Manager` 가 `Caching_Mode::WRITE_CACHE` 설정에 따라 DRAM 캐시에 먼저 데이터를 반영한다( 캐시 자체의 접근 지연은 `estimate_dram_access_time()` 으로 계산 ).
3. `Address_Mapping_Unit_Page_Level::query_cmt()` 가 CMT( Cached Mapping Table )에서 LPA 를 조회한다. hit 이면 바로 `translate_lpa_to_ppa()`, miss 면 `request_mapping_entry()` 로 매핑 페이지를 flash 에서 읽어와야 하고, 그마저 안 되면 `Waiting_unmapped_program_transactions` 에 넣고 대기시킨다.
4. `translate_lpa_to_ppa()` 안에서 write 요청은 `allocate_plane_for_user_write()` 로 plane 을 정한 뒤, **두 가지 GC 관련 검사**를 차례로 거친다( 코드로 직접 확인한 순서 ) —
   - **4a. 하드 블록** : `GC_and_WL_Unit::Stop_servicing_writes()` 가 `block_manager->Get_pool_size() < max_ongoing_gc_reqs_per_plane`( 기본값 10 — free 블록이 정말 얼마 안 남았을 때 )이면 true 를 반환하고, 이 write 트랜잭션은 **그 자리에서 실패 처리**된다( "there are too few free pages remaining only for GC"라는 소스 코드 주석 그대로 ).
   - **4b. GC 트리거** : 통과하면 `allocate_page_in_plane_for_user_write()` 가 실제 PPA 를 할당하는데, 이때 write frontier( `Data_wf` ) 블록이 **가득 차서**( `Current_page_write_index == pages_no_per_block` ) 새 free 블록으로 교체되는 순간에만 `GC_and_WL_Unit::Check_gc_required()` 가 불려 GC 가 트리거된다( 매 쓰기마다가 아니라 블록 하나를 다 썼을 때만 — 자세한 내용은 7-3절 ).
5. PPA 가 확정되면 `ftl->TSU->Submit_transaction()` 으로 트랜잭션이 제출되고, 리스트 처리가 끝나면 `ftl->TSU->Schedule()` 이 한 번 호출된다( 7-4절 참고 — die/plane-level 병렬성을 살리기 위해 여러 트랜잭션을 모아서 한 번에 스케줄링 ).
6. TSU 가 채널이 idle 이 되는 시점에 `NVM_PHY_ONFI::Send_command_to_chip()` 으로 `CMD_PROGRAM_PAGE` 를 내려보낸다. `Flash_Chip::Get_command_execution_latency()` 가 MLC 기준 750,000ns( `Page_Program_Latency_*` ) 지연을 계산해 완료 이벤트를 예약한다.
7. 커맨드가 끝나면 PHY 가 `broadcastTransactionServicedSignal()` 로 콜백을 호출 — `Flash_Block_Manager::Program_transaction_serviced()`( block bookkeeping 갱신 ), 필요하면 기존 PPA 를 `Invalidate_page_in_block()` 으로 무효화, `Stats` 카운터 갱신까지 이어진다.

<div style="margin-top: 60px;"></div>

### 7-2. Read 요청 흐름 — CMT hit vs miss

<div style="overflow-x:auto;">
<svg viewBox="0 0 1000 260" style="width:100%;max-width:860px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-ca2" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t-ca2{font-size:12.5px;font-weight:700;text-anchor:middle;}
    .b-ca2{font-size:10px;text-anchor:middle;}
    .f-ca2{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-ca2);fill:none;}
    .diamond-ca2{fill:#fff6df;stroke:#b8860b;stroke-width:2;}
  </style>

  <rect x="10" y="90" width="150" height="60" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="85" y="115" class="t-ca2" fill="#1e3a8a">NVMe READ</text>
  <text x="85" y="132" class="b-ca2" fill="#1e3a8a">요청 도착</text>

  <line x1="160" y1="120" x2="200" y2="120" class="f-ca2"/>

  <polygon points="200,90 290,120 200,150 110,120" class="diamond-ca2" transform="translate(90,0)"/>
  <text x="380" y="115" class="t-ca2">CMT 에</text>
  <text x="380" y="130" class="t-ca2">있나?</text>

  <line x1="470" y1="120" x2="510" y2="120" class="f-ca2"/>
  <text x="490" y="108" class="b-ca2" fill="#0d9488">HIT</text>

  <rect x="510" y="90" width="180" height="60" rx="8" fill="#ccfbf1" stroke="#0d9488" stroke-width="2"/>
  <text x="600" y="115" class="t-ca2" fill="#134e4a">translate_lpa_to_ppa()</text>
  <text x="600" y="132" class="b-ca2" fill="#134e4a">CMT->Retrieve_ppa()</text>

  <line x1="470" y1="150" x2="470" y2="210" class="f-ca2"/>
  <text x="500" y="185" class="b-ca2" fill="#e11d48">MISS</text>

  <rect x="330" y="210" width="280" height="40" rx="8" fill="#ffe4e6" stroke="#e11d48" stroke-width="2"/>
  <text x="470" y="228" class="t-ca2" fill="#881337">request_mapping_entry()</text>
  <text x="470" y="242" class="b-ca2" fill="#881337">generate_flash_read_request_for_mapping_data()</text>

  <line x1="610" y1="230" x2="700" y2="230" class="f-ca2"/>
  <line x1="700" y1="230" x2="700" y2="150" class="f-ca2"/>
  <line x1="700" y1="150" x2="690" y2="150" class="f-ca2"/>
  <text x="770" y="200" class="b-ca2">매핑 페이지 read 완료 후</text>
  <text x="770" y="214" class="b-ca2">online_create_entry_for_reads()</text>
  <text x="770" y="228" class="b-ca2">로 CMT에 새 entry 삽입 후 재시도</text>

  <line x1="690" y1="120" x2="730" y2="120" class="f-ca2"/>

  <rect x="730" y="90" width="150" height="60" rx="8" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>
  <text x="805" y="115" class="t-ca2" fill="#1e293b">CMD_READ_PAGE</text>
  <text x="805" y="132" class="b-ca2" fill="#1e293b">Chip 에서 실행</text>
</svg>
</div>

**단계별 설명**

1. `query_cmt()` 가 `Mapping_entry_accessible()` 로 CMT 존재 여부를 확인한다.
2. **HIT** — 바로 `translate_lpa_to_ppa()` → `domains[stream]->Get_ppa()` 로 PPA 를 얻고, `Read_transaction_issued()` 로 block bookkeeping 을 갱신한 뒤 TSU 로 넘어간다.
3. **MISS** — `request_mapping_entry()` 가 먼저 "혹시 지금 write-back 중인 항목에서 잡을 수 있는지"를 확인하고, 안 되면 `generate_flash_read_request_for_mapping_data()` 로 매핑 테이블 페이지(MVPN/MPPN, GTD 항목) 자체를 flash 에서 읽어오는 **별도의 flash read 트랜잭션**을 만든다.
4. 이 매핑 read 가 끝나면 `online_create_entry_for_reads()` 가 CMT 에 새 entry 를 채우고, 원래 대기 중이던 `Waiting_unmapped_read_transactions` 를 다시 꺼내 처리한다.
5. 이 "매핑 자체를 읽어와야 하는" 2단계 구조가 바로 DFTL 류 캐시가 page-level 풀매핑보다 read 지연이 더 걸릴 수 있는 이유이고, `Stats::readTR_CMT_miss` 카운터로 빈도를 추적한다.

<div style="margin-top: 60px;"></div>

### 7-3. GC 흐름 — 트리거부터 정책별 victim 선정까지

<div style="overflow-x:auto;">
<svg viewBox="0 0 1080 230" style="width:100%;max-width:920px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-ca3" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t-ca3{font-size:12px;font-weight:700;text-anchor:middle;}
    .b-ca3{font-size:9.5px;text-anchor:middle;}
    .f-ca3{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-ca3);fill:none;}
  </style>
  <rect x="10" y="70" width="150" height="70" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="85" y="95" class="t-ca3" fill="#78350f">free_block_pool</text>
  <text x="85" y="112" class="b-ca3" fill="#78350f">&lt; block_pool_gc</text>
  <text x="85" y="125" class="b-ca3" fill="#78350f">_threshold ?</text>

  <line x1="160" y1="105" x2="200" y2="105" class="f-ca3"/>

  <rect x="200" y="10" width="230" height="190" rx="8" fill="#ffe4e6" stroke="#e11d48" stroke-width="2"/>
  <text x="315" y="30" class="t-ca3" fill="#881337">block_selection_policy 별 victim 선정</text>
  <text x="215" y="52" class="b-ca3" fill="#881337" text-anchor="start">GREEDY : 전 블록 스캔, invalid 최다 &amp; full</text>
  <text x="215" y="70" class="b-ca3" fill="#881337" text-anchor="start">RGA : log2(N)개 무작위 셋 중 invalid 최다</text>
  <text x="215" y="88" class="b-ca3" fill="#881337" text-anchor="start">RANDOM : 안전 조건만 만족하면 무작위</text>
  <text x="215" y="106" class="b-ca3" fill="#881337" text-anchor="start">RANDOM_P : + full block 만</text>
  <text x="215" y="124" class="b-ca3" fill="#881337" text-anchor="start">RANDOM_PP : + invalid ≥ threshold</text>
  <text x="215" y="142" class="b-ca3" fill="#881337" text-anchor="start">FIFO : Block_usage_history 큐에서 pop</text>
  <text x="215" y="164" class="b-ca3" fill="#881337" font-style="italic" text-anchor="start">공통 조건 : is_safe_gc_wl_candidate()</text>
  <text x="215" y="180" class="b-ca3" fill="#881337" font-style="italic" text-anchor="start">— write frontier 아님 + 진행 중 program 없음</text>

  <line x1="430" y1="105" x2="470" y2="105" class="f-ca3"/>

  <rect x="470" y="70" width="150" height="70" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="545" y="95" class="t-ca3" fill="#78350f">block_manager</text>
  <text x="545" y="112" class="b-ca3" fill="#78350f">GC_WL_started()</text>
  <text x="545" y="125" class="b-ca3" fill="#78350f">barrier 설정</text>

  <line x1="620" y1="105" x2="660" y2="105" class="f-ca3"/>

  <rect x="660" y="10" width="190" height="70" rx="8" fill="#0d9488" fill-opacity="0.15" stroke="#0d9488" stroke-width="2"/>
  <text x="755" y="30" class="t-ca3" fill="#134e4a">valid page migration</text>
  <text x="755" y="50" class="b-ca3" fill="#134e4a">Get_data_mapping_info_for_gc()</text>
  <text x="755" y="65" class="b-ca3" fill="#134e4a">→ read 후 새 PPA 에 재기록</text>

  <line x1="660" y1="105" x2="660" y2="45" class="f-ca3"/>
  <line x1="660" y1="105" x2="660" y2="165" class="f-ca3"/>

  <rect x="660" y="130" width="190" height="70" rx="8" fill="#16a34a" fill-opacity="0.15" stroke="#16a34a" stroke-width="2"/>
  <text x="755" y="150" class="t-ca3" fill="#14532d">(옵션) static WL</text>
  <text x="755" y="170" class="b-ca3" fill="#14532d">check_static_wl_required()</text>
  <text x="755" y="185" class="b-ca3" fill="#14532d">erase count 편차 &gt; threshold</text>

  <line x1="850" y1="105" x2="890" y2="105" class="f-ca3"/>

  <rect x="890" y="70" width="170" height="70" rx="8" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>
  <text x="975" y="95" class="t-ca3" fill="#1e293b">CMD_ERASE_BLOCK</text>
  <text x="975" y="112" class="b-ca3" fill="#1e293b">Erase_count++</text>
  <text x="975" y="125" class="b-ca3" fill="#1e293b">Add_erased_block_to_pool()</text>
</svg>
</div>

**단계별 설명 — `GC_and_WL_Unit_Page_Level::Check_gc_required()` 실측 로직**

1. `free_block_pool_size < block_pool_gc_threshold`( `GC_Exec_Threshold=0.05` 로부터 계산된 절대 개수 )이면 GC 후보를 찾기 시작한다. 이미 이 plane 에서 동시 진행 중인 erase 가 `max_ongoing_gc_reqs_per_plane`( 기본 10 )을 넘으면 즉시 리턴.
2. `GC_Block_Selection_Policy_Type` 6가지 정책이 실제로 어떻게 다른지( 코드에서 직접 확인한 조건 ) —
   - **GREEDY** : 0번 블록부터 끝까지 순회하며 "가득 찼고(`Current_page_write_index == pages_no_per_block`) invalid page 가 가장 많은" 블록을 선택.
   - **RGA**( 기본 설정값 ) : `rga_set_size = log2(block_no_per_plane)`( 2048개 블록이면 11개 ) 만큼 무작위로 뽑은 안전한 후보 집합 중에서만 invalid 최다 블록을 고른다 — 전수 조사(GREEDY)보다 훨씬 싸면서 근사적으로 비슷한 효과.
   - **RANDOM/RANDOM_P/RANDOM_PP** : 무작위 블록을 뽑되 각각 "안전 조건만", "+ 가득 찬 블록만", "+ invalid page 수가 `random_pp_threshold` 이상"이라는 조건을 추가로 만족할 때까지 재추첨.
   - **FIFO** : 선정 로직이 없다 — `Block_usage_history` 큐(사용 순서 기록)에서 그냥 맨 앞을 꺼낸다.
   - 6개 정책 모두 공통으로 `is_safe_gc_wl_candidate()`( write frontier 가 아니고, 해당 블록에 진행 중인 program 요청이 없어야 함 )를 만족해야 한다.
3. 후보가 확정되면 `block_manager->GC_WL_started()` 로 블록 상태를 `Block_Service_Status::GC_WL` 로 바꾸고, `address_mapping_unit->Set_barrier_for_accessing_physical_block()` 로 барrier 를 걸어 이 블록의 LPA 들에 대한 새 요청을 막는다.
4. `block->Current_page_write_index - block->Invalid_page_count > 0`( 살아있는 valid page 가 있음 )이면 그 수만큼 `NVM_Transaction_Flash_RD`(읽기) + 이어지는 write(새 위치에 재기록) 쌍을 생성한다 — 이게 GC 로 인한 "추가 쓰기"(Write Amplification 의 원인)다.
5. 모든 valid page 이동이 끝나면 `NVM_Transaction_Flash_ER`( erase )가 실행되고, `Stats::Total_gc_executions++`, 블록의 `Erase_count++` 후 `Add_erased_block_to_pool()` 로 free pool 에 반환된다.
6. ⚠️ **Dynamic wear-leveling 은 GC victim 선정과는 무관한, 별도의 명시적 메커니즘이다**( 정정 — 이전에는 "RGA/RANDOM 의 확률적 선택에 자연히 녹아있다"고 잘못 적었었음 ). erase 가 끝나 블록이 `Flash_Block_Manager::Add_erased_block_to_pool()` 로 free pool 에 반환될 때, `Dynamic_Wearleveling_Enabled` 가 true 면 `PlaneBookKeepingType::Add_to_free_block_pool()` 이 그 블록을 **실제 erase count 를 key 로** free pool(`multimap`)에 넣는다. 다음에 write frontier 가 필요할 때 `Get_a_free_block()` 은 **항상 이 multimap 에서 key 가 가장 작은(=erase count 가 가장 낮은) 블록**을 꺼낸다 — 즉 "가장 적게 지워진 블록을 다음 쓰기 대상으로 우선 배정"하는 방식으로 마모를 분산시키며, GC 의 victim 선정 정책(RGA 등)과는 완전히 다른, **쓰기 쪽(free pool 배정)에서 일어나는 로직**이다.
7. **Static wear-leveling** 은 GC/dynamic WL 로도 못 잡는 케이스를 위한 세 번째 보정 — 코드 위치도 다르다(`GC_and_WL_Unit_Base.cpp`, `Page_Level.cpp` 가 아님). erase 가 끝날 때마다 `check_static_wl_required()` 가 "이 plane 의 최대/최소 erase count 차이가 `Static_Wearleveling_Threshold`(기본 100) 이상인지"를 확인해서, 그렇다면 `run_static_wearleveling()` 이 **erase count 가 가장 낮은(`Get_coldest_block_id()`) 블록**을 강제로 골라 옮겨 쓰고 지운다 — GC 트리거(`Check_gc_required`)와는 완전히 독립된 경로.

<div style="margin-top: 60px;"></div>

### 7-4. TSU 스케줄링 내부 흐름

<div style="overflow-x:auto;">
<svg viewBox="0 0 1020 260" style="width:100%;max-width:880px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-ca4" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t-ca4{font-size:12px;font-weight:700;text-anchor:middle;}
    .b-ca4{font-size:9.5px;text-anchor:middle;}
    .f-ca4{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-ca4);fill:none;}
  </style>
  <rect x="10" y="100" width="150" height="60" rx="8" fill="#e0e7ff" stroke="#4f46e5" stroke-width="2"/>
  <text x="85" y="123" class="t-ca4" fill="#312e81">transaction</text>
  <text x="85" y="140" class="b-ca4" fill="#312e81">_receive_slots</text>

  <line x1="160" y1="130" x2="200" y2="130" class="f-ca4"/>

  <rect x="200" y="10" width="230" height="230" rx="8" fill="#e0e7ff" fill-opacity="0.5" stroke="#4f46e5" stroke-width="2"/>
  <text x="315" y="30" class="t-ca4" fill="#312e81">Source × Type 별 큐 분류</text>
  <text x="215" y="55" class="b-ca4" fill="#312e81" text-anchor="start">USERIO/CACHE, READ → UserReadTRQueue[ch][chip][priority]</text>
  <text x="215" y="75" class="b-ca4" fill="#312e81" text-anchor="start">USERIO/CACHE, WRITE → UserWriteTRQueue[ch][chip][priority]</text>
  <text x="215" y="95" class="b-ca4" fill="#312e81" text-anchor="start">MAPPING, READ/WRITE → MappingRead/WriteTRQueue[ch][chip]</text>
  <text x="215" y="115" class="b-ca4" fill="#312e81" text-anchor="start">GC_WL, READ/WRITE → GCRead/WriteTRQueue[ch][chip]</text>
  <text x="215" y="135" class="b-ca4" fill="#312e81" text-anchor="start">ERASE(전부 GC_WL) → GCEraseTRQueue[ch][chip]</text>
  <text x="215" y="160" class="b-ca4" fill="#312e81" font-style="italic" text-anchor="start">우선순위 큐는 IO_Flow_Priority_Class</text>
  <text x="215" y="176" class="b-ca4" fill="#312e81" font-style="italic" text-anchor="start">(HIGH/...) 별로 별도 큐</text>
  <text x="215" y="200" class="b-ca4" fill="#312e81" font-style="italic" text-anchor="start">채널×칩 2차원 배열이라 die/plane</text>
  <text x="215" y="216" class="b-ca4" fill="#312e81" font-style="italic" text-anchor="start">레벨 병렬성을 그대로 노출</text>

  <line x1="430" y1="130" x2="470" y2="130" class="f-ca4"/>

  <rect x="470" y="100" width="180" height="60" rx="8" fill="#e0e7ff" stroke="#4f46e5" stroke-width="2"/>
  <text x="560" y="123" class="t-ca4" fill="#312e81">채널별 라운드로빈</text>
  <text x="560" y="140" class="b-ca4" fill="#312e81">Round_robin_turn_of_channel[ch]</text>

  <line x1="650" y1="130" x2="690" y2="130" class="f-ca4"/>

  <rect x="690" y="30" width="230" height="200" rx="8" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>
  <text x="805" y="50" class="t-ca4" fill="#1e293b">칩 하나당 우선순위</text>
  <text x="805" y="80" class="t-ca4" fill="#1e293b">service_read_transaction()</text>
  <text x="805" y="100" class="b-ca4" fill="#1e293b">실패하면 ↓</text>
  <text x="805" y="125" class="t-ca4" fill="#1e293b">service_write_transaction()</text>
  <text x="805" y="145" class="b-ca4" fill="#1e293b">실패하면 ↓</text>
  <text x="805" y="170" class="t-ca4" fill="#1e293b">service_erase_transaction()</text>
  <text x="805" y="195" class="b-ca4" fill="#1e293b" font-style="italic">채널이 idle 일 때만 시도,</text>
  <text x="805" y="210" class="b-ca4" fill="#1e293b" font-style="italic">성공하면 다음 채널로</text>
</svg>
</div>

**단계별 설명 — `TSU_Priority_OutOfOrder::Schedule()` 실측 로직**

1. `Prepare_for_transaction_submit()`/`Submit_transaction()` 으로 모인 트랜잭션들이 `Schedule()` 호출 시점에 한꺼번에 처리된다( `opened_scheduling_reqs` 카운터로 중첩 호출을 하나로 합침 — die/plane 레벨 병렬성을 살리려고 여러 트랜잭션을 모아서 스케줄 ).
2. 각 트랜잭션은 `Type`(READ/WRITE/ERASE) × `Source`(USERIO/CACHE, MAPPING, GC_WL) 조합으로 서로 다른 큐에 들어간다 — **사용자 요청, 매핑 테이블 접근, GC 페이지 이동이 처음부터 물리적으로 분리된 큐를 쓴다**는 점이 중요( 우리 이벤트 로그에서 "이 트랜잭션이 왜 지금 실행됐는지" 설명할 때 소스 구분의 근거 ).
3. 채널 하나씩 순회하며, 그 채널이 `BusChannelStatus::IDLE` 이면 `Round_robin_turn_of_channel[channelID]` 가 가리키는 칩부터 순서대로 시도한다 — 특정 칩만 계속 서비스되는 것을 막는 라운드로빈.
4. 칩 하나에 대해 **read > write > erase** 순서로 서비스를 시도하고( `process_chip_requests()` ), 하나라도 성공하면 그 칩 순번을 다음으로 넘기고 다음 칩으로 넘어간다. 이 우선순위 때문에 read 요청이 섞여 있으면 GC/매핑 write 보다 먼저 실행된다.
5. `service_read_transaction()` 내부의 실제 우선순위( 코드로 직접 확인 ) : **매핑(`MappingReadTRQueue`) 관련 트랜잭션이 항상 최우선** — 소스 코드 주석 그대로 "Flash transactions that are related to FTL mapping data have the highest priority". 그 다음은 `GC_is_in_urgent_mode()` 여부로 갈린다 — urgent 면 `GCReadTRQueue` 가 `UserReadTRQueue` 보다 먼저, urgent 가 아니면(preemptible) 그 반대. 우리 설정은 `Preemptible_GC_Enabled=false` 라서 `GC_is_in_urgent_mode()` 가 항상 true 를 반환 → **실질적으로 항상 "매핑 &gt; GC &gt; 사용자" 순서**가 된다.

<div style="margin-top: 60px;"></div>

### 7-5. NVMe multi-queue 요청 수신 흐름

<div style="overflow-x:auto;">
<svg viewBox="0 0 980 240" style="width:100%;max-width:840px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-ca5" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t-ca5{font-size:12px;font-weight:700;text-anchor:middle;}
    .b-ca5{font-size:9.5px;text-anchor:middle;}
    .f-ca5{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-ca5);fill:none;}
  </style>
  <rect x="10" y="20" width="220" height="80" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="120" y="42" class="t-ca5" fill="#1e3a8a">Host — Submission Queue</text>
  <text x="120" y="62" class="b-ca5" fill="#1e3a8a">SQ tail++ (새 커맨드 push)</text>
  <text x="120" y="78" class="b-ca5" fill="#1e3a8a">Submission_queue_tail_pointer_update()</text>

  <line x1="230" y1="60" x2="270" y2="60" class="f-ca5"/>

  <rect x="270" y="20" width="220" height="80" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="380" y="42" class="t-ca5" fill="#1e3a8a">Request_Fetch_Unit_NVMe</text>
  <text x="380" y="62" class="b-ca5" fill="#1e3a8a">Fetch_next_request()</text>
  <text x="380" y="78" class="b-ca5" fill="#1e3a8a">PCIe DMA 로 SQE 읽기</text>

  <line x1="490" y1="60" x2="530" y2="60" class="f-ca5"/>

  <rect x="530" y="20" width="220" height="80" rx="8" fill="#ccfbf1" stroke="#0d9488" stroke-width="2"/>
  <text x="640" y="42" class="t-ca5" fill="#134e4a">Input_Stream_Manager_NVMe</text>
  <text x="640" y="62" class="b-ca5" fill="#134e4a">segment_user_request()</text>
  <text x="640" y="78" class="b-ca5" fill="#134e4a">LBA 범위 → NVM_Transaction 분해</text>

  <line x1="750" y1="60" x2="790" y2="60" class="f-ca5"/>

  <rect x="790" y="20" width="180" height="80" rx="8" fill="#0d9488" fill-opacity="0.15" stroke="#0d9488" stroke-width="2"/>
  <text x="880" y="42" class="t-ca5" fill="#134e4a">FTL 처리</text>
  <text x="880" y="62" class="b-ca5" fill="#134e4a">(7-1/7-2절)</text>

  <line x1="880" y1="100" x2="880" y2="160" class="f-ca5"/>
  <line x1="880" y1="160" x2="380" y2="160" class="f-ca5"/>

  <rect x="270" y="140" width="220" height="80" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="380" y="162" class="t-ca5" fill="#1e3a8a">Request_Fetch_Unit_NVMe</text>
  <text x="380" y="182" class="b-ca5" fill="#1e3a8a">Send_completion_queue_element()</text>
  <text x="380" y="198" class="b-ca5" fill="#1e3a8a">CQE 작성 + phase bit 토글</text>

  <line x1="270" y1="180" x2="230" y2="180" class="f-ca5"/>

  <rect x="10" y="140" width="220" height="80" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="120" y="162" class="t-ca5" fill="#1e3a8a">Host — Completion Queue</text>
  <text x="120" y="182" class="b-ca5" fill="#1e3a8a">CQ head/tail 갱신</text>
  <text x="120" y="198" class="b-ca5" fill="#1e3a8a">인터럽트로 완료 통지</text>
</svg>
</div>

**단계별 설명**

1. 호스트가 NVMe 제출 큐(SQ)의 tail 포인터를 갱신하면(`Submission_queue_tail_pointer_update`), 디바이스는 SQ 에 새 커맨드가 쌓였음을 안다.
2. `Request_Fetch_Unit_NVMe::Fetch_next_request()` 가 PCIe DMA 로 실제 커맨드(Submission Queue Entry)를 읽어온다 — `Input_Stream_NVMe` 구조체가 스트림별 `Submission_head`/`Submission_tail` 링버퍼 포인터를 따로 관리하므로, 여러 스트림(=여러 I/O 큐, multi-queue 의 핵심)이 서로 간섭 없이 동시에 처리된다.
3. `Input_Stream_Manager_NVMe::segment_user_request()` 가 하나의 호스트 요청을 LBA 정렬 단위로 여러 `NVM_Transaction_Flash` 로 쪼갠다.
4. 트랜잭션들이 FTL(캐시→매핑→블록매니저→TSU→PHY)을 거쳐 처리된다(7-1, 7-2절).
5. 모두 완료되면 `Send_completion_queue_element()` 가 완료 큐(CQ)에 엔트리를 쓰고 phase bit 을 토글한다 — 호스트는 이 phase bit 변화로 "새 완료가 있다"를 폴링 없이 알아챈다.
6. SATA(`Host_Interface_SATA`)는 이 전체 과정이 스트림별 큐 대신 **단일 큐**로 처리된다는 점이 유일한 차이 — 그래서 NVMe 만 진짜 "multi-queue" 시연에 쓸 수 있다( Session 2 결론과 동일 ).

<div style="margin-top: 60px;"></div>

### 7-6. Flash chip 커맨드 실행 & suspend 흐름

<div style="overflow-x:auto;">
<svg viewBox="0 0 900 220" style="width:100%;max-width:760px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-ca6" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t-ca6{font-size:12px;font-weight:700;text-anchor:middle;}
    .b-ca6{font-size:9.5px;text-anchor:middle;}
    .f-ca6{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-ca6);fill:none;}
  </style>
  <rect x="10" y="70" width="170" height="70" rx="8" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>
  <text x="95" y="95" class="t-ca6" fill="#1e293b">ONFI_Channel</text>
  <text x="95" y="112" class="b-ca6" fill="#1e293b">SetStatus(BUSY)</text>
  <text x="95" y="127" class="b-ca6" fill="#1e293b">커맨드 전송 시작</text>

  <line x1="180" y1="105" x2="220" y2="105" class="f-ca6"/>

  <rect x="220" y="70" width="200" height="70" rx="8" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>
  <text x="320" y="90" class="t-ca6" fill="#1e293b">Flash_Chip</text>
  <text x="320" y="108" class="b-ca6" fill="#1e293b">start_command_execution()</text>
  <text x="320" y="123" class="b-ca6" fill="#1e293b">Get_command_execution_latency()</text>

  <line x1="420" y1="105" x2="460" y2="105" class="f-ca6"/>
  <text x="440" y="95" class="b-ca6" fill="#e11d48">ERASE 중 read 요청?</text>

  <rect x="460" y="10" width="200" height="60" rx="8" fill="#ffe4e6" stroke="#e11d48" stroke-width="2"/>
  <text x="560" y="32" class="t-ca6" fill="#881337">Suspend(dieID)</text>
  <text x="560" y="50" class="b-ca6" fill="#881337">RemainingSuspendedExecTime 저장</text>
  <line x1="460" y1="105" x2="460" y2="40" class="f-ca6"/>

  <rect x="460" y="90" width="200" height="70" rx="8" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>
  <text x="560" y="115" class="t-ca6" fill="#1e293b">아니면 그대로</text>
  <text x="560" y="132" class="b-ca6" fill="#1e293b">latency 만큼 대기 후</text>
  <text x="560" y="147" class="b-ca6" fill="#1e293b">finish_command_execution()</text>

  <line x1="660" y1="125" x2="700" y2="125" class="f-ca6"/>

  <rect x="700" y="90" width="180" height="70" rx="8" fill="#0d9488" fill-opacity="0.15" stroke="#0d9488" stroke-width="2"/>
  <text x="790" y="115" class="t-ca6" fill="#134e4a">broadcast</text>
  <text x="790" y="132" class="b-ca6" fill="#134e4a">TransactionServicedSignal</text>
  <text x="790" y="147" class="b-ca6" fill="#134e4a">→ AMU/GC/TSU 콜백</text>
</svg>
</div>

**단계별 설명**

1. TSU 가 채널을 통해 칩에 커맨드를 내려보내면 `ONFI_Channel_Base::SetStatus(BUSY)` 로 채널이 점유된다 — 같은 채널의 다른 칩은 이 시간 동안 커맨드를 못 받는다( 버스 경합 모델링 ).
2. `Flash_Chip::start_command_execution()` 이 `Get_command_execution_latency()` 로 지연시간을 계산한다 — MLC 는 페이지 인덱스가 짝/홀수인지(LSB/CSB)로 지연이 갈리고, TLC 는 페이지 위치에 따라 3단계로 갈린다( 실제 NAND 가 페이지 위치별로 program 시간이 다른 특성을 반영 ).
3. `CMD_Suspension_Support=ERASE`( 우리 설정값 ) 인 경우, 진행 중인 erase(3,800,000ns 로 매우 김) 도중 read 요청이 도착하면 `Suspend()` 로 erase 를 일시 중단하고 read 를 먼저 처리한 뒤 `Resume()` 으로 이어서 마저 지운다 — read 지연시간이 GC 의 긴 erase 뒤에서 무한정 기다리지 않게 하는 QoS 장치.
4. 커맨드가 완료되면 `finish_command_execution()` → `broadcast_ready_signal()` 을 거쳐, PHY 계층의 `broadcastTransactionServicedSignal()` 이 등록된 콜백들( `Address_Mapping_Unit_Page_Level::handle_transaction_serviced_signal_from_PHY`, `GC_and_WL_Unit_Base` 쪽, `TSU_Base::handle_transaction_serviced_signal_from_PHY` 등 )을 순서대로 호출한다 — 각 상위 계층이 "이 트랜잭션이 끝났다"는 신호를 받는 지점이 정확히 여기다.

<div style="margin-top: 60px;"></div>

### 7-7. Preconditioning 흐름 — steady-state 초기 점유율 채우기

<div style="overflow-x:auto;">
<svg viewBox="0 0 940 200" style="width:100%;max-width:800px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-ca7" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t-ca7{font-size:12px;font-weight:700;text-anchor:middle;}
    .b-ca7{font-size:9.5px;text-anchor:middle;}
    .f-ca7{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-ca7);fill:none;}
  </style>
  <rect x="10" y="70" width="170" height="60" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="95" y="93" class="t-ca7" fill="#78350f">Initial_Occupancy</text>
  <text x="95" y="110" class="b-ca7" fill="#78350f">_Percentage (예: 50%)</text>

  <line x1="180" y1="100" x2="220" y2="100" class="f-ca7"/>

  <rect x="220" y="70" width="230" height="60" rx="8" fill="#ccfbf1" stroke="#0d9488" stroke-width="2"/>
  <text x="335" y="93" class="t-ca7" fill="#134e4a">Allocate_address_for_preconditioning()</text>
  <text x="335" y="110" class="b-ca7" fill="#134e4a">plane 별 목표 점유율에 맞게 LPA 분배</text>

  <line x1="450" y1="100" x2="490" y2="100" class="f-ca7"/>

  <rect x="490" y="70" width="230" height="60" rx="8" fill="#ccfbf1" stroke="#0d9488" stroke-width="2"/>
  <text x="605" y="90" class="t-ca7" fill="#134e4a">steady-state 분포로</text>
  <text x="605" y="107" class="b-ca7" fill="#134e4a">블록별 valid page 개수 배정</text>

  <line x1="720" y1="100" x2="760" y2="100" class="f-ca7"/>

  <rect x="760" y="70" width="170" height="60" rx="8" fill="#fef3c7" stroke="#d97706" stroke-width="2"/>
  <text x="845" y="90" class="t-ca7" fill="#78350f">Flash_Block_Manager</text>
  <text x="845" y="107" class="b-ca7" fill="#78350f">나머지 page invalidate</text>
</svg>
</div>

**단계별 설명**

1. MQSim 논문의 핵심 주장 중 하나가 "SSD 의 steady-state( 어느 정도 채워지고 GC 가 정상적으로 도는 상태 )를 정확히 모델링해야 한다"였다 — 그래서 시뮬레이션을 0%(완전히 빈 상태)부터 시작하지 않고, `Enabled_Preconditioning=true` 면 시작 전에 미리 목표 점유율만큼 채워 넣는다.
2. `Allocate_address_for_preconditioning()` 이 각 plane 에 배정될 LPA 개수를 `Logical_Address_Partitioning_Unit::Get_share_of_physcial_pages_in_plane()` 비율대로 나눈다.
3. 단순히 앞에서부터 채우는 게 아니라, **블록별 valid page 개수 분포(steady-state distribution)**를 입력받아 "이 블록엔 valid page 200개, 저 블록엔 50개" 식으로 GC 가 실제로 운영되던 중간 상태처럼 흩뿌린다.
4. `Flash_Block_Manager::Allocate_Pages_in_block_and_invalidate_remaining_for_preconditioning()` 이 각 블록에서 배정된 개수만큼만 valid 로 두고 나머지는 invalid 로 표시 — 이렇게 해야 시뮬레이션 시작 직후부터 곧바로 GC 가 현실적인 빈도로 발생한다( Session 2 에서 확인한 "기본 워크로드로는 GC 가 0번" 문제가, occupancy/workload 조정 시 이 preconditioning 로직과 맞물려 있다 ).

<div style="margin-top: 60px;"></div>

### 7-8. 시뮬레이션 시나리오 루프 — 프로그램 전체 생명주기

<div style="overflow-x:auto;">
<svg viewBox="0 0 1000 200" style="width:100%;max-width:860px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs><marker id="arrow-ca8" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>
  <style>
    .t-ca8{font-size:11.5px;font-weight:700;text-anchor:middle;}
    .b-ca8{font-size:9px;text-anchor:middle;}
    .f-ca8{stroke:#7f8c8d;stroke-width:2;marker-end:url(#arrow-ca8);fill:none;}
  </style>
  <rect x="10" y="20" width="150" height="60" rx="8" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>
  <text x="85" y="45" class="t-ca8" fill="#1e293b">CLI 인자 파싱</text>
  <text x="85" y="62" class="b-ca8" fill="#1e293b">-i / -w 경로</text>

  <line x1="160" y1="50" x2="195" y2="50" class="f-ca8"/>
  <rect x="195" y="20" width="150" height="60" rx="8" fill="#f1f5f9" stroke="#475569" stroke-width="2"/>
  <text x="270" y="45" class="t-ca8" fill="#1e293b">설정/workload</text>
  <text x="270" y="62" class="b-ca8" fill="#1e293b">XML 파싱</text>

  <line x1="345" y1="50" x2="380" y2="50" class="f-ca8"/>
  <rect x="380" y="20" width="150" height="60" rx="8" fill="#e0e7ff" stroke="#4f46e5" stroke-width="2"/>
  <text x="455" y="45" class="t-ca8" fill="#312e81">시나리오 루프</text>
  <text x="455" y="62" class="b-ca8" fill="#312e81">Simulator-&gt;Reset()</text>

  <line x1="530" y1="50" x2="565" y2="50" class="f-ca8"/>
  <rect x="565" y="20" width="180" height="60" rx="8" fill="#dbeafe" stroke="#2563eb" stroke-width="2"/>
  <text x="655" y="42" class="t-ca8" fill="#1e3a8a">SSD_Device + Host_System</text>
  <text x="655" y="60" class="b-ca8" fill="#1e3a8a">조립, host.Attach_ssd_device()</text>

  <line x1="745" y1="50" x2="780" y2="50" class="f-ca8"/>
  <rect x="780" y="20" width="200" height="60" rx="8" fill="#e0e7ff" stroke="#4f46e5" stroke-width="2"/>
  <text x="880" y="42" class="t-ca8" fill="#312e81">Start_simulation()</text>
  <text x="880" y="60" class="b-ca8" fill="#312e81">EventTree 루프( 7절 전체 )</text>

  <line x1="880" y1="80" x2="880" y2="130" class="f-ca8"/>
  <line x1="880" y1="130" x2="150" y2="130" class="f-ca8"/>

  <rect x="10" y="110" width="220" height="60" rx="8" fill="#ecfccb" stroke="#65a30d" stroke-width="2"/>
  <text x="120" y="132" class="t-ca8" fill="#365314">collect_results()</text>
  <text x="120" y="150" class="b-ca8" fill="#365314">workload_scenario_N.xml 기록</text>

  <line x1="230" y1="140" x2="270" y2="140" class="f-ca8" transform="translate(0,0)"/>
  <text x="480" y="150" class="b-ca8" fill="#475569">다음 IO_Scenario 있으면 → 시나리오 루프로 되돌아가 반복(9/4에 확인한 3개 시나리오)</text>
</svg>
</div>

**단계별 설명**

1. `command_line_args()` 가 `-i ssdconfig.xml -w workload.xml` 형태의 인자를 파싱한다.
2. `read_configuration_parameters()`/`read_workload_definitions()` 가 각각 XML 을 파싱하되, **파일이 없으면 MQSim 내장 기본값으로 새로 파일을 써준다**( 우리가 처음 실행할 때 설정 파일을 안 줘도 동작하는 이유 ).
3. `io_scenarios`( `IO_Scenario` 여러 개 ) 를 순회하는 것이 바깥쪽 루프 — 시나리오 하나가 우리가 9/4 에 본 `workload_scenario_1/2/3.xml` 각각에 대응한다.
4. 시나리오마다 **반드시** `Simulator->Reset()` 으로 이벤트 엔진을 초기화한 뒤, `SSD_Device`/`Host_System` 을 새로 생성하고 `host.Attach_ssd_device(&ssd)` 로 연결한다.
5. `Simulator->Start_simulation()` 이 호출되는 순간부터 7절에서 다룬 모든 콜 플로우( write/read/GC/TSU/... )가 실제로 일어난다 — `EventTree` 에 등록된 이벤트가 바닥날 때까지( 또는 `IO_Flow` 들의 `stop_time`/`Total_Requests_To_Generate` 조건 충족 시 ) 계속 진행된다.
6. 시뮬레이션이 끝나면 `collect_results()` 가 `Host_System::Report_results_in_XML()` + `SSD_Device::Report_results_in_XML()` 을 호출해 결과를 하나의 XML 로 합쳐 쓴다 — 이 안에서 `Stats` 의 전역 카운터들이 최종적으로 소비된다.

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [MQSim 개요](/ftl-visual-simulator/mqsim/overview/) · [개발 계획](/ftl-visual-simulator/plan/)
- GitHub : [github.com/CMU-SAFARI/MQSim](https://github.com/CMU-SAFARI/MQSim)
