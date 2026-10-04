---
layout: default
title: MQSim 코드 분석
permalink: /ftl-visual-simulator/reference/mqsim-code-analysis/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# MQSim 코드 분석

엔진으로 쓰는 MQSim 의 코드를 **구조(큰 그림)** 와 **흐름(튜토리얼)** 두 갈래로 정리한 문서 모음이다. 모든 줄 번호와 코드 발췌는 MQSim 원본 `51f0f2d` 커밋 기준이다.


<div style="margin-top: 60px;"></div>

## 하위 문서

- [큰 그림](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/) — 코드를 열기 전에 머리에 넣을 지도. 그림 위주.
  - [계층 구조와 모듈 지도](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/architecture/) · [요청 하나가 지나가는 길](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/request-path/) · [플래시 구조와 주소 체계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/flash-and-addresses/) · [FTL 의 부품들과 자료구조](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/ftl-parts/) · [이벤트 엔진과 시간](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/event-engine/) · [FTL 개념 ↔ 파라미터·모듈 대응](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/concept-mapping/) · [원본의 알려진 한계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/known-limits/)
- [튜토리얼](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/) — `./MQSim` 실행부터 함수 호출을 따라가며 FTL 을 이해하는 11단계.
- [쓰기 전에 읽으면 페이지가 소비되는 이유](/ftl-visual-simulator/reference/mqsim-code-analysis/read-before-write/) — 매핑 없는 주소를 읽으면 MQSim 이 그 자리에서 페이지를 예약하는 이유와, 이 프로젝트가 Read 비율 UI 를 없앤 이유.


<div style="margin-top: 60px;"></div>

## 어디서부터 읽을까

| 상황 | 추천 |
|---|---|
| FTL 이 처음이다 | [큰 그림](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/) → [튜토리얼](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/) 순서로 |
| 코드를 이미 열어 놓았다 | [튜토리얼](/ftl-visual-simulator/reference/mqsim-code-analysis/tutorial/) 을 바로 시작해도 된다 |
| 특정 설정이 어디에 쓰이는지만 알고 싶다 | [FTL 개념 ↔ 파라미터·모듈 대응](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/concept-mapping/) |
| 원본을 믿어도 되는지 궁금하다 | [원본의 알려진 한계](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/known-limits/) · [Code Change](/ftl-visual-simulator/reference/code-change/) |


<div style="margin-top: 60px;"></div>

## 관련 문서

- [MQSim](/ftl-visual-simulator/reference/mqsim/) — MQSim 이 무엇이고 왜 골랐는가
- [Code Change](/ftl-visual-simulator/reference/code-change/) — 이 프로젝트가 원본에서 바꾼 것
