---
layout: default
title: step-03
permalink: /xv6/tutorial/step-03/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-03

<p class="subtitle">printk and panic</p>

| | |
|---|---|
| **Previous tag** | `step-02` |
| **This tag** | `step-03` (commit `63c1be0`) |
| **In one line** | formatted output `printk("%d %x %p %s")`, `panic()`, and below them `consputc()` (the output half of `console.c`) |
| **C code to compare** | `git show v0.2-x86_64-c:kernel/printk.c`, `git show v0.2-x86_64-c:kernel/console.c` |

```sh
git diff --stat step-02 step-03 -- . ':!docs' ':!*.pdf'
git checkout step-03 && make clean && make qemu
```

## 1. Before (`step-02`)

Strings could be sent to the serial port as they were. Printing a number meant turning it into characters yourself.

## 2. What changed

@@FIG maps map_step_03@@

@@STAT step-02 step-03@@

@@FIG step03 layers@@

### 2.1 `printk.cpp`

@@FIG step03 printkflow@@

Almost the same as the C version's `printk.c`. `printint()` turns a number into characters in a given base:

@@CODE step-03 | kernel/printk.cpp | ^static constexpr char digits | ^printptr\(uint64 x\)@@

@@FIG step03 printint@@

The body of `printk()` walks the format string and branches on the character after `%` (`%d`, `%ld`, `%lld`, `%u`, `%x`, `%p`, `%s`, `%c`, `%%`).
`<stdarg.h>` is not a C library header but **one the compiler provides**, so a freestanding kernel can use it.

Different from the C version: the C version takes `pr.lock` so that output from several CPUs doesn't interleave. There is one CPU and no lock code yet, so it's left out (it returns with `spinlock.cpp`).

`panic()`:

@@CODE step-03 | kernel/printk.cpp | ^panic\(const char \*s\) | ^}@@

Its declaration has `[[noreturn]]` (C++11): the compiler knows the function never returns, which avoids warnings about the code after it.

### 2.2 The `format(printf)` attribute: a check the C version lacks

@@FIG step03 fmtcheck@@

@@CODE step-03 | kernel/defs.h | ^// printk.cpp | \[\[noreturn\]\]@@

### 2.3 `console.cpp` (output only)

Only `consputc()` and `consoleinit()` come back. The input side (`consoleintr`, `consoleread`) and `consolewrite` need interrupts and processes and come later:

@@CODE step-03 | kernel/console.cpp | ^// C: #define BACKSPACE | ^consoleinit\(\)@@

### 2.4 `main.cpp`: printing the boot information

With numbers available, `main()` prints what the loader handed over (screen, ACPI, fs.img, and the UEFI memory map summed by type):

@@CODE step-03 | kernel/main.cpp | ^printbootinfo\(\) | ^}@@

## 3. After

QEMU's serial output (`make qemu`):

```
xv6 kernel is booting (C++, step 3)

screen: 1280x800, frame buffer at 0x0000000080000000
ACPI root pointer at 0x000000001f77e014
fs.img: 1024 bytes at 0x0000000007ffe000
UEFI memory map: 131 entries
  reserved: 3211392 pages (12544 MB)
  loader code: 33 pages (0 MB)
  ...
  free: 118232 pages (461 MB)
  ...
nothing else yet; halting
```

The screen is still step-01's dark blue picture: `printk()` goes to the serial port only (the screen is the next step).

- `free: 118232 pages (461 MB)`: the part of QEMU's 512 MB the firmware doesn't use. `kalloc.cpp` (Step 12) will hand it out
- `reserved: 12544 MB` is far more than the VM's 512 MB of RAM: the memory map's "reserved" also covers address ranges that aren't RAM. The kernel only uses `free` (type 7)

<div class="check" markdown="1">
**Check against the code**

- remove the `(void *)` in `main.cpp`'s `printk("%p", (void *)bootinfo.fb_base)` and build: the error in the diagram above
- put `panic("test")` in `main()` and boot: it stops after `panic: test`
- `git diff v0.2-x86_64-c:kernel/printk.c step-03:kernel/printk.cpp`: the lock left out, the `constexpr` added
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-02/">step-02</a></span><span><a href="/xv6/tutorial/step-04/">step-04</a> →</span></div>
