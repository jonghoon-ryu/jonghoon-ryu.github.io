---
layout: default
title: 부록 C. 디버깅과 작은 실험
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-debugging/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 부록 C. 디버깅과 작은 실험

코드를 읽다가 막히면 **직접 돌려 보는 것**이 가장 빠르다. 이 부록은 (1) MQSim 을 빌드하고 (2) 작은 workload 로 하나씩 보고 (3) 디버거를 거는 방법을 정리한다. 모든 숫자는 `51f0f2d` 를 빌드해서 실제로 얻은 것이다.


<div style="margin-top: 60px;"></div>

## 1. 빌드와 실행

```bash
make                                   # g++ -std=c++11 -O3 -g, 결과물은 ./MQSim
./MQSim -i ssdconfig.xml -w tiny.xml    # 인자는 정확히 4개 (argc != 5 면 사용법 출력 후 종료)
```

실행할 때 알아 둘 것이 세 가지 있다.

1. **끝에 `cin.get()` 으로 멈춘다**(`main.cpp` 마지막 줄, "Press any key to exit"). 스크립트나 배치에서 돌릴 때는 `echo | ./MQSim …` 또는 `< /dev/null` 로 입력을 막아 준다.
2. **`PRINT_ERROR` 도 `cin.get()` 한 뒤 `exit(1)` 한다**(`Sim_Defs.h:20`). 오류가 나면 터미널이 멈춘 것처럼 보이니 Enter 를 눌러야 종료된다.
3. 설정 파일이 **없으면** 기본값으로 만들어 그 이름으로 저장하고 계속 진행한다(`read_configuration_parameters`, `main.cpp:38`). 경로를 잘못 써도 오류가 아니라 새 파일이 생길 수 있다.

결과 파일은 workload 파일 이름 뒤에 `_scenario_N.xml` 이 붙어서 생긴다([통계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/statistics/)).


<div style="margin-top: 60px;"></div>

## 2. 작은 workload 로 한 가지씩 — 20개 실험

기본 `workload.xml` 은 시나리오 3개에 수만 요청이라 구조를 보기에는 너무 크다. 아래처럼 **요청 20개짜리**를 만들면 숫자 하나하나가 설명된다.

```xml
<IO_Flow_Parameter_Set_Synthetic>
  <Priority_Class>HIGH</Priority_Class>
  <Device_Level_Data_Caching_Mode>TURNED_OFF</Device_Level_Data_Caching_Mode>
  <Channel_IDs>0,1,2,3,4,5,6,7</Channel_IDs>   <Chip_IDs>0,1,2,3</Chip_IDs>
  <Die_IDs>0,1</Die_IDs>   <Plane_IDs>0,1</Plane_IDs>
  <Initial_Occupancy_Percentage>0</Initial_Occupancy_Percentage>
  <Working_Set_Percentage>1</Working_Set_Percentage>
  <Synthetic_Generator_Type>QUEUE_DEPTH</Synthetic_Generator_Type>
  <Read_Percentage>0</Read_Percentage>              <!-- 0 = 쓰기만, 100 = 읽기만 -->
  <Address_Distribution>RANDOM_UNIFORM</Address_Distribution>
  <Request_Size_Distribution>FIXED</Request_Size_Distribution>
  <Average_Request_Size>16</Average_Request_Size>   <!-- 16 sector = 8 KB = page 하나 -->
  <Average_No_of_Reqs_in_Queue>1</Average_No_of_Reqs_in_Queue>   <!-- 큐 깊이 1: 한 번에 하나 -->
  <Total_Requests_To_Generate>20</Total_Requests_To_Generate>
  <Seed>1</Seed>
</IO_Flow_Parameter_Set_Synthetic>
```

**큐 깊이 1 + 20 요청**이라서 요청이 서로 겹치지 않고, 응답 시간이 그 요청 하나가 겪은 일 그대로다. 네 가지로 바꿔 돌렸다.

<svg viewBox="0 0 980 330" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="실험 결과 비교"><defs><marker id="abars" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="abarss" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="18" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">같은 SSD 에 요청 20개 — 무엇을 보내느냐에 따라 Device_Response_Time (µs, 실측)</text><text x="15" y="72" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">쓰기 · 캐시 꺼짐</text><rect x="220" y="50" width="560.0" height="34" rx="4" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="790.0" y="72" font-size="11.5" fill="#2c3e50" text-anchor="start">854 µs   (tiny.xml)</text><text x="15" y="128" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">읽기 · 캐시 꺼짐</text><rect x="220" y="106" width="117.37704918032787" height="34" rx="4" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="347.37704918032784" y="128" font-size="11.5" fill="#2c3e50" text-anchor="start">179 µs   (tinyread.xml)</text><text x="15" y="184" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">쓰기 · WRITE_CACHE</text><rect x="220" y="162" width="28.19672131147541" height="34" rx="4" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="258.1967213114754" y="184" font-size="11.5" fill="#2c3e50" text-anchor="start">43 µs   (tinycache.xml)</text><text x="15" y="240" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">읽기 50% 쓰기 50%</text><rect x="220" y="218" width="272.1311475409836" height="34" rx="4" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="502.1311475409836" y="240" font-size="11.5" fill="#2c3e50" text-anchor="start">415 µs   (tinymix.xml (평균))</text><rect x="15" y="275" width="950" height="45" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="490.0" y="302.25" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">읽기 한 번은 약 2 × tR(75) 의 매핑+data 읽기, 쓰기 한 번은 tR + tPROG(750). 캐시는 tPROG 를 호스트 시야에서 지운다</text></svg>

| 실험 | 바꾼 것 | 결과 파일에서 보이는 것 |
|---|---|---|
| `tiny` | (기본: 쓰기, 캐시 꺼짐) | `Issued_Flash_Program_CMD`=20, `Issued_Flash_Read_CMD_For_Mapping`=20, `CMT_Misses_For_Write`=20, 응답 854 |
| `tinycache` | 캐시 `WRITE_CACHE` | program 은 그대로 20 인데 응답이 **43** |
| `tinyread` | `Read_Percentage` 100 | flash 읽기 40 (data 20 + 매핑 20), 응답 179 |
| `tinymix` | `Read_Percentage` 50 | 읽기 13 + 쓰기 7 (무작위라 정확히 10:10 이 아니다), 응답 평균 415 · 최소 179 |

이 표만으로도 확인되는 것이 많다. **요청마다 매핑 읽기가 한 번**(CMT 가 비어 있고 요청마다 다른 translation page 를 건드림), **쓰기 응답이 읽기보다 tPROG 만큼 길다**, **캐시가 응답만 짧게 한다**, 그리고 [부록 A](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-read-path/)에서 본 `CMT_Misses` 합계 칸 이상(0).

> **어떻게 읽었나**: 같은 방식으로 실험을 더 해 보라. `Total_Requests_To_Generate` 를 늘리고 `Initial_Occupancy_Percentage` 를 올리고 `Working_Set_Percentage` 를 키우면 GC 가 켜지는 지점이 보인다. 먼저 [FTL 개념 ↔ 파라미터 대응](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/concept-mapping/)에서 어떤 파라미터가 어느 부품을 움직이는지 보고 정하면 된다.


<div style="margin-top: 60px;"></div>

## 3. `DEBUG()` 로그 켜기

코드에는 `DEBUG(…)` 호출이 **23곳** 있다(호스트 · 매핑 · TSU · PHY · 칩 · GC · 엔진). 기본으로는 **아무것도 출력하지 않는다.** 정의가 이렇다(`sim/Sim_Defs.h:27`).

```cpp
#define DEBUG(M) //std::cout<<M<<std::endl;
```

`//` 를 지우면 켜진다. 다만 **헤더 하나가 바뀌므로 전체가 다시 빌드**되고(`make clean && make`), 출력이 매우 많아지므로 위의 20개 실험과 함께 쓴다.

```bash
sed -i 's|#define DEBUG(M) //std::cout|#define DEBUG(M) std::cout|' src/sim/Sim_Defs.h
make clean && make
echo | ./MQSim -i ssdconfig.xml -w tiny.xml | grep -v RegisterEvent | head -40
```

`DEBUG2` 도 같은 식이다. 끝나면 `git checkout src/sim/Sim_Defs.h` 로 되돌린다. (빌드는 `make -j8 CC_FLAGS="-std=c++11 -O0 -g"` 로 3초 안팎이었다.)

### 실제 출력 — 쓰기 한 번

`tiny.xml`(쓰기만, 캐시 꺼짐)의 **첫 요청**이 남긴 줄이다(`RegisterEvent` 줄은 엔진이 이벤트를 예약할 때마다 찍힌다; 시각은 ns).

```text
* Host: Request generated - Write, LBA:1487008, Size_in_bytes:16     ← ① 호스트가 요청 생성 (Size 는 실은 sector 수)
Address mapping table query - Stream ID:0, LPA:92938, MISS           ← ② CMT miss
2546 Issueing Transaction - Type:Read, PPA:34078976, LPA:1844…(NO_LPA), Channel: 4, Chip: 0
Chip 4, 0, 0: Sending read command to chip for LPA: 1844…(NO_LPA)   ← ③ 매핑 page 를 읽는 명령 (LPA 가 NO_LPA)
Command execution started on channel: 4 chip: 0
Channel 4 Chip 0- Finished executing read command                   ← ④ 읽기 끝: 시각 79,392
Address mapping table insert entry - Stream ID:0, LPA:92938, PPA:NO_PPA   ← ⑤ CMT 에 항목 삽입 (아직 안 쓴 LPA)
Address mapping table update entry - Stream ID:0, LPA:92938, PPA:18874368 ← ⑥ 새 page 할당
79392 Issueing Transaction - Type:Write, PPA:18874368, LPA:92938, Channel: 2, Chip: 1
Chip 2, 1, 0: Sending program command to chip for LPA: 92938        ← ⑦ program 명령
Channel 2 Chip 1- Finished executing program command                 ← ⑧ 끝: 시각 854,329
** Host Interface: Request #0 from stream #0 is finished            ← ⑨ 완료 → 호스트에 통지
```

| 구간 | 시각(ns) | 길이 | 설명 |
|---|--:|--:|---|
| 요청 → 매핑 읽기 발행 | 2,546 | 2.5 µs | PCIe 로 SQ → SSD, 쪼개기, CMT 조회 |
| 매핑 읽기 | 2,546 → 79,392 | **76.8 µs** | tR 75 µs + 명령·데이터 전송 |
| program | 79,392 → 854,329 | **774.9 µs** | tPROG 750 µs + 전송 |
| 완료 | 854,329 | — | 호스트가 본 응답 = 854 µs |

이 25줄이 [부록 B]의 "흐름" 전체이고, 숫자 하나하나가 앞의 실험표(854 µs)와 맞는다. 더 큰 workload 에서도 요청 번호(`Request #N`)를 따라가면 한 요청의 일생이 보인다.


<div style="margin-top: 60px;"></div>

## 4. gdb 로 따라가기

`-g` 는 이미 켜져 있다. 다만 `-O3` 라서 변수가 `<optimized out>` 으로 나오고 줄이 건너뛰어진다. 이 문서의 단계를 단계별로 걸어 볼 때는 최적화를 끄고 빌드한다.

```bash
make clean && make CC_FLAGS="-std=c++11 -O0 -g"
gdb --args ./MQSim -i ssdconfig.xml -w tiny.xml
```

<svg viewBox="0 0 980 480" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="중단점 지도"><defs><marker id="abpmap" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="abpmaps" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="18" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">gdb 중단점을 걸 만한 곳 — 요청이 지나가는 순서대로</text><rect x="15" y="38" width="34" height="46" rx="17" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="32" y="67" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">1</text><rect x="60" y="38" width="440" height="46" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="280.0" y="65.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">IO_Flow_Base::Submit_io_request</text><rect x="510" y="38" width="450" height="46" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="735.0" y="65.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">호스트가 요청을 SQ 에 넣는 곳</text><rect x="15" y="92" width="34" height="46" rx="17" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="32" y="121" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">2</text><rect x="60" y="92" width="440" height="46" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="280.0" y="119.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Input_Stream_Manager_NVMe::segment_user_request</text><rect x="510" y="92" width="450" height="46" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="735.0" y="119.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">요청이 page 단위 transaction 으로 쪼개짐 (Host_Interface_NVMe.cpp:170)</text><rect x="15" y="146" width="34" height="46" rx="17" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="32" y="175" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">3</text><rect x="60" y="146" width="440" height="46" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="280.0" y="173.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Data_Cache_Manager_Flash_Advanced::process_new_user_request</text><rect x="510" y="146" width="450" height="46" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="735.0" y="173.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">캐시 모드별 갈림길 (:186)</text><rect x="15" y="200" width="34" height="46" rx="17" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="32" y="229" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">4</text><rect x="60" y="200" width="440" height="46" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="280.0" y="227.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Address_Mapping_Unit_Page_Level::query_cmt</text><rect x="510" y="200" width="450" height="46" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="735.0" y="227.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">CMT hit/miss (:510)</text><rect x="15" y="254" width="34" height="46" rx="17" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="32" y="283" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">5</text><rect x="60" y="254" width="440" height="46" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="280.0" y="281.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Address_Mapping_Unit_Page_Level::allocate_page_in_plane_for_user_write</text><rect x="510" y="254" width="450" height="46" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="735.0" y="281.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">쓰기: page 할당 · 옛 page invalid (:1146)</text><rect x="15" y="308" width="34" height="46" rx="17" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="32" y="337" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">6</text><rect x="60" y="308" width="440" height="46" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="280.0" y="335.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">TSU_Base::issue_command_to_chip</text><rect x="510" y="308" width="450" height="46" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="735.0" y="335.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">플래시 칩에 명령이 나가는 순간 (:72)</text><rect x="15" y="362" width="34" height="46" rx="17" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="32" y="391" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">7</text><rect x="60" y="362" width="440" height="46" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="280.0" y="389.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">GC_and_WL_Unit_Page_Level::Check_gc_required</text><rect x="510" y="362" width="450" height="46" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="735.0" y="389.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">GC 시작 여부 (:43)</text><rect x="15" y="416" width="34" height="46" rx="17" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="32" y="445" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">8</text><rect x="60" y="416" width="440" height="46" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="280.0" y="443.25" font-size="10.5" font-weight="700" fill="#2c3e50" text-anchor="middle">IO_Flow_Base::NVMe_consume_io_request</text><rect x="510" y="416" width="450" height="46" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="735.0" y="443.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">완료가 호스트에 도착 (:247)</text></svg>

```gdb
(gdb) break SSD_Components::Address_Mapping_Unit_Page_Level::query_cmt
(gdb) run
(gdb) bt                  # 호출 스택: 여기까지 어떻게 왔나
(gdb) p transaction->LPA  # 지금 보는 transaction 의 LPA
(gdb) p *transaction
(gdb) finish              # 이 함수가 끝날 때까지
```

요령:

- **이벤트 기반이라 `bt` 가 얕다.** 이벤트 핸들러는 `Engine::Start_simulation` 에서 불리므로 스택이 `Start_simulation → Execute_simulator_event → …` 정도로 짧다. 호출자는 스택이 아니라 **누가 이 이벤트를 예약했는가**로 따라가야 한다([이벤트 엔진과 시간](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/event-engine/)).
- `break … if transaction->LPA == 5` 처럼 **조건 중단점**을 쓰면 특정 데이터만 따라갈 수 있다.
- `watch Stats::Total_gc_executions` 로 GC 가 시작되는 순간에 멈출 수도 있다(정적 멤버).


<div style="margin-top: 60px;"></div>

## 5. 자주 만나는 일

| 증상 | 원인 |
|---|---|
| 실행이 끝났는데 터미널이 안 돌아옴 | 마지막 `cin.get()` — Enter |
| `No implementation is available for the specified transaction scheduling algorithm` | `Transaction_Scheduling_Policy` 를 `FLIN` 으로 둠. 파서는 받지만 `SSD_Device.cpp` 에서 해당 case 가 주석 처리되어 있다 |
| `Requesting a free block from an empty pool!` 등 `PRINT_ERROR` | 시뮬레이션된 SSD 가 가득 참(OP 부족, GC 못 따라감) — 설정을 바꿔야 한다 |
| 결과 `*_scenario_1.xml` 이 workload 파일 옆이 아닌 다른 곳에 생김 | 결과 경로는 **workload 파일 경로**에서 만든다(확장자 앞까지) |
| `Average_Page_Movement_For_GC` 가 `-nan` | GC 가 한 번도 안 돌아서 0 으로 나눔 — 정상 |


<div class="step-nav"><span>[◂ 부록 B. 완료 경로](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-completion/)</span><span>[부록 D. 확인해 보기 답 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-answers/)</span></div>
