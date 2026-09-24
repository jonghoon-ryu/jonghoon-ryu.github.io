---
layout: default
title: 정적 마모 평준화 대상 선정 버그와 조용히 멈추던 버그들
permalink: /ftl-visual-simulator/reference/bug-list/wl-target-and-stall-bugs/
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
svg .box { fill: #f5f5f5; stroke: #999; stroke-width: 1; }
svg .box.self { fill: #fff4e5; stroke: #d9a441; }
svg .title { font-size: 12px; font-weight: bold; fill: #333; }
svg .sub { font-size: 10.5px; fill: #555; }
svg .flow { stroke: #888; stroke-width: 1.2; fill: none; marker-end: url(#arrow); }
svg .note { font-size: 10px; fill: #888; font-style: italic; }
</style>

# 정적 마모 평준화 대상 선정 버그와 조용히 멈추던 버그들

"마모평준화 시연"의 static WL 임계값을 1보다 높이려는 작업의 두 번째 라운드(2026-09-24). [지난번](/ftl-visual-simulator/reference/bug-list/suspend-resume-deadlock-bug/)에 스케줄러 데드락 4개를 고치고도 threshold 2 이상은 여전히 발동하지 않았고, "약 900만 요청 근처에서 원인 불명으로 멈춘다"는 잔여 문제도 남아 있었다. 이번에 둘 다 끝까지 추적했다:

- **threshold 가 안 올라가던 진짜 이유**는 GC 정책(RGA) 때문이 아니라, static WL 이 **대상 block 을 고르는 방식 자체의 버그**(#18)였다. 통계 집계 버그 2개(#19-20)도 같이 나왔다.
- **조용히 멈추던 문제**는 한 개가 아니라 **4개의 서로 다른 upstream 버그**(#21-24)였고, 하나를 고치면 그 뒤에 숨어 있던 다음 것이 드러나는 사슬 구조였다. 중간에 이 프로젝트 자신의 수정이 만든 회귀도 하나 있었다.

일곱 개 모두 원본 MQSim 에 있던 코드다. 버그 번호는 [버그 목록표](/ftl-visual-simulator/reference/bug-list/table/)와 같다.

<div style="margin-top: 60px;"></div>

## 1. 버그 #18 — static WL 이 평생 한 번밖에 발동하지 못한 이유

`run_static_wearleveling()` 은 "평면에서 erase count 가 가장 낮은 block"을 대상(가장 차가운 데이터가 있는 곳)으로 고른다. upstream 은 이걸 `Get_coldest_block_id()` 하나로 끝냈다 — 평면 전체에서 최소값, 동률이면 가장 작은 index.

문제는 그 "최소" block 이 거의 항상 **한 번도 쓰이지 않는 write frontier** 라는 점이다. 이 프로젝트 규모에서는 매핑 테이블 전체가 CMT(DRAM 캐시)에 들어가서, 매핑 페이지를 쓰는 `Translation_wf` block 은 끝까지 프로그램되지 않고 erase count 0 으로 남는다. 그 block 은 frontier 라서 `is_safe_gc_wl_candidate()` 가 거부하고, upstream 코드는 거부당하면 그냥 조용히 `return` 한다:

```cpp
flash_block_ID_type wl_candidate_block_id = block_manager->Get_coldest_block_id(plane_address);
if (!is_safe_gc_wl_candidate(pbke, wl_candidate_block_id)) {
    return;   // 다음 차가운 block 을 찾아보지도 않음
}
```

그 frontier 의 erase count 는 영원히 0 이니, 한 번 "가장 차가운 block"이 된 순간부터 **남은 시뮬레이션 내내 static WL 은 절대 발동할 수 없다.** 지금까지 "WL 이 딱 한 번만 뜬다"를 "방금 비운 block 이 새 frontier 가 되기 때문"이라고 설명해왔는데, 그 설명은 틀렸다. 또 발동 조건(`check_static_wl_required()`)도 같은 평면 전체 최소값을 써서, 데이터 block 들끼리는 고르게 닳아 있어도 이 ec=0 frontier 때문에 "차이가 임계값을 넘었다"고 판단하기도 했다.

한 가지 잠재 버그도 같은 곳에 있었다: 빈 free-pool block 이 최소값으로 뽑혀 대상이 되면, 옮길 데이터가 없는데도 erase 되고, 완료 시 `Add_erased_block_to_pool()` 이 이미 pool 에 있는 block 을 **두 번** 넣는다.

**수정**: `get_static_wl_erase_info()` 를 새로 만들어, 최소값(=대상)은 "실제로 데이터가 쓰여 있고(`Current_page_write_index > 0`) 안전한 후보인 block" 중에서만 고르고, 최대값은 평면 전체에서 계산한다. 발동 조건과 대상 선정이 같은 함수를 쓰므로 둘이 어긋날 일이 없다. 유닛 테스트 2개 추가(frontier 를 건너뛰고 다음 데이터 block 을 대상으로 삼는지, 빈 block 은 무시하는지).

<div style="margin-top: 60px;"></div>

## 2. 버그 #19, #20 — WL 이 GC 로 집계됨

- **#19**: 대상 block 에 진행 중인 user read/program 이 있어서 잠시 대기(park)했다가 재개된 WL 이 `Total_gc_executions` 로 셌다.
- **#20**: WL 의 페이지 이동이 `Total_page_movements_for_gc` 로 셌다 — 그래서 `Average_Page_Movement_For_WL` 은 항상 0 이었다.

둘 다 GC 와 WL 이 같은 코드 경로를 공유하면서 WL 쪽 분기를 빠뜨린 경우. 수정은 `Is_wl_triggered` 로 나눠 세는 것.

<div style="margin-top: 60px;"></div>

## 3. #18 을 고치자 드러난 것 — 워크로드가 static WL 에 맞지 않았다

#18 을 고치고 기존 워크로드(균일 무작위 한 flow)로 돌려보니, threshold 1 에서 WL 이 **151번**(GC 는 9번) 발동하는 헛돌기가 됐고, threshold 2-5 에서는 0-1번이었다. 균일 무작위 쓰기에서는 동적 WL(가장 덜 닳은 free block 부터 쓰기)만으로 마모가 거의 평평하게 유지돼서, erase count 차이가 1-2 이상 벌어지지 않기 때문이다.

static WL 이 원래 해결하려는 상황은 "한 번 쓰고 다시는 안 건드리는 데이터"가 block 을 붙잡고 있는 경우다. 그래서 프리셋을 두 flow 로 바꿨다: 자기 영역을 순차로 딱 한 번 쓰고 멈추는 cold flow(DRAM 캐시 끔)와, 기존과 같은 무작위 덮어쓰기 hot flow. 자세한 설계는 [마모평준화 시연 연동 작업 기록 9절](/ftl-visual-simulator/plan/wear-leveling-integration/)에 있다. 이 워크로드로 threshold 를 올리며 규모를 키워 돌리자, 이번엔 멈추는 문제들이 줄줄이 나왔다.

<div style="margin-top: 60px;"></div>

## 4. 멈춤의 사슬 — 하나를 고치면 다음 것이 드러난다

<div style="overflow-x:auto;">
<svg viewBox="0 0 760 170" width="100%" style="max-width:760px;" role="img" aria-label="멈춤 버그가 드러난 순서">
  <defs>
    <marker id="arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="7" markerHeight="7" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#888"/>
    </marker>
  </defs>
  <rect class="box" x="5" y="30" width="130" height="70" rx="6"/>
  <text class="title" x="70" y="55" text-anchor="middle">#21</text>
  <text class="sub" x="70" y="73" text-anchor="middle">barrier 해제 완료가</text>
  <text class="sub" x="70" y="87" text-anchor="middle">캐시에 안 전달됨</text>

  <rect class="box self" x="160" y="30" width="130" height="70" rx="6"/>
  <text class="title" x="225" y="55" text-anchor="middle">회귀 (자체)</text>
  <text class="sub" x="225" y="73" text-anchor="middle">block 0 카운터가</text>
  <text class="sub" x="225" y="87" text-anchor="middle">음수로</text>

  <rect class="box" x="315" y="30" width="130" height="70" rx="6"/>
  <text class="title" x="380" y="55" text-anchor="middle">#22</text>
  <text class="sub" x="380" y="73" text-anchor="middle">재개된 GC 가</text>
  <text class="sub" x="380" y="87" text-anchor="middle">erase 를 제출 안 함</text>

  <rect class="box" x="470" y="30" width="130" height="70" rx="6"/>
  <text class="title" x="535" y="55" text-anchor="middle">#23</text>
  <text class="sub" x="535" y="73" text-anchor="middle">대기 write 가</text>
  <text class="sub" x="535" y="87" text-anchor="middle">LPA barrier 무시</text>

  <rect class="box" x="625" y="30" width="130" height="70" rx="6"/>
  <text class="title" x="690" y="55" text-anchor="middle">#24</text>
  <text class="sub" x="690" y="73" text-anchor="middle">GC 재검사할</text>
  <text class="sub" x="690" y="87" text-anchor="middle">계기가 없음</text>

  <path class="flow" d="M135,65 L158,65"/>
  <path class="flow" d="M290,65 L313,65"/>
  <path class="flow" d="M445,65 L468,65"/>
  <path class="flow" d="M600,65 L623,65"/>
  <text class="note" x="380" y="130" text-anchor="middle">화살표 = "앞의 것을 고치자 드러남". 주황색은 이 프로젝트 자신의 수정이 만든 회귀.</text>
  <text class="note" x="380" y="148" text-anchor="middle">#22-24 는 실제 SSD 규모의 block 수에선 거의 드러나지 않는다.</text>
</svg>
</div>

모든 멈춤은 같은 모양이었다: 에러 메시지 없이 이벤트 큐가 비고, 결과에 `total requests generated: N total requests serviced: N-4` 처럼 요청 몇 개가 영원히 미완료로 남는다(4 = 그 flow 의 큐 깊이). 각 단계마다 종료 시점의 상태(평면별 free block 수, 대기 중인 write, block 별 진행 중 read/program 카운터, 잠긴 LPA)를 덤프하는 임시 계측을 엔진 사본에 넣어 원인을 좁혔다.

<div style="margin-top: 60px;"></div>

## 5. 버그 #21 — barrier 에서 풀려난 트랜잭션을 아무도 모름 (~9e9 정지의 정체)

GC/WL 이 어떤 LPA 의 페이지를 옮기는 동안 그 LPA 는 잠기고(barrier), 그 사이 들어온 user read/write 는 `Read/Write_transactions_behind_LPA_barrier` 에 대기한다. 이동이 끝나면 `Remove_barrier_for_accessing_lpa()` 가 이들을 "GC 가 읽은 데이터로 처리됐다"고 보고 완료시키는데, upstream 은 이렇게 했다:

```cpp
handle_transaction_serviced_signal_from_PHY((*write_tr).second);   // AMU 자기 핸들러만 호출
delete (*write_tr).second;
```

그런데 AMU 자신의 핸들러는 매핑 트랜잭션이 아니면 **첫 줄에서 바로 return** 한다. 즉 이 완료는 사실상 아무에게도 전달되지 않고 삭제만 된다. 진짜 flash 완료는 `NVM_PHY_ONFI` 의 broadcast 로 모든 리스너(TSU, data cache manager, AMU, GC/WL unit)에게 전달되는데, 여기선 그걸 건너뛴 것이다.

영향을 받는 건 data cache manager 다. DRAM 에서 flash 로 내려보낸 write-back 이 barrier 뒤에서 이렇게 사라지면 back-pressure 카운터가 줄지 않는다. 누수가 쌓여 `back_pressure_buffer_max_depth`(여기선 8)에 닿는 순간, 이후 모든 write 가 `waiting_user_requests_queue_for_dram_free_slot` 에서 영원히 기다린다. 캐시를 끈 flow 라면 user request 자체가 완료되지 않는다. 지난번 문서의 "900만 요청 근처에서 원인 불명으로 멈춤"이 바로 이것이었다 — 요청 수와만 상관관계가 있었던 건 누수가 쌓이는 속도 때문이다.

**수정**: `NVM_PHY_ONFI` 에 `Signal_transaction_serviced_without_flash_access()` 를 추가해, 풀려난 트랜잭션을 진짜 flash 완료와 **같은 broadcast** 로 알린다(삭제도 broadcast 쪽이 한다). 반복자 무효화를 피하려고 목록에서 먼저 지운 뒤 알린다.

<div style="margin-top: 60px;"></div>

## 6. 회귀 — 그 broadcast 가 block 0 을 음수로 만들었다

#21 을 고치자 16 block 구성에서 새로 멈췄다. 덤프를 보니 block 0 의 `Ongoing_user_program_count` 가 **-5** 였다. 원인은 방금 넣은 broadcast: GC/WL unit 의 완료 핸들러는 user 트랜잭션이 끝날 때마다 `transaction->Address` 의 block 에서 진행 중 카운터를 하나 뺀다. 그런데 barrier 뒤에서 풀려난 트랜잭션은 **주소가 한 번도 정해진 적이 없다** — `Address` 는 기본값(채널 0, 칩 0, … block 0)이고, 애초에 카운터를 올린 적도 없다.

**수정**: GC 핸들러에서 `Physical_address_determined` 가 false 면 block 회계를 건너뛴다. 그런데 이 플래그를 upstream 은 일관되게 세우지 않았다 — `translate_lpa_to_ppa()` 는 세우지만, 카운터를 올리는 다른 4곳(부분 페이지 쓰기의 update read, 매핑 read 2곳, 매핑 write)은 안 세웠다. 이 넷을 그대로 두면 이번엔 정상적인 완료까지 건너뛰어 카운터가 영원히 양수로 남는다(실제로 block 6 의 `uRd=1` 이 안 내려가서 그 block 의 GC 가 영원히 대기하는 걸 봤다). 그래서 넷 다 플래그를 세우도록 같이 고쳤다.

<div style="margin-top: 60px;"></div>

## 7. 버그 #22 — 대기했다 재개된 GC/WL 이 erase 를 제출하지 않음

GC 가 고른 block 에 아직 진행 중인 user read/program 이 있으면, GC 는 barrier 만 걸어두고 대기한다. 그 read/program 이 끝나면 재개해서 페이지 이동 트랜잭션과 erase 트랜잭션을 만든다. 직접 GC 를 시작하는 두 경로(`Check_gc_required()`, `run_static_wearleveling()`)는 끝에서 이렇게 한다:

```cpp
block->Erase_transaction = gc_erase_tr;
tsu->Submit_transaction(gc_erase_tr);
tsu->Schedule();
```

그런데 **재개 경로만** 가운데 줄이 없었다(upstream 원본은 완료 핸들러 안에 인라인으로 있었고, 이 프로젝트가 deferred 이벤트로 옮길 때도 그대로 옮겨왔다). erase 가 TSU 에 들어가지 않으니 block 은 영원히 "GC 중"(`Has_ongoing_gc_wl`) 상태로 남아 평면이 그 block 을 잃는다. 덤프에서는 모든 page 가 invalid 인 block 두 개가 `gcwl=1`, 옮길 페이지 0개인 채로 멈춰 있었고, free block 이 바닥나 write 8개가 평면 대기열에 갇혀 있었다.

**수정**: `tsu->Submit_transaction(gc_wl_erase_tr);` 한 줄.

<div style="margin-top: 60px;"></div>

## 8. 버그 #23 — 평면 대기열에서 풀려난 write 가 LPA barrier 를 무시함

#22 를 고치자 이번엔 멈추는 대신 **크래시**가 났다(4칩, 12 block, seed 를 바꾼 16 block 등 4개 구성):

```
ERROR:Inconsistency found when moving a page for GC/WL!
```

GC/WL 의 이동 read 가 끝났을 때, 그 LPA 의 매핑이 여전히 읽은 페이지를 가리키는지 확인하는 검사다. LPA 34 하나를 추적해보니:

<pre>
t=7039374189  WL 이 block 11 을 잠금 (LPA 34 = block 11, page 0 포함)
t=7039374192  user write 가 LPA 34 에 새 페이지를 할당   ← 잠겨 있는데!
t=7039461787  이동 read 완료: 읽은 PPA=176, 매핑은 이미 PPA=3 → 에러
</pre>

잠긴 LPA 에 3ns 뒤 user write 가 들어간 것이다. user write 를 번역하는 경로는 셋인데, 둘(`Translate_lpa_to_ppa_and_dispatch()`, 매핑 도착 후 `Waiting_unmapped_program_transactions` 해제)은 `is_lpa_locked_for_gc()` 를 먼저 확인하고 잠겨 있으면 barrier 뒤로 보낸다. 나머지 하나 — free page 가 없어 `Write_transactions_for_overfull_planes` 에서 기다리던 write 를 erase 후 풀어주는 경로 — 만 확인 없이 바로 번역했다. #22 이전에는 대기 GC 가 끝나질 않으니 이 타이밍이 생길 수 없었다.

**수정**: 그 경로에도 같은 확인을 넣어, 잠긴 LPA 의 write 는 barrier 뒤로 보낸다.

<div style="margin-top: 60px;"></div>

## 9. 버그 #24 — GC 를 다시 검사할 계기가 없음

마지막은 4칩 16 block 에서만 드러났다. 칩 2 의 평면 하나에 write 32개가 대기 중이고, free block 은 2개, 진행 중인 erase 는 0개. 그런데 청소할 수 있는 block 이 있었다 — 16 page 중 14 page 가 invalid 인 block 이 두 개나.

GC 검사(`Check_gc_required()`)는 write frontier 가 새 block 으로 넘어갈 때나 erase 가 끝날 때만 실행된다. 이 프로젝트의 기본 정책 RGA 는 "다 쓴 안전한 block" 중에서 무작위로 log₂(block 수) 개(16 block 이면 4개)를 뽑아 그중 invalid 가 가장 많은 걸 고르는데, 이 평면에는 후보 8개 중 청소할 게 있는 block 이 2개뿐이었다. 4개를 뽑아 둘 다 빗나갈 확률은 C(6,4)/C(8,4) = 15/70 ≈ **21%**. 빗나가면 invalid page 0개인 block 이 뽑혀 GC 는 아무것도 안 하고 끝난다.

보통은 다음 write 나 다음 erase 가 검사를 다시 부른다. 하지만 그 평면의 **모든 write 가 이미 대기 중이고 진행 중인 erase 도 없으면**, 다시 검사를 부를 사건이 영영 오지 않는다. 게다가 마지막 검사는 대개 첫 write 가 대기열에 들어가기 **전**에(erase 직후, 아직 free page 가 조금 남아 있을 때) 실행된다.

**수정** (선정 정책 자체는 건드리지 않음):
- 평면의 대기열에 첫 write 가 들어가는 순간 GC 검사를 요청(`Request_gc_check()`).
- GC 검사가 아무것도 시작하지 못했는데, 대기 중인 write 가 있고, 진행 중 erase 가 없고, 실제로 청소할 수 있는 block 이 존재하면 1µs 뒤 다시 검사(`gc_retry_needed()`). 청소할 게 정말 없으면 재시도하지 않는다.

> **정정 (같은 날, 후속 스윕에서)**: 처음에는 "그래서 무한 루프가 되지 않는다"고 썼는데 틀렸다. 청소할 block 이 있어도 **선정 정책이 그 block 을 끝내 고르지 못하면**(FIFO 가 그랬다) 1µs 마다 영원히 재시도했다. 이전 엔진이라면 그냥 멈췄을 구성이, 이 수정 때문에 끝나지 않는 시뮬레이션이 된 것 — 이 프로젝트 자신의 회귀. 연속 재시도 횟수에 상한(1000번)을 두고, FIFO 쪽 원인도 고쳤다. [12절](#section-12) 참고.

RGA 를 "빗나가면 greedy 로" 바꾸는 방법도 있었지만, 그러면 이 프로젝트의 RGA 가 원본과 다르게 동작한다. 재시도는 정책은 그대로 두고 "다시 물어볼 기회"만 보장한다.

<div style="margin-top: 60px;"></div>

## 10. 검증

- `test:engine`(골든 3/3), `test:engine:unit`(14/14) — 골든 결과는 수정 전과 완전히 동일.
- 네이티브 CLI 로 "마모평준화 시연" **29가지 구성**을 전부 돌려 모든 요청 완료 확인: threshold 1-10, 칩 1/2/4, block 16-40, GC 임계값 1-95%, seed 3종, Stop_Time 4배(약 670만 요청).

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>구성</th><th>GC</th><th>WL</th><th>WL 당 이동 page</th><th>완료</th></tr>
<tr><td>기본(24 block, threshold 3)</td><td>58</td><td>7</td><td>16</td><td>2,632,578 / 2,632,578</td></tr>
<tr><td>threshold 4</td><td>49</td><td>5</td><td>16</td><td>2,704,826 / 2,704,826</td></tr>
<tr><td>threshold 5, Stop_Time 4배</td><td>126</td><td>11</td><td>14</td><td>6,799,445 / 6,799,445</td></tr>
<tr><td>칩 4, block 16</td><td>252</td><td>72</td><td>15.8</td><td>2,227,434 / 2,227,434</td></tr>
<tr><td>block 16, Stop_Time 4배</td><td>130</td><td>28</td><td>15.4</td><td>6,729,305 / 6,729,305</td></tr>
</table>
</div>

- WASM 재빌드 후 브라우저에서 기본 설정이 네이티브와 **똑같이** GC 58 / WL 7 로 끝나는 것 확인, 콘솔 에러 없음.

<div style="margin-top: 60px;"></div>

## 11. 버그는 아니지만 남은 한계 — block 16개 미만

두 flow 는 각자 data/GC/매핑용 write frontier block 을 따로 가지므로, 한 flow 일 때보다 frontier 로 묶이는 block 이 두 배다. block 이 16개보다 적으면 칩 개수에 따라 시작하자마자 멈추거나(9-11 block), GC 도중 평면의 free block 이 바닥난다(`Requesting a free block from an empty pool!`, 4칩 14 block). 12 block 은 칩 1개에서만 동작했다. 코드 결함이 아니라 구성 자체가 성립하지 않는 경우라, 앱에서 이 프리셋의 block 개수 최솟값을 16으로 올렸다(다른 두 프리셋은 8 그대로).

<div style="margin-top: 60px;"></div>

## 12. 후속 스윕 — 다른 프리셋과 모든 GC 정책까지 {#section-12}

위 검증은 "마모평준화 시연"에 RGA 정책만 썼다. 같은 날 범위를 넓혀, 세 프리셋 모두에서 UI 로 고를 수 있는 모든 파라미터의 극단값(칩 1/4, block 8-64, block 당 page 4/64, OP 0/30%, GC 임계값 양 끝, 순차/무작위)과 GC 정책 6종을 조합한 83가지 구성을 돌렸더니 11개가 실패했다. 실패한 구성은 모두 이전 엔진(`d5c7c94`, 오늘 작업 전)에서도 다시 돌려 비교했다.

<div style="margin-top: 40px;"></div>

### 12.1 회귀 — 9절의 재시도가 끝나지 않음

"마모평준화 시연" + FIFO + 칩 4 + block 16 이 진행률 10% 에서 CPU 100% 로 멈춰 있었다. 이전 엔진에서는 요청 4개를 남기고 그냥 멈추던 구성이다. 9절의 재시도가 "청소할 block 이 있다"는 조건만 보고 계속 재시도했는데, FIFO 는 그 block 을 절대 고르지 못하는 상태였다(12.2). 연속 재시도를 1000번(시뮬레이션 시간 1ms)으로 제한했다 — FIFO 수정을 일부러 되돌린 빌드로 돌려보니, 끝나지 않던 실행이 0.3초 만에 "정지"로 끝나는 걸 확인했다. 정지도 버그지만, 끝나지 않는 것보다는 낫다.

<div style="margin-top: 40px;"></div>

### 12.2 버그 #25 — FIFO 후보 큐에서 block 이 영영 사라짐

FIFO 는 `Block_usage_history` 큐에서 가장 오래된 "다 쓴 안전한 block"을 **꺼내서** victim 으로 돌려준다. 그런데 공통 코드가 바로 뒤에서 "invalid page 가 하나도 없으면 청소할 게 없다"며 `return` 하면, 꺼낸 block 은 **큐에 다시 들어가지 않는다.** 그 block 이 나중에 invalid page 가 생겨 평면의 유일한 회수 대상이 되면, FIFO 는 그걸 영원히 못 본다 — 이게 12.1 의 진짜 원인이자, 이전 엔진이 멈추던 이유.

**수정**: 꺼내기 전에 거절될 조건(invalid page 0개, 12.4 의 이동 공간 부족)을 적격 검사에 포함해서, 거절될 block 은 꺼내지 않고 큐 뒤로 돌려보낸다.

<div style="margin-top: 40px;"></div>

### 12.3 버그 #26 — RANDOM 계열이 검증 안 된 후보를 그대로 사용

RANDOM, RANDOM_P, RANDOM_PP 는 조건에 맞는 block 이 나올 때까지 무작위로 다시 뽑는데, block 수만큼 실패하면 반복을 멈추고 **마지막으로 뽑은 block 을 조건과 상관없이** 쓴다. 그게 현재 write frontier 면 `Inconsistency in the global mapping table when locking an LPA!` 로 종료된다(GC 시연, block 8 + 칩 4). 예전에 GREEDY/FIFO 에서 고쳤던 것과 같은 종류의 결함이 RANDOM 계열에도 남아 있었던 것. 같은 방식으로 최종 후보를 검증하고, 아니면 이번 GC 기회를 건너뛴다.

<div style="margin-top: 40px;"></div>

### 12.4 이 프로젝트의 튜닝이 드러낸 문제 — GC 이동 공간

"마모평준화 시연" + RANDOM_P/RANDOM_PP 는 `Requesting a free block from an empty pool!` 로 종료됐다(이전 엔진에서는 정지). 종료 순간 평면을 보면 GC 3개가 동시에 돌면서 각각 7-15 page 를 옮기는 중이었다.

upstream 은 GC 가 page 를 옮길 공간을 따로 확인하지 않는다. 대신 free block 이 `max_ongoing_gc_reqs_per_plane` 보다 적으면 사용자 쓰기를 막는데, 이 값이 동시 GC 개수의 상한도 겸한다 — GC 하나가 옮기는 양은 최대 block 하나이므로, upstream 의 10 이면 동시 GC 10개의 여유가 보장된다. 이 프로젝트는 [데모 규모에 맞추려고](/ftl-visual-simulator/reference/tweaked-code/) 이 값을 3 으로 낮췄다. 게다가 사용자 쓰기는 free block 이 정확히 3개일 때도 block 을 하나 가져갈 수 있고(남는 건 2개), flow 가 둘이면 GC write frontier 도 둘이다. RGA/GREEDY 는 invalid page 가 많은 victim 을 골라 옮길 양이 적어서 이 한계에 닿지 않지만, 아무 block 이나 고르는 RANDOM_P/RANDOM_PP 는 닿는다.

**수정 (upstream 과 다른 동작)**: GC/WL 을 시작하기 전에, 이미 진행 중인 GC 들이 아직 옮길 page 와 이번 victim 의 valid page 를 free pool 이 다 담을 수 있는지 확인하고(`has_room_to_migrate()`), 모자라면 다음 기회로 미룬다. valid page 가 없는 victim 은 공간을 쓰지 않으므로 항상 허용.

<div style="margin-top: 40px;"></div>

### 12.5 버그가 아닌 것 — "매핑 기본"이 작은 용량에서 멈춤

나머지 3개("매핑 기본" + block 당 page 4, block 8 + page 4, block 8 + OP 0)는 이전 엔진과 결과가 완전히 같았고, 원인도 버그가 아니었다. 종료 시점에 invalid page 가 **하나도 없다** — 이 프리셋은 논리 공간 100% 에 쓰기 때문에, 용량이 작으면 덮어쓰기가 일어나기도 전에 장치가 가득 차서 쓰기가 막힌다. 청소할 게 없으니 GC 도 할 일이 없다. 이건 이미 `DEFAULT_MAPPING_PARAMS` 주석에 "장치가 차면 데모가 거기서 끝난다"고 기록해둔 설계상 한계다. 다만 UI 에서 그 조합을 고를 수 있고 화면에 이유가 안 나오는 건 따로 정할 문제로 남겼다.

<div style="margin-top: 40px;"></div>

### 12.6 최종 검증

- 83가지 + 기존 WL 29가지 = **112가지 구성 중 109개 완료**, 나머지 3개는 12.5 의 용량 한계.
- 세 프리셋 기본값의 결과(매핑 기본 183 요청 / GC 0, GC 시연 GC 31, 마모평준화 시연 GC 58 / WL 7)는 수정 전과 **완전히 동일** — 이동 공간 확인이 영향을 준 건 block 8 + OP 0, 칩 4 + block 16 같은 빡빡한 구성뿐이었다.
- `test:engine` 골든 3/3, `test:engine:unit` 14/14.

<div style="margin-top: 60px;"></div>

## 참고

- [버그 목록표](/ftl-visual-simulator/reference/bug-list/table/)
- [명령 서스펜드가 한 번도 작동한 적이 없던 버그](/ftl-visual-simulator/reference/bug-list/suspend-resume-deadlock-bug/) — 이 작업의 첫 번째 라운드, 그리고 "남은 문제"로 적어뒀던 정지가 #21
- [마모평준화 시연 연동 작업 기록](/ftl-visual-simulator/plan/wear-leveling-integration/) — 9절: threshold 3 달성과 2-flow 워크로드
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — 커밋 `1199ac3`(엔진), `d60b897`(앱), `0d66439`(12절의 후속 수정)
