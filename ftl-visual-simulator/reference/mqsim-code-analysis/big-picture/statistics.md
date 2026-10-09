---
layout: default
title: 통계와 결과 파일
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/statistics/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 통계와 결과 파일

시뮬레이션이 끝나면 `main()` 이 `workload_scenario_N.xml` 을 쓴다(`collect_results`, `main.cpp:231`). 이 페이지는 **그 파일을 읽는 법**과 통계 카운터(`ssd/Stats.*`, `Stats::` 정적 멤버)의 의미를 정리한다.


<div style="margin-top: 60px;"></div>

## 1. 파일의 구조

<svg viewBox="0 0 980 470" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="결과 XML 구조"><defs><marker id="axml" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="axmls" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">결과 XML (workload_scenario_N.xml) 의 구조 — collect_results(main.cpp:231)</text><rect x="380" y="40" width="220" height="40" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="490.0" y="65.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">MQSim_Results</text><rect x="120" y="115" width="230" height="40" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="235.0" y="140.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Host</text><rect x="630" y="115" width="230" height="40" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="745.0" y="140.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">SSDDevice</text><line x1="450" y1="80" x2="235" y2="115" stroke="#7f8c8d" stroke-width="2" marker-end="url(#axml)"/><line x1="530" y1="80" x2="745" y2="115" stroke="#7f8c8d" stroke-width="2" marker-end="url(#axml)"/><rect x="15" y="190" width="440" height="120" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="235.0" y="226.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Host.IO_Flow  (flow 마다)</text><text x="235.0" y="244.5" font-size="10.5" fill="#4d5656" text-anchor="middle">Request_Count · Read/Write_Request_Count</text><text x="235.0" y="259.0" font-size="10.5" fill="#4d5656" text-anchor="middle">IOPS · Bytes_Transferred · Bandwidth (읽기/쓰기 따로)</text><text x="235.0" y="273.5" font-size="10.5" fill="#4d5656" text-anchor="middle">Device_Response_Time (min/max)</text><text x="235.0" y="288.0" font-size="10.5" fill="#4d5656" text-anchor="middle">End_to_End_Request_Delay (min/max)</text><line x1="235" y1="155" x2="235" y2="190" stroke="#7f8c8d" stroke-width="2" marker-end="url(#axml)"/><rect x="480" y="190" width="120" height="130" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="540.0" y="239.5" font-size="10" font-weight="700" fill="#2c3e50" text-anchor="middle">SSDDevice.HostInterface</text><text x="540.0" y="256.5" font-size="9" fill="#4d5656" text-anchor="middle">stream 별 transaction 의</text><text x="540.0" y="269.5" font-size="9" fill="#4d5656" text-anchor="middle">Turnaround · Execution ·</text><text x="540.0" y="282.5" font-size="9" fill="#4d5656" text-anchor="middle">Transfer · Waiting 평균</text><line x1="745" y1="155" x2="540" y2="190" stroke="#7f8c8d" stroke-width="2" marker-end="url(#axml)"/><rect x="605" y="190" width="120" height="130" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="665.0" y="246.0" font-size="10" font-weight="700" fill="#2c3e50" text-anchor="middle">SSDDevice.FTL</text><text x="665.0" y="263.0" font-size="9" fill="#4d5656" text-anchor="middle">속성들: 발행한 flash 명령 종류별 개수,</text><text x="665.0" y="276.0" font-size="9" fill="#4d5656" text-anchor="middle">CMT hit/miss, GC · WL 횟수와 평균 이동 page 수</text><line x1="745" y1="155" x2="665" y2="190" stroke="#7f8c8d" stroke-width="2" marker-end="url(#axml)"/><rect x="730" y="190" width="120" height="130" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="790.0" y="246.0" font-size="10" font-weight="700" fill="#2c3e50" text-anchor="middle">SSDDevice.TSU</text><text x="790.0" y="263.0" font-size="9" fill="#4d5656" text-anchor="middle">큐마다: 들어온/나간 개수,</text><text x="790.0" y="276.0" font-size="9" fill="#4d5656" text-anchor="middle">평균·최대 큐 길이, 대기 시간</text><line x1="745" y1="155" x2="790" y2="190" stroke="#7f8c8d" stroke-width="2" marker-end="url(#axml)"/><rect x="855" y="190" width="120" height="130" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="915.0" y="239.5" font-size="10" font-weight="700" fill="#2c3e50" text-anchor="middle">SSDDevice.FlashChips</text><text x="915.0" y="256.5" font-size="9" fill="#4d5656" text-anchor="middle">칩마다 시간 비율:</text><text x="915.0" y="269.5" font-size="9" fill="#4d5656" text-anchor="middle">Execution · DataXfer ·</text><text x="915.0" y="282.5" font-size="9" fill="#4d5656" text-anchor="middle">Overlapped · Idle</text><line x1="745" y1="155" x2="915" y2="190" stroke="#7f8c8d" stroke-width="2" marker-end="url(#axml)"/><rect x="15" y="335" width="950" height="120" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="490.0" y="371.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">읽는 요령</text><text x="490.0" y="389.5" font-size="10.5" fill="#4d5656" text-anchor="middle">① 사용자가 체감한 성능: Host.IO_Flow 의 IOPS · Device_Response_Time</text><text x="490.0" y="404.0" font-size="10.5" fill="#4d5656" text-anchor="middle">② 왜 그런지: HostInterface 의 Waiting 이 크면 큐에서 오래 기다린 것(스케줄러·GC), Execution 은 칩 연산, Transfer 는 채널 점유</text><text x="490.0" y="418.5" font-size="10.5" fill="#4d5656" text-anchor="middle">③ FTL 의 일: CMT_Hits/Misses, Total_GC_Executions, Average_Page_Movement_For_GC, Issued_Flash_*_CMD</text><text x="490.0" y="433.0" font-size="10.5" fill="#4d5656" text-anchor="middle">④ 자원 사용률: FlashChips 의 Fraction_of_Time_* 와 TSU 큐의 Avg_Queue_Length</text></svg>

실제 샘플(`workload_scenario_1.xml`, 525줄)에서 확인한 구성이다. `SSDDevice.FTL` 은 요소 하나에 **속성이 수십 개** 붙어 있고, TSU 큐는 `[채널]@[칩]@우선순위` 이름으로 큐마다 한 줄씩(수백 줄) 나오며, 칩은 `@채널@칩` 마다 한 줄이다.


<div style="margin-top: 60px;"></div>

## 2. 호스트가 본 것 — IO_Flow

| 항목 | 의미 |
|---|---|
| `Request_Count` · `Read_/Write_Request_Count` | 완료된 요청 수 |
| `IOPS` · `Bandwidth` | 시뮬레이션 시간으로 환산한 처리량 (읽기·쓰기 따로) |
| `Device_Response_Time` | 요청이 **SQ 에 들어간 순간**(`Enqueue_time`)부터 완료까지 |
| `End_to_End_Request_Delay` | 호스트가 요청을 **만든 순간**(`Arrival_time`)부터 완료까지 — SQ 에 들어가기 전의 대기까지 포함 |

콘솔에도 flow 별로 같은 요약이 나온다(`collect_results` 의 `cout`).

<svg viewBox="0 0 980 300" style="font-variant-ligatures:none;width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="두 가지 시간"><defs><marker id="atime" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="atimes" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">같은 쓰기가 두 가지로 측정된다 (샘플 시나리오 1, flow 0, 단위 µs)</text><text x="15" y="62" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">flash transaction (page 하나)</text><rect x="15" y="75" width="842.1690371991247" height="40" rx="3" fill="#fdedec" fill-opacity="1.0" stroke="#c0392b" stroke-width="2"/><text x="436.08451859956233" y="100" font-size="11" fill="#2c3e50" text-anchor="middle">Waiting 6,551</text><rect x="857.1690371991247" y="75" width="8" height="40" rx="3" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><rect x="865.1690371991247" y="75" width="96.2882932166302" height="40" rx="3" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="913.3131838074397" y="100" font-size="11" fill="#2c3e50" text-anchor="middle">Exec 749</text><text x="15" y="138" font-size="11" fill="#4d5656" text-anchor="start">Turnaround = Waiting + Transfer + Execution = 7,312</text><text x="15" y="175" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">호스트가 본 응답 (Device_Response_Time)</text><rect x="15" y="188" width="62.22100656455142" height="40" rx="3" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="87.22100656455143" y="213" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="start">484 µs</text><rect x="15" y="245" width="950" height="45" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="490.0" y="272.0" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">왜 이렇게 다른가: WRITE_CACHE 는 DRAM 에 쓰자마자 호스트에 &quot;완료&quot; 를 돌려주고, flash 쓰기(page 단위 transaction)는 뒤에서 큐를 기다리며 진행한다</text></svg>

**호스트가 본 시간과 flash 가 쓴 시간은 다르다.** 캐시가 응답을 먼저 주기 때문이다([데이터 캐시 깊이 보기](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/data-cache/)). 그래서 Turnaround(=Waiting+Transfer+Execution)가 Device_Response_Time 보다 훨씬 길 수 있다.


<div style="margin-top: 60px;"></div>

## 3. FTL 속성

| 묶음 | 속성 | 읽는 법 |
|---|---|---|
| 발행한 flash 명령 | `Issued_Flash_Read_CMD`, `…_Multiplane_…`, `…_Interleaved_…`, `…_Copyback_…`, `…_Suspend_…` | **명령** 개수다. 멀티플레인 명령은 plane 이 여러 개여도 1 로 센다 → page 수와 다르다 |
| 매핑용 | `Issued_Flash_Read/Program_CMD_For_Mapping` | translation page 접근 |
| CMT | `CMT_Hits`, `CMT_Misses`, `Total_CMT_Queries`, `…_For_Read/Write` | 읽기·쓰기별 |
| GC / WL | `Total_GC_Executions`, `Average_Page_Movement_For_GC`, `Total_WL_Executions`, `Average_Page_Movement_For_WL` | 실행 횟수와 평균 이동 page 수 (한 번도 없으면 `-nan`) |

### 숫자를 읽을 때 주의 (코드로 확인한 것)

- **`CMT_Misses` 는 "그 자리에서 해결된 miss" 만 센다.** `query_cmt()` 에서 매핑을 바로 확보한 경우에만 `CMT_miss++` 가 불리고, 매핑 page 를 기다려야 하는 경우에는 읽기/쓰기별 카운터(`…_For_Read/Write`)만 오른다. 그래서 샘플에서 `CMT_Hits + CMT_Misses` 가 `Total_CMT_Queries` 와 맞지 않는다. 전체 miss 는 `…_For_Read` + `…_For_Write` 로 보는 것이 맞다.
- **WAF 를 이 파일에서 바로 얻을 수는 없다.** WAF = (호스트 쓰기 page + GC·WL 이동 page) ÷ 호스트 쓰기 page 이다. `Issued_Flash_Program_CMD` 는 명령 수라서 멀티플레인이면 과소집계된다. 이 프로젝트의 시뮬레이터는 page 단위 이벤트(`mapping_updated` 쓰기, `gc_page_migrated`)를 직접 세어 WAF 를 계산한다.
- 샘플 시나리오 1 은 `Total_GC_Executions = 0` 이다 — 빈 SSD 에서 시작해 GC 가 시작될 만큼 채워지지 않았기 때문이다([Preconditioning](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/preconditioning/)).


<div style="margin-top: 60px;"></div>

## 4. TSU 큐와 칩

- 큐 항목: `No_Of_Transactions_Enqueued/Dequeued`, `Avg_Queue_Length`, `Max_Queue_Length`, `STDev_Queue_Length`, `Avg/Max_Transaction_Waiting_Time`. **어느 큐(채널·칩·우선순위·소스)가 밀리는지** 찾을 때 쓴다.
- 칩 항목: `Fraction_of_Time_in_Execution`(array 가 일하는 시간), `…_in_DataXfer`(채널로 전송), `…_in_DataXfer_and_Execution`(겹침), `…_Idle`. 샘플에서는 칩이 약 92% 의 시간을 연산(프로그램)에 쓰고 전송은 1.6% 뿐이다 — **쓰기 부하에서는 칩 연산이 병목**이라는 뜻이다.


<div style="margin-top: 60px;"></div>

## 5. 이 프로젝트에서의 의미

시뮬레이터는 이 XML 을 쓰지 않는다. 엔진의 `getState()` 와 이벤트 hook 으로 같은 종류의 숫자를 **실시간**으로 얻어서 통계 패널(WAF · GC/WL 횟수 · erase 횟수 · valid page 비율)과 차트에 보여준다. 결과 XML 과 시뮬레이터의 숫자가 같은 원천(`Stats::`)에서 나오는지는 [골든 회귀 테스트](/ftl-visual-simulator/reference/code-change/upstream-diff/)가 확인한다.


<div style="margin-top: 60px;"></div>

## 관련 문서

- [튜토리얼 11단계 — 마무리](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step11-wrapup/) · [이벤트 엔진과 시간](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/event-engine/)
- [매핑 테이블은 어디에 저장되나](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/translation-pages/)
