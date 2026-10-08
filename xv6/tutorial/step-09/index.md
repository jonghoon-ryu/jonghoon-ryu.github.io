---
layout: default
title: "step-09 : USB 키보드로 입력"
permalink: /xv6/tutorial/step-09/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# `step-09` : USB 키보드로 입력

| | |
|---|---|
| **앞 태그** | `step-08` |
| **이 태그** | `step-09` (커밋 `64d9588`) |
| **한 줄** | 키보드의 interrupt IN 엔드포인트를 설정하고, boot protocol 의 8바이트 리포트를 글자로 바꿔 `consoleintr()` 로 보낸다. **USB 키보드로 입력이 된다** |
| **비교할 것** | USB HID 1.11 의 7.2 (`SET_IDLE`, `SET_PROTOCOL`), 부록 B (boot 리포트). HID Usage Tables 10장 (키 번호) |

```sh
git diff --stat step-08 step-09 -- . ':!docs' ':!*.pdf'
git checkout step-09 && make clean && make qemu USB=1
# 그리고 Ctrl-a c (QEMU monitor) → sendkey h → sendkey i → Ctrl-a c
```

## 1. 이전 상태 (`step-08`)

키보드를 알아보고 `a keyboard (typing comes in step 9)` 까지 찍었다. 키를 받지는 않았다.

## 2. 바꾼 것

| 파일 | | 더한 줄 | 지운 줄 |
|---|---|---:|---:|
| `kernel/main.cpp` | 바뀜 | 3 | 3 |
| `kernel/usb.cpp` | 바뀜 | 132 | 4 |
| `kernel/xhci.cpp` | 바뀜 | 49 | 0 |
| `kernel/xhci.h` | 바뀜 | 14 | 0 |
| **합계** (4 파일) | | **198** | **7** |

### 2.1 키보드 설정 (`kbdsetup()`)

[`kernel/usb.cpp:95–118`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-09/kernel/usb.cpp#L95-L118) (태그 `step-09`)

```cpp
kbdsetup(UsbDev &d, const KbdInfo &k, int config)
{
  Xhci &hc = *d.hc;
  int dci = 2 * k.ep + 1; // device context index of an IN endpoint
  int mps = k.mps > 64 ? 64 : k.mps;
  d.kbdiface = k.iface;
  d.kbddci = dci;
  d.kbdmps = mps;
  if (!hc.configep(d, dci, 7, mps, xinterval(d.speed, k.interval))) // 7: interrupt IN
    return false;
  if (!hc.control(d, 0x00, SET_CONFIGURATION, config, 0, 0, nullptr))
    return false;
  // boot protocol (0). keyboards start in it after a reset, but
  // the firmware may have switched this one to report protocol.
  if (!hc.control(d, 0x21, SET_PROTOCOL, 0, k.iface, 0, nullptr))
    printk("usb: keyboard refused SET_PROTOCOL\n");
  // report only when keys change. many keyboards refuse; harmless.
  hc.control(d, 0x21, SET_IDLE, 0, k.iface, 0, nullptr);
  d.report = d.buf + 2048; // control transfers use the first half
  memset(d.prev, 0, sizeof(d.prev));
  d.kbd = true;
  hc.queuein(d);
  return true;
}
```

| 순서 | 무엇 |
|---|---|
| `configep()` | Configure Endpoint 명령 : 키보드의 interrupt IN 엔드포인트와 그 링을 컨트롤러에 더한다 |
| `SET_CONFIGURATION` | 장치가 인터페이스를 켠다 |
| `SET_PROTOCOL(0)` | boot protocol : 고정된 8바이트 리포트 (펌웨어가 바꿔 놨을 수 있어서 다시) |
| `SET_IDLE(0)` | 키가 바뀔 때만 보내라 (많은 키보드가 거절해도 괜찮다) |
| `queuein()` | 첫 리포트를 요청 |

### 2.2 interrupt 엔드포인트

<svg viewBox="0 0 1000 250" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="interrupt 엔드포인트"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">interrupt 엔드포인트 : CPU 인터럽트가 아니라 &#x27;컨트롤러가 정해진 간격마다 묻는&#x27; 전송</text><text x="20.0" y="60.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">컨트롤러 ↔ 키보드</text><rect x="160" y="45" width="60" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="190.0" y="62.0" font-size="9.5" fill="#4d5656" text-anchor="middle">NAK</text><rect x="228" y="45" width="60" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="258.0" y="62.0" font-size="9.5" fill="#4d5656" text-anchor="middle">NAK</text><rect x="296" y="45" width="60" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="326.0" y="62.0" font-size="9.5" fill="#4d5656" text-anchor="middle">NAK</text><rect x="364" y="45" width="60" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="394.0" y="62.0" font-size="9.5" fill="#4d5656" text-anchor="middle">NAK</text><rect x="432" y="45" width="60" height="26" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="462.0" y="62.0" font-size="9.5" fill="#4d5656" text-anchor="middle">DATA</text><rect x="500" y="45" width="60" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="530.0" y="62.0" font-size="9.5" fill="#4d5656" text-anchor="middle">NAK</text><rect x="568" y="45" width="60" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="598.0" y="62.0" font-size="9.5" fill="#4d5656" text-anchor="middle">NAK</text><rect x="636" y="45" width="60" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="666.0" y="62.0" font-size="9.5" fill="#4d5656" text-anchor="middle">NAK</text><rect x="704" y="45" width="60" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="734.0" y="62.0" font-size="9.5" fill="#4d5656" text-anchor="middle">NAK</text><rect x="772" y="45" width="60" height="26" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="802.0" y="62.0" font-size="9.5" fill="#4d5656" text-anchor="middle">DATA</text><rect x="840" y="45" width="60" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="870.0" y="62.0" font-size="9.5" fill="#4d5656" text-anchor="middle">NAK</text><rect x="908" y="45" width="60" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="938.0" y="62.0" font-size="9.5" fill="#4d5656" text-anchor="middle">NAK</text><text x="160.0" y="92.0" font-size="10.5" fill="#4d5656" text-anchor="start">8 ms 마다 (QEMU 키보드 bInterval 7 → 2^6 × 125µs)</text><text x="20.0" y="140.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="start">CPU</text><line x1="462" y1="72" x2="462" y2="118" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ae)"/><rect x="402" y="120" width="120" height="40" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="462.0" y="136.0" font-size="9.0" fill="#4d5656" text-anchor="middle">전송 이벤트 →</text><text x="462.0" y="152.0" font-size="9.0" fill="#4d5656" text-anchor="middle">report, queuein()</text><line x1="802" y1="72" x2="802" y2="118" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ae)"/><rect x="742" y="120" width="120" height="40" rx="3" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="802.0" y="136.0" font-size="9.0" fill="#4d5656" text-anchor="middle">전송 이벤트 →</text><text x="802.0" y="152.0" font-size="9.0" fill="#4d5656" text-anchor="middle">report, queuein()</text><rect x="20" y="180" width="960" height="50" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="209.0" font-size="10.5" fill="#4d5656" text-anchor="middle">queuein() : Normal TRB 하나 (8바이트 버퍼) + doorbell. 키가 바뀔 때까지 CPU 는 아무것도 안 한다. 이벤트가 오면 처리하고 다시 queuein()</text></svg>

이름과 달리 CPU 인터럽트가 아니다. 간격은 엔드포인트의 `bInterval` 에서 오는데, 속도마다 단위가 다르다 :

[`kernel/usb.cpp:82–92`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-09/kernel/usb.cpp#L82-L92) (태그 `step-09`)

```cpp
xinterval(int speed, int binterval)
{
  if (speed == SPEED_HIGH || speed == SPEED_SUPER) {
    int n = binterval - 1;
    return n < 0 ? 0 : n > 15 ? 15 : n;
  }
  int n = 3; // 1 ms
  while (n < 10 && (1 << (n + 1)) <= binterval * 8)
    n++;
  return n;
}
```

[`kernel/xhci.cpp:724–729`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-09/kernel/xhci.cpp#L724-L729) (태그 `step-09`)

```cpp
Xhci::queuein(UsbDev &d)
{
  constexpr uint32 ISP = 1 << 2, IOC = 1 << 5;
  d.kbdring.push((uint64)d.report, d.kbdmps, (TRB_NORMAL << 10) | ISP | IOC);
  db[d.slot] = d.kbddci;
}
```

### 2.3 리포트 → 글자

<svg viewBox="0 0 1000 330" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="키보드 리포트"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">boot 키보드 리포트 8바이트 (QEMU 에서 실제로 받은 값)</text><rect x="250" y="50" width="70" height="30" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="285.0" y="69.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">수정 키</text><rect x="322" y="50" width="70" height="30" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="357.0" y="69.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">예약</text><rect x="394" y="50" width="70" height="30" rx="2" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="429.0" y="69.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">키 1</text><rect x="466" y="50" width="70" height="30" rx="2" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="501.0" y="69.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">키 2</text><rect x="538" y="50" width="70" height="30" rx="2" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="573.0" y="69.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">키 3</text><rect x="610" y="50" width="70" height="30" rx="2" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="645.0" y="69.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">키 4</text><rect x="682" y="50" width="70" height="30" rx="2" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="717.0" y="69.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">키 5</text><rect x="754" y="50" width="70" height="30" rx="2" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="789.0" y="69.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">키 6</text><text x="240.0" y="111.0" font-size="11.5" fill="#4d5656" text-anchor="end">a 누름</text><rect x="250" y="92" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="285.0" y="110.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="322" y="92" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="357.0" y="110.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="394" y="92" width="70" height="28" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="429.0" y="110.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">4</text><rect x="466" y="92" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="501.0" y="110.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="538" y="92" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="573.0" y="110.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="610" y="92" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="645.0" y="110.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="682" y="92" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="717.0" y="110.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="754" y="92" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="789.0" y="110.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><text x="840.0" y="111.0" font-size="11.5" fill="#1e8449" text-anchor="start">→ consoleintr(&#x27;a&#x27;)</text><text x="240.0" y="143.0" font-size="11.5" fill="#4d5656" text-anchor="end">a 뗌</text><rect x="250" y="124" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="285.0" y="142.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="322" y="124" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="357.0" y="142.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="394" y="124" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="429.0" y="142.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="466" y="124" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="501.0" y="142.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="538" y="124" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="573.0" y="142.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="610" y="124" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="645.0" y="142.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="682" y="124" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="717.0" y="142.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="754" y="124" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="789.0" y="142.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><text x="240.0" y="175.0" font-size="11.5" fill="#4d5656" text-anchor="end">Shift 누름</text><rect x="250" y="156" width="70" height="28" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="285.0" y="174.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">2</text><rect x="322" y="156" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="357.0" y="174.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="394" y="156" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="429.0" y="174.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="466" y="156" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="501.0" y="174.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="538" y="156" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="573.0" y="174.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="610" y="156" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="645.0" y="174.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="682" y="156" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="717.0" y="174.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="754" y="156" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="789.0" y="174.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><text x="240.0" y="207.0" font-size="11.5" fill="#4d5656" text-anchor="end">a 누름</text><rect x="250" y="188" width="70" height="28" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="285.0" y="206.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">2</text><rect x="322" y="188" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="357.0" y="206.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="394" y="188" width="70" height="28" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="429.0" y="206.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">4</text><rect x="466" y="188" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="501.0" y="206.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="538" y="188" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="573.0" y="206.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="610" y="188" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="645.0" y="206.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="682" y="188" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="717.0" y="206.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="754" y="188" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="789.0" y="206.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><text x="840.0" y="207.0" font-size="11.5" fill="#1e8449" text-anchor="start">→ consoleintr(&#x27;A&#x27;)</text><text x="240.0" y="239.0" font-size="11.5" fill="#4d5656" text-anchor="end">a 뗌</text><rect x="250" y="220" width="70" height="28" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="285.0" y="238.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">2</text><rect x="322" y="220" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="357.0" y="238.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="394" y="220" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="429.0" y="238.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="466" y="220" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="501.0" y="238.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="538" y="220" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="573.0" y="238.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="610" y="220" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="645.0" y="238.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="682" y="220" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="717.0" y="238.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="754" y="220" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="789.0" y="238.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><text x="240.0" y="271.0" font-size="11.5" fill="#4d5656" text-anchor="end">Shift 뗌</text><rect x="250" y="252" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="285.0" y="270.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="322" y="252" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="357.0" y="270.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="394" y="252" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="429.0" y="270.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="466" y="252" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="501.0" y="270.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="538" y="252" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="573.0" y="270.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="610" y="252" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="645.0" y="270.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="682" y="252" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="717.0" y="270.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><rect x="754" y="252" width="70" height="28" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="789.0" y="270.0" font-size="11.0" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace">0</text><text x="500.0" y="304.0" font-size="11.5" fill="#4d5656" text-anchor="middle">새 키 = 이번 리포트에 있고 지난 리포트 (prev) 에 없는 키.  수정 키 비트 : 1 왼쪽 Ctrl, 2 왼쪽 Shift, 0x10 오른쪽 Ctrl, 0x20 오른쪽 Shift</text></svg>

[`kernel/usb.cpp:251–273`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-09/kernel/usb.cpp#L251-L273) (태그 `step-09`)

```cpp
usbkbdreport(UsbDev &d, int len)
{
  uchar *r = d.report;
  if (len < 3 || r[2] == 1) // 1: too many keys down at once
    return;
  if (len > 8)
    len = 8;
  for (int i = 2; i < len; i++) {
    if (r[i] == 0)
      continue;
    bool old = false;
    for (int j = 2; j < 8; j++)
      if (d.prev[j] == r[i])
        old = true;
    if (!old) {
      int c = usbkey(r[i], r[0]);
      if (c != 0)
        consoleintr(c);
    }
  }
  memset(d.prev, 0, sizeof(d.prev));
  memmove(d.prev, r, len);
}
```

PS/2 (`kbd.cpp`) 는 키 하나가 눌리고 떼일 때마다 바이트가 오지만, USB 는 **지금 눌린 키 전부** 가 매번 온다. 새로 눌린 키는 지난 리포트와 비교해서 찾는다.
키 번호 (HID usage) → 글자는 `usbmap` (Shift 없음 / 있음 두 줄), Ctrl+글자는 `c & 0x1F` (Ctrl+U = 21 = `C('U')`).

## 3. 바뀐 뒤

QEMU (PS/2 를 끄고 USB 키보드로만 친 화면) :

![step-09 QEMU : USB 키보드로 입력](/assets/image/xv6-tut-step-09-step09-qemu.png)

- 실제 PC : 베어본의 키보드 (`4d9:a0f8`, full speed) 는 루트 포트 6 에 바로 있어서 **이 단계의 코드로 입력된다** (Step 10 코드로 확인)
- 아직 없는 것 : 키 반복 (꾹 누르면 한 번만, 타이머가 필요), Caps Lock 불, 허브 뒤의 키보드 (다음 단계)

<div class="check" markdown="1">
**코드와 대조해 볼 것**

- `usbkbdreport()` 맨 앞에서 리포트 바이트를 찍고 `sendkey a`, `sendkey shift-a` : 위 그림의 여섯 줄
- `kbdsetup()` 에서 `xinterval()` 결과 찍기 : QEMU 는 `bInterval 7 -> interval 6` (8 ms)
- `sendkey z 2000` (2초 누르기) : `z` 하나만
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-08/">step-08</a></span><span><a href="/xv6/tutorial/step-10/">step-10</a> →</span></div>
