---
layout: default
title: 참고 자료
permalink: /ftl-visual-simulator/reference/
---
# 참고 자료

시뮬레이터를 만드는 데 필요한 배경 지식을 모아두는 카테고리 — 엔진으로 쓰는 MQSim 자체에 대한 문서, 그리고 WASM/em++ 처럼 이 프로젝트에서 새로 등장하는 도구·개념에 대한 설명.

<div style="margin-top: 60px;"></div>

## 하위 문서

- [MQSim](/ftl-visual-simulator/reference/mqsim/) — 엔진으로 그대로 가져다 쓰는 MQSim 에 대한 문서 모음( 하위 문서 : [MQSim 개요](/ftl-visual-simulator/reference/mqsim/overview/), [MQSim 코드 분석](/ftl-visual-simulator/reference/mqsim/code-analysis/) → [MQSim 개괄](/ftl-visual-simulator/reference/mqsim/code-analysis/overview/) / [FTL 개념 ↔ 파라미터·모듈 대응](/ftl-visual-simulator/reference/mqsim/code-analysis/concept-mapping/) )
- [WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/) — WASM 이 뭔지, em++ 가 뭔지, 그리고 `main.cpp` 를 라이브러리로 바꾸는 작업을 포함해 앞으로 진행할 작업들이 왜 필요한지에 대한 설명
- [프론트엔드 스택 입문 (Vite · React · TS)](/ftl-visual-simulator/reference/frontend-stack/) — Vite, React, TypeScript, scaffold 가 각각 뭔지, 그리고 화면 쪽 구현에 왜 필요한지에 대한 설명
- [버그 목록](/ftl-visual-simulator/reference/bug-list/) — 이 프로젝트를 진행하며 실제 MQSim 원본에서 찾아낸 버그들을 모아두는 카테고리( 하위 문서 : [버그 목록표](/ftl-visual-simulator/reference/bug-list/table/)(전체 요약 표) / [MQSim 버그 헌트](/ftl-visual-simulator/reference/bug-list/mqsim-bug-hunt/) / [마모 평준화 버그와 동작 변경](/ftl-visual-simulator/reference/bug-list/wl-bug-deviation/) / [재구성 크래시 버그](/ftl-visual-simulator/reference/bug-list/reconfigure-crash-bug/) / [초기화되지 않은 Bandwidth 필드 버그](/ftl-visual-simulator/reference/bug-list/bandwidth-divide-by-zero-bug/) / [정적 마모 평준화 설정 누락 버그](/ftl-visual-simulator/reference/bug-list/wl-threshold-not-wired-bug/) / [잘못된 inline 선언 버그](/ftl-visual-simulator/reference/bug-list/inline-linkage-bug/) )

<div style="margin-top: 60px;"></div>

## 관련 문서

- [개발 동기/목표](/ftl-visual-simulator/motivation-goals/)
- [개발 계획](/ftl-visual-simulator/plan/)
- [개발 산출물](/ftl-visual-simulator/deliverables/)
