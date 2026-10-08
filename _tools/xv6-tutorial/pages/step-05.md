---
layout: default
title: step-05
permalink: /xv6/tutorial/step-05/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-05

<p class="subtitle">Keyboard input by polling</p>

| | |
|---|---|
| **Previous tag** | `step-04` |
| **This tag** | `step-05` (commit `42a80d2`) |
| **In one line** | the PS/2 keyboard `kbd.cpp`, console input `consoleintr()` and serial input `uartintr()`. With no interrupts yet, `main()`'s loop keeps asking (polling) |
| **C code to compare** | `git show v0.2-x86_64-c:kernel/kbd.c`, `kbd.h`, and `consoleintr` in `console.c` |

```sh
git diff --stat step-04 step-05 -- . ':!docs' ':!*.pdf'
git checkout step-05 && make clean && make vbox     # type in the window
```

## 1. Before (`step-04`)

Output went to the screen and the serial port. There was no input: `main()` printed the boot information and stopped with `hlt`.

In the C plan the keyboard returns only after interrupts (IDT, IOAPIC). To see "type and it shows on the screen" earlier, this step was added: **the same functions, called from a loop instead of by interrupts**.

## 2. What changed

@@FIG maps map_step_05@@

@@STAT step-04 step-05@@

@@FIG step05 inputpath@@

### 2.1 `main()`: the polling loop

@@CODE step-05 | kernel/main.cpp | ^  kbdinit\(\); // PS/2 keyboard | ^  \}@@

`hlt` lets the CPU sleep, but this loop keeps it 100% busy (`top` shows the VirtualBox process using a whole CPU). When interrupts come back (Steps 18, 19) it sleeps in `hlt` again.

### 2.2 `kbd.cpp`, `kbd.h`: key tables built at compile time

@@FIG step05 ps2bits@@

`kbdgetc()` is the C version's (scan code → character; [v0.2](/xv6/tutorial/v0.2-x86_64-c/) 2.2). The biggest change is the **key tables**:

@@FIG step05 keymap@@

@@CODE step-05 | kernel/kbd.h | ^struct Keymap | ^constexpr Keymap shiftcode@@

- `makemap()`'s parameter `const KeyAt (&at)[M]` is **a reference to an array**, so the compiler deduces the length `M` and a braced list can be passed directly
- the ten arrow keys repeated in all three tables (`normalmap`, `shiftmap`, `ctlmap`) are now one `e0keys` array
- `Keymap` has an `operator[]`, so `shiftcode[data]` reads as in the C version

[platform: real PC] Without a keyboard controller the ports read `0xFF`, which looks like an endless stream of "a byte is waiting". `kbdgetc()` filters `0xFF` first (a check the C version lacks; a real PC later turned out to read `0x55` too → [step-06](/xv6/tutorial/step-06/)).

### 2.3 `consoleintr()` in `console.cpp`, `uartintr()` in `uart.cpp`

@@FIG step05 ring@@

`consoleintr()` echoes, handles backspace (`^H`, Delete) and kill-line (`^U`), and collects characters in `cons.buf`. One place differs from the C version:

@@CODE step-05 | kernel/console.cpp | C\('D'\) | cons\.r = cons\.w;@@

The C version wakes `consoleread()` (the shell's `read()`) when a line is complete. There is no reader yet, so the line is dropped at once; otherwise the buffer would fill after 128 characters and input would stop.

`uartintr()`: called by the serial interrupt in the C version, by the loop here:

@@CODE step-05 | kernel/uart.cpp | ^uartintr\(\) | ^}@@

## 3. After

QEMU (`Hi there!` and Ctrl+U sent with QMP `send-key`):

@@IMG xv6-tut-step-05-step05-qemu.png step-05 in QEMU@@

VirtualBox:

@@IMG xv6-tut-step-05-step05-vbox.png step-05 in VirtualBox@@

- QEMU, VirtualBox: both the keyboard and the serial port work
- real PC: **only with a PS/2 keyboard, or if the firmware emulates PS/2 for a USB keyboard.** It didn't work on the barebone of 2026-10-07 → the USB driver from [step-06](/xv6/tutorial/step-06/)

<div class="check" markdown="1">
**Check against the code**

- in `kbd.h`, is entry `0x1E` of `normalmap` `'a'`? (`makemap`'s first list starts at scan code 0)
- find the finished 256-byte tables in `objdump -s -j .rodata kernel/kernel | less`: no code that calls `makemap()` is in the binary
- remove `cons.r = cons.w;` and type more than 130 characters: input stops
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-04/">step-04</a></span><span><a href="/xv6/tutorial/step-06/">step-06</a> →</span></div>
