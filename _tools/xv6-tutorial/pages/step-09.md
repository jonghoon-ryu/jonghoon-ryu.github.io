---
layout: default
title: step-09
permalink: /xv6/tutorial/step-09/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-09

<p class="subtitle">Typing on a USB keyboard</p>

| | |
|---|---|
| **Previous tag** | `step-08` |
| **This tag** | `step-09` (commit `64d9588`) |
| **In one line** | set up the keyboard's interrupt IN endpoint, and turn the boot protocol's 8-byte reports into characters for `consoleintr()`. **The USB keyboard types** |
| **To compare with** | USB HID 1.11: 7.2 (`SET_IDLE`, `SET_PROTOCOL`), appendix B (boot report). HID Usage Tables chapter 10 (key numbers) |

```sh
git diff --stat step-08 step-09 -- . ':!docs' ':!*.pdf'
git checkout step-09 && make clean && make qemu USB=1
# then Ctrl-a c (QEMU monitor) → sendkey h → sendkey i → Ctrl-a c
```

## 1. Before (`step-08`)

The keyboard was identified and printed as `a keyboard (typing comes in step 9)`. No keys were read.

## 2. What changed

@@FIG maps map_step_09@@

@@STAT step-08 step-09@@

@@FIG step09 keypath@@

### 2.1 Keyboard setup (`kbdsetup()`)

@@CODE step-09 | kernel/usb.cpp | ^kbdsetup\(UsbDev &d | ^}@@

| Step | What |
|---|---|
| `configep()` | Configure Endpoint command: adds the keyboard's interrupt IN endpoint and its ring to the controller |
| `SET_CONFIGURATION` | the device turns its interfaces on |
| `SET_PROTOCOL(0)` | boot protocol: the fixed 8-byte report (the firmware may have changed it, so set it again) |
| `SET_IDLE(0)` | report only when something changes (many keyboards refuse; that's fine) |
| `queuein()` | ask for the first report |

@@FIG step09 dci@@

### 2.2 The interrupt endpoint

@@FIG step09 poll@@

Despite the name, it isn't a CPU interrupt. The interval comes from the endpoint's `bInterval`, whose unit depends on the speed:

@@CODE step-09 | kernel/usb.cpp | ^xinterval\(int speed | ^}@@

@@CODE step-09 | kernel/xhci.cpp | ^Xhci::queuein\(UsbDev &d\) | ^}@@

### 2.3 Report → character

@@FIG step09 report@@

@@CODE step-09 | kernel/usb.cpp | ^usbkbdreport\(UsbDev &d | ^}@@

PS/2 (`kbd.cpp`) sends a byte each time a key goes down or up; USB sends **every key held right now**, every time. New presses are found by comparing with the last report.
Key number (HID usage) → character goes through `usbmap` (two rows: plain and Shift); Ctrl+letter is `c & 0x1F` (Ctrl+U = 21 = `C('U')`).

## 3. After

QEMU (typed on the USB keyboard only, with PS/2 switched off):

@@IMG xv6-tut-step-09-step09-qemu.png step-09 in QEMU: typed on the USB keyboard@@

- real PC: the barebone's keyboard (`4d9:a0f8`, full speed) is on root port 6 directly, so **this step's code types on it** (verified with Step 10's code)
- not yet: key repeat (holding a key gives one character; repeat needs a timer), the Caps Lock light, keyboards behind hubs (next step)

<div class="check" markdown="1">
**Check against the code**

- print the report bytes at the start of `usbkbdreport()`, then `sendkey a`, `sendkey shift-a`: the six lines in the diagram in 2.3
- print `xinterval()`'s result in `kbdsetup()`: QEMU gives `bInterval 7 -> interval 6` (8 ms)
- `sendkey z 2000` (hold for 2 seconds): one `z` only
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-08/">step-08</a></span><span><a href="/xv6/tutorial/step-10/">step-10</a> →</span></div>
