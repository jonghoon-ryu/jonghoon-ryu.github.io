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

<p class="subtitle">The PCI bus and an exception screen</p>

| | |
|---|---|
| **Previous tag** | `step-05` |
| **This tag** | `step-06` (commit `f184476`) |
| **In one line** | the first of five steps for a USB keyboard driver (Steps 6–10). Reads the PCI bus (`pci.cpp`) and adds a temporary IDT that prints CPU exceptions on the screen (`earlytrap.cpp`) |
| **To compare with** | no C code: the C version has no PCI or USB. Specs: [OSDev "PCI"](https://wiki.osdev.org/PCI), Intel SDM 3A chapter 6 |

```sh
git diff --stat step-05 step-06 -- . ':!docs' ':!*.pdf'
git checkout step-06 && make clean && make qemu USB=1     # USB=1: QEMU gets an xHCI controller
```

## 1. Before (`step-05`), and why this step exists

`step-05` takes PS/2 keyboard input in QEMU and VirtualBox. On 2026-10-07 it (plus diagnostic code) was booted on a real PC, a barebone:

![the real PC: the kernel runs, but the keyboard doesn't](/assets/image/xv6-tut-step-06-step06-realpc-ps2.jpg)

- the kernel runs: 8 white squares (boot stages), a blinking square (alive), the screen console, the memory map
- **the keyboard doesn't work.** This PC has no PS/2 controller; its status port read `0x55` (absent ports usually read `0xFF`). The firmware's "USB keyboard as PS/2" emulation stops once the kernel takes over

**If it doesn't work on a real PC, it isn't an OS yet**, so before the original Step 6 (memory), a USB keyboard driver was added in five steps. The USB controller sits on the PCI bus.

## 2. What changed

<!-- fig:map_step_06 -->
<svg viewBox="0 0 1000 286" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="files changed from step-05 to step-06"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Change map: step-05 → step-06  (lines added / removed per file; bar length ∝ √lines)</text><text x="300.0" y="50.0" font-size="11.5" font-weight="700" fill="#c0392b" text-anchor="end">removed ←</text><text x="320.0" y="50.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="start">file</text><text x="620.0" y="50.0" font-size="11.5" font-weight="700" fill="#1e8449" text-anchor="start">→ added</text><rect x="305" y="63" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="75.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/earlytrap.cpp</text><text x="570.0" y="75.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="64" width="236.0" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="856.0" y="75.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+61</text><rect x="305" y="85" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="97.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/pci.cpp</text><text x="570.0" y="97.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="86" width="236.0" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="856.0" y="97.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+61</text><rect x="305" y="107" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="119.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/earlyvec.S</text><text x="570.0" y="119.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="108" width="187.53263717760433" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="807.5" y="119.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+38</text><rect x="305" y="129" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="141.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/main.cpp</text><text x="570.0" y="141.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="259.5515176154339" y="130" width="35.44848238456608" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="254.6" y="141.0" font-size="11.5" fill="#c0392b" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−1</text><rect x="615" y="130" width="194.56229131222932" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="814.6" y="141.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+41</text><rect x="305" y="151" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="163.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/x86.h</text><text x="570.0" y="163.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="152" width="120.05348184650688" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="740.1" y="163.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+15</text><rect x="305" y="173" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="185.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">Makefile</text><text x="570.0" y="185.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="174" width="103.66956671499614" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="723.7" y="185.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+11</text><rect x="305" y="195" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="207.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/kbd.cpp</text><text x="570.0" y="207.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="237.99373230413448" y="196" width="57.006267695865525" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="233.0" y="207.0" font-size="11.5" fill="#c0392b" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−3</text><rect x="615" y="196" width="89.29288635911705" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="709.3" y="207.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+8</text><rect x="305" y="217" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="229.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/defs.h</text><text x="570.0" y="229.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="218" width="89.29288635911705" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="709.3" y="229.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+8</text><text x="500.0" y="262.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Total: 8 files, +243 −4 lines (docs and PDFs not counted)</text></svg>
<!-- /fig:map_step_06 -->

| File | | Added | Removed |
|---|---|---:|---:|
| `Makefile` | changed | 11 | 0 |
| `kernel/defs.h` | changed | 8 | 0 |
| `kernel/earlytrap.cpp` | new | 61 | 0 |
| `kernel/earlyvec.S` | new | 38 | 0 |
| `kernel/kbd.cpp` | changed | 8 | 3 |
| `kernel/main.cpp` | changed | 41 | 1 |
| `kernel/pci.cpp` | new | 61 | 0 |
| `kernel/x86.h` | changed | 15 | 0 |
| **Total** (8 files) | | **243** | **4** |

### 2.1 `pci.cpp`: PCI configuration space

<!-- fig:pciaddr -->
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="PCI configuration address"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Reading PCI configuration space: address to port 0xCF8, value from 0xCFC</text><rect x="100" y="70" width="60.0" height="44" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1.5"/><text x="130.0" y="96.0" font-size="11.5" fill="#4d5656" text-anchor="middle">enable</text><text x="130.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">31</text><rect x="160.0" y="70" width="70.0" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="195.0" y="96.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0</text><text x="162.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">30</text><text x="228.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">24</text><rect x="230.0" y="70" width="150.0" height="44" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="305.0" y="96.0" font-size="11.5" fill="#4d5656" text-anchor="middle">bus</text><text x="232.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">23</text><text x="378.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">16</text><rect x="380.0" y="70" width="120.0" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="440.0" y="96.0" font-size="11.5" fill="#4d5656" text-anchor="middle">device</text><text x="382.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">15</text><text x="498.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">11</text><rect x="500.0" y="70" width="90.0" height="44" rx="0" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="545.0" y="96.0" font-size="11.5" fill="#4d5656" text-anchor="middle">func</text><text x="502.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">10</text><text x="588.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">8</text><rect x="590.0" y="70" width="130.0" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="655.0" y="96.0" font-size="11.5" fill="#4d5656" text-anchor="middle">register</text><text x="592.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">7</text><text x="718.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">2</text><rect x="720.0" y="70" width="50.0" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="745.0" y="96.0" font-size="11.5" fill="#4d5656" text-anchor="middle">00</text><text x="722.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">1</text><text x="768.0" y="66.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><text x="90.0" y="97.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="end">0xCF8 ←</text><text x="500.0" y="140.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">pciaddr(bus, dev, func, off) = 0x80000000 | bus &lt;&lt; 16 | dev &lt;&lt; 11 | func &lt;&lt; 8 | (off &amp; 0xFC)</text><rect x="100" y="170" width="70" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="135.0" y="187.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0x00</text><rect x="170" y="170" width="240" height="26" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="290.0" y="187.0" font-size="11.5" fill="#4d5656" text-anchor="middle">vendor ID | device ID</text><text x="425.0" y="188.0" font-size="11.5" fill="#4d5656" text-anchor="start">0xFFFFFFFF if absent</text><rect x="100" y="200" width="70" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="135.0" y="217.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0x04</text><rect x="170" y="200" width="240" height="26" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="290.0" y="217.0" font-size="11.5" fill="#4d5656" text-anchor="middle">command</text><text x="425.0" y="218.0" font-size="11.5" fill="#4d5656" text-anchor="start">bit 1 memory, bit 2 bus master</text><rect x="100" y="230" width="70" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="135.0" y="247.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0x08</text><rect x="170" y="230" width="240" height="26" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="290.0" y="247.0" font-size="11.5" fill="#4d5656" text-anchor="middle">class code (31:8)</text><text x="425.0" y="248.0" font-size="11.5" fill="#4d5656" text-anchor="start">0x0C0330 = USB xHCI</text><rect x="100" y="260" width="70" height="26" rx="2" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="135.0" y="277.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0x10</text><rect x="170" y="260" width="240" height="26" rx="2" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="290.0" y="277.0" font-size="11.5" fill="#4d5656" text-anchor="middle">BAR0 (+ BAR1)</text><text x="425.0" y="278.0" font-size="11.5" fill="#4d5656" text-anchor="start">address of the device registers</text><rect x="640" y="170" width="340" height="116" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="810.0" y="200.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">pciscan(cls, found)</text><text x="810.0" y="216.0" font-size="11.5" fill="#4d5656" text-anchor="middle">bus 256 × device 32 × function 8</text><text x="810.0" y="232.0" font-size="11.5" fill="#4d5656" text-anchor="middle">skips vendor 0xFFFF</text><text x="810.0" y="248.0" font-size="11.5" fill="#4d5656" text-anchor="middle">calls found() when the class matches</text><text x="810.0" y="264.0" font-size="11.5" fill="#4d5656" text-anchor="middle">(no bridge walking: the simple way)</text></svg>
<!-- /fig:pciaddr -->

[`kernel/pci.cpp:20–24`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-06/kernel/pci.cpp#L20-L24) (tag `step-06`)

```cpp
static uint32
pciaddr(int bus, int dev, int func, int off)
{
  return 0x80000000u | (bus << 16) | (dev << 11) | (func << 8) | (off & 0xFC);
}
```

[`kernel/pci.cpp:44–61`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-06/kernel/pci.cpp#L44-L61) (tag `step-06`)

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

`inl` and `outl` (32-bit port I/O) were added to `x86.h`. In this step only, `main.cpp`'s `pcilist()` prints a few kinds of devices (like Linux's `lspci`):

<!-- fig:pcitree -->
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="PCI device tree"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">PCI bus 0 of QEMU&#x27;s q35 machine (step-06&#x27;s list, make qemu USB=1)</text><rect x="400" y="45" width="200" height="50" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="500.0" y="66.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">bus 0</text><text x="500.0" y="82.0" font-size="11.5" fill="#4d5656" text-anchor="middle">PCI root</text><path d="M500,95 L500,120 L110,120 L110,140" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="20" y="142" width="180" height="80" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="110.0" y="170.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">0:0.0</text><text x="110.0" y="186.0" font-size="11.5" fill="#4d5656" text-anchor="middle">8086:29c0</text><text x="110.0" y="202.0" font-size="11.5" fill="#4d5656" text-anchor="middle">host bridge</text><path d="M500,95 L500,120 L304,120 L304,140" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="214" y="142" width="180" height="80" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="304.0" y="170.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">0:1.0</text><text x="304.0" y="186.0" font-size="11.5" fill="#4d5656" text-anchor="middle">1234:1111</text><text x="304.0" y="202.0" font-size="11.5" fill="#4d5656" text-anchor="middle">VGA (screen)</text><path d="M500,95 L500,120 L498,120 L498,140" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="408" y="142" width="180" height="80" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="498.0" y="170.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">0:2.0</text><text x="498.0" y="186.0" font-size="11.5" fill="#4d5656" text-anchor="middle">8086:10d3</text><text x="498.0" y="202.0" font-size="11.5" fill="#4d5656" text-anchor="middle">Ethernet</text><path d="M500,95 L500,120 L692,120 L692,140" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="602" y="142" width="180" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="692.0" y="170.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">0:3.0</text><text x="692.0" y="186.0" font-size="11.5" fill="#4d5656" text-anchor="middle">1b36:000d</text><text x="692.0" y="202.0" font-size="11.5" fill="#4d5656" text-anchor="middle">xHCI (USB 3)</text><path d="M500,95 L500,120 L886,120 L886,140" fill="none" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="796" y="142" width="180" height="80" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="886.0" y="170.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">0:31.2</text><text x="886.0" y="186.0" font-size="11.5" fill="#4d5656" text-anchor="middle">8086:2922</text><text x="886.0" y="202.0" font-size="11.5" fill="#4d5656" text-anchor="middle">SATA AHCI</text><text x="500.0" y="250.0" font-size="11.5" fill="#4d5656" text-anchor="middle">bus:device.function. 0:31.2 = function 2 of device 31: several functions of one chip (ICH9)</text><text x="500.0" y="274.0" font-size="11.5" fill="#7d3c98" text-anchor="middle">the real PC&#x27;s xHCI: 0:20.0, 8086:7a60 (Intel 700 series)</text></svg>
<!-- /fig:pcitree -->

### 2.2 `earlyvec.S`, `earlytrap.cpp`: exceptions on the screen

<!-- fig:trapframe -->
<svg viewBox="0 0 1000 330" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="exception stack"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">When a CPU exception happens: earlyvec.S → earlytrap() and its stack</text><rect x="20" y="60" width="240" height="90" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="140.0" y="93.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU exception</text><text x="140.0" y="109.0" font-size="11.5" fill="#4d5656" text-anchor="middle">divide by 0, bad pointer …</text><text x="140.0" y="125.0" font-size="11.5" fill="#4d5656" text-anchor="middle">jumps to IDT[n]</text><rect x="300" y="60" width="240" height="90" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="420.0" y="85.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">earlyvec.S entry n</text><text x="420.0" y="101.0" font-size="11.5" fill="#4d5656" text-anchor="middle">pushes 0 if no error code</text><text x="420.0" y="117.0" font-size="11.5" fill="#4d5656" text-anchor="middle">pushes n</text><text x="420.0" y="133.0" font-size="11.5" fill="#4d5656" text-anchor="middle">jmp earlycommon</text><rect x="580" y="60" width="400" height="90" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="780.0" y="85.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">earlytrap(f)</text><text x="780.0" y="101.0" font-size="11.5" fill="#4d5656" text-anchor="middle">&quot;CPU exception 14 (page fault), error code 2&quot;</text><text x="780.0" y="117.0" font-size="11.5" fill="#4d5656" text-anchor="middle">&quot;rip 0x…, address 0x… (cr2)&quot;</text><text x="780.0" y="133.0" font-size="11.5" fill="#4d5656" text-anchor="middle">panic → stays on screen</text><line x1="260" y1="105" x2="298" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="540" y1="105" x2="578" y2="105" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="80" y="175" width="260" height="22" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="210.0" y="190.0" font-size="11.5" fill="#4d5656" text-anchor="middle">f[0] = vector number n</text><rect x="80" y="197" width="260" height="22" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="210.0" y="212.0" font-size="11.5" fill="#4d5656" text-anchor="middle">f[1] = error code (or 0)</text><rect x="80" y="219" width="260" height="22" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="210.0" y="234.0" font-size="11.5" fill="#4d5656" text-anchor="middle">f[2] = rip</text><rect x="80" y="241" width="260" height="22" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="210.0" y="256.0" font-size="11.5" fill="#4d5656" text-anchor="middle">f[3] = cs</text><rect x="80" y="263" width="260" height="22" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="210.0" y="278.0" font-size="11.5" fill="#4d5656" text-anchor="middle">f[4] = rflags</text><rect x="80" y="285" width="260" height="22" rx="0" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="210.0" y="300.0" font-size="11.5" fill="#4d5656" text-anchor="middle">f[5] = rsp, f[6] = ss</text><text x="345.0" y="190.0" font-size="11.5" fill="#4d5656" text-anchor="start">← rsp (= f)</text><rect x="480" y="175" width="500" height="132" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="730.0" y="205.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">Why now</text><text x="730.0" y="221.0" font-size="11.5" fill="#4d5656" text-anchor="middle">with no IDT of its own, the firmware&#x27;s IDT is still loaded</text><text x="730.0" y="237.0" font-size="11.5" fill="#4d5656" text-anchor="middle">QEMU: OVMF prints registers and hangs</text><text x="730.0" y="253.0" font-size="11.5" fill="#4d5656" text-anchor="middle">real PC: that firmware code may be gone → silent reboot</text><text x="730.0" y="269.0" font-size="11.5" fill="#4d5656" text-anchor="middle">much of the USB driver can only be tested on a real PC:</text><text x="730.0" y="285.0" font-size="11.5" fill="#4d5656" text-anchor="middle">failures must be visible in a photo</text></svg>
<!-- /fig:trapframe -->

`earlyvec.S` generates 32 entry points with assembler macros. The point is to give exceptions with an error code (8, 10–14, 17, 21, 29, 30) and without one the same stack shape:

[`kernel/earlyvec.S:12–31`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-06/kernel/earlyvec.S#L12-L31) (tag `step-06`)

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

<!-- fig:gate -->
<svg viewBox="0 0 1000 230" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="IDT gate"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">One IDT entry (struct gatedesc, 16 bytes): earlytrapinit() fills 32 of them</text><rect x="60" y="60" width="125.71428571428572" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="122.9" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">rsvd (0)</text><text x="62.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">127</text><text x="183.7" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">96</text><rect x="185.71428571428572" y="60" width="167.61904761904762" height="44" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="269.5" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">off_63_32</text><text x="187.7" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">95</text><text x="351.3" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">64</text><rect x="353.33333333333337" y="60" width="125.71428571428572" height="44" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="416.2" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">off_31_16</text><text x="355.3" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">63</text><text x="477.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">48</text><rect x="479.0476190476191" y="60" width="125.71428571428572" height="44" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="541.9" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">type_attr 0x8E</text><text x="481.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">47</text><text x="602.8" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">40</text><rect x="604.7619047619048" y="60" width="83.80952380952381" height="44" rx="0" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="1.5"/><text x="646.7" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">ist (0)</text><text x="606.8" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">39</text><text x="686.6" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">32</text><rect x="688.5714285714287" y="60" width="125.71428571428572" height="44" rx="0" fill="#eef2f7" stroke="#34495e" stroke-width="1.5"/><text x="751.4" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">cs (code selector)</text><text x="690.6" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">31</text><text x="812.3" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">16</text><rect x="814.2857142857144" y="60" width="125.71428571428572" height="44" rx="0" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="877.1" y="86.0" font-size="11.5" fill="#4d5656" text-anchor="middle">off_15_0</text><text x="816.3" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">15</text><text x="938.0" y="56.0" font-size="11.5" fill="#7f8c8d" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">0</text><text x="500.0" y="140.0" font-size="11.5" fill="#4d5656" text-anchor="middle">the three off_* pieces = handler address (earlyvectors + 16 × n). cs = the current code segment (mov %cs)</text><text x="500.0" y="164.0" font-size="11.5" fill="#4d5656" text-anchor="middle">0x8E = 1000 1110: P (present) = 1, DPL = 0 (kernel only), type 0xE = 64-bit interrupt gate (interrupts off on entry)</text><text x="500.0" y="188.0" font-size="11.5" fill="#4d5656" text-anchor="middle">lidt(idt, sizeof(idt)) tells the CPU the table&#x27;s address and size</text></svg>
<!-- /fig:gate -->

[`kernel/earlytrap.cpp:53–61`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-06/kernel/earlytrap.cpp#L53-L61) (tag `step-06`)

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

The traps part of the plan (`trap.cpp`, Step 16) replaces it.

### 2.3 `kbd.cpp`: a lesson from the real PC

The status port can read `0x55` instead of `0xFF`. Bit 0 ("a byte is waiting") is set, so `while (kbdgetc() >= 0)` might never end. It now reads at most 16 bytes per call:

[`kernel/kbd.cpp:128–132`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-06/kernel/kbd.cpp#L128-L132) (tag `step-06`)

```cpp
  // [platform: real PC] at most 16 bytes per call: with no
  // controller, the status port may read as "a byte is waiting"
  // forever, and this loop must not starve the other devices.
  // (the C version loops until kbdgetc() says no more.)
  for (int n = 0; n < 16 && (c = kbdgetc()) >= 0; n++) {
```

## 3. After

`make qemu USB=1`:

![step-06 in QEMU: PCI devices](/assets/image/xv6-tut-step-06-step06-qemu.png)

The real PC's xHCI is `0:20.0  vendor 8086 device 7a60` (an Intel 700-series chipset). The next step wakes it up.

<div class="check" markdown="1">
**Check against the code**

- on Linux, `lspci -nn` shows the same `[vendor:device]` numbers
- put `volatile int zero = 0; printk("%d", 1 / zero);` in `main()`: **no** exception. `100 / zero` traps. Why? `1 / x` can only be 1, −1 or 0, so GCC computes it with a comparison, no division (`objdump -d kernel/main.o` shows `lea 0x1(%rax)`, `cmp $0x2`, `cmovbe`). Division by zero is undefined behavior, so it needn't trap
- compare the vector numbers in `earlyvec.S`'s `.if` line with the "Error Code" column of Intel SDM 3A table 6-1
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-05/">step-05</a></span><span><a href="/xv6/tutorial/step-07/">step-07</a> →</span></div>
