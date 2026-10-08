from svg import D


def uart():
    d = D(1000, 380, "16550 UART: eight registers from I/O port 0x3F8 (COM1)")
    regs = [("+0", "THR / RHR", "byte to send / byte received"), ("+1", "IER", "interrupt enable (0 for now)"), ("+2", "FCR", "FIFO enable, clear"),
            ("+3", "LCR", "8 bits; baud-rate setting mode"), ("+5", "LSR", "status: bit 0 received, bit 5 can send")]
    y = 60
    for off, name, what in regs:
        d.box(20, y, 70, 40, "", [off], "hw", mono=True, size=12.5, rx=3)
        d.box(90, y, 120, 40, name, [], "hw", size=12.5, rx=3)
        d.text(222, y + 25, what, 11.5, anchor="start")
        y += 46
    d.box(560, 60, 420, 120, "uartputc_sync(c)", ["while ((ReadReg(LSR) & LSR_TX_IDLE) == 0)", "  ;   // wait until it can send", "WriteReg(THR, c);"], "new", mono=True, size=12.5)
    d.box(560, 200, 420, 150, "[platform: real PC] no COM1", ["a missing port reads 0xFF", "LSR = 0xFF → TX_IDLE looks set → no waiting:", "bytes are written into nothing, nothing hangs",
                                                             "RX_READY looks set too → uartgetc() filters 0xFF first"], "hw", size=12.5)
    d.text(20, 320, "RISC-V version: the UART is at memory address 0x10000000 (memory-mapped I/O, read and written through pointers)", 11.5, anchor="start")
    d.text(20, 342, "x86 PC: a separate I/O port address space (inb / outb instructions)", 11.5, anchor="start")
    return d.svg("UART registers")


def cxx():
    d = D(1000, 300, "C → C++: the same machine code, more checking")
    rows = [("#define LSR 5", "constexpr ushort LSR = 5;", "typed; seen by the debugger"),
            ("#define ReadReg(reg) (inb(COM1 + (reg)))", "static inline uchar ReadReg(ushort reg)", "types checked; no macro traps"),
            ("(char *)dst", "static_cast<char *>(dst)", "the kind of cast is visible"),
            ("void *memset(void *, int, uint)", "extern \"C\" void *memset(..., uint64)", "g++ calls it itself: C name")]
    d.text(250, 52, "C version", 12.5, True); d.text(620, 52, "C++ version", 12.5, True)
    y = 64
    for c, cpp, why in rows:
        d.box(20, y, 400, 46, "", [c], "gray", mono=True, size=12, rx=3)
        d.arrow(420, y + 23, 448, y + 23)
        d.box(450, y, 340, 46, "", [cpp], "new", mono=True, size=11.5, rx=3)
        d.text(800, y + 27, why, 10.5, anchor="start")
        y += 56
    return d.svg("C compared with C++")


def uartinit():
    d = D(1000, 300, "What uartinit() writes, in order (I/O port COM1 = 0x3F8)")
    w = [("IER ← 0x00", "interrupts off"), ("LCR ← 0x80", "baud-rate mode (DLAB)"), ("+0 ← 0x03", "divisor, low byte"), ("+1 ← 0x00", "divisor, high byte"),
         ("LCR ← 0x03", "8 bits, no parity"), ("FCR ← 0x07", "enable and clear FIFOs")]
    x = 15
    for i, (op, why) in enumerate(w):
        d.box(x, 60, 152, 70, op, [why], "hw" if i in (2, 3) else "base", size=12)
        if i:
            d.arrow(x - 13, 95, x - 1, 95)
        x += 165
    d.box(15, 160, 480, 110, "Speed: 115200 / divisor", ["the UART's base rate of 115200 baud divided by 3 = 38400 baud", "only while DLAB (LCR bit 7) is set",
                                                         "are +0 and +1 the divisor registers", "(normally +0 = THR/RHR, +1 = IER)"], "white", size=12)
    d.box(515, 160, 470, 110, "Different from the C version", ["the C version enables the transmit and receive", "interrupts (IER) at the end; this step has no", "interrupt handling yet, so it doesn't (Step 18)"], "chg", size=12)
    return d.svg("UART initialization order")


def lsrbits():
    d = D(1000, 210, "LSR (line status, COM1 + 5): the two bits xv6 looks at")
    d.bits(150, 60, 700, 8, [(7, 7, "", "gray"), (6, 6, "", "gray"), (5, 5, "TX_IDLE", "new"), (4, 4, "", "gray"), (3, 3, "", "gray"), (2, 2, "", "gray"), (1, 1, "", "gray"), (0, 0, "RX_READY", "new")], h=44, label="LSR")
    d.text(500, 140, "TX_IDLE (1 << 5): THR is empty and takes the next byte → uartputc_sync() waits for it", 11.5)
    d.text(500, 163, "RX_READY (1 << 0): a received byte is in RHR → uartgetc() reads it", 11.5)
    d.text(500, 186, "no port: 0xFF, every bit looks set → output just disappears, and uartgetc() filters 0xFF on input", 11.5, color="#7d3c98")
    return d.svg("LSR bits")
