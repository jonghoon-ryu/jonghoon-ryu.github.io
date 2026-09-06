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
- [MQSim 버그 헌트](/ftl-visual-simulator/reference/mqsim-bug-hunt/) — WASM 빌드가 네이티브와 다른 결과를 내던 문제를 추적해서 찾아낸 MQSim 원본의 이식성 버그 4개와 수정 기록
- [마모 평준화 버그와 의도적 동작 변경](/ftl-visual-simulator/reference/wl-bug-deviation/) — static 마모 평준화 hook 작업 중 발견한 MQSim 원본의 로직 버그 2개 — 위 이식성 버그와 달리, 고치면 이 프로젝트가 upstream MQSim 과 의도적으로 다르게 동작하게 되는 경우라 별도로 기록
- [재구성 크래시 버그](/ftl-visual-simulator/reference/reconfigure-crash-bug/) — DRAM 캐시 대기열의 이중 소유권(use-after-free) 버그. 원본 CLI는 항상 완주 후에만 정리하기 때문에 절대 안 겪지만, 이 프로젝트처럼 일시정지·재구성 UI를 얹는 순간 실제 위험이 됨
- [초기화되지 않은 Bandwidth 필드 버그](/ftl-visual-simulator/reference/bandwidth-divide-by-zero-bug/) — Session 10 workload 컨트롤 작업 중 발견한 0 나누기 크래시. 네이티브 CLI로는 재현이 안 되는 WASM 전용 버그라 UBSan + Node.js 로 WASM 을 직접 재생하는 방식으로 원인을 밝힘
- [정적 마모 평준화 설정이 아예 전달되지 않던 버그](/ftl-visual-simulator/reference/wl-threshold-not-wired-bug/) — "마모평준화 시연"을 실제 엔진에 연동하려다 발견한 세 번째 마모 평준화 버그. `Static_Wearleveling_Threshold` 가 설정과 무관하게 항상 무시되고 있었고, 고친 뒤 이 프로젝트 최초로 static WL 을 실제로 발동시키는 데 성공함

<div style="margin-top: 60px;"></div>

## 관련 문서

- [개발 동기/목표](/ftl-visual-simulator/motivation-goals/)
- [개발 계획](/ftl-visual-simulator/plan/)
- [개발 산출물](/ftl-visual-simulator/deliverables/)
