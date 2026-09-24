---
layout: default
title: MQSim 2일 학습 가이드 — 원본 코드를 그림으로
permalink: /ftl-visual-simulator/reference/mqsim/study-guide/
---
<style>
.progress-box { display:flex; align-items:center; gap:0.75rem; margin:0 0 1.5rem; font-size:0.95rem; color:#555; }
.progress-bar-track { flex:1; max-width:280px; height:6px; border-radius:4px; background:#e2e2e2; overflow:hidden; }
.progress-bar-fill { height:100%; width:0%; background:#3a7d44; transition:width 0.2s ease; }
table.plan-calendar { width:100% !important; table-layout:fixed !important; border-collapse:collapse; font-size:0.85rem; margin:1rem 0; }
table.plan-calendar th, table.plan-calendar td { border:1px solid #ddd; padding:6px 10px; text-align:left; overflow-wrap:break-word; word-break:break-word; }
table.plan-calendar th { background:#f5f5f5; color:#333; }
.table-mark { cursor:pointer; text-align:center !important; font-size:1.1rem; user-select:none; }
</style>

# MQSim 2일 학습 가이드 — 원본 코드를 그림으로

[MQSim](https://github.com/CMU-SAFARI/MQSim) 원본 C++ 코드(약 3만 줄)를 **직접 열어보지 않고도** 핵심 구조와 개념을 이해할 수 있도록, 그림 위주로 정리한 학습 자료다. 하루 5시간 × 2일, 1시간짜리 세션 10개로 나눴다. 각 세션 끝에는 스스로 확인할 질문이 있고, 표의 ☐ 를 누르면 진도가 이 브라우저에 저장된다.

이 가이드는 **이 프로젝트가 수정하기 전의 원본**(앱 저장소 첫 커밋 `90b0fb1` 의 `engine/mqsim/src`)을 기준으로 한다. 이 프로젝트가 무엇을 바꿨는지는 [원본 MQSim 대비 변경 사항](/ftl-visual-simulator/reference/upstream-diff/)에 따로 있다. 숫자(용량, 지연 시간 등)는 원본에 들어 있는 기본 설정 파일 `ssdconfig.xml` 의 값이다.

<div style="margin-top: 50px;"></div>

## 전체 그림 — 요청 하나가 지나가는 길

이틀 동안 이 그림의 상자를 왼쪽부터 하나씩 열어본다. Day 1 은 호스트에서 SSD 입구·DRAM 캐시까지, Day 2 는 FTL 과 flash 칩이다.

<svg viewBox="0 0 1000 250" style="width:100%;max-width:960px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs>
    <marker id="sg-arr" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker>
    <style>
      .sg-box { fill:#eef2f7; stroke:#34495e; stroke-width:2; }
      .sg-host { fill:#fdf2e9; stroke:#ca6f1e; stroke-width:2; }
      .sg-flash { fill:#e9f7ef; stroke:#1e8449; stroke-width:2; }
      .sg-t { fill:#2c3e50; font-size:14px; font-weight:700; text-anchor:middle; }
      .sg-s { fill:#566573; font-size:11px; text-anchor:middle; }
      .sg-f { stroke:#7f8c8d; stroke-width:2; fill:none; marker-end:url(#sg-arr); }
      .sg-day { fill:#7f8c8d; font-size:12px; font-weight:700; text-anchor:middle; }
    </style>
  </defs>
  <text class="sg-day" x="290" y="22">Day 1</text>
  <text class="sg-day" x="760" y="22">Day 2</text>
  <line x1="530" y1="30" x2="530" y2="230" stroke="#bbb" stroke-dasharray="5 4"/>
  <rect class="sg-host" x="10" y="80" width="130" height="80" rx="8"/>
  <text class="sg-t" x="75" y="112">Host</text>
  <text class="sg-s" x="75" y="132">IO Flow 가</text>
  <text class="sg-s" x="75" y="146">요청 생성</text>
  <rect class="sg-box" x="170" y="80" width="150" height="80" rx="8"/>
  <text class="sg-t" x="245" y="112">Host Interface</text>
  <text class="sg-s" x="245" y="132">NVMe 큐에서 가져와</text>
  <text class="sg-s" x="245" y="146">page 단위로 쪼갬</text>
  <rect class="sg-box" x="350" y="80" width="150" height="80" rx="8"/>
  <text class="sg-t" x="425" y="112">DRAM 캐시</text>
  <text class="sg-s" x="425" y="132">쓰기를 받아두고</text>
  <text class="sg-s" x="425" y="146">나중에 flash 로</text>
  <rect class="sg-box" x="560" y="40" width="190" height="160" rx="8"/>
  <text class="sg-t" x="655" y="66">FTL</text>
  <text class="sg-s" x="655" y="92">주소 매핑 (AMU)</text>
  <text class="sg-s" x="655" y="112">block 관리 (FBM)</text>
  <text class="sg-s" x="655" y="132">GC · 마모평준화</text>
  <text class="sg-s" x="655" y="152">명령 스케줄러 (TSU)</text>
  <text class="sg-s" x="655" y="178">논리 주소 → 물리 주소</text>
  <rect class="sg-flash" x="790" y="80" width="190" height="80" rx="8"/>
  <text class="sg-t" x="885" y="112">PHY · Flash 칩</text>
  <text class="sg-s" x="885" y="132">채널로 명령 전송,</text>
  <text class="sg-s" x="885" y="146">칩이 읽기/쓰기/지우기</text>
  <path class="sg-f" d="M140,120 L168,120"/>
  <path class="sg-f" d="M320,120 L348,120"/>
  <path class="sg-f" d="M500,120 L558,120"/>
  <path class="sg-f" d="M750,120 L788,120"/>
  <text class="sg-s" x="500" y="235">모든 상자는 하나의 이산 이벤트 엔진(시간 순 이벤트 큐) 위에서 움직인다 — Day 1 세션 2</text>
</svg>

<div style="margin-top: 50px;"></div>

## 일정

<div class="progress-box">
  <span>진행률: <span id="progress-count">0 / 10</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th style="width:9%">세션</th><th style="width:28%">주제</th><th>이 세션이 끝나면 할 수 있는 것</th><th style="width:8%">완료</th></tr>
<tr><td>1-1</td><td><a href="/ftl-visual-simulator/reference/mqsim/study-guide/day1/#session-1-1">큰 그림 · 폴더 · 객체 조립</a></td><td>MQSim 이 무엇을 입력받아 무엇을 내놓는지, 어떤 객체가 어떤 순서로 만들어지는지 그릴 수 있다</td><td class="table-mark" data-session="1-1">☐</td></tr>
<tr><td>1-2</td><td><a href="/ftl-visual-simulator/reference/mqsim/study-guide/day1/#session-1-2">이산 이벤트 엔진</a></td><td>"시간"이 어떻게 흐르는지, 한 이벤트가 다음 이벤트를 어떻게 예약하는지 설명할 수 있다</td><td class="table-mark" data-session="1-2">☐</td></tr>
<tr><td>1-3</td><td><a href="/ftl-visual-simulator/reference/mqsim/study-guide/day1/#session-1-3">호스트 — 워크로드 생성</a></td><td>synthetic/trace 워크로드, 큐 깊이 방식이 요청을 언제 만드는지 안다</td><td class="table-mark" data-session="1-3">☐</td></tr>
<tr><td>1-4</td><td><a href="/ftl-visual-simulator/reference/mqsim/study-guide/day1/#session-1-4">Host Interface — NVMe 큐와 요청 분해</a></td><td>SQ/CQ, doorbell, 요청 → page 단위 트랜잭션 분해를 그릴 수 있다</td><td class="table-mark" data-session="1-4">☐</td></tr>
<tr><td>1-5</td><td><a href="/ftl-visual-simulator/reference/mqsim/study-guide/day1/#session-1-5">DRAM 데이터 캐시</a></td><td>쓰기가 캐시에서 끝나는 경우와 flash 로 내려가는 경우, back-pressure 를 안다</td><td class="table-mark" data-session="1-5">☐</td></tr>
<tr><td>2-1</td><td><a href="/ftl-visual-simulator/reference/mqsim/study-guide/day2/#session-2-1">flash 구조와 주소</a></td><td>채널/칩/다이/플레인/블록/페이지, LPA 가 플레인에 고정 배정되는 방식을 안다</td><td class="table-mark" data-session="2-1">☐</td></tr>
<tr><td>2-2</td><td><a href="/ftl-visual-simulator/reference/mqsim/study-guide/day2/#session-2-2">주소 매핑 — GMT · CMT · GTD</a></td><td>LPA → PPA 번역, CMT miss 때 일어나는 일, LPA barrier 를 설명할 수 있다</td><td class="table-mark" data-session="2-2">☐</td></tr>
<tr><td>2-3</td><td><a href="/ftl-visual-simulator/reference/mqsim/study-guide/day2/#session-2-3">block 관리 — frontier · free pool · page 상태</a></td><td>빈 block 이 어떻게 나오고 page 가 valid → invalid → free 로 도는지 안다</td><td class="table-mark" data-session="2-3">☐</td></tr>
<tr><td>2-4</td><td><a href="/ftl-visual-simulator/reference/mqsim/study-guide/day2/#session-2-4">GC 와 마모평준화</a></td><td>GC 가 언제 시작해 무엇을 고르고 어떻게 옮기는지, 동적/정적 WL 의 차이를 안다</td><td class="table-mark" data-session="2-4">☐</td></tr>
<tr><td>2-5</td><td><a href="/ftl-visual-simulator/reference/mqsim/study-guide/day2/#session-2-5">TSU · PHY · flash 칩 + 총정리</a></td><td>큐 7종, 칩 상태, 명령 타이밍, suspend 를 알고, 쓰기 하나를 처음부터 끝까지 설명할 수 있다</td><td class="table-mark" data-session="2-5">☐</td></tr>
</table>
</div>

<div style="margin-top: 50px;"></div>

## 공부하는 법

- **그림 먼저, 글은 그림을 설명하는 데만.** 각 세션은 그림 3~5개가 중심이다. 그림을 보고 "무엇이 무엇에게 무엇을 넘기는가"를 소리 내어 말해볼 수 있으면 넘어가도 된다.
- **이름은 외우지 말고 알아보기만.** 클래스·함수 이름은 나중에 코드를 열었을 때 길을 잃지 않게 붙여둔 것이다. `코드 위치` 줄은 건너뛰어도 된다.
- **세션 끝 질문**에 답이 바로 안 나오면 그 세션의 그림을 한 번 더 본다.
- 이 앱(FTL Visual Simulator)을 옆에 띄워두면 좋다 — 로그에서 LPN 을 클릭하면 Day 2 의 개념(out-of-place update, GC 이동)이 실제로 보인다.

<div style="margin-top: 50px;"></div>

## 더 깊이 보고 싶을 때

- [MQSim 개괄](/ftl-visual-simulator/reference/mqsim/code-analysis/overview/) — 파일별 설명과 주요 콜 플로우(함수 호출 순서) 8개. 이 가이드를 끝낸 뒤 코드를 열 때 지도로 쓰기 좋다
- [FTL 개념 ↔ 파라미터·모듈 대응](/ftl-visual-simulator/reference/mqsim/code-analysis/concept-mapping/) — 설정값이 어느 모듈의 어떤 동작을 바꾸는지
- [쓰기 전에 읽으면 페이지가 소비되는 이유](/ftl-visual-simulator/reference/mqsim/read-before-write/)
- [원본 MQSim 대비 변경 사항](/ftl-visual-simulator/reference/upstream-diff/) · [버그 목록](/ftl-visual-simulator/reference/bug-list/) — 원본의 어디가 틀렸었는지

<script>
(function () {
  var STORAGE_KEY = 'mqsim-study-guide-progress';
  function load() { try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch (e) { return {}; } }
  function save(state) { try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {} }
  document.addEventListener('DOMContentLoaded', function () {
    var marks = Array.prototype.slice.call(document.querySelectorAll('.table-mark'));
    var countEl = document.getElementById('progress-count');
    var fillEl = document.getElementById('progress-fill');
    var state = load();
    function render() {
      var done = 0;
      marks.forEach(function (mark) {
        var isDone = !!state[mark.getAttribute('data-session')];
        mark.textContent = isDone ? '✅' : '☐';
        if (isDone) done++;
      });
      if (countEl) countEl.textContent = done + ' / ' + marks.length;
      if (fillEl) fillEl.style.width = (marks.length ? (done / marks.length) * 100 : 0) + '%';
    }
    marks.forEach(function (mark) {
      mark.addEventListener('click', function () {
        var id = mark.getAttribute('data-session');
        state[id] = !state[id];
        save(state);
        render();
      });
    });
    render();
  });
})();
</script>
