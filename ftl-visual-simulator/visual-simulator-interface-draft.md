---
layout: default
title: Visual Simulator Interface (초안)
permalink: /ftl-visual-simulator/visual-simulator-interface-draft/
---
<style>
.sim-mockup {
  font-family: 'SF Mono', 'Consolas', 'Menlo', monospace;
  font-size: 12.5px;
  background: #1c1e26;
  color: #d7dae0;
  border-radius: 10px;
  overflow: hidden;
  box-shadow: 0 4px 18px rgba(0,0,0,0.25);
  margin: 1.5rem 0;
}
.sim-toolbar {
  display: flex;
  justify-content: space-between;
  align-items: center;
  flex-wrap: wrap;
  gap: 10px;
  padding: 10px 14px;
  background: #23263080;
  border-bottom: 1px solid #33374a;
}
.sim-presets button, .sim-playback button {
  font-family: inherit;
  font-size: 12px;
  background: #2d3142;
  color: #d7dae0;
  border: 1px solid #3e4358;
  border-radius: 6px;
  padding: 5px 10px;
  margin-right: 6px;
  cursor: default;
}
.sim-presets button.active {
  background: #4a6cf7;
  border-color: #4a6cf7;
  color: #fff;
}
.sim-playback {
  display: flex;
  align-items: center;
  gap: 8px;
  color: #9aa0b0;
}
.sim-speed-track {
  width: 80px;
  height: 4px;
  background: #3e4358;
  border-radius: 2px;
  position: relative;
  display: inline-block;
}
.sim-speed-track::after {
  content: "";
  position: absolute;
  left: 40%;
  top: -4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #4a6cf7;
}
.sim-body {
  display: flex;
  gap: 0;
  flex-wrap: wrap;
}
.sim-grid-panel {
  flex: 1 1 480px;
  padding: 14px;
  border-right: 1px solid #33374a;
}
.sim-panel-title {
  font-size: 11px;
  text-transform: uppercase;
  letter-spacing: 0.06em;
  color: #8a90a4;
  margin-bottom: 8px;
}
.sim-caption {
  background: #262a3a;
  border-left: 3px solid #4a6cf7;
  padding: 8px 10px;
  border-radius: 4px;
  font-size: 12px;
  color: #c7cbe0;
  margin-bottom: 12px;
}
.grid-row {
  display: flex;
  align-items: center;
  gap: 6px;
  margin-bottom: 3px;
}
.row-label {
  width: 54px;
  font-size: 10.5px;
  color: #7d8296;
  flex-shrink: 0;
}
.row-cells {
  display: flex;
  gap: 2px;
}
.cell {
  width: 20px;
  height: 20px;
  border-radius: 3px;
  display: flex;
  align-items: center;
  justify-content: center;
  font-size: 9px;
  font-weight: 700;
  color: #1c1e26;
}
.cell.valid { background: #4fd18b; }
.cell.invalid { background: #f16d75; color: #3a0e10; }
.cell.free { background: #383c4d; color: #383c4d; }
.cell.moving { background: #f5b942; animation: none; }
.sim-legend {
  display: flex;
  flex-wrap: wrap;
  gap: 14px;
  margin-top: 10px;
  font-size: 11px;
  color: #9aa0b0;
}
.sim-legend span { display: inline-flex; align-items: center; gap: 5px; }
.swatch { width: 12px; height: 12px; border-radius: 3px; display: inline-block; }
.swatch.valid { background: #4fd18b; }
.swatch.invalid { background: #f16d75; }
.swatch.free { background: #383c4d; }
.swatch.moving { background: #f5b942; }
.sim-sidebar {
  flex: 1 1 260px;
  display: flex;
  flex-direction: column;
}
.sim-panel {
  padding: 12px 14px;
  border-bottom: 1px solid #33374a;
}
.mini-table {
  width: 100%;
  border-collapse: collapse;
  font-size: 11px;
}
.mini-table th, .mini-table td {
  padding: 3px 6px;
  text-align: left;
  border-bottom: 1px solid #2d3142;
  color: #c7cbe0;
}
.mini-table th { color: #7d8296; font-weight: 500; }
.param-row {
  margin-bottom: 10px;
}
.param-label {
  display: flex;
  justify-content: space-between;
  font-size: 11.5px;
  color: #c7cbe0;
  margin-bottom: 4px;
}
.param-hint {
  font-size: 10px;
  color: #7d8296;
  margin-top: 2px;
}
.param-slider {
  height: 4px;
  background: #3e4358;
  border-radius: 2px;
  position: relative;
}
.param-slider::after {
  content: "";
  position: absolute;
  top: -4px;
  width: 12px;
  height: 12px;
  border-radius: 50%;
  background: #4a6cf7;
}
.param-slider.p1::after { left: 30%; }
.param-slider.p2::after { left: 55%; }
.param-slider.p3::after { left: 20%; }
.param-select {
  font-size: 11px;
  background: #2d3142;
  border: 1px solid #3e4358;
  color: #d7dae0;
  border-radius: 4px;
  padding: 4px 8px;
  display: inline-block;
}
.stat-row {
  display: flex;
  justify-content: space-between;
  align-items: baseline;
  margin-bottom: 8px;
}
.stat-value {
  font-size: 15px;
  font-weight: 700;
  color: #fff;
}
.stat-hint {
  font-size: 10px;
  color: #7d8296;
}
.sim-log {
  padding: 12px 14px;
  max-height: 140px;
  overflow: hidden;
}
.log-entry {
  font-size: 11.5px;
  color: #c7cbe0;
  padding: 3px 0;
  border-bottom: 1px dashed #2d3142;
}
.log-time { color: #7d8296; margin-right: 8px; }
</style>

# Visual Simulator Interface (초안)

실제 코드는 아직 한 줄도 없다. 이건 Session 3(설계)에서 다룰 내용을 미리 그림으로 그려본 **레이아웃 초안**이다 — 화면 구성에 대한 의견을 먼저 듣고 싶어서 만들었다.

<div style="margin-top: 40px;"></div>

## 전체 화면 mockup

<div class="sim-mockup">
  <div class="sim-toolbar">
    <div class="sim-presets">
      <button>매핑 기본</button><button class="active">GC 시연</button><button>마모평준화 시연</button>
    </div>
    <div class="sim-playback">
      <button>⏮</button><button>⏸</button><button>⏭</button>
      <span>속도</span><span class="sim-speed-track"></span><span>1×</span>
    </div>
  </div>
  <div class="sim-body">
    <div class="sim-grid-panel">
      <div class="sim-panel-title">Flash Array — Block × Page</div>
      <div class="sim-caption">🔶 Block 2 가 꽉 차서 정리를 시작해요 — 유효한 페이지 4개를 새 block(5)으로 옮기는 중 (GC)</div>
      <div class="grid-row"><div class="row-label">Block 0</div><div class="row-cells"><div class="cell valid" title="Block 0 / Page 0 — valid">V</div><div class="cell valid" title="Block 0 / Page 1 — valid">V</div><div class="cell invalid" title="Block 0 / Page 2 — invalid">X</div><div class="cell valid" title="Block 0 / Page 3 — valid">V</div><div class="cell invalid" title="Block 0 / Page 4 — invalid">X</div><div class="cell valid" title="Block 0 / Page 5 — valid">V</div><div class="cell valid" title="Block 0 / Page 6 — valid">V</div><div class="cell invalid" title="Block 0 / Page 7 — invalid">X</div><div class="cell valid" title="Block 0 / Page 8 — valid">V</div><div class="cell valid" title="Block 0 / Page 9 — valid">V</div><div class="cell valid" title="Block 0 / Page 10 — valid">V</div><div class="cell valid" title="Block 0 / Page 11 — valid">V</div><div class="cell valid" title="Block 0 / Page 12 — valid">V</div><div class="cell free" title="Block 0 / Page 13 — free"></div><div class="cell valid" title="Block 0 / Page 14 — valid">V</div><div class="cell valid" title="Block 0 / Page 15 — valid">V</div></div></div>
      <div class="grid-row"><div class="row-label">Block 1</div><div class="row-cells"><div class="cell invalid" title="Block 1 / Page 0 — invalid">X</div><div class="cell free" title="Block 1 / Page 1 — free"></div><div class="cell invalid" title="Block 1 / Page 2 — invalid">X</div><div class="cell valid" title="Block 1 / Page 3 — valid">V</div><div class="cell free" title="Block 1 / Page 4 — free"></div><div class="cell valid" title="Block 1 / Page 5 — valid">V</div><div class="cell free" title="Block 1 / Page 6 — free"></div><div class="cell valid" title="Block 1 / Page 7 — valid">V</div><div class="cell valid" title="Block 1 / Page 8 — valid">V</div><div class="cell valid" title="Block 1 / Page 9 — valid">V</div><div class="cell valid" title="Block 1 / Page 10 — valid">V</div><div class="cell free" title="Block 1 / Page 11 — free"></div><div class="cell valid" title="Block 1 / Page 12 — valid">V</div><div class="cell invalid" title="Block 1 / Page 13 — invalid">X</div><div class="cell invalid" title="Block 1 / Page 14 — invalid">X</div><div class="cell valid" title="Block 1 / Page 15 — valid">V</div></div></div>
      <div class="grid-row"><div class="row-label">Block 2</div><div class="row-cells"><div class="cell valid" title="Block 2 / Page 0 — valid">V</div><div class="cell valid" title="Block 2 / Page 1 — valid">V</div><div class="cell valid" title="Block 2 / Page 2 — valid">V</div><div class="cell valid" title="Block 2 / Page 3 — valid">V</div><div class="cell valid" title="Block 2 / Page 4 — valid">V</div><div class="cell moving" title="Block 2 / Page 5 — 이동 중">→</div><div class="cell moving" title="Block 2 / Page 6 — 이동 중">→</div><div class="cell invalid" title="Block 2 / Page 7 — invalid">X</div><div class="cell moving" title="Block 2 / Page 8 — 이동 중">→</div><div class="cell moving" title="Block 2 / Page 9 — 이동 중">→</div><div class="cell invalid" title="Block 2 / Page 10 — invalid">X</div><div class="cell invalid" title="Block 2 / Page 11 — invalid">X</div><div class="cell invalid" title="Block 2 / Page 12 — invalid">X</div><div class="cell invalid" title="Block 2 / Page 13 — invalid">X</div><div class="cell invalid" title="Block 2 / Page 14 — invalid">X</div><div class="cell invalid" title="Block 2 / Page 15 — invalid">X</div></div></div>
      <div class="grid-row"><div class="row-label">Block 3</div><div class="row-cells"><div class="cell invalid" title="Block 3 / Page 0 — invalid">X</div><div class="cell valid" title="Block 3 / Page 1 — valid">V</div><div class="cell free" title="Block 3 / Page 2 — free"></div><div class="cell valid" title="Block 3 / Page 3 — valid">V</div><div class="cell valid" title="Block 3 / Page 4 — valid">V</div><div class="cell free" title="Block 3 / Page 5 — free"></div><div class="cell valid" title="Block 3 / Page 6 — valid">V</div><div class="cell invalid" title="Block 3 / Page 7 — invalid">X</div><div class="cell valid" title="Block 3 / Page 8 — valid">V</div><div class="cell invalid" title="Block 3 / Page 9 — invalid">X</div><div class="cell free" title="Block 3 / Page 10 — free"></div><div class="cell invalid" title="Block 3 / Page 11 — invalid">X</div><div class="cell free" title="Block 3 / Page 12 — free"></div><div class="cell valid" title="Block 3 / Page 13 — valid">V</div><div class="cell invalid" title="Block 3 / Page 14 — invalid">X</div><div class="cell invalid" title="Block 3 / Page 15 — invalid">X</div></div></div>
      <div class="grid-row"><div class="row-label">Block 4</div><div class="row-cells"><div class="cell invalid" title="Block 4 / Page 0 — invalid">X</div><div class="cell invalid" title="Block 4 / Page 1 — invalid">X</div><div class="cell free" title="Block 4 / Page 2 — free"></div><div class="cell free" title="Block 4 / Page 3 — free"></div><div class="cell invalid" title="Block 4 / Page 4 — invalid">X</div><div class="cell invalid" title="Block 4 / Page 5 — invalid">X</div><div class="cell valid" title="Block 4 / Page 6 — valid">V</div><div class="cell invalid" title="Block 4 / Page 7 — invalid">X</div><div class="cell invalid" title="Block 4 / Page 8 — invalid">X</div><div class="cell free" title="Block 4 / Page 9 — free"></div><div class="cell free" title="Block 4 / Page 10 — free"></div><div class="cell valid" title="Block 4 / Page 11 — valid">V</div><div class="cell valid" title="Block 4 / Page 12 — valid">V</div><div class="cell invalid" title="Block 4 / Page 13 — invalid">X</div><div class="cell valid" title="Block 4 / Page 14 — valid">V</div><div class="cell invalid" title="Block 4 / Page 15 — invalid">X</div></div></div>
      <div class="grid-row"><div class="row-label">Block 5 (GC 대상)</div><div class="row-cells"><div class="cell free" title="Block 5 / Page 0 — free"></div><div class="cell free" title="Block 5 / Page 1 — free"></div><div class="cell free" title="Block 5 / Page 2 — free"></div><div class="cell free" title="Block 5 / Page 3 — free"></div><div class="cell free" title="Block 5 / Page 4 — free"></div><div class="cell free" title="Block 5 / Page 5 — free"></div><div class="cell free" title="Block 5 / Page 6 — free"></div><div class="cell valid" title="Block 5 / Page 7 — 방금 이동해옴">V</div><div class="cell free" title="Block 5 / Page 8 — free"></div><div class="cell free" title="Block 5 / Page 9 — free"></div><div class="cell free" title="Block 5 / Page 10 — free"></div><div class="cell valid" title="Block 5 / Page 11 — 방금 이동해옴">V</div><div class="cell free" title="Block 5 / Page 12 — free"></div><div class="cell valid" title="Block 5 / Page 13 — 방금 이동해옴">V</div><div class="cell free" title="Block 5 / Page 14 — free"></div><div class="cell free" title="Block 5 / Page 15 — free"></div></div></div>
      <div class="sim-legend">
        <span><span class="swatch valid"></span>valid ( 유효한 데이터 )</span>
        <span><span class="swatch invalid"></span>invalid ( 지워질 예정 )</span>
        <span><span class="swatch free"></span>free ( 빈 페이지 )</span>
        <span><span class="swatch moving"></span>GC 로 이동 중</span>
      </div>
    </div>
    <div class="sim-sidebar">
      <div class="sim-panel">
        <div class="sim-panel-title">매핑 테이블 ( 일부 )</div>
        <table class="mini-table">
          <tr><th>LPA</th><th>PPA</th><th>상태</th></tr>
          <tr><td>0x0F2</td><td>B0·P5</td><td>valid</td></tr>
          <tr><td>0x0F3</td><td>B5·P7</td><td>방금 이동</td></tr>
          <tr><td>0x0F4</td><td>B0·P4</td><td style="color:#f16d75">invalid</td></tr>
          <tr><td>0x0F5</td><td>B3·P1</td><td>valid</td></tr>
        </table>
      </div>
      <div class="sim-panel">
        <div class="sim-panel-title">파라미터</div>
        <div class="param-row">
          <div class="param-label"><span>Over-provisioning</span><span>7%</span></div>
          <div class="param-slider p1"></div>
          <div class="param-hint">여유 공간을 더 두면 GC 가 덜 급해져요</div>
        </div>
        <div class="param-row">
          <div class="param-label"><span>GC 임계값</span><span>5%</span></div>
          <div class="param-slider p2"></div>
          <div class="param-hint">빈 block 이 이 아래로 떨어지면 GC 시작</div>
        </div>
        <div class="param-row">
          <div class="param-label"><span>매핑 방식</span></div>
          <span class="param-select">Page-level ▾</span>
          <div class="param-hint">Hybrid 로 바꾸면 log-block 방식으로 동작</div>
        </div>
      </div>
      <div class="sim-panel">
        <div class="sim-panel-title">통계</div>
        <div class="stat-row"><span>WAF</span><span class="stat-value">1.8×</span></div>
        <div class="stat-hint" style="margin-top:-6px; margin-bottom:8px;">1 번 쓰려고 실제로는 1.8 번 write 함 — 낮을수록 좋음</div>
        <div class="stat-row"><span>Valid page 비율</span><span class="stat-value">62%</span></div>
        <div class="stat-hint" style="margin-top:-6px; margin-bottom:8px;">전체 페이지 중 아직 쓸모있는 비율</div>
        <div class="stat-row"><span>GC 실행 횟수</span><span class="stat-value">14</span></div>
      </div>
    </div>
  </div>
  <div class="sim-log">
    <div class="sim-panel-title">이벤트 로그</div>
    <div class="log-entry"><span class="log-time">12:03:41</span>Block 2 의 valid page 4개를 Block 5 로 이동 시작 (GC)</div>
    <div class="log-entry"><span class="log-time">12:03:40</span>LPA 0x0F4 에 새 데이터가 쓰이면서 기존 페이지가 invalid 로 표시됨</div>
    <div class="log-entry"><span class="log-time">12:03:38</span>빈 block 비율이 5% 아래로 떨어져 GC 트리거됨</div>
  </div>
</div>

<div style="margin-top: 20px;"></div>

## 각 영역 설명

- **상단 툴바** : 개념별 프리셋 버튼( 매핑 기본 / GC 시연 / 마모평준화 시연 )과 재생 컨트롤( step / play·pause / 속도 ). 초심자는 프리셋만 눌러도 각 개념을 바로 볼 수 있음
- **왼쪽 — Flash grid** : block × page 격자, 상태별 색상( valid/invalid/free ) + GC 로 이동 중인 페이지는 별도 색. 상단의 캡션이 "지금 무슨 일이 일어나는지" 쉬운 말로 설명
- **오른쪽 — 매핑 테이블 / 파라미터 / 통계 패널** : 매핑 테이블은 LPA→PPA 일부만 스크롤 형태로, 파라미터는 슬라이더 밑에 쉬운 설명 한 줄씩, 통계도 숫자만이 아니라 "왜 중요한지" 캡션 포함
- **하단 — 이벤트 로그** : hook 이벤트를 그대로 나열하지 않고 자연어 문장으로 변환해서 표시

이 배치와 색상, 톤( 다크 테마 )은 전부 초안이라 바뀔 수 있다.

<div style="margin-top: 60px;"></div>

## 참고

- 이 초안의 근거가 된 설계 결정 : [통합 계획 (Plan)](/ftl-visual-simulator/plan/) Session 3
- 실제 구현 시 데이터 출처 : MQSim WASM 모듈의 hook 이벤트 / `getState()` — [MQSim 코드 분석](/ftl-visual-simulator/mqsim-code-analysis/)
