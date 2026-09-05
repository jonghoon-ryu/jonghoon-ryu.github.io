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
6. 매 쓰기 후 `Flash_Block_Manager` 의 free block pool 이 줄면 `GC_and_WL_Unit.Check_gc_required()` 가 불려서 GC 트리거 여부 판단 → 필요하면 victim block 선정, valid page migration, block erase 순으로 GC 실행

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

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>파일</th><th>설명</th></tr>
<tr><td colspan="2" style="background:#2c3e50;color:#fff;font-weight:700;">exec/ — 조립 · 설정</th></tr>
<tr><td><code>main.cpp</code></td><td>진입점. 인자 파싱 → <code>Execution_Parameter_Set</code> 로드 → workload XML 파싱 → 시나리오별로 <code>Simulator-&gt;Reset()</code> → <code>SSD_Device</code>/<code>Host_System</code> 생성 → <code>Simulator-&gt;Start_simulation()</code> → 결과 XML 기록을 반복한다.</td></tr>
<tr><td><code>SSD_Device.h/cpp</code></td><td>"SSD 한 대"에 해당하는 조립 클래스. <code>Host_interface</code>, <code>Cache_manager</code>, <code>Firmware</code>(FTL), <code>PHY</code>, <code>Channels</code> 를 실제로 new 해서 서로 연결한다. 헤더 주석에 파이프라인 전체가 한 줄로 적혀 있다.</td></tr>
<tr><td><code>Host_System.h/cpp</code></td><td>workload 정의로부터 <code>IO_Flow</code> 들을 만들고 <code>SSD_Device</code> 에 붙이는(<code>Attach_ssd_device</code>) 역할. PCIe 링크 계층( <code>PCIe_Root_Complex</code>/<code>Switch</code>/<code>Link</code> )도 여기서 조립된다.</td></tr>
<tr><td><code>Execution_Parameter_Set.h/cpp</code></td><td><code>ssdconfig.xml</code> 전체를 담는 최상위 컨테이너. <code>Host_Configuration</code>(Host_Parameter_Set) + <code>SSD_Device_Configuration</code>(Device_Parameter_Set) 두 덩어리로 나뉜다.</td></tr>
<tr><td><code>Device_Parameter_Set.h/cpp</code>, <code>Flash_Parameter_Set.h/cpp</code>, <code>Host_Parameter_Set.h/cpp</code>, <code>IO_Flow_Parameter_Set.h/cpp</code></td><td>XML 태그 하나하나를 그대로 멤버 변수로 들고 있는 설정 구조체 + <code>XML_serialize</code>/<code>XML_deserialize</code>. [MQSim 개요](/ftl-visual-simulator/mqsim/overview/)의 파라미터 표가 바로 이 파일들의 필드 목록이다.</td></tr>
<tr><td colspan="2" style="background:#2c3e50;color:#fff;font-weight:700;">sim/ — 이산 이벤트 엔진</th></tr>
<tr><td><code>Sim_Object.h</code></td><td>모든 시뮬레이션 구성요소의 베이스. 순수 가상 함수 <code>Execute_simulator_event()</code>( 이벤트 수신 진입점 ), <code>Start_simulation()</code>, <code>Validate_simulation_config()</code> 를 강제한다.</td></tr>
<tr><td><code>Sim_Event.h</code></td><td>이벤트 하나 = <code>{Fire_time, Target_sim_object, Parameters, Type}</code>. <code>Next_event</code> 포인터로 같은 시각 이벤트를 연결 리스트로 묶는다.</td></tr>
<tr><td><code>Engine.h/cpp</code></td><td>싱글턴( <code>Simulator</code> 매크로 ). <code>Register_sim_event()</code> 로 이벤트 등록, <code>Start_simulation()</code> 이 "가장 이른 이벤트 pop → 해당 객체의 <code>Execute_simulator_event</code> 호출"을 반복하는 메인 루프.</td></tr>
<tr><td><code>EventTree.h/cpp</code></td><td>Red-Black 트리로 구현된 이벤트 큐. 시각(<code>sim_time_type</code>)을 key 로 정렬해서 <code>Get_min_value()</code> 로 항상 가장 빠른 이벤트를 O(log n)에 꺼낸다.</td></tr>
<tr><td colspan="2" style="background:#2c3e50;color:#fff;font-weight:700;">host/ — 호스트 · workload 생성</th></tr>
<tr><td><code>IO_Flow_Base.h/cpp</code></td><td>워크로드 스트림 하나의 공통 로직 — NVMe SQ/CQ 링버퍼 상태(<code>nvme_queue_pair</code>), 응답시간/전송량 통계(<code>STAT_*</code>), <code>Submit_io_request()</code>. <code>Generate_next_request()</code> 만 하위 클래스가 구현.</td></tr>
<tr><td><code>IO_Flow_Synthetic.h/cpp</code></td><td>파라미터 기반 요청 생성기. read 비율, 주소 분포(RANDOM_UNIFORM 등), hot/cold 영역 비율, 요청 크기 분포, 도착 간격을 각각 별도의 <code>RandomGenerator</code> 시드로 생성한다.</td></tr>
<tr><td><code>IO_Flow_Trace_Based.h/cpp</code></td><td>실제 trace 파일( 예: <code>tpcc-small.trace</code> )을 한 줄씩 읽어 같은 <code>Host_IO_Request</code> 형태로 변환. <code>total_replay_no</code> 로 반복 재생도 가능.</td></tr>
<tr><td><code>PCIe_Root_Complex/Switch/Link.h/cpp</code></td><td>NVMe 가 얹히는 PCIe 링크 계층의 지연시간 모델. 호스트 쪽 요청이 이 계층을 거쳐 <code>Host_Interface_NVMe</code> 로 전달된다.</td></tr>
<tr><td><code>SATA_HBA.h/cpp</code></td><td>SATA 호스트 버스 어댑터. NVMe 의 PCIe 링크에 대응하는, SATA 쪽 단일 큐 인터페이스.</td></tr>
<tr><td colspan="2" style="background:#2c3e50;color:#fff;font-weight:700;">ssd/ — FTL 4대 클래스</th></tr>
<tr><td><code>FTL.h/cpp</code></td><td><code>NVM_Firmware</code> 를 상속하는 조립 클래스. <code>Address_Mapping_Unit</code>/<code>BlockManager</code>/<code>GC_and_WL_Unit</code>/<code>TSU</code>/<code>PHY</code> 5개 포인터를 멤버로 들고 생성자에서 순서대로 new 한다.</td></tr>
<tr><td><code>Address_Mapping_Unit_Base.h/cpp</code></td><td>매핑 계층의 추상 인터페이스. <code>Translate_lpa_to_ppa_and_dispatch()</code>( 요청 처리 진입점 )와, GC 가 LPA/블록에 거는 barrier 관련 함수( <code>Set_barrier_for_accessing_*</code> )들이 순수 가상으로 선언되어 있다.</td></tr>
<tr><td><code>Address_Mapping_Unit_Page_Level.h/cpp</code></td><td>실제로 쓰이는 매핑 구현( DFTL 스타일 ). <code>Cached_Mapping_Table</code>( LRU CMT ), <code>AddressMappingDomain</code>( 스트림별 GMT/GTD ), <code>query_cmt()</code>( CMT hit/miss 판정 ), <code>translate_lpa_to_ppa()</code>( 실제 PPA 할당/조회 )가 핵심.</td></tr>
<tr><td><code>Address_Mapping_Unit_Hybrid.h/cpp</code></td><td>⚠️ <b>모든 메서드가 빈 스텁이다</b>( <code>{}</code> 또는 <code>return 0</code> 뿐, 53줄 ). log-block merge 로직이 실제로는 구현되어 있지 않음 — 아래 "정확성 노트" 참고.</td></tr>
<tr><td><code>Flash_Block_Manager_Base.h/cpp</code>, <code>Flash_Block_Manager.h/cpp</code></td><td>block/page 상태 관리. <code>Block_Pool_Slot_Type</code>(erase count, invalid bitmap, 상태 머신), <code>PlaneBookKeepingType</code>(free/valid/invalid 개수, Data_wf/GC_wf/Translation_wf, <code>Free_block_pool</code>).</td></tr>
<tr><td><code>GC_and_WL_Unit_Base.h/cpp</code>, <code>GC_and_WL_Unit_Page_Level.h/cpp</code></td><td><code>Check_gc_required()</code>(트리거 판단), <code>GC_is_in_urgent_mode()</code>(preemptible GC), victim 선정( GREEDY/RGA/RANDOM 계열/FIFO 6가지 정책의 실제 switch-case ), <code>run_static_wearleveling()</code>.</td></tr>
<tr><td><code>TSU_Base.h/cpp</code>, <code>TSU_FLIN.h/cpp</code>, <code>TSU_OutofOrder.h/cpp</code>, <code>TSU_Priority_OutOfOrder.h/cpp</code></td><td><code>Prepare_for_transaction_submit()</code>→<code>Submit_transaction()</code>→<code>Schedule()</code> 3단계 API. <code>Schedule()</code> 이 트랜잭션을 채널/칩별 큐에 분류하고, read>write>erase 우선순위로 실행시킨다( 정책별 세부 규칙만 다름 ).</td></tr>
<tr><td><code>Host_Interface_Base.h/cpp</code></td><td><code>Input_Stream_Manager_Base</code>(스트림 관리)와 <code>Request_Fetch_Unit_Base</code>(PCIe 메시지 송수신)의 공통 골격.</td></tr>
<tr><td><code>Host_Interface_NVMe.h/cpp</code></td><td>NVMe multi-queue 구현. <code>Input_Stream_NVMe</code> 가 SQ/CQ 링버퍼( head/tail 포인터 )를 스트림별로 들고, <code>Request_Fetch_Unit_NVMe</code> 가 실제 PCIe DMA 로 SQE 를 읽어오고 CQE 를 써준다.</td></tr>
<tr><td><code>Host_Interface_SATA.h/cpp</code></td><td>SATA 단일 큐 구현. NVMe 와 달리 큐가 스트림별로 나뉘지 않는다.</td></tr>
<tr><td><code>Data_Cache_Manager_Base.h/cpp</code></td><td>SSD 내부 DRAM 캐시 공통 로직. <code>estimate_dram_access_time()</code> 이 tRCD/tCL/tRP 기반으로 DRAM 접근 지연을 계산한다.</td></tr>
<tr><td><code>Data_Cache_Manager_Flash_Simple.h/cpp</code>, <code>_Flash_Advanced.h/cpp</code>, <code>Data_Cache_Flash.h/cpp</code></td><td>Simple 은 캐시 없이 바로 통과에 가까운 구현, Advanced 는 실제 캐시 라인 관리( 우리 설정의 <code>Caching_Mechanism=ADVANCED</code> ）가 쓰는 쪽.</td></tr>
<tr><td><code>NVM_PHY_Base.h/cpp</code>, <code>NVM_PHY_ONFI.h/cpp</code>, <code>NVM_PHY_ONFI_NVDDR2.h/cpp</code></td><td>FTL 과 물리 칩 사이의 컨트롤러. <code>Send_command_to_chip()</code> 이 실제 커맨드를 내려보내고, 완료 시 <code>ConnectToTransactionServicedSignal</code> 로 등록된 콜백( AMU/GC/TSU 각자 )을 깨운다.</td></tr>
<tr><td><code>ONFI_Channel_Base.h/cpp</code>, <code>ONFI_Channel_NVDDR2.h/cpp</code></td><td>채널 하나의 버스 점유 상태(<code>BusChannelStatus</code>) 관리 — 같은 채널의 여러 칩이 동시에 전송할 수 없는 이유가 여기.</td></tr>
<tr><td><code>NVM_Transaction.h</code>, <code>NVM_Transaction_Flash.h/cpp</code>, <code>_RD/_WR/_ER.h/cpp</code></td><td>flash 트랜잭션 하나의 데이터 모델. <code>Source</code>(USERIO/CACHE/MAPPING/GC_WL), <code>Type</code>(READ/WRITE/ERASE), <code>Address</code>, <code>LPA</code>/<code>PPA</code> — TSU 의 큐 분류·우선순위가 전부 이 두 필드(Source, Type) 기준.</td></tr>
<tr><td><code>Stats.h/cpp</code></td><td>전역 정적 카운터 모음. <code>Total_gc_executions</code>, <code>CMT_hits</code>/<code>CMT_miss</code>, <code>Total_page_movements_for_gc</code> 등 — hook 이 잡아야 할 이벤트와 최종 카운터를 1:1로 대조할 때 기준이 되는 파일.</td></tr>
<tr><td><code>Flash_Transaction_Queue.h/cpp</code></td><td>TSU 가 채널/칩/우선순위별로 들고 있는 실제 트랜잭션 큐 자료구조.</td></tr>
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

## 참고

- 관련 문서 : [MQSim 개요](/ftl-visual-simulator/mqsim/overview/) · [개발 계획](/ftl-visual-simulator/plan/)
- GitHub : [github.com/CMU-SAFARI/MQSim](https://github.com/CMU-SAFARI/MQSim)
