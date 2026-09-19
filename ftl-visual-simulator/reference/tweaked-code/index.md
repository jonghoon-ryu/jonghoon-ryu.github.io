---
layout: default
title: 튜닝된 코드 (Tweaked Code)
permalink: /ftl-visual-simulator/reference/tweaked-code/
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

# 튜닝된 코드 (Tweaked Code)

[버그 목록](/ftl-visual-simulator/reference/bug-list/)이 MQSim 원본 자체의 결함(고쳐도 upstream 이 의도한 동작과 같아지는 것들)을 모아두는 곳이라면, 이 문서는 **결함이 아닌데도 일부러 upstream 과 다르게 동작하도록 바꾼 곳**을 모아두는 곳이다. 원본 코드 자체가 잘못됐던 게 아니라, 원본이 가정하는 규모(수천 개 block 짜리 데이터센터급 SSD)와 이 프로젝트가 화면에 보여줘야 하는 규모(한 화면에 다 보여야 하는 수십 개 block, 게다가 이제는 칩까지 여러 개)가 달라서 생기는 충돌을 해결하기 위한 항목들이다.

**여기 안 들어가는 것**: `ssdconfig.xml`/`SsdParams` 같은 원본이 원래부터 설정 가능하게 열어둔 값(`GC_Exec_Threshold`, `Block_No_Per_Plane` 등)을 특정 값으로 고른 것은 튜닝이 아니라 그냥 "설정"이다 — 프리셋마다 다른 값을 쓰는 건 이 문서의 대상이 아니다. 이 문서는 **원본 C++ 코드 자체에 손을 댄** 경우만 다룬다.

<div style="margin-top: 60px;"></div>

## 전체 목록

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr>
  <th>#</th>
  <th>튜닝</th>
  <th>위치</th>
  <th>원본 값 → 바꾼 값</th>
  <th>계기</th>
</tr>
<tr>
  <td>1</td>
  <td><code>max_ongoing_gc_reqs_per_plane</code></td>
  <td><code>exec/SSD_Device.cpp</code>(<code>GC_and_WL_Unit_Page_Level</code> 생성자 호출)</td>
  <td>10 → 4</td>
  <td>"GC 시연" 프리셋 데드락 조사 중 발견</td>
</tr>
</table>
</div>

지금까지는 이 항목 하나뿐이다.

<div style="margin-top: 60px;"></div>

## #1. `max_ongoing_gc_reqs_per_plane`: 10 → 4

### 이 상수가 하는 일

MQSim 원본은 이 값을 두 가지 용도로 쓴다(`GC_and_WL_Unit_Base.h`의 필드 주석 참고):

1. plane 하나당 동시에 진행 가능한 GC 작업 개수의 최댓값
2. **빈 block 이 이 값 밑으로 떨어지면 그 즉시 모든 신규 write 를 강제로 막는** 안전장치 (`Stop_servicing_writes()`)

원본 MQSim 은 이 값을 `ssdconfig.xml` 로 설정할 수 있게 열어두지 않고, `SSD_Device.cpp`가 `GC_and_WL_Unit_Page_Level`를 생성할 때 코드에 **리터럴 `10`을 그대로 박아서** 넘긴다.

### 왜 문제였나

GC 자신의 발동 기준(`GC_and_WL_Unit_Base.cpp`)도 이 값과 얽혀 있다:

```
block_pool_gc_threshold = floor(GC_Exec_Threshold × Block_No_Per_Plane)
// 단, 이 값이 max_ongoing_gc_reqs_per_plane 보다 작으면 그 값으로 올림
if (block_pool_gc_threshold < max_ongoing_gc_reqs_per_plane)
    block_pool_gc_threshold = max_ongoing_gc_reqs_per_plane;
```

원본이 가정하는 수천 개 block 규모에서는 이 clamp(끌어올림)가 사실상 절대 발동하지 않는다. 그런데 "GC 시연" 프리셋의 규모(block 16개, `GC_Exec_Threshold` 50%)에서는 `floor(0.5 × 16) = 8`이 나와서, 이 clamp 때문에 GC 의 발동 기준도 그대로 `10`으로 끌어올려진다 — **"GC 시작" 기준과 "write 전면 차단" 기준이 정확히 같은 지점에서 동시에 발동**하게 된 것이다.

이렇게 되면: 빈 block 이 처음으로 10 밑으로 떨어지는 순간, GC 는 청소할 만한(무효 페이지가 있는) block 을 찾아보지만 — 아직 이른 시점이라 그런 block 이 하나도 없을 수 있다 — 아무것도 못 찾고 그냥 넘어간다. 그런데 바로 그 순간 write 도 전면 차단됐다. write 가 막히면 그 무엇도 다시는 무효화(overwrite)될 일이 없으므로, GC 가 청소할 거리는 **영원히** 생기지 않는다. 실제로 "GC 시연" 프리셋을 처음부터 끝까지 돌려보면 GC 실행 횟수가 0 인 채로 멈춰 있었다 — 성능이 느린 게 아니라 진짜로 멈춰버린 상태였다(시뮬레이션 내부 시각을 확인해보면 `Stop_Time` 을 아무리 늘려도 항상 똑같은 시점에서 멈춘다).

### 왜 block 개수를 늘리는 대신 이 상수를 낮췄나

데드락을 피하는 또 다른 방법은 block 개수를 늘려서(예: 32개) `floor(0.5×32)=16`이 10 을 자연스럽게 넘어서게 만드는 것이다. 실제로 이 방법도 테스트해서 확인은 했다. 하지만 이 프로젝트는 이제 멀티 칩(칩 개수 × block 개수)까지 한 화면에 grid 로 보여줘야 해서, block 개수를 늘리는 건 화면 공간과 직접 충돌한다.

반대로 `max_ongoing_gc_reqs_per_plane` 자체를 낮추면, 화면에 보이는 block 개수는 그대로 두고도 clamp 가 걸리는 지점만 낮아진다 — 16개짜리 규모에서도 GC 기준(8)이 write 차단 기준(4) 보다 이미 높아서, 둘이 겹치지 않는다. `0`이 아니라 `4`를 고른 이유는 이 상수의 "동시 GC 작업 개수 제한"이라는 원래 역할도 완전히 무의미해지지 않게(0 이면 GC 가 동시에 아무 작업도 못 하게 됨) 여유를 조금 남겨두기 위해서다.

### 검증

- `npm run test:engine`(골든 리그레션, 실제 규모 샘플 시나리오 3개): 변경 전후 결과 동일 — 애초에 이 시나리오들은 block 수가 훨씬 커서 4든 10이든 이 clamp 근처에도 안 간다.
- `npm run test:engine:unit`(GMock, 12개): 전부 통과 — `GcTriggerTest` 등은 `max_ongoing_gc_reqs_per_plane`을 이 상수 값에 의존하지 않고 테스트 안에서 직접 원하는 값(10, 2 등)으로 생성해서 쓰기 때문에 이 변경과 무관하다.
- WASM 하네스로 직접 재확인: block 개수/`GC_Exec_Threshold`를 "GC 시연" 프리셋 그대로 두고 재생만 해봐도(block 16개, `Stop_Time` 만 조금 늘려서) 더 이상 멈추지 않고 GC 가 실제로 여러 번 발동한다.

이 변경만으로는 "GC 시연" 프리셋의 데드락은 해결되지만, 여전히 기존 `Stop_Time` 안에서는 GC 가 발동하기엔 시간이 부족하다 — 이건 원본 코드 튜닝이 아니라 이 프로젝트 자체 프리셋 설정(`Stop_Time`, 재생 속도 배율)의 문제라 이 문서 대신 [개발 계획](/ftl-visual-simulator/plan/)에서 다룬다.

같은 "GC 실행 횟수 0" 조사를 더 파고들다가, 애초에 이건 튜닝 문제가 아니라 **원본 MQSim 자체의 진짜 버그**(그것도 서로 얽힌 두 개)를 밟고 있었다는 걸 알게 됐다 - 자세한 내용은 [GC 자기 자신 경쟁 상태 버그](/ftl-visual-simulator/reference/bug-list/gc-self-victim-race-bug/) 참고.

<div style="margin-top: 60px;"></div>

## 참고

- [참고 자료](/ftl-visual-simulator/reference/)
- [버그 목록](/ftl-visual-simulator/reference/bug-list/) — 결함(고치면 upstream 과 같아지는 것들)을 모아두는 자매 문서
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app)
