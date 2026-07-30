---
layout: default
title: Weekend Study Plan
permalink: /learning-cs/os/study-plan/
---
<style>
.progress-box {
  display: flex;
  align-items: center;
  gap: 0.75rem;
  margin: 0 0 1.5rem;
  font-size: 0.95rem;
  color: #555;
}
.progress-bar-track {
  flex: 1;
  max-width: 280px;
  height: 6px;
  border-radius: 4px;
  background: #e2e2e2;
  overflow: hidden;
}
.progress-bar-fill {
  height: 100%;
  width: 0%;
  background: #3a7d44;
  transition: width 0.2s ease;
}
.session-check {
  display: inline-flex;
  align-items: center;
  gap: 0.4rem;
  font-size: 0.85rem;
  color: #777;
  cursor: pointer;
  user-select: none;
  margin: 0.2rem 0 0.6rem;
}
.session-check input {
  cursor: pointer;
}
.session.done h3 {
  color: #999;
  text-decoration: line-through;
  text-decoration-color: #bbb;
}
.session.done {
  opacity: 0.6;
}
</style>

# xv6 × OSTEP × Lecture series — Weekend Study Plan

A 15-session curriculum for building real OS understanding, sized for **~6 hours per weekend** (day job permitting).

<div style="margin-top: 60px;"></div>

## Method

The primary source is always **the xv6 source tree** — read the actual mechanism first, in code, before anything else.

A companion **xv6 lecture series** ([playlist](https://www.youtube.com/watch?v=xieHeMeu1HQ&list=PLbtzT1TYeoMj_YvECDl0YqipVZqucZHXs), episode 1: "xv6 #1: Introduction and Overview") gives a fast walkthrough before or alongside the code, standing in for the slower "read the book chapter first" step.

**OSTEP's homework simulators** (run from the [OSTEP homework page](https://pages.cs.wisc.edu/~remzi/OSTEP/Homework/homework.html)) cover what xv6 deliberately leaves out — MLFQ, lottery scheduling, page replacement, journaling, RAID.

The **OSTEP book** itself is a last-resort fallback, opened only when code + video + simulator together still leave something unclear. This is deliberately *not* the traditional order (read the chapter, then do the homework) — code comes first, always.

*Note: I could confirm the lecture playlist's first episode but not the full episode listing (YouTube blocks that kind of scraping), so sessions below just say "matching episode" — worth a five-minute skim of the playlist to pencil in which episode covers which topic.*

<div style="margin-top: 60px;"></div>

## Weekly rhythm (~6h budget)

- **30–40 min** — watch the matching lecture episode(s) for orientation
- **~3.5–4h** — trace the xv6 mechanism together, function by function
- **1–1.5h** — run the paired OSTEP simulator, compare it against what xv6 actually does
- **15–20 min** — write personal notes on what surprised you

If a weekend only gives 3–4 hours, protect the trace — let the simulator and video slip to a weekday evening rather than cutting the code reading short. Better to skip a weekend outright than compress two sessions into one.

<div style="margin-top: 100px;"></div>

## Sessions

<div class="progress-box">
  <span>Progress: <span id="progress-count">0 / 15</span></span>
  <span class="progress-bar-track"><span class="progress-bar-fill" id="progress-fill"></span></span>
</div>

<div class="session" data-session="1" markdown="1">

### 1. The process, from the outside

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="1"> mark complete</label>

Get fluent with xv6's tooling and see what a process looks like before opening any kernel internals.
- **xv6:** `make qemu`, `make qemu-gdb`, directory layout · `user/init.c`, `user/sh.c` (fork+exec+wait from user space) · `user/user.h` (the full syscall surface)
- **Video:** "Introduction and Overview" episode
- **OSTEP:** `process-run.py` — process intro / scheduling basics

</div>

<div class="session" data-session="2" markdown="1">

### 2. Boot: machine mode to supervisor mode

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="2"> mark complete</label>

One clean pass on power-on to the first process's memory being set up.
- **xv6:** `kernel/entry.S` (per-hart stack) → `kernel/start.c` (M-mode config, mret to S-mode) → `kernel/main.c` (subsystem init order, hart 0 vs. others)
- **Video:** matching boot/entry episode, if the playlist has one
- **OSTEP:** none — no homework covers boot specifically

</div>

<div class="session" data-session="3" markdown="1">

### 3. Traps & the syscall path

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="3"> mark complete</label>

How a user-mode `ecall` becomes a kernel function call and back — the mechanism underneath every syscall from here on.
- **xv6:** `kernel/trampoline.S` (uservec / userret) · `kernel/trap.c` (usertrap, prepare_return) · `kernel/syscall.c` (argument fetch, dispatch table)
- **Video:** matching traps/syscalls episode
- **OSTEP:** none — Limited Direct Execution has no OSTEP homework, mechanism only
- **If stuck:** OSTEP ch. 6, "Mechanism: Limited Direct Execution"

</div>

<div class="session" data-session="4" markdown="1">

### 4. Scheduling — xv6's round robin vs. the real thing

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="4"> mark complete</label>

See how little xv6 does to schedule processes, then use the simulators to explore what it's choosing not to do.
- **xv6:** `kernel/proc.c` (scheduler, yield, sleep/wakeup) · `kernel/swtch.S` (the register-level context switch) · `kernel/trap.c` (clockintr preemption via yield)
- **Video:** matching scheduler episode
- **OSTEP:** `scheduler.py`, `mlfq.py`, `lottery.py`, `multi.py`

</div>

<div class="session" data-session="5" markdown="1">

### 5. fork / exec / wait / exit, end to end

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="5"> mark complete</label>

Close the process-lifecycle loop — verify the fork() mechanics carefully, line by line.
- **xv6:** `kernel/proc.c` (kfork, kwait, kexit, reparent) · `kernel/exec.c` (ELF loading into a fresh address space) · `kernel/vm.c` (uvmcopy)
- **Video:** matching fork/exec episode
- **OSTEP:** revisit `process-run.py` against what actually happens underneath now

</div>

<div class="session" data-session="6" markdown="1">

### 6. Physical memory & page-table mechanics

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="6"> mark complete</label>

xv6 jumps straight to paging. See the base/bounds and segmentation steps it skipped before reading how it actually allocates and maps.
- **xv6:** `kernel/kalloc.c` (physical page free-list) · `kernel/vm.c` (walk, mappages, kvminit)
- **Video:** matching memory-management episode
- **OSTEP:** `relocation.py`, `segmentation.py`, `freespace.py`

</div>

<div class="session" data-session="7" markdown="1">

### 7. Address translation, deep dive

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="7"> mark complete</label>

The real three-level Sv39 walk, and the TRAMPOLINE/TRAPFRAME double-mapping trick that makes trap entry possible.
- **xv6:** `kernel/riscv.h` (PTE layout, Sv39 constants) · `kernel/vm.c` (walk, traced instruction by instruction) · why TRAMPOLINE/TRAPFRAME must map identically in every page table
- **Video:** matching paging/translation episode
- **OSTEP:** `paging-linear-translate.py`, `paging-multilevel-translate.py`, `mem.c`

</div>

<div class="session" data-session="8" markdown="1">

### 8. What xv6 leaves out: swap & page replacement

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="8"> mark complete</label>

xv6 never pages memory out to disk. Understand the simplification, and what real systems do instead.
- **xv6:** `kernel/proc.c` (growproc, uvmalloc, uvmdealloc) · `kernel/trap.c` (vmfault lazy-allocation path) · `kernel/exec.c` (the user stack guard page)
- **OSTEP:** `paging-policy.py` — page replacement, pure simulator since xv6 has none

</div>

<div class="session" data-session="9" markdown="1">

### 9. Locks

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="9"> mark complete</label>

Ground lock theory in xv6's two real primitives and the specific races they exist to prevent.
- **xv6:** `kernel/spinlock.c` (acquire/release, push_off/pop_off and why) · `kernel/sleeplock.c` (when a spinlock isn't the right tool)
- **Video:** matching locking episode
- **OSTEP:** threads-intro `x86.py`, thread-API `main-*.c` programs

</div>

<div class="session" data-session="10" markdown="1">

### 10. sleep()/wakeup() as xv6's condition variable

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="10"> mark complete</label>

Compare xv6's channel-based sleep/wakeup against textbook condition variables — same problem, different shape.
- **xv6:** `kernel/proc.c` (sleep, wakeup, the lost-wakeup problem it avoids) · `kernel/pipe.c` (a worked example) · `kernel/bio.c` (buffer cache waiters)
- **OSTEP:** CV `main-*.c` programs, semaphore code, `vector-*.c` (concurrency bugs)

</div>

<div class="session" data-session="11" markdown="1">

### 11. Interrupts & device drivers

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="11"> mark complete</label>

The other half of trap.c: external interrupts instead of syscalls, and what a minimal real driver looks like.
- **xv6:** `kernel/kernelvec.S`, `trap.c` (devintr) · `kernel/plic.c` (interrupt routing) · `kernel/uart.c`, `console.c`, `virtio_disk.c`
- **Video:** matching interrupts/drivers episode
- **If stuck:** OSTEP ch. 36, "I/O Devices"

</div>

<div class="session" data-session="12" markdown="1">

### 12. Buffer cache & on-disk layout

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="12"> mark complete</label>

How xv6 turns a raw disk into a structured filesystem, and where a disk scheduler or RAID layer would sit underneath it.
- **xv6:** `kernel/bio.c` (buffer cache) · `kernel/fs.c` (superblock, inode table, bitmap)
- **Video:** matching file-system intro episode
- **OSTEP:** `disk.py`, `raid.py`

</div>

<div class="session" data-session="13" markdown="1">

### 13. Files, directories & layout policy

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="13"> mark complete</label>

xv6's flat, no-locality layout against a real implementation's directory structure and FFS-style placement.
- **xv6:** `kernel/fs.c` (directories, namei, path lookup) · `kernel/stat.h`, `kernel/file.c` (the in-memory open-file layer)
- **OSTEP:** `vsfs.py`, `ffs.py`

</div>

<div class="session" data-session="14" markdown="1">

### 14. Crash consistency — and actually crashing it

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="14"> mark complete</label>

This repo already has crash-recovery test infrastructure — use it. Read the log, then break the system on purpose and watch it recover.
- **xv6:** `kernel/log.c` (write-ahead logging) · `test-xv6.py` crash / log modes · `user/dorphan.c`, `forphan.c`, `logstress.c`, `sync.c`
- **Video:** matching logging/crash-recovery episode, if covered
- **OSTEP:** `fsck.py`, `lfs.py` — alternative approaches to the same problem

</div>

<div class="session" data-session="15" markdown="1">

### 15. Capstone — one request, every layer

<label class="session-check"><input type="checkbox" class="session-checkbox" data-session="15"> mark complete</label>

Pick something as ordinary as `ls | grep foo` typed at the shell, and narrate it end to end without help: parsing and pipe(), fork/exec, the scheduler, the trap path, the console driver, the file system read, the buffer cache. If the whole story holds together, the plan worked.

</div>

<div style="margin-top: 100px;"></div>

## Pacing

Fifteen weekends at one-per-week is ~4 months; expect longer given the day job — that's fine, the order matters more than the calendar. If a weekend gets fully eaten by work, skip it rather than cramming two sessions into the next one.

<script>
(function () {
  var STORAGE_KEY = 'os-study-plan-progress';

  function load() {
    try { return JSON.parse(localStorage.getItem(STORAGE_KEY) || '{}'); } catch (e) { return {}; }
  }
  function save(state) {
    try { localStorage.setItem(STORAGE_KEY, JSON.stringify(state)); } catch (e) {}
  }

  document.addEventListener('DOMContentLoaded', function () {
    var boxes = Array.prototype.slice.call(document.querySelectorAll('.session-checkbox'));
    var countEl = document.getElementById('progress-count');
    var fillEl = document.getElementById('progress-fill');
    var total = boxes.length;
    var state = load();

    function render() {
      var done = 0;
      boxes.forEach(function (cb) {
        var id = cb.getAttribute('data-session');
        var isDone = !!state[id];
        cb.checked = isDone;
        var wrap = cb.closest('.session');
        if (wrap) wrap.classList.toggle('done', isDone);
        if (isDone) done++;
      });
      if (countEl) countEl.textContent = done + ' / ' + total;
      if (fillEl) fillEl.style.width = (total ? (done / total) * 100 : 0) + '%';
    }

    boxes.forEach(function (cb) {
      cb.addEventListener('change', function () {
        state[cb.getAttribute('data-session')] = cb.checked;
        save(state);
        render();
      });
    });

    render();
  });
})();
</script>
