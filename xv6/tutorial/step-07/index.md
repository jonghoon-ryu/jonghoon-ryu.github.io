---
layout: default
title: "step-07 : xHCI USB 컨트롤러 시작"
permalink: /xv6/tutorial/step-07/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# `step-07` : xHCI USB 컨트롤러 시작

| | |
|---|---|
| **앞 태그** | `step-06` |
| **이 태그** | `step-07` (커밋 `695f83e`) |
| **한 줄** | `xhci.h`, `xhci.cpp` : PCI 에서 찾은 USB 3 컨트롤러 (xHCI) 를 펌웨어에게서 넘겨받아 리셋하고, 메모리에 링을 만들어 시작한다. 연결된 포트를 리셋하고 속도를 찍는다 |
| **비교할 것** | [xHCI 명세 1.2](https://www.intel.com/content/www/us/en/products/docs/io/universal-serial-bus/extensible-host-controler-interface-usb-xhci.html) 4.2 (시작), 4.9 (링), 5 (레지스터). 코드 주석의 `(xHCI 4.9.2)` 같은 절 번호 |

```sh
git diff --stat step-06 step-07 -- . ':!docs' ':!*.pdf'
git checkout step-07 && make clean && make qemu USB=1
```

## 1. 이전 상태 (`step-06`)

PCI 목록에서 xHCI 컨트롤러를 볼 수는 있었지만, 아무것도 하지 않았다. 컨트롤러는 펌웨어가 쓰던 상태 그대로였다.

## 2. 바꾼 것

| 파일 | | 더한 줄 | 지운 줄 |
|---|---|---:|---:|
| `Makefile` | 바뀜 | 2 | 1 |
| `kernel/defs.h` | 바뀜 | 4 | 0 |
| `kernel/main.cpp` | 바뀜 | 7 | 38 |
| `kernel/x86.h` | 바뀜 | 22 | 0 |
| `kernel/xhci.cpp` | 새 파일 | 568 | 0 |
| `kernel/xhci.h` | 새 파일 | 116 | 0 |
| **합계** (6 파일) | | **719** | **39** |

**`#if` 가 아니라 실행 중에 찾는다.** `usbinit()` 이 `pciscan(0x0C0330, found)` 로 xHCI 를 찾고, 없으면 (VirtualBox, `USB=1` 없는 QEMU) `usb: no xHCI controller` 만 찍는다. 같은 `usb.img` 가 세 곳에서 돈다.

### 2.1 링과 doorbell

<svg viewBox="0 0 1000 330" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="명령 링과 이벤트 링"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">xHCI 와 이야기하는 법 : 메모리의 링 + doorbell 레지스터</text><text x="20.0" y="58.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">메모리 (DMA : 컨트롤러가 직접 읽고 쓴다)</text><text x="20.0" y="84.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="start">명령 링 (cmdring) : CPU → 컨트롤러</text><rect x="20" y="90" width="48" height="34" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="44.0" y="111.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><rect x="72" y="90" width="48" height="34" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="96.0" y="111.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><rect x="124" y="90" width="48" height="34" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="148.0" y="111.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><rect x="176" y="90" width="48" height="34" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="200.0" y="111.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><rect x="228" y="90" width="48" height="34" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="252.0" y="111.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><rect x="280" y="90" width="48" height="34" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="304.0" y="111.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><rect x="332" y="90" width="48" height="34" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="356.0" y="111.0" font-size="9.5" fill="#4d5656" text-anchor="middle">Link</text><path d="M356,124 L356,138 L44,138 L44,126" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="20.0" y="184.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="start">이벤트 링 (evring) : 컨트롤러 → CPU (Link 없이 끝에서 처음으로)</text><rect x="20" y="190" width="48" height="34" rx="2" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="44.0" y="211.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><rect x="72" y="190" width="48" height="34" rx="2" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="96.0" y="211.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><rect x="124" y="190" width="48" height="34" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="148.0" y="211.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><rect x="176" y="190" width="48" height="34" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="200.0" y="211.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><rect x="228" y="190" width="48" height="34" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="252.0" y="211.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><rect x="280" y="190" width="48" height="34" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="304.0" y="211.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><rect x="332" y="190" width="48" height="34" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="356.0" y="211.0" font-size="9.5" fill="#4d5656" text-anchor="middle">TRB</text><path d="M356,224 L356,238 L44,238 L44,226" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="440" y="80" width="230" height="60" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="555.0" y="98.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU</text><text x="555.0" y="114.0" font-size="10.5" fill="#4d5656" text-anchor="middle">Ring::push() 로 TRB 를 쓰고</text><text x="555.0" y="130.0" font-size="10.5" fill="#4d5656" text-anchor="middle">db[0] = 0 (doorbell)</text><rect x="440" y="180" width="230" height="60" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="555.0" y="198.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU : poll()</text><text x="555.0" y="214.0" font-size="10.5" fill="#4d5656" text-anchor="middle">cycle 비트가 맞는 TRB 를 읽고</text><text x="555.0" y="230.0" font-size="10.5" fill="#4d5656" text-anchor="middle">ERDP 에 어디까지 읽었나</text><rect x="740" y="80" width="240" height="160" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="860.0" y="124.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">xHCI 컨트롤러</text><text x="860.0" y="140.0" font-size="10.5" fill="#4d5656" text-anchor="middle">doorbell 이 울리면</text><text x="860.0" y="156.0" font-size="10.5" fill="#4d5656" text-anchor="middle">명령 링을 읽어 실행</text><text x="860.0" y="172.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="860.0" y="188.0" font-size="10.5" fill="#4d5656" text-anchor="middle">결과, 포트 변화, 전송 완료를</text><text x="860.0" y="204.0" font-size="10.5" fill="#4d5656" text-anchor="middle">이벤트 링에 써 넣는다</text><line x1="670" y1="110" x2="738" y2="110" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="704.0" y="104.0" font-size="10.5" fill="#566573" text-anchor="middle">doorbell</text><line x1="738" y1="210" x2="672" y2="210" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="705.0" y="204.0" font-size="10.5" fill="#566573" text-anchor="middle">이벤트</text><rect x="20" y="270" width="960" height="45" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="296.5" font-size="10.5" fill="#4d5656" text-anchor="middle">TRB = 16바이트 : param (64) · status (32) · control (32, 비트 0 = cycle, 비트 15:10 = 종류).  명령·전송 링 = 한 페이지 = TRB 255개 + Link TRB.  이벤트 링 = 한 페이지 = TRB 256개 (Link 없음)</text></svg>

[`kernel/xhci.h:12–16`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-07/kernel/xhci.h#L12-L16) (태그 `step-07`)

```cpp
struct Trb {
  volatile uint64 param;
  volatile uint32 status;
  volatile uint32 control; // bit 0: cycle; bits 15:10: TRB type
};
```

<svg viewBox="0 0 1000 250" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="cycle 비트"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">cycle 비트 : &#x27;이번 바퀴의 새 TRB&#x27; 표시 (공유하는 개수 없이 생산자와 소비자가 맞춘다)</text><text x="20.0" y="54.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="start">첫 바퀴 : 생산자 cycle = 1</text><rect x="20" y="60" width="56" height="40" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="48.0" y="84.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=1</text><rect x="80" y="60" width="56" height="40" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="108.0" y="84.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=1</text><rect x="140" y="60" width="56" height="40" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="168.0" y="84.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=1</text><rect x="200" y="60" width="56" height="40" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="228.0" y="84.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=1</text><rect x="260" y="60" width="56" height="40" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="288.0" y="84.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=1</text><rect x="320" y="60" width="56" height="40" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="348.0" y="84.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=0</text><rect x="380" y="60" width="56" height="40" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="408.0" y="84.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=0</text><rect x="440" y="60" width="56" height="40" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="468.0" y="84.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=0</text><text x="520.0" y="85.0" font-size="11" fill="#4d5656" text-anchor="start">← 새것 : cycle 이 소비자의 기대값과 같은 TRB</text><text x="20.0" y="144.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="start">Link 를 지난 뒤 : cycle = 0 (뒤집힘)</text><rect x="20" y="150" width="56" height="40" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="48.0" y="174.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=0</text><rect x="80" y="150" width="56" height="40" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="108.0" y="174.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=0</text><rect x="140" y="150" width="56" height="40" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="168.0" y="174.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=0</text><rect x="200" y="150" width="56" height="40" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="228.0" y="174.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=1</text><rect x="260" y="150" width="56" height="40" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="288.0" y="174.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=1</text><rect x="320" y="150" width="56" height="40" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="348.0" y="174.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=1</text><rect x="380" y="150" width="56" height="40" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="408.0" y="174.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=1</text><rect x="440" y="150" width="56" height="40" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="468.0" y="174.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">c=1</text><text x="520.0" y="175.0" font-size="11" fill="#4d5656" text-anchor="start">← 지난 바퀴의 TRB (c=1) 는 이제 &#x27;옛것&#x27;</text><rect x="20" y="200" width="960" height="40" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="224.0" font-size="10.5" fill="#4d5656" text-anchor="middle">push() 는 param, status 를 먼저 쓰고 cycle 이 든 control 을 마지막에 쓴다 : 반쯤 쓴 TRB 를 컨트롤러가 &#x27;새것&#x27; 으로 보지 않게</text></svg>

[`kernel/xhci.cpp:131–150`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-07/kernel/xhci.cpp#L131-L150) (태그 `step-07`)

```cpp
Ring::push(uint64 param, uint32 status, uint32 control)
{
  Trb *t = &trb[idx];
  t->param = param;
  t->status = status;
  asm volatile("" ::: "memory");
  t->control = (control & ~1u) | cycle;
  if (++idx == NTRB - 1) {
    // the link TRB back to the start; Toggle Cycle (bit 1) makes
    // the controller flip its cycle state as it follows it.
    Trb *l = &trb[idx];
    l->param = (uint64)trb;
    l->status = 0;
    asm volatile("" ::: "memory");
    l->control = (TRB_LINK << 10) | (1 << 1) | cycle;
    idx = 0;
    cycle ^= 1;
  }
  return t;
}
```

이벤트를 읽는 쪽 :

[`kernel/xhci.cpp:400–423`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-07/kernel/xhci.cpp#L400-L423) (태그 `step-07`)

```cpp
Xhci::poll()
{
  // [platform: real PC] wait() polls during handoff() and reset(),
  // before the event ring exists. reading through the null pointer
  // happened to work in QEMU, but firmware that unmaps page 0 (to
  // catch null pointers) would fault, and with no IDT, reboot.
  if (evring == nullptr)
    return;
  bool any = false;
  for (;;) {
    Trb *e = &evring[evidx];
    if ((e->control & 1) != evcycle)
      break;
    event(e);
    any = true;
    if (++evidx == Ring::NTRB) {
      evidx = 0;
      evcycle ^= 1;
    }
  }
  // tell the controller how far software has read.
  if (any)
    rtw64(IR0_ERDP, (uint64)&evring[evidx] | ERDP_EHB);
}
```

(`evring == nullptr` 검사도 실제 PC 를 위한 것이다. 링을 만들기 전에 `wait()` 가 `poll()` 을 부르면 주소 0 을 읽는데, QEMU 는 괜찮지만 0번 페이지를 막아 둔 펌웨어에서는 예외가 난다.)

### 2.2 컨트롤러 시작

<svg viewBox="0 0 1000 230" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="init 순서"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Xhci::init() 의 순서 (xHCI 4.2)</text><rect x="15" y="60" width="150" height="80" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="90.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">PCI</text><text x="90.0" y="104.0" font-size="10.5" fill="#4d5656" text-anchor="middle">메모리 응답,</text><text x="90.0" y="120.0" font-size="10.5" fill="#4d5656" text-anchor="middle">버스 마스터 켬</text><rect x="180" y="60" width="150" height="80" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="255.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">ismapped()</text><text x="255.0" y="104.0" font-size="10.5" fill="#4d5656" text-anchor="middle">레지스터가 펌웨어</text><text x="255.0" y="120.0" font-size="10.5" fill="#4d5656" text-anchor="middle">페이지 테이블에?</text><line x1="165" y1="100" x2="179" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="345" y="60" width="150" height="80" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="420.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">handoff()</text><text x="420.0" y="104.0" font-size="10.5" fill="#4d5656" text-anchor="middle">펌웨어에게서</text><text x="420.0" y="120.0" font-size="10.5" fill="#4d5656" text-anchor="middle">넘겨받기</text><line x1="330" y1="100" x2="344" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="510" y="60" width="150" height="80" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="585.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">reset()</text><text x="585.0" y="104.0" font-size="10.5" fill="#4d5656" text-anchor="middle">멈춤 → HCRST</text><text x="585.0" y="120.0" font-size="10.5" fill="#4d5656" text-anchor="middle">→ 준비 기다림</text><line x1="495" y1="100" x2="509" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="675" y="60" width="150" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="750.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">메모리</text><text x="750.0" y="104.0" font-size="10.5" fill="#4d5656" text-anchor="middle">DCBAA, scratchpad</text><text x="750.0" y="120.0" font-size="10.5" fill="#4d5656" text-anchor="middle">명령·이벤트 링</text><line x1="660" y1="100" x2="674" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="840" y="60" width="150" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="915.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Run</text><text x="915.0" y="104.0" font-size="10.5" fill="#4d5656" text-anchor="middle">USBCMD.RS = 1</text><text x="915.0" y="120.0" font-size="10.5" fill="#4d5656" text-anchor="middle">포트 전원</text><line x1="825" y1="100" x2="839" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="15" y="165" width="970" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="194.0" font-size="10.5" fill="#4d5656" text-anchor="middle">실제 PC (Intel 8086:7a60) : 레지스터가 0x6001100000 (4GB 위), scratchpad 34 쪽. QEMU : 0xc000000000, scratchpad 0</text></svg>

펌웨어에게서 넘겨받기 (`[platform: real PC]` : QEMU 의 컨트롤러에는 이 기능 자체가 없다) :

[`kernel/xhci.cpp:226–249`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-07/kernel/xhci.cpp#L226-L249) (태그 `step-07`)

```cpp
Xhci::handoff()
{
  uint32 off = (r32(CAP_HCCPARAMS1) >> 16) << 2;
  while (off) {
    uint32 v = r32(off);
    if ((v & 0xFF) == 1) {
      constexpr uint32 BIOS_OWNED = 1 << 16, OS_OWNED = 1 << 24;
      if (v & BIOS_OWNED) {
        w32(off, v | OS_OWNED);
        if (!wait([&] { return (r32(off) & BIOS_OWNED) == 0; }, 1000)) {
          printk("xhci%d: firmware did not let go; taking over\n", id);
          w32(off, (r32(off) & ~BIOS_OWNED) | OS_OWNED);
        }
      }
      // turn off the firmware's SMIs, and clear their status bits.
      uint32 c = r32(off + 4);
      c &= ~((1 << 0) | (1 << 4) | (1 << 13) | (1 << 14) | (1 << 15));
      c |= 7u << 29;
      w32(off + 4, c);
    }
    uint32 next = (v >> 8) & 0xFF;
    off = next ? off + (next << 2) : 0;
  }
}
```

메모리 : 아직 `kalloc` 이 없어서 `dmapage()` 가 UEFI 메모리 맵의 빈 곳 (4GB 아래, 될 수 있으면 `PHYSTOP` 위) 에서 페이지를 떼어 준다. 시간 : 타이머가 없어서 `microdelay()` 가 TSC 로 기다린다 (TSC 가 5GHz 이하라고 가정해서 **적어도** 그만큼).

이 단계에서만 init 끝에 아무 일도 안 하는 **No Op 명령** 을 보내 링이 도는지 본다 :

[`kernel/xhci.cpp:386–391`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-07/kernel/xhci.cpp#L386-L391) (태그 `step-07`)

```cpp
  // step 7 only: one command that does nothing, to see that the
  // command ring, the doorbell and the event ring all work.
  if (command(0, 0, TRB_NOOP_COMMAND << 10) == CC_SUCCESS)
    printk("xhci%d: running: a No Op command came back\n", id);
  else
    printk("xhci%d: the No Op command failed\n", id);
```

### 2.3 포트 : 연결 → 리셋 → 속도

USB 3 소켓 하나는 컨트롤러 포트 두 개 (USB 2 용, USB 3 용) 로 보인다. 키보드는 USB 2 라서 USB 2 포트만 본다.
**PORTSC 레지스터에 쓸 때 조심** : 비트 1 (PED) 에 1 을 쓰면 포트가 꺼지고, 변화 비트들은 1 을 쓰면 지워진다. `neutral()` 이 안전한 비트만 남긴다 :

[`kernel/xhci.cpp:195–200`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-07/kernel/xhci.cpp#L195-L200) (태그 `step-07`)

```cpp
neutral(uint32 v)
{
  constexpr uint32 RO = (1 << 0) | (1 << 3) | (0xF << 10) | (1 << 30);
  constexpr uint32 RWS = (0xF << 5) | (1 << 9) | (3 << 14) | (7 << 25);
  return v & (RO | RWS);
}
```

[`kernel/xhci.cpp:478–514`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-07/kernel/xhci.cpp#L478-L514) (태그 `step-07`)

```cpp
Xhci::portchange(int port)
{
  uint32 v = portsc(port);
  setportsc(port, neutral(v) | (v & PORT_CHANGES)); // acknowledge changes

  if ((v & PORT_CCS) == 0) {
    if (porthandled[port])
      printk("xhci%d: port %d: disconnected\n", id, port);
    porthandled[port] = false;
    return;
  }
  // handled already: set up, ignored, or failed. resetting a port
  // makes the controller report a change on it again, so without
  // this an ignored device would be set up over and over (seen on
  // a real PC: a built-in MSI device, id db0:76). a device gets
  // one try per connection; unplug and replug to try again.
  if (porthandled[port])
    return;
  porthandled[port] = true;

  // [platform: real PC] keyboards are USB 2 (low or full speed),
  // so USB 3 devices are left alone.
  if (portmajor[port] == 3)
    return;
  microdelay(100 * 1000); // let the connection settle (USB 2.0 7.1.7.3)
  if ((portsc(port) & PORT_CCS) == 0)
    return;
  if (!resetport(port)) {
    printk("usb: port %d does not enable\n", port);
    return;
  }
  int speed = (portsc(port) >> 10) & 0xF;
  // step 7: say what is there; step 8 will set it up.
  static const char *names[] = { "?", "full", "low", "high", "super" };
  printk("xhci%d: port %d: a USB 2 device, %s speed\n", id, port,
         speed <= 4 ? names[speed] : "?");
}
```

### 2.4 실제 PC 에서 찾은 버그 : `porthandled`

<svg viewBox="0 0 1000 300" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="끝없는 반복 버그"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">실제 PC 에서 찾은 버그 : 포트 리셋 → 포트 변화 이벤트 → 다시 리셋 …</text><rect x="20" y="70" width="200" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="120.0" y="101.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">포트 변화 이벤트</text><text x="120.0" y="117.0" font-size="11.0" fill="#4d5656" text-anchor="middle">portpending 에 표시</text><rect x="280" y="70" width="200" height="70" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="380.0" y="101.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">portchange(port)</text><text x="380.0" y="117.0" font-size="11.0" fill="#4d5656" text-anchor="middle">연결됨 → 리셋</text><rect x="540" y="70" width="200" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="640.0" y="101.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">포트 리셋 (PR)</text><text x="640.0" y="117.0" font-size="11.0" fill="#4d5656" text-anchor="middle">끝나면 PRC 비트</text><rect x="800" y="70" width="180" height="70" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="890.0" y="101.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">장치 설정</text><text x="890.0" y="117.0" font-size="11.0" fill="#4d5656" text-anchor="middle">키보드 아님 → 무시</text><line x1="220" y1="105" x2="278" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="480" y1="105" x2="538" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="740" y1="105" x2="798" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><path d="M640,140 L640,175 L120,175 L120,142" fill="none" stroke="#c0392b" stroke-width="2" marker-end="url(#ae)"/><text x="380.0" y="192.0" font-size="11.5" fill="#c0392b" text-anchor="middle">리셋이 끝났다는 것도 &#x27;포트 변화&#x27; 이벤트로 온다 → 처음부터 다시 (영원히)</text><rect x="20" y="215" width="960" height="65" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="500.0" y="235.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">고침 : porthandled[port]</text><text x="500.0" y="251.5" font-size="10.5" fill="#4d5656" text-anchor="middle">한 연결에서 한 번 본 포트 (설정 성공, 무시, 실패 모두) 는 다시 보지 않는다. 연결이 끊기면 지운다</text><text x="500.0" y="267.5" font-size="10.5" fill="#4d5656" text-anchor="middle">QEMU 에는 키보드와 허브만 있어서 안 보였다. 실제 PC 의 MSI 메인보드 장치 (db0:76) 가 찾아 주었다</text></svg>

![실제 PC 1차 시험 : 같은 장치를 끝없이 다시 설정](/assets/image/xv6-tut-step-07-step07-realpc-loop.jpg)

(이 사진은 Step 10 까지의 코드로 찍었다. 고친 곳이 포트를 다루는 이 단계의 코드라서 여기에 둔다.)

## 3. 바뀐 뒤

![step-07 QEMU : 컨트롤러 시작, No Op, 포트 셋](/assets/image/xv6-tut-step-07-step07-qemu.png)

```
xhci0: PCI 0:3.0, vendor 1b36 device d, registers at 0x000000c000000000
xhci0: version 100, 8 ports, 32 slots, 32-byte contexts, 0 scratchpad pages
xhci0: running: a No Op command came back
xhci0: port 5: a USB 2 device, high speed
```

실제 PC (Step 10 코드) 에서는 `version 120, 25 ports, 32 slots, 32-byte contexts, 34 scratchpad pages`.

<div class="check" markdown="1">
**코드와 대조해 볼 것**

- `porthandled` 검사 두 줄을 주석 처리하고 `make qemu USB=1` : 0.1초마다 같은 줄이 영원히 (실제 PC 의 버그 그대로)
- No Op 을 300번 보내고 `cmdring.idx`, `cmdring.cycle` 찍기 : `idx 45 cycle 0` (255 개 뒤 Link 에서 뒤집힘)
- `resetport()` 앞뒤의 `portsc(port)` : `0xee1` → `0xe03`. 비트를 풀어 보기 : 비트 0 연결 (CCS), 1 사용 가능 (PED), 8:5 링크 상태 (7 Polling → 0 U0), 9 전원, 13:10 속도 (3 = high). 리셋이 PED 를 켜고 링크를 올렸다
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-06/">step-06</a></span><span><a href="/xv6/tutorial/step-08/">step-08</a> →</span></div>
