---
layout: default
title: RGA 후보 선택이 아직 다 안 쓴 block도 포함하던 버그
permalink: /ftl-visual-simulator/reference/bug-list/rga-incomplete-block-bug/
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

# RGA 후보 선택이 아직 다 안 쓴 block도 포함하던 버그

[GC 자기 자신 경쟁 상태 버그](/ftl-visual-simulator/reference/bug-list/gc-self-victim-race-bug/) 조사와 같은 맥락 - "매핑 기본" 프리셋이 GC 임계값과 워크로드를 "GC 시연"과 똑같이 맞춰줘도 GC 가 발동하지 않는 이유를 계속 파고들다가 찾은, RGA 블록 선택 정책 자체의 결함.

<div style="margin-top: 60px;"></div>

## 1. 어쩌다 발견했나

Ryu 가 직접 계산까지 해서 반박했다: "8개 block 중 4개가 이미 다 쓰였고 GC 임계값이 50%면, 그중 하나는 청소 대상으로 뽑혀야 하는 거 아니냐?" - 맞는 말이었다. 실제로 그 블록(garbage 를 가진 block)은 존재했다. 그런데 GC 는 그 블록을 뽑지 않았다.

진단 로그로 확인해보니:

```
RGA found 3 candidates: 4 5 6
picked=4 write_index=0 invalid=0
```

RGA 가 뽑은 후보 3개(block 4, 5, 6)가 전부 **한 번도 쓰인 적 없는 완전히 빈 block**이었다 - 정작 진짜 데이터를 가진 block(0번, invalid page 1개)은 후보에 뽑히지도 못했다.

<div style="margin-top: 60px;"></div>

## 2. 원인 — RGA만 "다 쓴 block인지" 확인을 안 함

`GC_and_WL_Unit_Page_Level.cpp`의 `Check_gc_required()`는 정책마다 다른 방식으로 청소 대상을 고르는데, RGA 바로 아래 있는 `RANDOM_P`/`RANDOM_PP` 는 후보를 뽑는 재시도 조건에 **"이 block 이 이미 다 쓰였는가(Current_page_write_index == pages_no_per_block)"** 를 명시적으로 넣는다:

```cpp
// RANDOM_P - 이미 다 쓴 block 인지 확인함
while ((pbke->Blocks[gc_candidate_block_id].Current_page_write_index < pages_no_per_block
        || !is_safe_gc_wl_candidate(pbke, gc_candidate_block_id))
       && repeat++ < block_no_per_plane) { ... }
```

그런데 **RGA 는 이 확인이 아예 없었다** - `is_safe_gc_wl_candidate()`(프론티어가 아닌지, 진행 중인 작업이 없는지만 확인)만 통과하면 후보 집합에 들어갔다. 문제는 **한 번도 쓰인 적 없는 빈 block 도 이 조건을 그대로 통과**한다는 것 - 프론티어도 아니고, 진행 중인 작업도 없으니까. RGA 자신의 "더 나은 후보로 교체" 로직(아래)은 다 쓴 block 인지 확인하지만, 그건 **이미 뽑힌 후보들 중에서 더 나은 걸 고를 때**뿐이고,애초에 후보 집합에 빈 block 이 섞여 들어가는 건 막지 못했다:

```cpp
// RGA - "더 나은 후보로 교체"할 때만 다 쓴 block 인지 확인 (너무 늦음)
for (auto &block_id : random_set) {
    if (Invalid_page_count[block_id] > Invalid_page_count[gc_candidate_block_id]
        && Current_page_write_index[block_id] == pages_no_per_block) {
        gc_candidate_block_id = block_id;
    }
}
```

세 후보(4, 5, 6)가 전부 빈 block 이면, 셋 다 `Invalid_page_count == 0` 이라 서로 비교해도 아무도 "더 낫지" 않다 - 그래서 처음에 집합에 넣은 순서대로 첫 번째(`random_set.begin()`)가 그대로 최종 선택으로 남는다. 빈 block 을 고른 채로.

<div style="margin-top: 60px;"></div>

## 3. 왜 실제 MQSim 규모에서는 안 보였나

실제 MQSim 이 가정하는 수천 개 block 규모에서, 빈 공간이 정말로 부족해질 정도가 되려면 **거의 모든 block 을 이미 여러 번 순환해서 다 썼어야** 한다 - 그 시점엔 "한 번도 안 쓰인 block"이 사실상 존재하지 않는다. 반면 이 프로젝트의 작은 데모 규모(8~64개 block)에서는, 빈 공간이 임계값 아래로 떨어지는 시점이 **아직 대부분의 block 을 건드리지도 않은 아주 이른 시점**일 수 있다 - 그래서 RGA 의 무작위 표본 3개가 전부 "아직 손도 안 댄 block"일 확률이 실제로 존재한다.

<div style="margin-top: 60px;"></div>

## 4. 수정

RGA 의 후보 수집 조건에 다 쓴 block 인지 확인을 추가 - `RANDOM_P`/`RANDOM_PP` 가 이미 하고 있는 것과 동일하게:

```cpp
while (random_set.size() < rga_set_size && rga_attempts++ < rga_max_attempts) {
    flash_block_ID_type block_id = random_generator.Uniform_uint(0, block_no_per_plane - 1);
    if (pbke->Blocks[block_id].Current_page_write_index == pages_no_per_block   // ← 추가
        && pbke->Ongoing_erase_operations.find(block_id) == pbke->Ongoing_erase_operations.end()
        && is_safe_gc_wl_candidate(pbke, block_id)) {
        random_set.insert(block_id);
    }
}
```

(반복 횟수 상한 자체는 [이전 버그 수정](/ftl-visual-simulator/reference/bug-list/gc-self-victim-race-bug/)에서 이미 추가해둔 것을 그대로 사용 - 다 쓴 block 이 하나도 없으면 그 상한 안에서 자연스럽게 후보 0개로 끝나고, 이번 GC 기회를 건너뛴다.)

<div style="margin-top: 60px;"></div>

## 5. 검증

- **골든 리그레션(3/3), GMock(12/12)** 모두 수정 전과 완전히 동일 - 실제 규모 시나리오에서는 이 조건이 사실상 항상 이미 참이라 관찰 가능한 차이가 없음을 확인.
- **실제 동작 변화 확인**(둘 다 진짜 개선 - 이전엔 낭비되던 GC 기회가 이제 실제로 쓰임):
  - "GC 시연"(block 8개, 기존 기본값): 4회 → 4회, 변화 없음(이 조합에선 애초에 빈 block 을 안 뽑았던 것으로 확인)
  - "GC 시연"(block 16개, [재생 시간 연장 PR](https://github.com/jonghoon-ryu/ftl-visual-simulator-app/pull/30)의 새 기본값): 5회 → **6회**
  - "마모평준화 시연"(block 64개): GC 32회 → **29회**(더 적어졌지만, 이전 32회 중 일부는 사실 빈 block 을 뽑고 아무것도 안 한 "낭비된" 시도였을 가능성 - 정확한 개수 변화보다 "고른 block 이 항상 진짜 청소 대상"이라는 게 중요), WL 1회는 그대로.
- Ryu 가 원래 제기했던 8-block/8-page 극단 케이스는 이 수정 후에도 여전히 0회 - 하지만 원인이 바뀌었다: 이제는 "빈 block 을 잘못 골라서"가 아니라, **유일하게 데이터를 가진 block 이 하필 그 순간 마지막 쓰기 몇 개가 아직 완료 처리되지 않은 상태**라 (진행 중 쓰기 카운트, [자기 자신 경쟁 상태 버그](/ftl-visual-simulator/reference/bug-list/gc-self-victim-race-bug/) 참고) 정당하게 후보에서 제외됐기 때문 - block 이 8개뿐이라 "쓸모있는 block 이 단 하나"인 극단적으로 좁은 상황에서만 남는, 구조적으로 불가피한 한계.

<div style="margin-top: 60px;"></div>

## 6. 요약

- **수정해서 유지한다.** 실제 upstream MQSim 코드의 결함이고, 골든 시나리오 출력에는 영향 없음.
- 이전에 문서화됐던 "마모평준화 시연 GC 32회"는 이제 29회로 바뀜 - [마모평준화 시연 연동 작업 기록](/ftl-visual-simulator/plan/wear-leveling-integration/)의 해당 숫자도 함께 갱신.

<div style="margin-top: 60px;"></div>

## 참고

- [GC 자기 자신 경쟁 상태 버그](/ftl-visual-simulator/reference/bug-list/gc-self-victim-race-bug/) — 같은 조사에서 먼저 발견된, 원인이 얽힌 버그
- [튜닝된 코드](/ftl-visual-simulator/reference/tweaked-code/) — 이 모든 조사의 출발점
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — 실제 코드
