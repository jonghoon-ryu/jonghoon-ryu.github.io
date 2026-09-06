---
layout: default
title: 정적 마모 평준화 설정이 아예 전달되지 않던 버그 — 그리고 마침내 발동시킨 이야기
permalink: /ftl-visual-simulator/reference/bug-list/wl-threshold-not-wired-bug/
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

# 정적 마모 평준화 설정이 아예 전달되지 않던 버그 — 그리고 마침내 발동시킨 이야기

[마모 평준화 버그와 의도적 동작 변경](/ftl-visual-simulator/reference/bug-list/wl-bug-deviation/) 문서는 Session 6에서 고친 로직 버그 2개를 다루면서 "static 마모 평준화가 이 프로젝트 안에서 실제로 발동하는 걸 한 번도 확인 못 했다"고 끝맺었다. "마모평준화 시연" 프리셋을 실제 엔진에 연동하려고 다시 조사하다가 **세 번째 버그, 이번엔 완전히 다른 종류의 버그**를 찾았고 — 그걸 고치고 나서야 static WL 을 실제로 한 번 발동시키는 데 성공했다. 이 문서는 그 과정을 기록한다.

<div style="margin-top: 60px;"></div>

## 1. Static_Wearleveling_Threshold 를 아무리 바꿔도 반응이 없었다

"GC 시연"과 같은 방식으로("네이티브 CLI로 먼저 검증") 워크로드를 튜닝하기 시작했다. 접근 방법:

1. 오랫동안 GC 를 강제로 계속 실행시켜서(작은 지오메트리 + 높은 GC_Exec_Threshold) block 들의 erase count 를 서서히 갈라놓는다.
2. `Static_Wearleveling_Threshold` 를 원래 값(100)보다 훨씬 낮게(예: 5, 1) 설정해서, 그 갈라짐이 임계값을 넘기 쉽게 만든다.

블록 64개로 지오메트리를 키우고 오래 실행해보니(1700만 step 이상) `Get_min_max_erase_difference()`가 계산하는 min/max erase 차이가 0 → 7까지 꾸준히 벌어졌다. 그런데 **threshold 를 몇으로 설정하든 `Total_WL_Executions` 는 계속 0**이었다.

<div style="margin-top: 60px;"></div>

## 2. 원인 확정 — 디버그 프린트로 직접 찍어봄

`check_static_wl_required()` 안에 `Get_min_max_erase_difference()`가 반환하는 값과, 실제로 비교 대상인 `static_wearleveling_threshold` 값을 그대로 찍어보았다:

```
[CHK] enabled=1 diff=1 threshold=100
[CHK] enabled=1 diff=1 threshold=100
...
```

**XML 에 분명히 `<Static_Wearleveling_Threshold>1</Static_Wearleveling_Threshold>`라고 써서 넣었는데, 실행 중인 값은 항상 100** 이었다 — 마치 내가 넣은 설정이 통째로 무시되는 것처럼.

원인을 추적해보니 `SSD_Device.cpp`에서 `GC_and_WL_Unit_Page_Level`을 생성하는 코드였다:

```cpp
// 수정 전
gcwl = new SSD_Components::GC_and_WL_Unit_Page_Level(ftl->ID() + ".GCandWLUnit", amu, fbm, tsu, (SSD_Components::NVM_PHY_ONFI *)device->PHY,
    parameters->GC_Block_Selection_Policy, parameters->GC_Exec_Threshold, parameters->Preemptible_GC_Enabled, parameters->GC_Hard_Threshold,
    parameters->Flash_Channel_Count, parameters->Chip_No_Per_Channel,
    parameters->Flash_Parameters.Die_No_Per_Chip, parameters->Flash_Parameters.Plane_No_Per_Die,
    parameters->Flash_Parameters.Block_No_Per_Plane, parameters->Flash_Parameters.Page_No_Per_Block,
    parameters->Flash_Parameters.Page_Capacity / SECTOR_SIZE_IN_BYTE, parameters->Use_Copyback_for_GC, max_rho, 10,
    parameters->Seed++);
```

생성자 호출이 `..., max_rho, 10, parameters->Seed++)`에서 그냥 끝나버린다. 그런데 `GC_and_WL_Unit_Page_Level`의 실제 생성자 시그니처는:

```cpp
GC_and_WL_Unit_Page_Level(..., unsigned int max_ongoing_gc_reqs_per_plane = 10,
    bool dynamic_wearleveling_enabled = true, bool static_wearleveling_enabled = true,
    unsigned int static_wearleveling_threshold = 100, int seed = 432);
```

**`dynamic_wearleveling_enabled`, `static_wearleveling_enabled`, `static_wearleveling_threshold` 세 파라미터가 통째로 생략**됐다. C++ 은 생략된 인자에 기본값을 채워 넣으므로, `ssdconfig.xml`에 뭐라고 쓰든 실제로 도는 시뮬레이션은 항상 컴파일 타임에 박힌 기본값(`true, true, 100`)을 썼다. `Device_Parameter_Set::XML_deserialize()`는 이 세 값을 정확히 파싱해서 `Device_Parameter_Set`의 정적 멤버에 담아두는데, 그 값을 실제로 쓰는 곳까지 배선이 안 된 것이다.

<div style="margin-top: 60px;"></div>

## 3. 왜 지금까지 몰랐나

`Dynamic_Wearleveling_Enabled`/`Static_Wearleveling_Enabled`는 기본값이 둘 다 `true`라서, 이 두 값을 "끄고" 싶었던 적이 없는 한(이 프로젝트도, 아마 upstream 사용자 대부분도) 아무 문제가 안 생긴다. `Static_Wearleveling_Threshold`도 upstream 예제들의 기본값(100)이 컴파일 타임 기본값과 우연히 같아서, **이 threshold 를 실제로 다른 값으로 바꿔보려고 시도한 적이 없는 한** 절대 드러나지 않는 버그였다. 이 프로젝트가 "마모평준화 시연"을 위해 이 값을 의도적으로 크게 낮춰보려던 순간 처음으로 마주친 것으로 보인다.

<div style="margin-top: 60px;"></div>

## 4. 수정

`SSD_Device.cpp`에서 생략됐던 세 인자를 그대로 전달하도록 고쳤다:

```cpp
gcwl = new SSD_Components::GC_and_WL_Unit_Page_Level(..., max_rho, 10,
    parameters->Dynamic_Wearleveling_Enabled, parameters->Static_Wearleveling_Enabled, parameters->Static_Wearleveling_Threshold,
    parameters->Seed++);
```

커밋된 golden 시나리오들의 `ssdconfig.xml`은 이미 세 값 모두 컴파일 타임 기본값과 똑같이(`true`/`true`/`100`) 명시하고 있어서, 이 수정은 golden 회귀 테스트 결과에 전혀 영향을 주지 않는다(직접 확인함) — "우연히 맞던 값"이 "항상 명시적으로 맞는 값"으로 바뀌는 것뿐이다.

<div style="margin-top: 60px;"></div>

## 5. 이제 진짜로 발동시켜보기

버그를 고친 뒤, threshold 를 1로 낮추고 같은 워크로드를 다시 돌려보니:

```
step=1500000 minErase=0 maxErase=1 diff=1 GC=7 WL=1 blocks=64
```

**`Total_WL_Executions` 가 마침내 1이 됐다.** [마모 평준화 버그와 의도적 동작 변경](/ftl-visual-simulator/reference/bug-list/wl-bug-deviation/)에서 고친 두 로직 버그(`GC_WL_started()` 인자 타입 오류, erase count 차이 계산 오류)가 실제로 의미 있는 상태에서 작동하는 걸 처음으로 확인한 순간이다.

다만 이후 1500만 step 을 더 돌려도(diff 가 7까지 계속 벌어졌음에도) **WL 은 다시 발동하지 않았다.** 원인은 그 문서가 이미 짚었던 구조적 특성과 맞물려 있다: WL 이 하나의 "가장 안 지워진" 블록을 비우고 free pool 로 돌려보내면, dynamic 마모 평준화가 "가장 안 닳은 free 블록을 우선적으로 재사용"하는 정책 때문에 그 블록이 곧바로 **새로운 write frontier** 로 재배정된다. Frontier 블록은 `is_safe_gc_wl_candidate()`가 명시적으로 제외 대상이므로, 다시 "안전하게 고를 수 있는 가장 안 지워진 블록"이 나타나려면 이번에 새로 frontier 가 된 그 블록이 다 채워지고 회전할 때까지 기다려야 한다 — 이게 처음 한 번 걸리는 시간만큼 다시 걸린다.

즉 **정확히 1번의 실제 static WL 발동**이 이 프로젝트가 감당할 수 있는 데모 규모에서 정직하게 보여줄 수 있는 결과다. 반복해서 여러 번 보여주려면 지금보다 훨씬 긴 실행 시간이 필요하다.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th></th><th>버그 1·2 (로직 오류)</th><th>이 문서의 버그 (설정 누락)</th></tr>
<tr><td>증상</td><td>트리거 조건 계산 자체가 틀림</td><td>트리거 조건은 맞는데, 설정값이 반영 자체가 안 됨</td></tr>
<tr><td>기본값에서 드러나는가</td><td>아니오 (기본값으로는 결과가 안 달라짐)</td><td>아니오 (기본값이 컴파일 타임 기본값과 우연히 같음)</td></tr>
<tr><td>발견 계기</td><td>Session 6, 마모 평준화 hook 추가 중</td><td>"마모평준화 시연" 실제 연동 중, threshold 를 낮춰보려다가</td></tr>
<tr><td>고친 뒤 실제 영향 확인</td><td>못 함(3번째 구조적 문제 때문)</td><td>**확인함** — WL 1회 발동</td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 6. 요약

- 세 번째 real MQSim 버그(설정값 전달 누락) 발견 + 수정 — golden 회귀 테스트에 영향 없음 확인.
- 이 수정 덕분에 [마모 평준화 버그와 의도적 동작 변경](/ftl-visual-simulator/reference/bug-list/wl-bug-deviation/) 문서의 로직 수정 2개가 실제로 유효한 상태에서 작동하는 걸 이 프로젝트 최초로 확인했다.
- "마모평준화 시연" 프리셋을 real 엔진에 연동 완료 — 단, 재생 1회당 WL 발동은 정확히 1번. 여러 번 반복해서 보여주는 건 이 데모 규모에서는 비현실적이라 시도하지 않았다.
- Block 개수 64, `staticWlThreshold: 1` 등 정확한 튜닝값은 `src/data/mqsimConfigs.ts`의 `DEFAULT_WL_PARAMS`/`buildWlWorkloadXml` 참고.

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [마모 평준화 버그와 의도적 동작 변경](/ftl-visual-simulator/reference/bug-list/wl-bug-deviation/) — 이 문서가 이어받는 이전 조사
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — 실제 코드
