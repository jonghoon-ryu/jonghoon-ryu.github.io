---
layout: default
title: step-11
permalink: /xv6/tutorial/step-11/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
details { margin:0.6rem 0; }
summary { cursor:pointer; font-weight:600; }
</style>

# step-11

<p class="subtitle">The first piece of the OS: spinlocks</p>

| | |
|---|---|
| **Previous tag** | `step-10` (see [Code explanation up to step 10](/xv6/tutorial/code-explanation-step-10/) for the whole program at that point) |
| **This tag** | `step-11` (commit `8cad126`) |
| **In one line** | `spinlock.cpp` from the C version, the smallest `struct cpu` it needs, an RAII `LockGuard`, and `printk()` taking its first lock. One bug fix found while testing |
| **Book** | xv6 book, [RISC-V rev5](https://pdos.csail.mit.edu/6.1810/2025/xv6/book-riscv-rev5.pdf), chapter 7 "Locking": §7.1–7.5 (§7.6 optional), and §8.5 "Code: mycpu and myproc". Older editions call Locking chapter 6 |
| **Your time** | about 2 hours, see [section 9](#9-how-to-spend-the-2-hours) |

```sh
cd ~/Ryu/xv6-x86_64
git diff --stat step-10 step-11
git checkout step-11 && make clean && make qemu
```

## 1. Why this is step 11

Step 10 ended with a working machine and no OS: it boots, prints and echoes keys, but nothing is shared, so nothing needs managing. Every step from here adds one OS mechanism. Which one should come first?

<!-- fig:why -->
<svg viewBox="0 0 1000 420" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="why spinlock first"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Why spinlock is step 11: what each candidate needs, and what needs it</text><rect x="15" y="55" width="225" height="80" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="127.5" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">spinlock</text><text x="127.5" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">needs: nothing new</text><text x="127.5" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">~100 lines, no hardware</text><rect x="263" y="55" width="225" height="80" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="375.5" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">kalloc (step 12)</text><text x="375.5" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">needs: a lock for its</text><text x="375.5" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">free list (kmem.lock)</text><line x1="263" y1="95" x2="242" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="511" y="55" width="225" height="80" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="623.5" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">page tables (13-14)</text><text x="623.5" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">needs: kalloc for</text><text x="623.5" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">page-table pages</text><line x1="511" y1="95" x2="490" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="759" y="55" width="225" height="80" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="871.5" y="83.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">interrupts (15-19)</text><text x="871.5" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">needs: locks (a handler and</text><text x="871.5" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">main code share data)</text><line x1="759" y1="95" x2="738" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="500.0" y="160.0" font-size="11.5" fill="#566573" text-anchor="middle">each arrow: &quot;cannot come before&quot;. spinlock is the only one with no arrow out of it</text><text x="330.0" y="200.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="end">criterion</text><text x="420.0" y="200.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">spinlock</text><text x="570.0" y="200.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">kalloc</text><text x="720.0" y="200.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">page tables</text><text x="870.0" y="200.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">interrupts</text><line x1="15" y1="210" x2="985" y2="210" stroke="#bfc9ca" stroke-width="1.5"/><text x="330.0" y="230.0" font-size="11.5" fill="#4d5656" text-anchor="end">depends on nothing that isn&#x27;t here</text><text x="420.0" y="230.0" font-size="12" font-weight="700" fill="#1e8449" text-anchor="middle">✔</text><text x="570.0" y="230.0" font-size="12" fill="#c0392b" text-anchor="middle">✗ (a lock)</text><text x="720.0" y="230.0" font-size="12" fill="#c0392b" text-anchor="middle">✗ (kalloc)</text><text x="870.0" y="230.0" font-size="12" fill="#c0392b" text-anchor="middle">✗ (locks)</text><line x1="15" y1="248" x2="985" y2="248" stroke="#bfc9ca" stroke-width="1.5"/><text x="330.0" y="268.0" font-size="11.5" fill="#4d5656" text-anchor="end">touches no hardware (no new real-PC risk)</text><text x="420.0" y="268.0" font-size="12" font-weight="700" fill="#1e8449" text-anchor="middle">✔</text><text x="570.0" y="268.0" font-size="12" font-weight="700" fill="#1e8449" text-anchor="middle">✔</text><text x="720.0" y="268.0" font-size="12" fill="#c0392b" text-anchor="middle">✗ (CR3)</text><text x="870.0" y="268.0" font-size="12" fill="#c0392b" text-anchor="middle">✗ (APIC)</text><line x1="15" y1="286" x2="985" y2="286" stroke="#bfc9ca" stroke-width="1.5"/><text x="330.0" y="306.0" font-size="11.5" fill="#4d5656" text-anchor="end">C version&#x27;s size (lines)</text><text x="420.0" y="306.0" font-size="12" font-weight="700" fill="#1e8449" text-anchor="middle">✔ 116</text><text x="570.0" y="306.0" font-size="12" font-weight="700" fill="#1e8449" text-anchor="middle">✔ 102</text><text x="720.0" y="306.0" font-size="12" fill="#566573" text-anchor="middle">519</text><text x="870.0" y="306.0" font-size="12" fill="#566573" text-anchor="middle">~660 (4 files)</text><line x1="15" y1="324" x2="985" y2="324" stroke="#bfc9ca" stroke-width="1.5"/><text x="330.0" y="344.0" font-size="11.5" fill="#4d5656" text-anchor="end">everything after it uses it</text><text x="420.0" y="344.0" font-size="12" font-weight="700" fill="#1e8449" text-anchor="middle">✔</text><text x="570.0" y="344.0" font-size="12" fill="#566573" text-anchor="middle"></text><text x="720.0" y="344.0" font-size="12" fill="#566573" text-anchor="middle"></text><text x="870.0" y="344.0" font-size="12" fill="#566573" text-anchor="middle"></text><text x="500.0" y="400.0" font-size="11.5" fill="#566573" text-anchor="middle">kalloc alone would also be small, but the C version&#x27;s kalloc takes kmem.lock: it needs this step first</text></svg>
<!-- /fig:why -->

Four candidates were possible next steps. Three of them **depend on something not yet there**:

- **`kalloc`** (the page allocator) keeps its free list under a lock, `kmem.lock`. Without locks, it would have to be written differently now and changed later.
- **The kernel's page tables** need pages, so they need `kalloc` first.
- **Interrupts** need locks too: an interrupt handler and the code it interrupts share data, such as the console's input buffer.

The spinlock depends on nothing that isn't already there, it touches no hardware (so nothing new can break on the real PC), and the C version is 116 lines. Everything after it uses it. That makes it the natural step 11, and also the **smallest** possible first step, which matters because each step is one 2-hour session.

<div class="check" markdown="1">
**The rule for every step from now on: as small as possible.** Each step brings back only what is needed *now*, and leaves the rest for the step that first needs it. Section 7 lists what was left out of this one, and when it comes.
</div>

## 2. Before (`step-10`)

One CPU runs `main()`, interrupts are off from the first instruction (`cli` in `entry.S`), and the loop at the end polls the keyboards. `printk.cpp` had a comment where the C version's lock would go:

```cpp
// the C version takes pr.lock here so that printk()s from several
// CPUs do not interleave. there is one CPU and no spinlock yet;
// the lock comes back with spinlock.cpp.
```

That is now.

## 3. The idea: what a lock is for

<!-- fig:race -->
<svg viewBox="0 0 1000 360" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="race"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">The problem a lock solves: two CPUs printing at the same time</text><rect x="15" y="60" width="200" height="60" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="115.0" y="86.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU 0</text><text x="115.0" y="102.0" font-size="11.5" fill="#4d5656" text-anchor="middle">printk(&quot;Hello\n&quot;)</text><rect x="15" y="200" width="200" height="60" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="115.0" y="226.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU 1</text><text x="115.0" y="242.0" font-size="11.5" fill="#4d5656" text-anchor="middle">printk(&quot;World\n&quot;)</text><rect x="300" y="120" width="230" height="80" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="415.0" y="148.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">consputc() → screen</text><text x="415.0" y="164.0" font-size="11.5" fill="#4d5656" text-anchor="middle">one character at a time,</text><text x="415.0" y="180.0" font-size="11.5" fill="#4d5656" text-anchor="middle">no idea who is calling</text><line x1="215" y1="90" x2="298" y2="145" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="215" y1="230" x2="298" y2="180" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="600" y="50" width="385" height="90" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="792.5" y="75.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">without a lock</text><text x="792.5" y="91.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">HWeolrllod</text><text x="792.5" y="107.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="792.5" y="123.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">(characters interleave)</text><rect x="600" y="180" width="385" height="90" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="792.5" y="205.0" font-size="13" font-weight="700" fill="#2c3e50" text-anchor="middle">with pr.lock</text><text x="792.5" y="221.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">Hello</text><text x="792.5" y="237.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">World</text><text x="792.5" y="253.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">(one whole line at a time)</text><line x1="530" y1="150" x2="598" y2="100" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="530" y1="170" x2="598" y2="220" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="500.0" y="310.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">at step-11 only CPU 0 runs and interrupts are off, so this cannot happen yet:</text><text x="500.0" y="330.0" font-size="11.5" fill="#566573" text-anchor="middle">the lock is put in place now, and starts mattering at step 25 (other CPUs) and steps 15-19 (interrupts)</text></svg>
<!-- /fig:race -->

A **lock** protects data (or a device) that several CPUs, or a CPU and an interrupt handler, could use at the same time. The code between taking the lock and giving it back is the **critical section**: for each lock, at most one CPU is inside at a time. `printk()` is the classic first example. Without a lock, two CPUs printing at once mix their characters, because `consputc()` handles one character at a time and doesn't know who called.

A **spinlock** waits by *spinning*: it tries again and again in a loop until the lock is free. That wastes CPU time while waiting, so a spinlock is only for short critical sections. (xv6 also has *sleeplocks*, which give up the CPU while waiting; they need processes, step 22.)

**Honest note:** at step-11 the lock prevents nothing. Only CPU 0 runs and interrupts are always off, so no one can compete for it. The lock is put in place now, so that every later piece is written with it from the start. It starts doing real work with interrupts (steps 15–19) and other CPUs (step 25).

### Why one atomic instruction

<!-- fig:tas -->
<svg viewBox="0 0 1000 380" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="test and set"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Why acquire() needs one atomic instruction</text><text x="250.0" y="50.0" font-size="12.5" font-weight="700" fill="#c0392b" text-anchor="middle">naive: check, then set (two steps)</text><rect x="30" y="70" width="210" height="32" rx="4" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="135.0" y="90.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">read locked → 0</text><rect x="260" y="110" width="210" height="32" rx="4" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="365.0" y="130.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">read locked → 0</text><rect x="30" y="150" width="210" height="32" rx="4" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="135.0" y="170.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">set locked = 1, enter</text><rect x="260" y="190" width="210" height="32" rx="4" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="365.0" y="210.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">set locked = 1, enter</text><text x="250.0" y="250.0" font-size="12" font-weight="700" fill="#c0392b" text-anchor="middle">both CPUs are inside: the lock failed</text><text x="130.0" y="62.0" font-size="11.5" font-weight="700" fill="#566573" text-anchor="middle">CPU 0</text><text x="365.0" y="62.0" font-size="11.5" font-weight="700" fill="#566573" text-anchor="middle">CPU 1</text><text x="750.0" y="50.0" font-size="12.5" font-weight="700" fill="#1e8449" text-anchor="middle">xchg: read the old value and write 1, as one step</text><rect x="540" y="70" width="210" height="50" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="645.0" y="91.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU 0: xchg</text><text x="645.0" y="107.0" font-size="11.5" fill="#4d5656" text-anchor="middle">old = 0 → it owns the lock</text><rect x="770" y="130" width="210" height="50" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="875.0" y="151.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU 1: xchg</text><text x="875.0" y="167.0" font-size="11.5" fill="#4d5656" text-anchor="middle">old = 1 → try again</text><rect x="770" y="190" width="210" height="50" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="875.0" y="211.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU 1: xchg …</text><text x="875.0" y="227.0" font-size="11.5" fill="#4d5656" text-anchor="middle">old = 1 → try again (spin)</text><rect x="540" y="250" width="210" height="50" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="645.0" y="271.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU 0: release</text><text x="645.0" y="287.0" font-size="11.5" fill="#4d5656" text-anchor="middle">locked = 0 (a plain mov)</text><rect x="770" y="310" width="210" height="50" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="875.0" y="331.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">CPU 1: xchg</text><text x="875.0" y="347.0" font-size="11.5" fill="#4d5656" text-anchor="middle">old = 0 → now it owns it</text><text x="250.0" y="300.0" font-size="11.5" fill="#566573" text-anchor="middle">the CPU makes xchg with memory atomic:</text><text x="250.0" y="318.0" font-size="11.5" fill="#566573" text-anchor="middle">no other CPU can touch that memory in between</text></svg>
<!-- /fig:tas -->

The obvious code, "if `locked` is 0, set it to 1", is **two** steps, and two CPUs can both read 0 before either writes 1. The fix is an instruction that reads the old value and writes the new one **as one indivisible step**. On x86-64 that is `xchg` with a memory operand: the CPU keeps every other CPU away from that memory until it's done. The code asks the compiler for it with `__atomic_exchange_n`, and the compiled kernel really contains exactly one `xchg`, in `acquire()` (exercise 5).

## 4. What changed

<!-- fig:map_step_11 -->
<svg viewBox="0 0 1000 330" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="files changed from step-10 to step-11"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Change map: step-10 → step-11  (lines added / removed per file; bar length ∝ √lines)</text><text x="300.0" y="50.0" font-size="11.5" font-weight="700" fill="#c0392b" text-anchor="end">removed ←</text><text x="320.0" y="50.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="start">file</text><text x="620.0" y="50.0" font-size="11.5" font-weight="700" fill="#1e8449" text-anchor="start">→ added</text><rect x="305" y="63" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="75.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/spinlock.cpp</text><text x="570.0" y="75.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="64" width="236.0" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="856.0" y="75.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+113</text><rect x="305" y="85" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="97.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/spinlock.h</text><text x="570.0" y="97.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="86" width="139.3768365608266" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="759.4" y="97.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+38</text><rect x="305" y="107" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="119.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/proc.cpp</text><text x="570.0" y="119.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="108" width="135.81947983693644" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="755.8" y="119.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+36</text><rect x="305" y="129" width="10" height="16" rx="2" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="320.0" y="141.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/proc.h</text><text x="570.0" y="141.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">new</text><rect x="615" y="130" width="84.01179851768963" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="704.0" y="141.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+13</text><rect x="305" y="151" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="163.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/printk.cpp</text><text x="570.0" y="163.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="227.802510318128" y="152" width="67.19748968187201" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="222.8" y="163.0" font-size="11.5" fill="#c0392b" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−8</text><rect x="615" y="152" width="134.0037333526346" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="754.0" y="163.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+35</text><rect x="305" y="173" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="185.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/defs.h</text><text x="570.0" y="185.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="174" width="92.54631989129095" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="712.5" y="185.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+16</text><rect x="305" y="195" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="207.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/start.cpp</text><text x="570.0" y="207.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="196" width="63.245009830049625" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="683.2" y="207.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+7</text><rect x="305" y="217" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="229.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/earlytrap.cpp</text><text x="570.0" y="229.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="218" width="58.99858071233723" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="679.0" y="229.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+6</text><rect x="305" y="239" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="251.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">kernel/main.cpp</text><text x="570.0" y="251.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="267.36342002717726" y="240" width="27.636579972822737" height="14" rx="0" fill="#fdedec" stroke="#c0392b" stroke-width="1.5"/><text x="262.4" y="251.0" font-size="11.5" fill="#c0392b" text-anchor="end" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">−1</text><rect x="615" y="240" width="36.59874484093601" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="656.6" y="251.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+2</text><rect x="305" y="261" width="10" height="16" rx="2" fill="#fef9e7" stroke="#b7950b" stroke-width="1.5"/><text x="320.0" y="273.0" font-size="11.5" fill="#4d5656" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">Makefile</text><text x="570.0" y="273.0" font-size="11.5" fill="#7f8c8d" text-anchor="end">changed</text><rect x="615" y="262" width="36.59874484093601" height="14" rx="0" fill="#eafaf1" stroke="#1e8449" stroke-width="1.5"/><text x="656.6" y="273.0" font-size="11.5" fill="#1e8449" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">+2</text><text x="500.0" y="306.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">Total: 10 files, +268 −9 lines (docs and PDFs not counted)</text></svg>
<!-- /fig:map_step_11 -->

| File | | Added | Removed |
|---|---|---:|---:|
| `Makefile` | changed | 2 | 0 |
| `kernel/defs.h` | changed | 16 | 0 |
| `kernel/earlytrap.cpp` | changed | 6 | 0 |
| `kernel/main.cpp` | changed | 2 | 1 |
| `kernel/printk.cpp` | changed | 35 | 8 |
| `kernel/proc.cpp` | new | 36 | 0 |
| `kernel/proc.h` | new | 13 | 0 |
| `kernel/spinlock.cpp` | new | 113 | 0 |
| `kernel/spinlock.h` | new | 38 | 0 |
| `kernel/start.cpp` | changed | 7 | 0 |
| **Total** (10 files) | | **268** | **9** |

### 4.1 `spinlock.h`: the lock, and `LockGuard`

[`kernel/spinlock.h:6–12`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/spinlock.h#L6-L12) (tag `step-11`)

```cpp
struct spinlock {
  uint locked; // Is the lock held?

  // For debugging:
  const char *name; // Name of lock.
  struct cpu *cpu;  // The cpu holding the lock.
};
```

`locked` is the whole lock: 0 free, 1 held. `name` and `cpu` are for debugging and for `holding()`: they record *which* lock it is and *which* CPU has it.

<!-- fig:anatomy -->
<svg viewBox="0 0 1000 470" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="acquire and release"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">acquire() and release(), step by step</text><rect x="15" y="45" width="300" height="110" rx="8" fill="#ebf5fb" stroke="#2874a6" stroke-width="2"/><text x="165.0" y="80.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">struct spinlock</text><text x="165.0" y="96.0" font-size="11.5" fill="#4d5656" text-anchor="middle">locked: 0 free, 1 held</text><text x="165.0" y="112.0" font-size="11.5" fill="#4d5656" text-anchor="middle">name: &quot;pr&quot; (for debugging)</text><text x="165.0" y="128.0" font-size="11.5" fill="#4d5656" text-anchor="middle">cpu: who holds it (for holding())</text><text x="500.0" y="52.0" font-size="13" font-weight="700" fill="#1e8449" text-anchor="middle">acquire(lk)</text><rect x="360" y="65" width="280" height="42" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="500.0" y="90.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">push_off()</text><text x="655.0" y="91.0" font-size="11.5" fill="#4d5656" text-anchor="start">interrupts off (counted)</text><rect x="360" y="117" width="280" height="42" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="500.0" y="142.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">holding(lk)?</text><text x="655.0" y="143.0" font-size="11.5" fill="#4d5656" text-anchor="start">already mine → panic(&quot;acquire&quot;)</text><line x1="500" y1="107" x2="500" y2="116" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="360" y="169" width="280" height="42" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="500.0" y="194.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">while (xchg(locked, 1) != 0) ;</text><text x="655.0" y="195.0" font-size="11.5" fill="#4d5656" text-anchor="start">spin until the old value was 0</text><line x1="500" y1="159" x2="500" y2="168" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="360" y="221" width="280" height="42" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="500.0" y="246.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">lk-&gt;cpu = mycpu()</text><text x="655.0" y="247.0" font-size="11.5" fill="#4d5656" text-anchor="start">remember the owner</text><line x1="500" y1="211" x2="500" y2="220" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><text x="500.0" y="290.0" font-size="13" font-weight="700" fill="#b7950b" text-anchor="middle">release(lk)</text><rect x="360" y="303" width="280" height="32" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="500.0" y="323.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">holding(lk)?</text><text x="655.0" y="324.0" font-size="11.5" fill="#4d5656" text-anchor="start">not mine → panic(&quot;release&quot;)</text><rect x="360" y="343" width="280" height="32" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="500.0" y="363.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">lk-&gt;cpu = nullptr</text><text x="655.0" y="364.0" font-size="11.5" fill="#4d5656" text-anchor="start">forget the owner</text><rect x="360" y="383" width="280" height="32" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="500.0" y="403.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">store(locked, 0)</text><text x="655.0" y="404.0" font-size="11.5" fill="#4d5656" text-anchor="start">a plain mov on x86</text><rect x="360" y="423" width="280" height="32" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="500.0" y="443.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">pop_off()</text><text x="655.0" y="444.0" font-size="11.5" fill="#4d5656" text-anchor="start">interrupts back if they were on</text><rect x="15" y="300" width="300" height="140" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="165.0" y="342.0" font-size="12.5" font-weight="700" fill="#2c3e50" text-anchor="middle">the critical section</text><text x="165.0" y="358.0" font-size="11.5" fill="#4d5656" text-anchor="middle">the code between acquire()</text><text x="165.0" y="374.0" font-size="11.5" fill="#4d5656" text-anchor="middle">and release(): at most one</text><text x="165.0" y="390.0" font-size="11.5" fill="#4d5656" text-anchor="middle">CPU runs it at a time,</text><text x="165.0" y="406.0" font-size="11.5" fill="#4d5656" text-anchor="middle">for each lock</text></svg>
<!-- /fig:anatomy -->

### 4.2 `spinlock.cpp`: `acquire()` and `release()`

[`kernel/spinlock.cpp:27–49`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/spinlock.cpp#L27-L49) (tag `step-11`)

```cpp
acquire(struct spinlock *lk)
{
  push_off(); // disable interrupts to avoid deadlock.
  if (holding(lk))
    panic("acquire");

  // On x86-64, __atomic_exchange_n turns into one xchg instruction,
  // which is atomic (the CPU locks the memory bus or cache line for
  // it) and also a full memory barrier:
  //   mov  $1, %eax
  //   xchg %eax, (%rdi)
  // (on RISC-V it is amoswap.w.aq.)
  //
  // Passing __ATOMIC_ACQUIRE to __atomic_exchange_n tells
  // the compiler and the processor to not move loads or stores
  // past this point, to ensure that the critical section's memory
  // references happen strictly after the lock is acquired.
  while (__atomic_exchange_n(&lk->locked, 1, __ATOMIC_ACQUIRE) != 0)
    ;

  // Record info about lock acquisition for holding() and debugging.
  lk->cpu = mycpu();
}
```

Four things happen, in this order:
1. **`push_off()`**: interrupts off on this CPU (4.3 explains why, and why it is counted).
2. **`holding(lk)`**: if this CPU already holds the lock, spinning would wait for itself forever. That is always a bug, so it panics instead of hanging (exercise 1).
3. **The spin**: `__atomic_exchange_n` writes 1 and returns the old value. Old value 0 means "it was free, and now it is mine"; 1 means "someone has it, try again". `__ATOMIC_ACQUIRE` also stops the compiler and CPU from moving the critical section's memory accesses to before this point.
4. **Record the owner**, for `holding()` and for debugging.

[`kernel/spinlock.cpp:53–74`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/spinlock.cpp#L53-L74) (tag `step-11`)

```cpp
release(struct spinlock *lk)
{
  if (!holding(lk))
    panic("release");

  lk->cpu = nullptr;

  // Release the lock, equivalent to lk->locked = 0.
  //
  // This code doesn't use a C++ assignment, since the standard
  // implies that an assignment might be implemented with
  // multiple store instructions.
  //
  // On x86-64, __atomic_store_n with __ATOMIC_RELEASE is a plain
  // mov: x86 never moves a store before an earlier load or store,
  // so it needs no fence instruction (RISC-V needs fence rw,w).
  // The __ATOMIC_RELEASE argument still stops the compiler from
  // moving the critical section's loads and stores past it.
  __atomic_store_n(&lk->locked, 0, __ATOMIC_RELEASE);

  pop_off();
}
```

Releasing is a store of 0, but done with `__atomic_store_n(..., __ATOMIC_RELEASE)` rather than `lk->locked = 0`. That guarantees that everything written inside the critical section is visible to other CPUs **before** they can see the lock as free. On x86-64 this costs nothing extra: x86 never lets a store overtake an earlier load or store, so the compiler emits a plain `mov` (RISC-V needs a `fence` instruction there). The `__ATOMIC_RELEASE` still matters for the **compiler**, which would otherwise be free to move a store from inside the critical section below the release.

[`kernel/spinlock.cpp:80–83`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/spinlock.cpp#L80-L83) (tag `step-11`)

```cpp
holding(struct spinlock *lk)
{
  return lk->locked && lk->cpu == mycpu();
}
```

### 4.3 `push_off()` and `pop_off()`: interrupts off, counted

<!-- fig:pushoff -->
<svg viewBox="0 0 1000 330" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="push_off pop_off"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">push_off() / pop_off(): interrupts off, counted per CPU</text><rect x="15" y="60" width="180" height="50" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="105.0" y="89.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">start</text><rect x="85" y="190" width="40" height="20" rx="3" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="105.0" y="180.0" font-size="11.5" font-weight="700" fill="#2874a6" text-anchor="middle">noff = 0</text><text x="105.0" y="235.0" font-size="11.5" fill="#4d5656" text-anchor="middle">interrupts: off</text><rect x="212" y="60" width="180" height="50" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="302.0" y="89.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">acquire(A)</text><rect x="282" y="165" width="40" height="45" rx="3" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="302.0" y="155.0" font-size="11.5" font-weight="700" fill="#2874a6" text-anchor="middle">noff = 1</text><text x="302.0" y="235.0" font-size="11.5" fill="#4d5656" text-anchor="middle">push_off: intena = were they on?</text><rect x="409" y="60" width="180" height="50" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="499.0" y="89.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">acquire(B)</text><rect x="479" y="140" width="40" height="70" rx="3" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="499.0" y="130.0" font-size="11.5" font-weight="700" fill="#2874a6" text-anchor="middle">noff = 2</text><text x="499.0" y="235.0" font-size="11.5" fill="#4d5656" text-anchor="middle">push_off: just count</text><rect x="606" y="60" width="180" height="50" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="696.0" y="89.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">release(B)</text><rect x="676" y="165" width="40" height="45" rx="3" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="696.0" y="155.0" font-size="11.5" font-weight="700" fill="#2874a6" text-anchor="middle">noff = 1</text><text x="696.0" y="235.0" font-size="11.5" fill="#4d5656" text-anchor="middle">pop_off: still 1, stay off</text><rect x="803" y="60" width="180" height="50" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="893.0" y="89.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">release(A)</text><rect x="873" y="190" width="40" height="20" rx="3" fill="#ebf5fb" stroke="#2874a6" stroke-width="1.5"/><text x="893.0" y="180.0" font-size="11.5" font-weight="700" fill="#2874a6" text-anchor="middle">noff = 0</text><text x="893.0" y="235.0" font-size="11.5" fill="#4d5656" text-anchor="middle">pop_off: 0 → back on if intena</text><line x1="15" y1="210" x2="985" y2="210" stroke="#7f8c8d" stroke-width="1.5"/><text x="500.0" y="280.0" font-size="11.5" fill="#566573" text-anchor="middle">why turn interrupts off at all: if an interrupt handler on this CPU wanted a lock this CPU already holds,</text><text x="500.0" y="298.0" font-size="11.5" fill="#566573" text-anchor="middle">it would spin forever (deadlock). At step-11 interrupts are already off, so intena is always 0</text></svg>
<!-- /fig:pushoff -->

Why turn interrupts off while holding a spinlock? Suppose the code that reads the console holds `cons.lock`, and a keyboard interrupt arrives **on the same CPU**. The handler wants `cons.lock` too, so it spins, waiting for the lock to be released. But the code that would release it is the code the handler interrupted, which can't continue until the handler returns. The CPU spins forever: a **deadlock**. Turning interrupts off while any spinlock is held makes this impossible.

Locks nest (code may hold lock A and then take lock B), so "interrupts off" is counted per CPU in `noff`. Only when the last lock is released, and only if interrupts were on before the first one (`intena`), are they turned back on:

[`kernel/spinlock.cpp:90–100`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/spinlock.cpp#L90-L100) (tag `step-11`)

```cpp
push_off()
{
  // disable interrupts to prevent an involuntary context
  // switch while using mycpu().
  uint64 flags = intr_off_save();
  int old = (flags & FL_IF) != 0;

  if (mycpu()->noff == 0)
    mycpu()->intena = old;
  mycpu()->noff += 1;
}
```

[`kernel/spinlock.cpp:103–113`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/spinlock.cpp#L103-L113) (tag `step-11`)

```cpp
pop_off()
{
  struct cpu *c = mycpu();
  if (intr_get())
    panic("pop_off - interruptible");
  if (c->noff < 1)
    panic("pop_off");
  c->noff -= 1;
  if (c->noff == 0 && c->intena)
    intr_on();
}
```

`intr_off_save()` (in `x86.h` since the C port) reads the flags and clears the interrupt flag in one instruction sequence (`pushfq; cli; popq`), so no interrupt can slip in between. Bit 9 of RFLAGS (`FL_IF`) is the interrupt flag, the counterpart of RISC-V's `sstatus.SIE`.

### 4.4 `proc.h` / `proc.cpp`: the smallest `struct cpu`

`push_off()` and `holding()` need "this CPU's" state. The C version keeps it in `struct cpu`, in `proc.h`. Its full version also holds the running process and the scheduler's saved registers, which mean nothing yet. So step 11 brings back only the two fields locks use:

[`kernel/proc.h:8–13`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/proc.h#L8-L13) (tag `step-11`)

```cpp
struct cpu {
  int noff;   // Depth of push_off() nesting.
  int intena; // Were interrupts enabled before push_off()?
};

extern struct cpu cpus[NCPU];
```

<!-- fig:mycpu -->
<svg viewBox="0 0 1000 330" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="mycpu"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">mycpu(): which struct cpu belongs to the CPU running this code</text><rect x="15" y="60" width="220" height="70" rx="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/><text x="125.0" y="83.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">GS base register</text><text x="125.0" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">one per CPU (an MSR)</text><text x="125.0" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">start(): w_gsbase(0)</text><rect x="285" y="60" width="200" height="70" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="385.0" y="91.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">cpuid()</text><text x="385.0" y="107.0" font-size="11.5" fill="#4d5656" text-anchor="middle" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">r_gsbase() → 0</text><line x1="235" y1="95" x2="283" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="485" y1="95" x2="533" y2="95" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="535" y="60" width="50" height="70" rx="4" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="560.0" y="83.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">cpus[0]</text><text x="560.0" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">noff</text><text x="560.0" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">intena</text><rect x="591" y="60" width="50" height="70" rx="4" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="616.0" y="83.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">cpus[1]</text><text x="616.0" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">noff</text><text x="616.0" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">intena</text><rect x="647" y="60" width="50" height="70" rx="4" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="672.0" y="83.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">cpus[2]</text><text x="672.0" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">noff</text><text x="672.0" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">intena</text><rect x="703" y="60" width="50" height="70" rx="4" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="728.0" y="83.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">cpus[3]</text><text x="728.0" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">noff</text><text x="728.0" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">intena</text><rect x="759" y="60" width="50" height="70" rx="4" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="784.0" y="83.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">cpus[4]</text><text x="784.0" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">noff</text><text x="784.0" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">intena</text><rect x="815" y="60" width="50" height="70" rx="4" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="840.0" y="83.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">cpus[5]</text><text x="840.0" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">noff</text><text x="840.0" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">intena</text><rect x="871" y="60" width="50" height="70" rx="4" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="896.0" y="83.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">cpus[6]</text><text x="896.0" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">noff</text><text x="896.0" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">intena</text><rect x="927" y="60" width="50" height="70" rx="4" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="952.0" y="83.0" font-size="11.5" font-weight="700" fill="#2c3e50" text-anchor="middle">cpus[7]</text><text x="952.0" y="99.0" font-size="11.5" fill="#4d5656" text-anchor="middle">noff</text><text x="952.0" y="115.0" font-size="11.5" fill="#4d5656" text-anchor="middle">intena</text><text x="760.0" y="152.0" font-size="11.5" fill="#566573" text-anchor="middle">struct cpu cpus[NCPU]: 8 × 8 bytes; only cpus[0] is used at step-11</text><rect x="15" y="190" width="470" height="110" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="250.0" y="225.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">what a wrong value does (exercise 4)</text><text x="250.0" y="241.0" font-size="11.5" fill="#4d5656" text-anchor="middle">w_gsbase(3): uses cpus[3], works quietly</text><text x="250.0" y="257.0" font-size="11.5" fill="#4d5656" text-anchor="middle">w_gsbase(0x40000000): cpus[1073741824] is at 8 GB,</text><text x="250.0" y="273.0" font-size="11.5" fill="#4d5656" text-anchor="middle">past QEMU&#x27;s 512 MB → writes lost → panic: pop_off</text><rect x="515" y="190" width="470" height="110" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="750.0" y="225.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">why GS base</text><text x="750.0" y="241.0" font-size="11.5" fill="#4d5656" text-anchor="middle">RISC-V xv6 keeps the CPU id in the tp register;</text><text x="750.0" y="257.0" font-size="11.5" fill="#4d5656" text-anchor="middle">x86-64 has a register made for per-CPU data.</text><text x="750.0" y="273.0" font-size="11.5" fill="#4d5656" text-anchor="middle">the C version does the same (start.c, mpenter())</text></svg>
<!-- /fig:mycpu -->

[`kernel/proc.cpp:22–26`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/proc.cpp#L22-L26) (tag `step-11`)

```cpp
cpuid()
{
  int id = r_gsbase();
  return id;
}
```

[`kernel/proc.cpp:31–36`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/proc.cpp#L31-L36) (tag `step-11`)

```cpp
mycpu()
{
  int id = cpuid();
  struct cpu *c = &cpus[id];
  return c;
}
```

The file names are the C version's (`proc.h`, `proc.cpp`), so that steps 20–21 grow these same files into the process table and scheduler.

### 4.5 `start.cpp`: give CPU 0 its id

`cpuid()` reads the CPU's number from the **GS base** register (a model-specific register, MSR `0xC0000101`; on RISC-V xv6 this is the `tp` register). The kernel must put the number there itself:

[`kernel/start.cpp:38–42`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/start.cpp#L38-L42) (tag `step-11`)

```cpp
  // keep each CPU's id in its GS base register, for cpuid().
  // UEFI promises nothing about its value. (QEMU's and VirtualBox's
  // firmware leave 0; a wrong value makes mycpu() point outside
  // cpus[]: see the step-11 tutorial.)
  w_gsbase(0);
```

UEFI promises nothing about this register. QEMU's and VirtualBox's firmware happen to leave 0, so the kernel would *work* there without this line, which is exactly the kind of bug that only shows up on a real PC. Exercise 4 shows what a wrong value does.

### 4.6 `printk.cpp`: the first lock in use

[`kernel/printk.cpp:17–20`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/printk.cpp#L17-L20) (tag `step-11`)

```cpp
// lock to avoid interleaving concurrent printk's.
static struct {
  struct spinlock lock;
} pr;
```

[`kernel/printk.cpp:124–143`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/printk.cpp#L124-L143) (tag `step-11`)

```cpp
// Print to the console.
int
printk(const char *fmt, ...)
{
  va_list ap;

  va_start(ap, fmt);
  if (panicking == 0) {
    LockGuard guard(pr.lock); // released at the closing brace
    vprintk(fmt, ap);
  } else {
    // a panic may have happened while this CPU held pr.lock (in
    // acquire() itself, say): taking it again would only panic
    // again. print without it.
    vprintk(fmt, ap);
  }
  va_end(ap);

  return 0;
}
```

`printk()` takes `pr.lock` for the whole message, so one call's output is never split by another's. The exception is **during a panic**: `panic()` sets `panicking = 1` before printing, because the panic may have happened while this CPU held `pr.lock` (for example, `acquire()` itself panicking). Taking the lock again would just panic again, and the message would never appear. The C version has the same rule.

The C version wrote this as `if (panicking == 0) acquire(...)` at the top and `if (panicking == 0) release(...)` at the bottom. The C++ version moves the printing loop into `vprintk()` and uses a **`LockGuard`** on the locking path:

<!-- fig:guard -->
<svg viewBox="0 0 1000 330" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="LockGuard"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">LockGuard: the lock is released when the guard goes out of scope</text><rect x="15" y="50" width="470" height="230" rx="8" fill="#ffffff" stroke="#566573" stroke-width="2"/><text x="35.0" y="78.0" font-size="12" fill="#2c3e50" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">if (panicking == 0) {</text><text x="35.0" y="98.0" font-size="12" fill="#2c3e50" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  LockGuard guard(pr.lock);  // acquire</text><text x="35.0" y="118.0" font-size="12" fill="#2c3e50" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  vprintk(fmt, ap);</text><text x="35.0" y="138.0" font-size="12" fill="#2c3e50" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">}                            // release</text><text x="35.0" y="158.0" font-size="12" fill="#2c3e50" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none"></text><text x="35.0" y="178.0" font-size="12" fill="#2c3e50" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">{</text><text x="35.0" y="198.0" font-size="12" fill="#2c3e50" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  LockGuard g(lk);</text><text x="35.0" y="218.0" font-size="12" fill="#2c3e50" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  if (bad) return;  // released here too</text><text x="35.0" y="238.0" font-size="12" fill="#2c3e50" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">  ...</text><text x="35.0" y="258.0" font-size="12" fill="#2c3e50" text-anchor="start" font-family="'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace" style="font-variant-ligatures:none">}                  // and here</text><rect x="520" y="50" width="465" height="105" rx="8" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="752.5" y="82.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">C (by hand)</text><text x="752.5" y="98.5" font-size="11.5" fill="#4d5656" text-anchor="middle">acquire(&amp;pr.lock);</text><text x="752.5" y="114.5" font-size="11.5" fill="#4d5656" text-anchor="middle">... every return must release first ...</text><text x="752.5" y="130.5" font-size="11.5" fill="#4d5656" text-anchor="middle">release(&amp;pr.lock);</text><rect x="520" y="175" width="465" height="105" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="752.5" y="207.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">C++ (RAII)</text><text x="752.5" y="223.5" font-size="11.5" fill="#4d5656" text-anchor="middle">constructor: acquire()</text><text x="752.5" y="239.5" font-size="11.5" fill="#4d5656" text-anchor="middle">destructor: release(), on every way out</text><text x="752.5" y="255.5" font-size="11.5" fill="#4d5656" text-anchor="middle">copying is deleted: no double release</text><text x="500.0" y="310.0" font-size="11.5" fill="#566573" text-anchor="middle">RAII: Resource Acquisition Is Initialization; the same idea as std::lock_guard, without the standard library</text></svg>
<!-- /fig:guard -->

[`kernel/spinlock.h:27–38`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/spinlock.h#L27-L38) (tag `step-11`)

```cpp
class LockGuard {
public:
  explicit LockGuard(struct spinlock &lk) : lk(lk) { acquire(&lk); }
  ~LockGuard() { release(&lk); }

  // a copy would release the lock twice.
  LockGuard(const LockGuard &) = delete;
  LockGuard &operator=(const LockGuard &) = delete;

private:
  struct spinlock &lk;
};
```

`LockGuard` is the main C++ idea of this step. Its constructor calls `acquire()`, its destructor calls `release()`, and C++ runs the destructor on **every** way out of the block: the closing brace, `return`, `break`. A forgotten `release()` on an early return, a common bug in C, can't happen. Copying is deleted, because two guards for one lock would release it twice. This is the RAII pattern ("resource acquisition is initialization"), the same as `std::lock_guard` in the standard library, which a kernel can't use.

`printkinit()` names the lock, and `main()` calls it right after `consoleinit()`, before the first `printk()`, as in the C version.

### 4.7 `earlytrap.cpp`: a bug found while testing

<!-- fig:trapfix -->
<svg viewBox="0 0 1000 300" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="earlytrap fix"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">A bug found while testing: an exception inside printk()</text><rect x="15" y="50" width="180" height="60" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="105.0" y="76.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">printk()</text><text x="105.0" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">takes pr.lock</text><rect x="225" y="50" width="180" height="60" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="315.0" y="76.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">exception</text><text x="315.0" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">(e.g. a bad pointer)</text><rect x="435" y="50" width="180" height="60" rx="8" fill="#eef2f7" stroke="#34495e" stroke-width="2"/><text x="525.0" y="76.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">earlytrap()</text><text x="525.0" y="92.0" font-size="11.5" fill="#4d5656" text-anchor="middle">calls printk()</text><line x1="195" y1="80" x2="223" y2="80" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="405" y1="80" x2="433" y2="80" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="660" y="25" width="325" height="55" rx="8" fill="#fdedec" stroke="#c0392b" stroke-width="2"/><text x="822.5" y="48.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">before the fix</text><text x="822.5" y="64.5" font-size="11.5" fill="#4d5656" text-anchor="middle">acquire: already held → &quot;panic: acquire&quot;</text><rect x="660" y="95" width="325" height="55" rx="8" fill="#eafaf1" stroke="#1e8449" stroke-width="2"/><text x="822.5" y="118.5" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">after the fix</text><text x="822.5" y="134.5" font-size="11.5" fill="#4d5656" text-anchor="middle">&quot;CPU exception 6 (invalid opcode)&quot;</text><line x1="615" y1="70" x2="658" y2="52" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><line x1="615" y1="90" x2="658" y2="122" stroke="#7f8c8d" stroke-width="2" marker-end="url(#ae)"/><rect x="15" y="180" width="970" height="90" rx="8" fill="#fef9e7" stroke="#b7950b" stroke-width="2"/><text x="500.0" y="213.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">the fix: earlytrap() sets panicking = 1 first</text><text x="500.0" y="229.0" font-size="11.5" fill="#4d5656" text-anchor="middle">it ends in panic() anyway; printk() takes no lock while panicking (the C version&#x27;s rule)</text><text x="500.0" y="245.0" font-size="11.5" fill="#4d5656" text-anchor="middle">tested by putting ud2 (an invalid instruction) inside printk(): reproduced, then fixed</text></svg>
<!-- /fig:trapfix -->

Taking a lock in `printk()` created a new way to fail. If a CPU exception happens **inside** `printk()`, while `pr.lock` is held (say a bad pointer reaches `consputc()`), `earlytrap()` calls `printk()` to report it, `acquire()` finds the lock already held by this CPU, and the kernel panics with `panic: acquire`. The real report, the one you'd photograph on the real PC, is lost.

This was reproduced before fixing it: with an `ud2` (an always-invalid instruction) placed inside `printk()`, the screen showed only `panic: acquire`. The fix is one line at the top of `earlytrap()`, which ends in `panic()` anyway:

[`kernel/earlytrap.cpp:54–60`](https://github.com/jonghoon-ryu/xv6-x86_64/blob/step-11/kernel/earlytrap.cpp#L54-L60) (tag `step-11`)

```cpp
earlytrap(uint64 *f)
{
  // this ends in panic() anyway. say so now, so that printk() does
  // not take pr.lock: the exception may have happened inside
  // printk(), with pr.lock held, and acquire() would then panic
  // with "acquire" instead of this report. (step 11)
  panicking = 1;
```

With it, the same test prints `CPU exception 6 (invalid opcode)` with its `rip`.

## 5. C and C++, side by side

| C version (`v0.2-x86_64-c`) | C++ (`step-11`) | Why |
|---|---|---|
| `int holding(...)` | `bool holding(...)` | it is a yes/no answer |
| `char *name`, `initlock(..., char *)` | `const char *name` | the names are string literals, which C++ makes `const` |
| `lk->cpu = 0` | `lk->cpu = nullptr` | a typed null pointer |
| `acquire(&pr.lock)` … `release(&pr.lock)` by hand | `LockGuard guard(pr.lock);` | released on every way out of the block |
| `printk()` with the loop inside | `printk()` + `vprintk()` | so that one path can hold a guard and the other not |
| `struct cpu` with `proc`, `context`, `noff`, `intena` | only `noff`, `intena` | the rest needs processes |

`acquire()` and `release()` stay free functions taking a pointer, as in C. Making them member functions (`lk.acquire()`) would look more C++-like, but every later file brought back from the C version calls `acquire(&x.lock)`. Keeping that form means those files stay easy to compare with the book.

## 6. After

Nothing changes on the screen except the banner, and that is expected: no one competes for any lock yet.

![step-11 in QEMU (make qemu USB=1): typed "hello" on the USB keyboard behind a hub](/assets/image/xv6-tut-step-11-step11-qemu.png)

![step-11 in VirtualBox (2 CPUs configured, only CPU 0 runs): typed "hello"](/assets/image/xv6-tut-step-11-step11-vbox.png)

| Where | Result |
|---|---|
| QEMU, PS/2 keyboard (`make qemu`) | ✅ boots, "hello" typed |
| QEMU, USB keyboard behind a hub (`make qemu USB=1`) | ✅ boots, "hello" typed |
| VirtualBox, 2 CPUs (`make vbox`) | ✅ boots, "hello" typed |
| **real PC (barebone)** | ✅ boots, USB keyboard types (2026-10-16, photo below) |

### The real PC (barebone), 2026-10-16

![step-11 on the real PC: "ok, step 11 seems to be working !!" typed on the USB keyboard](/assets/image/xv6-tut-step-11-step11-realpc.jpg)

Same machine and same USB tree as in [step 10](/xv6/tutorial/step-10/#the-real-pc-barebone-2026-10-07). The keyboard on port 6 types, so `printk()` taking `pr.lock` works on real hardware too. **Step 11 is done.**

## 7. Deliberately left out

<!-- fig:notyet -->
<svg viewBox="0 0 1000 250" style="font-variant-ligatures:none;width:100%;max-width:1000px;height:auto;display:block;margin:1rem auto;" font-family="'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif" role="img" aria-label="not in step 11"><defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs><text x="500.0" y="22.0" font-size="14" font-weight="700" fill="#2c3e50" text-anchor="middle">Deliberately left out of step 11 (the smallest step that works)</text><rect x="15" y="50" width="330" height="38" rx="4" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="180.0" y="73.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">cons.lock (console.cpp)</text><text x="360.0" y="74.0" font-size="11.5" fill="#4d5656" text-anchor="start">nothing else touches cons until interrupts</text><text x="985.0" y="74.0" font-size="12" font-weight="700" fill="#2874a6" text-anchor="end">steps 18-19</text><rect x="15" y="96" width="330" height="38" rx="4" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="180.0" y="119.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">struct cpu: proc, context</text><text x="360.0" y="120.0" font-size="11.5" fill="#4d5656" text-anchor="start">no processes yet</text><text x="985.0" y="120.0" font-size="12" font-weight="700" fill="#2874a6" text-anchor="end">steps 20-21</text><rect x="15" y="142" width="330" height="38" rx="4" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="180.0" y="165.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">other CPUs set their GS base</text><text x="360.0" y="166.0" font-size="11.5" fill="#4d5656" text-anchor="start">only CPU 0 runs (mpenter())</text><text x="985.0" y="166.0" font-size="12" font-weight="700" fill="#2874a6" text-anchor="end">step 25</text><rect x="15" y="188" width="330" height="38" rx="4" fill="#f4f6f7" stroke="#7f8c8d" stroke-width="2"/><text x="180.0" y="211.0" font-size="12" font-weight="700" fill="#2c3e50" text-anchor="middle">sleeplock</text><text x="360.0" y="212.0" font-size="11.5" fill="#4d5656" text-anchor="start">a lock that sleeps instead of spinning</text><text x="985.0" y="212.0" font-size="12" font-weight="700" fill="#2874a6" text-anchor="end">step 22</text></svg>
<!-- /fig:notyet -->

These are all in the C version and all come back, each in the step that first needs it. Adding them now would make this step bigger without changing anything you could observe.

## 8. Exercises

Every expected result below was produced by actually running the change in QEMU at `step-11`. Make each change on top of `step-11`, run `make qemu`, look at the output, then undo it (`git checkout kernel/`).

<div class="tip" markdown="1">
**Exercise 1: take the same lock twice.** In `main()`, right after `printkinit();`, add:

```cpp
static struct spinlock lk;
initlock(&lk, "test");
acquire(&lk);
acquire(&lk);
```

(and `#include "spinlock.h"` before `defs.h` at the top). **Expected:** right after the loader's `starting kernel`, the only kernel output is

```
panic: acquire
```

The banner never appears, because this happens before it. **Why:** the second `acquire()` finds `holding(&lk)` true. Without that check it would spin forever, waiting for itself, a silent hang.
</div>

<div class="tip" markdown="1">
**Exercise 2: release a lock you don't hold.** Same place: `initlock(&lk, "test"); release(&lk);`. **Expected:**

```
panic: release
```
</div>

<div class="tip" markdown="1">
**Exercise 3: watch `LockGuard` and `noff`.** After `printkinit();` (with `#include "spinlock.h"` and `#include "proc.h"` before `defs.h`):

```cpp
static struct spinlock lk;
initlock(&lk, "test");
{
  LockGuard guard(lk);
  printk("inside the block: noff %d, holding %d\n", mycpu()->noff, holding(&lk));
}
printk("after the block:  noff %d, holding %d\n", mycpu()->noff, holding(&lk));
```

**Expected** (before the banner):

```
inside the block: noff 1, holding 1
after the block:  noff 0, holding 0
```

**Why 1, not 2:** `printk()` takes `pr.lock` too, which makes `noff` 2, but the arguments are evaluated *before* `printk()` is called. Try adding a `return;` inside the block in a small test function: the lock is still released.
</div>

<div class="tip" markdown="1">
**Exercise 4: the GS base register.** (a) In `start.cpp`, comment out `w_gsbase(0);` and in `main()` add right after `consoleinit();`:

```cpp
printk("GS base: %p\n", (void *)r_gsbase());
```

**Expected** in QEMU *and* in VirtualBox: `GS base: 0x0000000000000000`. Both firmwares leave 0, which is why this line looks unnecessary there. On the real PC it is unknown: try it there (`make usb.img`, boot it, read the screen).

(b) Change it to `w_gsbase(3);` and print `cpuid()`, `&cpus[0]` and `mycpu()` (`#include "proc.h"`). **Expected:**

```
cpuid() 3, &cpus[0] 0x00000000001171c0, mycpu() 0x00000000001171d8
```

Everything works, quietly using `cpus[3]`, which is 3 × 8 bytes further.

(c) Now `w_gsbase(0x40000000);`. **Expected:**

```
cpuid() 1073741824, &cpus[0] 0x00000000001171c0, mycpu() 0x00000002001171c0
panic: pop_off
```

`mycpu()` now points at 8 GB, far beyond QEMU's 512 MB of RAM. The firmware's page tables map that address, but no memory is there: `push_off()`'s `noff += 1` is lost, so when `release()` calls `pop_off()` it finds `noff < 1` and panics. A wrong per-CPU pointer shows up as a confusing message far from its cause, which is why `start()` sets the register explicitly.
</div>

<div class="tip" markdown="1">
**Exercise 5: find the atomic instruction.**

```sh
make && grep -n xchg kernel/kernel.asm
```

**Expected:** exactly one line, `xchg %eax,(%rbx)`, inside `acquire()`. Then look at `release()` in `kernel/kernel.asm`: the store is a plain `movl $0x0,(%rbx)`, with no fence instruction (section 4.2 explains why).
</div>

## 9. How to spend the 2 hours

| Time | What |
|---|---|
| 20 min | Book (rev5) §7.1 Races, §7.2 Code: Locks, §7.3 Code: Using locks, §7.4 Deadlock and lock ordering, §7.5 Locks and interrupts. If there is time, §7.6 (memory ordering: the `__ATOMIC_ACQUIRE`/`RELEASE` of section 4.2) and §8.5 (mycpu). Skip §7.7 Sleep locks (step 22) |
| 30 min | Read `kernel/spinlock.cpp` next to the C version (`git show v0.2-x86_64-c:kernel/spinlock.c`), then `spinlock.h` and the `printk()` change. Use the figures in sections 3–4 |
| 30 min | Exercises 1, 3 and 5 (the most telling ones). 2 and 4 if there's time |
| 20 min | Boot `usb.img` on the real PC and type. This is what finishes the step |
| 20 min | The self-check below; note questions for later |

## 10. Self-check

<details markdown="1">
<summary>1. At step-11 only one CPU runs and interrupts are off. What does pr.lock actually prevent right now?</summary>

Nothing. No other CPU or interrupt handler can call `printk()` at the same time. The lock is there so that the code is already correct when interrupts (steps 15–19) and other CPUs (step 25) arrive. Its checks (`holding()` in `acquire()` and `release()`) do already catch bugs: exercises 1 and 2.
</details>

<details markdown="1">
<summary>2. Why can't acquire() be written as "while (lk->locked) ; lk->locked = 1;"?</summary>

Two CPUs can both see `locked == 0` and both set it to 1: two separate steps leave a gap between the check and the set. `xchg` does both as one step that no other CPU can interrupt.
</details>

<details markdown="1">
<summary>3. Why does acquire() turn interrupts off, and why is it counted instead of just cli/sti?</summary>

If an interrupt handler on the same CPU tried to take a lock that CPU holds, it would spin forever (deadlock). Counting (`noff`) is needed because locks nest: releasing the inner lock must not turn interrupts back on while the outer one is still held. `intena` remembers whether they were on before the first lock.
</details>

<details markdown="1">
<summary>4. release() on x86-64 compiles to a plain mov. Why is __atomic_store_n still needed?</summary>

The CPU won't reorder it, but the **compiler** could: without the release ordering, it may move stores from inside the critical section past the unlocking store. `__ATOMIC_RELEASE` forbids that. (On RISC-V it also makes the CPU emit a fence.)
</details>

<details markdown="1">
<summary>5. Why does printk() not take pr.lock during a panic, and why did earlytrap() need the same treatment?</summary>

The panic (or exception) may have happened while this CPU held `pr.lock`. Taking it again makes `acquire()` panic with "acquire", and the original message is lost. `panic()` sets `panicking` before printing; step 11 makes `earlytrap()` do the same, because it also always ends in a panic.
</details>

<details markdown="1">
<summary>6. What does LockGuard give that acquire()/release() by hand doesn't?</summary>

The release happens in the destructor, which C++ runs on every way out of the scope, including early returns. So a missing `release()` can't happen. Copying is deleted, so one lock can't be released twice by two copies.
</details>

<details markdown="1">
<summary>7. Why does QEMU work even without w_gsbase(0)?</summary>

Its firmware (OVMF) happens to leave GS base at 0, and so does VirtualBox's. UEFI doesn't promise that, so on another machine `cpuid()` could return anything (exercise 4c shows the result).
</details>

## 11. Next

Step 12, `kalloc.cpp`: the page allocator, a free list of 4 KB pages built from the UEFI memory map, protected by `kmem.lock`, the first lock that will really be shared once there are several CPUs.

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-10/">step-10</a></span><span><a href="/xv6/tutorial/">Tutorial</a> →</span></div>
