from svg import D


def inputpath():
    d = D(1000, 290, "Input: no interrupts yet, so main()'s loop calls the handlers (polling)")
    d.box(20, 60, 170, 60, "PS/2 keyboard", ["ports 0x60, 0x64"], "hw")
    d.box(20, 140, 170, 60, "COM1 serial", ["port 0x3F8"], "hw")
    d.box(240, 60, 200, 60, "kbdintr()", ["kbdgetc(): scan code → char"], "new")
    d.box(240, 140, 200, 60, "uartintr()", ["uartgetc()"], "new")
    d.box(500, 95, 210, 70, "consoleintr(c)", ["echo, ^H, ^U", "collect in cons.buf"], "new")
    d.box(770, 95, 210, 70, "consputc()", ["screen + serial"], "base")
    d.arrow(190, 90, 238, 90); d.arrow(190, 170, 238, 170)
    d.arrow(440, 90, 498, 120); d.arrow(440, 170, 498, 140); d.arrow(710, 130, 768, 130)
    d.box(20, 220, 960, 50, "", ["main(): for (;;) { kbdintr(); uartintr(); pause; } → 100% CPU. In the C version interrupts call the same functions (here: Steps 18, 19)"], "white", size=12)
    return d.svg("polled input")


def keymap():
    d = D(1000, 260, "Key tables: C99 designated initializers → a constexpr function (tables built at compile time)")
    d.box(20, 55, 440, 110, "C version (kbd.h)", ["static uchar shiftcode[256] = {", "  [0x1D] CTL, [0x2A] SHIFT, ...", "};", "// C++ has no designated array initializers"], "gray", mono=True, size=12)
    d.arrow(460, 110, 528, 110)
    d.box(530, 55, 450, 110, "C++ version (kbd.h)", ["constexpr Keymap shiftcode = makemap({", "  {0x1D, CTL}, {0x2A, SHIFT}, ...", "});"], "new", mono=True, size=12)
    d.box(20, 190, 960, 50, "", ["makemap() is constexpr: g++ runs it during compilation and emits the finished 256-byte table (the same data as the C version)"], "white", size=12)
    return d.svg("key tables")


def ring():
    d = D(1000, 330, "cons.buf: a 128-byte circular buffer with three indexes r, w, e")
    n = 16; x0 = 60; cw = 55; txt = "ls\nech"
    for i in range(n):
        d.rect(x0 + i * cw, 80, cw, 50, "new" if i < 3 else "chg" if i < 6 else "white")
        ch = txt[i] if i < len(txt) else ""
        d.text(x0 + i * cw + cw / 2, 112, "\\n" if ch == "\n" else ch, 15, False, mono=True, color="#2c3e50")
        d.text(x0 + i * cw + cw / 2, 146, str(i), 9.5, mono=True, color="#7f8c8d")
    for idx, name, col in ((0, "r", "#c0392b"), (3, "w", "#1e8449"), (6, "e", "#b7950b")):
        x = x0 + idx * cw
        d.arrow(x, 185, x, 133, color=col); d.text(x, 200, name, 14, True, color=col, mono=True)
    d.text(x0 + 8 * cw, 70, "… really 128 cells; indexes wrap with % INPUT_BUF_SIZE", 11, False, "start")
    d.box(60, 225, 280, 85, "r … w: finished lines", ["what read() will take", "(\"ls\\n\")"], "new", size=12)
    d.box(360, 225, 280, 85, "w … e: the line being typed", ["can be edited with backspace, ^U", "(\"ech\")"], "chg", size=12)
    d.box(660, 225, 280, 85, "Different in step-05", ["no reader (consoleread) yet, so a", "finished line is dropped: r = w"], "white", size=12)
    return d.svg("console input buffer")


def ps2bits():
    d = D(1000, 200, "PS/2 status port 0x64: the bits kbd.cpp looks at")
    d.bits(150, 60, 700, 8, [(7, 7, "", "gray"), (6, 6, "", "gray"), (5, 5, "AUX", "chg"), (4, 4, "", "gray"), (3, 3, "", "gray"), (2, 2, "", "gray"), (1, 1, "IBF", "base"), (0, 0, "DIB", "new")], h=44, label="0x64")
    d.text(500, 138, "DIB (0x01): a byte is waiting at 0x60     IBF (0x02): the controller is still busy with a command (kbcwait waits)", 11.5)
    d.text(500, 162, "AUX (0x20): the byte came from the mouse → dropped.   No controller: 0xFF (all ones), which kbdgetc filters first", 11.5)
    return d.svg("PS/2 status bits")
