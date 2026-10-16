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

@@FIG step11 why@@

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

@@FIG step11 race@@

A **lock** protects data (or a device) that several CPUs, or a CPU and an interrupt handler, could use at the same time. The code between taking the lock and giving it back is the **critical section**: for each lock, at most one CPU is inside at a time. `printk()` is the classic first example. Without a lock, two CPUs printing at once mix their characters, because `consputc()` handles one character at a time and doesn't know who called.

A **spinlock** waits by *spinning*: it tries again and again in a loop until the lock is free. That wastes CPU time while waiting, so a spinlock is only for short critical sections. (xv6 also has *sleeplocks*, which give up the CPU while waiting; they need processes, step 22.)

**Honest note:** at step-11 the lock prevents nothing. Only CPU 0 runs and interrupts are always off, so no one can compete for it. The lock is put in place now, so that every later piece is written with it from the start. It starts doing real work with interrupts (steps 15–19) and other CPUs (step 25).

### Why one atomic instruction

@@FIG step11 tas@@

The obvious code, "if `locked` is 0, set it to 1", is **two** steps, and two CPUs can both read 0 before either writes 1. The fix is an instruction that reads the old value and writes the new one **as one indivisible step**. On x86-64 that is `xchg` with a memory operand: the CPU keeps every other CPU away from that memory until it's done. The code asks the compiler for it with `__atomic_exchange_n`, and the compiled kernel really contains exactly one `xchg`, in `acquire()` (exercise 5).

## 4. What changed

@@FIG maps map_step_11@@

@@STAT step-10 step-11@@

### 4.1 `spinlock.h`: the lock, and `LockGuard`

@@CODE step-11 | kernel/spinlock.h | ^struct spinlock \{ | ^\};@@

`locked` is the whole lock: 0 free, 1 held. `name` and `cpu` are for debugging and for `holding()`: they record *which* lock it is and *which* CPU has it.

@@FIG step11 anatomy@@

### 4.2 `spinlock.cpp`: `acquire()` and `release()`

@@CODE step-11 | kernel/spinlock.cpp | ^acquire\(struct spinlock \*lk\) | ^}@@

Four things happen, in this order:
1. **`push_off()`**: interrupts off on this CPU (4.3 explains why, and why it is counted).
2. **`holding(lk)`**: if this CPU already holds the lock, spinning would wait for itself forever. That is always a bug, so it panics instead of hanging (exercise 1).
3. **The spin**: `__atomic_exchange_n` writes 1 and returns the old value. Old value 0 means "it was free, and now it is mine"; 1 means "someone has it, try again". `__ATOMIC_ACQUIRE` also stops the compiler and CPU from moving the critical section's memory accesses to before this point.
4. **Record the owner**, for `holding()` and for debugging.

@@CODE step-11 | kernel/spinlock.cpp | ^release\(struct spinlock \*lk\) | ^}@@

Releasing is a store of 0, but done with `__atomic_store_n(..., __ATOMIC_RELEASE)` rather than `lk->locked = 0`. That guarantees that everything written inside the critical section is visible to other CPUs **before** they can see the lock as free. On x86-64 this costs nothing extra: x86 never lets a store overtake an earlier load or store, so the compiler emits a plain `mov` (RISC-V needs a `fence` instruction there). The `__ATOMIC_RELEASE` still matters for the **compiler**, which would otherwise be free to move a store from inside the critical section below the release.

@@CODE step-11 | kernel/spinlock.cpp | ^holding\(struct spinlock \*lk\) | ^}@@

### 4.3 `push_off()` and `pop_off()`: interrupts off, counted

@@FIG step11 pushoff@@

Why turn interrupts off while holding a spinlock? Suppose the code that reads the console holds `cons.lock`, and a keyboard interrupt arrives **on the same CPU**. The handler wants `cons.lock` too, so it spins, waiting for the lock to be released. But the code that would release it is the code the handler interrupted, which can't continue until the handler returns. The CPU spins forever: a **deadlock**. Turning interrupts off while any spinlock is held makes this impossible.

Locks nest (code may hold lock A and then take lock B), so "interrupts off" is counted per CPU in `noff`. Only when the last lock is released, and only if interrupts were on before the first one (`intena`), are they turned back on:

@@CODE step-11 | kernel/spinlock.cpp | ^push_off\(\) | ^}@@

@@CODE step-11 | kernel/spinlock.cpp | ^pop_off\(\) | ^}@@

`intr_off_save()` (in `x86.h` since the C port) reads the flags and clears the interrupt flag in one instruction sequence (`pushfq; cli; popq`), so no interrupt can slip in between. Bit 9 of RFLAGS (`FL_IF`) is the interrupt flag, the counterpart of RISC-V's `sstatus.SIE`.

### 4.4 `proc.h` / `proc.cpp`: the smallest `struct cpu`

`push_off()` and `holding()` need "this CPU's" state. The C version keeps it in `struct cpu`, in `proc.h`. Its full version also holds the running process and the scheduler's saved registers, which mean nothing yet. So step 11 brings back only the two fields locks use:

@@CODE step-11 | kernel/proc.h | ^struct cpu \{ | ^extern struct cpu@@

@@FIG step11 mycpu@@

@@CODE step-11 | kernel/proc.cpp | ^cpuid\(\) | ^}@@

@@CODE step-11 | kernel/proc.cpp | ^mycpu\(\) | ^}@@

The file names are the C version's (`proc.h`, `proc.cpp`), so that steps 20–21 grow these same files into the process table and scheduler.

### 4.5 `start.cpp`: give CPU 0 its id

`cpuid()` reads the CPU's number from the **GS base** register (a model-specific register, MSR `0xC0000101`; on RISC-V xv6 this is the `tp` register). The kernel must put the number there itself:

@@CODE step-11 | kernel/start.cpp | ^  // keep each CPU's id | ^  w_gsbase\(0\);@@

UEFI promises nothing about this register. QEMU's and VirtualBox's firmware happen to leave 0, so the kernel would *work* there without this line, which is exactly the kind of bug that only shows up on a real PC. Exercise 4 shows what a wrong value does.

### 4.6 `printk.cpp`: the first lock in use

@@CODE step-11 | kernel/printk.cpp | ^// lock to avoid interleaving | ^\} pr;@@

@@CODE step-11 | kernel/printk.cpp | ^// Print to the console. | ^}@@

`printk()` takes `pr.lock` for the whole message, so one call's output is never split by another's. The exception is **during a panic**: `panic()` sets `panicking = 1` before printing, because the panic may have happened while this CPU held `pr.lock` (for example, `acquire()` itself panicking). Taking the lock again would just panic again, and the message would never appear. The C version has the same rule.

The C version wrote this as `if (panicking == 0) acquire(...)` at the top and `if (panicking == 0) release(...)` at the bottom. The C++ version moves the printing loop into `vprintk()` and uses a **`LockGuard`** on the locking path:

@@FIG step11 guard@@

@@CODE step-11 | kernel/spinlock.h | ^class LockGuard \{ | ^\};@@

`LockGuard` is the main C++ idea of this step. Its constructor calls `acquire()`, its destructor calls `release()`, and C++ runs the destructor on **every** way out of the block: the closing brace, `return`, `break`. A forgotten `release()` on an early return, a common bug in C, can't happen. Copying is deleted, because two guards for one lock would release it twice. This is the RAII pattern ("resource acquisition is initialization"), the same as `std::lock_guard` in the standard library, which a kernel can't use.

`printkinit()` names the lock, and `main()` calls it right after `consoleinit()`, before the first `printk()`, as in the C version.

### 4.7 `earlytrap.cpp`: a bug found while testing

@@FIG step11 trapfix@@

Taking a lock in `printk()` created a new way to fail. If a CPU exception happens **inside** `printk()`, while `pr.lock` is held (say a bad pointer reaches `consputc()`), `earlytrap()` calls `printk()` to report it, `acquire()` finds the lock already held by this CPU, and the kernel panics with `panic: acquire`. The real report, the one you'd photograph on the real PC, is lost.

This was reproduced before fixing it: with an `ud2` (an always-invalid instruction) placed inside `printk()`, the screen showed only `panic: acquire`. The fix is one line at the top of `earlytrap()`, which ends in `panic()` anyway:

@@CODE step-11 | kernel/earlytrap.cpp | ^earlytrap\(uint64 \*f\) | ^  panicking = 1;@@

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

@@IMG xv6-tut-step-11-step11-qemu.png step-11 in QEMU (make qemu USB=1): typed "hello" on the USB keyboard behind a hub@@

@@IMG xv6-tut-step-11-step11-vbox.png step-11 in VirtualBox (2 CPUs configured, only CPU 0 runs): typed "hello"@@

| Where | Result |
|---|---|
| QEMU, PS/2 keyboard (`make qemu`) | ✅ boots, "hello" typed |
| QEMU, USB keyboard behind a hub (`make qemu USB=1`) | ✅ boots, "hello" typed |
| VirtualBox, 2 CPUs (`make vbox`) | ✅ boots, "hello" typed |
| **real PC (barebone)** | ✅ boots, USB keyboard types (2026-10-16, photo below) |

### The real PC (barebone), 2026-10-16

@@IMG xv6-tut-step-11-step11-realpc.jpg step-11 on the real PC: a test line typed on the USB keyboard appears on the screen@@

Same machine and same USB tree as in [step 10](/xv6/tutorial/step-10/#the-real-pc-barebone-2026-10-07). The keyboard on port 6 types, so `printk()` taking `pr.lock` works on real hardware too. **Step 11 is done.**

## 7. Deliberately left out

@@FIG step11 notyet@@

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
