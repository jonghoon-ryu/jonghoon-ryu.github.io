---
layout: default
title: step-07
permalink: /xv6/tutorial/step-07/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-07

<p class="subtitle">Starting the xHCI USB controller</p>

| | |
|---|---|
| **Previous tag** | `step-06` |
| **This tag** | `step-07` (commit `8b22258`) |
| **In one line** | `xhci.h`, `xhci.cpp`: take the USB 3 controller (xHCI) found on PCI over from the firmware, reset it, build rings in memory and start it. Reset connected ports and print their speed |
| **To compare with** | [xHCI specification 1.2](https://www.intel.com/content/www/us/en/products/docs/io/universal-serial-bus/extensible-host-controler-interface-usb-xhci.html) 4.2 (init), 4.9 (rings), 5 (registers); the code's comments give section numbers like `(xHCI 4.9.2)` |

```sh
git diff --stat step-06 step-07 -- . ':!docs' ':!*.pdf'
git checkout step-07 && make clean && make qemu USB=1
```

## 1. Before (`step-06`)

The xHCI controller showed up in the PCI list, but nothing touched it. It was in whatever state the firmware left it.

## 2. What changed

@@FIG maps map_step_07@@

@@STAT step-06 step-07@@

**Found at run time, not chosen with `#if`.** `usbinit()` looks for an xHCI with `pciscan(0x0C0330, found)`; without one (VirtualBox, QEMU without `USB=1`) it only prints `usb: no xHCI controller`. The same `usb.img` runs in all three places.

### 2.1 Rings and doorbells

@@FIG step07 rings@@

@@CODE step-07 | kernel/xhci.h | ^struct Trb | ^};@@

@@FIG step07 cycle@@

@@CODE step-07 | kernel/xhci.cpp | ^Ring::push | ^}@@

Reading events:

@@CODE step-07 | kernel/xhci.cpp | ^Xhci::poll\(\) | ^}@@

(The `evring == nullptr` check is for real PCs too: if `wait()` calls `poll()` before the ring exists, it reads address 0. QEMU allows that, but firmware that unmaps page 0 would fault.)

### 2.2 Starting the controller

@@FIG step07 init@@

@@FIG step07 regspace@@

Taking over from the firmware (`[platform: real PC]`: QEMU's controller doesn't even have this capability):

@@CODE step-07 | kernel/xhci.cpp | ^Xhci::handoff\(\) | ^}@@

@@FIG step07 dcbaa@@

Memory: there's no `kalloc` yet, so `dmapage()` takes pages from a free region of the UEFI memory map (below 4 GB, preferably above `PHYSTOP`). Time: there's no timer yet, so `microdelay()` waits on the TSC, assuming at most 5 GHz, so it waits **at least** as long as asked.

In this step only, `init()` ends with a **No Op command** that does nothing, to see that the rings work:

@@CODE step-07 | kernel/xhci.cpp | step 7 only: one command that does nothing | the No Op command failed@@

### 2.3 Ports: connected → reset → speed

@@FIG step07 portsc@@

Each USB 3 socket appears as two controller ports (one for USB 2, one for USB 3). Keyboards are USB 2, so only USB 2 ports are looked at.
**Careful when writing PORTSC**: writing 1 to bit 1 (PED) disables the port, and writing 1 to a change bit clears it. `neutral()` keeps only the bits that are safe to write back:

@@CODE step-07 | kernel/xhci.cpp | ^neutral\(uint32 v\) | ^}@@

@@CODE step-07 | kernel/xhci.cpp | ^Xhci::portchange\(int port\) | ^}@@

### 2.4 A bug found on the real PC: `porthandled`

@@FIG step07 loop@@

@@IMG xv6-tut-step-07-step07-realpc-loop.jpg the real PC, first test: the same device set up over and over@@

(This photo was taken with the code of Step 10. The fix is in this step's port code, so it's shown here.)

## 3. After

@@IMG xv6-tut-step-07-step07-qemu.png step-07 in QEMU: controller started, No Op, three ports@@

```
xhci0: PCI 0:3.0, vendor 1b36 device d, registers at 0x000000c000000000
xhci0: version 100, 8 ports, 32 slots, 32-byte contexts, 0 scratchpad pages
xhci0: running: a No Op command came back
xhci0: port 5: a USB 2 device, high speed
```

On the real PC (with Step 10's code): `version 120, 25 ports, 32 slots, 32-byte contexts, 34 scratchpad pages`.

<div class="check" markdown="1">
**Check against the code**

- comment out the two `porthandled` lines and run `make qemu USB=1`: the same line every 0.1 s, forever (the real PC's bug)
- send 300 No Op commands and print `cmdring.idx`, `cmdring.cycle`: `idx 45 cycle 0` (flipped at the Link after 255)
- print `portsc(port)` before and after `resetport()`: `0xee1` → `0xe03`; decode them with the diagram in 2.3
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-06/">step-06</a></span><span><a href="/xv6/tutorial/step-08/">step-08</a> →</span></div>
