---
layout: default
title: GC 자기 자신 경쟁 상태 버그 — 진행 중 쓰기 카운트 누락과 후속 무한 루프
permalink: /ftl-visual-simulator/reference/bug-list/gc-self-victim-race-bug/
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

# GC 자기 자신 경쟁 상태 버그 — 진행 중 쓰기 카운트 누락과 후속 무한 루프

멀티 칩 UI 를 리뷰하던 중 우연히, "GC 시연" 프리셋을 기본값 그대로 처음부터 끝까지 돌려보면 GC 실행 횟수가 0으로 멈춰 있다는 걸 발견했다([튜닝된 코드](/ftl-visual-simulator/reference/tweaked-code/) 문서의 계기가 된 그 조사). 그런데 그 조사를 계속 파고들다 보니, 애초에 GC 임계값 튜닝 문제가 아니라 **원본 MQSim 자체의 진짜 버그** — 그것도 서로 원인이 얽힌 두 개 — 를 밟고 있었다는 걸 알게 됐다. 이 문서는 그 둘을 함께 기록한다.

<div style="margin-top: 60px;"></div>

## 1. 어쩌다 발견했나

블록 개수를 이리저리 바꿔가며 재현 범위를 좁히던 중, 특정 조합(작은 블록 수 + 오래 걸리는 워크로드)에서 다음 에러로 프로세스가 그냥 죽는 걸 발견했다:

```
ERROR:Inconsistency in the global mapping table when locking an LPA!
```

이건 `Address_Mapping_Unit_Page_Level::Set_barrier_for_accessing_physical_block()`가 GC 가 block 을 청소 대상으로 잠그기 직전에 하는 자체 정합성 검사다 — block 안의 "유효(valid)"하다고 표시된 모든 page 를 순회하면서, 그 page 의 실제 metadata(LPA)가 매핑 테이블이 기억하는 값과 정말 일치하는지 재확인한다. 불일치하면 그냥 계속 진행하지 않고 그 자리에서 `exit(1)` — MQSim 자체의 assert 에 가깝다.

<div style="margin-top: 60px;"></div>

## 2. 원인 확정 — 진단 로그로 역추적

임시로 진단 로그를 여러 겹 심어서(최종 코드에는 없음) 정확히 무슨 일이 있었는지 재구성했다:

```
DIAG allocate-gc-write block2 page=0..14  (전부 GC 마이그레이션으로 정상 기록)
DIAG lock-block2 write_index=16 ... p14=I p15=V   ← page 15 는 "유효"로 표시돼 있는데
DIAG lpa=18446744073709551615(=NO_LPA) ...        ← page 15 의 실제 metadata 는 비어있음
```

`page=15`의 **할당(allocate)** 과 위 크래시가 **정확히 같은 시각**에 일어났다. 즉:

1. GC 마이그레이션 쓰기가 block 2 의 마지막 page(15번)를 채운다 — `Current_page_write_index`가 16(=꽉 참)이 된다.
2. `Allocate_block_and_page_in_plane_for_gc_write()`가 이 즉시(같은 함수 안에서, 동기적으로) block 2 를 GC 의 새 쓰기 목적지(`GC_wf`)에서 내리고 **다음 block 으로 교체**한다.
3. 바로 이어서, 같은 함수가 (block 2 가 꽉 찼으니) `Check_gc_required()`를 호출한다 — 그런데 이 시점엔 이미 2번에서 `GC_wf`가 다음 block 으로 바뀐 뒤라, block 2 는 더 이상 "현재 쓰기 프론티어"로 보이지 않는다.
4. `is_safe_gc_wl_candidate()`의 첫 번째 체크("현재 프론티어면 제외")는 그래서 block 2 를 걸러내지 못한다. 원래 이런 상황을 막기 위한 **두 번째 체크**("진행 중인 program 요청이 있으면 제외", `Ongoing_user_program_count`)가 있는데 — 확인해보니 `Allocate_block_and_page_in_plane_for_gc_write()`는 일반 사용자 쓰기용 쌍둥이 함수(`..._for_user_write()`)와 번역 페이지용 함수(`..._for_translation_write()`)가 둘 다 하는 `program_transaction_issued()` 호출을 **아예 하지 않는다.**
5. 그 결과 GC 는 방금 자기가 채운, **아직 물리적으로 flash 에 실제로 쓰이지도 않은** page 15 를 가진 block 2 를, 청소 대상 후보로 다시 골라버린다. `Set_barrier_for_accessing_physical_block()`가 page 15 를 검사하면 — "유효"하다고는 하는데 아직 진짜로 쓰인 적이 없으니 metadata 가 `NO_LPA`, 매핑 테이블과 당연히 안 맞고, 크래시.

<div style="margin-top: 60px;"></div>

## 3. 왜 지금까지 아무도 못 봤나 — 로직 버그가 아니라 확률 문제

이 버그는 "항상 틀린" 로직 버그가 아니라 **특정 우연이 겹쳐야만** 터지는 타이밍 문제다. GC 가 청소 대상을 고를 때는 plane 안의 block 중에서 **무작위로** 하나를 뽑는다. 이 버그가 터지려면:

1. 그 무작위 뽑기가 하필 **"방금 막 다 찬 block"** 을 골라야 하고,
2. 그것도 **그 block 의 마지막 page 물리적 쓰기가 아직 안 끝난, 아주 짧은 순간**에 뽑혀야 한다.

실제 MQSim 이 가정하는 수천 개 block 규모에서는 1번 자체의 확률이 이미 "수천 개 중 하나"다 — 게다가 그 대상이 되는 순간(2번)은 시뮬레이션 시간으로 봐도 아주 찰나라, 두 조건이 겹칠 확률은 사실상 0에 가깝다. 2018년부터 여러 연구에서 이 코드를 썼지만 아무도 이 경쟁을 밟지 않은 이유다.

이 프로젝트는 화면 하나에 flash 배열 전체가 다 보이게 하려고 block 수를 최소 7~8개까지 줄인다. block 이 7~8개뿐이면 1번의 확률은 "8개 중 하나"로 확 뛰어오르고, GC 가 수십 번 반복되는 동안 결국 한 번쯤은 걸리게 된다 — 로직은 그대로인데, **이 프로젝트가 확률을 실제로 일어날 만한 수준까지 끌어올린 것**이다.

<div style="margin-top: 60px;"></div>

## 4. 수정 (1) — 누락된 진행-중-쓰기 카운트

`Allocate_block_and_page_in_plane_for_gc_write()`(`Flash_Block_Manager.cpp`)에 쌍둥이 함수들과 똑같이 `program_transaction_issued()` 호출을 추가했다. 그리고 짝이 맞는 반대쪽 — GC 마이그레이션 쓰기가 실제로 완료됐을 때 카운트를 다시 내리는 `Program_transaction_serviced()` 호출 — 도 `GC_and_WL_Unit_Base.cpp`의 GC 전용 WRITE 완료 처리 쪽에 추가했다(원래 USERIO/MAPPING/CACHE 출처의 쓰기에만 있었다). 둘 다 없으면 카운트가 죽 쌓이기만 해서 그 block 이 영원히 GC 후보에서 제외돼버리므로, 반드시 짝으로 넣어야 했다.

<div style="margin-top: 60px;"></div>

## 5. 수정 (2) — 이 수정이 드러낸 두 번째 버그: RGA 후보 탐색의 무한 루프

수정 (1)만 넣고 다시 돌려보니, 이번엔 크래시 대신 **완전히 멈춰버리는(hang)** 사례가 나왔다 — 게다가 이건 극단적인 조건이 아니라, 이미 배포된 멀티 칩(칩 2개/4개) + block 8개 조합에서 실제로 재현됐다.

이 프로젝트가 쓰는 GC 블록 선택 정책(RGA)은 청소 대상을 딱 하나만 무작위로 뽑지 않는다 — 먼저 **서로 다른 안전한 후보를 여러 개(`rga_set_size`개) 모은 다음**, 그중 무효 page 가 가장 많은 걸 골라서 청소 효율을 높인다. 문제는 그 "서로 다른 안전한 후보를 모으는" 루프에 **애초에 반복 횟수 제한이 없었다**는 것:

```cpp
// 수정 전
std::set<flash_block_ID_type> random_set;
while (random_set.size() < rga_set_size) {   // 못 채우면 영원히 반복
    ...
}
```

바로 아래 있는 다른 정책들(RANDOM, RANDOM_P, RANDOM_PP)은 전부 `repeat++ < block_no_per_plane` 식으로 시도 횟수에 상한을 두는데, RGA 만 그게 없었다. 수정 (1)로 `is_safe_gc_wl_candidate()`의 체크가 더 정확해지면서 "안전한" block 후보가 더 줄어들었고, block 수가 워낙 적은(8개) 상태에서 칩까지 나뉘면 특정 순간에 `rga_set_size`(=log2(block 수)) 개수만큼의 서로 다른 안전한 후보가 아예 존재하지 않는 경우가 실제로 생겼다 — 그러면 이 루프는 존재하지도 않는 후보를 영원히 찾아 헤맨다.

```cpp
// 수정 후 - 시도 횟수 상한(block_no_per_plane²) + 못 채워도 있는 만큼 진행,
// 하나도 못 찾으면 이번 GC 기회는 그냥 건너뜀(다음 호출 때 재시도)
unsigned int rga_attempts = 0;
const unsigned int rga_max_attempts = block_no_per_plane * block_no_per_plane;
while (random_set.size() < rga_set_size && rga_attempts++ < rga_max_attempts) { ... }
if (random_set.empty()) {
    return;
}
```

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th></th><th>버그 (1) 진행-중-쓰기 카운트 누락</th><th>버그 (2) RGA 무한 루프</th></tr>
<tr><td>증상</td><td>크래시(exit 1) — 에러 메시지라도 남음</td><td>완전 멈춤(hang) — 에러 메시지 없이 탭이 그냥 응답 없음</td></tr>
<tr><td>네이티브 CLI로도 재현되는가</td><td>예(WASM 하네스로 확인, native 로직 자체의 문제)</td><td>예(같은 이유)</td></tr>
<tr><td>실제 배포 환경에서 재현 가능했나</td><td>아니오 — UI 에 없는 Stop_Time 을 인위적으로 늘려야 재현</td><td><b>예 — 이미 배포된 칩 2/4개 + block 8개 조합에서 바로 재현</b></td></tr>
<tr><td>발견 계기</td><td>"GC 시연" GC 실행 횟수 0 조사</td><td>버그 (1)을 고치자 바로 드러남</td></tr>
</table>
</div>

버그 (2)가 실제 배포본에서 바로 재현된다는 걸 확인한 뒤로는, 버그 (1)만 고치고 버그 (2)를 그대로 두는 건 고려하지 않았다 — 크래시(눈에 보이는 에러)를 무한 멈춤(아무 설명 없는 프리징)으로 바꾸는 것뿐이라 오히려 더 나쁜 상태였을 것이다. 둘을 같은 커밋에 묶어서 수정했다.

<div style="margin-top: 60px;"></div>

## 6. 검증

- **칩 개수 × block 개수 전수 조사**: "GC 시연"/"마모평준화 시연" 두 프리셋 모두, 칩 개수(1/2/4/8) × block 개수(8/16/32/64) 16가지 조합 전부 각자의 실제 배포 Stop_Time 으로 완주 확인(크래시도 멈춤도 없음, 서브프로세스 타임아웃으로 감시).
- 이전에 멈추던 정확한 조합(칩 2개/4개 + block 8개)에서 실제로 GC 가 발동하는 것까지 확인(칩 2개: 5회, 칩 4개: 16회).
- `npm run test:engine`(골든 리그레션 3/3), `test:engine:unit`(GMock 12/12) 모두 수정 전과 완전히 동일 — 골든 시나리오는 규모가 훨씬 커서 이 경쟁 조건 근처에도 가지 않고, GMock 테스트들은 이 두 함수를 자기 값으로 직접 구성해서 쓰므로 무관.
- 브라우저에서 직접 재현·확인: 칩 개수 2, Block 개수 8로 "GC 시연"을 재생하면 더 이상 멈추지 않고 GC 실행 횟수 5, Erase 횟수 5, 이벤트 로그에 "Block 3 소거 완료 (GC)"까지 정상 표시.

<div style="margin-top: 60px;"></div>

## 7. 요약

- **수정해서 유지한다.** 둘 다 실제 upstream MQSim 코드 자체의 결함이고, 고쳐도 골든 시나리오 출력에는 전혀 영향이 없다.
- 버그 (2)는 이미 배포된 조합에서 재현 가능했던, 우선순위가 높은 라이브 이슈였다 — 발견 즉시 같은 커밋으로 함께 수정.

<div style="margin-top: 60px;"></div>

## 참고

- [튜닝된 코드](/ftl-visual-simulator/reference/tweaked-code/) — 이 조사의 출발점이 된 "GC 시연 GC 실행 횟수 0" 문제
- [재구성 크래시 버그](/ftl-visual-simulator/reference/bug-list/reconfigure-crash-bug/) — 비슷하게 "원본 CLI는 절대 안 만드는 사용 패턴"에서만 드러난 다른 메모리/카운트 버그
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — 실제 코드
