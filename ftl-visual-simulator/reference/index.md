---
layout: default
title: 참고 자료
permalink: /ftl-visual-simulator/reference/
---
# 참고 자료

시뮬레이터를 만들고 쓰는 데 필요한 배경 지식을 모아두는 카테고리 — 엔진으로 쓰는 MQSim 자체에 대한 문서, 그 코드를 읽는 방법, 원본에서 바꾼 것, 그리고 WASM/em++ 처럼 이 프로젝트에서 새로 등장하는 도구·개념에 대한 설명.

<div style="margin-top: 60px;"></div>

## 하위 문서

- [MQSim](/ftl-visual-simulator/reference/mqsim/) — MQSim 이 무엇이고, 다른 오픈소스 SSD 시뮬레이터 대신 왜 이것을 골랐는지
- [MQSim 코드 분석](/ftl-visual-simulator/reference/mqsim-code-analysis/) — 코드를 **구조**와 **흐름** 두 갈래로 정리
  - [큰 그림](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/) — 그림 위주로 보는 MQSim ( [계층 구조](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/architecture/) · [요청의 길](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/request-path/) · [플래시와 주소](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/flash-and-addresses/) · [FTL 부품](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/ftl-parts/) · [이벤트 엔진](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/event-engine/) · [개념 ↔ 파라미터](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/concept-mapping/) · [알려진 한계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/known-limits/) )
  - [튜토리얼](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/) — `./MQSim` 실행부터 함수 호출을 따라가는 11단계, FTL 중심
  - [쓰기 전에 읽으면 페이지가 소비되는 이유](/ftl-visual-simulator/reference/mqsim-code-analysis/read-before-write/) — 매핑 없는 주소를 읽을 때 일어나는 일
- [Code Change](/ftl-visual-simulator/reference/code-change/) — 처음 가져온 원본과 지금 엔진의 모든 차이
  - [버그 목록](/ftl-visual-simulator/reference/code-change/bug-list/) — 원본에서 찾아 고친 버그 28개
  - [튜닝된 코드](/ftl-visual-simulator/reference/code-change/tweaked-code/) — 버그는 아니지만 화면 규모에 맞게 일부러 바꾼 곳
  - [원본 MQSim 대비 변경 사항](/ftl-visual-simulator/reference/code-change/upstream-diff/) — 종류별로 정리한 전체 비교
- [Evaluation Board](/ftl-visual-simulator/reference/evaluation-board/) — 실제 평가 보드에서 FTL 을 돌려 보는 방법 논의
- [WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/) — WASM 이 뭔지, em++ 가 뭔지, 왜 필요한지
- [프론트엔드 스택 입문 (Vite · React · TS)](/ftl-visual-simulator/reference/frontend-stack/) — 화면 쪽 구현 도구 설명

<div style="margin-top: 60px;"></div>

## 관련 문서

- [개발 동기/목표](/ftl-visual-simulator/motivation-goals/)
- [개발 계획](/ftl-visual-simulator/plan/)
