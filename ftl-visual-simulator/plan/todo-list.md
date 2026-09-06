---
layout: default
title: To do list
permalink: /ftl-visual-simulator/plan/todo-list/
---
# To do list

세션 진행 중 발견했지만 그 자리에서 바로 처리하지 않고 나중으로 미룬 자잘한 항목들을 모아두는 곳. 세션별 상세 계획([전체 개발 계획](/ftl-visual-simulator/plan/full-plan/))에 넣기엔 너무 작거나, 아직 우선순위가 안 정해진 것들.

<div style="margin-top: 60px;"></div>

## 열려있는 항목

- [ ] **크로스 브라우저 확인 — Microsoft Edge**: Session 11("마무리 (1) — 다듬기")의 "크로스 브라우저 확인" 작업 중, Claude 쪽에서는 Chrome 밖에 확인할 수 없어서 Safari/Firefox/Edge 는 미확인 상태로 남겨뒀음. Safari/Firefox 는 Ryu 가 별도로 확인 완료(OK). **Edge 는 아직 확인 필요.**

- [ ] **GTest/GMock 단위 테스트 도입** (13~16번 버퍼 예정, [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/)에 원래부터 명시돼 있던 항목). 지금 있는 [golden 회귀 테스트](https://github.com/jonghoon-ryu/ftl-visual-simulator-app/blob/main/engine/run-regression-tests.sh)는 "커밋된 시나리오 3개를 실제로 끝까지 돌려서 결과가 예전과 똑같은지"만 확인하는 것이라, 실행 자체가 느리고(수십만~수백만 event-group), 시나리오 안에서 우연히 발생하는 조건에만 의존한다. GMock 은 그것과 성격이 다른, **개별 모듈을 격리해서 원하는 상태를 강제로 주입해 즉시 검증**하는 방식이다.

  **왜 이게 좋은지 — [마모평준화 시연 연동 작업](/ftl-visual-simulator/plan/wear-leveling-integration/)에서 실제로 겪은 예시로 설명:**
  - 이번에 static 마모 평준화(WL)가 실제로 발동하는지 확인하려고, 네이티브 하니스로 **170만~2800만 event-group**을 실제로 돌려서 block 들의 erase count 가 우연히 벌어지길 기다려야 했다. GMock 으로 `Flash_Block_Manager_Base`(이미 추상 인터페이스로 존재)를 모킹했다면, `Get_min_max_erase_difference()`가 원하는 값(예: 7)을 즉시 반환하도록 만들어서 `check_static_wl_required()`/`run_static_wearleveling()`의 동작을 **밀리초 단위로, 정확히 원하는 조건에서** 검증할 수 있었을 것이다 — 실제로 그 조건이 벌어질 때까지 기다릴 필요가 없다.
  - [정적 마모 평준화 설정 누락 버그](/ftl-visual-simulator/reference/wl-threshold-not-wired-bug/)(threshold 값이 엔진까지 전달 안 되던 버그)도, `GC_and_WL_Unit_Page_Level`을 직접 인스턴스화해서 생성자에 넘긴 threshold 가 실제로 저장/사용되는지 확인하는 단위 테스트가 있었다면 **처음부터 못 만들었거나, 만들자마자 바로 잡혔을** 종류의 버그다. golden 회귀 테스트는 시나리오 XML 이 이미 기본값(100)을 쓰고 있어서 이 버그를 절대 못 잡는다 — 정확히 이런 "설정이 특정 값일 때만 차이가 드러나는" 버그를 잡는 게 단위 테스트의 몫이다.
  - [Block 개수 12/13개 경계의 데드락 버그](https://github.com/jonghoon-ryu/ftl-visual-simulator-app/pull/17)처럼 "정확히 이 경계값에서만" 발생하는 문제도, `max_ongoing_gc_reqs_per_plane`/free block pool 크기를 모킹으로 직접 통제하면 실제 워크로드를 안 돌리고도 그 경계 자체를 테스트로 못박아둘 수 있다.
  - 이미 `Address_Mapping_Unit_Base`/`Flash_Block_Manager_Base`/`GC_and_WL_Unit_Base`/`TSU_Base` 4개가 추상 인터페이스로 존재해서, 새로 리팩터링할 필요 없이 GMock 으로 바로 모킹 가능하다는 게 이 계획이 애초에 실현 가능하다고 판단한 근거였음([MQSim 개괄](/ftl-visual-simulator/reference/mqsim/code-analysis/overview/) 참고).

  요약하면: 골든 회귀 테스트는 "MQSim 이 예전과 똑같이 동작하는가"를 확인하고, GMock 단위 테스트는 "이 모듈이 이 조건에서 정확히 이렇게 동작하는가"를 몇 시간이 아니라 몇 밀리초 만에, 그리고 실제 워크로드로는 거의 못 만드는 희귀한 조건까지 확인해준다 — 이번 마모평준화 작업에서 겪은 두 가지 어려움(느린 재현, 설정값이 조용히 무시되는 버그)을 정확히 겨냥한 도구.

<div style="margin-top: 60px;"></div>

## 참고

- [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) — Session 11
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app)
