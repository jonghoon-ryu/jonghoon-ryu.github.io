---
layout: default
title: Claude 구현 작업 상세
permalink: /ftl-visual-simulator/plan/implementation/
---
<style>
table.plan-calendar {
  width: 100% !important;
  table-layout: fixed !important;
  border-collapse: collapse;
  font-size: 0.85rem;
  margin: 1rem 0;
}
table.plan-calendar th, table.plan-calendar td {
  border: 1px solid #ddd;
  padding: 6px 10px;
  text-align: left;
  overflow-wrap: break-word;
  word-break: break-word;
}
table.plan-calendar th {
  background: #f5f5f5;
  color: #333;
}
#main_content li > input.item-check {
  margin-right: 0.5em;
  vertical-align: middle;
  accent-color: #7c3aed;
  cursor: not-allowed;
}
#main_content li .item-comment {
  color: #7c3aed;
  font-style: italic;
  font-size: 0.85em;
  margin-left: 0.4em;
}
</style>

# Claude 구현 작업 상세

[전체 개발 계획](/ftl-visual-simulator/plan/full-plan/)의 각 세션에 있는 "Claude 가 할 일"은 세션 단위로 짧게만 적혀 있다. 이 문서는 그 내용을 **컴포넌트/기능 단위로 다시 묶어서**, 실제 코드에서 확인한 정확한 파일·함수 이름까지 포함해 상세하게 기록한 것 — 실제로 구현할 때 참고할 상세 스펙.

<div style="margin-top: 40px;"></div>

## 0. 전체 아키텍처

- **엔진** : MQSim C++ 원본( `/home/ryuj/Ryu/MQSim` )을 Emscripten 으로 WASM 컴파일해서 그대로 사용 — TS 재구현 아님
- **UI** : Vite + React + TypeScript
- **바인딩** : WASM 모듈과 React 상태를 잇는 얇은 JS/TS 레이어
- **입력 방식** : 파라미터 패널에서 만든 값을 실제 `ssdconfig.xml`/`workload.xml` 형식 텍스트로 만들어 Emscripten 가상 파일시스템(MEMFS)에 써넣고, MQSim 기존 XML 파싱 코드(`read_configuration_parameters`, `read_workload_definitions`)를 그대로 재사용
- **계측(hook) 방식** : 주기적 상태 스냅샷이 아니라 Emscripten `EM_ASM`/exported 콜백으로 이벤트를 즉시 JS 로 통지( Session 3 설계 결정 )
- **배포** : GitHub Pages 정적 호스팅

<div style="margin-top: 60px;"></div>

## 1. 프로젝트 뼈대 & 빌드 파이프라인 ( Session 3~4 )

- Vite + React + TS scaffold 생성 ( 9/5 진행 — [ftl-visual-simulator 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator) )
- Emscripten 툴체인 설치, MQSim 빌드 확인( 기존 `Makefile` 대신 Emscripten 용 빌드 스크립트 필요 )
- **`main.cpp` 라이브러리화** — 현재 `main()` 안에 있는 "설정 파싱 → workload 파싱 → 시나리오 루프( `Simulator->Reset()` → `SSD_Device` 생성 → `Host_System` 생성 → `Simulator->Start_simulation()` → `collect_results()` )" 흐름을 재호출 가능한 함수로 분리
- ( 여유 있으면 ) 이 라이브러리 분리 구조에 **GTest 프레임워크 연결** — 같은 리팩터링을 GMock 테스트 바이너리용으로도 재사용( 7-3 참고 )

> **사전 조사( 9/5, Session 4 예습 )** — Session 4 를 시작하기 전에 "Emscripten 빌드가 애초에 가능한가"만 미리 확인해봄( 라이브러리 리팩터링 없이 기존 `main.cpp` 그대로, `/tmp` 에서 실험, 실제 프로젝트 코드는 변경 없음 ).
> - MQSim 소스 61개 파일 전부 **수정 없이 그대로 컴파일 성공**( 기존에도 있던 warning 몇 개 외에는 문제 없음 ) — C++ 호환성 리스크는 낮아 보임
> - 링크는 `emcc` 가 아니라 **`em++`** 로 해야 함( `emcc` 는 C 링커 모드라 libc++ 심볼이 전부 undefined 로 뜸 )
> - 기본 옵션으로 실행하면 두 가지가 바로 걸림 — 전부 빌드 플래그로 해결됨, 코드 수정 불필요:
>   - 스택 오버플로우 → **`-sSTACK_SIZE=8MB`**( 기본 64KB 는 MQSim 에 너무 작음 )
>   - OOM → **`-sALLOW_MEMORY_GROWTH=1 -sINITIAL_MEMORY=128MB`**( 기본 16MB 는 너무 작음 )
> - 위 플래그로 빌드해 Node 에서 `ssdconfig.xml`/`workload.xml` 시나리오 1(synthetic)을 실행 → **결과가 9/4 네이티브 실행과 동일**( 요청 수·응답시간 일치 ). 시나리오 2 는 오래 걸리는데, 이건 버그가 아니라 그 시나리오 자체가 `Stop_Time=10,000,000,000` · `Total_Requests_To_Generate=0`( 무제한 )으로 설정된 긴 시나리오라서( 네이티브에서도 마찬가지로 오래 걸릴 것 ). 시나리오 3(trace 기반)은 이번엔 `traces/` 를 같이 안 실었어서 테스트 안 함.
> - 결론 : Emscripten 빌드 자체는 **막히는 지점이 아님**. Session 4 의 실제 작업은 그대로 "`main.cpp` 라이브러리화 + 위 빌드 플래그를 정식 빌드 스크립트에 반영"이 됨.

<div style="margin-top: 60px;"></div>

## 2. WASM 바인딩 API ( Session 6 종료 시점까지 확정 )

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>함수</th><th>역할</th></tr>
<tr><td><code>init(config)</code></td><td>ssdconfig.xml/workload.xml 텍스트를 MEMFS 에 쓰고 <code>SSD_Device</code>/<code>Host_System</code> 초기화( <code>main.cpp</code> 의 시나리오 루프 앞부분에 대응 )</td></tr>
<tr><td><code>step()</code> / <code>run(n)</code></td><td><code>Engine::Start_simulation()</code> 의 이벤트 루프를 이벤트 1개( 또는 n개 )만큼만 실행 — 재생 컨트롤(4장)의 기반</td></tr>
<tr><td><code>getState()</code></td><td>매핑 테이블·block/page 상태 스냅샷을 JS 객체로 반환( 매핑 테이블 뷰어의 데이터 소스 )<br>( 9/6 구현 — 현재는 <code>{ mapping: [...] }</code> 만 반환. block/page grid 상태는 3-2/3-3 hook 이 붙으면 여기에 추가 )</td></tr>
<tr><td><code>setEventCallback(fn)</code></td><td>( 9/6 추가, 원래 표에 없던 항목 ) 매핑 갱신 등 시뮬레이션 이벤트가 발생할 때마다 JS 함수 <code>fn(event)</code> 를 호출하도록 등록 — 재생 중 실시간 애니메이션(4장)의 데이터 소스</td></tr>
<tr><td><code>configure()</code></td><td>파라미터 변경 후 WASM 모듈 재구성(reset) — 파라미터 패널(5장)에서 호출</td></tr>
</table>
</div>

> ⚠️ **( 9/6 기록 ) LPA/PPA 는 JS 로 넘어올 때 `BigInt` 다.** MQSim 의 LPA/PPA 는 64비트 정수라 embind 가 JS `number` 대신 `BigInt` 로 변환한다 — 화면에 그대로 찍으려면 `.toString()`, JSON 으로 보내려면 커스텀 replacer 가 필요( `JSON.stringify` 는 BigInt 를 기본적으로 직렬화 못 함 ). React 컴포넌트(4장)에서 이 값을 다룰 때 실수하기 쉬운 지점이라 미리 적어둠.

<div style="margin-top: 60px;"></div>

## 3. 계측(hook) 지점 상세 ( Session 4~6 )

### 3-1. 주소 매핑 — `Address_Mapping_Unit_Page_Level.cpp`

- `query_cmt()` 안 : CMT hit/miss 판정 시점에 이벤트 발행( hit/miss 여부, LPA )
- `translate_lpa_to_ppa()` 안 : PPA 확정(매핑 갱신) 시점에 이벤트 발행 → 매핑 테이블 패널 갱신 트리거
- 기존 PPA가 있었다면 `Invalidate_page_in_block()` 호출 시점에 invalidate 이벤트

### 3-2. 블록 관리 — `Flash_Block_Manager.cpp` / `Flash_Block_Manager_Base.cpp`

- `Allocate_block_and_page_in_plane_for_user_write()` : free→valid 전환 이벤트( block/page grid 갱신 )
- `Add_erased_block_to_pool()` : erase 완료 후 free pool 복귀 이벤트
- `Program_transaction_serviced()`, `Invalidate_page_in_block()` : valid→invalid 전환 이벤트

### 3-3. GC — `GC_and_WL_Unit_Page_Level.cpp` / `GC_and_WL_Unit_Base.cpp`

> ⚠️ **( 9/6 정정 )** GC 실행에는 즉시 실행 경로( `Check_gc_required()`, Page_Level.cpp )와 다른 요청 때문에 지연됐다가 나중에 실행되는 경로( `handle_transaction_serviced_signal_from_PHY()`, **Base.cpp** )가 따로 있어서, 아래 hook 은 두 파일 모두에 추가했다. `Stats::Total_gc_executions`/`Stats::Total_page_movements_for_gc` 도 이 두 곳에서 나눠 증가하므로 검증 항목도 두 경로 합산 기준. 지연 실행 경로는 Session 6 의 static 마모평준화와 코드를 공유하고, MQSim 자신도 이 둘을 구분해서 세지 않는다(`Simulation_Events.h` 의 주석 참고).

- `Check_gc_required()` : GC 트리거 판단 + 정책별( GREEDY/RGA/RANDOM 계열/FIFO ) victim block 선정 결과 이벤트 ( 9/6 완료 — [PR #4](https://github.com/jonghoon-ryu/ftl-visual-simulator/pull/4), `GC_Started_Event`, 즉시/지연 두 실행 경로 모두 )
- valid page migration 루프 : 이동 중인 각 페이지 이벤트( read → 새 PPA 재기록 ) ( 9/6 완료 — `GC_Page_Migrated_Event` )
- block erase 실행 이벤트 ( 9/6 완료 — `GC_Block_Erased_Event`, erase 트랜잭션이 실제로 완료되는 시점 )
- **검증** : hook 이 카운트한 GC 실행 횟수가 `Stats::Total_gc_executions` 와 정확히 일치해야 함( 회귀 테스트 ) ( 9/6 완료 — 기본 샘플 설정은 GC 가 안 일어나서 GC_Exec_Threshold 를 임시로 높인 스트레스 설정으로 검증 : gc_started 17회/page migration 4323회 모두 Stats 와 정확히 일치, 결과 XML MD5 는 hook 추가 전후 동일 )

### 3-4. 마모 평준화 — `GC_and_WL_Unit_Base.cpp` / `Flash_Block_Manager_Base.cpp`

> ⚠️ **( 9/6 기록 ) static WL, dynamic WL hook 모두 완료.** 버그 수정([PR #5](https://github.com/jonghoon-ryu/ftl-visual-simulator/pull/5))과 static WL hook 추가([PR #7](https://github.com/jonghoon-ryu/ftl-visual-simulator/pull/7))를 별도 PR 로 분리했다. static WL 검증 중 원본 MQSim 버그 2개(`run_static_wearleveling()`의 블록 주소/ID 혼동, `Get_min_max_erase_difference()`의 인덱스-차 vs erase-count-차 혼동)를 발견해 고쳤다 — 상세 내용과 "이건 upstream 과 의도적으로 다르게 동작하기로 한 결정"이라는 점은 [마모 평준화 버그와 의도적 동작 변경](/ftl-visual-simulator/reference/bug-list/wl-bug-deviation/) 참고. dynamic WL 은 `PlaneBookKeepingType`( plane 좌표를 모르는 클래스 ) 자신이 아니라 이미 좌표를 갖고 있는 호출부(`Flash_Block_Manager.cpp`)에 계측했다 — GC/static WL 과 달리 매 write frontier 재배정마다 항상 관여해서 이벤트도 그만큼 자주 발생한다(기본 샘플만 돌려도 1493회).

- `PlaneBookKeepingType::Add_to_free_block_pool()` / `Get_a_free_block()` : dynamic WL 로 인해 어떤 블록이 다음 write frontier 로 선택됐는지 이벤트( erase count 최소 블록 우선 배정 ) ( 9/6 완료 — [PR #8](https://github.com/jonghoon-ryu/ftl-visual-simulator/pull/8), `Dynamic_WL_Block_Allocated_Event`/`Dynamic_WL_Block_Freed_Event`, 호출부 5곳에 계측 )
- `check_static_wl_required()` / `run_static_wearleveling()` : static WL 발동 이벤트( `Get_coldest_block_id()` 로 고른 블록 ) ( 9/6 완료 — `WL_Started_Event`/`WL_Page_Migrated_Event`/`WL_Block_Erased_Event`. 실제 발동은 재현 못했지만( 위 기록 참고 ) GC hook 과 동일 패턴으로 구현·회귀 테스트는 통과 )

### 3-5. 통계 — `Stats.h/cpp`

- 매 hook 이벤트와 최종 `Stats` 카운터(`Total_gc_executions`, `CMT_hits`/`CMT_miss` 등)를 1:1로 대조하는 회귀 테스트 자동화

<div style="margin-top: 60px;"></div>

## 4. 시각화 컴포넌트 ( Session 7~8 )

- **Flash array grid** : block/page 상태별 색상( valid/invalid/free/erasing ), hook 이벤트를 구독해 write/GC 실시간 애니메이션
- **매핑 테이블 뷰어** : `getState()` 스냅샷을 표시
- **이벤트 로그/타임라인** : hook 이벤트를 그대로 나열하지 않고 쉬운 말 설명으로 변환( 예: "block 12 GC 시작" → "block 12 가 꽉 차서 정리를 시작해요" )
- **통계 대시보드** : WAF, valid page 비율, GC/erase 횟수 + 지표별 "왜 중요한지" 한 줄 설명
- **재생 컨트롤** : step / play·pause / 속도 슬라이더 — WASM 을 Web Worker 로 실행해 속도 조절
- **범례·툴팁·색상 접근성** : 처음부터 포함( "나중에 다듬기" 아님, 초심자 학습 환경이 처음부터의 요구사항 )

<div style="margin-top: 60px;"></div>

## 5. 인터랙션 ( Session 9~10 )

- **파라미터 패널** : page 크기, block/page 개수, OP 비율, GC 임계값( `GC_Exec_Threshold`/`GC_Hard_Threshold` — ⚠️ 후자는 `Preemptible_GC_Enabled=true` 일 때만 실제로 의미 있음, [FTL 개념 ↔ 파라미터·모듈 대응](/ftl-visual-simulator/reference/mqsim/code-analysis/concept-mapping/) 참고 ), 매핑 방식 선택 — 각 항목에 쉬운 설명 툴팁 연결
- 파라미터 변경 시 값을 `ssdconfig.xml` 형식 텍스트로 재생성 → MEMFS 재기록 → WASM `configure()`(reset) 호출
- **개념별 프리셋 버튼** : "매핑 기본" / "GC 시연"( OP 비율 낮춤 ) / "마모평준화 시연"( 특정 block 에 쓰기 집중 ) — 파라미터와 workload 를 함께 전환
- **workload 컨트롤** : sequential/random, read/write 비율, burst 크기 → `workload.xml` 형식으로 생성
- ( 선택 ) 커스텀 trace 파일 업로드 → MEMFS 마운트 → 기존 trace 파싱 코드로 실행
- 입력값 검증 및 파라미터 범위 제한

<div style="margin-top: 60px;"></div>

## 6. 마무리 & 배포 ( Session 11~12 )

- UI 다듬기( 범례, 툴팁, 반응형 레이아웃, 색상 접근성 재점검 )
- 버그 수정, 크로스 브라우저 확인
- README / 동작 원리 문서 작성
- 최종 테스트, GitHub Pages 배포

<div style="margin-top: 60px;"></div>

## 7. 확장 목표 구현 상세 ( 13~16번 버퍼 )

### 7-1. Cost-Benefit GC 정책

- `GC_and_WL_Unit_Base.h` 의 `GC_Block_Selection_Policy_Type` enum 에 `COST_BENEFIT` 값 추가
- ⚠️ **`Block_Pool_Slot_Type` 에 age 정보가 없음** — 지금 코드엔 "마지막으로 valid page 가 갱신된 시각" 같은 필드가 없어서 새로 추가해야 함( `GC_and_WL_Unit_Page_Level.cpp` §13 정확성 노트 참고 )
- `GC_and_WL_Unit_Page_Level.cpp` 의 `Check_gc_required()` switch-case 에 `COST_BENEFIT` 분기 추가 : `age × (1-u)/(1+u)`( u = valid page 비율 )가 최대인 블록 선택
- RGA 와 비교 검증 : 같은 workload 로 `Total_GC_Executions`, WAF, 평균 응답시간 비교

### 7-2. Hybrid(log-block) 매핑

- ⚠️ **`Address_Mapping_Unit_Hybrid.cpp` 가 현재 전부 빈 스텁**( 53줄, 모든 메서드가 `{}` 또는 `return 0` ) — [MQSim 개괄](/ftl-visual-simulator/reference/mqsim/code-analysis/overview/)의 정확성 노트 참고
- `Translate_lpa_to_ppa_and_dispatch()` 부터 실제 log-block 로직을 새로 구현해야 함
- log block pool 관리, switch/partial/full merge 로직 새로 작성
- `Address_Mapping_Unit_Page_Level` 의 구조( `Cached_Mapping_Table`, `AddressMappingDomain` )를 참고해 유사한 형태로 구현

### 7-3. GTest/GMock 테스트 스위트

- Session 4 의 라이브러리 분리 리팩터링 시점에 테스트 바이너리 연결( 1장 참고 — 같은 리팩터링을 두 번 하지 않기 위함 )
- **골든/회귀 테스트**( GMock 불필요 ) : 고정 시나리오 실행 → 결과 통계 스냅샷 비교 ( 9/6 완료 — `engine/run-regression-tests.sh`/`npm run test:engine`, 샘플 시나리오 3개 결과를 `engine/tests/golden/` 과 바이트 단위 비교. 매핑/GC hook 검증 때마다 임시로 만들던 테스트를 저장소에 남는 형태로 정리한 것 )
- **단위 테스트**( GMock 필요 ) : `Address_Mapping_Unit_Base`/`Flash_Block_Manager_Base`/`GC_and_WL_Unit_Base`/`TSU_Base` 4개 추상 인터페이스를 mock 으로 갈아끼워 매핑/GC 로직만 격리 테스트 — Cost-Benefit GC 같은 새 로직 검증에 특히 유용

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [개발 계획](/ftl-visual-simulator/plan/) · [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) · [MQSim 코드 분석 계획](/ftl-visual-simulator/plan/code-analysis-plan/) · [MQSim 개괄](/ftl-visual-simulator/reference/mqsim/code-analysis/overview/) · [FTL 개념 ↔ 파라미터·모듈 대응](/ftl-visual-simulator/reference/mqsim/code-analysis/concept-mapping/)

<script>
(function () {
  // 이 문서는 전부 "Claude 가 할 일" 스펙이라 모든 체크박스가 Claude 전용(초록색, 비활성)이다.
  // Ryu 가 클릭해서 바꾸는 게 아니라, Claude 가 작업을 끝낼 때마다 이 파일을 직접 고쳐서
  // 아래 CLAUDE_DONE 에 항목을 추가하고, 필요하면 comment 를 덧붙인다.
  // "0. 전체 아키텍처"(확정된 결정 사항 나열, 할 일 아님)와 "참고"(링크 모음)는 체크박스 대상에서 제외.
  // key 형식 : 'i{번호}' — 제외 구간(0장, 인용구, 참고)을 뺀 나머지 목록을, 문서에 나오는 순서대로 0부터 센 것.
  var CLAUDE_DONE = {
    'i0': true,
    'i1': true,
    'i2': true,
    'i5': { comment: '9/6 완료 (PR #3) - read/write 두 분기 모두에서 발행. getState()/setEventCallback 바인딩도 함께 구현' },
    'i10': true,
    'i11': true,
    'i12': true,
    'i13': true,
    'i14': true,
    'i15': true,
    'i42': true
  };
  var SKIP_HEADINGS = ['0. 전체 아키텍처', '참고'];

  document.addEventListener('DOMContentLoaded', function () {
    var container = document.getElementById('main_content');
    if (!container) return;

    var skip = false;
    var idx = 0;

    Array.prototype.forEach.call(container.children, function (el) {
      if (/^H[1-4]$/.test(el.tagName)) {
        skip = SKIP_HEADINGS.indexOf(el.textContent.trim()) !== -1;
        return;
      }
      if (skip || el.tagName === 'BLOCKQUOTE') return;
      if (el.tagName !== 'UL' && el.tagName !== 'OL') return;

      el.querySelectorAll('li').forEach(function (li) {
        var itemId = 'i' + idx;
        idx++;

        var done = CLAUDE_DONE[itemId];
        var cb = document.createElement('input');
        cb.type = 'checkbox';
        cb.className = 'item-check';
        cb.checked = !!done;
        cb.title = 'Claude 가 작업 완료 시 직접 표시하는 항목';
        cb.addEventListener('click', function (e) { e.preventDefault(); });

        if (done && typeof done === 'object' && done.comment) {
          var note = document.createElement('span');
          note.className = 'item-comment';
          note.textContent = '— ' + done.comment;
          li.appendChild(note);
        }

        li.insertBefore(cb, li.firstChild);
      });
    });
  });
})();
</script>
