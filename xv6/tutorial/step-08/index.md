---
layout: default
title: "step-08 : USB 장치 알아보기"
permalink: /xv6/tutorial/step-08/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
</style>

# `step-08` : USB 장치 알아보기

| | |
|---|---|
| **앞 태그** | `step-07` |
| **이 태그** | `step-08` (`fb572a1`) |
| **한 줄** | 리셋된 포트의 장치에게 slot 과 주소를 주고, 제어 전송으로 디스크립터를 읽어 무슨 장치인지 찍는다 (`usb.cpp` 새 파일). 키보드는 남겨 두고 나머지는 놓아 준다 |
| **비교할 것** | xHCI 1.2 의 4.3 (장치 설정), 4.6.5 (Address Device), 6.2 (컨텍스트). USB 2.0 명세 9장 (요청, 디스크립터) |

```sh
git diff --stat step-07 step-08 -- . ':!docs' ':!*.pdf'
git checkout step-08 && make clean && make qemu USB=1
```

## 1. 이전 상태 (`step-07`)

포트에 장치가 꽂혀 있다는 것과 속도까지만 알았다 (`xhci0: port 5: a USB 2 device, high speed`). 그 장치와 말을 하지는 못했다.

## 2. 바꾼 것

| 파일 | | 더한 줄 | 지운 줄 |
|---|---|---:|---:|
| `Makefile` | 바뀜 | 1 | 0 |
| `kernel/kbd.cpp` | 바뀜 | 1 | 1 |
| `kernel/main.cpp` | 바뀜 | 1 | 1 |
| `kernel/usb.cpp` | 새 파일 | 145 | 0 |
| `kernel/xhci.cpp` | 바뀜 | 166 | 13 |
| `kernel/xhci.h` | 바뀜 | 56 | 2 |
| **합계** (6 파일) | | **370** | **17** |

### 2.1 순서

<svg viewBox="0 0 1000 520" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="장치 설정 순서"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">새 장치를 알아보기까지 (usbattach) : 명령은 컨트롤러에게, 요청은 장치에게</text><rect x="20" y="45" width="180" height="32" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="110.0" y="65.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">usb.cpp / xhci.cpp</text><line x1="110" y1="77" x2="110" y2="465" stroke="#d5dbdb" stroke-width="2" stroke-dasharray="4 4"/><rect x="390" y="45" width="180" height="32" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="480.0" y="65.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">xHCI 컨트롤러</text><line x1="480" y1="77" x2="480" y2="465" stroke="#d5dbdb" stroke-width="2" stroke-dasharray="4 4"/><rect x="730" y="45" width="180" height="32" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="820.0" y="65.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">USB 장치</text><line x1="820" y1="77" x2="820" y2="465" stroke="#d5dbdb" stroke-width="2" stroke-dasharray="4 4"/><line x1="110" y1="105" x2="476" y2="105" stroke="#1e8449" stroke-width="2" marker-end="url(#ae)"/><text x="295.0" y="99.0" font-size="11" fill="#4d5656" text-anchor="middle">Enable Slot 명령</text><line x1="480" y1="121" x2="114" y2="121" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ae)"/><text x="295.0" y="135.0" font-size="10.5" fill="#566573" text-anchor="middle">→ slot 번호</text><line x1="110" y1="165" x2="476" y2="165" stroke="#1e8449" stroke-width="2" marker-end="url(#ae)"/><text x="295.0" y="159.0" font-size="11" fill="#4d5656" text-anchor="middle">Address Device 명령 (입력 컨텍스트)</text><line x1="480" y1="205" x2="816" y2="205" stroke="#7d3c98" stroke-width="2" marker-end="url(#ae)"/><text x="650.0" y="199.0" font-size="11" fill="#4d5656" text-anchor="middle">SET_ADDRESS (컨트롤러가 직접)</text><line x1="110" y1="245" x2="816" y2="245" stroke="#b7950b" stroke-width="2" marker-end="url(#ae)"/><text x="465.0" y="239.0" font-size="11" fill="#4d5656" text-anchor="middle">GET_DESCRIPTOR 장치 8바이트</text><line x1="820" y1="261" x2="114" y2="261" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ae)"/><text x="465.0" y="275.0" font-size="10.5" fill="#566573" text-anchor="middle">→ 엔드포인트 0 크기</text><line x1="110" y1="305" x2="476" y2="305" stroke="#1e8449" stroke-width="2" marker-end="url(#ae)"/><text x="295.0" y="299.0" font-size="11" fill="#4d5656" text-anchor="middle">(필요하면) Evaluate Context</text><line x1="110" y1="345" x2="816" y2="345" stroke="#b7950b" stroke-width="2" marker-end="url(#ae)"/><text x="465.0" y="339.0" font-size="11" fill="#4d5656" text-anchor="middle">GET_DESCRIPTOR 장치 18바이트</text><line x1="820" y1="361" x2="114" y2="361" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ae)"/><text x="465.0" y="375.0" font-size="10.5" fill="#566573" text-anchor="middle">→ vendor, product, class</text><line x1="110" y1="405" x2="816" y2="405" stroke="#b7950b" stroke-width="2" marker-end="url(#ae)"/><text x="465.0" y="399.0" font-size="11" fill="#4d5656" text-anchor="middle">GET_DESCRIPTOR 설정 9바이트 → 전체</text><line x1="820" y1="421" x2="114" y2="421" stroke="#7f8c8d" stroke-width="2" stroke-dasharray="5 4" marker-end="url(#ae)"/><text x="465.0" y="435.0" font-size="10.5" fill="#566573" text-anchor="middle">→ 인터페이스, 엔드포인트</text><rect x="20" y="470" width="960" height="40" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="494.0" font-size="10.5" fill="#4d5656" text-anchor="middle">초록 = xHCI 명령 (명령 링),  노랑 = USB 제어 전송 (장치의 엔드포인트 0 링),  보라 = 컨트롤러가 스스로 보내는 것</text></svg>

`usbattach()` 의 앞부분이 이 순서 그대로다 :

[`kernel/usb.cpp:75–87`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-08/kernel/usb.cpp#L75-L87) (태그 `step-08`)

```cpp
usbattach(Xhci &hc, int speed, int rootport, uint32 route, int depth,
          int ttslot, int ttport, UsbDev **out)
{
  UsbDev *d = hc.newdev(speed, rootport, route, depth, ttslot, ttport);
  if (d == nullptr)
    return;
  if (!hc.addressdevice(*d)) {
    hc.freedev(d);
    return;
  }
  microdelay(10 * 1000); // at least 2 ms after SET_ADDRESS (USB 2.0 9.2.6.3)

  // the device descriptor's first 8 bytes hold endpoint 0's packet
```

### 2.2 slot 과 컨텍스트 (`xhci.cpp`)

`struct UsbDev` 가 장치 하나 : slot 번호, 속도, 위치 (루트 포트, route string, TT), 엔드포인트 0 의 링, 입력·장치 컨텍스트 페이지, 버퍼.

[`kernel/xhci.cpp:606–619`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-08/kernel/xhci.cpp#L606-L619) (태그 `step-08`)

```cpp
Xhci::addressdevice(UsbDev &d)
{
  memset(d.inctx, 0, PGSIZE);
  ictx(d, 0)[1] = (1 << 0) | (1 << 1); // add the slot and endpoint 0
  uint32 *s = ictx(d, 1);
  s[0] = d.route | (d.speed << 20) | (1 << 27); // 1 context entry
  s[1] = d.rootport << 16;
  s[2] = d.ttslot | (d.ttport << 8);
  ep0ctx(ictx(d, 2), d);
  int cc = command((uint64)d.inctx, 0, (TRB_ADDRESS_DEVICE << 10) | (d.slot << 24));
  if (cc != CC_SUCCESS)
    printk("usb: address device failed (%d)\n", cc);
  return cc == CC_SUCCESS;
}
```

입력 컨텍스트의 0번 항목은 "무엇을 더하나" (slot 과 엔드포인트 0), 1번은 slot 컨텍스트 (route, 속도, 루트 포트), 2번은 엔드포인트 0 (종류 Control, 최대 패킷 크기, 링 주소).
명령이 성공하면 컨트롤러가 장치에 `SET_ADDRESS` 를 직접 보낸다.

### 2.3 제어 전송

<svg viewBox="0 0 1000 240" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="제어 전송"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">제어 전송 = TRB 세 개 (엔드포인트 0 의 링)</text><rect x="20" y="60" width="300" height="100" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="170.0" y="90.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Setup TRB</text><text x="170.0" y="106.0" font-size="10.5" fill="#4d5656" text-anchor="middle">8바이트 요청을 TRB 안에 (IDT)</text><text x="170.0" y="122.0" font-size="10.5" fill="#4d5656" text-anchor="middle">bmRequestType, bRequest,</text><text x="170.0" y="138.0" font-size="10.5" fill="#4d5656" text-anchor="middle">wValue, wIndex, wLength</text><rect x="350" y="60" width="300" height="100" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="500.0" y="90.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Data TRB (있으면)</text><text x="500.0" y="106.0" font-size="10.5" fill="#4d5656" text-anchor="middle">버퍼 주소 d.buf, 길이</text><text x="500.0" y="122.0" font-size="10.5" fill="#4d5656" text-anchor="middle">방향 IN (장치 → 호스트)</text><text x="500.0" y="138.0" font-size="10.5" fill="#4d5656" text-anchor="middle">또는 OUT</text><rect x="680" y="60" width="300" height="100" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="830.0" y="90.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Status TRB</text><text x="830.0" y="106.0" font-size="10.5" fill="#4d5656" text-anchor="middle">데이터와 반대 방향</text><text x="830.0" y="122.0" font-size="10.5" fill="#4d5656" text-anchor="middle">IOC : 끝나면 전송 이벤트</text><text x="830.0" y="138.0" font-size="10.5" fill="#4d5656" text-anchor="middle">→ ctldone = true</text><line x1="320" y1="110" x2="348" y2="110" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="650" y1="110" x2="678" y2="110" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="180" width="960" height="45" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="206.5" font-size="10.5" fill="#4d5656" text-anchor="middle">db[slot] = 1 (엔드포인트 0 의 doorbell).  장치가 모르는 요청이면 STALL (완료 코드 6) → resetep() : Reset Endpoint + Set TR Dequeue</text></svg>

[`kernel/xhci.cpp:645–679`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-08/kernel/xhci.cpp#L645-L679) (태그 `step-08`)

```cpp
Xhci::control(UsbDev &d, uchar reqtype, uchar req, ushort value, ushort index,
              ushort len, void *data)
{
  constexpr uint32 IDT = 1 << 6, IOC = 1 << 5, DIR_IN = 1 << 16;
  bool in = reqtype & 0x80;
  if (len > PGSIZE)
    return false;

  uint64 setup = reqtype | (req << 8) | ((uint64)value << 16) |
                 ((uint64)index << 32) | ((uint64)len << 48);
  uint32 trt = len == 0 ? 0 : in ? 3 : 2; // transfer type: none, OUT, IN
  d.ep0.push(setup, 8, (TRB_SETUP << 10) | IDT | (trt << 16));
  if (len > 0) {
    if (!in)
      memmove(d.buf, data, len);
    d.ep0.push((uint64)d.buf, len, (TRB_DATA << 10) | (in ? DIR_IN : 0));
  }
  // the status stage goes the other way from the data.
  d.ep0.push(0, 0, (TRB_STATUS << 10) | IOC | (len > 0 && in ? 0 : DIR_IN));

  d.ctldone = false;
  db[d.slot] = 1; // endpoint 0's doorbell
  if (!wait([&] { return d.ctldone; }, 1000)) {
    printk("usb: request %x timed out\n", req);
    return false;
  }
  if (d.ctlcc != CC_SUCCESS) {
    // a STALL is the device saying "not supported".
    resetep(d, 1, d.ep0);
    return false;
  }
  if (in && len > 0)
    memmove(data, d.buf, len);
  return true;
}
```

### 2.4 디스크립터 읽기

<svg viewBox="0 0 1000 250" style="width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="장치 디스크립터"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker><marker id="as" viewBox="0 0 10 10" refX="1" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M10,0 L0,5 L10,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">장치 디스크립터 18바이트 (QEMU 의 USB 키보드, 실제로 읽은 값)</text><rect x="20" y="60" width="50" height="40" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="45.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">12</text><text x="45.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">0</text><text x="45.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">bLength</text><rect x="73" y="60" width="50" height="40" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="98.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">01</text><text x="98.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">1</text><text x="98.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">type</text><rect x="126" y="60" width="50" height="40" rx="2" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="151.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">00</text><text x="151.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">2</text><text x="177.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">bcdUSB</text><rect x="179" y="60" width="50" height="40" rx="2" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="204.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">02</text><text x="204.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">3</text><rect x="232" y="60" width="50" height="40" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="257.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">00</text><text x="257.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">4</text><text x="257.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">class</text><rect x="285" y="60" width="50" height="40" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="310.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">00</text><text x="310.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">5</text><text x="310.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">sub</text><rect x="338" y="60" width="50" height="40" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="363.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">00</text><text x="363.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">6</text><text x="363.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">proto</text><rect x="391" y="60" width="50" height="40" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="416.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">40</text><text x="416.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">7</text><text x="416.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">mps0</text><rect x="444" y="60" width="50" height="40" rx="2" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="469.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">27</text><text x="469.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">8</text><text x="495.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">idVendor</text><rect x="497" y="60" width="50" height="40" rx="2" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="522.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">06</text><text x="522.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">9</text><rect x="550" y="60" width="50" height="40" rx="2" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="575.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">01</text><text x="575.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">10</text><text x="601.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">idProduct</text><rect x="603" y="60" width="50" height="40" rx="2" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="628.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">00</text><text x="628.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">11</text><rect x="656" y="60" width="50" height="40" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="681.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">00</text><text x="681.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">12</text><text x="707.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">release</text><rect x="709" y="60" width="50" height="40" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="734.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">00</text><text x="734.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">13</text><rect x="762" y="60" width="50" height="40" rx="2" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="787.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">01</text><text x="787.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">14</text><text x="787.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">iManu</text><rect x="815" y="60" width="50" height="40" rx="2" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="840.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">04</text><text x="840.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">15</text><text x="840.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">iProd</text><rect x="868" y="60" width="50" height="40" rx="2" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="893.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">0b</text><text x="893.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">16</text><text x="893.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">iSerial</text><rect x="921" y="60" width="50" height="40" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="946.0" y="84.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">01</text><text x="946.0" y="54.0" font-size="9.5" fill="#4d5656" text-anchor="middle" font-family="ui-monospace,Menlo,Consolas,monospace">17</text><text x="946.0" y="118.0" font-size="10" fill="#4d5656" text-anchor="middle">nConf</text><rect x="20" y="140" width="960" height="90" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="173.0" font-size="10.5" fill="#4d5656" text-anchor="middle">bcdUSB 0x0200 = USB 2.0,  mps0 0x40 = 엔드포인트 0 최대 64바이트,  vendor 0x0627 / product 0x0001 (리틀 엔디언 : 27 06 → 0x0627)</text><text x="500.0" y="189.0" font-size="10.5" fill="#4d5656" text-anchor="middle">class 0 = 인터페이스마다 따로 정함 → 설정 디스크립터의 인터페이스에서 class 3 (HID), subclass 1 (boot), protocol 1 (키보드) 를 찾는다</text><text x="500.0" y="205.0" font-size="10.5" fill="#4d5656" text-anchor="middle">실제 PC 의 키보드 : id 4d9:a0f8 (Holtek 칩), full speed</text></svg>

설정 디스크립터 뒤에 인터페이스 (9바이트) 와 엔드포인트 (7바이트) 디스크립터가 이어진다. 각 디스크립터의 첫 바이트가 길이라서 `i += c[i]` 로 다음으로 건너뛴다 :

[`kernel/usb.cpp:48–68`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-08/kernel/usb.cpp#L48-L68) (태그 `step-08`)

```cpp
findkbd(uchar *c, int len)
{
  KbdInfo k;
  bool inkbd = false;
  for (int i = 0; i + 2 <= len && c[i] >= 2; i += c[i]) {
    if (c[i + 1] == DESC_INTERFACE && i + 9 <= len) {
      // class 3 (HID), subclass 1 (boot), protocol 1 (keyboard).
      inkbd = k.iface < 0 && c[i + 5] == 3 && c[i + 6] == 1 && c[i + 7] == 1;
      if (inkbd)
        k.iface = c[i + 2];
    } else if (c[i + 1] == DESC_ENDPOINT && i + 7 <= len && inkbd && k.ep < 0) {
      // an interrupt (attributes 3) IN (address bit 7) endpoint.
      if ((c[i + 2] & 0x80) && (c[i + 3] & 3) == 3) {
        k.ep = c[i + 2] & 0xF;
        k.mps = (c[i + 4] | (c[i + 5] << 8)) & 0x7FF;
        k.interval = c[i + 6];
      }
    }
  }
  return k;
}
```

이 단계에서는 허브를 `a hub: ignored (hubs come in step 10)`, 키보드를 `a keyboard (typing comes in step 9)` 로 찍기만 한다.
키보드가 아닌 장치는 `freedev()` (Disable Slot) 로 놓아 준다. 그 slot 은 다음 장치가 다시 받는다.

## 3. 바뀐 뒤

![step-08 QEMU : 장치 셋을 알아봄](/assets/image/xv6-tut-step-08-step08-qemu.png)

```
usb: port 5: high speed, id 627:1, class 0, not a keyboard: ignored
usb: port 6: full speed, id 409:55aa, class 9, a hub: ignored (hubs come in step 10)
usb: port 7: high speed, id 627:1, class 0, a keyboard (typing comes in step 9)
```

(QEMU 의 `usb-tablet` 과 `usb-kbd` 는 둘 다 `627:1` 이다. 설정 디스크립터의 인터페이스가 달라서 키보드인지 안다.)

<div class="check" markdown="1">
**코드와 대조해 볼 것**

- 장치 디스크립터 18바이트를 찍어서 위 그림과 비교
- 문자열 디스크립터 (type 3, 번호는 `dd[15]`) 를 읽어 제품 이름 `QEMU USB Keyboard` 찍기 (영어 튜토리얼 step08 연습 2)
- 모르는 vendor 요청 (`0xC0, 0x42`) 을 보내면 STALL (완료 코드 6). `resetep()` 를 빼면 다음 요청이 `timed out`
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-07/">step-07</a></span><span><a href="/xv6/tutorial/step-09/">step-09</a> →</span></div>
