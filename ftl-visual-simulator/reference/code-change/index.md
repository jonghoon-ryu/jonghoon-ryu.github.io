---
layout: default
title: Code Change
permalink: /ftl-visual-simulator/reference/code-change/
---
# Code Change

이 프로젝트는 MQSim 원본 C++ 코드를 그대로 컴파일해서 엔진으로 쓴다. 그러면서 원본에서 **무엇을 바꿨는지**를 모아둔 카테고리다. 바꾼 이유는 크게 네 가지다 — 버그 수정, 작은 화면 규모에 맞춘 튜닝, UI 에 필요한 계측(hook), 원본에 없는 기능 추가.

<div style="margin-top: 60px;"></div>

## 하위 문서

- [원본 MQSim 대비 변경 사항](/ftl-visual-simulator/reference/code-change/upstream-diff/) — 처음 가져온 원본(`90b0fb1`)과 지금 엔진을 비교해, 버그 수정 · 의도적 동작 변경 · 규모 튜닝 · 새 기능 · 계측/WASM · 테스트로 나눠 정리. **전체를 한눈에 보려면 여기부터.**
- [버그 목록](/ftl-visual-simulator/reference/code-change/bug-list/) — 원본에서 찾아 고친 버그 28개. 버그별 발견 경위와 디버깅 기록 ( 하위 문서 : [버그 목록표](/ftl-visual-simulator/reference/code-change/bug-list/table/) 에 전체 요약 )
- [튜닝된 코드 (Tweaked Code)](/ftl-visual-simulator/reference/code-change/tweaked-code/) — 버그는 아니지만, 원본이 가정하는 규모와 이 프로젝트의 화면 규모가 달라서 일부러 upstream 과 다르게 동작하도록 바꾼 곳

<div style="margin-top: 60px;"></div>

## 관련 문서

- [MQSim 코드 분석 — 원본의 알려진 한계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/known-limits/) — 원본에서 믿으면 안 되는 것들을 한곳에
- [MQSim](/ftl-visual-simulator/reference/mqsim/) · [참고 자료](/ftl-visual-simulator/reference/)
