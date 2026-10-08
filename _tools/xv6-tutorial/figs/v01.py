from svg import D


def boot():
    d = D(1000, 330, "Booting: who puts the kernel in memory and gets to main()")
    d.text(20, 58, "xv6-riscv (QEMU virt)", 12.5, True, "start", "#2c3e50")
    d.box(20, 70, 190, 70, "QEMU", ["-kernel loads the kernel", "at 0x80000000"], "hw")
    d.box(250, 70, 190, 70, "entry.S", ["machine mode", "a stack per CPU"], "base")
    d.box(480, 70, 190, 70, "start.c", ["machine → supervisor", "(mret)"], "base")
    d.box(710, 70, 190, 70, "main.c", ["kinit, kvminit, …", "scheduler()"], "base")
    for x in (210, 440, 670):
        d.arrow(x, 105, x + 38, 105)
    d.text(20, 178, "xv6-x86_64 (UEFI PC)", 12.5, True, "start", "#2c3e50")
    d.box(20, 190, 150, 110, "UEFI firmware", ["64-bit mode", "paging on", "memory = physical"], "hw")
    d.box(200, 190, 230, 110, "boot/loader.c (new)", ["reads kernel, fs.img", "ACPI, screen, memory map", "ExitBootServices", "→ _entry(bootinfo)"], "new")
    d.box(460, 190, 150, 110, "entry.S", ["at 0x100000", "sets a stack", "calls start()"], "chg")
    d.box(640, 190, 150, 110, "start.c", ["copies bootinfo", "sets EFER.NXE", "GS base = 0"], "chg")
    d.box(820, 190, 160, 110, "main.c", ["+ acpiinit", "+ ioapic, lapic", "+ startothers"], "chg")
    for a, b in ((170, 200), (430, 460), (610, 640), (790, 820)):
        d.arrow(a, 245, b - 2, 245)
    d.legend(20, 322, (("new", "new"), ("chg", "changed"), ("del", "deleted")))
    return d.svg("boot paths of RISC-V and x86-64")


def memmap():
    d = D(1000, 500, "Physical memory (x86-64 version, QEMU with 512 MB)")
    d.memmap(140, 60, 260, [
        ("LAPIC (per-CPU interrupt unit)", 34, "hw", "0xFEE00000"),
        ("IOAPIC (device interrupts)", 34, "hw", "0xFEC00000"),
        ("… (above PHYSTOP: unused)", 50, "gray", "PHYSTOP = 128MB"),
        ("free pages → kalloc()", 110, "mem", None),
        ("fs.img (RAM disk), bootinfo", 40, "new", None),
        ("free pages → kalloc()", 60, "mem", "end"),
        ("kernel text, data, bss", 50, "base", "0x00100000"),
        ("low memory: firmware, AP start page", 40, "gray", "0x00000000"),
    ])
    d.box(470, 70, 500, 120, "What changed in kinit()", [
        "RISC-V: everything from end to PHYSTOP is free",
        "x86-64: only the 'conventional' (free) regions of the",
        "UEFI memory map between end and PHYSTOP are freed",
        "a PC's RAM has holes, and the firmware uses some of it"], "chg", size=12.5)
    d.box(470, 220, 500, 100, "Devices have no fixed addresses", [
        "RISC-V virt: UART 0x10000000, PLIC 0x0c000000 (fixed)",
        "x86-64: LAPIC and IOAPIC addresses come from ACPI (MADT)",
        "the COM1 serial port is not memory but I/O port 0x3F8"], "hw", size=12.5)
    d.box(470, 350, 500, 80, "No disk", [
        "instead of a virtio disk (a virtual device), the loader puts",
        "fs.img in memory and ramdisk.c reads and writes it as a disk"], "new", size=12.5)
    return d.svg("physical memory layout of the x86-64 version")


def vmtop():
    d = D(1000, 400, "The top of the address space: the x86-64 version adds a CPUTABLES page")
    d.memmap(120, 70, 300, [("TRAMPOLINE (trampoline.S)", 40, "base", None), ("TRAPFRAME (p->trapframe)", 40, "base", None),
                            ("…", 30, "gray", None), ("user memory (text, data, stack, heap)", 80, "mem", "0")], title="xv6-riscv: user page table")
    d.memmap(600, 70, 300, [("TRAMPOLINE (trampoline.S)", 40, "chg", None), ("CPUTABLES (IDT, GDT, TSS)", 40, "new", None),
                            ("TRAPFRAME (p->trapframe)", 40, "chg", None), ("…", 30, "gray", None), ("user memory", 80, "mem", "0")], title="xv6-x86_64: user page table")
    d.box(120, 336, 780, 50, "", ["On a trap the CPU reads the IDT, GDT and TSS. So that it can read them while a user page table is active,",
                                   "the page holding them is mapped at the same address (just below TRAMPOLINE) in every page table"], "white", size=12)
    return d.svg("top of the address space")


def trap():
    d = D(1000, 450, "A system call from a user program: from int $64 to usertrap()")
    d.box(20, 60, 200, 70, "user program", ["usys.S: rax = number", "int $64"], "base")
    d.box(270, 60, 220, 70, "CPU (hardware)", ["switches to the TSS.rsp0 stack,", "pushes ss, rsp, rflags, cs, rip"], "hw")
    d.box(540, 60, 200, 70, "trampoline.S: uvec64", ["pushes err (0)", "and trapno (64)"], "new")
    d.box(790, 60, 190, 70, "uservec", ["pushes the 15", "general registers, cld"], "chg")
    d.arrow(220, 95, 268, 95); d.arrow(490, 95, 538, 95); d.arrow(740, 95, 788, 95)
    d.box(790, 170, 190, 90, "uservec (cont.)", ["GS = cpu id", "cr3 = kernel page table", "rsp = kernel stack", "call usertrap"], "chg")
    d.arrow(885, 130, 885, 168)
    d.box(540, 170, 200, 90, "usertrap() (trap.c)", ["lidt(kidt): kernel IDT", "trapno == 64 → syscall()", "rip already after the int"], "chg")
    d.arrow(790, 215, 742, 215)
    d.text(190, 182, "TRAPFRAME page (p->trapframe)", 12, True, "middle", "#2c3e50")
    y = 192
    for lab, h, k in [("kernel_cr3, kernel_sp, kernel_trap, kernel_hartid", 30, "gray"), ("r15 … rax  (pushed by uservec)", 34, "chg"),
                      ("trapno, err  (pushed by the vector stub)", 26, "new"), ("rip, cs, rflags, rsp, ss  (pushed by the CPU)", 34, "hw")]:
        d.box(30, y, 320, h, "", [lab], k, size=12, rx=0)
        y += h
    d.text(356, y + 4, "← TSS.rsp0 = end of TRAPFRAME", 10.5, False, "start", "#566573")
    d.text(30, y + 30, "addresses grow downward here; pushes fill it from the bottom up", 10.5, False, "start")
    d.box(20, 360, 960, 70, "Compared with RISC-V", [
        "RISC-V: ecall → uservec (from stvec) finds TRAPFRAME through sscratch and stores each register (the CPU saves only sepc)",
        "x86-64: the CPU pushes part of the state itself, so pointing the stack (rsp0) at the end of TRAPFRAME fills it by pushes alone"], "white", size=12)
    return d.svg("system call path and trapframe")


def acpi():
    d = D(1000, 300, "Finding the interrupt controllers: following the ACPI tables (acpi.c)")
    d.box(20, 70, 160, 70, "RSDP", ["the loader gets it", "from UEFI → bootinfo"], "new")
    d.box(230, 70, 160, 70, "XSDT", ["list of all", "table addresses"], "hw")
    d.box(440, 70, 200, 70, "MADT (\"APIC\")", ["CPUs and", "interrupt controllers"], "hw")
    d.arrow(180, 105, 228, 105); d.arrow(390, 105, 438, 105)
    d.box(700, 40, 280, 44, "LAPIC entries → apicids[] (CPU list)", [], "new", size=12)
    d.box(700, 92, 280, 44, "IOAPIC entry → ioapicaddr", [], "new", size=12)
    d.box(700, 144, 280, 44, "ISO entries → IRQ overrides (ISA → GSI)", [], "new", size=12)
    for y in (62, 114, 166):
        d.arrow(640, 105, 698, y)
    d.box(20, 200, 960, 80, "Compared with RISC-V", [
        "RISC-V virt: the PLIC (device interrupts) and CLINT (timer) sit at fixed addresses, so constants in memlayout.h suffice",
        "x86-64: addresses and CPU counts differ per machine. lapic.c and ioapic.c come from the old x86 xv6 (xv6-public), made 64-bit"], "white", size=12)
    return d.svg("finding LAPIC and IOAPIC through ACPI")


def ap():
    d = D(1000, 320, "Starting the other CPUs (startothers, entryother.S)")
    steps = [("BSP: main.c", ["copies entryother to", "a page below 1 MB,", "fills stack, cr3, entry"], "chg"),
             ("lapicstartap()", ["INIT, SIPI signals", "(LAPIC commands)"], "hw"),
             ("AP: 16-bit", ["starts in real mode", "loads a GDT"], "new"),
             ("AP: 32-bit", ["protected mode", "PAE, EFER.LME"], "new"),
             ("AP: 64-bit", ["long mode", "kernel cr3, stack"], "new"),
             ("mpenter()", ["GS = id", "apstarted = 1", "→ main()"], "chg")]
    x = 15
    for i, (t, ls, k) in enumerate(steps):
        d.box(x, 70, 150, 100, t, ls, k, size=12)
        if i:
            d.arrow(x - 15, 120, x - 1, 120)
        x += 165
    d.box(15, 205, 970, 90, "Why so much work", [
        "An x86 CPU wakes up in 16-bit real mode, like a 1978 8086 (only the first CPU, started by UEFI, is already 64-bit).",
        "So the other CPUs start in code below 1 MB and climb to 32-bit and then 64-bit mode themselves.",
        "On RISC-V virt every hart starts together in the same kernel code"], "white", size=12)
    return d.svg("AP start-up sequence")


def regmap():
    d = D(1000, 520, "Same job, different hardware: riscv.h ↔ x86.h (only what xv6 uses)")
    rows = [("page table base", "satp  (w_satp)", "CR3  (w_cr3)"), ("trap handler address", "stvec  (w_stvec)", "IDT  (lidt)"),
            ("trap cause", "scause  (r_scause)", "vector number trapno (pushed by stub)"), ("faulting address", "stval  (r_stval)", "CR2  (r_cr2)"),
            ("where the trap happened", "sepc  (r_sepc)", "rip in the trapframe (pushed by CPU)"), ("CPU number", "tp  (r_tp, w_tp)", "GS base MSR  (r_gsbase, wrmsr)"),
            ("interrupts on/off", "sstatus.SIE  (intr_on/off)", "RFLAGS.IF  (sti / cli)"), ("system call instruction", "ecall", "int $64"),
            ("return to user", "sret", "iretq"), ("flush the TLB", "sfence.vma", "rewrite CR3  (sfence_vma)"), ("timer", "stimecmp", "LAPIC timer")]
    d.text(160, 52, "what", 12, True); d.text(450, 52, "RISC-V (riscv.h)", 12, True); d.text(790, 52, "x86-64 (x86.h)", 12, True)
    y = 62
    for what, rv, x in rows:
        d.box(20, y, 280, 36, "", [what], "white", size=12.5, rx=3)
        d.box(310, y, 280, 36, "", [rv], "gray", size=12.5, mono=True, rx=3)
        d.arrow(592, y + 18, 618, y + 18)
        d.box(620, y, 360, 36, "", [x], "new", size=12, mono=True, rx=3)
        y += 40
    d.text(500, y + 12, "Some RISC-V registers have no x86 counterpart: trap cause and location are pushed on the stack by the CPU and the stubs", 11.5)
    return d.svg("RISC-V and x86-64 register mapping")


def pagewalk():
    d = D(1000, 420, "Virtual → physical: Sv39 (3 levels) and x86-64 (4 levels)")
    d.text(20, 58, "RISC-V Sv39", 12.5, True, "start", "#2c3e50")
    d.bits(150, 66, 820, 39, [(38, 30, "L2 (9 bits)", "chg"), (29, 21, "L1 (9 bits)", "chg"), (20, 12, "L0 (9 bits)", "chg"), (11, 0, "page offset (12)", "mem")], h=34)
    d.text(20, 160, "x86-64", 12.5, True, "start", "#2c3e50")
    d.bits(150, 168, 820, 48, [(47, 39, "PML4 (L3)", "new"), (38, 30, "PDPT (L2)", "chg"), (29, 21, "PD (L1)", "chg"), (20, 12, "PT (L0)", "chg"), (11, 0, "offset (12)", "mem")], h=34)
    d.box(20, 240, 470, 160, "What changed in walk() (vm.c)", ["for (level = 2 …)  →  for (level = 3 …)", "PX(level, va): 9 bits each, one more level", "",
                                                                "intermediate PTEs also get W | U:", "x86 checks W and U at every level,", "so only the leaf PTE decides"], "chg", size=12.5)
    d.box(510, 240, 470, 160, "MAXVA stays at RISC-V's 2³⁸", ["to keep the user address layout unchanged,", "xv6 uses up to 2³⁸ instead of x86's 2⁴⁷", "",
                                                            "→ the top PML4 index is always 0", "  (virtual address bits 47:39 are 0)", "TRAMPOLINE = MAXVA − 4096"], "white", size=12.5)
    return d.svg("page table levels compared")


def ptebits():
    d = D(1000, 250, "x86-64 PTE (64 bits): the bits xv6 uses")
    d.bits(60, 60, 900, 0, [(63, 63, "NX", "new", 3), (62, 52, "(unused)", "gray", 5), (51, 12, "physical page number (PTE2PA)", "mem", 14), (11, 11, "", "gray", 1),
                            (10, 10, "X*", "chg", 2), (9, 9, "R*", "chg", 2), (8, 5, "(unused)", "gray", 4), (4, 4, "PCD", "hw", 2), (3, 3, "PWT", "hw", 2),
                            (2, 2, "U", "base", 2), (1, 1, "W", "base", 2), (0, 0, "P (V)", "base", 2)], h=44)
    d.box(60, 140, 430, 90, "Hardware bits", ["P = PTE_V (present), W writable, U user", "PCD: cache disabled (LAPIC, IOAPIC mappings)", "NX (63): no execute → needs EFER.NXE"], "white", size=12)
    d.box(510, 140, 450, 90, "* software bits (ignored by the CPU)", ["PTE_R (9) and PTE_X (10) keep the RISC-V code's", "permission arguments working. mappages()", "sets NX when PTE_X is absent"], "chg", size=12)
    return d.svg("x86-64 PTE bits")


def swtch():
    d = D(1000, 300, "Context switch swtch(old, new): on x86-64 the return address is on the stack")
    d.box(20, 55, 300, 200, "struct context", ["ra   ← return address on the stack", "sp   ← rsp after returning", "rbx", "rbp", "r12  r13  r14  r15", "(callee-saved, System V ABI)"], "chg", size=12.5, mono=True)
    d.box(360, 55, 280, 90, "save (old)", ["movq (%rsp), %rax → old->ra", "leaq 8(%rsp) → old->sp", "rbx, rbp, r12–r15"], "base", size=12, mono=True)
    d.box(360, 165, 280, 90, "restore (new)", ["new->sp → %rsp", "rbx, rbp, r12–r15", "jmp *new->ra"], "base", size=12, mono=True)
    d.box(680, 55, 300, 200, "Unlike RISC-V", ["RISC-V: the return address is in ra", "→ ret goes back", "", "x86-64: call pushes the return address", "→ swtch pops it into ra when saving,", "  and 'returns' with jmp when restoring"], "white", size=12)
    return d.svg("swtch")
