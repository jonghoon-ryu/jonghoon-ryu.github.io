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

@@IMG xv6-tut-step-06-step06-realpc-ps2.jpg the real PC: the kernel runs, but the keyboard doesn't@@

- the kernel runs: 8 white squares (boot stages), a blinking square (alive), the screen console, the memory map
- **the keyboard doesn't work.** This PC has no PS/2 controller; its status port read `0x55` (absent ports usually read `0xFF`). The firmware's "USB keyboard as PS/2" emulation stops once the kernel takes over

**If it doesn't work on a real PC, it isn't an OS yet**, so before the original Step 6 (memory), a USB keyboard driver was added in five steps. The USB controller sits on the PCI bus.

## 2. What changed

@@FIG maps map_step_06@@

@@STAT step-05 step-06@@

### 2.1 `pci.cpp`: PCI configuration space

@@FIG step06 pciaddr@@

@@CODE step-06 | kernel/pci.cpp | ^static uint32$ | ^}@@

@@CODE step-06 | kernel/pci.cpp | ^pciscan\(uint32 cls | ^}@@

`inl` and `outl` (32-bit port I/O) were added to `x86.h`. In this step only, `main.cpp`'s `pcilist()` prints a few kinds of devices (like Linux's `lspci`):

@@FIG step06 pcitree@@

### 2.2 `earlyvec.S`, `earlytrap.cpp`: exceptions on the screen

@@FIG step06 trapframe@@

`earlyvec.S` generates 32 entry points with assembler macros. The point is to give exceptions with an error code (8, 10–14, 17, 21, 29, 30) and without one the same stack shape:

@@CODE step-06 | kernel/earlyvec.S | ^\.macro vec n | ^earlycommon:@@

@@FIG step06 gate@@

@@CODE step-06 | kernel/earlytrap.cpp | ^earlytrap\(uint64 \*f\) | ^}@@

The traps part of the plan (`trap.cpp`, Step 16) replaces it.

### 2.3 `kbd.cpp`: a lesson from the real PC

The status port can read `0x55` instead of `0xFF`. Bit 0 ("a byte is waiting") is set, so `while (kbdgetc() >= 0)` might never end. It now reads at most 16 bytes per call:

@@CODE step-06 | kernel/kbd.cpp | at most 16 bytes per call | for \(int n = 0; n < 16@@

## 3. After

`make qemu USB=1`:

@@IMG xv6-tut-step-06-step06-qemu.png step-06 in QEMU: PCI devices@@

The real PC's xHCI is `0:20.0  vendor 8086 device 7a60` (an Intel 700-series chipset). The next step wakes it up.

<div class="check" markdown="1">
**Check against the code**

- on Linux, `lspci -nn` shows the same `[vendor:device]` numbers
- put `volatile int zero = 0; printk("%d", 1 / zero);` in `main()`: **no** exception. `100 / zero` traps. Why? `1 / x` can only be 1, −1 or 0, so GCC computes it with a comparison, no division (`objdump -d kernel/main.o` shows `lea 0x1(%rax)`, `cmp $0x2`, `cmovbe`). Division by zero is undefined behavior, so it needn't trap
- compare the vector numbers in `earlyvec.S`'s `.if` line with the "Error Code" column of Intel SDM 3A table 6-1
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-05/">step-05</a></span><span><a href="/xv6/tutorial/step-07/">step-07</a> →</span></div>
