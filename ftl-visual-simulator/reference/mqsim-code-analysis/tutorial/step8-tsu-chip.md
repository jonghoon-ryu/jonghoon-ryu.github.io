---
layout: default
title: 8. FTL ③ 스케줄러와 플래시 칩
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step8-tsu-chip/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# 8. FTL ③ 스케줄러와 플래시 칩

물리 주소가 정해진 transaction 은 `TSU->Submit_transaction()` 으로 **TSU(Transaction Scheduling Unit)** 에 들어간다. TSU 가 "어느 칩에 언제 명령을 내릴까" 를 정하고, 그 아래 PHY 와 칩이 실제로 시간을 쓴다.

<svg viewBox="0 0 980 400" style="width:100%;max-width:980px;height:auto;display:block;margin:1rem auto;" font-family="'Maru Buri','Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="TSU 의 큐와 우선순위"><defs><marker id="atsu" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="atsus" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="490" y="20" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">TSU 큐와 서비스 순서 (TSU_Priority_OutOfOrder)</text><rect x="15" y="150" width="150" height="70" rx="8" fill="#eef2f7" fill-opacity="1.0" stroke="#34495e" stroke-width="2"/><text x="90.0" y="175.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">transaction</text><text x="90.0" y="194.5" font-size="11" fill="#4d5656" text-anchor="middle">_receive_slots</text><text x="90.0" y="209.5" font-size="11" fill="#4d5656" text-anchor="middle">(Schedule() 때 분류)</text><rect x="195" y="35" width="330" height="330" rx="10" fill="#f4ecf7" fill-opacity="0.35" stroke="#7d3c98" stroke-width="1.5" stroke-dasharray="6 4"/><text x="207" y="53" font-size="12" font-weight="700" fill="#7d3c98" text-anchor="start">소스 × 종류 별 큐  [채널][칩]</text><rect x="215" y="65" width="290" height="44" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="360.0" y="92.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">MappingRead / MappingWrite</text><rect x="215" y="121" width="290" height="44" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="360.0" y="148.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">UserRead[우선순위]</text><rect x="215" y="177" width="290" height="44" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="360.0" y="204.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">UserWrite[우선순위]</text><rect x="215" y="233" width="290" height="44" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="360.0" y="260.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">GCRead / GCWrite</text><rect x="215" y="289" width="290" height="44" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="360.0" y="316.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">GCErase</text><line x1="165" y1="185" x2="195" y2="185" stroke="#7f8c8d" stroke-width="2" marker-end="url(#atsu)"/><rect x="560" y="60" width="190" height="80" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="655.0" y="90.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">채널 순회</text><text x="655.0" y="109.5" font-size="11" fill="#4d5656" text-anchor="middle">채널이 IDLE 이면</text><text x="655.0" y="124.5" font-size="11" fill="#4d5656" text-anchor="middle">라운드로빈으로 칩 선택</text><rect x="560" y="170" width="190" height="80" rx="8" fill="#ebf5fb" fill-opacity="1.0" stroke="#2874a6" stroke-width="2"/><text x="655.0" y="200.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">칩 하나에 대해</text><text x="655.0" y="219.5" font-size="11" fill="#4d5656" text-anchor="middle">read → write → erase</text><text x="655.0" y="234.5" font-size="11" fill="#4d5656" text-anchor="middle">순서로 서비스 시도</text><rect x="560" y="280" width="190" height="80" rx="8" fill="#e9f7ef" fill-opacity="1.0" stroke="#1e8449" stroke-width="2"/><text x="655.0" y="310.5" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">PHY 에 전달</text><text x="655.0" y="329.5" font-size="11" fill="#4d5656" text-anchor="middle">Send_command_to_chip()</text><text x="655.0" y="344.5" font-size="11" fill="#4d5656" text-anchor="middle">(NVM_PHY_ONFI_NVDDR2:131)</text><line x1="525" y1="100" x2="560" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#atsu)"/><line x1="655" y1="140" x2="655" y2="170" stroke="#7f8c8d" stroke-width="2" marker-end="url(#atsu)"/><line x1="655" y1="250" x2="655" y2="280" stroke="#7f8c8d" stroke-width="2" marker-end="url(#atsu)"/><rect x="780" y="60" width="185" height="300" rx="8" fill="#ffffff" fill-opacity="1.0" stroke="#566573" stroke-width="2"/><text x="872.5" y="99.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">read 의 우선순위</text><text x="872.5" y="117.5" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="872.5" y="132.0" font-size="10.5" fill="#4d5656" text-anchor="middle">1. 매핑 관련 read</text><text x="872.5" y="146.5" font-size="10.5" fill="#4d5656" text-anchor="middle">   (항상 최우선)</text><text x="872.5" y="161.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="872.5" y="175.5" font-size="10.5" fill="#4d5656" text-anchor="middle">2. GC 가 긴급 모드면</text><text x="872.5" y="190.0" font-size="10.5" fill="#4d5656" text-anchor="middle">   GC read &gt; 사용자 read</text><text x="872.5" y="204.5" font-size="10.5" fill="#4d5656" text-anchor="middle">   아니면 반대</text><text x="872.5" y="219.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="872.5" y="233.5" font-size="10.5" fill="#4d5656" text-anchor="middle">※ 기본 설정은 GC 가 항상</text><text x="872.5" y="248.0" font-size="10.5" fill="#4d5656" text-anchor="middle">   긴급 모드</text><text x="872.5" y="262.5" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="872.5" y="277.0" font-size="10.5" fill="#4d5656" text-anchor="middle">→ 매핑 &gt; GC &gt; 사용자</text><text x="872.5" y="291.5" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="872.5" y="306.0" font-size="10.5" fill="#4d5656" text-anchor="middle">긴급 모드에서 GC write/erase</text><text x="872.5" y="320.5" font-size="10.5" fill="#4d5656" text-anchor="middle">가 대기 중이면 사용자 read</text><text x="872.5" y="335.0" font-size="10.5" fill="#4d5656" text-anchor="middle">는 서비스되지 않는다</text></svg>


<div style="margin-top: 60px;"></div>

## 1. Submit 과 Schedule

AMU 는 transaction 들을 `Submit_transaction()` 으로 모두 넣은 뒤 **한 번만** `Schedule()` 을 부른다. `Prepare_for_transaction_submit()` / `Schedule()` 짝이 `opened_scheduling_reqs` 카운터로 중첩 호출을 하나로 합쳐서, 같은 시점에 들어온 여러 transaction 을 **한꺼번에** 보고 die/plane 수준 병렬 실행을 고를 수 있게 한다 (`TSU_Priority_OutOfOrder.cpp:196`).

`Schedule()` 은 먼저 receive slot 의 transaction 을 **소스 × 종류**별 큐로 분류한다.

| 소스 | 큐 |
|---|---|
| `USERIO` · `CACHE` read / write | `UserRead/WriteTRQueue[채널][칩][우선순위]` |
| `MAPPING` read / write | `MappingRead/WriteTRQueue[채널][칩]` |
| `GC_WL` read / write | `GCRead/WriteTRQueue[채널][칩]` |
| erase (전부 GC_WL) | `GCEraseTRQueue[채널][칩]` |

**사용자 요청 · 매핑 접근 · GC 의 page 이동이 처음부터 서로 다른 큐를 쓴다.** 그래서 우선순위를 정책으로 줄 수 있다.


<div style="margin-top: 60px;"></div>

## 2. 누구를 먼저 서비스하나

채널 하나씩 돌며, 채널이 `IDLE` 이면 라운드로빈 순번의 칩부터 시도한다. 칩 하나에 대해서는 **read → write → erase** 순으로 서비스를 시도하고, 하나라도 성공하면 다음 칩으로 넘어간다 (`process_chip_requests`).

`service_read_transaction()` (`:335`) 의 우선순위는 코드 주석 그대로다.

```cpp
//Flash transactions that are related to FTL mapping data have the highest priority
if (MappingReadTRQueue[ch][chip].size() > 0) { ... }
else if (ftl->GC_and_WL_Unit->GC_is_in_urgent_mode(chip)) {
    // GC 가 긴급 모드면 GC 큐를 사용자 큐보다 먼저
    if (GCReadTRQueue.size() > 0)        { sourceQueue1 = GCRead; sourceQueue2 = user; }
    else if (GCWriteTRQueue.size() > 0)  { return false; }    // GC write 가 밀려 있으면 read 안 함
    else if (GCEraseTRQueue.size() > 0)  { return false; }
    else ...                                                  // 그 외에야 사용자 read
}
```

세 가지를 읽을 수 있다.

1. **매핑 접근이 항상 최우선이다.** CMT miss 로 만든 read 가 사용자 데이터 read 보다 먼저 나간다. 매핑을 모르면 데이터를 못 읽기 때문이다.
2. **GC 가 "긴급 모드" 면 GC 가 사용자보다 앞선다.** 기본 설정(`Preemptible_GC_Enabled` = false)에서는 `GC_is_in_urgent_mode()` 가 항상 true 이므로 실질적으로 **매핑 > GC > 사용자** 순서다.
3. 긴급 모드에서 그 칩에 **GC write 나 erase 가 대기 중이면 사용자 read 는 서비스되지 않는다**(`return false`). GC 가 도는 동안 읽기 지연이 커지는 한 원인이다. 칩이 erase 하는 3.8 ms 동안 read 를 멈추는 **suspend** 가 이를 완화하는 장치다.


<div style="margin-top: 60px;"></div>

## 3. PHY 와 칩 — 시간이 흐르는 곳

```
TSU → NVM_PHY_ONFI_NVDDR2::Send_command_to_chip()      NVM_PHY_ONFI_NVDDR2.cpp:131
        채널을 BUSY 로, 커맨드 전송 시간만큼 이벤트 예약
      → Flash_Chip::start_command_execution()           Flash_Chip.cpp:102
        Get_command_execution_latency() 만큼 후에 완료 이벤트 예약
      ...시간이 흐른다 (read 75µs / program 750µs / erase 3.8ms)...
      → Flash_Chip::finish_command_execution()          Flash_Chip.cpp:130
        broadcast_ready_signal() → PHY::handle_ready_signal_from_chip (:492)
      → broadcastTransactionServicedSignal()            "트랜잭션 완료"
```

- 같은 채널의 칩들은 **버스를 나눠 쓰므로** 명령 전송 중에는 다른 칩이 명령을 받지 못한다. 채널이 BUSY 로 표시되는 이유다.
- erase 도중 read 가 오면(`CMD_Suspension_Support`) `Send_command_to_chip` 의 `SuspendRequired` 경로에서 `Suspend()` 로 erase 를 일시 중단하도록 되어 있다. 단 **원본 `51f0f2d` 의 `TSU_Priority_OutOfOrder` 에서는 이 경로에 닿지 못한다** — `switch` 가 `suspensionRequired = true` 뒤에서 `break` 없이 `default: return false` 로 떨어지기 때문이다([서스펜드 깊이 보기](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/flash-chip-and-phy/)).

### 완료는 위로 올라간다

"트랜잭션 완료" 신호는 3단계에서 연결한 대로 **네 곳이 동시에 받는다.**

| 받는 곳 | 하는 일 |
|---|---|
| `Address_Mapping_Unit` | 매핑 read 면 CMT 에 항목을 채우고 기다리던 transaction 을 재개 |
| `GC_and_WL_Unit` | block 의 진행 중 read/program 카운트를 줄이고, GC 의 다음 단계(이동한 page 쓰기, erase)를 진행 |
| `Data_Cache_Manager` | 사용자 요청의 모든 조각이 끝났는지 확인하고 요청을 완료로 올림 |
| `TSU` | 칩/채널이 비었으니 다음 transaction 을 서비스 |


<div style="margin-top: 60px;"></div>

## 정리 — FTL 이 만든 transaction 이 칩 명령이 되기까지

```
AMU: 물리 주소 확정 → TSU->Submit_transaction → TSU->Schedule
TSU: 소스×종류 큐 분류 → 채널 라운드로빈 → 칩별 read>write>erase → PHY
PHY: Send_command_to_chip → 채널 BUSY → Flash_Chip 지연 → 완료 신호
신호: AMU · GC/WL · 캐시 · TSU 가 각자 후속 처리
```

## 확인해 보기

1. 사용자 write 와 GC write 가 같은 칩에 동시에 대기하면 누가 먼저인가? (`service_write_transaction`, `:471`)
2. `Preemptible_GC_Enabled` 를 true 로 바꾸면 어느 분기가 달라지나? `GC_Hard_Threshold` 는 언제 읽히나? (`GC_and_WL_Unit_Page_Level.cpp:24`)
3. 채널 하나에 칩이 4개일 때 명령 전송 시간 동안 다른 칩은 무엇을 하나?

> 풀이는 [부록 D. 확인해 보기 — 풀이](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/appendix-answers/) 에 있다. 먼저 코드에서 직접 찾아 보자.


<div style="margin-top: 60px;"></div>

<div class="step-nav"><span>[◂ 7. FTL ② 쓰기와 page 할당](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step7-write-alloc/)</span><span>[9. FTL ④ 가비지 컬렉션 ▸](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/step9-gc/)</span></div>
