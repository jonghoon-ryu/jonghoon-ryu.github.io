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

- [ ] **멀티 칩(multi-chip) UI 지원**: 지금 앱은 `Flash_Channel_Count`/`Chip_No_Per_Channel`/`Die_No_Per_Chip`/`Plane_No_Per_Die`를 전부 `mqsimConfigs.ts`에서 `1`로 하드코딩해두고 있다 — 원본 "현실적인" 설정(`engine/mqsim/ssdconfig.xml`)은 8채널×4칩×2다이×2플레인인데, 화면에 블록이 다 보이게 하려고 일부러 1×1×1×1로 단순화해둔 것. 실험 삼아 `Chip_No_Per_Channel`을 2로 바꿔서 돌려보니: (1) **엔진 자체는 전혀 문제 없이 동작**(네이티브 CLI로 확인, `Get_block_state_snapshot()`도 channel/chip/die/plane 정보를 전부 정확히 담아서 반환), (2) 그런데 **UI 라벨링이 깨짐** — `toBlockRows()`/`toWearRows()`(`src/lib/mqsimBlocks.ts`, `mqsimWear.ts`)가 블록 라벨을 `Block ${block.block}`으로만 붙이는데, 칩마다 블록 번호가 0부터 다시 시작하니까 "Block 0"이 칩 개수만큼 화면에 중복으로 나타남. 실제로 구현하려면: (a) `SsdParams`에 칩/다이/플레인 개수를 파라미터로 추가하고 `ParamPanel`에 슬라이더 노출, (b) 블록 라벨을 "Chip 0 · Block 0" 식으로 고쳐서 중복 안 되게 함.

- [x] ~~write 갯수 기반(시간 기반 아님) GC 테스트~~ ([PR #24](https://github.com/jonghoon-ryu/ftl-visual-simulator-app/pull/24)로 완료). 실제 브라우저 데모로 GC를 관찰하면 (1) 실행이 너무 빨리 끝나서 뭐가 일어났는지 보기 힘들고, (2) write 사이의 실제 시간 간격이 큐 깊이/flash 지연시간 등에 따라 매번 달라서 일정한 리듬으로 관찰하기 힘들다는 문제가 있었음. `GcTriggerTest`는 실제 워크로드를 전혀 안 돌리고 `Check_gc_required()`를 free-block-pool 크기만 바꿔가며 **write 1회당 1번씩 직접 호출** — 시뮬레이션 시간이 아예 개입 안 해서 매 스텝이 항상 동일한 "거리"를 가짐. `block_pool_gc_threshold = floor(gc_threshold × block_no_per_plane)` 공식대로 정확히 9번째 write에서 GC가 처음 발동하는 것까지 확인함. Ryu 확인 후 병합.

- [x] ~~GTest/GMock 단위 테스트 도입~~ ([PR #23](https://github.com/jonghoon-ryu/ftl-visual-simulator-app/pull/23)로 완료, `engine/tests/unit/`) — 왜 필요했는지, 어떻게 각 클래스를 다뤘는지는 [마모평준화 시연 연동 작업 기록](/ftl-visual-simulator/plan/wear-leveling-integration/) 참고.

<div style="margin-top: 60px;"></div>

## 참고

- [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) — Session 11
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app)
