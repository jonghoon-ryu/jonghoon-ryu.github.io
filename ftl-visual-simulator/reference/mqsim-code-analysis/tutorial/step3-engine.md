---
layout: default
title: 3. 엔진 시작과 이벤트 루프
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step3-engine/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 3. 엔진 시작과 이벤트 루프

`main.cpp:296` 의 `Simulator->Start_simulation()` 에서 비로소 시뮬레이션이 돈다. 엔진은 등록된 객체 전부를 **세 번** 훑은 뒤 이벤트 루프로 들어간다.

<svg viewBox="0 0 980 300" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Maru Buri','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="엔진 시작 과정"><defs><marker id="ast" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="asts" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">Engine::Start_simulation() (sim/Engine.cpp:56)</text><rect x="15" y="50" width="225" height="90" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="127.5" y="85.25" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">① Setup_triggers()</text><text x="127.5" y="104.25" font-size="11" fill="#4d5656" text-anchor="middle">모든 객체를 훑으며</text><text x="127.5" y="119.25" font-size="11" fill="#4d5656" text-anchor="middle">신호(콜백) 연결</text><line x1="240" y1="95" x2="255" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ast)"/><rect x="255" y="50" width="225" height="90" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="367.5" y="85.25" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">② Validate_simulation_config()</text><text x="367.5" y="104.25" font-size="11" fill="#4d5656" text-anchor="middle">연결이 빠졌는지 검사</text><text x="367.5" y="119.25" font-size="11" fill="#4d5656" text-anchor="middle">(없으면 예외)</text><line x1="480" y1="95" x2="495" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ast)"/><rect x="495" y="50" width="225" height="90" rx="8" fill="#f4ecf7" fill-opacity="1.0" stroke="#7d3c98" stroke-width="2"/><text x="607.5" y="85.25" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">③ Start_simulation()</text><text x="607.5" y="104.25" font-size="11" fill="#4d5656" text-anchor="middle">각자 초기화</text><text x="607.5" y="119.25" font-size="11" fill="#4d5656" text-anchor="middle">첫 이벤트 등록</text><line x1="720" y1="95" x2="735" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ast)"/><rect x="735" y="50" width="225" height="90" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="847.5" y="85.25" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">④ 이벤트 루프</text><text x="847.5" y="104.25" font-size="11" fill="#4d5656" text-anchor="middle">가장 이른 이벤트부터</text><text x="847.5" y="119.25" font-size="11" fill="#4d5656" text-anchor="middle">꺼내 실행</text><rect x="15" y="175" width="465" height="105" rx="8" fill="#f4f6f7" fill-opacity="1.0" stroke="#7f8c8d" stroke-width="2"/><text x="247.5" y="210.75" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">③ 에서 실제로 하는 일</text><text x="247.5" y="229.25" font-size="10.5" fill="#4d5656" text-anchor="middle">Host_System: NVMe stream 생성, (preconditioning 켜졌으면 SSD 미리 채움)</text><text x="247.5" y="243.75" font-size="10.5" fill="#4d5656" text-anchor="middle">Address_Mapping_Unit: Store_mapping_table_on_flash_at_start()</text><text x="247.5" y="258.25" font-size="10.5" fill="#4d5656" text-anchor="middle">IO_Flow_*: 첫 이벤트 등록 (QUEUE_DEPTH 는 t = 1 ns)</text><rect x="500" y="175" width="465" height="105" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="732.5" y="203.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">그 외 객체의 Start_simulation()</text><text x="732.5" y="222.0" font-size="10.5" fill="#4d5656" text-anchor="middle">FTL · SSD_Device · Data_Cache_Manager · PCIe_Link …</text><text x="732.5" y="236.5" font-size="10.5" fill="#4d5656" text-anchor="middle">→ 빈 함수</text><text x="732.5" y="251.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="732.5" y="265.5" font-size="10.5" fill="#4d5656" text-anchor="middle">※ 객체 목록이 unordered_map 이라 호출 순서는 정해져 있지 않다</text></svg>


<div style="margin-top: 60px;"></div>

## 1. Setup_triggers — 신호를 연결한다 (`Engine.cpp:64`)

객체들이 서로의 "이벤트 발생 알림" 에 자기 함수를 등록한다. 직접 호출 없이 객체 사이를 잇는 **배선**이다.

| 알림을 내는 쪽 | 알림 | 받는 쪽 (등록하는 함수) |
|---|---|---|
| `Host_Interface_NVMe` | 사용자 요청 도착 | `Data_Cache_Manager::handle_user_request_arrived_signal` |
| `Data_Cache_Manager` | 사용자 요청 완료 | `Host_Interface_Base::handle_user_request_serviced_signal_from_cache` |
| `NVM_PHY_ONFI_NVDDR2` | 트랜잭션 완료 | AMU · GC/WL · 캐시 · TSU 의 `handle_transaction_serviced_signal_from_PHY` |
| `NVM_PHY_ONFI_NVDDR2` | 채널 유휴 / 칩 유휴 | `TSU_Base::handle_channel_idle_signal` · `handle_chip_idle_signal` |
| `Flash_Chip` | 칩 준비됨 | `NVM_PHY_ONFI_NVDDR2::handle_ready_signal_from_chip` (`NVM_PHY_ONFI_NVDDR2.cpp:50` 에서 등록) |

요청은 **호스트 인터페이스 → 캐시 → FTL 부품들 → PHY → 칩** 으로 내려가고, 완료 신호는 **칩 → PHY → (매핑 · GC/WL · 캐시) → 호스트 인터페이스** 로 거슬러 올라온다. 특히 PHY 의 "트랜잭션 완료" 를 FTL 부품 셋이 모두 받는다는 점을 기억해 두자 — 8~10단계에서 계속 나온다.

## 2. Validate_simulation_config — 검사한다 (`Engine.cpp:71`)

필요한 포인터가 비어 있지 않은지 본다. `FTL::Validate_simulation_config()` (`FTL.cpp:35`)는 캐시 매니저 · 주소 매핑 · 블록 매니저 · GC 가 모두 연결됐는지 확인하고, 아니면 예외를 던진다.


<div style="margin-top: 60px;"></div>

## 3. Start_simulation — 초기화하고 첫 이벤트를 등록 (`Engine.cpp:77`)

하는 일이 있는 객체만 보면 이렇다.

| 객체 | 하는 일 |
|---|---|
| `Host_System` (`Host_System.cpp:114`) | NVMe 라면 flow 마다 `Create_new_stream()` 으로 SSD 쪽 stream 을 만든다. preconditioning 이 켜졌으면 SSD 를 미리 채운다 (샘플 설정은 꺼짐) |
| **`Address_Mapping_Unit_Page_Level`** (`:410`) | **FTL 쪽 첫 작업.** `Store_mapping_table_on_flash_at_start()` — 매핑 테이블을 담을 translation page 들을 플래시의 어느 plane·page 에 둘지 정하고 "사용 중" 으로 표시한다 |
| `IO_Flow_Synthetic` (`IO_Flow_Synthetic.cpp:197`) | **첫 이벤트를 등록.** `QUEUE_DEPTH` 방식은 시각 1 ns |
| `IO_Flow_Trace_Based` | trace 의 첫 줄 도착 시각에 첫 이벤트 등록 |

**요청이 하나도 오기 전에 플래시의 일부는 이미 채워져 있다.** 매핑 테이블 자체가 플래시에 저장되기 때문이다([FTL 의 부품들](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/ftl-parts/)의 GMT · translation page).

여기까지 끝나면 **이벤트 큐에는 flow 들이 등록한 첫 이벤트만 들어 있다.**


<div style="margin-top: 60px;"></div>

## 4. 이벤트 루프 (`Engine.cpp:81`)

```cpp
while (true) {
    if (_EventList->Count == 0 || stop) break;
    EventTreeNode* minNode = _EventList->Get_min_node();
    ev = minNode->FirstSimEvent;
    _sim_time = ev->Fire_time;              // 시계가 점프한다
    while (ev != NULL) {
        if (!ev->Ignore)
            ev->Target_sim_object->Execute_simulator_event(ev);   // :93
        ...
    }
    _EventList->Remove(minNode);
}
```

시각은 실제 시간이 아니라 이 루프가 꺼낼 때마다 뛴다([이벤트 엔진과 시간](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/event-engine/)). 큐가 비거나 `Stop_simulation()` 이 불리면 끝난다. 이제부터는 이벤트가 이벤트를 낳으며 요청이 SSD 안으로 들어간다.

## 확인해 보기

1. `Setup_triggers` 를 부르지 않으면 어떤 일이 생기나? 어떤 검사가 먼저 잡을까?
2. `Store_mapping_table_on_flash_at_start` 가 요청 전에 필요한 이유는? (6단계의 CMT miss 를 떠올려 보자)
3. 이벤트를 하나도 등록하지 않은 채 `Start_simulation()` 을 부르면 루프는 어떻게 되나?

> 풀이는 [부록 D. 확인해 보기 — 풀이](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-answers/) 에 있다. 먼저 코드에서 직접 찾아 보자.


<div style="margin-top: 60px;"></div>

<div class="step-nav"><span>[◂ 2. SSD 와 호스트 만들기](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step2-build-ssd/)</span><span>[4. 요청의 탄생 — SSD 입구까지 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step4-request-enters/)</span></div>
