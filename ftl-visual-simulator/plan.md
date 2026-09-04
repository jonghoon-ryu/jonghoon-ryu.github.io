---
layout: default
title: 계획 (Plan)
permalink: /ftl-visual-simulator/plan/
---
<style>
.progress-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1.5rem;
  font-size: 0.95rem;
  color: #555;
}
.progress-bar-track {
  flex: 1;
  max-width: 280px;
  height: 6px;
  border-radius: 4px;
  background: #e2e2e2;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  width: 0%;
  background: #3a7d44;
  transition: width 0.2s ease;
}
.session-check {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #777;
  cursor: pointer;
  user-select: none;
  margin: 0.2rem 0 0.6rem;
}
.session-check input {
  cursor: pointer;
}
.session.done h3 {
  color: #999;
  text-decoration: line-through;
  text-decoration-color: #bbb;
}
.session.done {
  opacity: 0.6;
}
.session {
  margin-top: 70px;
  padding-top: 32px;
  border-top: 1px solid #ddd;
}
.session:first-of-type {
  margin-top: 0;
  padding-top: 0;
  border-top: none;
}
table.plan-calendar {
  width: 100%;
  border-collapse: collapse;
  font-size: 0.85rem;
  margin: 1rem 0;
}
table.plan-calendar th, table.plan-calendar td {
  border: 1px solid #ddd;
  padding: 6px 10px;
  text-align: left;
}
table.plan-calendar th {
  background: #f5f5f5;
}
</style>

# FTL 시각화 시뮬레이터 — 일정 계획

**1차 완성 목표일 : 2026-10-11**. 9/4(금)를 시작일로 삼아, 이후 주말( 토/일 ) + 공휴일( 10/5, 10/9 ) 기준 하루 6시간씩 총 12세션 커리큘럼. 10/11 에 결과물을 직접 리뷰하고, 필요하면 10/17~10/18, 10/24~10/25 를 이용해 수정한다.

<div style="margin-top: 60px;"></div>

## 전제 조건

- 평일 작업은 기대하지 않음. 다만 가능하면 다음 세션 내용을 미리 당기거나, 여유( 버퍼 ) 로 사용
- **9/4(금)를 시작일로 사용** — 세션 1 (FTL 개념)을 짜투리 시간에 미리 시작. **9/5(토)는 계획에서 제외** (쉬는 날)
- 9/12(토), 9/13(일) 은 개인 사정으로 작업 불가 → 계획에서 제외
- 10/5(월), 10/9(금) 은 공휴일이라 평일이지만 주말과 동일하게 6시간 작업일로 포함
- **10/11 이 1차 마감** — 이 날짜 안에 "동작하는 배포본"을 만드는 것이 최우선이고, 그 다음 리뷰 결과에 따라 10/17~10/25 에 수정
- 세션 순서가 날짜보다 중요함. 한 세션이 밀리면 다음 세션도 그만큼 밀린다고 생각하고, 억지로 두 세션을 하루에 몰아넣지 않기

<div style="margin-top: 40px;"></div>

## 날짜표 ( 12 세션 )

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>세션</th><th>날짜</th><th>구분</th><th>단계</th></tr>
<tr><td>1</td><td>9/4 (금)</td><td>평일 (시작일)</td><td>Phase 1 — FTL 개념</td></tr>
<tr><td>2</td><td>9/6 (일)</td><td>주말</td><td>Phase 2 — MQSim 분석</td></tr>
<tr><td>3</td><td>9/19 (토)</td><td>주말</td><td>Phase 3 — 설계</td></tr>
<tr><td>4</td><td>9/20 (일)</td><td>주말</td><td>Phase 4 — 시뮬레이션 엔진 (1)</td></tr>
<tr><td>5</td><td>9/26 (토)</td><td>주말</td><td>Phase 4 — 시뮬레이션 엔진 (2)</td></tr>
<tr><td>6</td><td>9/27 (일)</td><td>주말</td><td>Phase 4 — 시뮬레이션 엔진 (3)</td></tr>
<tr><td>7</td><td>10/3 (토)</td><td>주말</td><td>Phase 5 — 시각화 (1)</td></tr>
<tr><td>8</td><td>10/4 (일)</td><td>주말</td><td>Phase 5 — 시각화 (2)</td></tr>
<tr><td>9</td><td>10/5 (월)</td><td>공휴일</td><td>Phase 6 — 인터랙션 (1)</td></tr>
<tr><td>10</td><td>10/9 (금)</td><td>공휴일</td><td>Phase 6 — 인터랙션 (2)</td></tr>
<tr><td>11</td><td>10/10 (토)</td><td>주말</td><td>Phase 7 — 마무리 (1)</td></tr>
<tr><td>12</td><td>10/11 (일)</td><td>주말 · 1차 마감</td><td>Phase 7 — 마무리 (2) · 배포 · 리뷰</td></tr>
</table>
</div>

<div style="margin-top: 20px;"></div>

**리뷰 후 버퍼 (계획 외)** : 10/17(토)~10/18(일), 10/24(토)~10/25(일) — 10/11 리뷰에서 나온 피드백을 반영하는 용도. 별도 세션 번호 없이, 리뷰 결과에 따라 자유롭게 사용.

<div style="margin-top: 60px;"></div>

## 세션

<div class="progress-box">
  <span>진행률: <span id="progress-count">0 / 12</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div class="session" data-session="1" markdown="1">

### 1. (9/4) FTL 개념 — 매핑 · GC · 마모 평준화 · Over-provisioning

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="1"> 완료 체크</label>

- NAND flash 의 물리적 제약 : page / block / plane 구조, "erase-before-write" ✅ ( 9/4 진행 )
- 주소 매핑 방식 : page-level, block-level, hybrid(log-block, FAST) mapping ✅ ( 9/4 진행 )
- 마모 평준화( static/dynamic ), bad block 관리, over-provisioning, DFTL 같은 demand-based 매핑 캐싱 — 이미 잘 알고 있음 ✅
- Garbage Collection ( victim block 선정 알고리즘 등 ) — **Session 5(GC 알고리즘 구현) 때 실습과 함께 깊이 다루기로 미룸**
- 결과물 : FTL 핵심 개념 정리 ( GC 제외 완료 )

</div>

<div class="session" data-session="2" markdown="1">

### 2. (9/6) MQSim 빌드 · 실행 · 구조 분석

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="2"> 완료 체크</label>

- [CMU-SAFARI/MQSim](https://github.com/CMU-SAFARI/MQSim) clone, 빌드, 샘플 설정으로 실행
- XML 설정 구조( Flash parameter, FTL parameter, GC 정책, cache ) 파악
- 주요 모듈 : Host_Interface, IO_Flow, Address_Mapping_Unit, Flash_Block_Manager, GC_and_WL_Unit, NVM_PHY_ONFI
- 결과물 : Host request → FTL 매핑 → Flash controller → NAND 로 이어지는 파이프라인 다이어그램, "시각화에 그대로 가져갈 부분 / 단순화할 부분" 정리

</div>

<div class="session" data-session="3" markdown="1">

### 3. (9/19) 시뮬레이터 설계 — 범위 · 스택 · 데이터 모델

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="3"> 완료 체크</label>

- MVP 범위 확정 : flash block/page grid ( free / valid / invalid / erasing 상태 ), 매핑 테이블, GC 이벤트, 통계( WAF, valid page 비율 )
- 사용자 조절 파라미터 확정 : page 크기, block 당 page 수, block 개수/OP 비율, 매핑 방식, GC 트리거 임계값, workload 패턴
- 기술 스택 결정 : TypeScript + React + Vite, 시뮬레이션 코어는 UI 와 분리된 순수 TS 모듈, Canvas/SVG 렌더링, GitHub Pages 정적 배포
- 데이터 모델 설계( Flash array, Block, Page, MappingTable, FTL controller — step() 기반 ) 와 화면 와이어프레임( flash grid, 매핑 테이블 패널, 파라미터 패널, 이벤트 로그, 통계 대시보드 )
- 결과물 : 설계 문서 + 와이어프레임, 프로젝트 뼈대(scaffold) 커밋

</div>

<div class="session" data-session="4" markdown="1">

### 4. (9/20) 시뮬레이션 엔진 (1) — 매핑 테이블과 read/write 경로

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="4"> 완료 체크</label>

- 프로젝트 scaffold ( Vite + React + TS )
- NAND flash array 자료구조, page-level FTL 매핑 테이블 구현
- host write 경로 ( 매핑 조회 → free page 할당 → 매핑 갱신 → 기존 page invalidate ), read 경로 구현

</div>

<div class="session" data-session="5" markdown="1">

### 5. (9/26) 시뮬레이션 엔진 (2) — GC 알고리즘

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="5"> 완료 체크</label>

- **GC 이론 학습** ( Session 1 에서 미뤄둔 부분 ) : victim block 선정 알고리즘( greedy vs cost-benefit ), GC 트리거 정책과 WAF 관계
- GC 알고리즘 구현 : victim block 선정, valid page migration, block erase
- UI 없이 시뮬레이션 코어만 단위 테스트 ( 샘플 write 시퀀스로 WAF 등 기대값 검증 )

</div>

<div class="session" data-session="6" markdown="1">

### 6. (9/27) 시뮬레이션 엔진 (3) — 마모 평준화와 엔진 마무리

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="6"> 완료 체크</label>

- 기본적인 dynamic wear leveling, bad block 표시 구현
- 비교용으로 hybrid/log-block 매핑을 대안 옵션으로 추가
- 시뮬레이션 엔진 API 확정 ( step, reset, configure )
- 결과물 : UI 없이도 동작·테스트가 끝난 시뮬레이션 엔진

</div>

<div class="session" data-session="7" markdown="1">

### 7. (10/3) 시각화 (1) — flash grid · 매핑 테이블 뷰

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="7"> 완료 체크</label>

- flash array grid 시각화 ( block/page 상태별 색상 구분 ), 시뮬레이션 엔진과 연결해 write/GC 실시간 애니메이션
- 매핑 테이블 뷰어 패널

</div>

<div class="session" data-session="8" markdown="1">

### 8. (10/4) 시각화 (2) — 로그 · 통계 · 재생 컨트롤

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="8"> 완료 체크</label>

- 이벤트 로그 / 타임라인, 통계 대시보드 ( WAF, valid page 비율, GC 발생 횟수, erase 횟수 )
- step / play·pause / 속도 조절 슬라이더, write/invalidate/erase/migrate 애니메이션 다듬기
- 결과물 : 고정 기본 파라미터로 브라우저에서 처음부터 끝까지 동작하는 시각화 시뮬레이터

</div>

<div class="session" data-session="9" markdown="1">

### 9. (10/5, 공휴일) 인터랙션 (1) — 파라미터 컨트롤 패널

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="9"> 완료 체크</label>

- page 크기, block/page 개수, OP 비율, GC 임계값, 매핑 방식 선택 UI
- 파라미터 변경 시 엔진을 실시간으로 reset/reconfigure 하도록 연동

</div>

<div class="session" data-session="10" markdown="1">

### 10. (10/9, 공휴일) 인터랙션 (2) — workload 컨트롤

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="10"> 완료 체크</label>

- workload 생성기 컨트롤 ( sequential/random, read/write 비율, burst 크기 )
- ( 선택 ) 간단한 CSV/텍스트 형식의 커스텀 trace 업로드
- 입력값 검증 및 파라미터 범위 제한
- 결과물 : 파라미터와 workload 를 바꿔가며 동작 차이를 직접 관찰할 수 있는 완전한 인터랙티브 시뮬레이터

</div>

<div class="session" data-session="11" markdown="1">

### 11. (10/10) 마무리 (1) — 다듬기

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="11"> 완료 체크</label>

- UI 다듬기 ( 범례, 툴팁, 반응형 레이아웃, 색상 접근성 )
- 버그 수정, 크로스 브라우저 확인
- README / 동작 원리 문서 작성

</div>

<div class="session" data-session="12" markdown="1">

### 12. (10/11) 마무리 (2) — 최종 테스트 · 배포 · 리뷰

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="12"> 완료 체크</label>

- 최종 테스트, GitHub Pages 배포
- 1차 완성본 리뷰 — 여기서 나온 피드백은 10/17 이후 버퍼 기간에 반영

</div>

<div style="margin-top: 100px;"></div>

## 페이싱 & 리스크 노트

- 12세션( 9/4 ~ 10/11 ) 을 다 채우면 정확히 1차 마감일에 맞음 → 여유가 거의 없는 일정
- 가장 위험한 구간은 **Phase 4 (시뮬레이션 엔진, 세션 4~6)**. 여기서 밀리면 Phase 5(시각화) 범위를 줄여서 흡수하고( 예 : 이벤트 로그 생략, grid+매핑테이블+통계만 유지 ), 엔진 정확성과 세션 11~12( 다듬기·배포 ) 는 타협하지 않기
- 세션 11~12( 마무리·배포 ) 는 일부러 축소하지 않음 — 10/11 에 "리뷰할 수 있는 배포된 결과물" 이 있는 것이 이번 계획의 핵심 목표이기 때문
- 평일에 시간이 나면 : 다음 세션 내용을 미리 당기거나, 확장 기능( hybrid 매핑 비교, DFTL 매핑 캐시 시각화, MQSim 을 WASM 으로 컴파일해서 코어로 사용, 실제 SSD trace 재생 ) 에 투자하거나, 그냥 버퍼로 저축
- 세션이 통째로 날아가면 억지로 다음 세션에 두 개를 몰아넣지 말고, 세션 11~12 버퍼로 흡수하는 쪽을 우선. 그래도 안 되면 10/11 리뷰 범위를 줄이고 10/17 이후로 일부 항목을 미루기

<script>
(function () {
  var STORAGE_KEY = 'ftl-visual-simulator-plan-progress';

  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch (e) { return {}; }
  }
  function save(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {}
  }

  document.addEventListener('DOMContentLoaded', function () {
    var boxes = Array.prototype.slice.call(document.querySelectorAll('.session-checkbox'));
    var countEl = document.getElementById('progress-count');
    var fillEl = document.getElementById('progress-fill');
    var total = boxes.length;
    var state = load();

    function render() {
      var done = 0;
      boxes.forEach(function (cb) {
        var id = cb.getAttribute('data-session');
        var isDone = !!state[id];
        cb.checked = isDone;
        var wrap = cb.closest('.session');
        if (wrap) wrap.classList.toggle('done', isDone);
        if (isDone) done++;
      });
      if (countEl) countEl.textContent = done + ' / ' + total;
      if (fillEl) fillEl.style.width = (total ? (done / total) * 100 : 0) + '%';
    }

    boxes.forEach(function (cb) {
      cb.addEventListener('change', function () {
        state[cb.getAttribute('data-session')] = cb.checked;
        save(state);
        render();
      });
    });

    render();
  });
})();
</script>
