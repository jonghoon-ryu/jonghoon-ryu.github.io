from svg import D


def layers():
    d = D(1000, 300, "Layers of output in step-03: printk → consputc → uartputc_sync")
    d.box(20, 60, 230, 80, "printk(fmt, ...)", ["%d %u %x %p %s %c", "%ld %lu %lx"], "new")
    d.box(290, 60, 200, 80, "consputc(c)", ["console.cpp", "handles BACKSPACE"], "new")
    d.box(530, 60, 200, 80, "uartputc_sync(c)", ["uart.cpp (step-02)"], "base")
    d.box(770, 60, 210, 80, "COM1", ["QEMU terminal", "vbox/serial.log"], "hw")
    d.arrow(250, 100, 288, 100); d.arrow(490, 100, 528, 100); d.arrow(730, 100, 768, 100)
    d.box(290, 170, 440, 50, "", ["step-04 adds fbconsputc() (the screen) here"], "white", size=12, dash=True)
    d.arrow(510, 140, 510, 168, dash=True)
    d.box(20, 240, 960, 45, "", ["panic(s): prints \"panic: \" + s and stops. With panicking set, other code (later the screen console) takes no locks"], "white", size=12)
    return d.svg("layers of output")


def fmtcheck():
    d = D(1000, 220, "The format(printf) attribute: g++ checks printk's argument types (no such check in C)")
    d.box(20, 55, 470, 80, "declaration (defs.h)", ["int printk(const char *, ...)", "  __attribute__((format(printf, 1, 2)));"], "new", mono=True, size=12.5)
    d.box(530, 55, 450, 80, "caught in the first build (main.cpp)", ["'%p' expects 'void*', but … 'long long unsigned int'", "'%ld' expects 'long int', but … 'long long unsigned int'"], "del", mono=True, size=11.5)
    d.arrow(490, 95, 528, 95)
    d.text(500, 170, "bootinfo's fields are all unsigned long long, shared by the loader (clang) and the kernel (g++) → printed via (void *) and (uint64)", 11.5)
    d.text(500, 195, "on x86-64 the sizes match and the output was right anyway, but the types were wrong; the check catches it at compile time", 11.5)
    return d.svg("format check")


def printkflow():
    d = D(1000, 300, "printk(fmt, …): the format string, one character at a time")
    d.box(20, 60, 200, 50, "fmt[i]", [], "base", size=13, mono=True)
    d.box(280, 30, 260, 44, "not '%'", ["consputc(c)"], "gray", size=12)
    d.box(280, 95, 260, 44, "'%': look at c0 c1 c2 after it", [], "white", size=12)
    d.arrow(220, 75, 278, 52); d.arrow(220, 95, 278, 117)
    rows = [("d", "printint(int, 10, signed)"), ("ld / lld", "printint(uint64, 10, signed)"), ("u / lu / llu", "printint(…, 10, unsigned)"),
            ("x / lx / llx", "printint(…, 16)"), ("p", "printptr: 0x + 16 digits"), ("s", "string (\"(null)\" for nullptr)"), ("c", "one character"), ("%", "'%'"),
            ("other", "'%' and that character, as is (to stand out)")]
    y = 30
    for k, v in rows:
        d.box(600, y, 110, 26, "", [k], "chg", size=11.5, mono=True, rx=3)
        d.text(720, y + 17, v, 11, False, "start")
        y += 29
    d.arrow(540, 117, 598, 117)
    d.text(300, 200, "va_arg(ap, type) takes the next argument (<stdarg.h>: a header from the compiler)", 11.5)
    d.text(300, 225, "two-letter formats like %ld skip ahead (i += 1; %lld: i += 2)", 11.5)
    return d.svg("printk flow")


def printint():
    d = D(1000, 250, "printint(255, 16, 0): digits collected lowest first, printed in reverse")
    y = 55
    for a, b, c in [("x = 255", "255 % 16 = 15 → 'f'", "x = 15"), ("x = 15", "15 % 16 = 15 → 'f'", "x = 0")]:
        d.box(30, y, 140, 40, "", [a], "base", size=12.5, mono=True)
        d.box(200, y, 260, 40, "", [b], "chg", size=12.5, mono=True)
        d.box(490, y, 140, 40, "", [c], "base", size=12.5, mono=True)
        d.arrow(170, y + 20, 198, y + 20); d.arrow(460, y + 20, 488, y + 20)
        y += 52
    d.text(800, 60, "buf", 12, True)
    for i, ch in enumerate("ff"):
        d.rect(740 + i * 50, 70, 46, 46, "new"); d.text(763 + i * 50, 100, ch, 18, True, mono=True)
        d.text(763 + i * 50, 132, f"buf[{i}]", 10, mono=True)
    d.text(800, 165, "→ consputc(buf[1]), then buf[0]", 11.5)
    d.text(500, 215, "negatives (%d): computed without the sign, '-' stored last so it prints first.  digits[] = \"0123456789abcdef\" (constexpr)", 11.5)
    return d.svg("printint")
