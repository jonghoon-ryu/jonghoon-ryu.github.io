---
layout: default
title: MQSim
permalink: /ftl-visual-simulator/reference/mqsim/
---
# MQSim

이 프로젝트가 엔진으로 그대로 가져다 쓰는 MQSim 에 대한 문서 모음.

<div style="margin-top: 60px;"></div>

## 하위 문서

- [MQSim 개요](/ftl-visual-simulator/reference/mqsim/overview/) — MQSim 이 뭔지, 다른 오픈소스 SSD 시뮬레이터와 비교해서 왜 이걸 골랐는지
- [MQSim 코드 분석](/ftl-visual-simulator/reference/mqsim/code-analysis/) — 코드 구조, 클래스별 역할, 동작 방식, 테스트 방식, FTL 개념 ↔ 파라미터·모듈 대응 등을 담은 하위 문서 모음
- [쓰기 전에 읽으면 페이지가 소비되는 이유](/ftl-visual-simulator/reference/mqsim/read-before-write/) — 매핑 없는 주소를 읽으면 MQSim 이 그 자리에서 페이지를 예약하는 이유와, 이 프로젝트가 Read 비율 UI 를 없앤 이유
- [MQSim 2일 학습 가이드](/ftl-visual-simulator/reference/mqsim/study-guide/) — 원본 MQSim(90b0fb1) 코드를 읽지 않고도 그림으로 핵심 개념을 익히는 5시간 × 2일 코스 (Day 1: 뼈대·호스트·캐시, Day 2: FTL·GC·스케줄러·플래시)

<div style="margin-top: 60px;"></div>

## 관련 문서

- [WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/) — MQSim 을 그대로 컴파일해서 쓰는 이유와 방법
- [Visual Simulator Layout (초안)](/ftl-visual-simulator/deliverables/visual-simulator/layout-draft/)
- [개발 계획](/ftl-visual-simulator/plan/)( [MQSim 코드 분석 계획](/ftl-visual-simulator/plan/code-analysis-plan/) 하위 문서 포함 )
