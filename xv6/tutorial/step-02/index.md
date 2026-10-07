---
layout: default
title: "step-02 : 시리얼 드라이버와 문자열 함수"
permalink: /xv6/tutorial/step-02/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# `step-02` : 시리얼 드라이버와 문자열 함수

| | |
|---|---|
| **앞 태그** | `step-01` |
| **이 태그** | `step-02` (커밋 `f150975`) |
| **한 줄** | C 판의 `uart.c` (출력과 폴링 입력 부분) 와 `string.c` 를 C++ 로 옮겼다. `main.cpp` 의 임시 시리얼 코드가 빠졌다 |
| **비교할 C 코드** | `git show v0.2-x86_64-c:kernel/uart.c`, `git show v0.2-x86_64-c:kernel/string.c` |

```sh
git diff --stat step-01 step-02 -- . ':!docs' ':!*.pdf'
git diff step-01 step-02 -- kernel/main.cpp     # 임시 코드가 어떻게 빠졌나
```

## 1. 이전 상태 (`step-01`)

`main.cpp` 안에 시리얼 포트를 직접 다루는 임시 함수 `earlyuartinit()`, `earlyputs()` 가 있었다 ([step-01](/xv6/tutorial/step-01/) 2.3). 커널에는 `memset` 같은 기본 함수도 없었다.

## 2. 바꾼 것

| 파일 | | 더한 줄 | 지운 줄 |
|---|---|---:|---:|
| `Makefile` | 바뀜 | 3 | 1 |
| `kernel/defs.h` | 새 파일 | 21 | 0 |
| `kernel/main.cpp` | 바뀜 | 11 | 41 |
| `kernel/string.cpp` | 새 파일 | 101 | 0 |
| `kernel/uart.cpp` | 새 파일 | 104 | 0 |
| **합계** (5 파일) | | **240** | **42** |

### 2.1 `uart.cpp` : 16550 UART 드라이버

PC 의 시리얼 포트 칩 (16550) 은 **I/O 포트** `0x3F8` 부터 8개의 레지스터를 가진다. RISC-V 판은 메모리 주소에 있던 같은 칩을 다뤘고, x86 판은 `inb`/`outb` 로 다룬다.

<svg viewBox="0 0 1000 380" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="UART 레지스터"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">16550 UART : I/O 포트 0x3F8 (COM1) 부터 8개의 레지스터</text><rect x="20" y="60" width="70" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="55.0" y="84.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">+0</text><rect x="90" y="60" width="120" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="150.0" y="84.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">THR / RHR</text><text x="222.0" y="85.0" font-size="11.5" fill="#4d5656" text-anchor="start">보낼 바이트 / 받은 바이트</text><rect x="20" y="106" width="70" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="55.0" y="130.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">+1</text><rect x="90" y="106" width="120" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="150.0" y="130.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">IER</text><text x="222.0" y="131.0" font-size="11.5" fill="#4d5656" text-anchor="start">인터럽트 켜기 (지금은 0)</text><rect x="20" y="152" width="70" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="55.0" y="176.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">+2</text><rect x="90" y="152" width="120" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="150.0" y="176.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">FCR</text><text x="222.0" y="177.0" font-size="11.5" fill="#4d5656" text-anchor="start">FIFO 켜기, 비우기</text><rect x="20" y="198" width="70" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="55.0" y="222.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">+3</text><rect x="90" y="198" width="120" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="150.0" y="222.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">LCR</text><text x="222.0" y="223.0" font-size="11.5" fill="#4d5656" text-anchor="start">8비트, 속도 설정 모드</text><rect x="20" y="244" width="70" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="55.0" y="268.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">+5</text><rect x="90" y="244" width="120" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="150.0" y="268.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">LSR</text><text x="222.0" y="269.0" font-size="11.5" fill="#4d5656" text-anchor="start">상태 : 비트 0 받음, 비트 5 보낼 수 있음</text><rect x="560" y="60" width="420" height="120" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="770.0" y="100.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">uartputc_sync(c)</text><text x="770.0" y="116.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">while ((ReadReg(LSR) &amp; LSR_TX_IDLE) == 0)</text><text x="770.0" y="132.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">  ;   // 보낼 수 있을 때까지 기다림</text><text x="770.0" y="148.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">WriteReg(THR, c);</text><rect x="560" y="200" width="420" height="150" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="770.0" y="247.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">[platform: real PC] COM1 이 없으면</text><text x="770.0" y="263.0" font-size="11.0" fill="#4d5656" text-anchor="middle">없는 포트를 읽으면 0xFF</text><text x="770.0" y="279.0" font-size="11.0" fill="#4d5656" text-anchor="middle">LSR = 0xFF → TX_IDLE 도 켜져 있음 → 기다리지 않고</text><text x="770.0" y="295.0" font-size="11.0" fill="#4d5656" text-anchor="middle">아무도 없는 곳에 써 버린다 : 멈추지 않는다</text><text x="770.0" y="311.0" font-size="11.0" fill="#4d5656" text-anchor="middle">RX_READY 도 켜져 보임 → uartgetc() 가 0xFF 를 먼저 거른다</text><text x="20.0" y="320.0" font-size="11.5" fill="#4d5656" text-anchor="start">RISC-V 판 : UART 가 메모리 주소 0x10000000 에 (메모리 매핑 I/O, 포인터로 읽고 씀)</text><text x="20.0" y="342.0" font-size="11.5" fill="#4d5656" text-anchor="start">x86 PC : I/O 포트라는 따로 있는 주소 공간 (inb / outb 명령)</text></svg>

C 판의 매크로가 C++ 의 타입 있는 상수와 inline 함수가 되었다 :

[`kernel/uart.cpp:25–47`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-02/kernel/uart.cpp#L25-L47) (태그 `step-02`)

```cpp
// C: #define constants; C++: typed constants the compiler checks.
constexpr ushort RHR = 0;                  // receive holding register (for input bytes)
constexpr ushort THR = 0;                  // transmit holding register (for output bytes)
constexpr ushort IER = 1;                  // interrupt enable register
constexpr ushort FCR = 2;                  // FIFO control register
constexpr uchar FCR_FIFO_ENABLE = 1 << 0;
constexpr uchar FCR_FIFO_CLEAR = 3 << 1;   // clear the content of the two FIFOs
constexpr ushort LCR = 3;                  // line control register
constexpr uchar LCR_EIGHT_BITS = 3 << 0;
constexpr uchar LCR_BAUD_LATCH = 1 << 7;   // special mode to set baud rate
constexpr ushort LSR = 5;                  // line status register
constexpr uchar LSR_RX_READY = 1 << 0;     // input is waiting to be read from RHR
constexpr uchar LSR_TX_IDLE = 1 << 5;      // THR can accept another character to send

// C: #define ReadReg(reg) (inb(COM1 + (reg))); C++: inline functions.
static inline uchar
ReadReg(ushort reg)
{
  return inb(COM1 + reg);
}

static inline void
WriteReg(ushort reg, uchar v)
```

`uartinit()` 은 C 판과 같은 순서로 레지스터를 설정한다. 다른 점 하나 : C 판은 끝에 송수신 인터럽트를 켜는데, 아직 인터럽트를 처리할 코드가 없으므로 켜지 않는다 :

[`kernel/uart.cpp:53–76`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-02/kernel/uart.cpp#L53-L76) (태그 `step-02`)

```cpp
uartinit()
{
  // disable interrupts.
  WriteReg(IER, 0x00);

  // special mode to set baud rate.
  WriteReg(LCR, LCR_BAUD_LATCH);

  // LSB for baud rate of 38.4K.
  WriteReg(0, 0x03);

  // MSB for baud rate of 38.4K.
  WriteReg(1, 0x00);

  // leave set-baud mode,
  // and set word length to 8 bits, no parity.
  WriteReg(LCR, LCR_EIGHT_BITS);

  // reset and enable FIFOs.
  WriteReg(FCR, FCR_FIFO_ENABLE | FCR_FIFO_CLEAR);

  // the C version enables transmit and receive interrupts here.
  // nothing handles interrupts yet, so they stay off.
}
```

이 단계에서 가져온 것은 **폴링 부분만** : `uartinit()`, `uartputc_sync()`, `uartgetc()`. 버퍼를 쓰는 `uartputc()`/`uartwrite()` 와 `uartintr()` 는 `sleep()` 과 인터럽트가 필요해서 나중에 돌아온다.

`uartgetc()` 의 `0xFF` 검사는 **C 판에 없다** (실제 PC 를 위한 것, 위 그림 오른쪽) :

[`kernel/uart.cpp:95–104`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-02/kernel/uart.cpp#L95-L104) (태그 `step-02`)

```cpp
uartgetc()
{
  uchar lsr = ReadReg(LSR);
  // [platform: real PC] no UART: every register reads 0xFF.
  if (lsr == 0xFF)
    return -1;
  if (lsr & LSR_RX_READY)
    return ReadReg(RHR);
  return -1;
}
```

### 2.2 `string.cpp` : 메모리·문자열 함수

`memset`, `memcmp`, `memmove`, `memcpy`, `strncmp`, `strncpy`, `safestrcpy`, `strlen`. 내용은 C 판 그대로. 다른 점은 이름의 **연결 (linkage)** 이다 :

[`kernel/defs.h:6–16`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-02/kernel/defs.h#L6-L16) (태그 `step-02`)

```cpp
// string.cpp
extern "C" {
void *memset(void *, int, uint64);
int memcmp(const void *, const void *, uint64);
void *memmove(void *, const void *, uint64);
void *memcpy(void *, const void *, uint64);
}
char *safestrcpy(char *, const char *, int);
int strlen(const char *);
int strncmp(const char *, const char *, uint);
char *strncpy(char *, const char *, int);
```

[`kernel/string.cpp:4–8`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-02/kernel/string.cpp#L4-L8) (태그 `step-02`)

```cpp
// memset, memcmp, memmove and memcpy have C linkage (extern "C" in
// defs.h): g++ itself may emit calls to them, for example to zero
// or copy a large struct, and looks for those plain names.
// their size arguments are uint64 (size_t), not uint as in the C
// version, to match what those compiler-made calls pass.
```

C++ 는 함수 이름에 인자 타입을 섞어 넣는다 (`strlen` → `_Z6strlenPKc`). 그런데 g++ 는 큰 구조체를 복사하거나 0 으로 채울 때 **스스로 `memcpy`, `memset` 을 부르는 코드** 를 만들고, 그때는 C 이름을 찾는다.
그래서 그 네 개만 `extern "C"` 로 C 이름을 쓴다. 나머지는 C++ 이름 그대로.

<svg viewBox="0 0 1000 300" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="C 와 C++ 비교"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">C → C++ : 같은 기계어, 더 많은 검사</text><text x="250.0" y="52.0" font-size="12.5" font-weight="700" fill="#4d5656" text-anchor="middle">C 판</text><text x="620.0" y="52.0" font-size="12.5" font-weight="700" fill="#4d5656" text-anchor="middle">C++ 판</text><rect x="20" y="64" width="400" height="46" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="220.0" y="91.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">#define LSR 5</text><line x1="420" y1="87" x2="448" y2="87" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="450" y="64" width="340" height="46" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="620.0" y="91.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">constexpr ushort LSR = 5;</text><text x="800.0" y="91.0" font-size="10.5" fill="#4d5656" text-anchor="start">타입이 있다. 디버거에 이름이 보인다</text><rect x="20" y="120" width="400" height="46" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="220.0" y="147.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">#define ReadReg(reg) (inb(COM1 + (reg)))</text><line x1="420" y1="143" x2="448" y2="143" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="450" y="120" width="340" height="46" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="620.0" y="147.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">static inline uchar ReadReg(ushort reg)</text><text x="800.0" y="147.0" font-size="10.5" fill="#4d5656" text-anchor="start">인자 타입 검사. 괄호 실수가 없다</text><rect x="20" y="176" width="400" height="46" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="220.0" y="203.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">(char *)dst</text><line x1="420" y1="199" x2="448" y2="199" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="450" y="176" width="340" height="46" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="620.0" y="203.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">static_cast&lt;char *&gt;(dst)</text><text x="800.0" y="203.0" font-size="10.5" fill="#4d5656" text-anchor="start">어떤 종류의 변환인지 드러난다</text><rect x="20" y="232" width="400" height="46" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="220.0" y="259.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">void *memset(void *, int, uint)</text><line x1="420" y1="255" x2="448" y2="255" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="450" y="232" width="340" height="46" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="620.0" y="259.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">extern &quot;C&quot; void *memset(..., uint64)</text><text x="800.0" y="259.0" font-size="10.5" fill="#4d5656" text-anchor="start">g++ 가 직접 부른다 : C 이름으로</text></svg>

### 2.3 `main.cpp`

`earlyuartinit()` → `uartinit()`, `earlyputs()` → `uart.cpp` 의 `uartputc_sync()` 를 쓰는 작은 `uartputs()`. 화면 칠하기와 "xv6" 글자는 그대로.

## 3. 바뀐 뒤

출력은 `step-01` 과 거의 같다 (단계 번호만) :

```
xv6 kernel is booting (C++, step 2)
nothing else yet; halting
```

보이는 것은 같지만, 이제 시리얼 출력이 C 판과 같은 함수 (`uartputc_sync`) 로 나간다. 다음 단계의 `printk()` 가 이 위에 선다.

<div class="check" markdown="1">
**코드와 대조해 볼 것**

- `nm kernel/kernel | grep -E " T (mem|_Z.*str)"` : `memset` 등은 맨 이름, `strlen` 등은 `_Z…` 이름
- `git diff v0.2-x86_64-c:kernel/uart.c step-02:kernel/uart.cpp` : 빠진 함수들 (`uartputc`, `uartwrite`, `uartintr`) 과 더해진 `0xFF` 검사
- `string.cpp` 와 `defs.h` 에서 `memcpy` 를 지우고, `main()` 에 큰 구조체 대입 (`struct Big { char x[256]; } a{}, b; b = a;`) 을 넣어 빌드 : 링크 오류 ``undefined reference to `memcpy'``. 코드에 `memcpy` 를 쓴 적이 없는데 g++ 가 대입을 `memcpy` 호출로 만들었다
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-01/">step-01</a></span><span><a href="/xv6/tutorial/step-03/">step-03</a> →</span></div>
