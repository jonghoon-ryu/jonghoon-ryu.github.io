---
layout: default
title: step-05
permalink: /xv6/tutorial/step-05/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-05

<p class="subtitle">Keyboard input by polling</p>

| | |
|---|---|
| **Previous tag** | `step-04` |
| **This tag** | `step-05` (commit `42a80d2`) |
| **In one line** | the PS/2 keyboard `kbd.cpp`, console input `consoleintr()` and serial input `uartintr()`. With no interrupts yet, `main()`'s loop keeps asking (polling) |
| **C code to compare** | `git show v0.2-x86_64-c:kernel/kbd.c`, `kbd.h`, and `consoleintr` in `console.c` |

```sh
git diff --stat step-04 step-05 -- . ':!docs' ':!*.pdf'
git checkout step-05 && make clean && make vbox     # type in the window
```

## 1. Before (`step-04`)

Output went to the screen and the serial port. There was no input: `main()` printed the boot information and stopped with `hlt`.

In the C plan the keyboard returns only after interrupts (IDT, IOAPIC). To see "type and it shows on the screen" earlier, this step was added: **the same functions, called from a loop instead of by interrupts**.

## 2. What changed

<!-- fig:map_step_05 -->
<svg viewBox="0 0 1000 264" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="files changed from step-04 to step-05"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Change map: step-04 → step-05  (lines added / removed per file; bar length ∝ √lines)</text><text x="300.0" y="50.0" font-size="11" font-weight="700" fill="#c0392b" text-anchor="end">removed ←</text><text x="320.0" y="50.0" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="start">file</text><text x="620.0" y="50.0" font-size="11" font-weight="700" fill="#1e8449" text-anchor="start">→ added</text><rect x="305" y="63" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="75.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/kbd.h</text><text x="570.0" y="75.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="64" width="236.0" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="856.0" y="75.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+154</text><rect x="305" y="85" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="97.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/kbd.cpp</text><text x="570.0" y="97.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="86" width="219.7436867754546" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="839.7" y="97.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+133</text><rect x="305" y="107" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="119.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/console.cpp</text><text x="570.0" y="119.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="251.93214365483252" y="108" width="43.06785634516749" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="246.9" y="119.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−4</text><rect x="615" y="108" width="167.57503986226806" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="787.6" y="119.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+76</text><rect x="305" y="129" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="141.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/uart.cpp</text><text x="570.0" y="141.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="243.60133304777594" y="130" width="51.398666952224055" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="238.6" y="141.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−6</text><rect x="615" y="130" width="105.8082577329567" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="725.8" y="141.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+29</text><rect x="305" y="151" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="163.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/main.cpp</text><text x="570.0" y="163.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="243.60133304777594" y="152" width="51.398666952224055" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="238.6" y="163.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−6</text><rect x="615" y="152" width="86.78751993113403" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="706.8" y="163.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+19</text><rect x="305" y="173" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="185.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/defs.h</text><text x="570.0" y="185.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="270.4660718274163" y="174" width="24.533928172583746" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="265.5" y="185.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−1</text><rect x="615" y="174" width="51.398666952224055" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="671.4" y="185.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+6</text><rect x="305" y="195" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="207.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">Makefile</text><text x="570.0" y="207.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="196" width="24.533928172583746" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="644.5" y="207.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+1</text><text x="500.0" y="240.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Total: 7 files, +418 −17 lines (docs and PDFs not counted)</text></svg>
<!-- /fig:map_step_05 -->

| File | | Added | Removed |
|---|---|---:|---:|
| `Makefile` | changed | 1 | 0 |
| `kernel/console.cpp` | changed | 76 | 4 |
| `kernel/defs.h` | changed | 6 | 1 |
| `kernel/kbd.cpp` | new | 133 | 0 |
| `kernel/kbd.h` | new | 154 | 0 |
| `kernel/main.cpp` | changed | 19 | 6 |
| `kernel/uart.cpp` | changed | 29 | 6 |
| **Total** (7 files) | | **418** | **17** |

<!-- fig:inputpath -->
<svg viewBox="0 0 1000 290" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="polled input"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Input: no interrupts yet, so main()&#x27;s loop calls the handlers (polling)</text><rect x="20" y="60" width="170" height="60" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="105.0" y="86.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">PS/2 keyboard</text><text x="105.0" y="102.0" font-size="11.0" fill="#4d5656" text-anchor="middle">ports 0x60, 0x64</text><rect x="20" y="140" width="170" height="60" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="105.0" y="166.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">COM1 serial</text><text x="105.0" y="182.0" font-size="11.0" fill="#4d5656" text-anchor="middle">port 0x3F8</text><rect x="240" y="60" width="200" height="60" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="340.0" y="86.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">kbdintr()</text><text x="340.0" y="102.0" font-size="11.0" fill="#4d5656" text-anchor="middle">kbdgetc(): scan code → char</text><rect x="240" y="140" width="200" height="60" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="340.0" y="166.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">uartintr()</text><text x="340.0" y="182.0" font-size="11.0" fill="#4d5656" text-anchor="middle">uartgetc()</text><rect x="500" y="95" width="210" height="70" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="605.0" y="118.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">consoleintr(c)</text><text x="605.0" y="134.0" font-size="11.0" fill="#4d5656" text-anchor="middle">echo, ^H, ^U</text><text x="605.0" y="150.0" font-size="11.0" fill="#4d5656" text-anchor="middle">collect in cons.buf</text><rect x="770" y="95" width="210" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="875.0" y="126.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">consputc()</text><text x="875.0" y="142.0" font-size="11.0" fill="#4d5656" text-anchor="middle">screen + serial</text><line x1="190" y1="90" x2="238" y2="90" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="190" y1="170" x2="238" y2="170" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="440" y1="90" x2="498" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="440" y1="170" x2="498" y2="140" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="710" y1="130" x2="768" y2="130" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="220" width="960" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="249.0" font-size="10.5" fill="#4d5656" text-anchor="middle">main(): for (;;) { kbdintr(); uartintr(); pause; } → 100% CPU. In the C version interrupts call the same functions (here: Steps 18, 19)</text></svg>
<!-- /fig:inputpath -->

### 2.1 `main()`: the polling loop

[`kernel/main.cpp:67–81`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-05/kernel/main.cpp#L67-L81) (tag `step-05`)

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

`hlt` lets the CPU sleep, but this loop keeps it 100% busy (`top` shows the VirtualBox process using a whole CPU). When interrupts come back (Steps 18, 19) it sleeps in `hlt` again.

### 2.2 `kbd.cpp`, `kbd.h`: key tables built at compile time

<!-- fig:ps2bits -->
<svg viewBox="0 0 1000 200" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="PS/2 status bits"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">PS/2 status port 0x64: the bits kbd.cpp looks at</text><text x="142.0" y="86.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="end">0x64</text><rect x="150" y="60" width="87.5" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="193.8" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="193.8" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">7</text><rect x="237.5" y="60" width="87.5" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="281.2" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="281.2" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">6</text><rect x="325.0" y="60" width="87.5" height="44" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="368.8" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">AUX</text><text x="368.8" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">5</text><rect x="412.5" y="60" width="87.5" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="456.2" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="456.2" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">4</text><rect x="500.0" y="60" width="87.5" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="543.8" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="543.8" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">3</text><rect x="587.5" y="60" width="87.5" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="631.2" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle"></text><text x="631.2" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">2</text><rect x="675.0" y="60" width="87.5" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="718.8" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">IBF</text><text x="718.8" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">1</text><rect x="762.5" y="60" width="87.5" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="806.2" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">DIB</text><text x="806.2" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><text x="500.0" y="138.0" font-size="11.5" fill="#4d5656" text-anchor="middle">DIB (0x01): a byte is waiting at 0x60     IBF (0x02): the controller is still busy with a command (kbcwait waits)</text><text x="500.0" y="162.0" font-size="11.5" fill="#4d5656" text-anchor="middle">AUX (0x20): the byte came from the mouse → dropped.   No controller: 0xFF (all ones), which kbdgetc filters first</text></svg>
<!-- /fig:ps2bits -->

`kbdgetc()` is the C version's (scan code → character; [v0.2](/xv6/tutorial/v0.2-x86_64-c/) 2.2). The biggest change is the **key tables**:

<!-- fig:keymap -->
<svg viewBox="0 0 1000 260" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="key tables"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Key tables: C99 designated initializers → a constexpr function (tables built at compile time)</text><rect x="20" y="55" width="440" height="110" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="240.0" y="82.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">C version (kbd.h)</text><text x="240.0" y="98.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">static uchar shiftcode[256] = {</text><text x="240.0" y="114.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  [0x1D] CTL, [0x2A] SHIFT, ...</text><text x="240.0" y="130.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">};</text><text x="240.0" y="146.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">// C++ has no designated array initializers</text><line x1="460" y1="110" x2="528" y2="110" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="530" y="55" width="450" height="110" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="755.0" y="90.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">C++ version (kbd.h)</text><text x="755.0" y="106.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">constexpr Keymap shiftcode = makemap({</text><text x="755.0" y="122.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  {0x1D, CTL}, {0x2A, SHIFT}, ...</text><text x="755.0" y="138.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">});</text><rect x="20" y="190" width="960" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="219.0" font-size="10.5" fill="#4d5656" text-anchor="middle">makemap() is constexpr: g++ runs it during compilation and emits the finished 256-byte table (the same data as the C version)</text></svg>
<!-- /fig:keymap -->

[`kernel/kbd.h:44–77`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-05/kernel/kbd.h#L44-L77) (tag `step-05`)

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

- `makemap()`'s parameter `const KeyAt (&at)[M]` is **a reference to an array**, so the compiler deduces the length `M` and a braced list can be passed directly
- the ten arrow keys repeated in all three tables (`normalmap`, `shiftmap`, `ctlmap`) are now one `e0keys` array
- `Keymap` has an `operator[]`, so `shiftcode[data]` reads as in the C version

[platform: real PC] Without a keyboard controller the ports read `0xFF`, which looks like an endless stream of "a byte is waiting". `kbdgetc()` filters `0xFF` first (a check the C version lacks; a real PC later turned out to read `0x55` too → [step-06](/xv6/tutorial/step-06/)).

### 2.3 `consoleintr()` in `console.cpp`, `uartintr()` in `uart.cpp`

<!-- fig:ring -->
<svg viewBox="0 0 1000 330" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="console input buffer"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">cons.buf: a 128-byte circular buffer with three indexes r, w, e</text><rect x="60" y="80" width="55" height="50" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="87.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">l</text><text x="87.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><rect x="115" y="80" width="55" height="50" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="142.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">s</text><text x="142.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">1</text><rect x="170" y="80" width="55" height="50" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="197.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">\n</text><text x="197.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">2</text><rect x="225" y="80" width="55" height="50" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="252.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">e</text><text x="252.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">3</text><rect x="280" y="80" width="55" height="50" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="307.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">c</text><text x="307.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">4</text><rect x="335" y="80" width="55" height="50" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="362.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">h</text><text x="362.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">5</text><rect x="390" y="80" width="55" height="50" rx="0" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="417.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="417.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">6</text><rect x="445" y="80" width="55" height="50" rx="0" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="472.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="472.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">7</text><rect x="500" y="80" width="55" height="50" rx="0" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="527.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="527.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">8</text><rect x="555" y="80" width="55" height="50" rx="0" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="582.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="582.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">9</text><rect x="610" y="80" width="55" height="50" rx="0" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="637.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="637.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">10</text><rect x="665" y="80" width="55" height="50" rx="0" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="692.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="692.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">11</text><rect x="720" y="80" width="55" height="50" rx="0" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="747.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="747.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">12</text><rect x="775" y="80" width="55" height="50" rx="0" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="802.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="802.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">13</text><rect x="830" y="80" width="55" height="50" rx="0" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="857.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="857.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">14</text><rect x="885" y="80" width="55" height="50" rx="0" fill="#ffffff" stroke="#566573" stroke-width="1.5"/><text x="912.5" y="112.0" font-size="15" fill="#2c3e50" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="912.5" y="146.0" font-size="9.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">15</text><line x1="60" y1="185" x2="60" y2="133" stroke="#c0392b" stroke-width="2" marker-end="url(#ae)"/><text x="60.0" y="200.0" font-size="14" font-weight="700" fill="#c0392b" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">r</text><line x1="225" y1="185" x2="225" y2="133" stroke="#1e8449" stroke-width="2" marker-end="url(#ae)"/><text x="225.0" y="200.0" font-size="14" font-weight="700" fill="#1e8449" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">w</text><line x1="390" y1="185" x2="390" y2="133" stroke="#b7950b" stroke-width="2" marker-end="url(#ae)"/><text x="390.0" y="200.0" font-size="14" font-weight="700" fill="#b7950b" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">e</text><text x="500.0" y="70.0" font-size="11" fill="#4d5656" text-anchor="start">… really 128 cells; indexes wrap with % INPUT_BUF_SIZE</text><rect x="60" y="225" width="280" height="85" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="200.0" y="255.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">r … w: finished lines</text><text x="200.0" y="271.5" font-size="10.5" fill="#4d5656" text-anchor="middle">what read() will take</text><text x="200.0" y="287.5" font-size="10.5" fill="#4d5656" text-anchor="middle">(&quot;ls\n&quot;)</text><rect x="360" y="225" width="280" height="85" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="500.0" y="255.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">w … e: the line being typed</text><text x="500.0" y="271.5" font-size="10.5" fill="#4d5656" text-anchor="middle">can be edited with backspace, ^U</text><text x="500.0" y="287.5" font-size="10.5" fill="#4d5656" text-anchor="middle">(&quot;ech&quot;)</text><rect x="660" y="225" width="280" height="85" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="800.0" y="255.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Different in step-05</text><text x="800.0" y="271.5" font-size="10.5" fill="#4d5656" text-anchor="middle">no reader (consoleread) yet, so a</text><text x="800.0" y="287.5" font-size="10.5" fill="#4d5656" text-anchor="middle">finished line is dropped: r = w</text></svg>
<!-- /fig:ring -->

`consoleintr()` echoes, handles backspace (`^H`, Delete) and kill-line (`^U`), and collects characters in `cons.buf`. One place differs from the C version:

[`kernel/console.cpp:103–108`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-05/kernel/console.cpp#L103-L108) (tag `step-05`)

```cpp
      if (c == '\n' || c == C('D') || cons.e - cons.r == INPUT_BUF_SIZE) {
        // a whole line (or end-of-file) has arrived. the C version
        // wakes up consoleread() here. with no reader yet, consume
        // the line at once, so the buffer never fills up.
        cons.w = cons.e;
        cons.r = cons.w;
```

The C version wakes `consoleread()` (the shell's `read()`) when a line is complete. There is no reader yet, so the line is dropped at once; otherwise the buffer would fill after 128 characters and input would stop.

`uartintr()`: called by the serial interrupt in the C version, by the loop here:

[`kernel/uart.cpp:113–127`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-05/kernel/uart.cpp#L113-L127) (tag `step-05`)

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

## 3. After

QEMU (`Hi there!` and Ctrl+U sent with QMP `send-key`):

![step-05 in QEMU](/assets/image/xv6-tut-step-05-step05-qemu.png)

VirtualBox:

![step-05 in VirtualBox](/assets/image/xv6-tut-step-05-step05-vbox.png)

- QEMU, VirtualBox: both the keyboard and the serial port work
- real PC: **only with a PS/2 keyboard, or if the firmware emulates PS/2 for a USB keyboard.** It didn't work on the barebone of 2026-10-07 → the USB driver from [step-06](/xv6/tutorial/step-06/)

<div class="check" markdown="1">
**Check against the code**

- in `kbd.h`, is entry `0x1E` of `normalmap` `'a'`? (`makemap`'s first list starts at scan code 0)
- find the finished 256-byte tables in `objdump -s -j .rodata kernel/kernel | less`: no code that calls `makemap()` is in the binary
- remove `cons.r = cons.w;` and type more than 130 characters: input stops
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-04/">step-04</a></span><span><a href="/xv6/tutorial/step-06/">step-06</a> →</span></div>
