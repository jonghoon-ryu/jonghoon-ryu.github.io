---
layout: default
title: 초기화되지 않은 Bandwidth 필드 버그 — 반복 재구성 시 0 나누기 크래시
permalink: /ftl-visual-simulator/reference/bug-list/bandwidth-divide-by-zero-bug/
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
pre {
  background: #f5f5f5;
  padding: 12px 14px;
  border-radius: 6px;
  overflow-x: auto;
  font-size: 0.85rem;
}
</style>

# 초기화되지 않은 Bandwidth 필드 버그 — 반복 재구성 시 0 나누기 크래시

Session 10("workload 컨트롤" — 접근 패턴/read 비율/burst 크기를 실제 조작 가능하게 만드는 작업) 도중, 워크로드 설정을 몇 번 연달아 바꾸면 `divide by zero`로 WASM 엔진이 죽는 버그를 발견했다. [재구성 크래시 버그](/ftl-visual-simulator/reference/bug-list/reconfigure-crash-bug/)와 마찬가지로 **"인터랙티브하게 여러 번 재구성해야만" 드러나는 버그**지만, 원인은 메모리 소유권이 아니라 **초기화되지 않은 변수**다. 이 문서는 재현 과정, 정확한 원인, 그리고 수정 내용을 기록한다.

<div style="margin-top: 60px;"></div>

## 1. 증상

브라우저에서 "접근 패턴"(Random/Sequential) 드롭다운을 몇 번 연달아 바꾸면(재생 중이 아니어도 재현됨) 콘솔에 다음 에러가 뜨고 엔진이 멈췄다:

```
Error: divide by zero
    at worker.onmessage (useMqsimEngine.ts:46:24)
```

처음 1~3번 바꿀 때는 멀쩡하다가, 몇 번째부터 크래시하는지는 매번 달랐다 — 4번째에 죽을 때도, 5번째까지 멀쩡할 때도 있었다. 이런 "가끔, 몇 번째부터인지 일정하지 않게" 나는 크래시는 대개 초기화 안 된 메모리나 메모리 손상을 의심해야 한다.

<div style="margin-top: 60px;"></div>

## 2. 재현 — 네이티브 CLI로는 안 됐다

이 프로젝트의 원칙대로("네이티브 CLI로 먼저 검증") 재현을 시도했는데, 막혔다:

- 같은 워크로드를 네이티브 CLI로 여러 시나리오를 이어붙여 돌려도 크래시하지 않음
- `Load_workload → Initialize_scenario → Run_step → Finalize_scenario`를 그대로 흉내내는 작은 C++ 테스트 하니스를 만들어 재구성을 8번, 그 뒤엔 40번까지 반복해봐도 크래시하지 않음

즉 **네이티브 빌드에서는 재현이 안 되는, WASM 전용 버그**였다([MQSim 버그 헌트](/ftl-visual-simulator/reference/bug-list/mqsim-bug-hunt/)의 이식성 버그들과 같은 계열). 그래서 실제 WASM 모듈(`mqsim.mjs`/`mqsim.wasm`)을 브라우저 없이 Node.js에서 직접 로드해 똑같은 호출 순서(`init` → `configure` 반복)를 재생하는 스크립트로 바꿔봤더니, 재현됐다 — 브라우저가 필요한 게 아니라 WASM 런타임 자체가 필요했던 것.

<div style="margin-top: 60px;"></div>

## 3. 원인 확정 — UndefinedBehaviorSanitizer

`divide by zero`라는 메시지만으로는 소스 코드 어느 줄인지 전혀 알 수 없었다. 그래서 엔진을 `-fsanitize=integer-divide-by-zero`를 켜서 다시 빌드하고, 위 Node.js 재현 스크립트로 다시 돌렸더니 정확한 위치가 나왔다:

```
Host_System.cpp:57:92: runtime error: division by zero
```

문제의 줄:

```cpp
// Host_System.cpp - IO_Flow_Synthetic 생성자 호출부
flow_param->Synthetic_Generator_Type,
(flow_param->Bandwidth == 0
    ? 0
    : NanoSecondCoeff / ((flow_param->Bandwidth / SECTOR_SIZE_IN_BYTE) / flow_param->Average_Request_Size)),
```

`Bandwidth`가 0이면 삼항 연산자가 그냥 0을 넘기니 안전하다. 문제는 `Bandwidth`가 0이 **아닌**, 그러면서 `SECTOR_SIZE_IN_BYTE`(512)보다 작은 값일 때다 — 정수 나눗셈 `Bandwidth / 512`가 그냥 **0으로 내림**되고, 그 뒤 `NanoSecondCoeff / 0`에서 진짜로 0으로 나누게 된다.

<div style="margin-top: 60px;"></div>

## 4. 왜 Bandwidth 가 이상한 값이었나

`Bandwidth`는 `Synthetic_Generator_Type`이 `BANDWIDTH`(초당 고정 전송량 기반)일 때만 쓰는 값이다. 이 프로젝트는 항상 `QUEUE_DEPTH`(큐 깊이 기반) 생성기만 쓰기 때문에, 우리가 만드는 `workload.xml`에는 애초에 `<Bandwidth>` 태그 자체를 넣지 않는다 — 필요가 없으니까.

그런데 파서 쪽 코드는:

```cpp
// IO_Flow_Parameter_Set.cpp
} else if (strcmp(param->name(), "Bandwidth") == 0) {
    Bandwidth = std::stoi(val);
}
```

XML에 해당 태그가 **있을 때만** `Bandwidth`에 값을 대입한다. 그리고 클래스 정의 쪽은:

```cpp
// IO_Flow_Parameter_Set.h (수정 전)
unsigned int Bandwidth;  // 기본값 없음
```

기본값이 없다. 즉 XML에 태그가 없으면 `Bandwidth`는 **`new`로 갓 할당된 메모리에 우연히 남아있던 값** 그대로다. C++에서 `unsigned int` 같은 원시 타입 멤버는 `new`가 자동으로 0으로 밀어주지 않는다.

- 새 프로세스가 막 시작해서 처음 요청하는 메모리는 대개 운영체제가 0으로 밀어서 주기 때문에, 우연히 0이 나온다 → 안전.
- 그런데 이 앱은 워크로드/파라미터를 바꿀 때마다 `configure()`가 호출되어 기존 시뮬레이션 객체를 통째로 `delete`하고 새로 `new`한다. 몇 번 반복되면 메모리 할당기가 방금 해제된 블록을 재활용해서 내주기 시작하는데, 그 블록에는 **이전에 거기 있던 값의 잔여 바이트**가 남아있을 수 있다. 그 값이 하필 512보다 작은 값이면 크래시.

몇 번째에 크래시하는지 매번 달랐던 이유도 이걸로 설명된다 — 정확히 몇 번째 재구성에서 어떤 크기의 블록이 재활용되는지는 메모리 할당기 내부 상태에 달려 있어서, 결정론적으로 예측할 수 없었다.

<div style="margin-top: 60px;"></div>

## 5. 왜 지금까지 아무도 못 봤나

[재구성 크래시 버그](/ftl-visual-simulator/reference/bug-list/reconfigure-crash-bug/)와 똑같은 이유다 — **원본 MQSim 은 이 코드 경로를 절대 반복 실행하지 않는다.**

- upstream 예제 `workload.xml`들과 `MQSim_Interface.cpp`의 기본 워크로드 폴백 코드는 `Bandwidth`를 항상 명시적으로 채워 넣는다(예: `io_flow_1->Bandwidth = 262144;`) — 애초에 이 필드가 비어있는 상황 자체를 안 만든다.
- 이 프로젝트가 만드는 워크로드는 처음으로 "필요 없는 필드는 아예 안 쓴다"는 방식으로 XML을 생성했고, 동시에 "같은 프로세스에서 설정을 몇 번이고 다시 로드한다"는 것도 이 프로젝트가 처음 만든 사용 패턴이다. 두 조건이 겹쳐야만 드러나는 버그라, 배치 실행 한 번으로 끝나는 원본 CLI 사용 방식에서는 나올 수가 없었다.

<div style="overflow-x:auto;">
<table class="plan-calendar">
<tr><th></th><th>재구성 크래시 버그 (DRAM UAF)</th><th>이 문서의 버그</th></tr>
<tr><td>성격</td><td>메모리 안전성 버그(이중 소유권)</td><td>초기화되지 않은 변수</td></tr>
<tr><td>네이티브 CLI로 재현되는가</td><td>예 (ASan으로 확인)</td><td>아니오 — WASM 런타임에서만 재현됨</td></tr>
<tr><td>어떤 도구로 정체를 밝혔나</td><td>AddressSanitizer</td><td>UndefinedBehaviorSanitizer + Node.js 로 WASM 직접 재생</td></tr>
<tr><td>이 프로젝트가 처음 겪은 이유</td><td>일시정지/재구성 UI를 처음 만듦</td><td>+ 필요 없는 XML 필드를 생략하는 방식으로 워크로드를 처음 생성함</td></tr>
</table>
</div>

<div style="margin-top: 60px;"></div>

## 6. 수정

`Bandwidth`에 기본값을 줘서, XML에 태그가 있든 없든, 프로세스가 몇 번을 재구성하든 항상 well-defined 하게 만들었다:

```cpp
// IO_Flow_Parameter_Set.h (수정 후)
unsigned int Bandwidth = 0;
```

한 줄짜리 수정이지만, "이 필드는 QUEUE_DEPTH 생성기에서는 안 쓰인다"는 걸 몰랐다면 놓치기 쉬운 종류의 버그다.

(같은 조사 과정에서 `Utils::Logical_Address_Partitioning_Unit::Reset()`이 누적 통계용 정적 변수 두 개(`total_pda_no`, `total_lha_no`)를 리셋하지 않는 것도 발견했다 — 이번 크래시의 직접 원인은 아니었지만, 재구성할 때마다 값이 계속 누적되는 별개의 잠재 버그라 같이 고쳤다.)

<div style="margin-top: 60px;"></div>

## 7. 검증

- **회귀 테스트**: `npm run test:engine`의 golden 시나리오 3개 모두 수정 전/후 결과 완전 동일 — 커밋된 `workload.xml`들도 `<Bandwidth>` 태그가 없었지만, 항상 프로세스가 갓 시작한 상태(첫 할당은 0)에서 딱 한 번만 실행되기 때문에 원래도 우연히 0이었던 것으로 보인다. 즉 이 수정은 "우연히 맞았던 값"을 "항상 명시적으로 맞는 값"으로 바꾼 것뿐, 실제 계산 결과에는 영향이 없다.
- **크래시 재현 테스트**: 수정 전 WASM 빌드로는 접근 패턴을 4~8번 연달아 바꾸면 재현되던 크래시가, 수정 후 빌드로는 **40번 연속 재구성(중간에 실제 스텝 실행까지 섞어서)** 을 반복해도 한 번도 재현되지 않았다.
- 브라우저에서도 동일하게 접근 패턴을 8번 연속으로 바꿔가며 확인 — 크래시 없음.

<div style="margin-top: 60px;"></div>

## 8. 요약

- upstream MQSim 자체의 버그(초기화되지 않은 멤버 변수)이고, 커밋된 golden 시나리오에는 영향이 없다.
- **QUEUE_DEPTH 생성기만 쓰면서 + 같은 프로세스를 여러 번 재구성하는** 이 프로젝트의 사용 패턴이 겹쳐야만 드러난다 — 둘 중 하나만 있었다면 못 봤을 것이다.
- 네이티브 CLI로 재현이 안 되는 버그를 만나면, WASM 모듈을 브라우저 없이 Node.js로 직접 로드해서 똑같은 호출 순서를 재생해보는 게 훨씬 빠른 반복 주기로 디버깅할 수 있는 방법이었다 — 이번에 새로 익힌 디버깅 기법.

<div style="margin-top: 60px;"></div>

## 참고

- 관련 문서 : [재구성 크래시 버그](/ftl-visual-simulator/reference/bug-list/reconfigure-crash-bug/), [MQSim 버그 헌트](/ftl-visual-simulator/reference/bug-list/mqsim-bug-hunt/)
- [전체 개발 계획](/ftl-visual-simulator/plan/full-plan/) — Session 10
- [ftl-visual-simulator-app 저장소](https://github.com/jonghoon-ryu/ftl-visual-simulator-app) — 실제 코드
