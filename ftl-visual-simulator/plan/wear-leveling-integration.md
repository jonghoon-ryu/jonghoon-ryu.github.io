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
- **`buildWlWorkloadXml()`** — "GC 시연"과 같은 워크로드 형태(`Working_Set_Percentage: 25`)에 `Stop_Time: 8000000000`(GC 시연의 2500000000 보다 김 - WL 발동에 필요한 event-group 수가 더 많기 때문). 네이티브 하니스로 측정한 최종 실행 규모(당시): 약 279만 event-group, GC 29회, WL 1회 — 자연 종료(이벤트 큐 고갈이 아니라 Stop_Time 도달로 정상 종료됨을 확인). (GC 횟수는 원래 32회로 측정됐으나, 이후 [RGA 후보 선택 버그](/ftl-visual-simulator/reference/bug-list/rga-incomplete-block-bug/) 수정으로 29회로 갱신 - 빈 block 을 잘못 고르던 낭비된 시도가 줄어든 결과.) **다시 갱신**: `chipCount === 1`일 때 `Address_Alignment_Unit`을 페이지가 아니라 섹터 단위로 잘못 계산하던 버그(`ioAddressAlignmentUnitSectors()`, 4KB 페이지 기준 실제로는 2페이지 간격으로만 주소가 생성되고 있었음)를 고치고 네이티브 하니스로 재측정 - **GC 92회(그중 일부는 실제 페이지 이동 동반, 이전엔 전부 0), WL 1회는 그대로**. event-group 총량은 재측정하지 않음.
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

## 8. 후속 작업 — WL 임계값을 1보다 높여보려는 시도

1회 발동을 목표로 정리한 뒤, "erase count 차이가 겨우 1이어도 발동하는 게 맞냐"는 질문에서 시작해 threshold 를 더 현실적인 숫자(3, 5 등)로 올려볼 수 있는지 다시 파봤다. 결론부터 말하면 **못 올렸다** — 그 과정에서 진짜 데드락 버그 4개를 새로 찾아 고쳤고, 워크로드 자체를 바꾸는 시도도 구조적인 이유로 실패했다.

<div style="margin-top: 60px;"></div>

### 8.1 계기 — "재생 재개해도 배너가 안 사라짐" 버그 조사 중 진짜 데드락을 밟다

UI 버그(재시작 후 WL 마커가 안 지워짐, 재생 재개해도 발동 배너가 안 사라짐 등) 몇 개를 고치던 중, threshold 를 2 이상으로 올려서 재현 테스트를 하다가 시뮬레이션이 에러 없이 조용히 멈추는(hang) 문제를 다시 마주쳤다. 이건 사실 훨씬 이전 세션에 "block 개수가 작을 때 TSU_FLIN 스케줄러에서 멈춘다"고 잘못 추정하고 [GitHub 이슈](https://github.com/jonghoon-ryu/ftl-visual-simulator-app/issues/41)로만 남겨뒀던 바로 그 정지였다.

이번엔 제대로 추적해서 `TSU_FLIN` 이 애초에 인스턴스화조차 안 되는 죽은 코드라는 걸 확인하고, 진짜 원인 — `TSU_OutOfOrder`/`TSU_Priority_OutOfOrder` 스케줄러에 걸쳐 서로를 가리고 있던 4개의 독립된 버그(switch-case fallthrough, 생성자 인자 순서 오류, 서스펜드/리쥼 시 활성 다이 카운터 어긋남) — 를 찾아 수정했다. 상세 분석과 수정 내용은 [명령 서스펜드가 한 번도 작동한 적이 없던 버그](/ftl-visual-simulator/reference/bug-list/suspend-resume-deadlock-bug/) 문서에 별도로 기록.

<div style="margin-top: 60px;"></div>

### 8.2 데드락을 고쳐도 threshold 2 이상은 여전히 발동 안 함

데드락을 고친 뒤 재검증:

- 기본 설정(threshold=1, Stop_Time 그대로): 100% 완주, `Total_WL_Executions=1` 유지 — 회귀 없음.
- threshold 를 2~50 으로 올리면: 더 이상 멈추진 않지만(데드락은 확실히 해결) 기본 Stop_Time 안에서는 **한 번도 발동하지 않고 완주**해버림.
- Stop_Time 을 2~3배로 늘려도(약 560만~840만 요청) 여전히 0회 — 그 이상(3.5~4배, 약 900만 요청) 늘리면 **아직 다 못 고친 잔여 stall**(같은 조사에서 발견, 근본 원인 미규명, 요청 수와만 상관관계 있고 threshold 값과는 무관하게 항상 같은 지점에서 발생)에 걸림.
- Over-provisioning 을 5%/3%로 낮추거나, block 개수를 16개로 줄이거나, GC 정책을 RANDOM/GREEDY 로 바꿔봐도 마찬가지 — threshold=2조차 안 뜨거나(RANDOM 은 오히려 그 잔여 stall 을 더 일찍 밟음).

원인: 이 프로젝트가 쓰는 GC 정책(RGA)은 애초에 "마모를 고르게 분산시키는" 것 자체가 목적이라, block 간 erase count 차이가 크게 벌어지질 않는다. static WL 이 잡아내야 할 "불균형"을 GC 자신이 이미 상당 부분 막고 있는 셈 — 그러니 threshold, OP, block 개수를 아무리 조정해도 근본적인 한계는 안 바뀐다.

> **정정 (2026-09-24)**: 위 원인 분석은 틀렸다. 진짜 원인은 static WL 이 대상을 고르는 방식의 버그(#18) — 평면 전체에서 erase count 가 가장 낮은 block 이 거의 항상 한 번도 안 쓰이는 write frontier 라서, 그게 거부되면 WL 은 그 뒤로 영원히 포기했다. 아래 "잔여 stall" 도 근본 원인을 찾았다(#21). [9절](#section-9) 참고.

<div style="margin-top: 60px;"></div>

### 8.3 워크로드 자체를 바꿔보기 — hot/cold 스큐도 구조적으로 막힘

파라미터 조정이 안 되니 워크로드 생성 자체를 hot/cold 스큐(`Address_Distribution_Type::RANDOM_HOTCOLD`)로 바꿔서, 특정 LPN 에 쓰기를 집중시켜보려 했다. 두 단계에서 모두 막혔다:

1. **DRAM 쓰기 캐시가 다 흡수해버림**: hot 영역을 좁게 잡으니(전체 주소 공간의 5~20%), 300만 개 넘는 요청 중 실제 flash 에 프로그램 명령이 나간 건 **단 9번**(`Issued_Flash_Program_CMD="9"`) — hot 영역의 distinct 페이지 수가 DRAM 쓰기 캐시 용량보다 작아서 거의 전부 캐시에서만 맴돌고 flash 까지 내려가질 않았다.
2. **캐시를 꺼도(`Caching_Mode::TURNED_OFF`) 여전히 발동 안 함**: 이번엔 실제로 292번 소거가 일어났지만(`Average_Page_Movement_For_GC="0.000000"` — 전부 완전-무효 block 만 골라 마이그레이션 없이 청소), hot 비율(5~20%)·threshold(2~5) 어떤 조합에도 WL 은 여전히 0회.

두 번째 결과의 진짜 이유는 **page-level FTL 의 논리/물리 주소 분리** 때문이다: 어떤 LPN 을 아무리 자주 덮어써도, 실제 쓰기는 그 LPN 의 "과거 위치"가 아니라 **그 순간의 write frontier(현재 활성 block)** 에 순차로 쌓인다. 즉 논리 주소 접근 빈도를 스큐해도, 그게 어느 physical block 을 더 닳게 하는지는 논리 주소값이 아니라 "쓰기 순서"가 결정한다 — 그래서 hot/cold 패턴을 아무리 강하게 줘도 물리 block 소거 횟수는 여전히 고르게 퍼진다. static WL 이 원래 잡아내야 하는 "한 block 에 cold 데이터가 오래 남아있는" 상황을 재현하려면, 그 데이터를 **아예 한 번도 다시 건드리지 않는** 진짜 cold 영역이 필요한데, MQSim 의 `RANDOM_HOTCOLD` 생성기는 두 영역 모두에 계속(비율만 다르게) 트래픽을 흘려보내는 방식이라 이 조건을 만들어주지 못한다.

<div style="margin-top: 60px;"></div>

### 8.4 결론 — threshold=1 유지

이 preset 의 현재 설계(block 24개, RGA, OP 10%, 이 워크로드 생성기) 안에서는 **threshold=1 이 사실상 유일하게 동작하는 값**이라는 결론을 냈다. 더 큰 숫자로 "제대로" 보여주려면 파라미터 조정이 아니라, 워크로드 생성기 자체에 "한 번 쓰고 다시는 안 건드리는 진짜 cold 영역" 개념을 새로 추가하는 수준의 엔진 작업이 필요 — 오늘은 여기서 멈추고, threshold=1 그대로 유지하기로 했다.

새로 찾은 데드락 버그 4개는 고쳐서 유지한다(threshold 조정과 무관하게 그 자체로 진짜 upstream 버그이자, 이후 threshold 를 조정할 여지를 다시 열어주는 전제 조건이므로).

<div style="margin-top: 60px;"></div>

## 9. 후속 작업 2 — threshold 3 달성 {#section-9}

8절에서 멈췄던 두 가지를 다시 파서 둘 다 풀었다. 이 절은 프리셋 설계 쪽 기록이고, 엔진 버그의 상세 분석은 [정적 마모 평준화 대상 선정 버그와 조용히 멈추던 버그 4개](/ftl-visual-simulator/reference/bug-list/wl-target-and-stall-bugs/)에 따로 있다.

<div style="margin-top: 60px;"></div>

### 9.1 발동이 안 되던 진짜 이유 — 대상 선정 버그

8.2의 "RGA 가 마모를 고르게 퍼뜨리기 때문"이라는 설명은 틀렸다. static WL 은 "평면에서 erase count 가 가장 낮은 block"을 대상으로 삼는데, 그 block 이 거의 항상 **한 번도 프로그램되지 않는 write frontier**(매핑 테이블이 CMT 에 다 들어가서 영원히 erase count 0 인 `Translation_wf`)였다. frontier 는 안전한 후보가 아니라서 거부되고, upstream 코드는 거기서 다음 후보를 찾지 않고 그냥 포기했다 — 그 frontier 의 erase count 는 영원히 0 이니 평생 포기. 대상을 "데이터가 있고 안전한 block" 중에서 고르도록 고쳤다(버그 #18).

<div style="margin-top: 60px;"></div>

### 9.2 워크로드 — "한 번 쓰고 다시 안 건드리는" 진짜 cold flow

#18 을 고치자 8.3의 결론이 그대로 맞았음이 드러났다: 기존 워크로드(균일 무작위 한 flow)로는 threshold 1 에서 WL 이 151번 헛돌고, 2-5 에서는 0-1번. 동적 WL 이 마모를 평평하게 유지해서 erase count 차이가 1-2 이상 벌어지지 않는다.

8.3에서 "`RANDOM_HOTCOLD` 는 두 영역 모두에 계속 트래픽을 흘려서 안 된다"고 했던 문제는, 생성기를 고치는 대신 **flow 를 두 개로 나눠서** 풀었다. MQSim 은 논리 주소 공간을 flow 수만큼 나누고, flow 마다 자기 write frontier 를 따로 가지므로 두 flow 의 데이터는 같은 block 에 섞이지 않는다:

- **flow 0 (cold)**: `STREAMING` 으로 자기 영역의 절반을 순서대로 **딱 한 번씩** 쓰고 영원히 멈춘다(`Stop_Time=0` + `Total_Requests_To_Generate` = 그 영역의 page 수 - 1). DRAM 쓰기 캐시는 끈다 — 켜두면 8.3처럼 캐시가 전부 흡수해서 flash 까지 안 내려간다.
- **flow 1 (hot)**: 기존과 같은 무작위 덮어쓰기, 자기 영역의 50%, 끝까지.

cold block 은 erase count 0 에 머무르고 hot block 들만 계속 닳아서, static WL 이 원래 잡아내야 하는 불균형이 실제로 생긴다.

<div style="margin-top: 60px;"></div>

### 9.3 규모를 키우자 드러난 멈춤 버그들

threshold 를 올리고 Stop_Time 을 늘리며 여러 구성을 돌리자, 8.2의 "잔여 stall" 을 비롯해 멈추거나 크래시하는 upstream 버그가 4개 연달아 나왔다(#21-24 — 하나를 고칠 때마다 다음 것이 드러나는 사슬). 전부 고친 뒤 29가지 구성(threshold 1-10, 칩 1/2/4, block 16-40, GC 임계값 1-95%, seed 3종, Stop_Time 4배)이 모두 모든 요청을 완료했다.

<div style="margin-top: 60px;"></div>

### 9.4 최종 설정

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>항목</th><th>이전</th><th>지금</th></tr>
<tr><td>워크로드</td><td>균일 무작위 1 flow</td><td>cold(순차 1회) + hot(무작위) 2 flow</td></tr>
<tr><td><code>staticWlThreshold</code></td><td>1</td><td>3</td></tr>
<tr><td>기본 결과(24 block)</td><td>WL 1회</td><td>GC 58 / WL 7, 매번 cold block 한 개(16 page) 통째로 이동</td></tr>
<tr><td>Block 개수 슬라이더 최솟값</td><td>8</td><td>16 (이 프리셋만 — flow 가 둘이라 frontier block 이 두 배)</td></tr>
</table>
</div>

브라우저(WASM)에서도 기본 설정이 네이티브와 똑같이 GC 58 / WL 7 로 끝나는 것을 확인했다. 앱 쪽에서는 두 flow 가 같은 LPN 번호를 따로 쓰기 때문에(cold 의 LPN 5 ≠ hot 의 LPN 5), 로그와 덮어쓰기 표시가 쓰는 "LPN → 위치" 맵을 flow 별로 구분하도록 같이 고쳤다.

남은 것: WL 임계값 슬라이더는 아직 UI 에 없고, block 마다 cold/hot 중 어느 flow 의 데이터인지 엔진이 알려주긴 하지만(`streamId`) 화면에는 아직 표시하지 않는다.

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [마모 평준화 버그와 의도적 동작 변경](/ftl-visual-simulator/reference/bug-list/wl-bug-deviation/) (Session 6, 로직 버그 2개), [정적 마모 평준화 설정 누락 버그](/ftl-visual-simulator/reference/bug-list/wl-threshold-not-wired-bug/) (처음 찾은 버그의 근본 원인 분석), [명령 서스펜드가 한 번도 작동한 적이 없던 버그](/ftl-visual-simulator/reference/bug-list/suspend-resume-deadlock-bug/) (8절에서 찾은 데드락 버그 4개), [정적 마모 평준화 대상 선정 버그와 조용히 멈추던 버그 4개](/ftl-visual-simulator/reference/bug-list/wl-target-and-stall-bugs/) (9절)
- [Claude 구현 작업 상세](/ftl-visual-simulator/plan/implementation/), [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/)
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — 실제 코드
