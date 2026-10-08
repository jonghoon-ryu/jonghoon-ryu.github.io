---
layout: default
title: step-02
permalink: /xv6/tutorial/step-02/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-02

<p class="subtitle">The serial driver and string functions</p>

| | |
|---|---|
| **Previous tag** | `step-01` |
| **This tag** | `step-02` (commit `ff6ad7a`) |
| **In one line** | the C version's `uart.c` (output and polled input) and `string.c` in C++. `main.cpp`'s temporary serial code is gone |
| **C code to compare** | `git show v0.2-x86_64-c:kernel/uart.c`, `git show v0.2-x86_64-c:kernel/string.c` |

```sh
git diff --stat step-01 step-02 -- . ':!docs' ':!*.pdf'
git diff step-01 step-02 -- kernel/main.cpp     # how the temporary code went away
```

## 1. Before (`step-01`)

`main.cpp` had temporary functions that drove the serial port directly, `earlyuartinit()` and `earlyputs()` ([step-01](/xv6/tutorial/step-01/) 2.3). The kernel had no basic functions such as `memset`.

## 2. What changed

@@FIG maps map_step_02@@

@@STAT step-01 step-02@@

### 2.1 `uart.cpp`: the 16550 UART driver

A PC's serial port chip (16550) has eight registers starting at **I/O port** `0x3F8`. The RISC-V version drove the same chip at a memory address; on x86 it is `inb`/`outb`.

@@FIG step02 uart@@

The C version's macros became typed C++ constants and inline functions:

@@CODE step-02 | kernel/uart.cpp | ^// C: #define constants | ^WriteReg\(ushort reg, uchar v\)@@

@@FIG step02 uartinit@@

`uartinit()` sets the registers in the same order as the C version, with one difference: the C version enables transmit and receive interrupts at the end, and there is no interrupt handling yet, so they stay off:

@@CODE step-02 | kernel/uart.cpp | ^uartinit\(\) | ^}@@

Only **the polled part** comes back in this step: `uartinit()`, `uartputc_sync()`, `uartgetc()`. The buffered `uartputc()`/`uartwrite()` and `uartintr()` need `sleep()` and interrupts and come later.

@@FIG step02 lsrbits@@

The `0xFF` check in `uartgetc()` is **not in the C version** (it is for real PCs; diagram above):

@@CODE step-02 | kernel/uart.cpp | ^uartgetc\(\) | ^}@@

### 2.2 `string.cpp`: memory and string functions

`memset`, `memcmp`, `memmove`, `memcpy`, `strncmp`, `strncpy`, `safestrcpy`, `strlen`. The bodies are the C version's. What differs is their **linkage**:

@@CODE step-02 | kernel/defs.h | ^// string.cpp | ^char \*strncpy@@

@@CODE step-02 | kernel/string.cpp | ^// memset, memcmp, memmove and memcpy have C linkage | to match what those compiler-made calls pass.@@

C++ mixes the parameter types into a function's name (`strlen` → `_Z6strlenPKc`). But when g++ copies or zeroes a large struct, it **emits calls to `memcpy` and `memset` itself**, and then it looks for the C names.
So those four use `extern "C"` (C names); the rest keep C++ names.

@@FIG step02 cxx@@

### 2.3 `main.cpp`

`earlyuartinit()` → `uartinit()`; `earlyputs()` → a small `uartputs()` on top of `uart.cpp`'s `uartputc_sync()`. The screen painting and the "xv6" letters stay.

## 3. After

The output is almost the same as `step-01` (just the step number):

```
xv6 kernel is booting (C++, step 2)
nothing else yet; halting
```

It looks the same, but serial output now goes through the same function as in the C version (`uartputc_sync`). The next step's `printk()` is built on it.

<div class="check" markdown="1">
**Check against the code**

- `nm kernel/kernel | grep -E " T (mem|_Z.*str)"`: `memset` and friends have plain names, `strlen` and friends `_Z…` names
- `git diff v0.2-x86_64-c:kernel/uart.c step-02:kernel/uart.cpp`: the functions left out (`uartputc`, `uartwrite`, `uartintr`) and the added `0xFF` check
- remove `memcpy` from `string.cpp` and `defs.h`, add a large struct assignment to `main()` (`struct Big { char x[256]; } a{}, b; b = a;`) and build: the link fails with ``undefined reference to `memcpy'``. The code never calls `memcpy`; g++ turned the assignment into a call
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-01/">step-01</a></span><span><a href="/xv6/tutorial/step-03/">step-03</a> →</span></div>
