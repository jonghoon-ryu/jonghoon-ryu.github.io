---
layout: default
title: step-04
permalink: /xv6/tutorial/step-04/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-04

<p class="subtitle">Text on the screen</p>

| | |
|---|---|
| **Previous tag** | `step-03` |
| **This tag** | `step-04` (commit `918bf02`) |
| **In one line** | the C version's screen console `fbcons.c` and font `font.h` in C++. `printk()` appears on the serial port and **on the screen**; the blue screen and hand-drawn letters are gone |
| **C code to compare** | `git show v0.2-x86_64-c:kernel/fbcons.c` (diagrams in [v0.2](/xv6/tutorial/v0.2-x86_64-c/) 2.1) |

```sh
git diff --stat step-03 step-04 -- . ':!docs' ':!*.pdf'
git diff v0.2-x86_64-c:kernel/fbcons.c step-04:kernel/fbcons.cpp    # the C version vs the C++ version
git checkout step-04 && make clean && make vbox
```

## 1. Before (`step-03`)

<!-- fig:beforeafter -->
<svg viewBox="0 0 1000 260" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="before and after step-04"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">step-03 → step-04: where printk goes</text><text x="250.0" y="50.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">step-03</text><text x="750.0" y="50.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">step-04</text><rect x="40" y="65" width="140" height="44" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="110.0" y="91.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">printk</text><rect x="200" y="65" width="140" height="44" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="270.0" y="91.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">consputc</text><rect x="360" y="65" width="120" height="44" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="420.0" y="91.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">UART</text><line x1="180" y1="87" x2="198" y2="87" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="340" y1="87" x2="358" y2="87" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="40" y="130" width="440" height="100" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="260.0" y="160.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">screen</text><text x="260.0" y="176.0" font-size="10.5" fill="#4d5656" text-anchor="middle">a dark blue background painted by main.cpp</text><text x="260.0" y="192.0" font-size="10.5" fill="#4d5656" text-anchor="middle">+ hand-drawn 8×8 &quot;xv6&quot;</text><text x="260.0" y="208.0" font-size="10.5" fill="#4d5656" text-anchor="middle">(printk never reaches the screen)</text><rect x="540" y="65" width="130" height="44" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="605.0" y="91.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">printk</text><rect x="690" y="65" width="130" height="44" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="755.0" y="91.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">consputc</text><rect x="840" y="40" width="140" height="44" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="910.0" y="66.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">fbconsputc</text><rect x="840" y="100" width="140" height="44" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="910.0" y="126.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">UART</text><line x1="670" y1="87" x2="688" y2="87" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="820" y1="80" x2="838" y2="62" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="820" y1="95" x2="838" y2="120" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="540" y="165" width="440" height="65" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="760.0" y="185.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">screen</text><text x="760.0" y="201.5" font-size="10.5" fill="#4d5656" text-anchor="middle">boot messages as text (Spleen font)</text><text x="760.0" y="217.5" font-size="10.5" fill="#4d5656" text-anchor="middle">→ visible on real PCs without a serial port</text></svg>
<!-- /fig:beforeafter -->

`printk()` went to the serial port only. The screen had just the dark blue background and the hand-drawn 8×8 "xv6" painted by `main.cpp`. On a real PC without a serial port, the boot messages were invisible.

## 2. What changed

<!-- fig:map_step_04 -->
<svg viewBox="0 0 1000 242" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="files changed from step-03 to step-04"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Change map: step-03 → step-04  (lines added / removed per file; bar length ∝ √lines)</text><text x="300.0" y="50.0" font-size="11" font-weight="700" fill="#c0392b" text-anchor="end">removed ←</text><text x="320.0" y="50.0" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="start">file</text><text x="620.0" y="50.0" font-size="11" font-weight="700" fill="#1e8449" text-anchor="start">→ added</text><rect x="305" y="63" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="75.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/font.h</text><text x="570.0" y="75.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="64" width="236.0" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="856.0" y="75.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+547</text><rect x="305" y="85" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="97.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/fbcons.cpp</text><text x="570.0" y="97.0" font-size="10" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="86" width="127.64097380499176" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="747.6" y="97.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+153</text><rect x="305" y="107" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="119.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/main.cpp</text><text x="570.0" y="119.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="222.30195741383164" y="108" width="72.69804258616834" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="217.3" y="119.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−46</text><rect x="615" y="108" width="25.668179741214587" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="645.7" y="119.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+4</text><rect x="305" y="129" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="141.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/console.cpp</text><text x="570.0" y="141.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="130" width="30.08850226766052" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="650.1" y="141.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+6</text><rect x="305" y="151" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="163.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/defs.h</text><text x="570.0" y="163.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="152" width="25.668179741214587" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="645.7" y="163.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+4</text><rect x="305" y="173" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="185.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">Makefile</text><text x="570.0" y="185.0" font-size="10" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="174" width="15.834089870607293" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="635.8" y="185.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+1</text><text x="500.0" y="218.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Total: 6 files, +715 −46 lines (docs and PDFs not counted)</text></svg>
<!-- /fig:map_step_04 -->

| File | | Added | Removed |
|---|---|---:|---:|
| `Makefile` | changed | 1 | 0 |
| `kernel/console.cpp` | changed | 6 | 0 |
| `kernel/defs.h` | changed | 4 | 0 |
| `kernel/fbcons.cpp` | new | 153 | 0 |
| `kernel/font.h` | new | 547 | 0 |
| `kernel/main.cpp` | changed | 4 | 46 |
| **Total** (6 files) | | **715** | **46** |

`font.h` is the C version's, unchanged (Spleen bitmaps, 547 lines). `main.cpp` loses `paintscreen()`, `drawglyph()` and the hand-drawn letters (−50 lines).

### 2.1 `fbcons.cpp`: same job as the C version, C++ shape

<!-- fig:cursorrules -->
<svg viewBox="0 0 1000 360" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="cursor rules"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">fbconsputc(c): one character and the cursor (cx, cy)</text><rect x="30" y="50" width="90" height="32" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="75.0" y="70.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">&#x27;\n&#x27;</text><text x="135.0" y="71.0" font-size="12" fill="#4d5656" text-anchor="start">cx = 0, cy + 1</text><rect x="30" y="88" width="90" height="32" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="75.0" y="108.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">&#x27;\r&#x27;</text><text x="135.0" y="109.0" font-size="12" fill="#4d5656" text-anchor="start">cx = 0</text><rect x="30" y="126" width="90" height="32" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="75.0" y="146.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">&#x27;\b&#x27;</text><text x="135.0" y="147.0" font-size="12" fill="#4d5656" text-anchor="start">cx − 1 (stays at 0)</text><rect x="30" y="164" width="90" height="32" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="75.0" y="184.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">&#x27;\t&#x27;</text><text x="135.0" y="185.0" font-size="12" fill="#4d5656" text-anchor="start">cx to the next multiple of 8</text><rect x="30" y="202" width="90" height="32" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="75.0" y="222.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">other</text><text x="135.0" y="223.0" font-size="12" fill="#4d5656" text-anchor="start">drawchar(cx, cy, c), cx + 1</text><rect x="470" y="50" width="240" height="60" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="590.0" y="76.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">cx ≥ cols ?</text><text x="590.0" y="92.0" font-size="11.0" fill="#4d5656" text-anchor="middle">→ cx = 0, cy + 1 (wrap)</text><rect x="470" y="130" width="240" height="60" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="590.0" y="156.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">cy ≥ rows ?</text><text x="590.0" y="172.0" font-size="11.0" fill="#4d5656" text-anchor="middle">→ scroll(), cy = rows − 1</text><line x1="590" y1="110" x2="590" y2="128" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="740" y="50" width="240" height="140" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="860.0" y="100.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">around it</text><text x="860.0" y="116.0" font-size="11.0" fill="#4d5656" text-anchor="middle">cursor(BG): erase the old cursor</text><text x="860.0" y="132.0" font-size="11.0" fill="#4d5656" text-anchor="middle">… the steps on the left …</text><text x="860.0" y="148.0" font-size="11.0" fill="#4d5656" text-anchor="middle">cursor(FG): draw the new one</text><rect x="30" y="245" width="950" height="95" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="505.0" y="272.5" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Screen size → text cells (real values)</text><text x="505.0" y="288.5" font-size="11.0" fill="#4d5656" text-anchor="middle">QEMU: 1280 × 800, 16 × 32 font → 80 columns × 25 rows</text><text x="505.0" y="304.5" font-size="11.0" fill="#4d5656" text-anchor="middle">VirtualBox: 2560 × 1440, 32 × 64 font (2560 or wider) → 80 columns × 22 rows</text><text x="505.0" y="320.5" font-size="11.0" fill="#4d5656" text-anchor="middle">the barebone PC: 1920 × 1080, 16 × 32 font → 120 columns × 33 rows</text></svg>
<!-- /fig:cursorrules -->

How characters, the cursor and scrolling work is shown in [v0.2](/xv6/tutorial/v0.2-x86_64-c/) 2.1. What changed is the structure of the code:

<!-- fig:fbclass -->
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="fbcons structure"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">fbcons: C&#x27;s &#x27;global struct + functions&#x27; → C++&#x27;s &#x27;struct + member functions&#x27;</text><rect x="20" y="55" width="440" height="200" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="240.0" y="111.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">C version (fbcons.c)</text><text x="240.0" y="127.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">static struct { fb, stride, cols, rows,</text><text x="240.0" y="143.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  cx, cy, charw, charh; lock } cons;</text><text x="240.0" y="159.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="240.0" y="175.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">static void fillrect(...)  { cons.fb ... }</text><text x="240.0" y="191.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">static void drawchar(...)  { cons.fb ... }</text><text x="240.0" y="207.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">static void cursor(...), scroll(...)</text><line x1="460" y1="155" x2="528" y2="155" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="530" y="55" width="450" height="200" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="755.0" y="95.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">C++ version (fbcons.cpp)</text><text x="755.0" y="111.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">namespace {</text><text x="755.0" y="127.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">struct FbCons {</text><text x="755.0" y="143.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  uint *fb; int stride; ...</text><text x="755.0" y="159.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  void fillrect(...) { fb ... }</text><text x="755.0" y="175.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  void drawchar(...), cursor(...), scroll()</text><text x="755.0" y="191.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">};</text><text x="755.0" y="207.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">FbCons cons;</text><text x="755.0" y="223.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">}</text><text x="500.0" y="285.0" font-size="11.5" fill="#4d5656" text-anchor="middle">an anonymous namespace = C&#x27;s static: invisible outside this file. The lock (cons.lock) returns with spinlock.cpp</text></svg>
<!-- /fig:fbclass -->

[`kernel/fbcons.cpp:33–44`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-04/kernel/fbcons.cpp#L33-L44) (tag `step-04`)

```cpp
namespace {

// the C version keeps the same fields in a static struct and has
// free functions fillrect(), drawchar(), cursor(), scroll() that
// use it; here they are its member functions.
// (the C version's cons.lock comes back with spinlock.cpp.)
struct FbCons {
  uint *fb;         // frame buffer, 32 bits per pixel
  int stride;       // pixels per scan line
  int cols, rows;   // screen size in characters
  int cx, cy;       // cursor position, in characters
  int charw, charh; // character cell size in pixels: the font size
```

Inside member functions it's just `fb` instead of `cons.fb`. Scrolling:

[`kernel/fbcons.cpp:82–92`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-04/kernel/fbcons.cpp#L82-L92) (tag `step-04`)

```cpp
  // move every line up by one, and clear the bottom line.
  void
  scroll()
  {
    auto dst = reinterpret_cast<uint64 *>(fb);
    auto src = reinterpret_cast<uint64 *>(fb + charh * stride);
    uint64 n = (uint64)(rows - 1) * charh * stride / 2;
    for (uint64 i = 0; i < n; i++)
      dst[i] = src[i];
    fillrect(0, (rows - 1) * charh, cols * charw, charh, BG);
  }
```

The C version's `#define BIGSCREEN 2560`, `FG` and `BG` became `constexpr`. Which font each platform gets is noted in `[platform: ...]` comments:

[`kernel/fbcons.cpp:24–31`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-04/kernel/fbcons.cpp#L24-L31) (tag `step-04`)

```cpp
// the big font on screens at least this wide.
// [platform: VirtualBox] vbox.sh sets 2560x1440, so VirtualBox gets
// the 32x64 font; QEMU's 1280x800 gets 16x32. [platform: real PC]
// depends on the monitor: 4K screens get the big font.
constexpr uint64 BIGSCREEN = 2560;

constexpr uint FG = 0x00D0D0D0; // light gray; the same in RGB and BGR pixel formats
constexpr uint BG = 0x00000000;
```

### 2.2 `console.cpp`: sending to the screen too

`consputc()` sends to **the screen before** the serial port (so the screen still shows when the serial socket is blocked). `consoleinit()` also calls `fbconsinit()`:

[`kernel/console.cpp:26–41`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-04/kernel/console.cpp#L26-L41) (tag `step-04`)

```cpp
consputc(int c)
{
  if (c == BACKSPACE) {
    // if the user typed backspace, overwrite with a space.
    // the screen first: a serial line may be slow, or blocked.
    fbconsputc('\b');
    fbconsputc(' ');
    fbconsputc('\b');
    uartputc_sync('\b');
    uartputc_sync(' ');
    uartputc_sync('\b');
  } else {
    fbconsputc(c);
    uartputc_sync(c);
  }
}
```

## 3. After

QEMU (1280 × 800, 16×32 font):

![step-04 in QEMU](/assets/image/xv6-tut-step-04-step04-qemu.png)

VirtualBox (2560 × 1440, 32×64 font):

![step-04 in VirtualBox](/assets/image/xv6-tut-step-04-step04-vbox.png)

- the serial output is the same as `step-03`; the same text is now on the screen too
- **the boot messages are visible on a real PC as well.** The first photo from the barebone on 2026-10-07 ([step-06](/xv6/tutorial/step-06/)) shows this screen console

<div class="check" markdown="1">
**Check against the code**

- pair each `FbCons` member function with the `static` function of the C version it came from
- what changes without `namespace {`? Compare symbol names with `nm kernel/kernel | grep cons`
- set `BIGSCREEN` to 1024 and open QEMU in a window: the big font. Window command: `qemu-system-x86_64 -machine q35 -m 512M -serial stdio -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd -drive if=pflash,format=raw,file=ovmf_vars.fd -drive format=raw,file=usb.img`
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-03/">step-03</a></span><span><a href="/xv6/tutorial/step-05/">step-05</a> →</span></div>
