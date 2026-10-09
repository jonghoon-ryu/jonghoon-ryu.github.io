---
layout: default
title: step-03
permalink: /xv6/tutorial/step-03/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-03

<p class="subtitle">printk and panic</p>

| | |
|---|---|
| **Previous tag** | `step-02` |
| **This tag** | `step-03` (commit `63c1be0`) |
| **In one line** | formatted output `printk("%d %x %p %s")`, `panic()`, and below them `consputc()` (the output half of `console.c`) |
| **C code to compare** | `git show v0.2-x86_64-c:kernel/printk.c`, `git show v0.2-x86_64-c:kernel/console.c` |

```sh
git diff --stat step-02 step-03 -- . ':!docs' ':!*.pdf'
git checkout step-03 && make clean && make qemu
```

## 1. Before (`step-02`)

Strings could be sent to the serial port as they were. Printing a number meant turning it into characters yourself.

## 2. What changed

<!-- fig:map_step_03 -->
<svg viewBox="0 0 1000 220" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="files changed from step-02 to step-03"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Change map: step-02 → step-03  (lines added / removed per file; bar length ∝ √lines)</text><text x="300.0" y="50.0" font-size="11.5" font-weight="700" fill="#c0392b" text-anchor="end">removed ←</text><text x="320.0" y="50.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="start">file</text><text x="620.0" y="50.0" font-size="11.5" font-weight="700" fill="#1e8449" text-anchor="start">→ added</text><rect x="305" y="63" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="75.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/printk.cpp</text><text x="570.0" y="75.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="64" width="236.0" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="856.0" y="75.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+133</text><rect x="305" y="85" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="97.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/console.cpp</text><text x="570.0" y="97.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="86" width="135.24884199827375" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="755.2" y="97.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+42</text><rect x="305" y="107" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="119.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/main.cpp</text><text x="570.0" y="119.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="229.1694121028357" y="108" width="65.83058789716429" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="224.2" y="119.0" font-size="11.5" fill="#c0392b" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−9</text><rect x="615" y="108" width="141.26359673431637" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="761.3" y="119.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+46</text><rect x="305" y="129" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="141.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/defs.h</text><text x="570.0" y="141.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="130" width="69.0669771673144" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="689.1" y="141.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+10</text><rect x="305" y="151" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="163.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">Makefile</text><text x="570.0" y="163.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="152" width="34.204409616308425" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="654.2" y="163.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+2</text><text x="500.0" y="196.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Total: 5 files, +233 −9 lines (docs and PDFs not counted)</text></svg>
<!-- /fig:map_step_03 -->

| File | | Added | Removed |
|---|---|---:|---:|
| `Makefile` | changed | 2 | 0 |
| `kernel/console.cpp` | new | 42 | 0 |
| `kernel/defs.h` | changed | 10 | 0 |
| `kernel/main.cpp` | changed | 46 | 9 |
| `kernel/printk.cpp` | new | 133 | 0 |
| **Total** (5 files) | | **233** | **9** |

<!-- fig:layers -->
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="layers of output"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Layers of output in step-03: printk → consputc → uartputc_sync</text><rect x="20" y="60" width="230" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="135.0" y="88.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">printk(fmt, ...)</text><text x="135.0" y="104.0" font-size="11.5" fill="#4d5656" text-anchor="middle">%d %u %x %p %s %c</text><text x="135.0" y="120.0" font-size="11.5" fill="#4d5656" text-anchor="middle">%ld %lu %lx</text><rect x="290" y="60" width="200" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="390.0" y="88.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">consputc(c)</text><text x="390.0" y="104.0" font-size="11.5" fill="#4d5656" text-anchor="middle">console.cpp</text><text x="390.0" y="120.0" font-size="11.5" fill="#4d5656" text-anchor="middle">handles BACKSPACE</text><rect x="530" y="60" width="200" height="80" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="630.0" y="96.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">uartputc_sync(c)</text><text x="630.0" y="112.0" font-size="11.5" fill="#4d5656" text-anchor="middle">uart.cpp (step-02)</text><rect x="770" y="60" width="210" height="80" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="875.0" y="88.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">COM1</text><text x="875.0" y="104.0" font-size="11.5" fill="#4d5656" text-anchor="middle">QEMU terminal</text><text x="875.0" y="120.0" font-size="11.5" fill="#4d5656" text-anchor="middle">vbox/serial.log</text><line x1="250" y1="100" x2="288" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="490" y1="100" x2="528" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="730" y1="100" x2="768" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="290" y="170" width="440" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2" stroke-dasharray="6 4"/><text x="510.0" y="199.0" font-size="11.5" fill="#4d5656" text-anchor="middle">step-04 adds fbconsputc() (the screen) here</text><line x1="510" y1="140" x2="510" y2="168" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ae)"/><rect x="20" y="240" width="960" height="45" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="266.5" font-size="11.5" fill="#4d5656" text-anchor="middle">panic(s): prints &quot;panic: &quot; + s and stops. With panicking set, other code (later the screen console) takes no locks</text></svg>
<!-- /fig:layers -->

### 2.1 `printk.cpp`

<!-- fig:printkflow -->
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="printk flow"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">printk(fmt, …): the format string, one character at a time</text><rect x="20" y="60" width="200" height="50" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="120.0" y="89.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">fmt[i]</text><rect x="280" y="30" width="260" height="44" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="410.0" y="48.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">not &#x27;%&#x27;</text><text x="410.0" y="64.0" font-size="11.5" fill="#4d5656" text-anchor="middle">consputc(c)</text><rect x="280" y="95" width="260" height="44" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="410.0" y="121.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">&#x27;%&#x27;: look at c0 c1 c2 after it</text><line x1="220" y1="75" x2="278" y2="52" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="220" y1="95" x2="278" y2="117" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="600" y="30" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="47.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">d</text><text x="720.0" y="47.0" font-size="11.5" fill="#4d5656" text-anchor="start">printint(int, 10, signed)</text><rect x="600" y="59" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="76.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">ld / lld</text><text x="720.0" y="76.0" font-size="11.5" fill="#4d5656" text-anchor="start">printint(uint64, 10, signed)</text><rect x="600" y="88" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="105.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">u / lu / llu</text><text x="720.0" y="105.0" font-size="11.5" fill="#4d5656" text-anchor="start">printint(…, 10, unsigned)</text><rect x="600" y="117" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="134.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">x / lx / llx</text><text x="720.0" y="134.0" font-size="11.5" fill="#4d5656" text-anchor="start">printint(…, 16)</text><rect x="600" y="146" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="163.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">p</text><text x="720.0" y="163.0" font-size="11.5" fill="#4d5656" text-anchor="start">printptr: 0x + 16 digits</text><rect x="600" y="175" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="192.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">s</text><text x="720.0" y="192.0" font-size="11.5" fill="#4d5656" text-anchor="start">string (&quot;(null)&quot; for nullptr)</text><rect x="600" y="204" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="221.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">c</text><text x="720.0" y="221.0" font-size="11.5" fill="#4d5656" text-anchor="start">one character</text><rect x="600" y="233" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="250.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">%</text><text x="720.0" y="250.0" font-size="11.5" fill="#4d5656" text-anchor="start">&#x27;%&#x27;</text><rect x="600" y="262" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="279.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">other</text><text x="720.0" y="279.0" font-size="11.5" fill="#4d5656" text-anchor="start">&#x27;%&#x27; and that character, as is (to stand out)</text><line x1="540" y1="117" x2="598" y2="117" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="300.0" y="200.0" font-size="11.5" fill="#4d5656" text-anchor="middle">va_arg(ap, type) takes the next argument (&lt;stdarg.h&gt;: a header from the compiler)</text><text x="300.0" y="225.0" font-size="11.5" fill="#4d5656" text-anchor="middle">two-letter formats like %ld skip ahead (i += 1; %lld: i += 2)</text></svg>
<!-- /fig:printkflow -->

Almost the same as the C version's `printk.c`. `printint()` turns a number into characters in a given base:

[`kernel/printk.cpp:20–47`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-03/kernel/printk.cpp#L20-L47) (tag `step-03`)

```cpp
static constexpr char digits[] = "0123456789abcdef";

static void
printint(long long xx, int base, int sign)
{
  char buf[20];
  int i;
  unsigned long long x;

  if (sign && (sign = (xx < 0)))
    x = -xx;
  else
    x = xx;

  i = 0;
  do {
    buf[i++] = digits[x % base];
  } while ((x /= base) != 0);

  if (sign)
    buf[i++] = '-';

  while (--i >= 0)
    consputc(buf[i]);
}

static void
printptr(uint64 x)
```

<!-- fig:printint -->
<svg viewBox="0 0 1000 250" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="printint"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">printint(255, 16, 0): digits collected lowest first, printed in reverse</text><rect x="30" y="55" width="140" height="40" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="100.0" y="79.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">x = 255</text><rect x="200" y="55" width="260" height="40" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="330.0" y="79.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">255 % 16 = 15 → &#x27;f&#x27;</text><rect x="490" y="55" width="140" height="40" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="560.0" y="79.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">x = 15</text><line x1="170" y1="75" x2="198" y2="75" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="460" y1="75" x2="488" y2="75" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="30" y="107" width="140" height="40" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="100.0" y="131.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">x = 15</text><rect x="200" y="107" width="260" height="40" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="330.0" y="131.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">15 % 16 = 15 → &#x27;f&#x27;</text><rect x="490" y="107" width="140" height="40" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="560.0" y="131.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">x = 0</text><line x1="170" y1="127" x2="198" y2="127" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="460" y1="127" x2="488" y2="127" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="800.0" y="60.0" font-size="12" font-weight="700" fill="#4d5656" text-anchor="middle">buf</text><rect x="740" y="70" width="46" height="46" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="763.0" y="100.0" font-size="18" font-weight="700" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">f</text><text x="763.0" y="132.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">buf[0]</text><rect x="790" y="70" width="46" height="46" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="813.0" y="100.0" font-size="18" font-weight="700" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">f</text><text x="813.0" y="132.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">buf[1]</text><text x="800.0" y="165.0" font-size="11.5" fill="#4d5656" text-anchor="middle">→ consputc(buf[1]), then buf[0]</text><text x="500.0" y="215.0" font-size="11.5" fill="#4d5656" text-anchor="middle">negatives (%d): computed without the sign, &#x27;-&#x27; stored last so it prints first.  digits[] = &quot;0123456789abcdef&quot; (constexpr)</text></svg>
<!-- /fig:printint -->

The body of `printk()` walks the format string and branches on the character after `%` (`%d`, `%ld`, `%lld`, `%u`, `%x`, `%p`, `%s`, `%c`, `%%`).
`<stdarg.h>` is not a C library header but **one the compiler provides**, so a freestanding kernel can use it.

Different from the C version: the C version takes `pr.lock` so that output from several CPUs doesn't interleave. There is one CPU and no lock code yet, so it's left out (it returns with `spinlock.cpp`).

`panic()`:

[`kernel/printk.cpp:125–133`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-03/kernel/printk.cpp#L125-L133) (tag `step-03`)

```cpp
panic(const char *s)
{
  panicking = 1;
  printk("panic: ");
  printk("%s\n", s);
  panicked = 1; // freeze uart output from other CPUs
  for (;;)
    ;
}
```

Its declaration has `[[noreturn]]` (C++11): the compiler knows the function never returns, which avoids warnings about the code after it.

### 2.2 The `format(printf)` attribute: a check the C version lacks

<!-- fig:fmtcheck -->
<svg viewBox="0 0 1000 220" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="format check"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">The format(printf) attribute: g++ checks printk&#x27;s argument types (no such check in C)</text><rect x="20" y="55" width="470" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="255.0" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">declaration (defs.h)</text><text x="255.0" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">int printk(const char *, ...)</text><text x="255.0" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  __attribute__((format(printf, 1, 2)));</text><rect x="530" y="55" width="450" height="80" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="755.0" y="83.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">caught in the first build (main.cpp)</text><text x="755.0" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">&#x27;%p&#x27; expects &#x27;void*&#x27;, but … &#x27;long long unsigned int&#x27;</text><text x="755.0" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">&#x27;%ld&#x27; expects &#x27;long int&#x27;, but … &#x27;long long unsigned int&#x27;</text><line x1="490" y1="95" x2="528" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="500.0" y="170.0" font-size="11.5" fill="#4d5656" text-anchor="middle">bootinfo&#x27;s fields are all unsigned long long, shared by the loader (clang) and the kernel (g++) → printed via (void *) and (uint64)</text><text x="500.0" y="195.0" font-size="11.5" fill="#4d5656" text-anchor="middle">on x86-64 the sizes match and the output was right anyway, but the types were wrong; the check catches it at compile time</text></svg>
<!-- /fig:fmtcheck -->

[`kernel/defs.h:10–14`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-03/kernel/defs.h#L10-L14) (tag `step-03`)

```cpp
// printk.cpp
// format(printf): g++ checks each call's arguments against the
// format string, as it does for printf. the C version has no check.
int printk(const char *, ...) __attribute__((format(printf, 1, 2)));
[[noreturn]] void panic(const char *);
```

### 2.3 `console.cpp` (output only)

Only `consputc()` and `consoleinit()` come back. The input side (`consoleintr`, `consoleread`) and `consolewrite` need interrupts and processes and come later:

[`kernel/console.cpp:16–39`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-03/kernel/console.cpp#L16-L39) (tag `step-03`)

```cpp
// C: #define BACKSPACE 0x100
constexpr int BACKSPACE = 0x100; // erase the last output character

//
// send one character to the uart, but don't use
// interrupts or sleep(). safe to be called from
// interrupts, e.g. by printk and to echo input
// characters.
//
void
consputc(int c)
{
  if (c == BACKSPACE) {
    // if the user typed backspace, overwrite with a space.
    uartputc_sync('\b');
    uartputc_sync(' ');
    uartputc_sync('\b');
  } else {
    uartputc_sync(c);
  }
}

void
consoleinit()
```

### 2.4 `main.cpp`: printing the boot information

With numbers available, `main()` prints what the loader handed over (screen, ACPI, fs.img, and the UEFI memory map summed by type):

[`kernel/main.cpp:32–54`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-03/kernel/main.cpp#L32-L54) (tag `step-03`)

```cpp
printbootinfo()
{
  // bootinfo's fields are unsigned long long (see bootinfo.h);
  // the casts match them to %p and %lu, which g++ checks.
  printk("screen: %dx%d, frame buffer at %p\n", (int)bootinfo.fb_width,
         (int)bootinfo.fb_height, (void *)bootinfo.fb_base);
  printk("ACPI root pointer at %p\n", (void *)bootinfo.rsdp);
  printk("fs.img: %lu bytes at %p\n", (uint64)bootinfo.fsimg_size,
         (void *)bootinfo.fsimg);

  uint64 pages[16] = {};
  int n = 0;
  for (uint64 off = 0; off < bootinfo.memmap_size;
       off += bootinfo.memmap_descsize, n++) {
    auto d = reinterpret_cast<efi_memdesc *>(bootinfo.memmap + off);
    pages[d->type < 15 ? d->type : 15] += d->npages;
  }
  printk("UEFI memory map: %d entries\n", n);
  for (uint t = 0; t < 16; t++)
    if (pages[t] != 0)
      printk("  %s: %ld pages (%ld MB)\n", memtype(t), pages[t],
             pages[t] * 4096 / (1024 * 1024));
}
```

## 3. After

QEMU's serial output (`make qemu`):

```
xv6 kernel is booting (C++, step 3)

screen: 1280x800, frame buffer at 0x0000000080000000
ACPI root pointer at 0x000000001f77e014
fs.img: 1024 bytes at 0x0000000007ffe000
UEFI memory map: 131 entries
  reserved: 3211392 pages (12544 MB)
  loader code: 33 pages (0 MB)
  ...
  free: 118232 pages (461 MB)
  ...
nothing else yet; halting
```

The screen is still step-01's dark blue picture: `printk()` goes to the serial port only (the screen is the next step).

- `free: 118232 pages (461 MB)`: the part of QEMU's 512 MB the firmware doesn't use. `kalloc.cpp` (Step 12) will hand it out
- `reserved: 12544 MB` is far more than the VM's 512 MB of RAM: the memory map's "reserved" also covers address ranges that aren't RAM. The kernel only uses `free` (type 7)

<div class="check" markdown="1">
**Check against the code**

- remove the `(void *)` in `main.cpp`'s `printk("%p", (void *)bootinfo.fb_base)` and build: the error in the diagram above
- put `panic("test")` in `main()` and boot: it stops after `panic: test`
- `git diff v0.2-x86_64-c:kernel/printk.c step-03:kernel/printk.cpp`: the lock left out, the `constexpr` added
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-02/">step-02</a></span><span><a href="/xv6/tutorial/step-04/">step-04</a> →</span></div>
