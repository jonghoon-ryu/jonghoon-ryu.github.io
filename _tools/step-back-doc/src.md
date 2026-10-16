---
layout: default
title: 한 줄 되돌리기(⏪)는 어떻게 동작하나
permalink: /ftl-visual-simulator/reference/step-back/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
table { font-size:0.88rem; }
</style>

# 한 줄 되돌리기(⏪)는 어떻게 동작하나

시뮬레이터 툴바의 **⏪ 1 step** 버튼(또는 ← 키)은 "1 step" / "5 steps" 로 진행한 것을 한 step(로그 한 줄)씩 되돌린다. 되돌리면 격자 색과 테두리, 로그, 통계, 차트가 모두 그 줄 직전 모습으로 돌아가고, 거기서 다시 진행하면 **똑같은 일이 똑같은 순서로** 또 일어난다.

MQSim 에는 되돌리기 기능이 없다. 이 문서는 MQSim 코드를 한 줄도 고치지 않고 이것을 어떻게 만들었는지, 그리고 왜 그 방법이 정확한지를 설명한다. 코드는 앱 저장소의 커밋 `ffe997f` 에 있다.

<div style="margin-top: 60px;"></div>

## 1. 왜 쉽지 않은가

시뮬레이터는 **앞으로만 간다.** MQSim 이 한 줄을 진행하면 이벤트 큐에서 이벤트를 꺼내 처리하고, 매핑 테이블을 고치고, page 를 invalid 로 바꾸고, 칩 상태를 바꾼다. 모두 **제자리에서 덮어쓰는** 변경이라 "방금 뭘 바꿨는지" 는 어디에도 남지 않는다. 그래서 한 단계를 거꾸로 실행하는 방법은 없다 — 되돌리려면 **그 시점의 상태를 미리 저장해 두었다가 다시 꺼내는 수밖에** 없다.

게다가 저장해야 할 상태가 두 군데에 있다.

@@SVG two_places@@

- **엔진** — Web Worker 안에서 도는 WASM MQSim. SSD 의 진짜 상태다.
- **화면** — React 쪽. 로그, 방금 바뀐 칸의 테두리, 차트 기록, 통계 카운터는 getState() 로 읽어 오는 것이 아니라 **엔진이 보내 준 이벤트를 하나씩 쌓아서** 만든 것이다. 그래서 엔진만 되돌리면 격자는 과거인데 로그와 차트는 미래인, 앞뒤가 안 맞는 화면이 된다.

<div style="margin-top: 60px;"></div>

## 2. 두 가지 방법

@@SVG two_options@@

**A. 처음부터 다시 실행.** MQSim 은 결정적이다 — 같은 설정, 같은 워크로드면 몇 번을 돌려도 같은 이벤트가 같은 순서로 나온다(골든 테스트가 이걸 확인하고, [버그 #29](/ftl-visual-simulator/reference/code-change/bug-list/table/) 수정도 결정성을 지키기 위한 것이었다). 그러니 줄 16 에서 ⏪ 를 누르면 init() 하고 줄 15 까지 조용히 다시 돌리면 된다. 문제는 두 가지다. 뒤로 갈수록 다시 돌릴 양이 늘어나고, 화면 쪽 hook 들이 그 동안 쏟아지는 이벤트로 상태를 전부 다시 쌓아야 한다.

**B. 스냅샷.** 각 줄을 진행하기 **직전에** 엔진과 화면의 사본을 하나씩 만들어 두고, ⏪ 는 가장 최근 사본을 되돌려 쓴다. 언제 누르든 비용이 같고, 화면도 사본을 그대로 돌려놓기만 하면 된다. 이 시뮬레이터는 B 를 골랐다. 남은 질문은 "MQSim 같은 거대한 C++ 객체 덩어리를 어떻게 통째로 복사하느냐" 인데, 답은 WASM 의 구조에 있다.

<div style="margin-top: 60px;"></div>

## 3. 엔진 사본 — WASM 메모리를 통째로 복사

C++ 를 WASM 으로 컴파일하면 프로그램이 쓰는 메모리 전체가 **하나의 큰 바이트 배열**(선형 메모리)이 된다. 전역 변수도, `new` 로 만든 객체도, 스택도 모두 이 배열 안의 어딘가에 있다. JavaScript 에서는 이 배열을 `HEAPU8` 이라는 `Uint8Array` 로 볼 수 있다. ([WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/) 참고)

그러니 **이 배열을 복사해 두었다가 나중에 그대로 다시 써 넣으면, MQSim 은 그 순간으로 돌아간다.** MQSim 의 클래스 하나하나를 직렬화하는 코드를 짤 필요가 없다. 포인터도 문제 없다 — 포인터는 이 배열 안의 위치(숫자)일 뿐이고, 배열을 통째로 되돌리면 가리키는 곳도 같이 돌아간다.

다만 배열 전체는 128 MB 라서 매 줄 복사하기엔 크다. 실제로 쓰이는 부분만 고르면 된다.

@@SVG memory@@

시뮬레이터에서 실제로 잰 배치다 (GC 시연, 3000 줄 진행 후).

| 구간 | 크기 | 복사? | 이유 |
|---|---|---|---|
| 정적 데이터 `[0, stackLow)` | 약 77 KB | ✔ | 전역/static 변수 — `Stats` 카운터, 이벤트 콜백 포인터, 그리고 힙이 어디까지 찼는지 기억하는 sbrk 포인터 |
| C++ 스택 `[stackLow, stackHigh)` | 16 MB | ✘ | 함수가 실행 중이 아니면 쓸모없는 내용뿐 (4절) |
| 힙 `[stackHigh, heapEnd)` | 약 2.2 ~ 2.4 MB | ✔ | `new`/`malloc` 으로 만든 MQSim 객체 전부, malloc 자신의 장부 |
| 그 위 `[heapEnd, 128 MB)` | 나머지 | ✘ | 아직 아무도 쓰지 않은 공간 |

경계 주소는 C++ 쪽에 작은 함수를 하나 추가해서 알아낸다. Emscripten 이 제공하는 스택 경계 함수와, 힙의 끝을 돌려주는 `sbrk(0)` 를 그대로 넘겨줄 뿐이다.

```cpp
// engine/mqsim/src/wasm/bindings.cpp
val memory_layout()
{
	val layout = val::object();
	layout.set("stackLow", (double)emscripten_stack_get_end());
	layout.set("stackHigh", (double)emscripten_stack_get_base());
	layout.set("heapEnd", (double)(uintptr_t)sbrk(0));
	return layout;
}
```

워커는 이 범위만 잘라서 복사하고, 되돌릴 때는 같은 자리에 다시 써 넣는다.

```ts
// src/workers/mqsim.worker.ts
function takeSnapshot(mod: MqsimModule): MemorySnapshot {
  const { stackLow, stackHigh, heapEnd } = mod.memoryLayout();
  return { low: mod.HEAPU8.slice(0, stackLow), highStart: stackHigh, high: mod.HEAPU8.slice(stackHigh, heapEnd) };
}

function restoreSnapshot(mod: MqsimModule, snap: MemorySnapshot) {
  // Memory only ever grows, so the current buffer is always big enough.
  mod.HEAPU8.set(snap.low, 0);
  mod.HEAPU8.set(snap.high, snap.highStart);
}
```

사본 하나는 매핑 기본 · GC 시연에서 약 2.3 ~ 2.6 MB, 마모평준화 시연에서 약 4.6 ~ 4.9 MB 이고, 복사는 1 ms 안팎이다. 최대 30 개까지 보관하므로 GC 시연에서도 100 MB 를 넘지 않는다.

<div class="check" markdown="1">
**빌드 설정 한 줄.** `HEAPU8` 은 기본적으로 모듈 밖에 공개되지 않아서, `engine/build-wasm.sh` 에 `-sEXPORTED_RUNTIME_METHODS=HEAPU8` 을 추가했다. 메모리가 자라면(`ALLOW_MEMORY_GROWTH`) Emscripten 이 새 버퍼로 `HEAPU8` 을 다시 만들어 주므로, 워커는 매번 `mod.HEAPU8` 을 새로 읽는다.
</div>

<div style="margin-top: 60px;"></div>

## 4. 왜 이걸로 충분한가

"배열 안에 있는 것" 만 되돌리는데, 배열 **밖에** 있는 상태는 없을까? 하나씩 따져 보면 이렇다.

**C++ 스택.** 스냅샷은 워커가 WASM 함수를 부르지 않고 있는 순간에만 찍는다. 함수가 return 하면 스택 포인터는 맨 위로 돌아가 있고, 스택에 남은 바이트는 다음 호출이 덮어쓸 쓰레기일 뿐이다. 그래서 16 MB 를 건너뛰어도 된다.

@@SVG stack_idle@@

**WASM 전역값.** 스택 포인터는 메모리 밖(WASM global)에 있지만, 호출이 없을 때는 항상 같은 값(맨 위)이다.

**JavaScript 쪽 객체.** 엔진이 이벤트를 넘겨주는 JS 콜백은 모듈이 로드될 때 **한 번만** 등록되고 바뀌지 않는다. C++ 가 들고 있는 것은 그 콜백을 가리키는 번호뿐이고, 그 번호는 어느 사본에서나 같다.

**파일.** 설정 XML 은 `init()` 때 한 번 읽고 끝이다. 진행 중에는 파일을 건드리지 않는다.

**메모리 크기.** WASM 메모리는 줄어들지 않는다. 옛 사본의 힙이 지금보다 작아도 그 범위를 덮어쓰면 그만이고, 그 위에 남은 바이트는 — sbrk 포인터까지 옛 값으로 돌아갔으므로 — 아무도 쓰지 않는 빈 공간이 된다.

이 추론이 맞는지는 실험으로 확인했다 (7절).

<div style="margin-top: 60px;"></div>

## 5. 화면 사본

화면 쪽은 hook 마다 `snapshot()` 과 `restore()` 를 하나씩 추가했다. 엔진 사본과 같은 순간에 모두 불러서 하나로 묶어 둔다.

| hook | 사본에 담는 것 | 복사 방식 |
|---|---|---|
| `useMqsimEvents` | 로그 50줄, 통계 카운터, 굵게 표시할 줄 번호, 다음 줄 번호, LPN → 이전 주소 지도 | 지도만 복사 (이벤트마다 고쳐지므로) |
| `useMqsimMigrations` · `useMqsimOverwrites` | 방금 옮긴/쓴/읽은/지운 칸 (격자 테두리), LPN → page 지도 | 칸 집합은 매번 새로 만들어지므로 참조만, 지도는 복사 |
| `useFreeBlockHistory` | 빈 block 수 차트 기록, 마지막 GC 정보, GC 횟수 | 참조만 |
| `useReadLatencyHistory` | 읽기 지연 차트 기록, 직전 누적값 | 참조만 |
| `useLpnJourney` | LPN 별 이동 기록, block 별 erase 순번 | 깊은 복사 (기록 배열에 제자리 push 하므로) |
| `useMqsimWlHighlight` | WL 발동 횟수, 마지막 발동 정보, 배너 표시 여부 | 참조만 |
| `App` | TRIM 커서 위치 | 숫자 |

"참조만" 으로 충분한 경우가 많은 이유: 이 hook 들은 상태를 바꿀 때 기존 배열/집합을 고치지 않고 **새 것을 만들어 바꿔 끼운다**(React 의 일반적인 방식). 옛 배열은 아무도 고치지 않으므로 그대로 들고 있으면 그게 곧 사본이다. 반대로 이벤트가 올 때마다 제자리에서 고치는 `Map` 이나 배열은 반드시 복사해야 한다 — 그렇지 않으면 사본이 미래의 내용으로 바뀌어 버린다.

어느 LPN 을 따라가고 있는지(LPN 여정 패널)는 시뮬레이션 상태가 아니라 보는 사람의 선택이라 되돌리지 않는다. 대신 되돌린 기록으로 여정을 다시 그린다.

<div class="check" markdown="1">
**"5 steps" 에서 생긴 함정 — `useMirroredState`.** React 의 `useState` 값은 다음 렌더링 때 바뀐다. 그런데 "5 steps" 은 다섯 줄을 연달아 진행하면서 매 줄 직전에 사본을 찍으므로, 두 번째 줄의 사본을 찍는 순간에는 첫 줄의 결과가 아직 렌더링되지 않았을 수 있다. 그러면 사본이 한 줄 늦은 화면을 담게 된다. 그래서 상태를 바꾸는 순간 **동기적으로** 최신 값을 ref 에도 적어 두는 작은 hook `useMirroredState` 를 만들어, 사본은 항상 그 ref 에서 읽게 했다.
</div>

<div style="margin-top: 60px;"></div>

## 6. 전체 흐름

@@SVG flow@@

- 엔진 사본은 **워커 안에** 보관한다. 몇 MB 짜리를 메인 스레드로 보냈다가 다시 받을 이유가 없다. 메인 스레드는 "push", "pop" 같은 짧은 메시지만 보낸다.
- 두 스택은 같이 push 하고 같이 pop 한다. 30 개를 넘으면 둘 다 가장 오래된 것부터 버린다.
- **순서 보장.** 진행과 되돌리기는 모두 하나의 줄(promise 체인)에 세워서 차례로 실행한다. 한 줄 진행이 아직 끝나지 않았는데 ⏪ 를 눌러도, 진행이 끝난 뒤에 되돌린다. 그래서 버튼을 아무리 빨리 눌러도 한 번 누를 때마다 정확히 한 줄씩 움직인다.
- **기록을 지우는 때.** ▶ 재생은 한 틱에 여러 줄을 사본 없이 진행하므로, ▶ 를 누르는 순간 기록을 지운다. ⏮ 와 설정 변경은 엔진을 새로 만들므로 역시 지운다. TRIM 은 기록을 지우지 않는다 — TRIM 뒤에 진행한 줄을 넘어 되돌리면 TRIM 도 함께 되돌아간다.
- 마모평준화 시연에는 한 줄씩 진행하는 버튼이 없어서 ⏪ 도 없다.

<div style="margin-top: 60px;"></div>

## 7. 어떻게 검증했나

@@SVG verify@@

**엔진 단독 (`engine/tests/cache/stepback.mts`).** Node 에서 WASM 모듈을 직접 불러, 세 프리셋 각각 다섯 지점(0, 50, 300, 1500, 4000 줄)에서 위 그림대로 실험했다. 기록 A 와 B 에는 그 다섯 줄 동안 나온 **모든 이벤트**와 마지막 `getState()` 전체(매핑 테이블, 모든 block 의 page 상태, 통계)를 문자열로 담는다. 15 번 모두 글자 하나 다르지 않았다. 되돌림이 무언가를 빠뜨렸다면 B 는 다른 상태에서 출발하므로 결과가 달라졌을 것이다.

**화면까지 (e2e 테스트).** 실제 브라우저로 GC 시연을 줄 200 근처까지 ▶ 로 돌린 뒤, "5 steps" 을 여섯 번 눌러 첫 GC 를 지나가게 하고, 매 번 화면 지문(격자의 모든 칸 상태와 테두리, 로그 내용, 통계)을 기록한다. 그다음 ⏪ 를 30 번 눌러(마지막 다섯 번은 ← 키) 다섯 줄마다 화면 지문이 그때 기록한 것과 같은지 확인하고, 다시 앞으로 30 줄 가서 처음 도착했던 화면과 같은지 확인한다. 로그의 시각(HH:MM:SS)만은 실제 시계라 비교에서 뺐다.

<div style="margin-top: 60px;"></div>

## 8. 한계

- 되돌릴 수 있는 것은 **한 줄씩 진행한 것뿐**이다. ▶ 로 진행한 구간은 되돌릴 수 없다 — 틱마다 사본을 찍을 수도 있지만, 그러면 ⏪ 한 번이 "한 줄" 이 아니라 "한 틱(수십 줄)" 이 되어 의미가 달라진다.
- 최대 30 줄. 메모리를 더 쓰면 늘릴 수 있지만(사본 하나 약 2.5 MB), 지금 용도에는 충분하다고 봤다.
- 이 방법은 엔진이 **WASM 메모리 밖에 상태를 두지 않는다**는 가정에 기대고 있다. 나중에 엔진이 JS 쪽에 상태를 따로 두게 되면(예: 진행 중에 파일을 쓰거나, 호출할 때마다 바뀌는 JS 객체를 C++ 가 붙잡게 되면) 그 부분은 따로 사본을 떠야 한다. `stepback.mts` 가 그런 변화를 잡아 줄 것이다.

<div style="margin-top: 60px;"></div>

## 관련 문서

- [WASM · em++ 입문](/ftl-visual-simulator/reference/wasm-primer/) — 선형 메모리, Emscripten
- [프론트엔드 스택 입문](/ftl-visual-simulator/reference/frontend-stack/) — React 의 상태와 렌더링
- [이벤트 엔진과 시간](/ftl-visual-simulator/reference/mqsim-code-analysis/big-picture/event-engine/) — "한 줄" 이 엔진에서는 무엇인지
