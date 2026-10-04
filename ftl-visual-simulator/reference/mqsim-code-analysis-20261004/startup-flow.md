---
layout: default
title: workload.xml 과 시작 과정 — 프로그램 시작부터 FTL 진입까지
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis-20261004/startup-flow/
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
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
</style>

# workload.xml 과 시작 과정 — 프로그램 시작부터 FTL 진입까지

`/home/ryuj/Ryu/MQSim` ( commit `51f0f2d` ) 기준. 라인 번호는 이 commit 의 것이다.

이 문서가 답하는 질문은 두 가지다.

1. `workload.xml` 은 무엇이고, 시나리오는 몇 개이며, 서로 어떻게 다른가?
2. `./MQSim -i ssdconfig.xml -w workload.xml` 을 실행하면, 실제 FTL 이 일을 시작할 때까지 무슨 일이 어떤 순서로 일어나는가?

<div style="margin-top: 60px;"></div>

## 0. 한눈에 보기

```
main()                                           main.cpp:260
 ├─ ① 인자 검사 · 파일 경로 추출                  :263, :269
 ├─ ② ssdconfig.xml 읽기                         :272    → Execution_Parameter_Set
 ├─ ③ workload.xml 읽기                          :273    → 시나리오 목록 (각 시나리오 = IO flow 정의 목록)
 │
 └─ for 각 시나리오:                              :276
     ├─ ④ Simulator->Reset()                      :284    이벤트 큐 · 객체 목록 비우기
     ├─ ⑤ SSD_Device ssd(...)                     :291    SSD 쪽 부품 전부 생성 + 서로 연결
     ├─ ⑥ Host_System host(...)                   :293    PCIe + IO flow 생성
     ├─ ⑦ host.Attach_ssd_device(&ssd)            :294    호스트 ↔ SSD 연결
     ├─ ⑧ Simulator->Start_simulation()           :296
     │      ├─ 8-1 모든 객체 Setup_triggers()      Engine.cpp:64   신호(콜백) 연결
     │      ├─ 8-2 모든 객체 Validate_...()        Engine.cpp:71   설정 검사
     │      ├─ 8-3 모든 객체 Start_simulation()    Engine.cpp:77   각자 초기화 + 첫 이벤트 등록
     │      └─ 8-4 이벤트 루프                     Engine.cpp:81   가장 이른 이벤트부터 꺼내 실행
     │             └─ 첫 요청이 호스트 → PCIe → 호스트 인터페이스 → 캐시 → ★ FTL 로 들어간다
     └─ ⑨ collect_results()                       :306    workload_scenario_N.xml 작성
```

<div class="check">
<b>이 문서에서 "FTL 이 시작한다" 의 두 가지 의미</b><br>
(a) <b>FTL 쪽 초기화</b> — 8-3 단계에서 <code>Address_Mapping_Unit_Page_Level::Start_simulation()</code> 이 매핑 테이블( translation page )을 플래시에 배치한다.<br>
(b) <b>첫 요청이 FTL 로 진입</b> — 이벤트 루프 안에서 <code>Data_Cache_Manager</code> 가 <code>Address_Mapping_Unit::Translate_lpa_to_ppa_and_dispatch()</code> 를 처음 호출하는 순간. 이 호출이 FTL 의 실제 입구다.
</div>

<div style="margin-top: 60px;"></div>

## 1. workload.xml

### 1.1 무엇인가

**시뮬레이터에게 "어떤 I/O 를 얼마나 어떻게 보낼 것인가" 를 알려주는 입력 파일**이다. `-w` 로 경로를 준다. SSD 자체의 사양( 채널·칩·캐시·GC 정책 등 )은 `ssdconfig.xml` 에 있고, `workload.xml` 은 그 SSD 에 가해질 **부하만** 정의한다.

구조는 두 단계다.

```
<MQSim_IO_Scenarios>
  <IO_Scenario>                             ← 시나리오 하나 = 시뮬레이션 한 번
    <IO_Flow_Parameter_Set_Synthetic>…      ← flow 하나 = 호스트의 I/O 발생기 하나
    <IO_Flow_Parameter_Set_Synthetic>…
  </IO_Scenario>
  <IO_Scenario> … </IO_Scenario>
</MQSim_IO_Scenarios>
```

- **시나리오**( `IO_Scenario` )는 서로 독립이다. `main` 의 `for` 루프가 하나씩 꺼내 **처음부터 새로** 시뮬레이션한다( 매번 `Simulator->Reset()` 후 SSD·호스트를 새로 만든다 ).
- **flow** 는 시나리오 안에서 **동시에** 실행되는 I/O 발생기다. flow 마다 NVMe submission/completion queue 한 쌍이 생기고( queue id = flow 번호 + 1, 0번은 admin 전용 ), SSD 쪽에서는 stream 하나가 된다.
- flow 종류는 두 가지다.
  - `IO_Flow_Parameter_Set_Synthetic` — 파라미터로 만들어내는 가짜 부하( 읽기 비율, 주소 분포, 요청 크기, 큐 깊이 … ).
  - `IO_Flow_Parameter_Set_Trace_Based` — 실제 trace 파일을 재생.

> **입력과 출력을 혼동하지 말 것.** `workload.xml` 은 입력이고, 같은 폴더의 `workload_scenario_1.xml`, `_2.xml`, `_3.xml` 은 **시뮬레이터가 쓴 결과 파일**이다( 루트가 `<MQSim_Results>` ). 이름은 입력 파일명에서 `.xml` 을 뗀 것 + `_scenario_` + 시나리오 번호( `main.cpp:306` ).

### 1.2 시나리오는 3개

| | 시나리오 1 | 시나리오 2 | 시나리오 3 |
|---|---|---|---|
| flow 수 | 2 ( Synthetic ×2 ) | 2 ( Synthetic ×2 ) | 1 ( **Trace_Based** ) |
| 읽기 비율 | **0 %** ( 전부 쓰기 ) | **100 %** ( 전부 읽기 ) | trace 에 따름 ( 읽기 4,381 / 쓰기 2,618 ) |
| 우선순위 | flow0 HIGH, flow1 HIGH | flow0 **URGENT**, flow1 HIGH | HIGH |
| 큐 깊이 ( `Average_No_of_Reqs_in_Queue` ) | flow0 **16**, flow1 **2** | 16, 16 | — ( trace 의 도착 시각을 따름 ) |
| 부하 생성 방식 | `QUEUE_DEPTH` | `QUEUE_DEPTH` | trace 의 timestamp 재생 |
| 캐시 모드 | WRITE_CACHE | WRITE_CACHE | WRITE_CACHE |
| 초기 점유율 ( `Initial_Occupancy_Percentage` ) | 75 % | 75 % | 70 % |
| 작업 영역 ( `Working_Set_Percentage` ) | 50 % | 50 % | — |
| 요청 크기 | 8 sector ( 4 KB ) 고정 | 8 sector 고정 | trace 에 따름 |
| 주소 분포 | RANDOM_UNIFORM | RANDOM_UNIFORM | trace 에 따름 |
| seed | 798 / 6533 | 798 / 6533 | — |
| 입력 데이터 | 없음 ( 생성 ) | 없음 ( 생성 ) | `traces/tpcc-small.trace` ( 6,999 줄 ) |

세 시나리오가 **공통으로 쓰는 것**: 같은 SSD( `ssdconfig.xml` ), 모든 flow 가 **전체 하드웨어**( 8 채널 × 4 칩 × 2 다이 × 2 플레인 )를 공유, `Stop_Time` = 10,000,000,000 ns( 10초 ), `Total_Requests_To_Generate` = 0( 시간으로만 멈춤 ).

**코드와 값으로 읽을 수 있는 차이의 의미** ( 파일에 의도가 적혀 있지는 않으므로 추정이 섞인다 ):

- **시나리오 1 — 쓰기만, 큐 깊이가 다른 두 flow.** 두 flow 가 같은 SSD 의 쓰기 자원을 나눠 쓸 때 큐 깊이( 동시에 던지는 요청 수 )가 처리량을 얼마나 좌우하는지 본다.
- **시나리오 2 — 읽기만, 우선순위가 다른 두 flow.** 같은 부하인데 한쪽이 `URGENT` 일 때 응답 시간이 어떻게 갈리는지( 우선순위 스케줄링 `PRIORITY_OUT_OF_ORDER` )를 본다.
- **시나리오 3 — 실제 trace 한 개.** 합성 부하가 아니라 실제 워크로드( tpcc )를 재생한다. 도착 시각이 trace 에 박혀 있어서 부하 강도를 trace 가 정한다.

**이미 돌려서 나온 결과**( 이 폴더의 `workload_scenario_*.xml` )로 확인해 보면 위 설명이 맞다.

| 시나리오 | flow | 요청 수 | 읽기 / 쓰기 | IOPS | 대역폭 | 평균 응답 |
|---|---|--:|---|--:|--:|--:|
| 1 | No_0 ( QD 16 ) | 330,160 | 0 / 330,160 | 32,954 | 135 MB/s | 484 µs |
| 1 | No_1 ( QD 2 ) | 41,272 | 0 / 41,272 | 4,119 | 16.9 MB/s | 484 µs |
| 2 | No_0 ( URGENT ) | 906,909 | 906,909 / 0 | 90,689 | 371.5 MB/s | 176 µs |
| 2 | No_1 ( HIGH ) | 624,553 | 624,553 / 0 | 62,454 | 255.8 MB/s | 256 µs |
| 3 | tpcc-small.trace | 6,999 | 4,381 / 2,618 | 6,304 | 53.8 MB/s | 3,458 µs |

- 시나리오 1 : 큐 깊이 16 대 2 → IOPS 가 약 **8 배**( 16 / 2 ). 두 flow 의 응답 시간이 똑같이 484 µs 인 점이 눈에 띈다 — 둘 다 같은 `WRITE_CACHE` 와 같은 쓰기 경로를 거치기 때문으로 보인다( 확인하지는 않았다 ).
- 시나리오 2 : URGENT flow 가 HIGH flow 보다 IOPS 가 높고 응답이 짧다.
- 시나리오 3 : trace 의 6,999 줄이 전부 처리됐다( 읽기 4,381 + 쓰기 2,618 = 6,999 ).

### 1.3 같이 알아둘 SSD 설정 ( ssdconfig.xml )

모든 시나리오는 같은 SSD 를 쓴다.

| 항목 | 값 | 의미 |
|---|---|---|
| `HostInterface_Type` | NVME | 호스트 ↔ SSD 는 NVMe 방식( SATA 도 지원 ) |
| `Flash_Channel_Count` × `Chip_No_Per_Channel` | 8 × 4 | 칩 32개 |
| `Die_No_Per_Chip` × `Plane_No_Per_Die` | 2 × 2 | 플레인 128개 |
| `Block_No_Per_Plane` × `Page_No_Per_Block` | 2048 × 256 | 플레인당 블록 2,048개, 블록당 페이지 256개 |
| `Page_Capacity` | 8192 B | 페이지 8 KB → 원시 용량 **512 GiB** |
| `Flash_Technology` | MLC | 읽기 75 µs, 쓰기 750 µs, 지우기 3.8 ms |
| `Address_Mapping` / `CMT_Capacity` | PAGE_LEVEL / 2 MiB | 페이지 단위 매핑, 매핑 캐시( CMT ) |
| `Plane_Allocation_Scheme` | CWDP | 채널 → 칩( Way ) → 다이 → 플레인 순으로 쓰기를 분산 |
| `Caching_Mechanism` | ADVANCED, 256 MiB | DRAM 데이터 캐시 |
| `Transaction_Scheduling_Policy` | PRIORITY_OUT_OF_ORDER | TSU( 플래시 트랜잭션 스케줄러 ) 정책 |
| `Overprovisioning_Ratio` | 0.07 | OP 7 % |
| `GC_Block_Selection_Policy` / `GC_Exec_Threshold` | RGA / 0.05 | 여유 블록이 5 % 아래로 내려가면 GC |
| `Enabled_Preconditioning` | **false** | 시작 전에 SSD 를 미리 채우지 **않는다** |

### 1.4 읽을 때 주의할 점 ( 코드로 확인한 것 )

- **`Initial_Occupancy_Percentage` 는 지금 설정에서 효과가 없다.** 이 값은 *preconditioning* 이 켜져 있을 때만 쓰인다( 8-3 단계 참고 ). `ssdconfig.xml` 의 `Enabled_Preconditioning` 이 `false` 이므로 세 시나리오 모두 **빈 SSD 에서 시작**한다.
- **`<Intensity>` 태그는 읽히지 않는다.** `workload.xml` 의 Synthetic flow 에는 `Intensity` 가 있지만, 파서( `IO_Flow_Parameter_Set.cpp` )는 `Bandwidth` 만 읽는다. `QUEUE_DEPTH` 방식은 대역폭을 쓰지 않으므로 지금은 문제가 없지만, `BANDWIDTH` 방식으로 바꾸면 초기화되지 않은 `Bandwidth` 가 쓰인다 ( 관련 : [초기화되지 않은 Bandwidth 필드 버그](/ftl-visual-simulator/reference/bug-list/bandwidth-divide-by-zero-bug/) ).
- **`Working_Set_Percentage`** 는 flow 가 접근할 주소 범위를 그 비율로 줄인다( `IO_Flow_Synthetic` 생성자가 `start + (end − start) × ratio` 로 끝 주소를 계산 ).

<div style="margin-top: 60px;"></div>

## 2. 프로그램이 FTL 에 도달하기까지

### 단계 ① — 인자 검사 ( `main.cpp:260` )

`argc != 5` 이면 도움말만 출력하고 종료한다. 즉 인자는 정확히 `-i <설정> -w <workload>` 두 쌍이어야 한다. `command_line_args()` 가 `-i` 뒤의 경로를 `ssd_config_file_path`, `-w` 뒤의 경로를 `workload_defs_file_path` 에 넣는다.

### 단계 ② — SSD 설정 읽기 ( `read_configuration_parameters`, `main.cpp:38` )

1. `Execution_Parameter_Set` 을 기본값으로 만든다( `main.cpp:271` ).
2. 파일이 없으면 기본값을 그 경로에 XML 로 써 놓고 계속한다.
3. 파일이 있으면 rapidxml 로 파싱해 `XML_deserialize()` 로 기본값을 덮어쓴다. 파일 내용이 `USE_INTERNAL_PARAMS` 한 줄이면 내부 기본값을 쓰고 그 값을 파일로 써 준다.

결과는 `exec_params` ( 호스트 설정 + SSD 설정 )이다. **아직 시뮬레이터 객체는 하나도 만들어지지 않았다.**

### 단계 ③ — workload 읽기 ( `read_workload_definitions`, `main.cpp:88` )

`workload.xml` 을 파싱해 `vector<vector<IO_Flow_Parameter_Set*>>` 를 만든다. `IO_Scenario` 마다 안쪽 벡터가 하나, flow 마다 `IO_Flow_Parameter_Set_Synthetic` 또는 `_Trace_Based` 객체가 하나 생긴다( `new` + `XML_deserialize` ). 파일이 없거나 시나리오가 하나도 없으면 코드에 박힌 기본 flow 2개를 쓰고 그 내용을 파일에 쓴다.

이 단계도 순수한 파싱이다. 값들은 **일반 구조체의 필드**로만 존재한다.

### 단계 ④ — 시나리오 루프와 Reset ( `main.cpp:276` ~ `:289` )

시나리오마다 다음을 한다.

1. `Simulator->Reset()` ( `Engine.cpp:15` ) — 이벤트 리스트와 객체 목록을 비우고, 시뮬레이션 시각을 0 으로, `Logical_Address_Partitioning_Unit` 도 초기화한다. 시나리오끼리 아무것도 공유하지 않게 하는 장치다.
2. 현재 시나리오의 flow 정의를 `exec_params->Host_Configuration.IO_Flow_Definitions` 에 복사한다.

`Simulator` 는 전역 싱글턴이다( `#define Simulator MQSimEngine::Engine::Instance()`, `Engine.h:47` ). 뒤에 나오는 모든 `Simulator->AddObject(…)`, `Register_sim_event(…)` 가 같은 엔진 하나로 들어간다.

### 단계 ⑤ — SSD_Device 생성 ( `SSD_Device.cpp:22` )

이 생성자 하나가 SSD 쪽 부품을 **아래에서 위로** 전부 만들고 서로 연결한다. 번호는 코드 주석( `Step 1 … 10` )과 같다.

| # | 만드는 것 | 클래스 | 비고 |
|--:|---|---|---|
| 1 | 플래시 칩 32개 | `Flash_Chip` | 기술( SLC/MLC/TLC )에 따라 지연 시간 배열을 만들어 넘긴다. `Simulator->AddObject` 로 등록 |
| 2 | 채널 8개 | `ONFI_Channel_NVDDR2` | 칩을 묶는 수동 객체. **엔진에 등록하지 않는다**( 이벤트를 처리하지 않으므로 ) |
| 3 | 채널 컨트롤러 | `NVM_PHY_ONFI_NVDDR2` | 채널들과 칩들을 다룬다. 등록됨 |
| 4 | **FTL** | `FTL` | 부품을 담는 **껍데기**. 등록은 되지만 `Start_simulation()` 과 `Execute_simulator_event()` 가 **비어 있다**( `FTL.cpp:891`, `:895` ). 나머지 FTL 부품을 가리키는 포인터만 쥔다 |
| 5 | 트랜잭션 스케줄러 | `TSU_Priority_OutOfOrder` | 설정의 `Transaction_Scheduling_Policy` 로 고른다. 명령 서스펜드 지원 여부도 여기서 결정 |
| 6 | 블록 매니저 | `Flash_Block_Manager` | 플레인별 블록 풀과 free/used 상태 관리 |
| 7 | **주소 매핑** | `Address_Mapping_Unit_Page_Level` | 이 직전에 `Logical_Address_Partitioning_Unit::Allocate_logical_address_for_flows()` 로 flow 별 논리 주소 범위와 자원( 채널·칩·다이·플레인 )을 나눈다 |
| 8 | GC / 마모평준화 | `GC_and_WL_Unit_Page_Level` | 정책·임계값은 설정에서 |
| 9 | 데이터 캐시 | `Data_Cache_Manager_Flash_Advanced` | flow 별 캐시 모드( `WRITE_CACHE` 등 ) 전달 |
| 10 | 호스트 인터페이스 | `Host_Interface_NVMe` | 안에서 `Input_Stream_Manager_NVMe` 와 `Request_Fetch_Unit_NVMe` 를 만든다 |

**FTL 이 실제로 무엇으로 이루어졌는지**가 여기서 보인다. `FTL` 객체는 4번의 껍데기이고, 진짜 FTL 기능은 5~8번( TSU, 블록 매니저, 주소 매핑, GC/WL )과 9번( 캐시 )이 나눠 가진다. 이 객체들이 만들어질 때마다 포인터가 `ftl->…` 에 꽂힌다( `ftl->TSU`, `ftl->BlockManager`, `ftl->Address_Mapping_Unit`, `ftl->GC_and_WL_Unit`, `ftl->Data_cache_manager` ).

### 단계 ⑥ — Host_System 생성 ( `Host_System.cpp:11` )

호스트 쪽 부품을 만든다.

1. `PCIe_Link` ( 대역폭·레인 수는 설정 ), `PCIe_Root_Complex`, `PCIe_Switch` 를 만들어 서로 연결한다. 링크는 엔진에 등록한다.
2. flow 정의마다 `IO_Flow_Synthetic` 또는 `IO_Flow_Trace_Based` 를 `new` 하고 엔진에 등록한다( `Host_System.cpp:35` 의 루프 ). 파라미터 구조체의 값이 생성자 인자로 옮겨지는데, 몇 가지는 변환된다.
   - 주소 범위 : 단계 ⑤ 의 `Logical_Address_Partitioning_Unit` 이 정해 둔 flow 별 시작·끝 주소를 받는다. `Working_Set_Percentage` 는 `/100` 한 비율( `working_set_ratio` )로 바뀌고, 이 비율만큼 끝 주소가 줄어든다.
   - 큐 번호 : `FLOW_ID_TO_Q_ID(flow_id)` = `flow_id + 1`. NVMe 의 0번 큐는 admin 전용이다.
   - `Bandwidth` : 평균 도착 간격( ns )으로 바뀐다. `BANDWIDTH` 방식에서만 쓰인다.
   - `Read_Percentage` / `Percentage_of_Hot_Region` / `Initial_Occupancy_Percentage` : `/100` 한 비율.
3. `PCIe_Root_Complex` 에 flow 목록을 알려 준다( 완료 메시지를 해당 flow 에 돌려주기 위해 ).

### 단계 ⑦ — 연결 ( `host.Attach_ssd_device(&ssd)`, `Host_System.cpp:102` )

- `ssd.Attach_to_host(PCIe_switch)` — SSD 의 호스트 인터페이스가 PCIe 스위치를 안다.
- `PCIe_switch->Attach_ssd_device(Host_interface)` — 스위치가 호스트 인터페이스를 안다.

이제 호스트의 `PCIe_Link` → `PCIe_Switch` → `Host_Interface` 로 메시지가 흐를 수 있다. **그러나 지금까지 시각은 0 이고, 이벤트는 하나도 등록되지 않았다.**

### 단계 ⑧ — Simulator->Start_simulation() ( `Engine.cpp:56` )

여기서 비로소 시뮬레이션이 돈다. 엔진은 객체 목록( `unordered_map` )을 **세 번** 훑은 다음 이벤트 루프로 들어간다.

#### 8-1. `Setup_triggers()` — 신호( 콜백 )를 연결

객체들이 서로의 "이벤트 발생 알림"에 자기 함수를 등록한다. 이것이 객체 사이를 **직접 호출 없이** 잇는 배선이다.

| 알림을 내는 쪽 | 알림 | 받는 쪽 ( 등록하는 함수 ) |
|---|---|---|
| `Host_Interface_NVMe` | 사용자 요청 도착 | `Data_Cache_Manager::handle_user_request_arrived_signal` ( `Data_Cache_Manager_Base.cpp:26` ) |
| `Data_Cache_Manager` | 사용자 요청 완료 / 메모리 트랜잭션 완료 | `Host_Interface_Base::handle_user_request_serviced_signal_from_cache` 등 ( `Host_Interface_Base.cpp:47` ) |
| `NVM_PHY_ONFI_NVDDR2` | 트랜잭션 완료 | 주소 매핑, GC/WL, 캐시, TSU 의 `handle_transaction_serviced_signal_from_PHY` ( 각 `Setup_triggers` ) |
| `NVM_PHY_ONFI_NVDDR2` | 채널 유휴 / 칩 유휴 | `TSU_Base::handle_channel_idle_signal`, `handle_chip_idle_signal` ( `TSU_Base.cpp:34` ) |
| `Flash_Chip` | 칩 준비됨 | `NVM_PHY_ONFI_NVDDR2::handle_ready_signal_from_chip` ( `NVM_PHY_ONFI_NVDDR2.cpp:45` ) |

방향을 정리하면 **호스트 인터페이스 → 캐시 → ( FTL 부품들 ) → PHY → 칩** 이 요청 방향이고, 완료 신호는 **칩 → PHY → ( 매핑 / GC / 캐시 ) → 호스트 인터페이스** 로 거슬러 올라간다.

#### 8-2. `Validate_simulation_config()` — 설정 점검

필요한 포인터가 비어 있지 않은지 확인한다. 예를 들어 `FTL::Validate_simulation_config()` ( `FTL.cpp:35` )는 캐시 매니저, 주소 매핑, 블록 매니저, GC 가 모두 연결됐는지 검사하고 아니면 예외를 던진다. `Host_System::Validate_simulation_config()` 는 IO flow 가 하나도 없거나 PCIe 구성이 비었는지 본다.

#### 8-3. `Start_simulation()` — 각자 초기화하고 첫 이벤트를 등록

객체마다 자기 `Start_simulation()` 이 호출된다. 하는 일이 있는 것만 적으면 다음과 같다.

| 객체 | 하는 일 |
|---|---|
| `Host_System` ( `Host_System.cpp:114` ) | ① NVMe 라면 flow 마다 `Create_new_stream()` 으로 SSD 쪽에 stream 을 만든다( 우선순위, 논리 주소 범위, submission/completion queue 주소 전달 ). ② `preconditioning_required` 가 참이면 `ssd_device->Perform_preconditioning()` 으로 SSD 를 미리 채운다. **이 설정에서는 거짓이라 건너뛴다.** |
| `Address_Mapping_Unit_Page_Level` ( `Address_Mapping_Unit_Page_Level.cpp:410` ) | **FTL 쪽 첫 작업.** `Store_mapping_table_on_flash_at_start()` — stream 마다 translation page 들( 매핑 테이블을 플래시에 저장하는 페이지 )을 플래시의 어느 플레인·페이지에 둘지 정하고 그 페이지를 "사용 중" 으로 표시한다. 요청이 하나도 오기 전에 플래시의 일부가 이미 채워진다 |
| `IO_Flow_Synthetic` ( `IO_Flow_Synthetic.cpp:197` ) | 로그 파일 준비 후 **첫 이벤트를 등록**. `QUEUE_DEPTH` 는 시각 1 ns, `BANDWIDTH` 는 지수분포 난수 후 |
| `IO_Flow_Trace_Based` ( `IO_Flow_Trace_Based.cpp:76` ) | trace 파일 전체를 한 번 훑어 시간이 단조 증가하는지, 줄 수가 몇인지 확인하고, 파일을 다시 열어 **첫 줄의 도착 시각**에 첫 이벤트를 등록 |
| 그 외 ( `FTL`, `SSD_Device`, `Data_Cache_Manager`, `PCIe_Link` … ) | 빈 함수 |

`Preconditioning` 을 켜면 `FTL::Perform_precondition()` ( `FTL.cpp:47` ) 이 workload 통계로 "정상 상태에서 접근될 논리 페이지" 를 미리 만들어 플래시에 써 넣고, 이어서 캐시를 데운다( `Do_warmup` ). `Initial_Occupancy_Percentage` 가 쓰이는 곳이 바로 여기다.

> **순서에 대한 주의.** 엔진은 `unordered_map` 을 순회하므로 8-3 에서 객체들의 `Start_simulation()` **호출 순서는 정해져 있지 않다**. 위 표의 작업들이 서로 독립이라 문제가 없지만, 한 객체의 Start 가 다른 객체의 Start 결과를 필요로 하게 만들면 안 된다.

여기까지 끝나면 **이벤트 큐에는 flow 가 등록한 첫 이벤트들만 들어 있다.**

#### 8-4. 이벤트 루프 ( `Engine.cpp:81` )

```
while (이벤트가 있고 stop 이 아니면):
    가장 이른 시각의 이벤트 묶음을 꺼낸다
    현재 시각 = 그 이벤트의 Fire_time
    묶음의 이벤트마다   Target_sim_object->Execute_simulator_event(ev)
```

시뮬레이션 시각은 실제 시간이 아니라 **이 루프가 이벤트를 꺼낼 때마다 점프**한다. 객체들이 `Register_sim_event(미래 시각, 대상, …)` 로 다음 일을 예약하고, 큐가 비면( 또는 `Stop_simulation()` 이 불리면 ) 끝난다.

### 단계 ⑨ — 첫 요청이 FTL 에 들어가는 길 ( 시나리오 1 의 flow 0 을 따라가며 )

시각 1 ns 에 `IO_Flow_Synthetic` 의 첫 이벤트가 터지는 순간부터다. 쓰기 전용 + `WRITE_CACHE` + NVMe 인 경우를 따라간다.

```
 t = 1 ns   IO_Flow_Synthetic::Execute_simulator_event()                 IO_Flow_Synthetic.cpp:219
              QUEUE_DEPTH 방식 → Average_No_of_Reqs_in_Queue(16)개 요청을 한꺼번에 만든다
              └ Generate_next_request()   주소·크기·읽기/쓰기를 난수로 결정
              └ IO_Flow_Base::Submit_io_request()                          IO_Flow_Base.cpp:405
                   · submission queue(메모리)에 항목 기록, tail 증가
                   · PCIe_Root_Complex::Write_to_device(doorbell, tail)    "새 명령이 있다"
 ───────────────────────────────  호스트 ➜ 장치  ───────────────────────────────
            PCIe_Link::Deliver()  → (전송 시간 만큼 뒤에) 이벤트 → PCIe_Switch::Deliver_to_device()
            Host_Interface::Consume_pcie_message()                          Host_Interface_Base.h:113
              └ Request_Fetch_Unit_NVMe::Process_pcie_write_message()       Host_Interface_NVMe.cpp:219
                   └ Input_Stream_Manager_NVMe::Submission_queue_tail_pointer_update()   :40
                        └ (대기 중 요청 수 < Queue_Fetch_Size) Fetch_next_request()      :46
                             └ Send_read_message_to_host(SQE 주소)  "그 명령 내용을 읽어 가겠다" (DMA)
 ───────────────────────────────  장치 ➜ 호스트 ➜ 장치  ──────────────────────────
            호스트가 submission queue 항목을 READ_COMP 로 돌려줌 (PCIe_Root_Complex::Read_from_memory)
            Request_Fetch_Unit_NVMe::Process_pcie_read_message()           Host_Interface_NVMe.cpp:278
              └ NVMe 명령(Opcode, LBA, 크기)을 User_Request 로 변환
              └ Input_Stream_Manager_NVMe::Handle_new_arrived_request()    :69
                   · 읽기 → 바로 segment_user_request + 도착 신호
                   · 쓰기 → Fetch_write_data()  "쓸 데이터도 DMA 로 가져온다" → 도착하면
                            Handle_arrived_write_data()                    :92
                                 └ segment_user_request()                  :170
                                      요청을 "페이지 단위 트랜잭션"(NVM_Transaction_Flash_WR)으로 쪼갬
                                      LHA(섹터 주소) → LPA(논리 페이지 주소)
                                 └ broadcast_user_request_arrival_signal()
 ─────────────────────────────  신호(8-1에서 연결됨)  ─────────────────────────────
            Data_Cache_Manager::handle_user_request_arrived_signal()       Data_Cache_Manager_Base.cpp
              └ Data_Cache_Manager_Flash_Advanced::process_new_user_request()   :187
                   쓰기 + WRITE_CACHE →  write_to_destage_buffer()          :266
                        · DRAM 쓰기 지연을 모델링하고 캐시 슬롯에 데이터를 넣는다
                        · 처음 보는 LPA(bloom filter 에 없음) 는 "차가운 데이터" 로 보고
                          곧바로 플래시에도 쓰도록 writeback_transactions 에 모은다   :312
                        · ★ Address_Mapping_Unit->Translate_lpa_to_ppa_and_dispatch(writeback_transactions)   :347
 ───────────────────────────────────  ★  FTL 진입  ★  ──────────────────────────────
            Address_Mapping_Unit_Page_Level::Translate_lpa_to_ppa_and_dispatch()   Address_Mapping_Unit_Page_Level.cpp:480
```

#### 여기가 FTL 의 입구인 이유

`Translate_lpa_to_ppa_and_dispatch()` 부터가 FTL 의 일이다.

1. 트랜잭션마다 `query_cmt()` — **매핑 캐시( CMT )에 LPA 의 매핑이 있는가**를 묻는다. 없으면 플래시에서 translation page 를 읽어 와야 한다( 그래서 단계 8-3 의 translation page 배치가 먼저 필요했다 ).
2. 쓰기라면 물리 페이지( PPA )를 새로 할당한다 — 이때 블록 매니저가 쓸 블록을 고르고, `Plane_Allocation_Scheme`( CWDP )가 채널·칩·다이·플레인을 정한다.
3. 물리 주소가 정해진 트랜잭션을 `TSU->Submit_transaction()` 으로 넘기고 `TSU->Schedule()` 로 실행을 시작시킨다.
4. TSU 가 PHY( `NVM_PHY_ONFI_NVDDR2` )를 거쳐 칩에 명령을 보내면, `Flash_Chip` 가 지연 시간 후 완료 이벤트를 등록하고, 완료 신호가 위 8-1 의 연결을 따라 거슬러 올라간다.

즉 이 문서가 끝나는 지점 이후가 **FTL 코드 읽기의 시작**이다.

#### 읽기 요청이라면

읽기( 시나리오 2 )는 쓰기와 달리 **데이터를 가져오는 DMA 단계 없이** 명령을 받자마자 `segment_user_request()` 로 간다. 그다음 `process_new_user_request()` 의 `READ` 분기( `:194` )에서 갈라진다.

- 캐시 모드가 `TURNED_OFF` 이면 캐시를 보지 않고 바로 FTL 로 간다( `:197` ).
- 그 밖의 모드( `WRITE_CACHE`, `READ_CACHE`, `WRITE_READ_CACHE` 는 같은 코드를 공유한다 )는 먼저 **캐시를 조회**한다. 전부 캐시에 있으면 FTL 은 건드리지 않고 DRAM 읽기 시간만 모델링한다. 일부 또는 전부가 없으면, 없는 부분만 FTL 로 보낸다( `:233` ).

시나리오 2 는 처음에 SSD 가 비어 있으므로( preconditioning 꺼짐 ) 첫 읽기들은 캐시에 없고 FTL 까지 내려간다.

#### 같은 요청이 끝날 때

플래시 읽기/쓰기가 끝나면 신호가 `Data_Cache_Manager` → `Host_Interface` 로 올라가고, `Request_Fetch_Unit_NVMe::Send_completion_queue_element()` 가 완료 항목( CQE )을 PCIe 로 호스트에 쓴다. 호스트의 `IO_Flow_Base::NVMe_consume_io_request()` 가 응답 시간을 통계에 더하고, `QUEUE_DEPTH` 방식의 flow 는 **완료될 때마다 새 요청을 하나 더** 만든다. 그래서 큐 깊이가 일정하게 유지된다( 닫힌 루프 ).

<div style="margin-top: 60px;"></div>

## 3. 정리 — 누가 누구를 부르는가

| 시점 | 호출하는 쪽 | 부르는 대상 | 효과 |
|---|---|---|---|
| 프로그램 시작 | `main` | XML 파서 | 설정·workload 가 구조체가 된다 |
| 시나리오 시작 | `main` | `SSD_Device` 생성자 | SSD 부품 생성·연결·엔진 등록 |
| 〃 | `main` | `Host_System` 생성자 | PCIe + IO flow 생성·엔진 등록 |
| 〃 | `main` | `Engine::Start_simulation` | 배선 → 검증 → 초기화 → 루프 |
| 루프 안, 시각 ≈ 0 | `IO_Flow_*` | `Submit_io_request` → PCIe | 요청이 장치로 간다 |
| 〃 | `Request_Fetch_Unit_NVMe` | PCIe 읽기 요청 | 명령·데이터를 DMA 로 가져온다 |
| 〃 | `Input_Stream_Manager_NVMe` | `segment_user_request` + 신호 | 요청 → 페이지 트랜잭션 |
| 〃 | `Data_Cache_Manager` | `Address_Mapping_Unit::Translate_lpa_to_ppa_and_dispatch` | **FTL 진입** |

이 흐름에서 중요한 습관 하나: **객체 사이의 호출은 두 종류**다. ① 직접 호출( 위 표의 대부분 ), ② `Register_sim_event` 로 예약한 미래 이벤트( PCIe 전송 시간, 플래시 지연 등 시간이 걸리는 곳 ). 어떤 함수의 다음 동작을 찾을 때 "이 함수가 이벤트를 예약하는가?" 를 먼저 보면 흐름을 놓치지 않는다.

<div style="margin-top: 60px;"></div>

## 4. 다음에 읽을 곳

- `Engine::Register_sim_event` / `Sim_Event` / 이벤트 트리 — 시간이 어떻게 흐르는지 ( `src/sim/` )
- `Data_Cache_Manager_Flash_Advanced` — 캐시 적중·destage·eviction ( 위 ⑨ 의 한가운데 )
- `Address_Mapping_Unit_Page_Level::query_cmt` 와 `allocate_plane_for_user_write` — FTL 첫 코드
- `TSU_Priority_OutOfOrder::Schedule` — FTL 이 만든 물리 트랜잭션이 칩 명령이 되는 곳

## 관련 문서

- [MQSim 코드 분석 ( 2026/10/04 )](/ftl-visual-simulator/reference/mqsim-code-analysis-20261004/)
- [MQSim 개괄](/ftl-visual-simulator/reference/mqsim/code-analysis/overview/)
- [MQSim 2일 학습 가이드](/ftl-visual-simulator/reference/mqsim/study-guide/)
