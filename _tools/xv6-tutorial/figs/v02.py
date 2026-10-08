import re as _re, subprocess as _sp
from svg import D


def _glyph(tag, ch):
    src = _sp.run(["git", "-C", "/home/ryuj/Ryu/xv6-x86_64", "show", f"{tag}:kernel/font.h"], capture_output=True, text=True, check=True).stdout
    i = src.index("font16x32"); j = src.index(f"// '{ch}'", i)
    return [int(x, 16) for x in _re.findall(r"0x[0-9a-fA-F]+", src[j:src.index("}", j)])]


def paths():
    d = D(1000, 380, "Input and output paths: the screen and the keyboard are new")
    d.text(20, 55, "output", 13, True, "start", "#2c3e50")
    d.box(20, 65, 170, 60, "printk() / write(1)", ["consputc, consolewrite"], "base")
    d.box(250, 65, 170, 60, "console.c", ["screen first, then serial"], "chg")
    d.box(480, 40, 200, 50, "fbconsputc() → screen", [], "new")
    d.box(480, 100, 200, 50, "uartputc() → COM1", [], "base")
    d.arrow(190, 95, 248, 95); d.arrow(420, 95, 478, 65); d.arrow(420, 95, 478, 125)
    d.box(720, 40, 260, 110, "Why the screen first", ["if nobody is connected to", "VirtualBox's serial socket, the serial", "port blocks; the screen still shows"], "white", size=12)
    d.text(20, 205, "input", 13, True, "start", "#2c3e50")
    d.box(20, 215, 150, 60, "PS/2 keyboard", ["ports 0x60, 0x64"], "hw")
    d.box(200, 215, 150, 60, "IOAPIC → LAPIC", ["IRQ 1 → vector 33"], "hw")
    d.box(380, 215, 160, 60, "devintr() (trap.c)", ["T_IRQ0 + IRQ_KBD"], "chg")
    d.box(570, 215, 160, 60, "kbdintr() (kbd.c)", ["kbdgetc(): scan codes"], "new")
    d.box(760, 215, 220, 60, "consoleintr()", ["echo, line editing, wake read()"], "base")
    for a, b in ((170, 200), (350, 380), (540, 570), (730, 760)):
        d.arrow(a, 245, b - 2, 245)
    d.box(20, 300, 960, 60, "", ["Serial input (COM1, IRQ 4 → uartintr) was there since v0.1. The keyboard path joins it at the same consoleintr().",
                                   "kbd.c and kbd.h were taken from the old x86 xv6 (xv6-public) and adapted"], "white", size=12)
    d.legend(700, 205, (("new", "new"), ("chg", "changed"), ("del", "deleted")))
    return d.svg("input and output paths")


def fb():
    d = D(1000, 300, "The frame buffer: the screen's pixels are plain memory (UEFI GOP)")
    x0, y0, W, H = 40, 60, 420, 200
    d.rect(x0, y0, W, H, "white")
    for c in range(1, 10):
        d.line(x0 + c * 42, y0, x0 + c * 42, y0 + H, "#e5e8e8", 1)
    for r in range(1, 5):
        d.line(x0, y0 + r * 40, x0 + W, y0 + r * 40, "#e5e8e8", 1)
    d.rect(x0 + 3 * 42, y0 + 2 * 40, 42, 40, "new"); d.text(x0 + 3 * 42 + 21, y0 + 2 * 40 + 25, "(3,2)", 10, mono=True)
    d.rect(x0 + 5 * 42, y0 + 4 * 40 + 34, 42, 5, "base")
    d.text(x0 + 5 * 42 + 21, y0 + H + 18, "cursor = 4 rows at the cell bottom", 10)
    d.text(x0 + W / 2, y0 - 8, "character cells (cols × rows), one cell = charw × charh pixels", 11)
    d.box(500, 60, 470, 90, "Address of pixel (x, y)", ["fb_base + (y × stride + x) × 4 bytes", "stride = pixels per scan line (may exceed width)"], "mem", size=12.5)
    d.box(500, 165, 470, 95, "scroll()", ["copies everything from the second text line (charh", "pixel rows) up by one line, then clears the last line to BG"], "new", size=12.5)
    return d.svg("frame buffer addressing")


def glyph():
    d = D(1000, 470, "One character = 16 × 32 pixels: 'A' in font.h (Spleen font, real data)")
    rows = _glyph("v0.2-x86_64-c", "A")
    cs = 12; x0, y0 = 60, 50
    for j, bits in enumerate(rows):
        for i in range(16):
            on = bits & (0x8000 >> i)
            d.p.append(f'<rect x="{x0 + i * cs}" y="{y0 + j * cs}" width="{cs}" height="{cs}" fill="{"#2c3e50" if on else "#ffffff"}" stroke="#d5dbdb" stroke-width="0.5"/>')
        d.text(x0 + 16 * cs + 8, y0 + j * cs + 10, f"0x{bits:04x}", 9.5, anchor="start", mono=True, color="#566573" if bits else "#bfc9ca")
    d.text(20, y0 + 32 * cs + 22, "one row = one ushort; leftmost pixel = highest bit (0x8000)", 10.5, False, "start")
    d.box(420, 60, 560, 150, "drawchar(col, row, c)", ["for j in 0..31:  bits = font16x32[c][j]", "  p = fb + (row*32 + j) * stride + col*16",
                                                       "  for i in 0..15:  p[i] = (bits & (0x8000 >> i)) ? FG : BG", "", "FG 0xD0D0D0 (light gray), BG 0 (black)"], "new", size=12.5, mono=True)
    d.box(420, 240, 560, 120, "On screens 2560 pixels wide or more", ["font32x64 (32 × 64 pixels, one uint per row)", "VirtualBox 2560 × 1440 → 80 columns × 22 rows",
                                                                    "QEMU 1280 × 800 → 16×32 font, 80 columns × 25 rows"], "white", size=12.5)
    return d.svg("font bitmap")


def kbdflow():
    d = D(1000, 470, "kbdgetc(): how one byte becomes a character (kbd.c)")
    d.box(380, 45, 240, 44, "read status port 0x64", [], "hw", size=12.5)
    d.box(380, 115, 240, 44, "bit 0 (DIB) == 0 ?", [], "white", size=12.5); d.arrow(500, 89, 500, 113)
    d.box(700, 115, 260, 44, "return -1 (no byte waiting)", [], "gray", size=11.5); d.arrow(620, 137, 698, 137, "yes")
    d.box(380, 185, 240, 44, "read data port 0x60 → data", [], "hw", size=12.5); d.arrow(500, 159, 500, 183, "no", lx=520, ly=176)
    rows = [("data == 0xE0 ?", "shift |= E0ESC  (next byte is an extended key)", "return 0"),
            ("data & 0x80 ?  (key released)", "shift &= ~shiftcode[data]", "return 0"),
            ("(key pressed)", "shift |= shiftcode, shift ^= togglecode", "look up the character")]
    y = 255
    for q, act, ret in rows:
        d.box(40, y, 300, 44, q, [], "white", size=12)
        d.box(370, y, 380, 44, "", [act], "chg", size=11.5, mono=True)
        d.box(780, y, 180, 44, ret, [], "new" if "character" in ret else "gray", size=12)
        d.arrow(340, y + 22, 368, y + 22); d.arrow(750, y + 22, 778, y + 22)
        y += 56
    d.path("M500,229 L500,242 L190,242 L190,253")
    d.box(40, 425, 920, 36, "", ["c = charcode[shift & (CTL | SHIFT)][data]   (normalmap, shiftmap, ctlmap, ctlmap)   + Caps Lock swaps case"], "white", size=12, mono=True)
    return d.svg("kbdgetc flow")


def backspace():
    d = D(1000, 250, "Erasing a character on screen: consputc(BACKSPACE) = '\\b', ' ', '\\b'")
    steps = [("start", "ls_", 2), ("'\\b'", "ls", 1), ("' '", "l _", 2), ("'\\b'", "l_", 1)]
    x = 30
    for i, (lab, txt, cur) in enumerate(steps):
        d.text(x + 100, 60, lab, 12, True, color="#2c3e50")
        for c in range(4):
            ch = txt[c] if c < len(txt) and txt[c] not in "_ " else ""
            d.rect(x + 20 + c * 40, 72, 40, 54, "white")
            d.text(x + 40 + c * 40, 106, ch, 20, False, mono=True, color="#2c3e50")
        d.rect(x + 22 + cur * 40, 118, 36, 5, "base")
        if i < 3:
            d.arrow(x + 190, 99, x + 222, 99)
        x += 240
    d.box(30, 150, 940, 80, "", ["Step back (\\b) → overwrite with a space → step back again. The same three characters go to the screen (fbconsputc)",
                                   "and to the serial port (uartputc_sync); serial terminals erase the same way. The cursor is the bar under the cell (cursor() in fbcons.c)"], "white", size=12)
    return d.svg("backspace")
