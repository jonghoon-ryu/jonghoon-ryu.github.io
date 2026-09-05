---
layout: default
title: WASM · em++ 입문
permalink: /ftl-visual-simulator/reference/wasm-primer/
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
</style>

# WASM · em++ 입문

이 프로젝트를 진행하면서 "WASM", "em++", "라이브러리화", "hook" 같은 낯선 말이 계속 나온다. 이 문서는 **그 용어들이 정확히 뭔지, 그리고 앞으로 진행할 작업들이 왜 필요한지**를, WASM/em++ 를 전혀 몰라도 이해할 수 있게 정리한 것. [개발 계획](/ftl-visual-simulator/plan/)에서 "이 작업을 왜 하는지"가 궁금해질 때마다 돌아와서 참고하면 된다.

<div style="margin-top: 60px;"></div>

## 1. WASM 이 뭔가요?

**WASM(WebAssembly)** 은 브라우저 안에서 실행할 수 있는, JavaScript 가 아닌 다른 형태의 프로그램 실행 방식이다.

원래 브라우저에서 동작하는 언어는 JavaScript 하나뿐이었다. 그런데 C++/Rust 같은 언어로 이미 짜여진, 검증된 프로그램을 브라우저에서 그대로 돌리고 싶은 경우가 많다 — 이 프로젝트의 MQSim 이 정확히 그런 경우다. WASM 은 이런 언어로 짠 코드를 미리 컴파일해서, 브라우저가 이해할 수 있는 이진 형식으로 바꿔주는 실행 형식이다. JavaScript 엔진 옆에서 같이 돌아가며, JS 보다 훨씬 빠르게 실행된다(원래 컴파일 언어의 속도에 가깝다).

비유하자면 : JavaScript 가 "브라우저 안에서 태어난 언어"라면, WASM 은 "다른 언어로 이미 짠 프로그램을 브라우저 안으로 들여오는 통로"다. 이 프로젝트에서는 이 통로를 통해 **MQSim(C++ 로 짠 실제 SSD 시뮬레이터)을 브라우저 안으로 그대로 들여오는 것**이 목표다.

<div style="margin-top: 40px;"></div>

## 2. em++ 가 뭔가요?

WASM 은 "실행 형식"일 뿐, C++ 소스 코드를 WASM 으로 바꿔주는 건 별도의 **컴파일러**가 해야 한다. 그 컴파일러가 **Emscripten** 이고, `em++` 는 Emscripten 이 제공하는 "C++ 전용 컴파일러 명령어" 이름이다.

이미 익숙한 것에 비유하면 이해가 빠르다 — 지금까지 MQSim 은 `g++`(리눅스용 C++ 컴파일러)로 빌드해서 "내 컴퓨터에서 바로 실행되는 프로그램"을 만들었다. `em++` 는 그 자리에 그대로 넣어 쓰는, "브라우저에서 실행되는 프로그램(WASM)을 만드는 컴파일러" 다. 명령어 사용법도 g++ 와 거의 똑같다( `g++ file.cpp -o app` → `em++ file.cpp -o app.js` ). 실제로 9/5 에 확인해본 결과, MQSim 소스 61개 파일이 **코드 수정 없이 em++ 로 그대로 컴파일** 됐다( [Claude 구현 작업 상세](/ftl-visual-simulator/plan/implementation/) 1장의 "사전 조사" 참고 ).

`em++` 를 실행하면 두 개의 파일이 나온다.

- `.wasm` : 실제로 실행되는 이진 코드( MQSim 의 로직이 통째로 들어있음 )
- `.js` : 그 `.wasm` 파일을 브라우저에서 불러오고, JavaScript 에서 호출할 수 있게 이어주는 "접착제(glue)" 코드

React 코드 입장에서는, 이 `.js` 파일이 내보내는 함수들을 마치 npm 라이브러리를 `import` 해서 쓰듯이 호출하면 된다 — 그 함수 뒤에서 실제로는 C++ 로 짠 MQSim 로직이 돌아가고 있다는 점만 다르다.

<div style="margin-top: 60px;"></div>

## 3. 왜 굳이 MQSim 을 통째로 WASM 으로 컴파일하나요?

FTL 개념( 매핑, GC, 마모 평준화 )을 보여주는 화면만 필요하다면, TypeScript 로 비슷하게 흉내 낸 엔진을 새로 짜는 방법도 있었다. 그런데 그러면 "MQSim 이 실제로 하는 동작"이 아니라 "우리가 이해한 대로 다시 짠 동작"을 보여주는 셈이 된다 — 미묘하게 실제와 다를 위험이 항상 있다.

그래서 [개발 계획](/ftl-visual-simulator/plan/) 초반에 "힘들어도 정확하게 하자"는 원칙으로, **MQSim 원본 C++ 코드를 그대로 WASM 으로 컴파일해서 쓰기로 결정**했다. 이렇게 하면 시뮬레이터가 보여주는 모든 동작이 MQSim 논문/코드와 100% 동일하다는 게 보장된다 — 대가로 WASM 컴파일이라는 낯선 작업이 필요해진 것.

<div style="margin-top: 60px;"></div>

## 4. 지금 MQSim 은 "한 번 실행하고 끝나는 프로그램" 이다

여기서부터가 핵심이다. **WASM 으로 컴파일한다고 해서 프로그램의 구조 자체가 저절로 바뀌지는 않는다.** 지금 MQSim 의 `main.cpp` 는 이렇게 짜여 있다.

1. `-i`/`-w` 옵션으로 받은 설정 파일(`ssdconfig.xml`, `workload.xml`)을 읽는다
2. 시나리오별로 `SSD_Device`/`Host_System` 을 만들고, `Simulator->Start_simulation()` 으로 **시뮬레이션을 끝까지 통째로 돌린다**
3. 다 끝나면 결과를 `result.xml` 에 쓰고, **프로세스가 종료된다**

이건 전형적인 "배치(batch) 프로그램" 구조다 — 명령어 한 줄 실행하면, 중간에 아무것도 보여주지 않다가, 끝나야 결과 파일 하나가 뚝 떨어진다. `em++` 로 컴파일해도 이 구조는 그대로 남는다 — "한 번 실행되고 끝나는 프로그램"을 "브라우저에서 한 번 실행되고 끝나는 프로그램"으로 옮겨온 것 뿐이다.

<div style="overflow-x:auto;">
<svg viewBox="0 0 900 420" style="width:100%;max-width:760px;height:auto;display:block;margin:1.5rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs>
    <marker id="arrow-wp1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/>
    </marker>
  </defs>
  <style>
    .box { fill:#eef2f7; stroke:#34495e; stroke-width:2; }
    .boxAlt { fill:#eafaf1; stroke:#1e8449; stroke-width:2; }
    .title { fill:#2c3e50; font-size:14px; font-weight:700; text-anchor:middle; }
    .titleAlt { fill:#196f3d; font-size:14px; font-weight:700; text-anchor:middle; }
    .body { fill:#3d4a5a; font-size:11px; text-anchor:middle; }
    .flow { stroke:#7f8c8d; stroke-width:2; marker-end:url(#arrow-wp1); fill:none; }
    .flowAlt { stroke:#1e8449; stroke-width:2; marker-end:url(#arrow-wp1); fill:none; }
    .rowlabel { fill:#2c3e50; font-size:13px; font-weight:700; }
    .note { fill:#7f8c8d; font-size:11px; font-style:italic; }
  </style>

  <text x="10" y="25" class="rowlabel">Before — 지금 그대로 컴파일하면 ( batch, 1회성 )</text>

  <rect x="10" y="45" width="200" height="90" rx="8" class="box"/>
  <text x="110" y="80" class="title">ssdconfig.xml</text>
  <text x="110" y="98" class="title">workload.xml</text>
  <text x="110" y="122" class="body">설정 파일</text>

  <line x1="210" y1="90" x2="250" y2="90" class="flow"/>

  <rect x="250" y="45" width="260" height="90" rx="8" class="box"/>
  <text x="380" y="75" class="title">main() 실행</text>
  <text x="380" y="98" class="body">파싱 → 시뮬레이션</text>
  <text x="380" y="115" class="body">처음부터 끝까지 한 번에</text>

  <line x1="510" y1="90" x2="550" y2="90" class="flow"/>

  <rect x="550" y="45" width="250" height="90" rx="8" class="box"/>
  <text x="675" y="75" class="title">result.xml 저장</text>
  <text x="675" y="98" class="body">프로세스 종료</text>
  <text x="675" y="115" class="body">(WASM 이면 모듈 종료)</text>

  <text x="450" y="165" text-anchor="middle" class="note">중간에 "지금 몇 번 블록에서 GC 중" 같은 걸 물어볼 방법이 없음 — 끝나야 결과가 나옴</text>

  <line x1="20" y1="200" x2="880" y2="200" stroke="#ddd" stroke-width="1"/>

  <text x="10" y="235" class="rowlabel">After — 이번 프로젝트가 만들 구조 ( 라이브러리, 여러 번 호출 )</text>

  <rect x="10" y="255" width="190" height="130" rx="8" class="boxAlt"/>
  <text x="105" y="285" class="titleAlt">웹 UI</text>
  <text x="105" y="303" class="titleAlt">(React)</text>
  <text x="105" y="330" class="body">재생·일시정지·스텝</text>
  <text x="105" y="347" class="body">파라미터 패널</text>

  <line x1="200" y1="295" x2="245" y2="295" class="flowAlt"/>
  <text x="222" y="288" text-anchor="middle" class="note" font-size="10">호출</text>
  <line x1="245" y1="345" x2="200" y2="345" class="flowAlt"/>
  <text x="222" y="362" text-anchor="middle" class="note" font-size="10">이벤트·상태</text>

  <rect x="245" y="255" width="280" height="130" rx="8" class="boxAlt"/>
  <text x="385" y="280" class="titleAlt">WASM 모듈 (라이브러리)</text>
  <text x="385" y="302" class="body">init() · step() · run(n)</text>
  <text x="385" y="319" class="body">getState() · configure()</text>
  <text x="385" y="340" class="body" font-weight="700">필요할 때마다 반복 호출 가능</text>

  <line x1="525" y1="295" x2="565" y2="295" class="flowAlt"/>

  <rect x="565" y="255" width="325" height="130" rx="8" class="boxAlt"/>
  <text x="727" y="280" class="titleAlt">FTL 코드 속 hook</text>
  <text x="727" y="302" class="body">매핑 갱신 · GC 시작/victim</text>
  <text x="727" y="319" class="body">선정·migration·erase · WL 발동</text>
  <text x="727" y="340" class="body" font-weight="700">일어나는 즉시 JS 로 통지</text>
</svg>
</div>

<div style="margin-top: 60px;"></div>

## 5. 그래서 `main.cpp` 를 왜 "라이브러리로" 바꿔야 하나요?

위 그림의 Before → After 를 만들려면, `main()` 안에 지금 다 뭉쳐 있는 로직( 파싱 → 시뮬레이션 루프 → 결과 저장 )을 **각각 따로 호출할 수 있는 여러 개의 함수**로 쪼개야 한다. 이게 "라이브러리화"의 실체다 — 어렵게 들리지만, "하나로 뭉쳐서 한 번만 실행되는 코드"를 "여러 조각으로 나눠서 필요할 때마다 하나씩 실행되는 함수들"로 바꾸는 것 뿐이다.

왜 이게 꼭 필요한가 하면, 시각화 시뮬레이터가 하려는 것 자체가 지금 구조로는 불가능하기 때문이다.

- **재생 컨트롤**( step / play·pause / 속도 조절 )을 만들려면, "이벤트 딱 하나만 실행하고 멈추기"가 가능해야 한다. 지금 `main()` 은 한 번 시작하면 끝까지 멈추지 않고 실행된다 — 중간에 멈춰서 한 걸음씩 보여줄 수가 없다.
- **매핑 테이블 뷰어/통계 대시보드**는 시뮬레이션이 진행되는 중간중간 "지금 상태 좀 보여줘" 라고 물어봐야 한다. 지금 구조는 다 끝나야 `result.xml` 하나를 뱉을 뿐, 중간 상태를 물어볼 방법 자체가 없다.
- **파라미터를 바꾸면 다시 시작**하려면, 처음부터 다시 초기화할 수 있어야 한다. 지금 구조는 프로세스가 한 번 끝나면(=WASM 이면 모듈이 끝나면) 그걸로 끝이다 — 다시 쓰려면 처음부터 새로 만들어야 하는데, 이건 매번 페이지를 새로고침하는 것과 다름없다.

그래서 Session 4 에서 `main()` 의 흐름을 `init(config)` / `step()` / `getState()` / `configure()` 같은, **독립적으로 몇 번이고 다시 호출할 수 있는 함수들**로 나누는 리팩터링을 한다( 표는 [Claude 구현 작업 상세](/ftl-visual-simulator/plan/implementation/) 2장 참고 ). 이 작업이 끝나야 비로소 WASM 으로 컴파일한 MQSim 이 "한 번 쓰고 버리는 배치 프로그램"에서 "브라우저가 계속 말 걸 수 있는 라이브러리"가 된다.

( 덧붙이면, 이 리팩터링은 나중에 GTest/GMock 테스트를 붙일 때도 그대로 필요한 작업이라 — 어차피 한 번은 해야 하니 Session 4 에서 미리 해두는 것이 시간을 아끼는 길이다. )

<div style="margin-top: 60px;"></div>

## 6. hook(계측)은 왜 필요한가요?

라이브러리화만 해도 "재생/멈춤/상태 조회"는 가능해진다. 그런데 그것만으로는 화면에 **"지금 이 순간 무슨 일이 일어나고 있는지"** 를 보여줄 수 없다.

이유는, MQSim 이 결과를 남기는 방식 자체가 "다 끝난 뒤 최종 집계만 `Stats` 로 모아서 XML 에 쓰는" 방식이기 때문이다. 예를 들어 GC 가 어떤 블록에서 몇 번 일어났는지는 최종 통계로는 알 수 있어도, **"몇 번째 write 요청 직후에, 몇 번 block 에서 GC 가 시작됐는지"** 같은 시점별 사건은 MQSim 안 어디에도 남지 않는다 — 코드가 그 순간 딱 알고 지나갈 뿐이다.

**hook** 은 바로 그 "코드가 알고 지나가는 그 순간"에, "이 사실을 JS 한테도 알려줘" 라는 코드 몇 줄을 끼워 넣는 것이다. 예를 들어 `Address_Mapping_Unit_Page_Level.cpp` 의 `translate_lpa_to_ppa()` 함수는 원래 "매핑을 갱신하고 다음 코드로 넘어갈 뿐"이지만, 여기에 한 줄을 추가해서 "매핑이 갱신됐다"는 사건을 즉시 JS 쪽으로 통지하게 만드는 식이다. 원래 로직은 전혀 바뀌지 않고, "이 일이 일어났다는 걸 밖으로 알려주는" 코드만 옆에 덧붙는 것 — 그래서 hook 을 다 추가해도 시뮬레이션 결과 자체( `Stats` 값들 )는 hook 이 없을 때와 정확히 똑같아야 한다( [Claude 구현 작업 상세](/ftl-visual-simulator/plan/implementation/) 3장의 "hook 이 카운트한 값과 `Stats` 값이 정확히 일치해야 함" 검증이 이 얘기다 ).

정리하면 : 라이브러리화가 "언제든 실행/조회할 수 있게" 만드는 작업이라면, hook 은 "실행되는 동안 무슨 일이 있었는지 하나하나 알려주게" 만드는 작업이다. 시각화 시뮬레이터에는 둘 다 필요하다.

<div style="margin-top: 60px;"></div>

## 7. 파라미터 입력은 왜 "가짜 파일(MEMFS)" 방식인가요?

파라미터 패널에서 OP 비율이나 GC 임계값을 바꾸면, 그 값을 MQSim 에 어떻게 전달할까? 가장 간단한 방법은 **MQSim 이 원래 하던 방식을 그대로 쓰는 것**이다 — MQSim 은 `ssdconfig.xml`/`workload.xml` 파일을 열어서 읽는 것으로 설정을 받는다( `read_configuration_parameters`, `read_workload_definitions` ).

문제는, 브라우저 안의 WASM 프로그램은 보안상 당연히 **컴퓨터의 진짜 파일 시스템에 접근할 수 없다**. 그런데 MQSim 코드는 "파일을 열어서 읽는" 코드로 가득 차 있다 — 이걸 전부 "문자열을 파싱하는 코드"로 새로 고쳐 쓰면, 그 과정에서 원본과 미묘하게 다른 동작이 섞여 들어갈 위험이 생긴다( 3번 항목에서 얘기한, TS 로 새로 짜지 않기로 한 이유와 같은 문제 ).

Emscripten 은 이 문제를 해결하는 **MEMFS( 메모리 파일 시스템 )** 라는 걸 제공한다 — WASM 프로그램 안에 "가짜 파일 시스템"을 하나 만들어 주는 것이다. 이 가짜 파일 시스템에 "ssdconfig.xml" 이라는 이름으로 문자열을 넣어두면, MQSim 의 `ifstream`( 파일 읽기 ) 코드는 그게 가짜라는 걸 전혀 모른 채 평소처럼 파일을 열어서 읽는다. 그래서 이 프로젝트는 :

1. 파라미터 패널에서 값이 바뀌면, JS 에서 그 값들로 `ssdconfig.xml` 형식의 문자열을 만들고
2. 그 문자열을 MEMFS 에 "ssdconfig.xml" 이라는 이름으로 써넣은 뒤
3. WASM 의 `configure()` 를 호출하면, **MQSim 의 원본 파싱 코드가 그 파일을 그대로 읽어서** 새 설정을 적용한다

이렇게 하면 XML 파서를 새로 짤 필요가 없고, MQSim 의 검증된 파싱 로직을 한 글자도 안 고치고 그대로 재사용할 수 있다.

<div style="margin-top: 60px;"></div>

## 8. 용어 정리

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>용어</th><th>한 줄 설명</th></tr>
<tr><td>WASM (WebAssembly)</td><td>C++ 같은 다른 언어로 짠 프로그램을 브라우저에서 거의 원본 속도로 실행할 수 있게 해주는 실행 형식</td></tr>
<tr><td>Emscripten / em++</td><td>C++ 소스를 WASM 으로 바꿔주는 컴파일러. `g++` 자리에 그대로 넣어 쓰면 됨( C 코드는 `emcc`, C++ 코드는 `em++` )</td></tr>
<tr><td>MEMFS</td><td>Emscripten 이 제공하는 "가짜 파일 시스템". 문자열을 파일처럼 넣어두면 원본 코드의 파일 읽기 로직을 그대로 재사용할 수 있음</td></tr>
<tr><td>라이브러리화</td><td>`main()` 안에 뭉쳐 있던 "한 번 실행하고 끝" 로직을, `init()`/`step()`/`getState()` 처럼 여러 번 따로 호출 가능한 함수들로 쪼개는 작업</td></tr>
<tr><td>hook(계측)</td><td>원래 로직은 그대로 두고, "이 사건이 일어났다"는 사실만 그 자리에서 JS 로 즉시 통지하도록 코드를 덧붙이는 것</td></tr>
<tr><td>바인딩(binding) 레이어</td><td>WASM 모듈이 내보내는 함수들과 React 상태를 이어주는 얇은 JS/TS 코드. React 쪽에서는 C++ 이 뒤에 있다는 걸 몰라도 됨</td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [Claude 구현 작업 상세](/ftl-visual-simulator/plan/implementation/) — 이 문서에서 설명한 개념들이 실제로 어느 파일·함수에 적용되는지의 상세 스펙
- [MQSim](/ftl-visual-simulator/reference/mqsim/) — WASM 으로 컴파일하는 대상 자체에 대한 문서
- [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) — Session 4~6 이 바로 이 문서에서 설명한 작업들
- [ftl-visual-simulator 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator) — 실제 코드
