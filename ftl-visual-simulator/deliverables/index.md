---
layout: default
title: 개발 산출물
permalink: /ftl-visual-simulator/deliverables/
---
# 개발 산출물

FTL 시각화 시뮬레이터를 실제로 만들어가면서 나오는 산출물( 화면 설계, 빌드 결과, 배포본 등 )을 모아두는 카테고리.

**코드 저장소** : [github.com/jonghoon-ryu/ftl-visual-simulator-app](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — Vite+React+TS 앱과, MIT 라이선스인 [MQSim](https://github.com/CMU-SAFARI/MQSim) 소스를 `engine/mqsim` 아래 vendoring 해서 WASM 으로 컴파일한 엔진이 올라가 있음( 저장소 이름은 원래 `ftl-visual-simulator` 였으나, 블로그의 `/ftl-visual-simulator/*` 문서 경로와 GitHub Pages URL 이 충돌해서 9/6 에 변경 — [시뮬레이터 실행](/ftl-visual-simulator/run-simulator/) 참고 ).

**배포된 시뮬레이터** : [시뮬레이터 실행](/ftl-visual-simulator/run-simulator/) 페이지에서 바로 열어볼 수 있음 — `main` 에 push 될 때마다 자동 배포.

<div style="margin-top: 60px;"></div>

## 하위 문서

- [Visual Simulator](/ftl-visual-simulator/deliverables/visual-simulator/) — 실제로 만들어지는 WASM 엔진 + 웹 UI 산출물

<div style="margin-top: 60px;"></div>

## 관련 문서

- [개발 동기/목표](/ftl-visual-simulator/motivation-goals/)
- [개발 계획](/ftl-visual-simulator/plan/)
