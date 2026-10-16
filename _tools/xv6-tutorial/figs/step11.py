from svg import D


def why():
    d = D(1000, 420, "Why spinlock is step 11: what each candidate needs, and what needs it")
    cands = [
        ("spinlock", ["needs: nothing new", "~100 lines, no hardware"], "new"),
        ("kalloc (step 12)", ["needs: a lock for its", "free list (kmem.lock)"], "gray"),
        ("page tables (13-14)", ["needs: kalloc for", "page-table pages"], "gray"),
        ("interrupts (15-19)", ["needs: locks (a handler and", "main code share data)"], "gray"),
    ]
    for i, (t, ls, k) in enumerate(cands):
        x = 15 + i * 248
        d.box(x, 55, 225, 80, t, ls, k, size=12.5)
        if i:
            d.arrow(x, 95, x - 21, 95)
    d.text(500, 160, "each arrow: \"cannot come before\". spinlock is the only one with no arrow out of it", 11.5, color="#566573")
    rows = [("depends on nothing that isn't here", "✔", "✗ (a lock)", "✗ (kalloc)", "✗ (locks)"),
            ("touches no hardware (no new real-PC risk)", "✔", "✔", "✗ (CR3)", "✗ (APIC)"),
            ("C version's size (lines)", "✔ 116", "✔ 102", "519", "~660 (4 files)"),
            ("everything after it uses it", "✔", "", "", "")]
    d.text(330, 200, "criterion", 12, True, "end", "#2c3e50")
    for i, h in enumerate(["spinlock", "kalloc", "page tables", "interrupts"]):
        d.text(420 + i * 150, 200, h, 12, True, color="#2c3e50")
    for j, (c, *v) in enumerate(rows):
        y = 230 + j * 38
        d.line(15, y - 20, 985, y - 20)
        d.text(330, y, c, 11.5, False, "end")
        for i, x in enumerate(v):
            d.text(420 + i * 150, y, x, 12, x.startswith("✔"), color="#1e8449" if x.startswith("✔") else "#c0392b" if x.startswith("✗") else "#566573")
    d.text(500, 400, "kalloc alone would also be small, but the C version's kalloc takes kmem.lock: it needs this step first", 11.5, color="#566573")
    return d.svg("why spinlock first")


def race():
    d = D(1000, 360, "The problem a lock solves: two CPUs printing at the same time")
    d.box(15, 60, 200, 60, "CPU 0", ["printk(\"Hello\\n\")"], "hw", size=12)
    d.box(15, 200, 200, 60, "CPU 1", ["printk(\"World\\n\")"], "hw", size=12)
    d.box(300, 120, 230, 80, "consputc() → screen", ["one character at a time,", "no idea who is calling"], "base", size=12)
    d.arrow(215, 90, 298, 145); d.arrow(215, 230, 298, 180)
    d.box(600, 50, 385, 90, "without a lock", ["HWeolrllod", "", "(characters interleave)"], "del", size=13, mono=True)
    d.box(600, 180, 385, 90, "with pr.lock", ["Hello", "World", "(one whole line at a time)"], "new", size=13, mono=True)
    d.arrow(530, 150, 598, 100); d.arrow(530, 170, 598, 220)
    d.text(500, 310, "at step-11 only CPU 0 runs and interrupts are off, so this cannot happen yet:", 11.5, True, color="#2c3e50")
    d.text(500, 330, "the lock is put in place now, and starts mattering at step 25 (other CPUs) and steps 15-19 (interrupts)", 11.5, color="#566573")
    return d.svg("race")


def tas():
    d = D(1000, 380, "Why acquire() needs one atomic instruction")
    d.text(250, 50, "naive: check, then set (two steps)", 12.5, True, color="#c0392b")
    rows = [("CPU 0", "read locked → 0", None), ("CPU 1", None, "read locked → 0"), ("CPU 0", "set locked = 1, enter", None), ("CPU 1", None, "set locked = 1, enter")]
    for i, (who, a, b) in enumerate(rows):
        y = 70 + i * 40
        d.box(30 if a else 260, y, 210, 32, a or b, [], "del" if i >= 2 else "base", size=11.5, rx=4)
    d.text(250, 250, "both CPUs are inside: the lock failed", 12, True, color="#c0392b")
    d.text(130, 62, "CPU 0", 11.5, True, color="#566573"); d.text(365, 62, "CPU 1", 11.5, True, color="#566573")
    d.text(750, 50, "xchg: read the old value and write 1, as one step", 12.5, True, color="#1e8449")
    d.box(540, 70, 210, 50, "CPU 0: xchg", ["old = 0 → it owns the lock"], "new", size=11.5)
    d.box(770, 130, 210, 50, "CPU 1: xchg", ["old = 1 → try again"], "chg", size=11.5)
    d.box(770, 190, 210, 50, "CPU 1: xchg …", ["old = 1 → try again (spin)"], "chg", size=11.5)
    d.box(540, 250, 210, 50, "CPU 0: release", ["locked = 0 (a plain mov)"], "base", size=11.5)
    d.box(770, 310, 210, 50, "CPU 1: xchg", ["old = 0 → now it owns it"], "new", size=11.5)
    d.text(250, 300, "the CPU makes xchg with memory atomic:", 11.5, color="#566573")
    d.text(250, 318, "no other CPU can touch that memory in between", 11.5, color="#566573")
    return d.svg("test and set")


def anatomy():
    d = D(1000, 470, "acquire() and release(), step by step")
    d.box(15, 45, 300, 110, "struct spinlock", ["locked: 0 free, 1 held", "name: \"pr\" (for debugging)", "cpu: who holds it (for holding())"], "mem", size=12.5)
    steps_a = [("push_off()", "interrupts off (counted)"), ("holding(lk)?", "already mine → panic(\"acquire\")"),
               ("while (xchg(locked, 1) != 0) ;", "spin until the old value was 0"), ("lk->cpu = mycpu()", "remember the owner")]
    d.text(500, 52, "acquire(lk)", 13, True, color="#1e8449")
    for i, (t, s) in enumerate(steps_a):
        y = 65 + i * 52
        d.box(360, y, 280, 42, t, [], "new", size=11.5, mono=True)
        d.text(655, y + 26, s, 11.5, anchor="start")
        if i:
            d.arrow(500, y - 10, 500, y - 1)
    steps_r = [("holding(lk)?", "not mine → panic(\"release\")"), ("lk->cpu = nullptr", "forget the owner"),
               ("store(locked, 0)", "a plain mov on x86"), ("pop_off()", "interrupts back if they were on")]
    d.text(500, 290, "release(lk)", 13, True, color="#b7950b")
    for i, (t, s) in enumerate(steps_r):
        y = 303 + i * 40
        d.box(360, y, 280, 32, t, [], "chg", size=11.5, mono=True)
        d.text(655, y + 21, s, 11.5, anchor="start")
    d.box(15, 300, 300, 140, "the critical section", ["the code between acquire()", "and release(): at most one", "CPU runs it at a time,", "for each lock"], "white", size=12.5)
    return d.svg("acquire and release")


def pushoff():
    d = D(1000, 330, "push_off() / pop_off(): interrupts off, counted per CPU")
    seq = [("start", 0, "interrupts: off"), ("acquire(A)", 1, "push_off: intena = were they on?"), ("acquire(B)", 2, "push_off: just count"),
           ("release(B)", 1, "pop_off: still 1, stay off"), ("release(A)", 0, "pop_off: 0 → back on if intena")]
    for i, (t, n, s) in enumerate(seq):
        x = 15 + i * 197
        d.box(x, 60, 180, 50, t, [], "base" if i == 0 else ("new" if "acquire" in t else "chg"), size=12, mono=True)
        h = 20 + n * 25
        d.rect(x + 70, 210 - h, 40, h, "mem", rx=3)
        d.text(x + 90, 200 - h, f"noff = {n}", 11.5, True, color="#2874a6")
        d.text(x + 90, 235, s, 11.5)
    d.line(15, 210, 985, 210, color="#7f8c8d")
    d.text(500, 280, "why turn interrupts off at all: if an interrupt handler on this CPU wanted a lock this CPU already holds,", 11.5, color="#566573")
    d.text(500, 298, "it would spin forever (deadlock). At step-11 interrupts are already off, so intena is always 0", 11.5, color="#566573")
    return d.svg("push_off pop_off")


def mycpu():
    d = D(1000, 330, "mycpu(): which struct cpu belongs to the CPU running this code")
    d.box(15, 60, 220, 70, "GS base register", ["one per CPU (an MSR)", "start(): w_gsbase(0)"], "hw", size=12)
    d.box(285, 60, 200, 70, "cpuid()", ["r_gsbase() → 0"], "base", size=12, mono=True)
    d.arrow(235, 95, 283, 95); d.arrow(485, 95, 533, 95)
    for i in range(8):
        x = 535 + i * 56
        d.box(x, 60, 50, 70, f"cpus[{i}]", ["noff", "intena"], "new" if i == 0 else "gray", size=11.5, rx=4)
    d.text(760, 152, "struct cpu cpus[NCPU]: 8 × 8 bytes; only cpus[0] is used at step-11", 11.5, color="#566573")
    d.box(15, 190, 470, 110, "what a wrong value does (exercise 4)", ["w_gsbase(3): uses cpus[3], works quietly", "w_gsbase(0x40000000): cpus[1073741824] is at 8 GB,", "past QEMU's 512 MB → writes lost → panic: pop_off"], "del", size=12)
    d.box(515, 190, 470, 110, "why GS base", ["RISC-V xv6 keeps the CPU id in the tp register;", "x86-64 has a register made for per-CPU data.", "the C version does the same (start.c, mpenter())"], "white", size=12)
    return d.svg("mycpu")


def guard():
    d = D(1000, 330, "LockGuard: the lock is released when the guard goes out of scope")
    d.box(15, 50, 470, 230, "", [], "white")
    lines = ["if (panicking == 0) {", "  LockGuard guard(pr.lock);  // acquire", "  vprintk(fmt, ap);", "}                            // release",
             "", "{", "  LockGuard g(lk);", "  if (bad) return;  // released here too", "  ...", "}                  // and here"]
    for i, ln in enumerate(lines):
        d.text(35, 78 + i * 20, ln.replace(" ", "\u00a0"), 12, False, "start", "#2c3e50", mono=True)  # keep the indentation
    d.box(520, 50, 465, 105, "C (by hand)", ["acquire(&pr.lock);", "... every return must release first ...", "release(&pr.lock);"], "gray", size=12, mono=False)
    d.box(520, 175, 465, 105, "C++ (RAII)", ["constructor: acquire()", "destructor: release(), on every way out", "copying is deleted: no double release"], "new", size=12)
    d.text(500, 310, "RAII: Resource Acquisition Is Initialization; the same idea as std::lock_guard, without the standard library", 11.5, color="#566573")
    return d.svg("LockGuard")


def trapfix():
    d = D(1000, 300, "A bug found while testing: an exception inside printk()")
    d.box(15, 50, 180, 60, "printk()", ["takes pr.lock"], "base", size=12)
    d.box(225, 50, 180, 60, "exception", ["(e.g. a bad pointer)"], "del", size=12)
    d.box(435, 50, 180, 60, "earlytrap()", ["calls printk()"], "base", size=12)
    d.arrow(195, 80, 223, 80); d.arrow(405, 80, 433, 80)
    d.box(660, 25, 325, 55, "before the fix", ["acquire: already held → \"panic: acquire\""], "del", size=12)
    d.box(660, 95, 325, 55, "after the fix", ["\"CPU exception 6 (invalid opcode)\""], "new", size=12)
    d.arrow(615, 70, 658, 52); d.arrow(615, 90, 658, 122)
    d.box(15, 180, 970, 90, "the fix: earlytrap() sets panicking = 1 first", ["it ends in panic() anyway; printk() takes no lock while panicking (the C version's rule)",
                                                                            "tested by putting ud2 (an invalid instruction) inside printk(): reproduced, then fixed"], "chg", size=12)
    return d.svg("earlytrap fix")


def notyet():
    d = D(1000, 250, "Deliberately left out of step 11 (the smallest step that works)")
    items = [("cons.lock (console.cpp)", "nothing else touches cons until interrupts", "steps 18-19"),
             ("struct cpu: proc, context", "no processes yet", "steps 20-21"),
             ("other CPUs set their GS base", "only CPU 0 runs (mpenter())", "step 25"),
             ("sleeplock", "a lock that sleeps instead of spinning", "step 22")]
    for i, (a, b, c) in enumerate(items):
        y = 50 + i * 46
        d.box(15, y, 330, 38, a, [], "gray", size=12, rx=4)
        d.text(360, y + 24, b, 11.5, anchor="start")
        d.text(985, y + 24, c, 12, True, "end", "#2874a6")
    return d.svg("not in step 11")
