---
layout: default
title: Visual Simulator Layout (초안)
permalink: /ftl-visual-simulator/deliverables/visual-simulator/layout-draft/
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

.wl-row { display: flex; align-items: center; gap: 10px; margin-bottom: 9px; }
.wl-label { width: 62px; font-size: 11px; color: #c7cbe0; flex-shrink: 0; }
.wl-track { flex: 1; height: 14px; background: #2d3142; border-radius: 4px; overflow: hidden; }
.wl-fill { height: 100%; border-radius: 4px; }
.wl-fill.cool { background: #4fd18b; }
.wl-fill.warm { background: #f5b942; }
.wl-fill.hot { background: #f16d75; }
.wl-count { width: 78px; text-align: right; font-size: 11px; color: #9aa0b0; flex-shrink: 0; }

.queue-row { display: flex; align-items: center; gap: 8px; margin-bottom: 7px; }
.queue-label { width: 40px; font-size: 11px; color: #9aa0b0; flex-shrink: 0; }
.queue-reqs { display: flex; gap: 3px; flex-wrap: wrap; }
.req-chip { width: 13px; height: 13px; border-radius: 3px; background: #4a6cf7; }
.req-chip.sata { background: #6a7085; }

.chip-row { display: flex; align-items: center; gap: 6px; margin-bottom: 4px; }
.chip-row-label { width: 32px; font-size: 10.5px; color: #7d8296; flex-shrink: 0; }
.chip-cell {
  width: 34px; height: 26px; border-radius: 4px;
  display: flex; align-items: center; justify-content: center;
  font-size: 10px; font-weight: 700; color: #1c1e26;
}
.chip-cell.idle { background: #383c4d; color: #7d8296; }
.chip-cell.read { background: #6ea8ff; }
.chip-cell.write { background: #b98cf0; }
.chip-cell.erase { background: #f5b942; }
.preset-block { margin-bottom: 46px; }
</style>

# Visual Simulator Layout (초안)

실제 코드는 아직 한 줄도 없다. 이건 Session 3(설계)에서 다룰 내용을 미리 그림으로 그려본 **레이아웃 초안**이다 — 화면 구성에 대한 의견을 먼저 듣고 싶어서 만들었다.

<div style="margin-top: 40px;"></div>

## 프리셋별 화면

프리셋 버튼을 누르면 이런 식으로 보이지 않을까 — 3가지 스냅샷.

<div class="preset-block">

### 프리셋 1 — 매핑 기본

막 시작한 상태. 몇 번 쓰기만 했고 아직 GC 는 필요 없다. 주소 매핑이라는 개념 자체에 집중할 수 있게 화면이 단순하다.

<div class="sim-mockup">
  <div class="sim-toolbar">
    <div class="sim-presets">
      <button class="active">매핑 기본</button><button>GC 시연</button><button>마모평준화 시연</button>
    </div>
    <div class="sim-playback">
      <button>⏮</button><button>⏸</button><button>⏭</button>
      <span>속도</span><span class="sim-speed-track"></span><span>1×</span>
    </div>
  </div>
  <div class="sim-body">
    <div class="sim-grid-panel">
      <div class="sim-panel-title">Flash Array — Block × Page</div>
      <div class="sim-caption">🔵 LPA 0x001 을 처음 썼어요 — 비어있던 Block 0 · Page 0 에 매핑되고, 매핑 테이블에 새 항목이 생겨요</div>
      <div class="grid-row"><div class="row-label">Block 0</div><div class="row-cells"><div class="cell valid" title="Block 0 / Page 0 — valid">V</div><div class="cell valid" title="Block 0 / Page 1 — valid">V</div><div class="cell valid" title="Block 0 / Page 2 — valid">V</div><div class="cell free" title="Block 0 / Page 3 — free"></div><div class="cell free" title="Block 0 / Page 4 — free"></div><div class="cell free" title="Block 0 / Page 5 — free"></div><div class="cell free" title="Block 0 / Page 6 — free"></div><div class="cell free" title="Block 0 / Page 7 — free"></div><div class="cell free" title="Block 0 / Page 8 — free"></div><div class="cell free" title="Block 0 / Page 9 — free"></div><div class="cell free" title="Block 0 / Page 10 — free"></div><div class="cell free" title="Block 0 / Page 11 — free"></div><div class="cell free" title="Block 0 / Page 12 — free"></div><div class="cell free" title="Block 0 / Page 13 — free"></div><div class="cell free" title="Block 0 / Page 14 — free"></div><div class="cell free" title="Block 0 / Page 15 — free"></div></div></div>
      <div class="grid-row"><div class="row-label">Block 1</div><div class="row-cells"><div class="cell free" title="Block 1 / Page 0 — free"></div><div class="cell free" title="Block 1 / Page 1 — free"></div><div class="cell free" title="Block 1 / Page 2 — free"></div><div class="cell free" title="Block 1 / Page 3 — free"></div><div class="cell free" title="Block 1 / Page 4 — free"></div><div class="cell free" title="Block 1 / Page 5 — free"></div><div class="cell free" title="Block 1 / Page 6 — free"></div><div class="cell free" title="Block 1 / Page 7 — free"></div><div class="cell free" title="Block 1 / Page 8 — free"></div><div class="cell free" title="Block 1 / Page 9 — free"></div><div class="cell free" title="Block 1 / Page 10 — free"></div><div class="cell free" title="Block 1 / Page 11 — free"></div><div class="cell free" title="Block 1 / Page 12 — free"></div><div class="cell free" title="Block 1 / Page 13 — free"></div><div class="cell free" title="Block 1 / Page 14 — free"></div><div class="cell free" title="Block 1 / Page 15 — free"></div></div></div>
      <div class="sim-legend">
        <span><span class="swatch valid"></span>valid ( 유효한 데이터 )</span>
        <span><span class="swatch free"></span>free ( 빈 페이지 )</span>
      </div>
    </div>
    <div class="sim-sidebar">
      <div class="sim-panel">
        <div class="sim-panel-title">매핑 테이블 ( 일부 )</div>
        <table class="mini-table">
          <tr><th>LPA</th><th>PPA</th><th>상태</th></tr>
          <tr><td>0x001</td><td>B0·P0</td><td>valid</td></tr>
          <tr><td>0x002</td><td>B0·P1</td><td>valid</td></tr>
          <tr><td>0x003</td><td>B0·P2</td><td>valid</td></tr>
        </table>
      </div>
      <div class="sim-panel">
        <div class="sim-panel-title">통계</div>
        <div class="stat-row"><span>WAF</span><span class="stat-value">1.0×</span></div>
        <div class="stat-hint" style="margin-top:-6px; margin-bottom:8px;">아직 재기록이 없어서 이상적인 값</div>
        <div class="stat-row"><span>GC 실행 횟수</span><span class="stat-value">0</span></div>
      </div>
    </div>
  </div>
</div>

</div>

<div class="preset-block">

### 프리셋 2 — GC 시연

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

</div>

<div class="preset-block">

### 프리셋 3 — 마모 평준화 시연

이번엔 페이지 격자 대신 **block 별 erase count**( 몇 번 지워졌는지 )를 보여주는 화면. Block 2 는 유독 자주 지워졌고( hot ), Block 5 는 거의 안 지워졌다( cold ) — 마모가 한쪽으로 쏠리는 걸 색으로 바로 보여준다.

<div class="sim-mockup">
  <div class="sim-toolbar">
    <div class="sim-presets">
      <button>매핑 기본</button><button>GC 시연</button><button class="active">마모평준화 시연</button>
    </div>
    <div class="sim-playback">
      <button>⏮</button><button>⏸</button><button>⏭</button>
      <span>속도</span><span class="sim-speed-track"></span><span>1×</span>
    </div>
  </div>
  <div class="sim-body">
    <div class="sim-grid-panel">
      <div class="sim-panel-title">Block 별 Erase Count ( 마모 평준화 대상 )</div>
      <div class="sim-caption">🟨 Block 2(118회)는 마모가 심하고 Block 5(9회)는 거의 안 닳았어요 — static WL 이 Block 5 의 cold 데이터를 옮겨서 Block 5 를 free pool 로 돌려보내는 중</div>
      <div class="wl-row"><div class="wl-label">Block 0</div><div class="wl-track"><div class="wl-fill warm" style="width:35%"></div></div><div class="wl-count">42 회 erase</div></div>
      <div class="wl-row"><div class="wl-label">Block 1</div><div class="wl-track"><div class="wl-fill warm" style="width:46%"></div></div><div class="wl-count">55 회 erase</div></div>
      <div class="wl-row"><div class="wl-label">Block 2</div><div class="wl-track"><div class="wl-fill hot" style="width:98%"></div></div><div class="wl-count">118 회 erase 🔥</div></div>
      <div class="wl-row"><div class="wl-label">Block 3</div><div class="wl-track"><div class="wl-fill warm" style="width:39%"></div></div><div class="wl-count">47 회 erase</div></div>
      <div class="wl-row"><div class="wl-label">Block 4</div><div class="wl-track"><div class="wl-fill cool" style="width:25%"></div></div><div class="wl-count">30 회 erase</div></div>
      <div class="wl-row"><div class="wl-label">Block 5</div><div class="wl-track"><div class="wl-fill cool" style="width:8%"></div></div><div class="wl-count">9 회 erase ❄️</div></div>
      <div class="sim-legend">
        <span><span class="swatch valid"></span>cool ( 적게 닳음 )</span>
        <span><span class="swatch moving"></span>warm</span>
        <span><span class="swatch invalid"></span>hot ( 많이 닳음 )</span>
      </div>
    </div>
    <div class="sim-sidebar">
      <div class="sim-panel">
        <div class="sim-panel-title">파라미터</div>
        <div class="param-row">
          <div class="param-label"><span>Static WL 임계값</span><span>erase count 차이 100</span></div>
          <div class="param-hint">이 차이를 넘으면 cold 데이터를 강제로 옮김</div>
        </div>
      </div>
      <div class="sim-panel">
        <div class="sim-panel-title">통계</div>
        <div class="stat-row"><span>최대-최소 erase 차이</span><span class="stat-value">109</span></div>
        <div class="stat-hint" style="margin-top:-6px; margin-bottom:8px;">이 값이 클수록 마모가 한쪽으로 쏠린 것</div>
        <div class="stat-row"><span>WL 발동 횟수</span><span class="stat-value">3</span></div>
      </div>
    </div>
  </div>
  <div class="sim-log">
    <div class="sim-panel-title">이벤트 로그</div>
    <div class="log-entry"><span class="log-time">12:05:02</span>Block 2 와 Block 5 의 erase count 차이(109)가 임계값을 넘어 static WL 트리거됨</div>
    <div class="log-entry"><span class="log-time">12:05:03</span>Block 5 의 cold 데이터를 Block 2 로 이동 — Block 5 가 free pool 로 돌아감</div>
  </div>
</div>

</div>

<div style="margin-top: 60px;"></div>

## 그 외 MQSim 이 보여줄 수 있는 다른 기능들

3개 프리셋 말고도, MQSim 이 실제로 모델링하는 것 중 화면으로 보여주면 재미있을 만한 것들.

<div class="preset-block">

### Host Interface — NVMe Multi-Queue

MQSim 논문의 핵심 주장 중 하나가 "최신 multi-queue 프로토콜을 제대로 모델링한다"는 것 — NVMe 는 큐가 여러 개라 요청이 동시에 여러 갈래로 처리된다. SATA 의 단일 큐와 나란히 보여주면 그 차이가 바로 느껴진다.

<div class="sim-mockup">
  <div class="sim-body">
    <div class="sim-grid-panel" style="flex: 1 1 100%; border-right: none;">
      <div class="sim-panel-title">NVMe ( 큐 4개, 동시에 처리 )</div>
      <div class="queue-row"><div class="queue-label">Q0</div><div class="queue-reqs"><div class="req-chip"></div><div class="req-chip"></div><div class="req-chip"></div></div></div>
      <div class="queue-row"><div class="queue-label">Q1</div><div class="queue-reqs"><div class="req-chip"></div><div class="req-chip"></div></div></div>
      <div class="queue-row"><div class="queue-label">Q2</div><div class="queue-reqs"><div class="req-chip"></div><div class="req-chip"></div><div class="req-chip"></div><div class="req-chip"></div><div class="req-chip"></div></div></div>
      <div class="queue-row"><div class="queue-label">Q3</div><div class="queue-reqs"><div class="req-chip"></div></div></div>
      <div class="sim-panel-title" style="margin-top:16px;">SATA ( 큐 1개, 순서대로 )</div>
      <div class="queue-row"><div class="queue-label">Q0</div><div class="queue-reqs"><div class="req-chip sata"></div><div class="req-chip sata"></div><div class="req-chip sata"></div><div class="req-chip sata"></div><div class="req-chip sata"></div><div class="req-chip sata"></div><div class="req-chip sata"></div><div class="req-chip sata"></div><div class="req-chip sata"></div><div class="req-chip sata"></div><div class="req-chip sata"></div></div></div>
      <div class="sim-caption" style="margin-top:12px;">NVMe 는 4개 큐에 나눠 담겨 있던 11개 요청을 동시에 처리하지만, SATA 는 같은 11개를 한 줄로 세워 순서대로 처리해요</div>
    </div>
  </div>
</div>

</div>

<div class="preset-block">

### 채널 / 칩 사용률 ( TSU 스케줄링 )

TSU 가 어느 채널·칩에 read/write/erase 를 배정했는지, 어디가 비어있고 어디가 바쁜지 한눈에 보여주는 화면. GC 로 인한 erase 가 사용자 요청과 자원을 다투는 모습도 여기서 보인다.

<div class="sim-mockup">
  <div class="sim-body">
    <div class="sim-grid-panel" style="flex: 1 1 100%; border-right: none;">
      <div class="sim-panel-title">Channel × Chip 상태</div>
      <div class="chip-row"><div class="chip-row-label">Ch0</div><div class="chip-cell read" title="Channel 0 / Chip 0 — read">R</div><div class="chip-cell read" title="Channel 0 / Chip 1 — read">R</div><div class="chip-cell write" title="Channel 0 / Chip 2 — write">W</div><div class="chip-cell read" title="Channel 0 / Chip 3 — read">R</div></div>
      <div class="chip-row"><div class="chip-row-label">Ch1</div><div class="chip-cell write" title="Channel 1 / Chip 0 — write">W</div><div class="chip-cell read" title="Channel 1 / Chip 1 — read">R</div><div class="chip-cell idle" title="Channel 1 / Chip 2 — idle">-</div><div class="chip-cell read" title="Channel 1 / Chip 3 — read">R</div></div>
      <div class="chip-row"><div class="chip-row-label">Ch2</div><div class="chip-cell read" title="Channel 2 / Chip 0 — read">R</div><div class="chip-cell write" title="Channel 2 / Chip 1 — write">W</div><div class="chip-cell erase" title="Channel 2 / Chip 2 — erase (GC)">E</div><div class="chip-cell idle" title="Channel 2 / Chip 3 — idle">-</div></div>
      <div class="chip-row"><div class="chip-row-label">Ch3</div><div class="chip-cell idle" title="Channel 3 / Chip 0 — idle">-</div><div class="chip-cell write" title="Channel 3 / Chip 1 — write">W</div><div class="chip-cell read" title="Channel 3 / Chip 2 — read">R</div><div class="chip-cell write" title="Channel 3 / Chip 3 — write">W</div></div>
      <div class="sim-legend" style="margin-top:12px;">
        <span><span class="swatch free"></span>idle</span>
        <span style="background:#6ea8ff; width:12px; height:12px; border-radius:3px; display:inline-block;"></span><span>read</span>
        <span style="background:#b98cf0; width:12px; height:12px; border-radius:3px; display:inline-block;"></span><span>write</span>
        <span style="background:#f5b942; width:12px; height:12px; border-radius:3px; display:inline-block;"></span><span>erase (GC)</span>
      </div>
      <div class="sim-caption" style="margin-top:12px;">Channel 2 · Chip 2 에서 GC 로 인한 erase 가 실행 중 — 이 채널의 다른 칩들은 여전히 사용자 요청을 처리할 수 있어요( 채널 단위가 아니라 칩 단위로 병렬 )</div>
    </div>
  </div>
</div>

</div>

<div style="margin-top: 20px;"></div>

## 각 영역 설명

- **상단 툴바** : 개념별 프리셋 버튼( 매핑 기본 / GC 시연 / 마모평준화 시연 )과 재생 컨트롤( step / play·pause / 속도 ). 초심자는 프리셋만 눌러도 각 개념을 바로 볼 수 있음
- **프리셋 1( 매핑 기본 )** : occupancy 가 낮고 GC 가 없는 가장 단순한 상태 — 주소 매핑이라는 개념 하나에만 집중
- **프리셋 2( GC 시연 )** : block × page 격자에서 valid/invalid/free + GC 로 이동 중인 페이지를 색으로 구분, 매핑 테이블·파라미터·통계·이벤트 로그까지 전체 레이아웃을 보여주는 기준 화면
- **프리셋 3( 마모 평준화 시연 )** : page 격자 대신 **block 별 erase count 막대**로 전환 — 마모 평준화는 페이지 단위가 아니라 block 단위 개념이라 아예 다른 시각화를 씀
- **그 외 기능** : NVMe multi-queue( vs SATA 단일 큐 ), Channel×Chip 사용률( TSU 스케줄링, GC erase 가 자원을 다투는 모습 ) — 3개 프리셋에는 안 들어가지만 MQSim 이 실제로 모델링하는 것들이라 별도 화면으로 넣어볼 만함
- **공통 원칙** : 숫자나 raw 이벤트를 그대로 보여주지 않고, 캡션·이벤트 로그·통계 옆 설명을 전부 쉬운 말로 바꿔서 표시

이 배치와 색상, 톤( 다크 테마 )은 전부 초안이라 바뀔 수 있다. 프리셋 3, NVMe multi-queue, 채널/칩 화면은 MVP 범위에 넣을지 확장 기능으로 미룰지도 아직 미정.

<div style="margin-top: 60px;"></div>

## 참고

- 이 초안의 근거가 된 설계 결정 : [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) Session 3
- 실제 구현 시 데이터 출처 : MQSim WASM 모듈의 hook 이벤트 / `getState()` — [MQSim 개괄](/ftl-visual-simulator/mqsim/code-analysis/overview/)
