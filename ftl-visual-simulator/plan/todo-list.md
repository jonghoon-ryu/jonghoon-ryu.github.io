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

- [x] ~~멀티 칩(multi-chip) UI 지원~~ (2026-09-19 앱 커밋 `08cc312` 로 완료 — 칩 개수 선택(현재 1/2/4), 격자의 칩 배지로 "Chip N · Block M" 중복 문제 해결. 2026-09-24 에는 칩 색상을 색각 이상 기준을 통과하는 색으로 교체(`96ea771`)). 원래 메모: 앱이 칩/다이/플레인 수를 1로 하드코딩하고 있었고, 칩을 늘리면 칩마다 block 번호가 0부터 다시 시작해 라벨이 중복되던 문제.

- [x] ~~write 갯수 기반(시간 기반 아님) GC 테스트~~ ([PR #24](https://github.com/jonghoon-ryu/ftl-visual-simulator-app/pull/24)로 완료). 실제 브라우저 데모로 GC를 관찰하면 (1) 실행이 너무 빨리 끝나서 뭐가 일어났는지 보기 힘들고, (2) write 사이의 실제 시간 간격이 큐 깊이/flash 지연시간 등에 따라 매번 달라서 일정한 리듬으로 관찰하기 힘들다는 문제가 있었음. `GcTriggerTest`는 실제 워크로드를 전혀 안 돌리고 `Check_gc_required()`를 free-block-pool 크기만 바꿔가며 **write 1회당 1번씩 직접 호출** — 시뮬레이션 시간이 아예 개입 안 해서 매 스텝이 항상 동일한 "거리"를 가짐. `block_pool_gc_threshold = floor(gc_threshold × block_no_per_plane)` 공식대로 정확히 9번째 write에서 GC가 처음 발동하는 것까지 확인함. Ryu 확인 후 병합.

- [x] ~~GTest/GMock 단위 테스트 도입~~ ([PR #23](https://github.com/jonghoon-ryu/ftl-visual-simulator-app/pull/23)로 완료, `engine/tests/unit/`) — 왜 필요했는지, 어떻게 각 클래스를 다뤘는지는 [마모평준화 시연 연동 작업 기록](/ftl-visual-simulator/plan/wear-leveling-integration/) 참고.

- [x] ~~Session 3 설계 산출물(MVP 범위 문서, 와이어프레임, hook 위치 설계표)~~ — 작성하지 않고 **종료(대체됨)**. Session 4 엔진 작업이 먼저 끝나면서 건너뛰었고, 지금은 실제 앱과 [MQSim 코드 분석](/ftl-visual-simulator/reference/mqsim/code-analysis/overview/)·버그 문서들이 그 역할을 대신함 (2026-09-24 정리).

- [ ] **Cost-Benefit GC 구현** (확장 목표, 10/17~18 버퍼): MQSim 에 없는 정책. 앱의 "GC 알고리즘 비교" 표에 한 줄 추가하면 RGA 등과 바로 비교 가능.

<div style="margin-top: 60px;"></div>

## 참고

- [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) — Session 11
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app)
