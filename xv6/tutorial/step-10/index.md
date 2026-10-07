---
layout: default
title: "step-10 : USB 허브, 실제 PC"
permalink: /xv6/tutorial/step-10/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# `step-10` : USB 허브, 실제 PC

| | |
|---|---|
| **앞 태그** | `step-09` |
| **이 태그** | `step-10` (`3645541`) |
| **한 줄** | 허브와 그 뒤의 장치 (route string, Transaction Translator), Intel 7/8/9 시리즈의 소켓 연결. **2026.10.7 실제 PC 에서 입력을 확인한 코드** |
| **비교할 것** | USB 2.0 명세 11장 (허브 : 11.14 TT, 11.23.2.1 허브 디스크립터, 11.24.2 허브 요청). xHCI 1.2 의 6.2.2 (slot 컨텍스트), 8.9 (route string) |

```sh
git diff --stat step-09 step-10 -- . ':!docs' ':!*.pdf'
git checkout step-10 && make clean && make qemu USB=1      # 이제 키보드가 허브 뒤에
```

## 1. 이전 상태 (`step-09`)

루트 포트에 바로 꽂힌 키보드는 입력된다. 허브는 `a hub: ignored` 로 무시했다. PC 안에는 허브 칩이 흔하다 (베어본에도 둘).

## 2. 바꾼 것

| 파일 | | 더한 줄 | 지운 줄 |
|---|---|---:|---:|
| `Makefile` | 바뀜 | 3 | 3 |
| `kernel/main.cpp` | 바뀜 | 1 | 1 |
| `kernel/usb.cpp` | 바뀜 | 80 | 2 |
| `kernel/xhci.cpp` | 바뀜 | 38 | 1 |
| `kernel/xhci.h` | 바뀜 | 1 | 0 |
| **합계** (5 파일) | | **123** | **7** |

### 2.1 허브 설정

<svg viewBox="0 0 1000 220" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="허브 설정"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">허브 설정 (usbattach 의 class 9 갈래 → hub())</text><rect x="15" y="60" width="180" height="80" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="105.0" y="96.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">SET_CONFIGURATION</text><text x="105.0" y="112.0" font-size="10.5" fill="#4d5656" text-anchor="middle">허브 켜기</text><rect x="213" y="60" width="180" height="80" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="303.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">허브 디스크립터</text><text x="303.0" y="104.0" font-size="10.5" fill="#4d5656" text-anchor="middle">포트 수, TT 시간,</text><text x="303.0" y="120.0" font-size="10.5" fill="#4d5656" text-anchor="middle">전원 안정 시간</text><line x1="195" y1="100" x2="212" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="411" y="60" width="180" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="501.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">sethub()</text><text x="501.0" y="104.0" font-size="10.5" fill="#4d5656" text-anchor="middle">Configure Endpoint</text><text x="501.0" y="120.0" font-size="10.5" fill="#4d5656" text-anchor="middle">Hub = 1, 포트 수</text><line x1="393" y1="100" x2="410" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="609" y="60" width="180" height="80" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="699.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">포트마다 전원</text><text x="699.0" y="104.0" font-size="10.5" fill="#4d5656" text-anchor="middle">SET_FEATURE</text><text x="699.0" y="120.0" font-size="10.5" fill="#4d5656" text-anchor="middle">PORT_POWER</text><line x1="591" y1="100" x2="608" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="807" y="60" width="180" height="80" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="897.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">포트마다</text><text x="897.0" y="104.0" font-size="10.5" fill="#4d5656" text-anchor="middle">GET_STATUS → 리셋</text><text x="897.0" y="120.0" font-size="10.5" fill="#4d5656" text-anchor="middle">→ 속도 → usbattach()</text><line x1="789" y1="100" x2="806" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="15" y="160" width="970" height="45" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="186.5" font-size="10.5" fill="#4d5656" text-anchor="middle">usbattach() 가 hub() 를, hub() 가 다시 usbattach() 를 부른다 (재귀). 허브 뒤의 허브도 같은 길. 깊이는 최대 5</text></svg>

[`kernel/usb.cpp:186–201`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-10/kernel/usb.cpp#L186-L201) (태그 `step-10`)

```cpp
    if (cls == 9) {
      printk(", a hub\n");
      if (depth >= MAXDEPTH ||
          !hc.control(*d, 0x00, SET_CONFIGURATION, config, 0, 0, nullptr))
        goto fail;
      uchar hd[9];
      if (!hc.control(*d, 0xA0, GET_DESCRIPTOR, DESC_HUB << 8, 0, 9, hd))
        goto fail;
      int nports = hd[2];
      int ttt = (hd[3] >> 5) & 3; // TT think time
      if (!hc.sethub(*d, nports, ttt))
        goto fail;
      *out = d;
      hub(*d, nports, hd[5]);
      return;
    }
```

`sethub()` 이 없으면 컨트롤러가 허브 뒤의 장치로 가는 길을 내지 않는다 :

[`kernel/xhci.cpp:723–737`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-10/kernel/xhci.cpp#L723-L737) (태그 `step-10`)

```cpp
Xhci::sethub(UsbDev &d, int nports, int ttt)
{
  memset(d.inctx, 0, PGSIZE);
  ictx(d, 0)[1] = 1 << 0; // just the slot context
  uint32 *s = ictx(d, 1);
  memmove(s, octx(d, 0), csz);
  s[0] |= 1 << 26; // Hub
  s[1] = (s[1] & 0x00FFFFFF) | (nports << 24);
  s[2] = (s[2] & ~(3u << 16)) | (ttt << 16);
  s[3] = 0;
  int cc = command((uint64)d.inctx, 0, (TRB_CONFIGURE_EP << 10) | (d.slot << 24));
  if (cc != CC_SUCCESS) // xHCI before 0.96 wants Evaluate Context instead
    cc = command((uint64)d.inctx, 0, (TRB_EVALUATE_CONTEXT << 10) | (d.slot << 24));
  return cc == CC_SUCCESS;
}
```

### 2.2 허브의 포트마다

[`kernel/usb.cpp:237–275`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-10/kernel/usb.cpp#L237-L275) (태그 `step-10`)

```cpp
hub(UsbDev &d, int nports, int pwrgood)
{
  Xhci &hc = *d.hc;
  for (int p = 1; p <= nports; p++)
    hc.control(d, 0x23, SET_FEATURE, PORT_POWER, p, 0, nullptr);
  microdelay((pwrgood * 2 + 100) * 1000); // power on, then let devices connect

  for (int p = 1; p <= nports && p <= 15; p++) {
    uint32 st;
    if (!hubportstatus(d, p, &st) || (st & 1) == 0) // bit 0: connected
      continue;
    hc.control(d, 0x23, CLEAR_FEATURE, C_PORT_CONNECTION, p, 0, nullptr);
    hc.control(d, 0x23, SET_FEATURE, PORT_RESET, p, 0, nullptr);
    bool done = false;
    for (int i = 0; i < 50 && !done; i++) {
      microdelay(10 * 1000);
      done = hubportstatus(d, p, &st) && (st & (1 << (16 + 4))); // reset changed
    }
    if (!done || (st & 2) == 0) { // bit 1: enabled
      printk("usb: hub port %d does not enable\n", p);
      continue;
    }
    hc.control(d, 0x23, CLEAR_FEATURE, C_PORT_RESET, p, 0, nullptr);
    microdelay(10 * 1000); // reset recovery

    int speed = (st & (1 << 9)) ? SPEED_LOW : (st & (1 << 10)) ? SPEED_HIGH : SPEED_FULL;
    // a low or full speed device behind a high speed hub talks
    // through the hub's Transaction Translator; behind a full
    // speed hub, through whatever translator that hub uses.
    int ttslot = d.ttslot, ttport = d.ttport;
    if (d.speed == SPEED_HIGH && speed != SPEED_HIGH) {
      ttslot = d.slot;
      ttport = p;
    }
    UsbDev *child = nullptr;
    usbattach(hc, speed, d.rootport, d.route | (p << (4 * d.depth)), d.depth + 1,
              ttslot, ttport, &child);
  }
}
```

자식 장치의 위치 : 같은 루트 포트, route string 에 4비트 (이 허브의 포트 번호) 를 더하고, 깊이 +1.
low/full speed 장치가 **high speed 허브** 뒤에 있으면 그 허브의 TT (Transaction Translator : 480 Mb/s ↔ 12, 1.5 Mb/s 변환기) 를 거치므로 `ttslot`, `ttport` 를 채운다.

### 2.3 Intel 7/8/9 시리즈 `[platform: real PC]`

[`kernel/xhci.cpp:761–772`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-10/kernel/xhci.cpp#L761-L772) (태그 `step-10`)

```cpp
intelroute(int bus, int dev, int func)
{
  uint32 ids = pciread(bus, dev, func, 0x00);
  uint32 vendor = ids & 0xFFFF, device = ids >> 16;
  if (vendor != 0x8086)
    return;
  if (device != 0x1E31 && device != 0x8C31 && device != 0x9C31 &&
      device != 0x9CB1 && device != 0x8CB1)
    return;
  pciwrite(bus, dev, func, 0xD8, pciread(bus, dev, func, 0xDC)); // USB 3 sockets
  pciwrite(bus, dev, func, 0xD0, pciread(bus, dev, func, 0xD4)); // USB 2 sockets
}
```

그 칩셋들은 USB 소켓을 옛 EHCI 컨트롤러에 연결해 둘 수 있다. Linux 처럼 모두 xHCI 로 돌린다. 베어본 (700 시리즈) 에는 해당 없다.

## 3. 바뀐 뒤

QEMU (`make qemu USB=1` : 키보드가 허브 뒤, PS/2 를 끄고 친 화면) :

![step-10 QEMU : 허브 뒤의 키보드로 입력](/assets/image/xv6-tut-step-10-step10-qemu.png)

### 실제 PC (베어본), 2026.10.7

![실제 PC : USB 키보드로 Hi, claude / It looks like it works!](/assets/image/xv6-tut-step-10-step10-realpc.jpg)

<svg viewBox="0 0 1000 470" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="실제 PC 의 USB 나무"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">실제 PC (베어본) 의 USB 나무 : 2026.10.7 의 화면에서</text><rect x="380" y="45" width="240" height="50" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="500.0" y="66.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">xHCI 8086:7a60</text><text x="500.0" y="82.0" font-size="10.5" fill="#4d5656" text-anchor="middle">25 포트, PCI 0:20.0</text><path d="M500,95 L500,120 L80,120 L80,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="15" y="152" width="130" height="70" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="80.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">포트 2</text><text x="80.0" y="191.0" font-size="10.0" fill="#4d5656" text-anchor="middle">db0:76</text><text x="80.0" y="207.0" font-size="10.0" fill="#4d5656" text-anchor="middle">MSI 내장 : 무시</text><path d="M500,95 L500,120 L220,120 L220,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="155" y="152" width="130" height="70" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="220.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">포트 3</text><text x="220.0" y="191.0" font-size="10.0" fill="#4d5656" text-anchor="middle">5e3:610</text><text x="220.0" y="207.0" font-size="10.0" fill="#4d5656" text-anchor="middle">허브 (high)</text><path d="M500,95 L500,120 L360,120 L360,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="295" y="152" width="130" height="70" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="360.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">포트 5</text><text x="360.0" y="191.0" font-size="10.0" fill="#4d5656" text-anchor="middle">46d:c092</text><text x="360.0" y="207.0" font-size="10.0" fill="#4d5656" text-anchor="middle">마우스 : 무시</text><path d="M500,95 L500,120 L500,120 L500,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="435" y="152" width="130" height="70" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="500.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">포트 6</text><text x="500.0" y="191.0" font-size="10.0" fill="#4d5656" text-anchor="middle">4d9:a0f8</text><text x="500.0" y="207.0" font-size="10.0" fill="#4d5656" text-anchor="middle">키보드 ← 입력</text><path d="M500,95 L500,120 L640,120 L640,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="575" y="152" width="130" height="70" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="640.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">포트 7</text><text x="640.0" y="191.0" font-size="10.0" fill="#4d5656" text-anchor="middle">480:900</text><text x="640.0" y="207.0" font-size="10.0" fill="#4d5656" text-anchor="middle">저장 장치 : 무시</text><path d="M500,95 L500,120 L780,120 L780,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="715" y="152" width="130" height="70" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="780.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">포트 8</text><text x="780.0" y="191.0" font-size="10.0" fill="#4d5656" text-anchor="middle">4e8:4001</text><text x="780.0" y="207.0" font-size="10.0" fill="#4d5656" text-anchor="middle">저장 장치 : 무시</text><path d="M500,95 L500,120 L920,120 L920,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="855" y="152" width="130" height="70" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="920.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">포트 11</text><text x="920.0" y="191.0" font-size="10.0" fill="#4d5656" text-anchor="middle">5e3:608</text><text x="920.0" y="207.0" font-size="10.0" fill="#4d5656" text-anchor="middle">허브 (high)</text><path d="M975,222 L975,262 L905,262 L905,288" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="830" y="290" width="150" height="70" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="905.0" y="313.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">포트 11.1</text><text x="905.0" y="329.0" font-size="10.0" fill="#4d5656" text-anchor="middle">bda:8178</text><text x="905.0" y="345.0" font-size="10.0" fill="#4d5656" text-anchor="middle">Wi-Fi : 무시</text><text x="905.0" y="380.0" font-size="10.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">route = 1, depth 1</text><rect x="15" y="290" width="780" height="160" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="405.0" y="334.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">허브 뒤의 장치를 컨트롤러에게 알리는 법 (slot 컨텍스트)</text><text x="405.0" y="350.0" font-size="10.5" fill="#4d5656" text-anchor="middle">root port : 맨 처음 컨트롤러 포트 (11)</text><text x="405.0" y="366.0" font-size="10.5" fill="#4d5656" text-anchor="middle">route string : 허브마다 4비트씩 허브의 포트 번호 (11.1 → 0x1, 5.3.2 → 0x23)</text><text x="405.0" y="382.0" font-size="10.5" fill="#4d5656" text-anchor="middle">TT : low/full speed 장치가 high speed 허브 뒤에 있으면 그 허브의 slot, port</text><text x="405.0" y="398.0" font-size="10.5" fill="#4d5656" text-anchor="middle">     (허브 안의 Transaction Translator 가 480 ↔ 12 / 1.5 Mb/s 를 바꿔 준다)</text><text x="405.0" y="414.0" font-size="10.5" fill="#4d5656" text-anchor="middle">키보드는 루트 포트 6 에 바로 있어서 허브도 TT 도 필요 없었다</text></svg>

| 시험 | 결과 |
|---|---|
| 1차 (Step 10 코드, `porthandled` 없이) | 컨트롤러 시작 ✅, 장치 읽기 ✅, MSI 장치를 끝없이 반복 ✗ → [step-07](/xv6/tutorial/step-07/) 2.4 |
| 2차 (이 태그의 코드) | ✅ **입력됨**. 허브 둘, 허브 뒤 장치 하나 |

**Step 6–10 끝.** xv6 가 실제 PC 에서 키보드 입력을 받는다. 다음은 원래 계획으로 돌아가 Step 11 (`spinlock.cpp`).

<div class="check" markdown="1">
**코드와 대조해 볼 것**

- `Makefile` 의 `USB=1` 에 허브를 하나 더 끼워 `port 5.3.2` 만들기 : route `0x23`
- `usbattach()` 맨 앞에서 `rootport, route, depth, ttslot, ttport` 찍기 (QEMU 의 허브는 full speed 라 TT 는 0)
- (실제 PC, 선택) 키보드를 앞면 소켓에 꽂아 `port 3.N` 이 나오면 TT 경로 확인
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-09/">step-09</a></span><span><a href="/xv6/tutorial/">튜토리얼 목록</a> →</span></div>
