---
layout: default
title: 개발 계획
permalink: /ftl-visual-simulator/plan/
---
# 개발 계획

FTL 시각화 시뮬레이터를 실제로 만들어가는 일정과 세션별 작업 내용을 담은 카테고리.

<div style="margin-top: 60px;"></div>

## 요약

- **1차 완성 목표일 : 2026-10-11**, 9/4(금) 시작, 주말( 토/일 ) + 공휴일( 10/5, 10/9 ) 기준 하루 5시간씩. 리뷰/수정 버퍼는 10/17~10/18, 10/24~10/25.
- **12개 핵심 세션 + 4개 버퍼 세션(13~16)**, 세션 2는 9/5~9/6 이틀로 확장 진행됨.
- **7단계 Phase 구성** : Phase 1( FTL 개념 ) → Phase 2( MQSim 개괄 ) → Phase 3( 설계 ) → Phase 4( 시뮬레이션 엔진 — 매핑/GC/마모평준화 ) → Phase 5( 시각화 ) → Phase 6( 인터랙션 ) → Phase 7( 마무리·배포 ).
- **엔진은 MQSim C++ 원본을 Emscripten 으로 WASM 컴파일**해서 그대로 쓰고, hook 을 심어 시각화 — 자체 TS 재구현이 아님.
- **구현은 전부 Claude 담당**, Ryu 는 방향 결정·리뷰·매 세션 FTL 개념/MQSim 소스코드 학습을 담당.
- **확장 목표(시간이 남으면, 13~16번 버퍼)** : Cost-Benefit GC 정책 직접 구현, Hybrid(log-block) 매핑 직접 구현( `Address_Mapping_Unit_Hybrid.cpp` 가 빈 스텁으로 확인됨 ), GTest/GMock 테스트 스위트.
- **초심자 학습 환경**이 설계 단계부터 목표 — 쉬운 용어 툴팁, 개념별 프리셋( 매핑 기본/GC 시연/마모평준화 시연 ), 평범한 말 설명 패널.

<div style="margin-top: 60px;"></div>

## 하위 문서

- [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) — 날짜표, 세션별 상세( Ryu 가 할 일 / Claude 가 할 일 ), 페이싱·리스크 노트
- [Claude 구현 작업 상세](/ftl-visual-simulator/plan/implementation/) — Claude 가 할 일을 컴포넌트/기능 단위로 다시 묶어 정확한 파일·함수명까지 상세히 기록
- [MQSim 코드 분석 계획](/ftl-visual-simulator/plan/code-analysis-plan/) — MQSim 소스코드를 처음부터 끝까지 읽는 16세션 커리큘럼
- [To do list](/ftl-visual-simulator/plan/todo-list/) — 세션 중 나중으로 미룬 자잘한 확인/처리 항목 모음
- [마모평준화 시연 연동 작업 기록](/ftl-visual-simulator/plan/wear-leveling-integration/) — 1차 완성 이후 "마모평준화 시연" 프리셋을 실제 엔진에 연동한 전체 과정(시행착오, 버그 발견, 최종 튜닝, 검증)

<div style="margin-top: 60px;"></div>

## 관련 문서

- [개발 동기/목표](/ftl-visual-simulator/motivation-goals/)
- [MQSim 코드 분석](/ftl-visual-simulator/reference/mqsim/code-analysis/)
- [개발 산출물](/ftl-visual-simulator/deliverables/)
