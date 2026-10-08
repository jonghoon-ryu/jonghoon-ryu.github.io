from svg import D


def pciaddr():
    d = D(1000, 300, "Reading PCI configuration space: address to port 0xCF8, value from 0xCFC")
    fields = [(31, 31, "enable", "hw", 60), (30, 24, "0", "gray", 70), (23, 16, "bus", "mem", 150), (15, 11, "device", "new", 120),
              (10, 8, "func", "chg", 90), (7, 2, "register", "base", 130), (1, 0, "00", "gray", 50)]
    d.bits(100, 70, 670, 0, fields, h=44)
    d.text(90, 97, "0xCF8 ←", 11.5, True, "end", "#2c3e50")
    d.text(500, 140, "pciaddr(bus, dev, func, off) = 0x80000000 | bus << 16 | dev << 11 | func << 8 | (off & 0xFC)", 11.5, mono=True)
    regs = [("0x00", "vendor ID | device ID", "0xFFFFFFFF if absent"), ("0x04", "command", "bit 1 memory, bit 2 bus master"),
            ("0x08", "class code (31:8)", "0x0C0330 = USB xHCI"), ("0x10", "BAR0 (+ BAR1)", "address of the device registers")]
    y = 170
    for off, name, note in regs:
        d.box(100, y, 70, 26, "", [off], "gray", mono=True, size=11.5, rx=2)
        d.box(170, y, 240, 26, "", [name], "white", size=11.5, rx=2)
        d.text(425, y + 18, note, 11, anchor="start")
        y += 30
    d.box(640, 170, 340, 116, "pciscan(cls, found)", ["bus 256 × device 32 × function 8", "skips vendor 0xFFFF", "calls found() when the class matches", "(no bridge walking: the simple way)"], "new", size=12)
    return d.svg("PCI configuration address")


def trapframe():
    d = D(1000, 330, "When a CPU exception happens: earlyvec.S → earlytrap() and its stack")
    d.box(20, 60, 240, 90, "CPU exception", ["divide by 0, bad pointer …", "jumps to IDT[n]"], "hw")
    d.box(300, 60, 240, 90, "earlyvec.S entry n", ["pushes 0 if no error code", "pushes n", "jmp earlycommon"], "new")
    d.box(580, 60, 400, 90, "earlytrap(f)", ["\"CPU exception 14 (page fault), error code 2\"", "\"rip 0x…, address 0x… (cr2)\"", "panic → stays on screen"], "new")
    d.arrow(260, 105, 298, 105); d.arrow(540, 105, 578, 105)
    y = 175
    for lab, k in [("f[0] = vector number n", "new"), ("f[1] = error code (or 0)", "new"), ("f[2] = rip", "hw"), ("f[3] = cs", "hw"), ("f[4] = rflags", "hw"), ("f[5] = rsp, f[6] = ss", "hw")]:
        d.box(80, y, 260, 22, "", [lab], k, size=11.5, rx=0)
        y += 22
    d.text(345, 190, "← rsp (= f)", 10.5, False, "start")
    d.box(480, 175, 500, 132, "Why now", ["with no IDT of its own, the firmware's IDT is still loaded", "QEMU: OVMF prints registers and hangs",
                                        "real PC: that firmware code may be gone → silent reboot", "much of the USB driver can only be tested on a real PC:", "failures must be visible in a photo"], "white", size=12)
    return d.svg("exception stack")


def pcitree():
    d = D(1000, 300, "PCI bus 0 of QEMU's q35 machine (step-06's list, make qemu USB=1)")
    d.box(400, 45, 200, 50, "bus 0", ["PCI root"], "hw", size=12.5)
    x = 20
    for addr, ids, what, k in [("0:0.0", "8086:29c0", "host bridge", "gray"), ("0:1.0", "1234:1111", "VGA (screen)", "base"), ("0:2.0", "8086:10d3", "Ethernet", "base"),
                               ("0:3.0", "1b36:000d", "xHCI (USB 3)", "new"), ("0:31.2", "8086:2922", "SATA AHCI", "base")]:
        d.path(f"M500,95 L500,120 L{x + 90},120 L{x + 90},140")
        d.box(x, 142, 180, 80, addr, [ids, what], k, size=12.5)
        x += 194
    d.text(500, 250, "bus:device.function. 0:31.2 = function 2 of device 31: several functions of one chip (ICH9)", 11.5)
    d.text(500, 274, "the real PC's xHCI: 0:20.0, 8086:7a60 (Intel 700 series)", 11.5, color="#7d3c98")
    return d.svg("PCI device tree")


def gate():
    d = D(1000, 230, "One IDT entry (struct gatedesc, 16 bytes): earlytrapinit() fills 32 of them")
    d.bits(60, 60, 880, 0, [(127, 96, "rsvd (0)", "gray", 3), (95, 64, "off_63_32", "mem", 4), (63, 48, "off_31_16", "mem", 3),
                            (47, 40, "type_attr 0x8E", "new", 3), (39, 32, "ist (0)", "gray", 2), (31, 16, "cs (code selector)", "base", 3), (15, 0, "off_15_0", "mem", 3)], h=44)
    d.text(500, 140, "the three off_* pieces = handler address (earlyvectors + 16 × n). cs = the current code segment (mov %cs)", 11.5)
    d.text(500, 164, "0x8E = 1000 1110: P (present) = 1, DPL = 0 (kernel only), type 0xE = 64-bit interrupt gate (interrupts off on entry)", 11.5)
    d.text(500, 188, "lidt(idt, sizeof(idt)) tells the CPU the table's address and size", 11.5)
    return d.svg("IDT gate")
