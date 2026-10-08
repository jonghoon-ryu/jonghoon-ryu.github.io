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

@@FIG maps map_step_10@@

@@STAT step-09 step-10@@

### 2.1 Setting up a hub

@@FIG step10 hubsetup@@

@@CODE step-10 | kernel/usb.cpp | ^    if \(cls == 9\) \{ | ^    \}@@

Without `sethub()` the controller won't route to devices behind the hub:

@@CODE step-10 | kernel/xhci.cpp | ^Xhci::sethub\(UsbDev &d | ^}@@

### 2.2 Each port of the hub

@@FIG step10 hubstatus@@

@@CODE step-10 | kernel/usb.cpp | ^hub\(UsbDev &d, int nports | ^}@@

@@FIG step10 route@@

A child's location: the same root port, 4 more bits (this hub's port number) in the route string, depth + 1.
A low/full speed device behind a **high speed hub** goes through that hub's TT (Transaction Translator: 480 Mb/s ↔ 12 or 1.5 Mb/s), so `ttslot` and `ttport` are filled in.

@@FIG step10 tt@@

### 2.3 Intel 7/8/9 series `[platform: real PC]`

@@CODE step-10 | kernel/xhci.cpp | ^intelroute\(int bus | ^}@@

Those chipsets can connect USB sockets to an old EHCI controller instead, and the firmware may leave them there. Like Linux, xv6 routes every socket to the xHCI on those chips. Not relevant on the barebone (700 series).

## 3. After

QEMU (`make qemu USB=1`: the keyboard behind a hub, typed with PS/2 switched off):

@@IMG xv6-tut-step-10-step10-qemu.png step-10 in QEMU: typing on a keyboard behind a hub@@

### The real PC (barebone), 2026-10-07

@@IMG xv6-tut-step-10-step10-realpc.jpg the real PC: "Hi, claude / It looks like it works!" typed on the USB keyboard@@

@@FIG step10 tree@@

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
