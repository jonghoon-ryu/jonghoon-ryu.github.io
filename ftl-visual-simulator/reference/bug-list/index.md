---
layout: default
title: 버그 목록
permalink: /ftl-visual-simulator/reference/bug-list/
---
# 버그 목록

이 프로젝트는 원본 MQSim C++ 코드를 그대로 컴파일해서 쓰기 때문에("힘들어도 정확하게" — [WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/) 참고), 재구현했다면 절대 마주치지 않았을 upstream MQSim 자체의 버그들을 실제로 밟아왔다. 이 카테고리는 그렇게 찾아낸 버그들을 발견 경위·근본 원인·수정 내용까지 상세히 기록한 하위 문서들과, 그걸 한눈에 볼 수 있는 요약 표를 모아둔다.

<div style="margin-top: 60px;"></div>

## 하위 문서

- [버그 목록표](/ftl-visual-simulator/reference/bug-list/table/) — 지금까지 확인된 버그 전체를 표 하나로 정리
- [MQSim 버그 헌트](/ftl-visual-simulator/reference/bug-list/mqsim-bug-hunt/) — WASM 빌드가 네이티브와 다른 결과를 내던 문제를 추적해서 찾아낸 이식성 버그 4개
- [마모 평준화 버그와 의도적 동작 변경](/ftl-visual-simulator/reference/bug-list/wl-bug-deviation/) — static 마모 평준화 hook 작업 중 발견한 로직 버그 2개
- [재구성 크래시 버그](/ftl-visual-simulator/reference/bug-list/reconfigure-crash-bug/) — DRAM 캐시 대기열의 이중 소유권(use-after-free) 버그
- [초기화되지 않은 Bandwidth 필드 버그](/ftl-visual-simulator/reference/bug-list/bandwidth-divide-by-zero-bug/) — workload 컨트롤 작업 중 발견한 0 나누기 크래시
- [정적 마모 평준화 설정이 아예 전달되지 않던 버그](/ftl-visual-simulator/reference/bug-list/wl-threshold-not-wired-bug/) — `Static_Wearleveling_Threshold` 가 설정과 무관하게 항상 무시되던 문제
- [잘못된 inline 선언 버그](/ftl-visual-simulator/reference/bug-list/inline-linkage-bug/) — GMock 유닛 테스트가 처음 밖에서 불러본 protected 메서드의 링크 에러

<div style="margin-top: 60px;"></div>

## 관련 문서

- [참고 자료](/ftl-visual-simulator/reference/)
- [마모평준화 시연 연동 작업 기록](/ftl-visual-simulator/plan/wear-leveling-integration/)
