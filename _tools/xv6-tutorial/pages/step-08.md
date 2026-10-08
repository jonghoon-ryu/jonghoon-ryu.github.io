---
layout: default
title: step-08
permalink: /xv6/tutorial/step-08/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-08

<p class="subtitle">Identifying USB devices</p>

| | |
|---|---|
| **Previous tag** | `step-07` |
| **This tag** | `step-08` (commit `605b0ae`) |
| **In one line** | give the device on a reset port a slot and an address, read its descriptors with control transfers, and print what it is (`usb.cpp`, new). Keyboards are kept; everything else is let go |
| **To compare with** | xHCI 1.2: 4.3 (device setup), 4.6.5 (Address Device), 6.2 (contexts). USB 2.0 chapter 9 (requests, descriptors) |

```sh
git diff --stat step-07 step-08 -- . ':!docs' ':!*.pdf'
git checkout step-08 && make clean && make qemu USB=1
```

## 1. Before (`step-07`)

Only that a device was plugged into a port, and its speed, were known (`xhci0: port 5: a USB 2 device, high speed`). Nothing talked to the device.

## 2. What changed

@@FIG maps map_step_08@@

@@STAT step-07 step-08@@

### 2.1 The sequence

@@FIG step08 enum@@

The start of `usbattach()` follows it exactly:

@@CODE step-08 | kernel/usb.cpp | ^usbattach\(Xhci &hc | the device descriptor's first 8 bytes@@

### 2.2 Slots and contexts (`xhci.cpp`)

@@FIG step08 contexts@@

`struct UsbDev` is one device: slot number, speed, location (root port, route string, TT), endpoint 0's ring, the input and device context pages, and a buffer.

@@CODE step-08 | kernel/xhci.cpp | ^Xhci::addressdevice\(UsbDev &d\) | ^}@@

Input context entry 0 says "what to add" (slot and endpoint 0); entry 1 is the slot context (route, speed, root port); entry 2 is endpoint 0 (type Control, max packet size, ring address).
When the command succeeds, the controller sends `SET_ADDRESS` to the device itself.

@@FIG step08 lifecycle@@

### 2.3 Control transfers

@@FIG step08 control@@

@@CODE step-08 | kernel/xhci.cpp | ^Xhci::control\(UsbDev &d | ^}@@

### 2.4 Reading descriptors

@@FIG step08 desc@@

The configuration descriptor is followed by interface (9-byte) and endpoint (7-byte) descriptors. Each starts with its length, so `i += c[i]` steps to the next:

@@CODE step-08 | kernel/usb.cpp | ^findkbd\(uchar \*c, int len\) | ^}@@

In this step, a hub is printed as `a hub: ignored (hubs come in step 10)` and a keyboard as `a keyboard (typing comes in step 9)`.
A device that isn't a keyboard is released with `freedev()` (Disable Slot), and the next device gets that slot again.

## 3. After

@@IMG xv6-tut-step-08-step08-qemu.png step-08 in QEMU: three devices identified@@

```
usb: port 5: high speed, id 627:1, class 0, not a keyboard: ignored
usb: port 6: full speed, id 409:55aa, class 9, a hub: ignored (hubs come in step 10)
usb: port 7: high speed, id 627:1, class 0, a keyboard (typing comes in step 9)
```

(QEMU's `usb-tablet` and `usb-kbd` are both `627:1`; their configuration descriptors' interfaces tell the keyboard apart.)

<div class="check" markdown="1">
**Check against the code**

- print the 18 bytes of the device descriptor and compare them with the diagram in 2.4
- print the product name: after the 18-byte `GET_DESCRIPTOR`, add the code below to get `product: QEMU USB Keyboard` (string descriptors are type 3, UTF-16; printing the low bytes is enough for English)

  ```cpp
  uchar s[64];
  if (dd[15] && hc.control(*d, 0x80, GET_DESCRIPTOR, (3 << 8) | dd[15], 0x0409, sizeof(s), s)) {
    printk("product: ");
    for (int i = 2; i + 1 < s[0]; i += 2)
      printk("%c", s[i]);
    printk("\n");
  }
  ```
- send an unknown vendor request (`0xC0, 0x42`): STALL (completion code 6). Without `resetep()` the next request ends in `timed out`
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-07/">step-07</a></span><span><a href="/xv6/tutorial/step-09/">step-09</a> →</span></div>
