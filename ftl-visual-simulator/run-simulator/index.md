---
layout: default
title: 시뮬레이터 실행
permalink: /ftl-visual-simulator/run-simulator/
---
<style>
.run-sim-cta {
  display: block;
  margin: 1.5rem 0;
  padding: 1.1rem 1.4rem;
  border-radius: 10px;
  background: #2f6fd6;
  color: #fff !important;
  text-decoration: none;
  font-weight: 700;
  font-size: 1.05rem;
  text-align: center;
}
.run-sim-cta:hover {
  background: #24589f;
}
</style>

# 시뮬레이터 실행

지금까지 만든 FTL 시각화 시뮬레이터를 브라우저에서 직접 열어볼 수 있는 링크. `main` 브랜치에 코드가 머지될 때마다 자동으로 다시 배포되므로, 항상 최신 상태를 보여준다.

<a class="run-sim-cta" href="https://jonghoon-ryu.github.io/ftl-visual-simulator-app/" target="_blank" rel="noopener">▶ 시뮬레이터 열기 (jonghoon-ryu.github.io/ftl-visual-simulator-app)</a>

<div style="margin-top: 40px;"></div>

## 지금 상태

**아직 완성된 시뮬레이터가 아니다** — [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) Session 7("시각화")이 진행 중인 단계라, 화면에 보이는 것 중 일부는 실제 WASM 엔진과 아직 연결되지 않은 정적 목업(가짜 데이터)이다. Session 7 이 슬라이스 단위로 진행되면서 하나씩 실제 데이터로 바뀌어 간다:

- 실제 MQSim WASM 엔진 로딩 — 완료
- 매핑 테이블 뷰어 — 진행 중
- 이벤트 로그, 재생 컨트롤, flash grid, 통계 패널 — 아직

이 페이지는 그 진행 상황과 무관하게 항상 "지금 배포된 최신 버전"으로 연결된다.

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [개발 산출물](/ftl-visual-simulator/deliverables/) — 화면 설계, 코드 저장소 등
- [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) — Session 7 진행 상황
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — 실제 코드
