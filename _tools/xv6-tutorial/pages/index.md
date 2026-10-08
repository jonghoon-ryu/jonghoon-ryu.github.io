---
layout: default
title: Tutorial
permalink: /xv6/tutorial/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# Tutorial: reading the code tag by tag

One page per **git tag** of [jonghoon-ryu/xv6-x86_64](https://github.com/jonghoon-ryu/xv6-x86_64). Each page has three parts:

1. **Before**: what the code at the previous tag looked like and did
2. **What changed**: file by file, what changed and why. Code excerpts are copied from that tag, and their links go to that tag and line on GitHub
3. **After**: what you see when it boots (screens, photos)

Colors in the diagrams: <span style="background:#eafaf1;border:1px solid #1e8449;padding:0 4px">new</span>
<span style="background:#fef9e7;border:1px solid #b7950b;padding:0 4px">changed</span>
<span style="background:#fdedec;border:1px solid #c0392b;padding:0 4px">deleted</span>
<span style="background:#f4ecf7;border:1px solid #7d3c98;padding:0 4px">hardware, firmware</span>

@@FIG index timeline@@

## The whole picture

@@FIG index system@@

@@FIG index lines@@

## Tags

| Tag | Previous tag | In one line |
|---|---|---|
| [`v0.1-x86_64-c`](/xv6/tutorial/v0.1-x86_64-c/) | MIT `06aad25` | xv6-riscv ported to x86-64 PCs (C). UEFI boot, several CPUs, `usertests` pass. Serial port only |
| [`v0.2-x86_64-c`](/xv6/tutorial/v0.2-x86_64-c/) | `v0.1-x86_64-c` | + screen console (GOP frame buffer, font), PS/2 keyboard |
| [`step-01`](/xv6/tutorial/step-01/) | `v0.2-x86_64-c` | start of the C++ version: everything but the boot skeleton deleted. `start.cpp`, `main.cpp` |
| [`step-02`](/xv6/tutorial/step-02/) | `step-01` | `uart.cpp`, `string.cpp`: serial output |
| [`step-03`](/xv6/tutorial/step-03/) | `step-02` | `printk.cpp`, `console.cpp`: `printk()`, `panic()` |
| [`step-04`](/xv6/tutorial/step-04/) | `step-03` | `fbcons.cpp`, `font.h`: text on the screen |
| [`step-05`](/xv6/tutorial/step-05/) | `step-04` | `kbd.cpp`: keyboard input (polling) |
| [`step-06`](/xv6/tutorial/step-06/) | `step-05` | `pci.cpp`, `earlytrap.cpp`: the PCI bus, CPU exceptions on screen |
| [`step-07`](/xv6/tutorial/step-07/) | `step-06` | `xhci.cpp`: the USB controller starts |
| [`step-08`](/xv6/tutorial/step-08/) | `step-07` | `usb.cpp`: identifying USB devices |
| [`step-09`](/xv6/tutorial/step-09/) | `step-08` | typing on a USB keyboard |
| [`step-10`](/xv6/tutorial/step-10/) | `step-09` | USB hubs; the code verified on the real PC |

## How to read

<div class="tip" markdown="1">
**Studying one tag** (for example `step-03`)

```sh
cd ~/Ryu/xv6-x86_64
git fetch --tags
git diff --stat step-02 step-03        # changed files (the same as the page's "What changed" table)
git diff step-02 step-03 -- kernel     # every changed line
git checkout step-03                   # that tag's code (read-only look)
make clean && make qemu                # boot it as it was
git checkout cpp                       # back to the latest
```

To keep two tags open side by side: `git worktree add ../xv6-step03 step-03`
</div>

- The link above each code excerpt (for example [`kernel/main.cpp:12–30`]) goes to **that line at that tag**, the same line numbers as in your checkout
- The schedule is on the [progress page](/xv6/plan/) and the final goal on the [goal page](/xv6/goal/) (both in Korean)
