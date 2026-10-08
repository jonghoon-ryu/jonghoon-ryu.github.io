---
layout: default
title: step-10
permalink: /xv6/tutorial/step-10/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-10

<p class="subtitle">USB hubs, and the real PC</p>

| | |
|---|---|
| **Previous tag** | `step-09` |
| **This tag** | `step-10` (commit `c9bbb18`) |
| **In one line** | hubs and the devices behind them (route string, Transaction Translator), and socket routing on Intel 7/8/9 series chipsets. **The code verified on the real PC on 2026-10-07** |
| **To compare with** | USB 2.0 chapter 11 (hubs: 11.14 TT, 11.23.2.1 hub descriptor, 11.24.2 hub requests). xHCI 1.2: 6.2.2 (slot context), 8.9 (route string) |

```sh
git diff --stat step-09 step-10 -- . ':!docs' ':!*.pdf'
git checkout step-10 && make clean && make qemu USB=1      # the keyboard is now behind a hub
```

## 1. Before (`step-09`)

A keyboard plugged straight into a root port types. Hubs were ignored (`a hub: ignored`). Hub chips are common inside PCs (the barebone has two).

## 2. What changed

<!-- fig:map_step_10 -->
<svg viewBox="0 0 1000 220" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="files changed from step-09 to step-10"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Change map: step-09 → step-10  (lines added / removed per file; bar length ∝ √lines)</text><text x="300.0" y="50.0" font-size="11.5" font-weight="700" fill="#c0392b" text-anchor="end">removed ←</text><text x="320.0" y="50.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="start">file</text><text x="620.0" y="50.0" font-size="11.5" font-weight="700" fill="#1e8449" text-anchor="start">→ added</text><rect x="305" y="63" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="75.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/usb.cpp</text><text x="570.0" y="75.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="252.63380690806363" y="64" width="42.36619309193636" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="247.6" y="75.0" font-size="11.5" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−2</text><rect x="615" y="64" width="236.0" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="856.0" y="75.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+80</text><rect x="305" y="85" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="97.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/xhci.cpp</text><text x="570.0" y="97.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="263.2852182587524" y="86" width="31.71478174124758" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="258.3" y="97.0" font-size="11.5" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−1</text><rect x="615" y="86" width="164.51656064903753" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="784.5" y="97.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+38</text><rect x="305" y="107" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="119.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">Makefile</text><text x="570.0" y="119.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="244.4606915186147" y="108" width="50.5393084813853" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="239.5" y="119.0" font-size="11.5" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−3</text><rect x="615" y="108" width="50.5393084813853" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="670.5" y="119.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+3</text><rect x="305" y="129" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="141.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/main.cpp</text><text x="570.0" y="141.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="263.2852182587524" y="130" width="31.71478174124758" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="258.3" y="141.0" font-size="11.5" fill="#c0392b" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−1</text><rect x="615" y="130" width="31.71478174124758" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="651.7" y="141.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+1</text><rect x="305" y="151" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="163.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/xhci.h</text><text x="570.0" y="163.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="152" width="31.71478174124758" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="651.7" y="163.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+1</text><text x="500.0" y="196.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Total: 5 files, +123 −7 lines (docs and PDFs not counted)</text></svg>
<!-- /fig:map_step_10 -->

| File | | Added | Removed |
|---|---|---:|---:|
| `Makefile` | changed | 3 | 3 |
| `kernel/main.cpp` | changed | 1 | 1 |
| `kernel/usb.cpp` | changed | 80 | 2 |
| `kernel/xhci.cpp` | changed | 38 | 1 |
| `kernel/xhci.h` | changed | 1 | 0 |
| **Total** (5 files) | | **123** | **7** |

### 2.1 Setting up a hub

<!-- fig:hubsetup -->
<svg viewBox="0 0 1000 220" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="hub setup"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Setting up a hub (usbattach&#x27;s class 9 branch → hub())</text><rect x="15" y="60" width="180" height="80" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="105.0" y="96.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">SET_CONFIGURATION</text><text x="105.0" y="112.0" font-size="11.5" fill="#4d5656" text-anchor="middle">turn the hub on</text><rect x="213" y="60" width="180" height="80" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="303.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">hub descriptor</text><text x="303.0" y="104.0" font-size="11.5" fill="#4d5656" text-anchor="middle">ports, TT think time,</text><text x="303.0" y="120.0" font-size="11.5" fill="#4d5656" text-anchor="middle">power-on time</text><line x1="195" y1="100" x2="212" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="411" y="60" width="180" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="501.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">sethub()</text><text x="501.0" y="104.0" font-size="11.5" fill="#4d5656" text-anchor="middle">Configure Endpoint</text><text x="501.0" y="120.0" font-size="11.5" fill="#4d5656" text-anchor="middle">Hub = 1, ports</text><line x1="393" y1="100" x2="410" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="609" y="60" width="180" height="80" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="699.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">power each port</text><text x="699.0" y="104.0" font-size="11.5" fill="#4d5656" text-anchor="middle">SET_FEATURE</text><text x="699.0" y="120.0" font-size="11.5" fill="#4d5656" text-anchor="middle">PORT_POWER</text><line x1="591" y1="100" x2="608" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="807" y="60" width="180" height="80" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="897.0" y="88.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">each port</text><text x="897.0" y="104.0" font-size="11.5" fill="#4d5656" text-anchor="middle">GET_STATUS → reset</text><text x="897.0" y="120.0" font-size="11.5" fill="#4d5656" text-anchor="middle">→ speed → usbattach()</text><line x1="789" y1="100" x2="806" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="15" y="160" width="970" height="45" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="500.0" y="186.5" font-size="11.5" fill="#4d5656" text-anchor="middle">usbattach() calls hub(), and hub() calls usbattach() again (recursion). Hubs behind hubs take the same path, up to 5 deep</text></svg>
<!-- /fig:hubsetup -->

[`kernel/usb.cpp:186–201`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-10/kernel/usb.cpp#L186-L201) (tag `step-10`)

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

Without `sethub()` the controller won't route to devices behind the hub:

[`kernel/xhci.cpp:723–737`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-10/kernel/xhci.cpp#L723-L737) (tag `step-10`)

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

### 2.2 Each port of the hub

<!-- fig:hubstatus -->
<svg viewBox="0 0 1000 230" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="hub port status"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Hub port status (GET_STATUS, 4 bytes = wPortChange : wPortStatus)</text><rect x="120" y="60" width="73.04347826086956" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="156.5" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="122.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">31</text><text x="191.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">21</text><rect x="193.04347826086956" y="60" width="73.04347826086956" height="44" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="229.6" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">C_RESET</text><text x="229.6" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">20</text><rect x="266.0869565217391" y="60" width="36.52173913043478" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="284.3" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="268.1" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">19</text><text x="300.6" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">17</text><rect x="302.6086956521739" y="60" width="73.04347826086956" height="44" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="339.1" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">C_CONN</text><text x="339.1" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">16</text><rect x="375.65217391304344" y="60" width="73.04347826086956" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="412.2" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="377.7" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">15</text><text x="446.7" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">11</text><rect x="448.695652173913" y="60" width="73.04347826086956" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="485.2" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">HS</text><text x="485.2" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">10</text><rect x="521.7391304347825" y="60" width="73.04347826086956" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="558.3" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">LS</text><text x="558.3" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">9</text><rect x="594.782608695652" y="60" width="73.04347826086956" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="631.3" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">power</text><text x="631.3" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">8</text><rect x="667.8260869565215" y="60" width="36.52173913043478" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="686.1" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="669.8" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">7</text><text x="702.3" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">5</text><rect x="704.3478260869563" y="60" width="73.04347826086956" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="740.9" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">reset</text><text x="740.9" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">4</text><rect x="777.3913043478258" y="60" width="36.52173913043478" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="795.7" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="779.4" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">3</text><text x="811.9" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">2</text><rect x="813.9130434782605" y="60" width="73.04347826086956" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="850.4" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">enable</text><text x="850.4" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">1</text><rect x="886.95652173913" y="60" width="73.04347826086956" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="923.5" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">conn</text><text x="923.5" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><text x="540.0" y="140.0" font-size="12" fill="#4d5656" text-anchor="middle">hub(): connected (bit 0) → SET_FEATURE(PORT_RESET) → wait for C_RESET (bit 20) → check enabled (bit 1)</text><text x="540.0" y="165.0" font-size="12" fill="#4d5656" text-anchor="middle">speed: bit 9 → low, bit 10 → high, neither → full. CLEAR_FEATURE clears the C_ bits (features 16 and 20)</text></svg>
<!-- /fig:hubstatus -->

[`kernel/usb.cpp:237–275`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-10/kernel/usb.cpp#L237-L275) (tag `step-10`)

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

<!-- fig:route -->
<svg viewBox="0 0 1000 250" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="route string"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">The route string (slot context dw0 bits 19:0): 4 bits per hub</text><text x="142.0" y="86.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="end">route</text><rect x="150" y="60" width="152.0" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="226.0" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">tier-5 hub port</text><text x="152.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">19</text><text x="300.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">16</text><rect x="302.0" y="60" width="152.0" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="378.0" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">tier 4</text><text x="304.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">15</text><text x="452.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">12</text><rect x="454.0" y="60" width="152.0" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="530.0" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">tier 3</text><text x="456.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">11</text><text x="604.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">8</text><rect x="606.0" y="60" width="152.0" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="682.0" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">tier 2: 2</text><text x="608.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">7</text><text x="756.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">4</text><rect x="758.0" y="60" width="152.0" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="834.0" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">tier 1: 3</text><text x="760.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">3</text><text x="908.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><text x="530.0" y="140.0" font-size="12" fill="#4d5656" text-anchor="middle">port 5.3.2 = root port 5 → port 3 of the first hub → port 2 of the second → route 0x23 (the root port is separate, in dw1)</text><text x="530.0" y="165.0" font-size="12" fill="#4d5656" text-anchor="middle">hub() gives each child: route | (p &lt;&lt; (4 × depth)), depth + 1. At most 5 hubs deep (MAXDEPTH)</text><text x="530.0" y="190.0" font-size="12" fill="#7d3c98" text-anchor="middle">the real PC&#x27;s Wi-Fi (port 11.1): root port 11, route 0x1</text></svg>
<!-- /fig:route -->

A child's location: the same root port, 4 more bits (this hub's port number) in the route string, depth + 1.
A low/full speed device behind a **high speed hub** goes through that hub's TT (Transaction Translator: 480 Mb/s ↔ 12 or 1.5 Mb/s), so `ttslot` and `ttport` are filled in.

<!-- fig:tt -->
<svg viewBox="0 0 1000 280" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="TT"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">The Transaction Translator: a speed converter inside high speed hubs</text><rect x="30" y="100" width="180" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="120.0" y="131.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">xHCI</text><text x="120.0" y="147.0" font-size="11.5" fill="#4d5656" text-anchor="middle">talks at 480 Mb/s</text><rect x="300" y="70" width="280" height="130" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="440.0" y="107.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">high speed hub</text><text x="440.0" y="123.0" font-size="11.5" fill="#4d5656" text-anchor="middle">one TT per port (or per hub)</text><text x="440.0" y="139.0" font-size="11.5" fill="#4d5656" text-anchor="middle"></text><text x="440.0" y="155.0" font-size="11.5" fill="#4d5656" text-anchor="middle">480 Mb/s ↔ 12 / 1.5 Mb/s</text><text x="440.0" y="171.0" font-size="11.5" fill="#4d5656" text-anchor="middle">split transactions</text><rect x="670" y="60" width="290" height="60" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="815.0" y="86.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">keyboard (full / low speed)</text><text x="815.0" y="102.0" font-size="11.5" fill="#4d5656" text-anchor="middle">ttslot = the hub&#x27;s slot, ttport = port</text><rect x="670" y="150" width="290" height="60" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="815.0" y="176.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Wi-Fi (high speed)</text><text x="815.0" y="192.0" font-size="11.5" fill="#4d5656" text-anchor="middle">no TT needed (ttslot = 0)</text><line x1="210" y1="135" x2="298" y2="135" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="254.0" y="129.0" font-size="11.5" fill="#566573" text-anchor="middle">480</text><line x1="580" y1="110" x2="668" y2="90" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="624.0" y="94.0" font-size="11.5" fill="#566573" text-anchor="middle">12 / 1.5</text><line x1="580" y1="160" x2="668" y2="180" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="624.0" y="164.0" font-size="11.5" fill="#566573" text-anchor="middle">480</text><text x="500.0" y="240.0" font-size="12" fill="#4d5656" text-anchor="middle">QEMU&#x27;s usb-hub is a full speed hub, so no TT is used → this path can only be tested on a real PC</text></svg>
<!-- /fig:tt -->

### 2.3 Intel 7/8/9 series `[platform: real PC]`

[`kernel/xhci.cpp:761–772`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-10/kernel/xhci.cpp#L761-L772) (tag `step-10`)

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

Those chipsets can connect USB sockets to an old EHCI controller instead, and the firmware may leave them there. Like Linux, xv6 routes every socket to the xHCI on those chips. Not relevant on the barebone (700 series).

## 3. After

QEMU (`make qemu USB=1`: the keyboard behind a hub, typed with PS/2 switched off):

![step-10 in QEMU: typing on a keyboard behind a hub](/assets/image/xv6-tut-step-10-step10-qemu.png)

### The real PC (barebone), 2026-10-07

![the real PC: "Hi, claude / It looks like it works!" typed on the USB keyboard](/assets/image/xv6-tut-step-10-step10-realpc.jpg)

<!-- fig:tree -->
<svg viewBox="0 0 1000 470" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif" role="img" aria-label="the real PC&#x27;s USB tree"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">The real PC&#x27;s (barebone&#x27;s) USB tree, from the 2026-10-07 screen</text><rect x="380" y="45" width="240" height="50" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="500.0" y="66.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">xHCI 8086:7a60</text><text x="500.0" y="82.0" font-size="11.5" fill="#4d5656" text-anchor="middle">25 ports, PCI 0:20.0</text><path d="M500,95 L500,120 L80,120 L80,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="15" y="152" width="130" height="70" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="80.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">port 2</text><text x="80.0" y="191.0" font-size="11.5" fill="#4d5656" text-anchor="middle">db0:76</text><text x="80.0" y="207.0" font-size="11.5" fill="#4d5656" text-anchor="middle">MSI: ignored</text><path d="M500,95 L500,120 L220,120 L220,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="155" y="152" width="130" height="70" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="220.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">port 3</text><text x="220.0" y="191.0" font-size="11.5" fill="#4d5656" text-anchor="middle">5e3:610</text><text x="220.0" y="207.0" font-size="11.5" fill="#4d5656" text-anchor="middle">hub (high)</text><path d="M500,95 L500,120 L360,120 L360,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="295" y="152" width="130" height="70" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="360.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">port 5</text><text x="360.0" y="191.0" font-size="11.5" fill="#4d5656" text-anchor="middle">46d:c092</text><text x="360.0" y="207.0" font-size="11.5" fill="#4d5656" text-anchor="middle">mouse: ignored</text><path d="M500,95 L500,120 L500,120 L500,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="435" y="152" width="130" height="70" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="500.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">port 6</text><text x="500.0" y="191.0" font-size="11.5" fill="#4d5656" text-anchor="middle">4d9:a0f8</text><text x="500.0" y="207.0" font-size="11.5" fill="#4d5656" text-anchor="middle">keyboard ← types</text><path d="M500,95 L500,120 L640,120 L640,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="575" y="152" width="130" height="70" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="640.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">port 7</text><text x="640.0" y="191.0" font-size="11.5" fill="#4d5656" text-anchor="middle">480:900</text><text x="640.0" y="207.0" font-size="11.5" fill="#4d5656" text-anchor="middle">storage: ignored</text><path d="M500,95 L500,120 L780,120 L780,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="715" y="152" width="130" height="70" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="780.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">port 8</text><text x="780.0" y="191.0" font-size="11.5" fill="#4d5656" text-anchor="middle">4e8:4001</text><text x="780.0" y="207.0" font-size="11.5" fill="#4d5656" text-anchor="middle">storage: ignored</text><path d="M500,95 L500,120 L920,120 L920,150" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="855" y="152" width="130" height="70" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="920.0" y="175.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">port 11</text><text x="920.0" y="191.0" font-size="11.5" fill="#4d5656" text-anchor="middle">5e3:608</text><text x="920.0" y="207.0" font-size="11.5" fill="#4d5656" text-anchor="middle">hub (high)</text><path d="M975,222 L975,262 L905,262 L905,288" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="830" y="290" width="150" height="70" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="905.0" y="313.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">port 11.1</text><text x="905.0" y="329.0" font-size="11.5" fill="#4d5656" text-anchor="middle">bda:8178</text><text x="905.0" y="345.0" font-size="11.5" fill="#4d5656" text-anchor="middle">Wi-Fi: ignored</text><text x="905.0" y="380.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">route = 1, depth 1</text><rect x="15" y="290" width="780" height="160" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="405.0" y="334.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Telling the controller where a device behind hubs is (slot context)</text><text x="405.0" y="350.0" font-size="11.5" fill="#4d5656" text-anchor="middle">root port: the first controller port on the way (11)</text><text x="405.0" y="366.0" font-size="11.5" fill="#4d5656" text-anchor="middle">route string: 4 bits per hub, that hub&#x27;s port number (11.1 → 0x1, 5.3.2 → 0x23)</text><text x="405.0" y="382.0" font-size="11.5" fill="#4d5656" text-anchor="middle">TT: for a low/full speed device behind a high speed hub, that hub&#x27;s slot and port</text><text x="405.0" y="398.0" font-size="11.5" fill="#4d5656" text-anchor="middle">     (the hub&#x27;s Transaction Translator converts 480 ↔ 12 / 1.5 Mb/s)</text><text x="405.0" y="414.0" font-size="11.5" fill="#4d5656" text-anchor="middle">the keyboard was on root port 6 directly: no hub, no TT needed</text></svg>
<!-- /fig:tree -->

| Test on the real PC | Result |
|---|---|
| 1st (Step 10's code without `porthandled`) | controller started ✅, devices read ✅, the MSI device set up over and over ✗ → [step-07](/xv6/tutorial/step-07/) 2.4 |
| 2nd (this tag's code) | ✅ **typing works**. Two hubs, one device behind a hub |

**Steps 6–10 are done.** xv6 takes keyboard input on a real PC. Next, back to the original plan: Step 11 (`spinlock.cpp`).

<div class="check" markdown="1">
**Check against the code**

- add one more hub to the `USB=1` lines in the `Makefile` to get `port 5.3.2`: route `0x23`
- print `rootport, route, depth, ttslot, ttport` at the start of `usbattach()` (QEMU's hub is full speed, so TT is 0)
- (real PC, optional) plug the keyboard into a front socket: if it shows as `port 3.N` and types, the TT path works on real hardware
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-09/">step-09</a></span><span><a href="/xv6/tutorial/">Tutorial</a> →</span></div>
