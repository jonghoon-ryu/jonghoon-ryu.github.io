---
layout: default
title: 11. 마무리 — 전체 콜 그래프
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step11-wrapup/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 11. 마무리 — 전체 콜 그래프

요청 하나가 끝나는 곳까지 마저 따라가고, 전체를 한 장으로 정리한다.


<div style="margin-top: 60px;"></div>

## 1. 요청이 끝날 때

플래시 program 이 끝나면 "트랜잭션 완료" 신호가 올라온다([8단계](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step8-tsu-chip/)). 캐시가 이를 받아 사용자 요청의 모든 조각이 끝났는지 확인하고, 끝났으면 호스트 인터페이스로 "요청 완료" 를 올린다. `Request_Fetch_Unit_NVMe::Send_completion_queue_element()` 가 **완료 항목(CQE)을 PCIe 로 호스트에 쓴다.** 호스트의 `IO_Flow_Base::NVMe_consume_io_request()` (`IO_Flow_Base.cpp:247`)가 응답 시간을 통계에 더하고, `QUEUE_DEPTH` 방식의 flow 는 **새 요청을 하나 더** 만든다 — 4단계의 닫힌 루프가 여기서 닫힌다.

> WRITE_CACHE 가 켜져 있으면 사용자 요청은 **DRAM 쓰기가 끝난 시점**에 이미 완료된다. flash program 은 그와 별개로(나중에) 끝난다. 두 완료 시점이 다르다는 것을 기억하자.

## 2. 시뮬레이션이 끝나면

이벤트가 모두 소진되거나 `Stop_Time` 에 닿으면 이벤트 루프가 끝나고 `main()` 이 `collect_results()` (`main.cpp:231`)를 부른다. flow 별 요청 수 · IOPS · 대역폭 · 응답 시간, 그리고 FTL 통계(GC 실행 횟수, 이동한 page, CMT hit/miss, erase 히스토그램 …)가 `workload_scenario_N.xml` 에 써진다. 마지막에 "Press any key" 를 기다리므로(`cin.get()`) 배치로 돌릴 때는 이 줄을 빼는 것이 편하다.


<div style="margin-top: 60px;"></div>

## 3. 한 장으로 보기

<svg viewBox="0 0 980 560" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="쓰기 요청의 전체 콜 그래프"><defs><marker id="acg" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="acgs" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">쓰기 요청 하나의 전체 콜 그래프 (굵은 상자 = 이 튜토리얼의 단계)</text><rect x="360" y="40" width="260" height="40" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="490.0" y="64.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">main()</text><text x="350" y="65" font-size="12" font-weight="700" fill="#7f8c8d" text-anchor="end">1</text><rect x="360" y="100" width="260" height="40" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="490.0" y="124.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">Engine::Start_simulation</text><text x="350" y="125" font-size="12" font-weight="700" fill="#7f8c8d" text-anchor="end">3</text><rect x="360" y="160" width="260" height="40" rx="8" fill="#fdf2e9" fill-opacity="1.0" stroke="#ca6f1e" stroke-width="2"/><text x="490.0" y="184.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">IO_Flow::Submit_io_request</text><text x="350" y="185" font-size="12" font-weight="700" fill="#7f8c8d" text-anchor="end">4</text><rect x="360" y="220" width="260" height="40" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="490.0" y="244.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">Request_Fetch_Unit_NVMe</text><text x="350" y="245" font-size="12" font-weight="700" fill="#7f8c8d" text-anchor="end">4</text><rect x="360" y="280" width="260" height="40" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="490.0" y="304.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">segment_user_request</text><text x="350" y="305" font-size="12" font-weight="700" fill="#7f8c8d" text-anchor="end">4</text><rect x="360" y="340" width="260" height="40" rx="8" fill="#fef9e7" fill-opacity="1.0" stroke="#b7950b" stroke-width="2"/><text x="490.0" y="364.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">Data_Cache::write_to_destage_buffer</text><text x="350" y="365" font-size="12" font-weight="700" fill="#7f8c8d" text-anchor="end">5</text><rect x="360" y="400" width="260" height="40" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="490.0" y="424.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">AMU::Translate_lpa_to_ppa_and_dispatch</text><text x="350" y="425" font-size="12" font-weight="700" fill="#7f8c8d" text-anchor="end">5</text><rect x="360" y="460" width="260" height="40" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="490.0" y="484.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">query_cmt / translate_lpa_to_ppa</text><text x="350" y="485" font-size="12" font-weight="700" fill="#7f8c8d" text-anchor="end">6</text><line x1="490" y1="80" x2="490" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acg)"/><line x1="490" y1="140" x2="490" y2="160" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acg)"/><line x1="490" y1="200" x2="490" y2="220" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acg)"/><line x1="490" y1="260" x2="490" y2="280" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acg)"/><line x1="490" y1="320" x2="490" y2="340" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acg)"/><line x1="490" y1="380" x2="490" y2="400" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acg)"/><line x1="490" y1="440" x2="490" y2="460" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acg)"/><rect x="10" y="400" width="330" height="60" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="175.0" y="420.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">7. allocate_page_in_plane_for_user_write</text><text x="175.0" y="438.5" font-size="10" fill="#4d5656" text-anchor="middle">→ Flash_Block_Manager::Allocate_block_and_page…</text><text x="175.0" y="452.5" font-size="10" fill="#4d5656" text-anchor="middle">   frontier 가 차면 Check_gc_required</text><rect x="10" y="480" width="330" height="60" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="175.0" y="507.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">8. TSU::Submit → Schedule → PHY → Flash_Chip</text><text x="175.0" y="525.5" font-size="10" fill="#4d5656" text-anchor="middle">완료: broadcastTransactionServicedSignal</text><rect x="640" y="400" width="330" height="60" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="805.0" y="427.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">9. GC_and_WL::Check_gc_required</text><text x="805.0" y="445.5" font-size="10" fill="#4d5656" text-anchor="middle">→ read/write/erase transaction → 완료 신호 체인</text><rect x="640" y="480" width="330" height="60" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="805.0" y="507.5" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="middle">10. check_static_wl_required</text><text x="805.0" y="525.5" font-size="10" fill="#4d5656" text-anchor="middle">→ run_static_wearleveling</text><line x1="360" y1="480" x2="340" y2="430" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acg)"/><line x1="360" y1="490" x2="340" y2="505" stroke="#7f8c8d" stroke-width="2" marker-end="url(#acg)"/><line x1="620" y1="480" x2="640" y2="430" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#acg)"/><line x1="640" y1="505" x2="620" y2="490" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="6 4" marker-end="url(#acg)"/><rect x="640" y="40" width="330" height="120" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="805.0" y="82.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">시간이 걸리는 곳 (이벤트 예약)</text><text x="805.0" y="101.5" font-size="11" fill="#4d5656" text-anchor="middle">PCIe 전송 · DRAM 접근 · 플래시 지연</text><text x="805.0" y="116.5" font-size="11" fill="#4d5656" text-anchor="middle">→ 이 지점마다 호출 사슬이 끊기고</text><text x="805.0" y="131.5" font-size="11" fill="#4d5656" text-anchor="middle">   나중에 Execute_simulator_event 에서 이어진다</text></svg>

## 4. FTL 의 질문과 답

| 질문 | 어디서 | 단계 |
|---|---|---|
| 이 LPA 는 지금 어디 있나? | `query_cmt` → CMT → (miss 면) translation page 읽기 | 6 |
| 어느 plane 에 쓸까? | `allocate_plane_for_user_write` (CWDP) | 7 |
| 어느 page 에 쓸까? | `Data_wf` 의 다음 빈 page | 7 |
| 옛 데이터는? | `Invalidate_page_in_block` — 지우지 않고 invalid 로 | 7 |
| 칩에는 언제, 누가 먼저? | TSU 큐 · 채널 라운드로빈 · 매핑 > GC > 사용자 | 8 |
| 공간이 모자라면? | `Check_gc_required` → victim → 이동 → erase | 9 |
| 어느 block 이 닳았나? | free pool 의 정렬 + static WL | 10 |


<div style="margin-top: 60px;"></div>

## 5. 직접 확인해 보기 — 이 프로젝트의 시뮬레이터

이 튜토리얼의 장면 대부분을 [시뮬레이터](/ftl-visual-simulator/run-simulator/)에서 눈으로 볼 수 있다.

| 이 튜토리얼 | 시뮬레이터 |
|---|---|
| 7단계 out-of-place update | **매핑 기본** — 로그의 LPN 을 클릭하면 그 데이터의 여정 |
| 5단계 캐시가 쓰기를 흡수 | "DRAM 쓰기 캐시" 를 끄고 켜며 GC 횟수 비교 |
| 9단계 GC · victim · WAF | **GC 시연** — 빈 block 차트 · "왜 이 block 을 골랐나요?" · 비교 실험실 |
| 10단계 static WL | **마모평준화 시연** |

## 6. 다음에 읽을 곳

- `Data_Cache_Manager_Flash_Advanced` 의 evict · destage 경로 전체 (5단계는 쓰기만 봤다)
- `Flash_Chip::Suspend()` / `Resume()` — erase 도중 read 가 끼어드는 방법
- Preconditioning (`FTL::Perform_precondition`) — 시작 전에 SSD 를 정상 상태로 미리 채우는 방법
- `Address_Mapping_Unit_Page_Level::handle_transaction_serviced_signal_from_PHY` (`:1665`) — 6단계 miss 가 어떻게 풀리는지
- 이 프로젝트가 원본에서 바꾼 곳: [Code Change](/ftl-visual-simulator/reference/code-change/)

## 7. 마지막 확인 문제

1. `./MQSim` 을 실행해서 첫 `Write` 가 일어나는 **가장 이른 시각**은 몇 ns 이고, 그 시각에 등록된 이벤트는 누가 만들었나?
2. 4 KB 쓰기 하나가 flash program 하나가 되기까지, 일어날 수 있는 flash **read** 는 모두 몇 종류인가? (CMT miss · update read)
3. GC 가 한 번 일어나면 호스트 쓰기 대비 flash 쓰기가 늘어나는 이유를 3단계 호출 사슬로 설명해 보자.

<div style="margin-top: 60px;"></div>

<div class="step-nav"><span>[◂ 10. FTL ⑤ 마모평준화](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step10-wl/)</span><span>[튜토리얼 목차 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/)</span></div>
