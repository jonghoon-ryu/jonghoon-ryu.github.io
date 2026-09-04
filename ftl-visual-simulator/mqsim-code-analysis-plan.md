---
layout: default
title: MQSim 코드 분석 계획
permalink: /ftl-visual-simulator/mqsim-code-analysis-plan/
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
  color: #333;
}
table.plan-calendar .row-mark {
  cursor: pointer;
  user-select: none;
}
</style>

# MQSim 코드 분석 계획

시뮬레이터를 만들기 전에, MQSim 소스코드 자체를 처음부터 끝까지 체계적으로 읽는 계획. [통합 계획 (Plan)](/ftl-visual-simulator/plan/) 과 같은 12세션 날짜를 그대로 따라가되, 여기서는 **그 세션에 어떤 MQSim 소스를 읽을 것인가**만 다룬다.

<div style="margin-top: 40px;"></div>

## 왜 이 순서인가

- **하향식( top-down )** : 전체 그림 → 요청이 들어오는 입구 → FTL 핵심(매핑·GC·WL) → 요청이 빠져나가는 출구(스케줄링·물리) → 입출력 주변부(캐시·통계·workload) → 마지막에 전체를 한 번에 관통
- 각 세션은 [MQSim 코드 분석](/ftl-visual-simulator/mqsim-code-analysis/) 문서의 해당 부분을 먼저 훑고, 실제 소스 파일을 열어 문서의 설명과 코드가 정말 일치하는지 확인하는 방식으로 진행
- [통합 계획 (Plan)](/ftl-visual-simulator/plan/) 의 "MQSim/FTL 심화" 항목과 내용이 겹치는 세션도 있음 — 여긴 그걸 하나로 모아 더 깊게 파는 버전

<div style="margin-top: 60px;"></div>

## 세션

<div class="progress-box">
  <span>진행률: <span id="progress-count">0 / 12</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div class="session" data-session="1" markdown="1">

### 1. 전체 그림 잡기 — 디렉터리 구조와 파이프라인

읽을 파일 : `src/` 디렉터리 구조 훑어보기, `src/exec/SSD_Device.h`( 주석의 파이프라인 다이어그램 ), `src/ssd/FTL.h`

- `exec/host/nvm_chip/sim/ssd/utils` 6개 디렉터리가 각각 뭘 담당하는지 감 잡기
- `FTL` 클래스가 `Address_Mapping_Unit` / `Flash_Block_Manager` / `GC_and_WL_Unit` / `TSU` 4개를 들고 있다는 구조부터 확인
- 체크포인트 : "SSD_Device 하나가 조립되면 그 안에 뭐가 들어있는지" 를 그림으로 그려볼 수 있으면 통과

</div>

<div class="session" data-session="2" markdown="1">

### 2. 시뮬레이션 엔진 — 이산 이벤트가 어떻게 도는가

읽을 파일 : `src/sim/Sim_Object.h`, `src/sim/Engine.h`, `src/sim/EventTree.h`, `src/main.cpp`

- `Sim_Object::Execute_simulator_event()` 가 모든 구성요소의 공통 진입점이라는 것 확인
- `Engine`( `Simulator` 매크로 )이 싱글턴이고 `EventTree` 로 이벤트를 시간순 관리한다는 것 확인
- `main.cpp` 에서 설정 파싱 → 워크로드 파싱 → 시나리오 루프( `Simulator->Reset()` → `SSD_Device` 생성 → `Host_System` 생성 → `Simulator->Start_simulation()` ) 흐름을 코드에서 직접 짚어보기
- 체크포인트 : "이벤트 하나가 등록되고 실행되는 과정"을 코드 줄 번호로 설명할 수 있으면 통과

</div>

<div class="session" data-session="3" markdown="1">

### 3. 주소 매핑 (1) — 자료구조

읽을 파일 : `src/ssd/Address_Mapping_Unit_Base.h`, `src/ssd/Address_Mapping_Unit_Page_Level.h`, `src/ssd/Flash_Block_Manager_Base.h`

- `Block_Pool_Slot_Type`( `Invalid_page_bitmap`, `Erase_count`, `Current_status` 상태 머신 )가 실제 block 상태를 어떻게 들고 있는지
- `PlaneBookKeepingType` 의 `Data_wf` / `GC_wf` / `Translation_wf`( double write frontier ) 구조 이해
- CMT( Cached Mapping Table ) 관련 메서드( `Exists`, `Retrieve_ppa`, `Reserve_slot_for_lpn` )가 매핑 테이블 전체를 캐싱하지 않는 이유
- 체크포인트 : "매핑 테이블 하나의 엔트리가 무엇을 저장하는지" 정확히 설명

</div>

<div class="session" data-session="4" markdown="1">

### 4. 주소 매핑 (2) — 실제 동작

읽을 파일 : `src/ssd/Address_Mapping_Unit_Page_Level.cpp` ( `Translate_lpa_to_ppa_and_dispatch` 중심 )

- write 요청이 들어왔을 때 : 기존 매핑 조회( CMT hit/miss ) → 새 PPA 할당( `Flash_Block_Manager` 호출 ) → 매핑 갱신 → 기존 PPA invalidate, 이 순서를 코드에서 그대로 추적
- read 요청 경로도 동일하게 추적
- 체크포인트 : write 요청 하나가 `Translate_lpa_to_ppa_and_dispatch` 안에서 거치는 단계를 순서대로 나열

</div>

<div class="session" data-session="5" markdown="1">

### 5. GC — 트리거부터 erase 까지

읽을 파일 : `src/ssd/GC_and_WL_Unit_Base.h`, `src/ssd/GC_and_WL_Unit_Page_Level.cpp`( `Check_gc_required`, `GC_is_in_urgent_mode`, victim selection 부분 )

- free block pool 이 줄어들 때 `Check_gc_required()` 가 왜/어떻게 불리는지
- `GC_Block_Selection_Policy`( GREEDY/RGA/RANDOM 계열/FIFO ) 중 실제 설정값( RGA )의 코드 분기 추적
- victim block 선정 → valid page migration → block erase, 3단계를 코드에서 순서대로 확인
- 체크포인트 : "GC 가 왜 지금 시작됐는지" 를 코드 조건문 기준으로 설명

</div>

<div class="session" data-session="6" markdown="1">

### 6. Hybrid 매핑과 마모 평준화

읽을 파일 : `src/ssd/Address_Mapping_Unit_Hybrid.h/cpp`, `GC_and_WL_Unit_Page_Level.cpp` 의 wear-leveling 관련 부분

- log-block 방식에서 merge( switch/partial/full )가 어떤 조건에서 어떤 방식으로 갈리는지
- dynamic wear-leveling 이 GC 로직과 어떻게 얽혀 있는지( 같은 클래스 안에 있는 이유 )
- 체크포인트 : page-level 매핑과 hybrid 매핑의 코드 구조 차이를 한 문단으로 요약

</div>

<div class="session" data-session="7" markdown="1">

### 7. 요청이 들어오는 입구 — Host Interface 와 Cache

읽을 파일 : `src/ssd/Host_Interface_Base.h`, `Host_Interface_NVMe.h/cpp`, `Data_Cache_Manager_Base.h`, `Data_Cache_Manager_Flash_Simple.cpp`

- NVMe 의 multi-queue 구조( `Input_Stream_Manager_NVMe`, `Request_Fetch_Unit_NVMe` )가 SATA 단일 큐와 어떻게 다른지
- 캐시 히트 시 FTL 까지 안 내려가는 경로가 있는지 확인
- 체크포인트 : 호스트 요청이 `Host_Interface` 에서 `FTL` 까지 가는 경로를 그림으로

</div>

<div class="session" data-session="8" markdown="1">

### 8. 요청이 빠져나가는 출구 — TSU 와 물리 계층

읽을 파일 : `src/ssd/TSU_Base.h`, `TSU_FLIN.cpp` 또는 `TSU_OutofOrder.cpp`, `NVM_PHY_ONFI.h/cpp`, `ONFI_Channel_Base.h/cpp`

- `TSU.Schedule()` 이 여러 채널/칩 중 무엇을 언제 실행시킬지 정하는 기준
- ONFI 타이밍 모델( read/program/erase 지연시간 )이 어디서 더해지는지
- 채널 하나에 여러 칩이 붙을 때 버스 경합이 어떻게 처리되는지
- 체크포인트 : flash transaction 하나가 큐에 들어가서 실제로 실행되기까지의 대기 이유를 설명

</div>

<div class="session" data-session="9" markdown="1">

### 9. 결과 집계 — Stats 와 XML 출력

읽을 파일 : `src/ssd/Stats.h/cpp`, `src/utils/XMLWriter.h/cpp`, `main.cpp` 의 `collect_results()`

- `Total_GC_Executions`, WAF 관련 카운터 등이 시뮬레이션 도중 어디서 증가되는지 역추적( GC_and_WL_Unit 쪽 카운터 증가 지점 )
- 왜 MQSim 은 중간 상태 없이 "끝나고 나서" 결과를 한 번에 XML 로 쓰는 구조인지( = 우리가 hook 을 심어야 하는 이유 재확인 )
- 체크포인트 : 9/4 에 봤던 결과 XML 의 특정 숫자 하나를 골라, 그 값이 코드 어디서 만들어지는지 추적

</div>

<div class="session" data-session="10" markdown="1">

### 10. Workload 입력 — Synthetic vs Trace

읽을 파일 : `src/host/IO_Flow_Base.h`, `IO_Flow_Synthetic.cpp`, `IO_Flow_Trace_Based.cpp`

- synthetic 워크로드가 파라미터( 분포, hot region 비율 등 )로부터 실제 요청을 어떻게 생성하는지
- trace 기반 워크로드( `tpcc-small.trace` )가 파일을 어떻게 파싱해서 같은 형태의 요청으로 변환하는지
- 체크포인트 : 두 방식이 최종적으로 `Host_Interface` 에 요청을 넘기는 지점이 왜 동일한 인터페이스로 수렴하는지 설명

</div>

<div class="session" data-session="11" markdown="1">

### 11. 재점검 — hook 지점 다시 훑기

지금까지 읽은 8개 파일( Address_Mapping_Unit_Page_Level/Hybrid, GC_and_WL_Unit_Page_Level, Flash_Block_Manager, Stats )을 다시 열어서, 실제로 시뮬레이터에 추가된 hook 코드가 원본 로직의 정확히 어느 지점에 들어갔는지 하나씩 대조

- 체크포인트 : hook 코드 한 줄 한 줄이 "왜 거기 있는지" 설명 가능해야 함

</div>

<div class="session" data-session="12" markdown="1">

### 12. 캡스톤 — 전체 관통

도움 없이, write 요청 하나를 골라 다음을 순서대로 코드 파일/함수 이름을 대며 설명해보기

1. `Host_Interface` 가 요청을 받는다 ( 어느 파일/클래스? )
2. `Data_Cache_Manager` 를 거친다
3. `Address_Mapping_Unit` 에서 매핑을 조회/갱신한다 ( 어느 함수? )
4. `TSU` 가 스케줄링한다
5. `NVM_PHY_ONFI`/`ONFI_Channel` 이 물리 타이밍을 시뮬레이션한다
6. `Flash_Block_Manager` 의 free block pool 이 줄어 `GC_and_WL_Unit.Check_gc_required()` 가 트리거될 수도 있다
7. `Stats` 에 결과가 집계되고 `main.cpp` 의 `collect_results()` 가 XML 로 쓴다

이 7단계가 막힘없이 나오면 MQSim 코드 이해는 끝난 것.

</div>

<script>
(function () {
  var STORAGE_KEY = 'ftl-mqsim-code-analysis-plan-progress';

  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch (e) { return {}; }
  }
  function save(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {}
  }

  document.addEventListener('DOMContentLoaded', function () {
    var sessions = Array.prototype.slice.call(document.querySelectorAll('.session[data-session]'));
    var countEl = document.getElementById('progress-count');
    var fillEl = document.getElementById('progress-fill');
    var total = sessions.length;
    var state = load();

    function render() {
      var done = 0;
      sessions.forEach(function (wrap) {
        var id = wrap.getAttribute('data-session');
        var isDone = !!state[id];
        wrap.classList.toggle('done', isDone);
        if (isDone) done++;
      });
      if (countEl) countEl.textContent = done + ' / ' + total;
      if (fillEl) fillEl.style.width = (total ? (done / total) * 100 : 0) + '%';
    }

    sessions.forEach(function (wrap) {
      var h3 = wrap.querySelector('h3');
      if (!h3) return;
      h3.style.cursor = 'pointer';
      h3.title = '클릭해서 완료 표시';
      h3.addEventListener('click', function () {
        var id = wrap.getAttribute('data-session');
        state[id] = !state[id];
        save(state);
        render();
      });
    });

    render();
  });
})();
</script>
