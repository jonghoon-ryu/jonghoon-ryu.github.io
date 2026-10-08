---
layout: default
title: step-04
permalink: /xv6/tutorial/step-04/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# step-04

<p class="subtitle">Text on the screen</p>

| | |
|---|---|
| **Previous tag** | `step-03` |
| **This tag** | `step-04` (commit `918bf02`) |
| **In one line** | the C version's screen console `fbcons.c` and font `font.h` in C++. `printk()` appears on the serial port and **on the screen**; the blue screen and hand-drawn letters are gone |
| **C code to compare** | `git show v0.2-x86_64-c:kernel/fbcons.c` (diagrams in [v0.2](/xv6/tutorial/v0.2-x86_64-c/) 2.1) |

```sh
git diff --stat step-03 step-04 -- . ':!docs' ':!*.pdf'
git diff v0.2-x86_64-c:kernel/fbcons.c step-04:kernel/fbcons.cpp    # the C version vs the C++ version
git checkout step-04 && make clean && make vbox
```

## 1. Before (`step-03`)

@@FIG step04 beforeafter@@

`printk()` went to the serial port only. The screen had just the dark blue background and the hand-drawn 8×8 "xv6" painted by `main.cpp`. On a real PC without a serial port, the boot messages were invisible.

## 2. What changed

@@FIG maps map_step_04@@

@@STAT step-03 step-04@@

`font.h` is the C version's, unchanged (Spleen bitmaps, 547 lines). `main.cpp` loses `paintscreen()`, `drawglyph()` and the hand-drawn letters (−50 lines).

### 2.1 `fbcons.cpp`: same job as the C version, C++ shape

@@FIG step04 cursorrules@@

How characters, the cursor and scrolling work is shown in [v0.2](/xv6/tutorial/v0.2-x86_64-c/) 2.1. What changed is the structure of the code:

@@FIG step04 fbclass@@

@@CODE step-04 | kernel/fbcons.cpp | ^namespace \{ | ^  int charw, charh;@@

Inside member functions it's just `fb` instead of `cons.fb`. Scrolling:

@@CODE step-04 | kernel/fbcons.cpp | ^  // move every line up by one | ^  \}@@

The C version's `#define BIGSCREEN 2560`, `FG` and `BG` became `constexpr`. Which font each platform gets is noted in `[platform: ...]` comments:

@@CODE step-04 | kernel/fbcons.cpp | ^// the big font on screens at least this wide | ^constexpr uint BG@@

### 2.2 `console.cpp`: sending to the screen too

`consputc()` sends to **the screen before** the serial port (so the screen still shows when the serial socket is blocked). `consoleinit()` also calls `fbconsinit()`:

@@CODE step-04 | kernel/console.cpp | ^consputc\(int c\) | ^}@@

## 3. After

QEMU (1280 × 800, 16×32 font):

@@IMG xv6-tut-step-04-step04-qemu.png step-04 in QEMU@@

VirtualBox (2560 × 1440, 32×64 font):

@@IMG xv6-tut-step-04-step04-vbox.png step-04 in VirtualBox@@

- the serial output is the same as `step-03`; the same text is now on the screen too
- **the boot messages are visible on a real PC as well.** The first photo from the barebone on 2026-10-07 ([step-06](/xv6/tutorial/step-06/)) shows this screen console

<div class="check" markdown="1">
**Check against the code**

- pair each `FbCons` member function with the `static` function of the C version it came from
- what changes without `namespace {`? Compare symbol names with `nm kernel/kernel | grep cons`
- set `BIGSCREEN` to 1024 and open QEMU in a window: the big font. Window command: `qemu-system-x86_64 -machine q35 -m 512M -serial stdio -drive if=pflash,format=raw,readonly=on,file=/usr/share/OVMF/OVMF_CODE_4M.fd -drive if=pflash,format=raw,file=ovmf_vars.fd -drive format=raw,file=usb.img`
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-03/">step-03</a></span><span><a href="/xv6/tutorial/step-05/">step-05</a> →</span></div>
