---
layout: default
title: step-01
permalink: /xv6/tutorial/step-01/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-01

<p class="subtitle">The C++ version begins: a boot skeleton</p>

| | |
|---|---|
| **Previous tag** | `v0.2-x86_64-c` (the finished C version) |
| **This tag** | `step-01` (commit `ddd9638`), branch `cpp` |
| **In one line** | **almost all of** the C kernel deleted; only what booting needs is kept, and two new C++ files, `start.cpp` and `main.cpp` |
| **Plan** | Step 1 on the [progress page](/xv6/plan/) (2026-11-07) |

```sh
git diff --stat v0.2-x86_64-c step-01 -- . ':!docs' ':!*.pdf'
git checkout step-01 && make clean && make qemu
```

## 1. Before: the finished C version (`v0.2`)

A C kernel with a shell that passes `usertests` (45 kernel files, 26 user program files), with a screen console and a PS/2 keyboard ([`v0.2-x86_64-c`](/xv6/tutorial/v0.2-x86_64-c/)).

Instead of converting the C version in place, the C++ version is **rebuilt from scratch**: one piece comes back at a time, in C++, so that each piece can be read next to the C version and the xv6 book.

## 2. What changed

@@FIG maps map_step_01@@

@@STAT v0.2-x86_64-c step-01@@

@@FIG step01 files@@

### 2.1 What was kept, and why

| File | Why it stays |
|---|---|
| `boot/loader.c`, `boot/efi.h` | the UEFI loader, still C (a separate program built with clang, not part of the kernel) |
| `kernel/entry.S` | the kernel's first instructions; assembly stays assembly |
| `kernel/kernel.ld` | the linker script |
| `bootinfo.h`, `memlayout.h`, `param.h`, `types.h`, `x86.h` | constants and small inline functions the next steps use as they are |

### 2.2 `start.cpp`: the C version's `start.c` in C++

@@FIG step01 mangle@@

@@CODE step-01 | kernel/start.cpp | ^void main\(\); | ^}@@

Differences from the C version:

- `extern "C"`: `entry.S` is assembly and doesn't know C++'s **mangled** names (`_Z5startP8bootinfo`), so `start` and `stack0` are exported with plain C names
- **running global constructors**: C++ global objects need their constructors run before `main()`. Normally the C runtime does that; a kernel has none

@@FIG step01 ctors@@

- `EFER.NXE` and the GS base from the C version's `start()` are gone for now (they return with page tables and multiple CPUs)

### 2.3 `main.cpp`: just showing that the kernel is alive

All console code (`uart.c`, `printk.c`, `console.c`, `fbcons.c`) is gone, so `main.cpp` writes to the serial port and paints the screen itself:

@@CODE step-01 | kernel/main.cpp | ^main\(\) | ^}@@

@@FIG step01 flow@@

Some C++ touches:

| In C | Here |
|---|---|
| `#define LSR 5` | `constexpr int LSR = 5;` (typed, visible in the debugger) |
| `(uint *)bootinfo.fb_base` | `reinterpret_cast<uint *>(bootinfo.fb_base)` (a risky cast stands out) |
| `uint *fb = ...` | `auto fb = ...` |

The hand-drawn 8×8 letters `x`, `v`, `6` are replaced by a real font in [step-04](/xv6/tutorial/step-04/).

### 2.4 `Makefile`: building C++

@@FIG step01 pipeline@@

@@CODE step-01 | Makefile | ^# freestanding C\+\+20 | ^CXXFLAGS \+= -Wno-main@@

| Option | Why |
|---|---|
| `-fno-exceptions` | `throw` needs a runtime that unwinds the stack |
| `-fno-rtti` | `dynamic_cast` and `typeid` need runtime support too |
| `-fno-threadsafe-statics` | no `__cxa_guard_*` calls when a function-local `static` object is initialized |
| `-fno-use-cxa-atexit` | global destructors are not registered with `__cxa_atexit` (a kernel never exits) |

`kernel.ld` drops the section for `trampoline.S` (`trampsec`) and adds `.init_array` (diagram above).

### 2.5 For real PCs (`boot/loader.c`, `Makefile`)

This tag also has changes for booting a real PC:

| Change | Why |
|---|---|
| kernel pages allocated as `EfiLoaderCode` | newer firmware may map data pages no-execute, and the kernel runs on the firmware's page tables for a while |
| carry on without a free page below 640 KB | only needed to start other CPUs; a real PC may have none |
| print the memory map near the kernel if its place is taken | to see the cause in a photo if a real PC fails |
| the loader prints screen size and pixel format, then waits 3 s | same reason |
| `usb.img` (a GPT disk image) | real PCs won't boot a bare FAT image without a partition table (`esp.img`) |

@@FIG step01 usbimg@@

## 3. After

QEMU's serial output (`make qemu`):

```
xv6 kernel is booting (C++ skeleton)
nothing else yet; halting
```

The screen turns dark blue with "xv6" in white:

@@IMG xv6-tut-step-01-step01-qemu.png step-01 in QEMU@@

VirtualBox (2560 × 1440):

@@IMG xv6-tut-step-01-step01-vbox.png step-01 in VirtualBox@@

The loader screen (shown for 3 seconds: time to photograph it on a real PC):

@@IMG xv6-tut-step-01-step01-loader-qemu.png the step-01 loader screen@@

- no shell, no keyboard, no `printk()`. But it **boots in all three places**
- from the next step on, pieces of the C version come back one at a time, starting with the serial driver

<div class="check" markdown="1">
**Check against the code**

- `nm kernel/kernel | grep -i " start$\| stack0$"`: unmangled names thanks to `extern "C"`. Remove `extern "C"` and the linker can't find `start`
- `objdump -h kernel/kernel` has an `.init_array` section (size 0: no global objects yet)
- read `git show v0.2-x86_64-c:kernel/start.c` next to `kernel/start.cpp`
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/v0.2-x86_64-c/">v0.2-x86_64-c</a></span><span><a href="/xv6/tutorial/step-02/">step-02</a> →</span></div>
