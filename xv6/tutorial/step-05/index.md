---
layout: default
title: "step-05 : 키보드 입력 (폴링)"
permalink: /xv6/tutorial/step-05/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# `step-05` : 키보드 입력 (폴링)

| | |
|---|---|
| **앞 태그** | `step-04` |
| **이 태그** | `step-05` (커밋 `42a80d2`) |
| **한 줄** | PS/2 키보드 `kbd.cpp`, 콘솔 입력 `consoleintr()`, 시리얼 입력 `uartintr()` 를 옮겼다. 인터럽트가 아직 없으므로 `main()` 의 루프가 계속 물어본다 (폴링) |
| **비교할 C 코드** | `git show v0.2-x86_64-c:kernel/kbd.c`, `kbd.h`, `console.c` 의 `consoleintr` |

```sh
git diff --stat step-04 step-05 -- . ':!docs' ':!*.pdf'
git checkout step-05 && make clean && make vbox     # 창에서 쳐 보기
```

## 1. 이전 상태 (`step-04`)

출력은 화면과 시리얼 둘 다. 입력은 없었다 : `main()` 은 부팅 정보를 찍고 `hlt` 로 멈췄다.

C 판 계획에서 키보드는 인터럽트 (IDT, IOAPIC) 가 생긴 뒤에야 돌아온다. 그 전에 "치면 화면에 나오는" 것을 보려고, **같은 함수를 인터럽트 대신 루프에서 부르는** 단계를 넣었다.

## 2. 바꾼 것

| 파일 | | 더한 줄 | 지운 줄 |
|---|---|---:|---:|
| `Makefile` | 바뀜 | 1 | 0 |
| `kernel/console.cpp` | 바뀜 | 76 | 4 |
| `kernel/defs.h` | 바뀜 | 6 | 1 |
| `kernel/kbd.cpp` | 새 파일 | 133 | 0 |
| `kernel/kbd.h` | 새 파일 | 154 | 0 |
| `kernel/main.cpp` | 바뀜 | 19 | 6 |
| `kernel/uart.cpp` | 바뀜 | 29 | 6 |
| **합계** (7 파일) | | **418** | **17** |

<svg viewBox="0 0 1000 290" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="폴링 입력"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">입력 : 인터럽트가 아직 없으니 main() 의 루프가 부른다 (폴링)</text><rect x="20" y="60" width="170" height="60" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="105.0" y="86.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">PS/2 키보드</text><text x="105.0" y="102.0" font-size="11.0" fill="#4d5656" text-anchor="middle">포트 0x60, 0x64</text><rect x="20" y="140" width="170" height="60" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="105.0" y="166.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">COM1 시리얼</text><text x="105.0" y="182.0" font-size="11.0" fill="#4d5656" text-anchor="middle">포트 0x3F8</text><rect x="240" y="60" width="200" height="60" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="340.0" y="86.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">kbdintr()</text><text x="340.0" y="102.0" font-size="11.0" fill="#4d5656" text-anchor="middle">kbdgetc() : 스캔 코드 → 글자</text><rect x="240" y="140" width="200" height="60" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="340.0" y="166.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">uartintr()</text><text x="340.0" y="182.0" font-size="11.0" fill="#4d5656" text-anchor="middle">uartgetc()</text><rect x="500" y="95" width="210" height="70" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="605.0" y="118.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">consoleintr(c)</text><text x="605.0" y="134.0" font-size="11.0" fill="#4d5656" text-anchor="middle">에코, ^H, ^U</text><text x="605.0" y="150.0" font-size="11.0" fill="#4d5656" text-anchor="middle">cons.buf 에 모음</text><rect x="770" y="95" width="210" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="875.0" y="126.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">consputc()</text><text x="875.0" y="142.0" font-size="11.0" fill="#4d5656" text-anchor="middle">화면 + 시리얼</text><line x1="190" y1="90" x2="238" y2="90" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="190" y1="170" x2="238" y2="170" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="440" y1="90" x2="498" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="440" y1="170" x2="498" y2="140" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="710" y1="130" x2="768" y2="130" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="220" width="960" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="249.0" font-size="10.5" fill="#4d5656" text-anchor="middle">main() : for (;;) { kbdintr(); uartintr(); pause; }  → CPU 100%.  C 판에서는 인터럽트가 부르는 같은 함수들 (Step 18, 19 에서 인터럽트로)</text></svg>

### 2.1 `main()` : 폴링 루프

[`kernel/main.cpp:67–81`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-05/kernel/main.cpp#L67-L81) (태그 `step-05`)

```cpp
  kbdinit(); // PS/2 keyboard

  printk("\ntype on the keyboard (or the serial console): ");

  // [platform: QEMU, VirtualBox] keys come from the PS/2 keyboard
  // (the window) and from the serial port (make qemu's terminal).
  // [platform: real PC] only a PS/2 keyboard, or a USB keyboard
  // that the firmware still emulates as PS/2; see kbd.cpp.
  // unlike hlt, this loop keeps the CPU 100% busy; interrupts
  // (later steps) will let it sleep until a key arrives.
  for (;;) {
    kbdintr();
    uartintr();
    asm volatile("pause"); // a hint to the CPU that this is a spin loop
  }
```

`hlt` 는 CPU 를 재우지만, 이 루프는 CPU 를 100% 쓴다 (VirtualBox 프로세스가 CPU 한 개를 다 쓰는 것을 `top` 으로 볼 수 있다). 인터럽트가 돌아오면 (Step 18, 19) 다시 `hlt` 로 잔다.

### 2.2 `kbd.cpp`, `kbd.h` : 키 표를 컴파일 중에 만든다

`kbdgetc()` 의 내용은 C 판 그대로 (스캔 코드 → 글자, [v0.2 튜토리얼](/xv6/tutorial/v0.2-x86_64-c/) 2.2). 가장 큰 변화는 **키 표** 다 :

<svg viewBox="0 0 1000 260" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="키 표"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">키 표 : C99 의 지정 초기화 → constexpr 함수 (컴파일 중에 표를 만든다)</text><rect x="20" y="55" width="440" height="110" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="240.0" y="82.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">C 판 (kbd.h)</text><text x="240.0" y="98.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">static uchar shiftcode[256] = {</text><text x="240.0" y="114.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">  [0x1D] CTL, [0x2A] SHIFT, ...</text><text x="240.0" y="130.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">};</text><text x="240.0" y="146.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">// C++ 에는 배열의 지정 초기화가 없다</text><line x1="460" y1="110" x2="528" y2="110" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="530" y="55" width="450" height="110" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="755.0" y="90.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">C++ 판 (kbd.h)</text><text x="755.0" y="106.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">constexpr Keymap shiftcode = makemap({</text><text x="755.0" y="122.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">  {0x1D, CTL}, {0x2A, SHIFT}, ...</text><text x="755.0" y="138.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">});</text><rect x="20" y="190" width="960" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="219.0" font-size="10.5" fill="#4d5656" text-anchor="middle">makemap() 는 constexpr : g++ 가 컴파일 중에 실행해서 256 바이트 표를 만든다. 실행 파일에는 완성된 표만 들어간다 (C 판과 같은 데이터)</text></svg>

[`kernel/kbd.h:44–77`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-05/kernel/kbd.h#L44-L77) (태그 `step-05`)

```cpp
struct Keymap {
  uchar code[256];
  constexpr uchar operator[](uint i) const { return code[i]; }
};

struct KeyAt {
  uchar scancode;
  uchar value;
};

template <int M>
constexpr Keymap
makemap(const KeyAt (&at)[M])
{
  Keymap m{};
  for (int i = 0; i < M; i++)
    m.code[at[i].scancode] = at[i].value;
  return m;
}

// the same, plus a second list of pairs shared by several maps.
template <int N, int M, int K>
constexpr Keymap
makemap(const uchar (&first)[N], const KeyAt (&at)[M], const KeyAt (&more)[K])
{
  Keymap m = makemap(at);
  for (int i = 0; i < K; i++)
    m.code[more[i].scancode] = more[i].value;
  for (int i = 0; i < N; i++)
    m.code[i] = first[i];
  return m;
}

constexpr Keymap shiftcode = makemap({
```

- `makemap()` 의 인자 `const KeyAt (&at)[M]` : **배열의 참조** 라서 컴파일러가 길이 `M` 을 알아낸다. 중괄호 목록을 그대로 넘길 수 있다
- 세 표 (`normalmap`, `shiftmap`, `ctlmap`) 에 똑같이 들어가던 화살표 키 10개는 `e0keys` 하나로 묶었다
- `Keymap` 에 `operator[]` 가 있어서 `shiftcode[data]` 처럼 C 판과 같은 모양으로 읽는다

[platform: real PC] 키보드 컨트롤러가 없으면 포트가 `0xFF` 로 읽혀 끝없이 "글자 있음" 으로 보인다. `kbdgetc()` 가 `0xFF` 를 먼저 거른다 (C 판에 없는 검사. 나중에 실제 PC 에서 `0x55` 도 있다는 것을 알게 된다 → [step-06](/xv6/tutorial/step-06/)).

### 2.3 `console.cpp` 의 `consoleintr()`, `uart.cpp` 의 `uartintr()`

`consoleintr()` 는 에코, 백스페이스 (`^H`, Delete), 줄 지우기 (`^U`) 를 하고 글자를 `cons.buf` 에 모은다. C 판과 한 곳이 다르다 :

[`kernel/console.cpp:103–108`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-05/kernel/console.cpp#L103-L108) (태그 `step-05`)

```cpp
      if (c == '\n' || c == C('D') || cons.e - cons.r == INPUT_BUF_SIZE) {
        // a whole line (or end-of-file) has arrived. the C version
        // wakes up consoleread() here. with no reader yet, consume
        // the line at once, so the buffer never fills up.
        cons.w = cons.e;
        cons.r = cons.w;
```

C 판은 한 줄이 끝나면 `consoleread()` (셸의 `read()`) 를 깨운다. 아직 읽는 쪽이 없어서 줄을 바로 버린다. 안 버리면 128자 뒤에 버퍼가 차서 입력이 멈춘다.

`uartintr()` : C 판에서는 시리얼 인터럽트가 부르는 함수. 지금은 루프가 부른다 :

[`kernel/uart.cpp:113–127`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-05/kernel/uart.cpp#L113-L127) (태그 `step-05`)

```cpp
uartintr()
{
  ReadReg(ISR); // acknowledge the interrupt

  // the C version wakes up a thread in uartwrite() here when the
  // UART is ready for more output. no uartwrite() yet.

  // read and process incoming characters, if any.
  while (1) {
    int c = uartgetc();
    if (c == -1)
      break;
    consoleintr(c);
  }
}
```

## 3. 바뀐 뒤

QEMU (QMP `send-key` 로 `Hi there!` 와 Ctrl+U 를 보낸 화면) :

![step-05 QEMU 화면](/assets/image/xv6-tut-step-05-step05-qemu.png)

VirtualBox :

![step-05 VirtualBox 화면](/assets/image/xv6-tut-step-05-step05-vbox.png)

- QEMU, VirtualBox : 키보드와 시리얼 둘 다 입력된다
- 실제 PC : **PS/2 키보드가 있거나 펌웨어가 USB 키보드를 PS/2 로 흉내 낼 때만.** 2026.10.7 베어본에서는 안 됐다 → [step-06](/xv6/tutorial/step-06/) 부터 USB 드라이버

<div class="check" markdown="1">
**코드와 대조해 볼 것**

- `kbd.h` 의 `normalmap` 에서 `0x1E` 번째가 `'a'` 인지 (`makemap` 의 첫 목록은 스캔 코드 0 부터 차례로)
- `objdump -s -j .rodata kernel/kernel | less` 에서 완성된 256 바이트 표 찾기 : `makemap()` 을 부르는 코드는 실행 파일에 없다
- `cons.r = cons.w;` 를 지우고 130 글자 넘게 쳐 보기 : 입력이 멈춘다
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-04/">step-04</a></span><span><a href="/xv6/tutorial/step-06/">step-06</a> →</span></div>
