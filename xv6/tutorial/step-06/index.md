---
layout: default
title: step-06
permalink: /xv6/tutorial/step-06/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-06

<p class="subtitle">PCI 버스와 예외 화면</p>

| | |
|---|---|
| **앞 태그** | `step-05` |
| **이 태그** | `step-06` (커밋 `f184476`) |
| **한 줄** | USB 키보드 드라이버 (Step 6–10) 의 첫 단계. PCI 버스를 읽고 (`pci.cpp`), CPU 예외를 화면에 찍는 임시 IDT (`earlytrap.cpp`) 를 넣었다 |
| **비교할 C 코드** | 없다. C 판에 PCI, USB 가 없다. 명세와 비교 : [OSDev "PCI"](https://wiki.osdev.org/PCI), Intel SDM 3A 6장 |

```sh
git diff --stat step-05 step-06 -- . ':!docs' ':!*.pdf'
git checkout step-06 && make clean && make qemu USB=1     # USB=1 : QEMU 에 xHCI 를 더한다
```

## 1. 이전 상태 (`step-05`) 와, 이 단계가 생긴 이유

`step-05` 는 QEMU, VirtualBox 에서 PS/2 키보드로 입력이 된다. 2026.10.7, 이것 (+ 진단 코드) 을 실제 PC (베어본) 에서 부팅해 보았다 :

![실제 PC : 커널은 돌지만 키보드가 안 된다](/assets/image/xv6-tut-step-06-step06-realpc-ps2.jpg)

- 커널은 돈다 : 흰 네모 8개 (부팅 단계), 깜빡이는 네모 (살아 있음), 화면 콘솔, 메모리 맵
- **키보드가 안 된다.** 이 PC 에는 PS/2 컨트롤러가 없다. 상태 포트가 `0x55` 로 읽혔다 (없는 포트는 보통 `0xFF`). 펌웨어의 "USB 키보드를 PS/2 로 흉내" 는 커널이 시작되면 멈춘다

**실제 PC 에서 안 되면 OS 라고 할 수 없으므로**, 원래 Step 6 (메모리) 로 가기 전에 USB 키보드 드라이버를 다섯 단계로 넣었다. 그 USB 컨트롤러는 PCI 버스에 있다.

## 2. 바꾼 것

<!-- fig:map_step_06 -->
<svg viewBox="0 0 1000 286" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="step-05 에서 step-06 로 바뀐 파일"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">변경 지도 : step-05 → step-06  (파일마다 더한 줄 / 지운 줄, 막대 길이는 √줄 수)</text><text x="300.0" y="50.0" font-size="11" font-weight="700" fill="#c0392b" text-anchor="end">지운 줄 ←</text><text x="320.0" y="50.0" font-size="11" font-weight="700" fill="#2c3e50" text-anchor="start">파일</text><text x="620.0" y="50.0" font-size="11" font-weight="700" fill="#1e8449" text-anchor="start">→ 더한 줄</text><rect x="305" y="63" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="75.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/earlytrap.cpp</text><text x="570.0" y="75.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="64" width="236.0" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="856.0" y="75.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+61</text><rect x="305" y="85" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="97.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/pci.cpp</text><text x="570.0" y="97.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="86" width="236.0" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="856.0" y="97.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+61</text><rect x="305" y="107" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="119.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/earlyvec.S</text><text x="570.0" y="119.0" font-size="10" fill="#7f8c8d" text-anchor="end">새 파일</text><rect x="615" y="108" width="187.53263717760433" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="807.5" y="119.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+38</text><rect x="305" y="129" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="141.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/main.cpp</text><text x="570.0" y="141.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="259.5515176154339" y="130" width="35.44848238456608" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="254.6" y="141.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−1</text><rect x="615" y="130" width="194.56229131222932" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="814.6" y="141.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+41</text><rect x="305" y="151" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="163.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/x86.h</text><text x="570.0" y="163.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="615" y="152" width="120.05348184650688" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="740.1" y="163.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+15</text><rect x="305" y="173" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="185.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">Makefile</text><text x="570.0" y="185.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="615" y="174" width="103.66956671499614" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="723.7" y="185.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+11</text><rect x="305" y="195" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="207.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/kbd.cpp</text><text x="570.0" y="207.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="237.99373230413448" y="196" width="57.006267695865525" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="233.0" y="207.0" font-size="10" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−3</text><rect x="615" y="196" width="89.29288635911705" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="709.3" y="207.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+8</text><rect x="305" y="217" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="229.0" font-size="11" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/defs.h</text><text x="570.0" y="229.0" font-size="10" fill="#7f8c8d" text-anchor="end">바뀜</text><rect x="615" y="218" width="89.29288635911705" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="709.3" y="229.0" font-size="10" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+8</text><text x="500.0" y="262.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">합계 8 파일, +243 −4 줄 (docs, PDF 제외)</text></svg>
<!-- /fig:map_step_06 -->

| 파일 | | 더한 줄 | 지운 줄 |
|---|---|---:|---:|
| `Makefile` | 바뀜 | 11 | 0 |
| `kernel/defs.h` | 바뀜 | 8 | 0 |
| `kernel/earlytrap.cpp` | 새 파일 | 61 | 0 |
| `kernel/earlyvec.S` | 새 파일 | 38 | 0 |
| `kernel/kbd.cpp` | 바뀜 | 8 | 3 |
| `kernel/main.cpp` | 바뀜 | 41 | 1 |
| `kernel/pci.cpp` | 새 파일 | 61 | 0 |
| `kernel/x86.h` | 바뀜 | 15 | 0 |
| **합계** (8 파일) | | **243** | **4** |

### 2.1 `pci.cpp` : PCI 설정 공간

<!-- fig:pcitree -->
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="PCI 장치 나무"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">QEMU q35 의 PCI 버스 0 (step-06 의 목록, make qemu USB=1)</text><rect x="400" y="45" width="200" height="50" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="500.0" y="66.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">버스 0</text><text x="500.0" y="82.0" font-size="11.0" fill="#4d5656" text-anchor="middle">PCI 루트</text><path d="M500,95 L500,120 L110,120 L110,140" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="142" width="180" height="80" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="110.0" y="170.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">0:0.0</text><text x="110.0" y="186.0" font-size="11.0" fill="#4d5656" text-anchor="middle">8086:29c0</text><text x="110.0" y="202.0" font-size="11.0" fill="#4d5656" text-anchor="middle">host bridge</text><path d="M500,95 L500,120 L304,120 L304,140" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="214" y="142" width="180" height="80" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="304.0" y="170.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">0:1.0</text><text x="304.0" y="186.0" font-size="11.0" fill="#4d5656" text-anchor="middle">1234:1111</text><text x="304.0" y="202.0" font-size="11.0" fill="#4d5656" text-anchor="middle">VGA (화면)</text><path d="M500,95 L500,120 L498,120 L498,140" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="408" y="142" width="180" height="80" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="498.0" y="170.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">0:2.0</text><text x="498.0" y="186.0" font-size="11.0" fill="#4d5656" text-anchor="middle">8086:10d3</text><text x="498.0" y="202.0" font-size="11.0" fill="#4d5656" text-anchor="middle">Ethernet</text><path d="M500,95 L500,120 L692,120 L692,140" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="602" y="142" width="180" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="692.0" y="170.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">0:3.0</text><text x="692.0" y="186.0" font-size="11.0" fill="#4d5656" text-anchor="middle">1b36:000d</text><text x="692.0" y="202.0" font-size="11.0" fill="#4d5656" text-anchor="middle">xHCI (USB 3)</text><path d="M500,95 L500,120 L886,120 L886,140" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="796" y="142" width="180" height="80" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="886.0" y="170.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">0:31.2</text><text x="886.0" y="186.0" font-size="11.0" fill="#4d5656" text-anchor="middle">8086:2922</text><text x="886.0" y="202.0" font-size="11.0" fill="#4d5656" text-anchor="middle">SATA AHCI</text><text x="500.0" y="250.0" font-size="11.5" fill="#4d5656" text-anchor="middle">버스:장치.기능 (bus:device.function).  0:31.2 = 장치 31 의 기능 2 : 한 칩 (ICH9) 의 여러 기능</text><text x="500.0" y="274.0" font-size="11.5" fill="#7d3c98" text-anchor="middle">실제 PC 의 xHCI : 0:20.0, 8086:7a60 (Intel 700 시리즈)</text></svg>
<!-- /fig:pcitree -->

<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="PCI 설정 주소"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">PCI 설정 공간 읽기 : 포트 0xCF8 에 주소, 0xCFC 에서 값</text><rect x="100" y="70" width="60" height="44" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="130.0" y="96.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">enable</text><text x="130.0" y="62.0" font-size="10" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">31</text><rect x="160" y="70" width="70" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="195.0" y="96.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">0</text><text x="195.0" y="62.0" font-size="10" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">30–24</text><rect x="230" y="70" width="150" height="44" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="305.0" y="96.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">bus</text><text x="305.0" y="62.0" font-size="10" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">23–16</text><rect x="380" y="70" width="120" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="440.0" y="96.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">device</text><text x="440.0" y="62.0" font-size="10" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">15–11</text><rect x="500" y="70" width="90" height="44" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="545.0" y="96.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">func</text><text x="545.0" y="62.0" font-size="10" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">10–8</text><rect x="590" y="70" width="130" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="655.0" y="96.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">register</text><text x="655.0" y="62.0" font-size="10" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">7–2</text><rect x="720" y="70" width="50" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="745.0" y="96.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">00</text><text x="745.0" y="62.0" font-size="10" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">1–0</text><text x="60.0" y="97.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="end">0xCF8 ←</text><text x="500.0" y="140.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">pciaddr(bus, dev, func, off) = 0x80000000 | bus &lt;&lt; 16 | dev &lt;&lt; 11 | func &lt;&lt; 8 | (off &amp; 0xFC)</text><rect x="100" y="170" width="70" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="135.0" y="187.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0x00</text><rect x="170" y="170" width="240" height="26" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="290.0" y="187.0" font-size="10.0" fill="#4d5656" text-anchor="middle">vendor ID | device ID</text><text x="425.0" y="188.0" font-size="11" fill="#4d5656" text-anchor="start">없으면 0xFFFFFFFF</text><rect x="100" y="200" width="70" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="135.0" y="217.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0x04</text><rect x="170" y="200" width="240" height="26" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="290.0" y="217.0" font-size="10.0" fill="#4d5656" text-anchor="middle">command</text><text x="425.0" y="218.0" font-size="11" fill="#4d5656" text-anchor="start">비트 1 메모리, 비트 2 버스 마스터</text><rect x="100" y="230" width="70" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="135.0" y="247.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0x08</text><rect x="170" y="230" width="240" height="26" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="290.0" y="247.0" font-size="10.0" fill="#4d5656" text-anchor="middle">class code (31:8)</text><text x="425.0" y="248.0" font-size="11" fill="#4d5656" text-anchor="start">0x0C0330 = USB xHCI</text><rect x="100" y="260" width="70" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="135.0" y="277.0" font-size="10.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0x10</text><rect x="170" y="260" width="240" height="26" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="290.0" y="277.0" font-size="10.0" fill="#4d5656" text-anchor="middle">BAR0 (+ BAR1)</text><text x="425.0" y="278.0" font-size="11" fill="#4d5656" text-anchor="start">장치 레지스터의 주소</text><rect x="640" y="170" width="340" height="116" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="810.0" y="200.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">pciscan(cls, found)</text><text x="810.0" y="216.0" font-size="10.5" fill="#4d5656" text-anchor="middle">버스 256 × 장치 32 × 기능 8</text><text x="810.0" y="232.0" font-size="10.5" fill="#4d5656" text-anchor="middle">vendor 0xFFFF 면 건너뜀</text><text x="810.0" y="248.0" font-size="10.5" fill="#4d5656" text-anchor="middle">class 가 같으면 found() 호출</text><text x="810.0" y="264.0" font-size="10.5" fill="#4d5656" text-anchor="middle">(브리지를 따라가지 않는 단순한 방법)</text></svg>

[`kernel/pci.cpp:20–24`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-06/kernel/pci.cpp#L20-L24) (태그 `step-06`)

```cpp
static uint32
pciaddr(int bus, int dev, int func, int off)
{
  return 0x80000000u | (bus << 16) | (dev << 11) | (func << 8) | (off & 0xFC);
}
```

[`kernel/pci.cpp:44–61`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-06/kernel/pci.cpp#L44-L61) (태그 `step-06`)

```cpp
pciscan(uint32 cls, void (*found)(int bus, int dev, int func))
{
  for (int bus = 0; bus < 256; bus++) {
    for (int dev = 0; dev < 32; dev++) {
      // a missing device reads all ones.
      if ((pciread(bus, dev, 0, 0x00) & 0xFFFF) == 0xFFFF)
        continue;
      // header type bit 7: the device has functions 1-7 too.
      int nfunc = (pciread(bus, dev, 0, 0x0C) & 0x800000) ? 8 : 1;
      for (int func = 0; func < nfunc; func++) {
        if ((pciread(bus, dev, func, 0x00) & 0xFFFF) == 0xFFFF)
          continue;
        if ((pciread(bus, dev, func, 0x08) >> 8) == cls)
          found(bus, dev, func);
      }
    }
  }
}
```

`inl`, `outl` (32비트 포트 I/O) 은 `x86.h` 에 더했다. 이 단계에서만 `main.cpp` 의 `pcilist()` 가 몇 종류의 장치를 찍는다 (Linux 의 `lspci` 처럼).

### 2.2 `earlyvec.S`, `earlytrap.cpp` : 예외를 화면에

<!-- fig:gate -->
<svg viewBox="0 0 1000 230" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="IDT 게이트"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">IDT 항목 하나 (struct gatedesc, 16 바이트) : earlytrapinit() 이 32 개 채운다</text><rect x="60" y="60" width="125.71428571428572" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="122.9" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">rsvd (0)</text><text x="62.0" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">127</text><text x="183.7" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">96</text><rect x="185.71428571428572" y="60" width="167.61904761904762" height="44" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="269.5" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">off_63_32</text><text x="187.7" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">95</text><text x="351.3" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">64</text><rect x="353.33333333333337" y="60" width="125.71428571428572" height="44" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="416.2" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">off_31_16</text><text x="355.3" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">63</text><text x="477.0" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">48</text><rect x="479.0476190476191" y="60" width="125.71428571428572" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="541.9" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">type_attr 0x8E</text><text x="481.0" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">47</text><text x="602.8" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">40</text><rect x="604.7619047619048" y="60" width="83.80952380952381" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="646.7" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">ist (0)</text><text x="606.8" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">39</text><text x="686.6" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">32</text><rect x="688.5714285714287" y="60" width="125.71428571428572" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="751.4" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">cs (코드 셀렉터)</text><text x="690.6" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">31</text><text x="812.3" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">16</text><rect x="814.2857142857144" y="60" width="125.71428571428572" height="44" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="877.1" y="86.0" font-size="10.5" fill="#4d5656" text-anchor="middle">off_15_0</text><text x="816.3" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">15</text><text x="938.0" y="56.0" font-size="9" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><text x="500.0" y="140.0" font-size="11.5" fill="#4d5656" text-anchor="middle">off_* 세 조각 = 처리 코드 주소 (earlyvectors + 16 × n).  cs = 지금의 코드 세그먼트 (mov %cs)</text><text x="500.0" y="164.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0x8E = 1000 1110 : P (있음) = 1, DPL = 0 (커널만), 종류 0xE = 64비트 interrupt gate (들어가면 인터럽트 끔)</text><text x="500.0" y="188.0" font-size="11.5" fill="#4d5656" text-anchor="middle">lidt(idt, sizeof(idt)) 로 CPU 에 표의 주소와 크기를 알린다</text></svg>
<!-- /fig:gate -->

<svg viewBox="0 0 1000 330" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="예외 처리 스택"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU 예외가 나면 : earlyvec.S → earlytrap() 의 스택</text><rect x="20" y="60" width="240" height="90" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="140.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU 예외</text><text x="140.0" y="109.0" font-size="11.0" fill="#4d5656" text-anchor="middle">0 나누기, 잘못된 포인터 …</text><text x="140.0" y="125.0" font-size="11.0" fill="#4d5656" text-anchor="middle">IDT[n] 의 주소로 뛴다</text><rect x="300" y="60" width="240" height="90" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="420.0" y="85.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">earlyvec.S 의 진입점 n</text><text x="420.0" y="101.0" font-size="11.0" fill="#4d5656" text-anchor="middle">오류 코드 없으면 push 0</text><text x="420.0" y="117.0" font-size="11.0" fill="#4d5656" text-anchor="middle">push n</text><text x="420.0" y="133.0" font-size="11.0" fill="#4d5656" text-anchor="middle">jmp earlycommon</text><rect x="580" y="60" width="400" height="90" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="780.0" y="85.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">earlytrap(f)</text><text x="780.0" y="101.0" font-size="11.0" fill="#4d5656" text-anchor="middle">&quot;CPU exception 14 (page fault), error code 2&quot;</text><text x="780.0" y="117.0" font-size="11.0" fill="#4d5656" text-anchor="middle">&quot;rip 0x…, address 0x… (cr2)&quot;</text><text x="780.0" y="133.0" font-size="11.0" fill="#4d5656" text-anchor="middle">panic → 화면에 남는다</text><line x1="260" y1="105" x2="298" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="540" y1="105" x2="578" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="80" y="175" width="260" height="22" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="210.0" y="190.0" font-size="10.0" fill="#4d5656" text-anchor="middle">f[0] = 벡터 번호 n</text><rect x="80" y="197" width="260" height="22" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="210.0" y="212.0" font-size="10.0" fill="#4d5656" text-anchor="middle">f[1] = 오류 코드 (또는 0)</text><rect x="80" y="219" width="260" height="22" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="210.0" y="234.0" font-size="10.0" fill="#4d5656" text-anchor="middle">f[2] = rip</text><rect x="80" y="241" width="260" height="22" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="210.0" y="256.0" font-size="10.0" fill="#4d5656" text-anchor="middle">f[3] = cs</text><rect x="80" y="263" width="260" height="22" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="210.0" y="278.0" font-size="10.0" fill="#4d5656" text-anchor="middle">f[4] = rflags</text><rect x="80" y="285" width="260" height="22" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="210.0" y="300.0" font-size="10.0" fill="#4d5656" text-anchor="middle">f[5] = rsp, f[6] = ss</text><text x="345.0" y="190.0" font-size="10.5" fill="#4d5656" text-anchor="start">← rsp (= f)</text><rect x="480" y="175" width="500" height="132" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="730.0" y="205.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">왜 지금 필요한가</text><text x="730.0" y="221.0" font-size="10.5" fill="#4d5656" text-anchor="middle">커널에 IDT 가 없으면 펌웨어의 IDT 가 남아 있다</text><text x="730.0" y="237.0" font-size="10.5" fill="#4d5656" text-anchor="middle">QEMU : OVMF 가 레지스터를 찍고 멈춘다 (튜토리얼 연습 4)</text><text x="730.0" y="253.0" font-size="10.5" fill="#4d5656" text-anchor="middle">실제 PC : 그 펌웨어 코드는 이미 사라졌을 수 있다 → 조용히 재부팅</text><text x="730.0" y="269.0" font-size="10.5" fill="#4d5656" text-anchor="middle">USB 드라이버는 실제 PC 에서만 시험되는 부분이 많다 :</text><text x="730.0" y="285.0" font-size="10.5" fill="#4d5656" text-anchor="middle">무슨 일이 생기면 사진으로 볼 수 있어야 한다</text></svg>

`earlyvec.S` 는 어셈블러 매크로로 진입점 32개를 만든다. 오류 코드를 넣는 예외 (8, 10–14, 17, 21, 29, 30) 와 안 넣는 예외의 스택 모양을 맞추는 것이 핵심 :

[`kernel/earlyvec.S:12–31`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-06/kernel/earlyvec.S#L12-L31) (태그 `step-06`)

```asm
.macro vec n
        .align 16
        .if (\n == 8 || (\n >= 10 && \n <= 14) || \n == 17 || \n == 21 || \n == 29 || \n == 30)
        .else
        pushq $0
        .endif
        pushq $\n
        jmp earlycommon
.endm

.align 16
.global earlyvectors
earlyvectors:
.set i, 0
.rept 32
        vec %i
        .set i, i+1
.endr

earlycommon:
```

[`kernel/earlytrap.cpp:53–61`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-06/kernel/earlytrap.cpp#L53-L61) (태그 `step-06`)

```cpp
earlytrap(uint64 *f)
{
  printk("\nCPU exception %ld (%s), error code %lx\n", f[0], excname(f[0]), f[1]);
  printk("  rip %p", (void *)f[2]);
  if (f[0] == 14)
    printk(", address %p (cr2)", (void *)r_cr2());
  printk("\n");
  panic("early trap: please take a photo of this screen");
}
```

트랩 단계 (Step 16 의 `trap.cpp`) 가 이것을 대신한다.

### 2.3 `kbd.cpp` : 실제 PC 에서 배운 것

상태 포트가 `0xFF` 가 아닌 `0x55` 로 읽힐 수도 있다. 비트 0 ("글자 있음") 이 켜져 있어서 `while (kbdgetc() >= 0)` 가 끝나지 않을 수 있다. 한 번에 16바이트까지만 읽게 바꿨다 :

[`kernel/kbd.cpp:128–132`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-06/kernel/kbd.cpp#L128-L132) (태그 `step-06`)

```cpp
  // [platform: real PC] at most 16 bytes per call: with no
  // controller, the status port may read as "a byte is waiting"
  // forever, and this loop must not starve the other devices.
  // (the C version loops until kbdgetc() says no more.)
  for (int n = 0; n < 16 && (c = kbdgetc()) >= 0; n++) {
```

## 3. 바뀐 뒤

`make qemu USB=1` :

![step-06 QEMU : PCI 장치 목록](/assets/image/xv6-tut-step-06-step06-qemu.png)

실제 PC 의 xHCI 는 `0:20.0  vendor 8086 device 7a60` (Intel 700 시리즈 칩셋) 이다. 다음 단계가 이것을 깨운다.

<div class="check" markdown="1">
**코드와 대조해 볼 것**

- Linux 에서 `lspci -nn` : 같은 `[vendor:device]` 번호
- `main()` 에 `volatile int zero = 0; printk("%d", 1 / zero);` : 예외가 **안 난다**. `100 / zero` 는 난다. 왜? `1 / x` 는 1, −1, 0 중 하나라서 GCC 가 나눗셈 없이 비교로 계산한다 (`objdump -d kernel/main.o` 에 `lea 0x1(%rax)`, `cmp $0x2`, `cmovbe`). 0 으로 나누기는 정의되지 않은 동작이라 예외를 낼 의무가 없다
- `earlyvec.S` 의 `.if` 줄의 벡터 번호를 Intel SDM 3A 표 6-1 의 "Error Code" 열과 비교
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-05/">step-05</a></span><span><a href="/xv6/tutorial/step-07/">step-07</a> →</span></div>
