---
layout: default
title: FTL Visual Simulator
permalink: /ftl-visual-simulator/
---
# FTL 시각화 시뮬레이터 만들기

MQSim 엔진을 WASM 으로 그대로 컴파일해서, 웹 기반으로 동작하고 사용자가 파라미터를 직접 조절할 수 있는 FTL(Flash Translation Layer) 시각화 시뮬레이터를 만들어보자.

<div style="margin-top: 100px;"></div>

## 왜 이 프로젝트를 시작했나?

- MQSim 이라는 오픈소스 SSD 시뮬레이터가 있음 ( 논문 기반, C++ )
- 로그/통계 파일 기반이라 내부 동작( 매핑, GC, 마모 평준화 )을 직관적으로 이해하기 어려움
- FTL 개념을 눈으로 보면서 제대로 익히고 싶음
- 겸사겸사 웹 기반 인터랙티브 시각화 도구도 하나 만들어보고 싶음

<div style="margin-top: 100px;"></div>

## 목표

1. FTL 이 실제로 어떻게 동작하는지 제대로 이해하기 ( 주소 매핑, GC, 마모 평준화, bad block 관리 등 )
2. MQSim 엔진(WASM 컴파일)을 그대로 사용하는 웹 기반 시각화 시뮬레이터 제작
3. 사용자가 파라미터( 페이지 크기, 블록 수, Over-provisioning 비율, 매핑 방식, GC 정책 등 )를 직접 조절해 볼 수 있게 만들기
4. **2026-10-11 까지 1차 완성** → 직접 리뷰하고 필요하면 10/17~10/25 사이에 수정

<div style="margin-top: 100px;"></div>

## 작업 방식

- 9/4(금)를 시작일로 사용, 9/5(토)는 쉬는 날
- 이후 평일에는 원칙적으로 작업하지 않음 ( 가능하면 하되, 기본적으로 기대하지 않음 )
- 주말( 토/일 )과 공휴일( 10/5, 10/9 )에 하루 5시간씩 작업
- 9/12, 9/13 은 개인 사정으로 작업 불가
- 10/11 에 1차 완성본을 리뷰 → 10/17~10/18, 10/24~10/25 는 리뷰 후 수정용 버퍼로 남겨둠 ( 아래 계획에는 포함하지 않음 )

<div style="margin-top: 100px;"></div>

## 참고

- MQSim ( GitHub ): [github.com/CMU-SAFARI/MQSim](https://github.com/CMU-SAFARI/MQSim)
- 관련 배경 지식 : [OS 공부](/learning-cs/os/) 에서 다루는 페이지 매핑, 캐싱, 스케줄링 개념이 FTL 을 이해하는 데도 많이 겹침

<div style="margin-top: 100px;"></div>

## 진행 계획

- [일정 및 계획 (Plan)](/ftl-visual-simulator/plan/) — 9/4 ~ 10/11, 12세션 계획 ( 1차 완성 목표 )
