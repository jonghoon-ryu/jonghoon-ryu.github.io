from svg import D


def regmap():
    d = D(1000, 520, "같은 일, 다른 장치 : riscv.h ↔ x86.h (xv6 가 쓰는 것만)")
    rows = [("페이지 테이블 시작", "satp  (w_satp)", "CR3  (w_cr3)"),
            ("트랩 처리 주소", "stvec  (w_stvec)", "IDT  (lidt)"),
            ("트랩 원인", "scause  (r_scause)", "벡터 번호 trapno (스텁이 push)"),
            ("잘못된 주소", "stval  (r_stval)", "CR2  (r_cr2)"),
            ("트랩 난 곳", "sepc  (r_sepc)", "trapframe 의 rip (CPU 가 push)"),
            ("CPU 번호", "tp  (r_tp, w_tp)", "GS base MSR  (r_gsbase, wrmsr)"),
            ("인터럽트 켬/끔", "sstatus.SIE  (intr_on/off)", "RFLAGS.IF  (sti / cli)"),
            ("시스템 콜 명령", "ecall", "int $64"),
            ("사용자로 돌아가기", "sret", "iretq"),
            ("TLB 비우기", "sfence.vma", "CR3 다시 쓰기  (sfence_vma)"),
            ("타이머", "stimecmp", "LAPIC 타이머")]
    d.text(160, 52, "하는 일", 12, True); d.text(450, 52, "RISC-V (riscv.h)", 12, True); d.text(790, 52, "x86-64 (x86.h)", 12, True)
    y = 62
    for what, rv, x in rows:
        d.box(20, y, 280, 36, "", [what], "white", size=12.5, rx=3)
        d.box(310, y, 280, 36, "", [rv], "gray", size=12.5, mono=True, rx=3)
        d.arrow(592, y + 18, 618, y + 18)
        d.box(620, y, 360, 36, "", [x], "new", size=12.5, mono=True, rx=3)
        y += 40
    d.text(500, y + 12, "x86 에는 같은 이름의 레지스터가 없는 것도 있다 : 트랩 원인과 위치는 CPU 와 스텁이 스택에 push 한다", 11.5)
    return d.svg("RISC-V 와 x86-64 레지스터 대응")


def pagewalk():
    d = D(1000, 420, "가상 주소 → 물리 주소 : Sv39 (3단계) 와 x86-64 (4단계)")
    d.text(20, 58, "RISC-V Sv39", 12.5, True, "start", "#2c3e50")
    d.bits(150, 66, 820, 39, [(38, 30, "L2 (9비트)", "chg"), (29, 21, "L1 (9비트)", "chg"), (20, 12, "L0 (9비트)", "chg"), (11, 0, "페이지 안 오프셋 (12)", "mem")], h=34)
    d.text(20, 160, "x86-64", 12.5, True, "start", "#2c3e50")
    d.bits(150, 168, 820, 48, [(47, 39, "PML4 (L3)", "new"), (38, 30, "PDPT (L2)", "chg"), (29, 21, "PD (L1)", "chg"), (20, 12, "PT (L0)", "chg"), (11, 0, "오프셋 (12)", "mem")], h=34)
    d.box(20, 240, 470, 160, "walk() 이 바뀐 곳 (vm.c)", ["for (level = 2 …)  →  for (level = 3 …)", "PX(level, va) : 9비트씩, 한 단계 더", "",
                                                       "중간 단계 PTE 에 W | U 도 켠다 :", "x86 은 모든 단계에서 W, U 를 검사하므로", "마지막 (leaf) PTE 만 권한을 정하게"], "chg", size=12.5)
    d.box(510, 240, 470, 160, "MAXVA 는 RISC-V 그대로 (2³⁸)", ["사용자 주소 배치를 바꾸지 않으려고", "x86 이 허용하는 2⁴⁷ 대신 2³⁸ 까지만 쓴다", "",
                                                         "→ 맨 위 PML4 의 인덱스는 언제나 0", "  (가상 주소 비트 47:39 가 0)", "TRAMPOLINE = MAXVA − 4096"], "white", size=12.5)
    return d.svg("페이지 테이블 단계 비교")


def ptebits():
    d = D(1000, 250, "x86-64 PTE (64비트) : xv6 가 쓰는 비트")
    d.bits(60, 60, 900, 0, [(63, 63, "NX", "new", 3), (62, 52, "(안 씀)", "gray", 5), (51, 12, "물리 페이지 번호 (PTE2PA)", "mem", 14), (11, 11, "", "gray", 1),
                            (10, 10, "X*", "chg", 2), (9, 9, "R*", "chg", 2), (8, 5, "(안 씀)", "gray", 4), (4, 4, "PCD", "hw", 2), (3, 3, "PWT", "hw", 2),
                            (2, 2, "U", "base", 2), (1, 1, "W", "base", 2), (0, 0, "P (V)", "base", 2)], h=44)
    d.box(60, 140, 430, 90, "하드웨어 비트", ["P = PTE_V (있음), W 쓰기, U 사용자", "PCD : 캐시 끔 (LAPIC, IOAPIC 매핑)", "NX (63) : 실행 금지 → EFER.NXE 를 켜야 동작"], "white", size=12)
    d.box(510, 140, 450, 90, "* 소프트웨어 비트 (CPU 는 무시)", ["PTE_R (9), PTE_X (10) : RISC-V 코드의 권한 인자를", "그대로 쓰려고 남겼다. mappages() 가", "PTE_X 가 없으면 NX 를 켠다"], "chg", size=12)
    return d.svg("x86-64 PTE 비트")


def swtch():
    d = D(1000, 300, "문맥 교환 swtch(old, new) : 반환 주소가 스택에 있는 x86-64")
    d.box(20, 55, 300, 200, "struct context", ["ra   ← 스택 맨 위의 반환 주소", "sp   ← 돌아간 뒤의 rsp", "rbx", "rbp", "r12  r13  r14  r15", "(callee-saved, System V ABI)"], "chg", size=12.5, mono=True)
    d.box(360, 55, 280, 90, "저장 (old)", ["movq (%rsp), %rax → old->ra", "leaq 8(%rsp) → old->sp", "rbx, rbp, r12–r15"], "base", size=12, mono=True)
    d.box(360, 165, 280, 90, "복원 (new)", ["new->sp → %rsp", "rbx, rbp, r12–r15", "jmp *new->ra"], "base", size=12, mono=True)
    d.box(680, 55, 300, 200, "RISC-V 와 다른 점", ["RISC-V : ra 레지스터에 반환 주소", "→ ret 로 돌아간다", "", "x86-64 : call 이 반환 주소를 스택에 push", "→ 저장할 때 꺼내 ra 에 두고,", "  복원할 때 jmp 로 '돌아간다'"], "white", size=12)
    return d.svg("swtch")
