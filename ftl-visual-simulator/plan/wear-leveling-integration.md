---
layout: default
title: 마모평준화 시연 연동 작업 기록
permalink: /ftl-visual-simulator/plan/wear-leveling-integration/
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

# 마모평준화 시연 연동 작업 기록

Session 12(1차 완성)까지는 "마모평준화 시연" 프리셋이 정적 목업으로 남아있었다 — [Session 6 조사](/ftl-visual-simulator/reference/bug-list/wl-bug-deviation/)에서 로직 버그 2개를 고쳤음에도 static 마모 평준화(WL)가 데모 규모에서 한 번도 실제로 발동하지 않았기 때문에, 확인 안 된 상태로 UI 에 연결하지 않기로 했었다. 이 문서는 1차 완성 이후 이 프리셋을 실제로 연동한 작업 전체를 기록한다 — [정적 마모 평준화 설정 누락 버그](/ftl-visual-simulator/reference/bug-list/wl-threshold-not-wired-bug/) 문서가 버그 자체의 근본 원인 분석에 집중한다면, 이 문서는 **왜 그 버그를 찾게 됐는지, 어떤 시도들을 거쳤는지, 최종적으로 어떻게 튜닝했는지** 작업 과정 전체를 다룬다.

<div style="margin-top: 60px;"></div>

## 1. 시작점 — GC 시연과 같은 방식이 통할 거라는 가정

"GC 시연" 프리셋은 `GC_Exec_Threshold`를 0.05 → 0.5 로 높여서 데모 규모에서도 GC 가 실제로 발동하도록 튜닝했었다(자세한 내용은 `mqsimConfigs.ts`의 `buildGcWorkloadXml` 주석 참고). 같은 방식이 통할 거라 가정하고 시작했다:

1. 작은 지오메트리 + 높은 `GC_Exec_Threshold`로 GC/erase 사이클을 계속 강제 발생시켜서 block 들의 erase count 를 서서히 갈라놓는다.
2. `Static_Wearleveling_Threshold`(기본 100)를 데모 규모에서 도달 가능한 낮은 값으로 낮춘다.

<div style="margin-top: 60px;"></div>

## 2. 네이티브 하니스로 검증 — 첫 번째 막힘

`engine/mqsim/src`를 라이브러리로 직접 호출하는 작은 C++ 하니스를 만들어(`Load_workload` → `Initialize_scenario` → `Run_step` 반복, `Get_block_state_snapshot()`으로 주기적으로 erase count 를 찍어봄) 여러 지오메트리를 실험했다:

- **Block 16개**(다른 프리셋들의 기본값): 워크로드가 자연스럽게 멈춰버림(free block pool 이 hard-block 임계값에 걸리는 것과 같은 계열의 문제) — 오래 실행할 수가 없어서 erase count 차이가 거의 안 벌어짐.
- **Block 64개**: 1700만 step 넘게 안정적으로 실행됨. `Get_min_max_erase_difference()`가 계산하는 min/max 차이가 0 → 7까지 꾸준히 벌어졌다.

그런데 **`Static_Wearleveling_Threshold` 를 5, 심지어 1로 낮춰도 `Total_WL_Executions` 는 계속 0**이었다. 분명히 조건(`diff >= threshold`)이 여러 번 충족됐을 텐데도 실행 횟수가 안 올라간다는 건, 조건 계산이 아니라 그 값 자체가 반영이 안 되고 있다는 뜻이었다.

<div style="margin-top: 60px;"></div>

## 3. 근본 원인 — 설정값이 엔진까지 전달되지 않고 있었다

`check_static_wl_required()` 안에 디버그 프린트를 심어서 실제로 비교되는 threshold 값을 직접 찍어보니 **항상 100**이었다 — XML 에 뭘 넣든 무시되고 있었다. `SSD_Device.cpp`가 `GC_and_WL_Unit_Page_Level`을 생성할 때 `Dynamic_Wearleveling_Enabled`/`Static_Wearleveling_Enabled`/`Static_Wearleveling_Threshold` 세 인자를 통째로 생략해서, 항상 컴파일 타임 기본값(`true, true, 100`)을 쓰고 있었던 것 — 근본 원인과 수정 내용의 전체 분석은 [정적 마모 평준화 설정 누락 버그](/ftl-visual-simulator/reference/bug-list/wl-threshold-not-wired-bug/) 문서 참고.

<div style="margin-top: 60px;"></div>

## 4. 버그 수정 후 재검증 — 실제로 발동시키다

`SSD_Device.cpp`를 고친 뒤 같은 하니스로 재실행:

```
step=1500000 minErase=0 maxErase=1 diff=1 GC=7 WL=1 blocks=64
```

**`Total_WL_Executions` 가 처음으로 1이 됐다.** 이후 1500만 step 을 더 돌려도(diff 는 7까지 계속 벌어졌음에도) 다시 발동하지 않는다는 것도 확인했다 — 이유는 WL 이 비운 block 이 dynamic 마모 평준화에 의해 곧바로 새 write frontier 로 재배정되고, frontier 는 `is_safe_gc_wl_candidate()`가 명시적으로 제외하기 때문이다(같은 계열의 재발동을 다시 만들려면 그 새 frontier 가 다 채워질 때까지 처음과 비슷한 시간이 또 필요함).

이 결과를 바탕으로 **"재생 1회당 정확히 1번 발동"을 이 데모의 정직한 목표**로 잡았다 — 여러 번 반복 발동을 억지로 만들어내려 하지 않기로 했다(그러려면 실행 시간이 지금보다 훨씬 길어져야 하는데, 다른 두 프리셋과의 데모 경험 일관성이 깨짐).

<div style="margin-top: 60px;"></div>

## 5. 최종 데모 설정

`src/data/mqsimConfigs.ts`:

- **`DEFAULT_WL_PARAMS`** — 다른 두 프리셋의 `DEFAULT_MAPPING_PARAMS`를 베이스로, `blockNoPerPlane: 64`(다른 프리셋의 16보다 훨씬 큼 - 2절의 실험 결과), `gcExecThreshold: 0.5`("GC 시연"과 동일한 GC 강제 발생 튜닝), `staticWlThreshold: 1`(새로 추가한 필드 - `SsdParams`에 `staticWlThreshold` 필드 자체를 새로 추가하고 `buildSsdConfigXml`이 이를 XML 로 내보내도록 확장).
- **`buildWlWorkloadXml()`** — "GC 시연"과 같은 워크로드 형태(`Working_Set_Percentage: 25`)에 `Stop_Time: 8000000000`(GC 시연의 2500000000 보다 김 - WL 발동에 필요한 event-group 수가 더 많기 때문). 네이티브 하니스로 측정한 최종 실행 규모: **약 279만 event-group, GC 32회, WL 1회, erase 33회** — 자연 종료(이벤트 큐 고갈이 아니라 Stop_Time 도달로 정상 종료됨을 확인).
- `App.tsx`의 `TICKS_MULTIPLIER`에 `'wear-leveling': 15000` 추가 — "GC 시연"의 5000 대비 279만/95만 ≈ 3배 규모이므로 그만큼 배속.

`src/lib/mqsimWear.ts`(신규): 엔진의 실제 블록별 erase count 스냅샷(`getState().blocks[].eraseCount`)을 `WearLevelingView`가 그리는 `WearRow[]`로 변환. 기존 정적 목업은 `maxEraseCount: 120`(upstream 의 현실적인 `Block_PE_Cycles_Limit` 대비 스케일)을 고정값으로 썼지만, 이 데모 규모에서는 실제 erase count 가 한 자릿수뿐이라 고정 스케일을 그대로 쓰면 막대가 다 비어 보인다 — 대신 **그 시점에 관측된 최댓값 기준 상대 스케일**을 사용하도록 설계.

`App.tsx`: `'wear-leveling'`을 `WIRED_PRESET_DEFAULTS`에 추가, `isWearPreset` 분기로 이 프리셋일 때만 `toWearRows()`(실제 데이터)를 쓰고 매핑 테이블 컬럼은 안 보이게 처리(다른 두 프리셋과 컬럼 구성이 다름).

<div style="margin-top: 60px;"></div>

## 6. 검증

- **골든 회귀 테스트**(`npm run test:engine`) 통과 — `SSD_Device.cpp` 수정이 커밋된 시나리오 결과에 영향 없음(기존 시나리오들이 이미 `true`/`true`/`100`을 명시하고 있었기 때문).
- **네이티브 하니스**: 버그 수정 전에는 threshold 를 1로 낮춰도 WL=0 유지, 수정 후에는 동일 설정에서 WL=1 확인.
- **브라우저(WASM) 실제 재생**: "마모평준화 시연" 프리셋을 8배속으로 재생해 최종 통계 `GC 실행 횟수=32, WL 실행 횟수=1, Erase 횟수=33`(32 GC-erase + 1 WL-erase) 확인 — 네이티브 하니스 예측과 정확히 일치. 콘솔에 앱 관련 에러 없음.
- 다른 두 프리셋("매핑 기본", "GC 시연")도 이 프리셋 전환 후에 다시 재생해 회귀 없음 확인.

<div style="margin-top: 60px;"></div>

## 7. 요약

- 12개 핵심 세션 완료 이후 추가로 진행한 작업 — 원래 계획엔 "확장 목표"로도 명시돼 있지 않았던, Session 6 조사 당시 "구조적 한계로 검증 못 함"이라 적어뒀던 항목을 나중에 실제로 풀어낸 경우.
- 세 번째 real MQSim 버그를 새로 찾아 고쳤고, 그 결과로 이전 세션의 로직 수정 2개가 실제로 유효하게 작동하는 걸 이 프로젝트 최초로 확인했다.
- "여러 번 반복 발동"은 이 데모 규모에서 비현실적이라는 걸 확인하고, "1회 발동"을 정직한 목표로 재설정 — 억지로 부풀리지 않음.

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [마모 평준화 버그와 의도적 동작 변경](/ftl-visual-simulator/reference/bug-list/wl-bug-deviation/) (Session 6, 로직 버그 2개), [정적 마모 평준화 설정 누락 버그](/ftl-visual-simulator/reference/bug-list/wl-threshold-not-wired-bug/) (이번에 찾은 버그의 근본 원인 분석)
- [Claude 구현 작업 상세](/ftl-visual-simulator/plan/implementation/), [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/)
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — 실제 코드
