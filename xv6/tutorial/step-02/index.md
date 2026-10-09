---
layout: default
title: step-02
permalink: /xv6/tutorial/step-02/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-02

<p class="subtitle">The serial driver and string functions</p>

| | |
|---|---|
| **Previous tag** | `step-01` |
| **This tag** | `step-02` (commit `ff6ad7a`) |
| **In one line** | the C version's `uart.c` (output and polled input) and `string.c` in C++. `main.cpp`'s temporary serial code is gone |
| **C code to compare** | `git show v0.2-x86_64-c:kernel/uart.c`, `git show v0.2-x86_64-c:kernel/string.c` |

```sh
git diff --stat step-01 step-02 -- . ':!docs' ':!*.pdf'
git diff step-01 step-02 -- kernel/main.cpp     # how the temporary code went away
```

## 1. Before (`step-01`)

`main.cpp` had temporary functions that drove the serial port directly, `earlyuartinit()` and `earlyputs()` ([step-01](/xv6/tutorial/step-01/) 2.3). The kernel had no basic functions such as `memset`.

## 2. What changed

<!-- fig:map_step_02 -->
<svg viewBox="0 0 1000 220" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="files changed from step-01 to step-02"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Change map: step-01 → step-02  (lines added / removed per file; bar length ∝ √lines)</text><text x="300.0" y="50.0" font-size="11.5" font-weight="700" fill="#c0392b" text-anchor="end">removed ←</text><text x="320.0" y="50.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="start">file</text><text x="620.0" y="50.0" font-size="11.5" font-weight="700" fill="#1e8449" text-anchor="start">→ added</text><rect x="305" y="63" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="75.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/uart.cpp</text><text x="570.0" y="75.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="64" width="236.0" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="856.0" y="75.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+104</text><rect x="305" y="85" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="97.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/string.cpp</text><text x="570.0" y="97.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="86" width="232.65841802487387" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="852.7" y="97.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+101</text><rect x="305" y="107" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="119.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/defs.h</text><text x="570.0" y="119.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="108" width="109.35245894138548" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="729.4" y="119.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+21</text><rect x="305" y="129" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="141.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/main.cpp</text><text x="570.0" y="141.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="144.58806250067937" y="130" width="150.41193749932063" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="139.6" y="141.0" font-size="11.5" fill="#c0392b" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−41</text><rect x="615" y="130" width="80.80101809261895" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="700.8" y="141.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+11</text><rect x="305" y="151" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="163.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">Makefile</text><text x="570.0" y="163.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="266.4466444591088" y="152" width="28.553355540891165" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="261.4" y="163.0" font-size="11.5" fill="#c0392b" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−1</text><rect x="615" y="152" width="45.063557677988555" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="665.1" y="163.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+3</text><text x="500.0" y="196.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Total: 5 files, +240 −42 lines (docs and PDFs not counted)</text></svg>
<!-- /fig:map_step_02 -->

| File | | Added | Removed |
|---|---|---:|---:|
| `Makefile` | changed | 3 | 1 |
| `kernel/defs.h` | new | 21 | 0 |
| `kernel/main.cpp` | changed | 11 | 41 |
| `kernel/string.cpp` | new | 101 | 0 |
| `kernel/uart.cpp` | new | 104 | 0 |
| **Total** (5 files) | | **240** | **42** |

### 2.1 `uart.cpp`: the 16550 UART driver

A PC's serial port chip (16550) has eight registers starting at **I/O port** `0x3F8`. The RISC-V version drove the same chip at a memory address; on x86 it is `inb`/`outb`.

<!-- fig:uart -->
<svg viewBox="0 0 1000 380" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="UART registers"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">16550 UART: eight registers from I/O port 0x3F8 (COM1)</text><rect x="20" y="60" width="70" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="55.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+0</text><rect x="90" y="60" width="120" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="150.0" y="84.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">THR / RHR</text><text x="222.0" y="85.0" font-size="11.5" fill="#4d5656" text-anchor="start">byte to send / byte received</text><rect x="20" y="106" width="70" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="55.0" y="130.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+1</text><rect x="90" y="106" width="120" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="150.0" y="130.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">IER</text><text x="222.0" y="131.0" font-size="11.5" fill="#4d5656" text-anchor="start">interrupt enable (0 for now)</text><rect x="20" y="152" width="70" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="55.0" y="176.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+2</text><rect x="90" y="152" width="120" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="150.0" y="176.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">FCR</text><text x="222.0" y="177.0" font-size="11.5" fill="#4d5656" text-anchor="start">FIFO enable, clear</text><rect x="20" y="198" width="70" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="55.0" y="222.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+3</text><rect x="90" y="198" width="120" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="150.0" y="222.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">LCR</text><text x="222.0" y="223.0" font-size="11.5" fill="#4d5656" text-anchor="start">8 bits; baud-rate setting mode</text><rect x="20" y="244" width="70" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="55.0" y="268.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+5</text><rect x="90" y="244" width="120" height="40" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="150.0" y="268.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">LSR</text><text x="222.0" y="269.0" font-size="11.5" fill="#4d5656" text-anchor="start">status: bit 0 received, bit 5 can send</text><rect x="560" y="60" width="420" height="120" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="770.0" y="100.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">uartputc_sync(c)</text><text x="770.0" y="116.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">while ((ReadReg(LSR) &amp; LSR_TX_IDLE) == 0)</text><text x="770.0" y="132.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  ;   // wait until it can send</text><text x="770.0" y="148.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">WriteReg(THR, c);</text><rect x="560" y="200" width="420" height="150" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="770.0" y="247.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">[platform: real PC] no COM1</text><text x="770.0" y="263.0" font-size="11.5" fill="#4d5656" text-anchor="middle">a missing port reads 0xFF</text><text x="770.0" y="279.0" font-size="11.5" fill="#4d5656" text-anchor="middle">LSR = 0xFF → TX_IDLE looks set → no waiting:</text><text x="770.0" y="295.0" font-size="11.5" fill="#4d5656" text-anchor="middle">bytes are written into nothing, nothing hangs</text><text x="770.0" y="311.0" font-size="11.5" fill="#4d5656" text-anchor="middle">RX_READY looks set too → uartgetc() filters 0xFF first</text><text x="20.0" y="320.0" font-size="11.5" fill="#4d5656" text-anchor="start">RISC-V version: the UART is at memory address 0x10000000 (memory-mapped I/O, read and written through pointers)</text><text x="20.0" y="342.0" font-size="11.5" fill="#4d5656" text-anchor="start">x86 PC: a separate I/O port address space (inb / outb instructions)</text></svg>
<!-- /fig:uart -->

The C version's macros became typed C++ constants and inline functions:

[`kernel/uart.cpp:25–47`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-02/kernel/uart.cpp#L25-L47) (tag `step-02`)

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

<!-- fig:uartinit -->
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="UART initialization order"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">What uartinit() writes, in order (I/O port COM1 = 0x3F8)</text><rect x="15" y="60" width="152" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="91.0" y="91.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">IER ← 0x00</text><text x="91.0" y="107.0" font-size="11.5" fill="#4d5656" text-anchor="middle">interrupts off</text><rect x="180" y="60" width="152" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="256.0" y="91.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">LCR ← 0x80</text><text x="256.0" y="107.0" font-size="11.5" fill="#4d5656" text-anchor="middle">baud-rate mode (DLAB)</text><line x1="167" y1="95" x2="179" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="345" y="60" width="152" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="421.0" y="91.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">+0 ← 0x03</text><text x="421.0" y="107.0" font-size="11.5" fill="#4d5656" text-anchor="middle">divisor, low byte</text><line x1="332" y1="95" x2="344" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="510" y="60" width="152" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="586.0" y="91.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">+1 ← 0x00</text><text x="586.0" y="107.0" font-size="11.5" fill="#4d5656" text-anchor="middle">divisor, high byte</text><line x1="497" y1="95" x2="509" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="675" y="60" width="152" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="751.0" y="91.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">LCR ← 0x03</text><text x="751.0" y="107.0" font-size="11.5" fill="#4d5656" text-anchor="middle">8 bits, no parity</text><line x1="662" y1="95" x2="674" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="840" y="60" width="152" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="916.0" y="91.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">FCR ← 0x07</text><text x="916.0" y="107.0" font-size="11.5" fill="#4d5656" text-anchor="middle">enable and clear FIFOs</text><line x1="827" y1="95" x2="839" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="15" y="160" width="480" height="110" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="255.0" y="187.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Speed: 115200 / divisor</text><text x="255.0" y="203.0" font-size="11.5" fill="#4d5656" text-anchor="middle">the UART&#x27;s base rate of 115200 baud divided by 3 = 38400 baud</text><text x="255.0" y="219.0" font-size="11.5" fill="#4d5656" text-anchor="middle">only while DLAB (LCR bit 7) is set</text><text x="255.0" y="235.0" font-size="11.5" fill="#4d5656" text-anchor="middle">are +0 and +1 the divisor registers</text><text x="255.0" y="251.0" font-size="11.5" fill="#4d5656" text-anchor="middle">(normally +0 = THR/RHR, +1 = IER)</text><rect x="515" y="160" width="470" height="110" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="750.0" y="195.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Different from the C version</text><text x="750.0" y="211.0" font-size="11.5" fill="#4d5656" text-anchor="middle">the C version enables the transmit and receive</text><text x="750.0" y="227.0" font-size="11.5" fill="#4d5656" text-anchor="middle">interrupts (IER) at the end; this step has no</text><text x="750.0" y="243.0" font-size="11.5" fill="#4d5656" text-anchor="middle">interrupt handling yet, so it doesn&#x27;t (Step 18)</text></svg>
<!-- /fig:uartinit -->

`uartinit()` sets the registers in the same order as the C version, with one difference: the C version enables transmit and receive interrupts at the end, and there is no interrupt handling yet, so they stay off:

[`kernel/uart.cpp:53–76`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-02/kernel/uart.cpp#L53-L76) (tag `step-02`)

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

Only **the polled part** comes back in this step: `uartinit()`, `uartputc_sync()`, `uartgetc()`. The buffered `uartputc()`/`uartwrite()` and `uartintr()` need `sleep()` and interrupts and come later.

<!-- fig:lsrbits -->
<svg viewBox="0 0 1000 210" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="LSR bits"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">LSR (line status, COM1 + 5): the two bits xv6 looks at</text><text x="142.0" y="86.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="end">LSR</text><rect x="150" y="60" width="87.5" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="193.8" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="193.8" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">7</text><rect x="237.5" y="60" width="87.5" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="281.2" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="281.2" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">6</text><rect x="325.0" y="60" width="87.5" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="368.8" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">TX_IDLE</text><text x="368.8" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">5</text><rect x="412.5" y="60" width="87.5" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="456.2" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="456.2" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">4</text><rect x="500.0" y="60" width="87.5" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="543.8" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="543.8" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">3</text><rect x="587.5" y="60" width="87.5" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="631.2" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="631.2" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">2</text><rect x="675.0" y="60" width="87.5" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="718.8" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="718.8" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">1</text><rect x="762.5" y="60" width="87.5" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="806.2" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">RX_READY</text><text x="806.2" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><text x="500.0" y="140.0" font-size="11.5" fill="#4d5656" text-anchor="middle">TX_IDLE (1 &lt;&lt; 5): THR is empty and takes the next byte → uartputc_sync() waits for it</text><text x="500.0" y="163.0" font-size="11.5" fill="#4d5656" text-anchor="middle">RX_READY (1 &lt;&lt; 0): a received byte is in RHR → uartgetc() reads it</text><text x="500.0" y="186.0" font-size="11.5" fill="#7d3c98" text-anchor="middle">no port: 0xFF, every bit looks set → output just disappears, and uartgetc() filters 0xFF on input</text></svg>
<!-- /fig:lsrbits -->

The `0xFF` check in `uartgetc()` is **not in the C version** (it is for real PCs; diagram above):

[`kernel/uart.cpp:95–104`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-02/kernel/uart.cpp#L95-L104) (tag `step-02`)

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

### 2.2 `string.cpp`: memory and string functions

`memset`, `memcmp`, `memmove`, `memcpy`, `strncmp`, `strncpy`, `safestrcpy`, `strlen`. The bodies are the C version's. What differs is their **linkage**:

[`kernel/defs.h:6–16`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-02/kernel/defs.h#L6-L16) (tag `step-02`)

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

[`kernel/string.cpp:4–8`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-02/kernel/string.cpp#L4-L8) (tag `step-02`)

```cpp
// memset, memcmp, memmove and memcpy have C linkage (extern "C" in
// defs.h): g++ itself may emit calls to them, for example to zero
// or copy a large struct, and looks for those plain names.
// their size arguments are uint64 (size_t), not uint as in the C
// version, to match what those compiler-made calls pass.
```

C++ mixes the parameter types into a function's name (`strlen` → `_Z6strlenPKc`). But when g++ copies or zeroes a large struct, it **emits calls to `memcpy` and `memset` itself**, and then it looks for the C names.
So those four use `extern "C"` (C names); the rest keep C++ names.

<!-- fig:cxx -->
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="C compared with C++"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">C → C++: the same machine code, more checking</text><text x="250.0" y="52.0" font-size="12.5" font-weight="700" fill="#4d5656" text-anchor="middle">C version</text><text x="620.0" y="52.0" font-size="12.5" font-weight="700" fill="#4d5656" text-anchor="middle">C++ version</text><rect x="20" y="64" width="400" height="46" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="220.0" y="91.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">#define LSR 5</text><line x1="420" y1="87" x2="448" y2="87" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="450" y="64" width="340" height="46" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="620.0" y="91.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">constexpr ushort LSR = 5;</text><text x="800.0" y="91.0" font-size="11.5" fill="#4d5656" text-anchor="start">typed; seen by the debugger</text><rect x="20" y="120" width="400" height="46" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="220.0" y="147.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">#define ReadReg(reg) (inb(COM1 + (reg)))</text><line x1="420" y1="143" x2="448" y2="143" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="450" y="120" width="340" height="46" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="620.0" y="147.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">static inline uchar ReadReg(ushort reg)</text><text x="800.0" y="147.0" font-size="11.5" fill="#4d5656" text-anchor="start">types checked; no macro traps</text><rect x="20" y="176" width="400" height="46" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="220.0" y="203.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">(char *)dst</text><line x1="420" y1="199" x2="448" y2="199" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="450" y="176" width="340" height="46" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="620.0" y="203.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">static_cast&lt;char *&gt;(dst)</text><text x="800.0" y="203.0" font-size="11.5" fill="#4d5656" text-anchor="start">the kind of cast is visible</text><rect x="20" y="232" width="400" height="46" rx="3" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="220.0" y="259.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">void *memset(void *, int, uint)</text><line x1="420" y1="255" x2="448" y2="255" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="450" y="232" width="340" height="46" rx="3" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="620.0" y="259.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">extern &quot;C&quot; void *memset(..., uint64)</text><text x="800.0" y="259.0" font-size="11.5" fill="#4d5656" text-anchor="start">g++ calls it itself: C name</text></svg>
<!-- /fig:cxx -->

### 2.3 `main.cpp`

`earlyuartinit()` → `uartinit()`; `earlyputs()` → a small `uartputs()` on top of `uart.cpp`'s `uartputc_sync()`. The screen painting and the "xv6" letters stay.

## 3. After

The output is almost the same as `step-01` (just the step number):

```
xv6 kernel is booting (C++, step 2)
nothing else yet; halting
```

It looks the same, but serial output now goes through the same function as in the C version (`uartputc_sync`). The next step's `printk()` is built on it.

<div class="check" markdown="1">
**Check against the code**

- `nm kernel/kernel | grep -E " T (mem|_Z.*str)"`: `memset` and friends have plain names, `strlen` and friends `_Z…` names
- `git diff v0.2-x86_64-c:kernel/uart.c step-02:kernel/uart.cpp`: the functions left out (`uartputc`, `uartwrite`, `uartintr`) and the added `0xFF` check
- remove `memcpy` from `string.cpp` and `defs.h`, add a large struct assignment to `main()` (`struct Big { char x[256]; } a{}, b; b = a;`) and build: the link fails with ``undefined reference to `memcpy'``. The code never calls `memcpy`; g++ turned the assignment into a call
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-01/">step-01</a></span><span><a href="/xv6/tutorial/step-03/">step-03</a> →</span></div>
