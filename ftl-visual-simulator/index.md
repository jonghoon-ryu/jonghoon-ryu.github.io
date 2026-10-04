---
layout: default
title: FTL Visual Simulator
permalink: /ftl-visual-simulator/
---
# FTL Visual Simulator

MQSim 엔진을 WASM 으로 그대로 컴파일해서, 웹 기반으로 동작하고 사용자가 파라미터를 직접 조절할 수 있는 FTL(Flash Translation Layer) 시각화 시뮬레이터를 만드는 프로젝트. 초심자도 화면만 보고 매핑 · GC · 마모평준화를 익힐 수 있는 것이 목표다. 아래는 이 프로젝트의 하위 카테고리 요약.

<div style="margin-top: 60px;"></div>

## 하위 문서

- [개발 동기/목표](/ftl-visual-simulator/motivation-goals/) — 왜 이 프로젝트를 시작했는지, 목표 7가지, 진행/작업 방식
- [개발 계획](/ftl-visual-simulator/plan/) — 계획 대비 실제 진행, 타임라인, 계획에 없던 일, 원래 계획(9/4)
- [참고 자료](/ftl-visual-simulator/reference/) — 시뮬레이터를 만들고 쓰는 데 필요한 배경 지식
  - [MQSim](/ftl-visual-simulator/reference/mqsim/) — 엔진으로 쓰는 MQSim 이 무엇이고 왜 골랐는가
  - [MQSim 코드 분석](/ftl-visual-simulator/reference/mqsim-code-analysis/) — [큰 그림](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/)(그림 위주 구조 설명)과 [튜토리얼](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/)(`./MQSim` 실행부터 FTL 까지 함수 호출을 따라가기)
  - [Code Change](/ftl-visual-simulator/reference/code-change/) — 원본 MQSim 에서 바꾼 것: [버그 목록](/ftl-visual-simulator/reference/code-change/bug-list/) · [튜닝된 코드](/ftl-visual-simulator/reference/code-change/tweaked-code/) · [원본 대비 변경 사항](/ftl-visual-simulator/reference/code-change/upstream-diff/)
  - [Evaluation Board](/ftl-visual-simulator/reference/evaluation-board/) — 실제 하드웨어에서 FTL 을 돌려 보기 위한 평가 보드 논의
  - [WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/) · [프론트엔드 스택 입문](/ftl-visual-simulator/reference/frontend-stack/)
- [시뮬레이터 실행](/ftl-visual-simulator/run-simulator/) — 지금 배포된 시뮬레이터를 브라우저에서 바로 열어보기
