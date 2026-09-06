---
layout: default
title: 잘못된 inline 선언 버그 — 유닛 테스트가 처음으로 밖에서 불러본 함수
permalink: /ftl-visual-simulator/reference/bug-list/inline-linkage-bug/
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

# 잘못된 inline 선언 버그 — 유닛 테스트가 처음으로 밖에서 불러본 함수

[GMock/GTest 유닛 테스트 스위트](/ftl-visual-simulator/plan/wear-leveling-integration/)를 `GC_and_WL_Unit_Base`까지 확장해서 만들다가, 링크 에러 하나를 만났다. 원인은 버그라기보단 **아무도 지금까지 이 코드를 그 파일 밖에서 부른 적이 없어서** 몇 년째 티가 안 났던 실수였다.

<div style="margin-top: 60px;"></div>

## 1. 증상

`check_static_wl_required()`를 유닛 테스트 파일(`gc_and_wl_unit_test.cpp`)에서 직접 호출하도록 짜고 빌드했더니, **컴파일은 통과했는데 링크 단계에서 실패**했다:

```
undefined reference to `SSD_Components::GC_and_WL_Unit_Base::check_static_wl_required(NVM::FlashMemory::Physical_Page_Address)'
```

헤더(`GC_and_WL_Unit_Base.h`)에는 분명히 선언이 있고, `.cpp`에도 분명히 정의가 있는데 "정의를 못 찾겠다"는 에러 — 보통 이런 메시지는 파일을 빌드에서 빠뜨렸을 때 나오는데, 이 `.cpp`는 이미 빌드 대상에 정상적으로 포함돼 있었다.

<div style="margin-top: 60px;"></div>

## 2. 원인 — 헤더에 없는 inline을 .cpp 정의에 붙여놓음

`GC_and_WL_Unit_Base.cpp`를 보니:

```cpp
// 수정 전
inline bool GC_and_WL_Unit_Base::check_static_wl_required(const NVM::FlashMemory::Physical_Page_Address plane_address)
{
	return static_wearleveling_enabled && (block_manager->Get_min_max_erase_difference(plane_address) >= static_wearleveling_threshold);
}
```

`inline` 키워드가 붙어 있다. 그런데 헤더 쪽 선언은:

```cpp
// GC_and_WL_Unit_Base.h
bool check_static_wl_required(const NVM::FlashMemory::Physical_Page_Address plane_address);
```

`inline`이 없다. **`inline`은 "이 정의가 여러 번역 단위(.cpp)에 걸쳐 반복돼도 괜찮다"는 약속**이고, 그래서 보통 헤더에 넣어서 그 헤더를 include 하는 모든 `.cpp`가 각자 정의를 갖게 만드는 용도로 쓴다. 그런데 이 정의는 헤더가 아니라 **`GC_and_WL_Unit_Base.cpp` 딱 한 곳에만** 있다.

정의가 `inline`으로 표시돼 있고 실제로는 정확히 한 번역 단위에만 존재하면, 컴파일러는 "이 함수는 이 번역 단위 안에서만 쓰이고 끝날 것"이라고 가정하고 **다른 번역 단위가 링크할 수 있는 외부 심볼을 아예 안 만들어도 된다**고 판단할 수 있다. 실제로 이 프로젝트에서 `check_static_wl_required()`를 부르는 곳은 원래 같은 파일(`GC_and_WL_Unit_Base.cpp`) 안, 딱 한 군데(`handle_transaction_serviced_signal_from_PHY()`)뿐이었다 — 그 호출은 인라이닝되면서 사라지고, 컴파일러 입장에선 정말로 이 함수의 "진짜" 정의를 남겨둘 이유가 없었던 것.

`Use_static_wearleveling()`도 같은 실수가 있었다.

<div style="margin-top: 60px;"></div>

## 3. 왜 지금까지 아무 문제가 없었나

**이 두 함수는 `protected`다.** `GC_and_WL_Unit_Base`를 상속하는 클래스이거나, 클래스 자기 자신의 코드에서만 부를 수 있다는 뜻이다. 이 프로젝트에서 그런 코드는 지금까지 전부 `GC_and_WL_Unit_Base.cpp`/`GC_and_WL_Unit_Page_Level.cpp` 안에만 있었고, 둘 다 **같은 `.cpp` 파일에서 정의된 함수를 부르는 구조라 문제가 될 일이 없었다.** `inline`이 잘못 붙어있어도, "어차피 이 파일 안에서만 쓰이니까" 괜찮았던 것 — 컴파일러가 무슨 선택을 하든 최소한 자기 자신은 그 정의를 볼 수 있으니까.

이 문제가 드러나려면 **`GC_and_WL_Unit_Base`를 상속하면서 다른 `.cpp` 파일에 있는 코드**가 이 protected 메서드를 호출해야 하는데, 이 프로젝트가 유닛 테스트에서 처음으로 그런 상황(별도 `.cpp`의 테스트 헬퍼 클래스가 `using`으로 protected 메서드를 노출해서 직접 호출)을 만들어냈다.

<div style="margin-top: 60px;"></div>

## 4. 수정

두 곳 모두 `inline`을 지웠다:

```cpp
// 수정 후
bool GC_and_WL_Unit_Base::check_static_wl_required(const NVM::FlashMemory::Physical_Page_Address plane_address)
{
	return static_wearleveling_enabled && (block_manager->Get_min_max_erase_difference(plane_address) >= static_wearleveling_threshold);
}
```

`.cpp` 파일에만 있는 정의는 애초에 `inline`일 이유가 없다 — 그 파일 하나만 컴파일되니 반복 정의 문제 자체가 생길 수 없고, 지우면 컴파일러는 무조건 외부에서 링크 가능한 심볼을 만든다. 동작은 한 글자도 안 바뀌었다.

<div style="margin-top: 60px;"></div>

## 5. 검증

- 유닛 테스트 빌드: 링크 에러 사라지고 `check_static_wl_required()`를 부르는 3개 테스트 전부 통과.
- **골든 회귀 테스트**(`npm run test:engine`) 통과 — `inline` 제거는 심볼 가시성만 바꿀 뿐 함수 본문은 그대로라, 시뮬레이션 결과에는 애초에 영향을 줄 수 없는 종류의 수정.

<div style="margin-top: 60px;"></div>

## 6. 요약

- 버그라기보단 **몇 년째 아무도 안 밟은 지뢰**에 가깝다 — protected 메서드를 같은 파일 밖에서 부르는 코드가 이 프로젝트의 유닛 테스트가 처음이었다.
- [MQSim 버그 헌트](/ftl-visual-simulator/reference/bug-list/mqsim-bug-hunt/)의 이식성 버그들이나 [정적 마모 평준화 설정 누락 버그](/ftl-visual-simulator/reference/bug-list/wl-threshold-not-wired-bug/)처럼 실제 시뮬레이션 결과에 영향을 주는 버그와는 성격이 다르다 — 순수하게 **빌드/링크 문제**이고, 고쳐도 동작은 완전히 동일하다.
- "유닛 테스트를 작성하면서 실제 버그를 하나 더 찾았다"는 점에서, GMock 도입이 왜 필요한지를 보여주는 또 하나의 사례로 기록해둔다 — 이번엔 로직 버그가 아니라 빌드 구조의 결함이었다는 점이 다를 뿐.

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [마모평준화 시연 연동 작업 기록](/ftl-visual-simulator/plan/wear-leveling-integration/) — 이 버그를 발견한 유닛 테스트 스위트 작업
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — 실제 코드
