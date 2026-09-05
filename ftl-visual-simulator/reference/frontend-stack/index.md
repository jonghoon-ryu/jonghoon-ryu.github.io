---
layout: default
title: 프론트엔드 스택 입문 (Vite · React · TS)
permalink: /ftl-visual-simulator/reference/frontend-stack/
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

# 프론트엔드 스택 입문 (Vite · React · TS)

[개발 계획](/ftl-visual-simulator/plan/) 과 [Claude 구현 작업 상세](/ftl-visual-simulator/plan/implementation/) 에 "Vite", "React", "TS(TypeScript)", "scaffold" 같은 말이 아무 설명 없이 등장한다. 이 문서는 **이 세 가지가 각각 뭔지, 그리고 이 프로젝트에 왜 필요한지**를 프론트엔드를 전혀 몰라도 이해할 수 있게 정리한 것이다. [WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/) 이 "엔진(MQSim)을 브라우저로 들여오는 방법"에 대한 문서라면, 이 문서는 "그 엔진을 사람이 볼 수 있는 화면으로 보여주는 방법"에 대한 문서다.

<div style="margin-top: 60px;"></div>

## 0. 이 셋은 왜 같이 다니나요?

WASM 으로 컴파일한 MQSim 은 **화면이 없다.** 함수를 호출하면 값을 돌려주는 라이브러리일 뿐이다 — flash grid 를 그려주지도, 버튼을 보여주지도 않는다. 그 "값을 받아서 사람이 보는 화면으로 그려주는" 역할을 하는 게 프론트엔드 코드인데, 이걸 처음부터 순수 JavaScript 로 손으로 짜는 대신, 이 프로젝트는 세 가지 도구를 조합해서 쓴다.

- **React** — 화면을 어떻게 "구성"할지 (버튼을 누르면 grid 가 다시 그려지는 방식)
- **TypeScript(TS)** — 그 화면 코드를 어떤 "언어"로 쓸지 (오타·타입 실수를 미리 잡아주는 JS)
- **Vite** — 그 코드를 브라우저가 실행할 수 있는 파일로 어떻게 "빌드"할지, 그리고 개발 중엔 어떻게 빠르게 미리보기 할지

셋 다 처음 들으면 낯설지만, 이미 알고 있는 MQSim/WASM 쪽 작업과 정확히 대응되는 개념들이라 하나씩 비유를 붙여가며 보면 어렵지 않다.

<div style="margin-top: 60px;"></div>

## 1. React 가 뭔가요?

**React** 는 "화면을 이루는 조각(컴포넌트)들을 만들고, 데이터가 바뀌면 화면에서 바뀐 부분만 알아서 다시 그려주는" JavaScript 라이브러리다.

비유하자면 : 순수 JavaScript 로 화면을 만들면, "값이 바뀌었으니 이 부분 지우고 다시 그려라" 를 개발자가 일일이 코드로 지시해야 한다. React 는 "지금 데이터가 이렇게 생겼다" 라고만 선언해두면, 데이터가 바뀔 때 어디를 다시 그려야 하는지는 React 가 알아서 계산해서 처리해준다.

**이 프로젝트에 왜 필요한가** — 이 시뮬레이터의 화면은 가만히 있지 않는다. WASM 에서 매 스텝마다 이벤트가 날아오고(매핑 갱신, GC 시작, block 상태 변경), 그때마다 flash grid 의 특정 칸 색깔, 매핑 테이블의 특정 행, 통계 대시보드의 숫자가 바뀌어야 한다. 이런 "데이터가 계속 바뀌고, 그때마다 화면 여기저기가 갱신되는" 화면을 손으로 관리하려면 코드가 금방 엉킨다. React 의 "데이터 → 화면" 자동 갱신 모델이 정확히 이 문제를 풀어준다. 또한 flash grid / 매핑 테이블 뷰 / 파라미터 패널 / 이벤트 로그 / 통계 대시보드처럼 화면이 여러 독립된 조각으로 나뉘는 구조도, React 의 "컴포넌트" 단위와 잘 맞는다.

<div style="margin-top: 40px;"></div>

## 2. TypeScript(TS) 가 뭔가요?

**TypeScript** 는 "타입 검사 기능이 추가된 JavaScript" 다. JS 코드에 `숫자만 들어와야 한다`, `이 객체는 반드시 이런 필드를 가져야 한다` 같은 규칙(타입)을 적어두면, 코드를 실행하기도 전에 실수를 잡아준다.

비유하자면 : C++ 에서 함수 시그니처에 `int`, `std::string` 같은 타입을 적어두면 컴파일러가 틀린 타입을 넘기는 실수를 바로 잡아주는 것과 똑같은 원리다. 순수 JavaScript 는 이런 검사가 전혀 없어서, 오타나 타입 실수가 코드를 실제로 실행할 때(그것도 특정 조건에서만) 뒤늦게 드러난다. TypeScript 는 그 검사를 코드 작성 시점으로 앞당겨준다.

**이 프로젝트에 왜 필요한가** — WASM 쪽에서 JS 로 넘어오는 데이터가 단순하지 않다. hook 이벤트마다 필드가 다르고(매핑 갱신 이벤트엔 LPA/PPA, GC 이벤트엔 victim block 번호가 필요한 식), `getState()` 가 돌려주는 매핑 테이블 스냅샷도 구조가 있는 데이터다. 이런 데이터를 다루는 코드를 순수 JS 로 짜면, "이벤트 객체에 이 필드가 있는 줄 알았는데 없어서 화면이 깨지는" 식의 실수가 나중에야 (그것도 브라우저에서 눈으로 봐야) 발견된다. TypeScript 로 각 hook 이벤트·WASM 바인딩 함수의 타입을 미리 정의해두면, 이런 실수를 코드 작성 중에 바로 잡을 수 있다 — MQSim 원본이 C++ 로 타입이 엄격한 언어인 것과 스타일을 맞추는 선택이기도 하다.

<div style="margin-top: 40px;"></div>

## 3. Vite 가 뭔가요?

**Vite** 는 React + TypeScript 로 짠 소스 코드를, 브라우저가 바로 실행할 수 있는 HTML/JS/CSS 파일 묶음으로 변환해주는 **빌드 도구** 다. 개발 중에는 코드를 수정하는 즉시 브라우저 화면에 반영해주는 개발 서버 역할도 한다.

비유하자면 : `em++` 가 "C++ 소스를 브라우저가 실행할 수 있는 WASM 으로 바꿔주는 컴파일러" 였던 것처럼, Vite 는 "React/TS 소스를 브라우저가 실행할 수 있는 JS/HTML/CSS 로 바꿔주는 컴파일러 + 번들러" 다. 브라우저는 TypeScript 나 React 문법(JSX)을 원래 이해하지 못한다 — Vite 가 이걸 평범한 JavaScript 로 미리 변환·정리해줘야 한다.

**이 프로젝트에 왜 필요한가** — 이 프로젝트는 최종적으로 **GitHub Pages** 에 정적 파일로 배포된다( 서버 프로그램 없이, HTML/JS/CSS 파일만 올려두는 방식 ). React/TS 소스 코드 자체는 그대로 올릴 수 없고, 반드시 "빌드"라는 과정을 거쳐 순수 HTML/JS/CSS 묶음으로 만들어야 하는데, 그 역할을 Vite 가 담당한다. 또, 개발 중에는 코드를 한 줄 고칠 때마다 처음부터 다시 빌드하면 너무 느린데, Vite 는 바뀐 부분만 즉시 반영해주는 속도가 특히 빨라서( 다른 도구 대비 개발 생산성 이점이 크다는 것이 채택 이유 ) 이 프로젝트처럼 hook 이벤트를 눈으로 보며 화면을 계속 조정해야 하는 작업에 잘 맞는다.

<div style="margin-top: 40px;"></div>

## 4. "scaffold" 는 또 뭔가요?

**scaffold(스캐폴드)** 는 원래 건물을 지을 때 세우는 "비계(가설 구조물)"를 뜻하는 말이다. 소프트웨어에서는 **프로젝트를 처음 시작할 때 필요한 기본 폴더/설정 파일 뼈대를 도구가 자동으로 만들어주는 것**을 가리킨다.

명령어 하나(`npm create vite@latest`)를 실행하면, React+TS 프로젝트에 필요한 폴더 구조, 설정 파일, "Hello World" 수준의 기본 코드가 자동으로 생성된다. 이후 작업은 이 뼈대 위에 실제 컴포넌트(flash grid, 매핑 테이블 뷰 등)를 채워 넣는 방식으로 진행된다.

**이 프로젝트에 왜 필요한가** — MQSim 을 g++ 로 처음 빌드했을 때 이미 완성된 소스 트리가 있었던 것과 달리, 화면 쪽은 아무것도 없는 상태에서 시작해야 한다. scaffold 를 쓰면 "React/TS/Vite 가 서로 맞물려 돌아가게 만드는" 초기 설정( 어떤 파일이 어떤 파일을 불러오는지, 빌드 설정이 뭔지 )을 처음부터 손으로 짜지 않고, 검증된 기본값으로 바로 시작할 수 있다. [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) Session 3~4 에서 "scaffold" 라고 부르는 것이 바로 이 초기 뼈대 생성 작업이다.

<div style="margin-top: 60px;"></div>

## 5. 넷이 실제로 어떻게 맞물리나요?

<div style="overflow-x:auto;">
<svg viewBox="0 0 900 260" style="width:100%;max-width:760px;height:auto;display:block;margin:1.5rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic',sans-serif">
  <defs>
    <marker id="arrow-fe1" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto-start-reverse">
      <path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/>
    </marker>
  </defs>
  <style>
    .box { fill:#eef2f7; stroke:#34495e; stroke-width:2; }
    .boxAlt { fill:#eafaf1; stroke:#1e8449; stroke-width:2; }
    .title { fill:#2c3e50; font-size:14px; font-weight:700; text-anchor:middle; }
    .titleAlt { fill:#196f3d; font-size:14px; font-weight:700; text-anchor:middle; }
    .body { fill:#3d4a5a; font-size:11px; text-anchor:middle; }
    .flow { stroke:#7f8c8d; stroke-width:2; marker-end:url(#arrow-fe1); fill:none; }
    .note { fill:#7f8c8d; font-size:11px; font-style:italic; text-anchor:middle; }
  </style>

  <rect x="10" y="30" width="220" height="90" rx="8" class="box"/>
  <text x="120" y="60" class="title">.tsx 소스 코드</text>
  <text x="120" y="82" class="body">React 컴포넌트</text>
  <text x="120" y="99" class="body">(TypeScript 문법)</text>

  <line x1="230" y1="75" x2="270" y2="75" class="flow"/>

  <rect x="270" y="30" width="200" height="90" rx="8" class="box"/>
  <text x="370" y="60" class="title">Vite</text>
  <text x="370" y="82" class="body">빌드 / 개발 서버</text>
  <text x="370" y="99" class="body">(TS+JSX → JS 변환)</text>

  <line x1="470" y1="75" x2="510" y2="75" class="flow"/>

  <rect x="510" y="30" width="200" height="90" rx="8" class="boxAlt"/>
  <text x="610" y="60" class="titleAlt">브라우저 화면</text>
  <text x="610" y="82" class="body">flash grid · 매핑 테이블</text>
  <text x="610" y="99" class="body">파라미터 패널 등</text>

  <line x1="710" y1="55" x2="750" y2="55" class="flow"/>
  <text x="730" y="45" class="note" font-size="10">호출</text>
  <line x1="750" y1="95" x2="710" y2="95" class="flow"/>
  <text x="730" y="112" class="note" font-size="10">이벤트·상태</text>

  <rect x="750" y="30" width="140" height="90" rx="8" class="box"/>
  <text x="820" y="60" class="title">WASM 모듈</text>
  <text x="820" y="82" class="body">(MQSim, em++ 로</text>
  <text x="820" y="99" class="body">컴파일한 것)</text>

  <text x="450" y="160" text-anchor="middle" class="note">React/TS 로 짠 화면 코드는 Vite 가 실행 가능한 형태로 묶어주고, 그 화면이 WASM 함수를 호출해서 MQSim 을 움직인다</text>
  <text x="450" y="185" text-anchor="middle" class="note">→ 즉 Vite·React·TS 는 "화면 쪽" 스택, WASM·em++( 왼쪽 도구 ) 는 "엔진 쪽" 스택 — 이 문서와 WASM 입문 문서가 각각 담당</text>
</svg>
</div>

<div style="margin-top: 60px;"></div>

## 6. 용어 정리

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th>용어</th><th>한 줄 설명</th></tr>
<tr><td>React</td><td>데이터가 바뀌면 화면에서 바뀐 부분만 알아서 다시 그려주는 JavaScript UI 라이브러리. 화면을 "컴포넌트" 단위로 쪼개서 만든다</td></tr>
<tr><td>TypeScript(TS)</td><td>타입 검사가 추가된 JavaScript. 오타·타입 실수를 코드 실행 전에(작성 중에) 잡아준다</td></tr>
<tr><td>Vite</td><td>React/TS 소스를 브라우저가 실행할 수 있는 JS/HTML/CSS 로 변환해주는 빌드 도구 + 개발 서버. em++ 의 "화면 버전"에 해당</td></tr>
<tr><td>Scaffold</td><td>프로젝트를 처음 시작할 때 필요한 폴더/설정 파일 뼈대를 도구가 자동으로 만들어주는 것( "비계"가 원래 뜻 )</td></tr>
<tr><td>컴포넌트(component)</td><td>화면을 이루는 독립된 조각 하나( 예 : flash grid, 매핑 테이블 뷰, 파라미터 패널 각각이 컴포넌트 하나 )</td></tr>
<tr><td>JSX / .tsx</td><td>React 컴포넌트를 HTML 처럼 보이는 문법으로 쓸 수 있게 해주는 JS 문법 확장. TS 와 결합된 확장자가 `.tsx`</td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/) — 이 문서가 다루는 "화면 쪽" 스택과 짝을 이루는 "엔진 쪽" 스택 설명
- [Claude 구현 작업 상세](/ftl-visual-simulator/plan/implementation/) — 이 스택이 실제로 어느 컴포넌트·파일에 적용되는지의 상세 스펙
- [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) — Session 3~4 의 "scaffold" 항목이 바로 이 문서에서 설명한 작업
- [ftl-visual-simulator 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator) — 실제 코드
</content>
