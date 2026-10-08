from svg import D


def fbclass():
    d = D(1000, 300, "fbcons: C's 'global struct + functions' → C++'s 'struct + member functions'")
    d.box(20, 55, 440, 200, "C version (fbcons.c)", ["static struct { fb, stride, cols, rows,", "  cx, cy, charw, charh; lock } cons;", "",
                                                     "static void fillrect(...)  { cons.fb ... }", "static void drawchar(...)  { cons.fb ... }", "static void cursor(...), scroll(...)"], "gray", mono=True, size=12)
    d.arrow(460, 155, 528, 155)
    d.box(530, 55, 450, 200, "C++ version (fbcons.cpp)", ["namespace {", "struct FbCons {", "  uint *fb; int stride; ...",
                                                          "  void fillrect(...) { fb ... }", "  void drawchar(...), cursor(...), scroll()", "};", "FbCons cons;", "}"], "new", mono=True, size=12)
    d.text(500, 285, "an anonymous namespace = C's static: invisible outside this file. The lock (cons.lock) returns with spinlock.cpp", 11.5)
    return d.svg("fbcons structure")


def beforeafter():
    d = D(1000, 260, "step-03 → step-04: where printk goes")
    d.text(250, 50, "step-03", 13, True, color="#2c3e50"); d.text(750, 50, "step-04", 13, True, color="#2c3e50")
    d.box(40, 65, 140, 44, "printk", [], "base"); d.box(200, 65, 140, 44, "consputc", [], "base"); d.box(360, 65, 120, 44, "UART", [], "hw")
    d.arrow(180, 87, 198, 87); d.arrow(340, 87, 358, 87)
    d.box(40, 130, 440, 100, "screen", ["a dark blue background painted by main.cpp", "+ hand-drawn 8×8 \"xv6\"", "(printk never reaches the screen)"], "del", size=12)
    d.box(540, 65, 130, 44, "printk", [], "base"); d.box(690, 65, 130, 44, "consputc", [], "chg")
    d.box(840, 40, 140, 44, "fbconsputc", [], "new"); d.box(840, 100, 140, 44, "UART", [], "hw")
    d.arrow(670, 87, 688, 87); d.arrow(820, 80, 838, 62); d.arrow(820, 95, 838, 120)
    d.box(540, 165, 440, 65, "screen", ["boot messages as text (Spleen font)", "→ visible on real PCs without a serial port"], "new", size=12)
    return d.svg("before and after step-04")


def cursorrules():
    d = D(1000, 360, "fbconsputc(c): one character and the cursor (cx, cy)")
    rows = [("'\\n'", "cx = 0, cy + 1"), ("'\\r'", "cx = 0"), ("'\\b'", "cx − 1 (stays at 0)"), ("'\\t'", "cx to the next multiple of 8"), ("other", "drawchar(cx, cy, c), cx + 1")]
    y = 50
    for c, act in rows:
        d.box(30, y, 90, 32, "", [c], "chg", size=12.5, mono=True, rx=3)
        d.text(135, y + 21, act, 12, False, "start")
        y += 38
    d.box(470, 50, 240, 60, "cx ≥ cols ?", ["→ cx = 0, cy + 1 (wrap)"], "white", size=12.5)
    d.box(470, 130, 240, 60, "cy ≥ rows ?", ["→ scroll(), cy = rows − 1"], "white", size=12.5)
    d.arrow(590, 110, 590, 128)
    d.box(740, 50, 240, 140, "around it", ["cursor(BG): erase the old cursor", "… the steps on the left …", "cursor(FG): draw the new one"], "new", size=12.5)
    d.box(30, 245, 950, 95, "Screen size → text cells (real values)", ["QEMU: 1280 × 800, 16 × 32 font → 80 columns × 25 rows",
                                                                     "VirtualBox: 2560 × 1440, 32 × 64 font (2560 or wider) → 80 columns × 22 rows",
                                                                     "the barebone PC: 1920 × 1080, 16 × 32 font → 120 columns × 33 rows"], "white", size=12.5)
    return d.svg("cursor rules")
