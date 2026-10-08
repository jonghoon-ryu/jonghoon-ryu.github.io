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

<p class="subtitle">`printk()` 와 `panic()`</p>

| | |
|---|---|
| **앞 태그** | `step-02` |
| **이 태그** | `step-03` (커밋 `63c1be0`) |
| **한 줄** | 형식 있는 출력 `printk("%d %x %p %s")` 와 `panic()`, 그 아래의 `consputc()` (출력 쪽 `console.c`) 를 옮겼다 |
| **비교할 C 코드** | `git show v0.2-x86_64-c:kernel/printk.c`, `git show v0.2-x86_64-c:kernel/console.c` |

```sh
git diff --stat step-02 step-03 -- . ':!docs' ':!*.pdf'
git checkout step-03 && make clean && make qemu
```

## 1. 이전 상태 (`step-02`)

시리얼에 문자열을 그대로 보낼 수만 있었다. 숫자를 찍으려면 직접 글자로 바꿔야 했다.

## 2. 바꾼 것

<!-- fig:map_step_03 -->
<svg viewBox="0 0 1000 220" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="step-02 에서 step-03 로 바뀐 파일"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">변경 지도 : step-02 → step-03  (파일마다 더한 줄 / 지운 줄, 막대 길이는 √줄 수)</text><text x="300.0" y="50.0" font-size="11" font-weight="700" fill="#c0392b" text-anchor="end">지운 줄 ←</text><text x="320.0" y="50.0" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="start">파일</text><text x="620.0" y="50.0" font-size="11" font-weight="700" fill="#1e8449" text-anchor="start">→ 더한 줄</text><rect x="305" y="63" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="75.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/printk.cpp</text><text x="570.0" y="75.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="64" width="236.0" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="856.0" y="75.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+133</text><rect x="305" y="85" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="97.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/console.cpp</text><text x="570.0" y="97.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="86" width="135.24884199827375" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="755.2" y="97.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+42</text><rect x="305" y="107" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="119.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/main.cpp</text><text x="570.0" y="119.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="229.1694121028357" y="108" width="65.83058789716429" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="224.2" y="119.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−9</text><rect x="615" y="108" width="141.26359673431637" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="761.3" y="119.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+46</text><rect x="305" y="129" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="141.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/defs.h</text><text x="570.0" y="141.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="615" y="130" width="69.0669771673144" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="689.1" y="141.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+10</text><rect x="305" y="151" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="163.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">Makefile</text><text x="570.0" y="163.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="615" y="152" width="34.204409616308425" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="654.2" y="163.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+2</text><text x="500.0" y="196.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">합계 5 파일, +233 −9 줄 (docs, PDF 제외)</text></svg>
<!-- /fig:map_step_03 -->

| 파일 | | 더한 줄 | 지운 줄 |
|---|---|---:|---:|
| `Makefile` | 바뀜 | 2 | 0 |
| `kernel/console.cpp` | 새 파일 | 42 | 0 |
| `kernel/defs.h` | 바뀜 | 10 | 0 |
| `kernel/main.cpp` | 바뀜 | 46 | 9 |
| `kernel/printk.cpp` | 새 파일 | 133 | 0 |
| **합계** (5 파일) | | **233** | **9** |

<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="출력의 층"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">출력의 층 : step-03 에서 printk → consputc → uartputc_sync</text><rect x="20" y="60" width="230" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="135.0" y="88.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">printk(fmt, ...)</text><text x="135.0" y="104.0" font-size="11.0" fill="#4d5656" text-anchor="middle">%d %u %x %p %s %c</text><text x="135.0" y="120.0" font-size="11.0" fill="#4d5656" text-anchor="middle">%ld %lu %lx</text><rect x="290" y="60" width="200" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="390.0" y="88.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">consputc(c)</text><text x="390.0" y="104.0" font-size="11.0" fill="#4d5656" text-anchor="middle">console.cpp</text><text x="390.0" y="120.0" font-size="11.0" fill="#4d5656" text-anchor="middle">BACKSPACE 처리</text><rect x="530" y="60" width="200" height="80" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="630.0" y="96.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">uartputc_sync(c)</text><text x="630.0" y="112.0" font-size="11.0" fill="#4d5656" text-anchor="middle">uart.cpp (step-02)</text><rect x="770" y="60" width="210" height="80" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="875.0" y="88.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">COM1</text><text x="875.0" y="104.0" font-size="11.0" fill="#4d5656" text-anchor="middle">QEMU 터미널</text><text x="875.0" y="120.0" font-size="11.0" fill="#4d5656" text-anchor="middle">vbox/serial.log</text><line x1="250" y1="100" x2="288" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="490" y1="100" x2="528" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="730" y1="100" x2="768" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="290" y="170" width="440" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2" stroke-dasharray="6 4"/><text x="510.0" y="199.0" font-size="10.5" fill="#4d5656" text-anchor="middle">step-04 에서 여기에 fbconsputc() (화면) 가 더해진다</text><line x1="510" y1="140" x2="510" y2="168" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ae)"/><rect x="20" y="240" width="960" height="45" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="266.5" font-size="10.5" fill="#4d5656" text-anchor="middle">panic(s) : &quot;panic: &quot; + s 를 찍고 멈춘다. panicking 이 켜지면 다른 곳 (나중의 화면 콘솔) 이 잠금을 잡지 않는다</text></svg>

### 2.1 `printk.cpp`

<!-- fig:printkflow -->
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="printk 흐름"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">printk(fmt, …) : 형식 문자열을 한 글자씩</text><rect x="20" y="60" width="200" height="50" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="120.0" y="89.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">fmt[i]</text><rect x="280" y="30" width="260" height="44" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="410.0" y="48.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">&#x27;%&#x27; 가 아니면</text><text x="410.0" y="64.0" font-size="10.5" fill="#4d5656" text-anchor="middle">consputc(c)</text><rect x="280" y="95" width="260" height="44" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="410.0" y="121.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">&#x27;%&#x27; 이면 뒤의 c0 c1 c2 를 본다</text><line x1="220" y1="75" x2="278" y2="52" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="220" y1="95" x2="278" y2="117" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="600" y="30" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="47.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">d</text><text x="720.0" y="47.0" font-size="11" fill="#4d5656" text-anchor="start">printint(int, 10, 부호)</text><rect x="600" y="59" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="76.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">ld / lld</text><text x="720.0" y="76.0" font-size="11" fill="#4d5656" text-anchor="start">printint(uint64, 10, 부호)</text><rect x="600" y="88" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="105.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">u / lu / llu</text><text x="720.0" y="105.0" font-size="11" fill="#4d5656" text-anchor="start">printint(…, 10, 부호 없음)</text><rect x="600" y="117" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="134.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">x / lx / llx</text><text x="720.0" y="134.0" font-size="11" fill="#4d5656" text-anchor="start">printint(…, 16)</text><rect x="600" y="146" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="163.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">p</text><text x="720.0" y="163.0" font-size="11" fill="#4d5656" text-anchor="start">printptr : 0x + 16 자리</text><rect x="600" y="175" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="192.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">s</text><text x="720.0" y="192.0" font-size="11" fill="#4d5656" text-anchor="start">문자열 (nullptr 면 &quot;(null)&quot;)</text><rect x="600" y="204" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="221.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">c</text><text x="720.0" y="221.0" font-size="11" fill="#4d5656" text-anchor="start">글자 하나</text><rect x="600" y="233" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="250.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">%</text><text x="720.0" y="250.0" font-size="11" fill="#4d5656" text-anchor="start">&#x27;%&#x27;</text><rect x="600" y="262" width="110" height="26" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="655.0" y="279.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">그 밖</text><text x="720.0" y="279.0" font-size="11" fill="#4d5656" text-anchor="start">&#x27;%&#x27; 와 그 글자를 그대로 (눈에 띄게)</text><line x1="540" y1="117" x2="598" y2="117" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="300.0" y="200.0" font-size="11.5" fill="#4d5656" text-anchor="middle">va_arg(ap, 타입) 로 다음 인자를 꺼낸다 (&lt;stdarg.h&gt; : 컴파일러가 주는 헤더)</text><text x="300.0" y="225.0" font-size="11.5" fill="#4d5656" text-anchor="middle">%ld 처럼 두 글자면 i 를 더 넘긴다 (i += 1, %lld 는 i += 2)</text></svg>
<!-- /fig:printkflow -->

<!-- fig:printint -->
<svg viewBox="0 0 1000 250" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="printint"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">printint(255, 16, 0) : 아래 자리부터 버퍼에 쌓고 거꾸로 출력</text><rect x="30" y="55" width="140" height="40" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="100.0" y="79.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">x = 255</text><rect x="200" y="55" width="260" height="40" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="330.0" y="79.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">255 % 16 = 15 → &#x27;f&#x27;</text><rect x="490" y="55" width="140" height="40" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="560.0" y="79.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">x = 15</text><line x1="170" y1="75" x2="198" y2="75" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="460" y1="75" x2="488" y2="75" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="30" y="107" width="140" height="40" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="100.0" y="131.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">x = 15</text><rect x="200" y="107" width="260" height="40" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="330.0" y="131.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">15 % 16 = 15 → &#x27;f&#x27;</text><rect x="490" y="107" width="140" height="40" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="560.0" y="131.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">x = 0</text><line x1="170" y1="127" x2="198" y2="127" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="460" y1="127" x2="488" y2="127" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="800.0" y="60.0" font-size="12" font-weight="700" fill="#4d5656" text-anchor="middle">buf</text><rect x="740" y="70" width="46" height="46" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="763.0" y="100.0" font-size="18" font-weight="700" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">f</text><text x="763.0" y="132.0" font-size="10" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">buf[0]</text><rect x="790" y="70" width="46" height="46" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="813.0" y="100.0" font-size="18" font-weight="700" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">f</text><text x="813.0" y="132.0" font-size="10" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">buf[1]</text><text x="800.0" y="165.0" font-size="11.5" fill="#4d5656" text-anchor="middle">→ buf[1], buf[0] 순서로 consputc</text><text x="500.0" y="215.0" font-size="11.5" fill="#4d5656" text-anchor="middle">음수 (%d) 는 부호를 떼고 계산한 뒤 &#x27;-&#x27; 를 마지막에 쌓아서 맨 앞에 나오게 한다.  digits[] = &quot;0123456789abcdef&quot; (constexpr)</text></svg>
<!-- /fig:printint -->

C 판 `printk.c` 와 거의 같다. 숫자를 진법에 맞게 글자로 바꾸는 `printint()` :

[`kernel/printk.cpp:20–47`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-03/kernel/printk.cpp#L20-L47) (태그 `step-03`)

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

`printk()` 본체는 형식 문자열을 한 글자씩 보며 `%` 뒤의 글자로 갈래를 탄다 (`%d`, `%ld`, `%lld`, `%u`, `%x`, `%p`, `%s`, `%c`, `%%`).
`<stdarg.h>` 는 C 라이브러리가 아니라 **컴파일러가 주는 헤더** 라서 freestanding 커널에서도 쓸 수 있다.

C 판과 다른 점 : C 판은 여러 CPU 의 출력이 섞이지 않게 `pr.lock` 을 잡는다. 아직 CPU 하나, 잠금 코드도 없어서 뺐다 (`spinlock.cpp` 와 함께 돌아온다).

`panic()` :

[`kernel/printk.cpp:125–133`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-03/kernel/printk.cpp#L125-L133) (태그 `step-03`)

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

선언에 `[[noreturn]]` 을 붙였다 (C++11). 돌아오지 않는 함수라는 것을 컴파일러가 알아서, 그 뒤 코드에 대한 경고를 줄인다.

### 2.2 `format(printf)` 속성 : C 판에 없는 검사

<svg viewBox="0 0 1000 220" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="format 검사"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">format(printf) 속성 : g++ 가 printk 의 인자 타입을 검사한다 (C 판에는 없는 검사)</text><rect x="20" y="55" width="470" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="255.0" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">선언 (defs.h)</text><text x="255.0" y="99.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">int printk(const char *, ...)</text><text x="255.0" y="115.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  __attribute__((format(printf, 1, 2)));</text><rect x="530" y="55" width="450" height="80" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="755.0" y="83.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">처음 빌드에서 걸린 것 (main.cpp)</text><text x="755.0" y="99.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">&#x27;%p&#x27; expects &#x27;void*&#x27;, but … &#x27;long long unsigned int&#x27;</text><text x="755.0" y="115.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">&#x27;%ld&#x27; expects &#x27;long int&#x27;, but … &#x27;long long unsigned int&#x27;</text><line x1="490" y1="95" x2="528" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="500.0" y="170.0" font-size="11.5" fill="#4d5656" text-anchor="middle">bootinfo 의 필드는 로더 (clang) 와 커널 (g++) 이 함께 쓰려고 모두 unsigned long long → (void *), (uint64) 로 바꿔 찍는다</text><text x="500.0" y="195.0" font-size="11.5" fill="#4d5656" text-anchor="middle">x86-64 에서는 크기가 같아 결과는 같지만, 타입이 틀린 것을 컴파일 때 잡아 준다</text></svg>

[`kernel/defs.h:10–14`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-03/kernel/defs.h#L10-L14) (태그 `step-03`)

```cpp
// printk.cpp
// format(printf): g++ checks each call's arguments against the
// format string, as it does for printf. the C version has no check.
int printk(const char *, ...) __attribute__((format(printf, 1, 2)));
[[noreturn]] void panic(const char *);
```

### 2.3 `console.cpp` (출력 쪽만)

`consputc()` 와 `consoleinit()` 만 가져왔다. 입력 쪽 (`consoleintr`, `consoleread`) 과 `consolewrite` 는 인터럽트와 프로세스가 있어야 하므로 나중에 :

[`kernel/console.cpp:16–39`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-03/kernel/console.cpp#L16-L39) (태그 `step-03`)

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

### 2.4 `main.cpp` : 부팅 정보 찍기

이제 숫자를 찍을 수 있으므로, `main()` 이 로더가 넘겨준 것 (화면, ACPI, fs.img, UEFI 메모리 맵의 종류별 합) 을 출력한다 :

[`kernel/main.cpp:32–54`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-03/kernel/main.cpp#L32-L54) (태그 `step-03`)

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

## 3. 바뀐 뒤

QEMU 시리얼 (`make qemu`) :

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

화면은 아직 `step-01` 의 남색 그림이다. `printk()` 는 시리얼로만 나간다 (화면은 다음 단계).

- `free: 118232 pages (461 MB)` : QEMU 의 512MB 중 펌웨어가 안 쓰는 RAM. 나중에 `kalloc.cpp` (Step 12) 가 이것을 나눠 준다
- `reserved: 12544 MB` 는 VM 의 RAM (512MB) 보다 훨씬 크다 : 메모리 맵의 "reserved" 에는 RAM 이 아닌 주소 범위도 들어 있다. 커널은 `free` (type 7) 만 쓴다

<div class="check" markdown="1">
**코드와 대조해 볼 것**

- `main.cpp` 의 `printk("%p", (void *)bootinfo.fb_base)` 에서 `(void *)` 를 지우고 빌드 : 위 그림의 오류가 나온다
- `panic("test")` 를 `main()` 에 넣고 부팅 : `panic: test` 뒤에 멈춘다
- `git diff v0.2-x86_64-c:kernel/printk.c step-03:kernel/printk.cpp` : 빠진 잠금, 더한 `constexpr`
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-02/">step-02</a></span><span><a href="/xv6/tutorial/step-04/">step-04</a> →</span></div>
