from svg import D
from figs.common import numstat


def timeline():
    d = D(1000, 300, "The order of the tags: each tag starts from the one before it")
    d.text(20, 62, "branch main (C)", 12, True, "start", "#2c3e50")
    d.box(20, 75, 130, 54, "06aad25", ["MIT xv6-riscv"], "gray")
    d.box(190, 75, 150, 54, "v0.1-x86_64-c", ["x86-64 port (C)"], "base")
    d.box(380, 75, 150, 54, "v0.2-x86_64-c", ["+ screen, keyboard"], "base")
    d.arrow(150, 102, 188, 102); d.arrow(340, 102, 378, 102)
    d.path("M455,129 L455,150 L64,150 L64,188")
    d.text(470, 154, "← delete almost all of the C version, keep the boot skeleton, build up again", 10.5, False, "start", "#566573")
    d.text(80, 178, "branch cpp (C++)", 12, True, "start", "#2c3e50")
    xs = [20, 115, 210, 305, 400, 495, 590, 685, 780, 875]
    for i, x in enumerate(xs):
        d.box(x, 190, 88, 46, f"step-{i + 1:02d}", [], "new" if i >= 5 else "chg", size=12)
        if i:
            d.arrow(xs[i - 1] + 88, 213, x, 213)
    d.text(232, 262, "Steps 1–5: boot, console, screen, keyboard (from the C version)", 11)
    d.text(737, 262, "Steps 6–10: USB keyboard (new, for the real PC)", 11)
    d.legend(330, 290, (("chg", "C code rewritten in C++"), ("new", "code the C version never had")))
    return d.svg("order of the tags")


def system():
    d = D(1000, 560, "The whole kernel at step-10: which step added what")
    d.text(20, 52, "boot", 12.5, True, "start", "#2c3e50")
    boot = [("UEFI firmware", "", "hw"), ("boot/loader.c", "v0.1 · step-01", "base"), ("entry.S", "step-01", "base"), ("start.cpp", "step-01", "base"), ("main.cpp", "step-01 … 10", "base")]
    x = 20
    for i, (n, s, k) in enumerate(boot):
        d.box(x, 62, 172, 52, n, [s] if s else [], k, size=12)
        if i:
            d.arrow(x - 22, 88, x - 1, 88)
        x += 194
    d.text(20, 150, "output", 12.5, True, "start", "#2c3e50")
    d.box(20, 160, 200, 52, "printk / panic", ["step-03"], "chg", size=12)
    d.box(250, 160, 200, 52, "console.cpp", ["step-03, 04, 05"], "chg", size=12)
    d.box(480, 140, 200, 46, "fbcons.cpp + font.h", ["step-04 → screen"], "chg", size=11.5)
    d.box(480, 192, 200, 46, "uart.cpp", ["step-02 → COM1"], "chg", size=11.5)
    d.arrow(220, 186, 248, 186); d.arrow(450, 180, 478, 163); d.arrow(450, 192, 478, 215)
    d.box(720, 140, 260, 98, "On a real PC", ["screen: visible (1920 × 1080)", "COM1: usually absent → reads 0xFF", "output simply disappears (no hang)"], "white", size=11.5)
    d.text(20, 278, "input (polled by main()'s loop)", 12.5, True, "start", "#2c3e50")
    d.box(20, 290, 190, 50, "kbd.cpp", ["step-05: PS/2"], "chg", size=12)
    d.box(20, 350, 190, 50, "uart.cpp", ["step-05: uartintr"], "chg", size=12)
    d.box(20, 410, 190, 50, "usb.cpp", ["step-08, 09, 10"], "new", size=12)
    d.box(250, 410, 190, 50, "xhci.cpp", ["step-07 … 10"], "new", size=12)
    d.box(480, 410, 190, 50, "pci.cpp", ["step-06"], "new", size=12)
    d.arrow(210, 435, 248, 435); d.arrow(440, 435, 478, 435, "finds")
    d.box(250, 300, 220, 90, "consoleintr()", ["echo, line editing", "(console.cpp, step-05)"], "chg", size=12)
    d.arrow(210, 315, 248, 330); d.arrow(210, 375, 248, 360); d.path("M115,410 L115,400 L240,400 L248,380")
    d.box(720, 290, 260, 170, "hardware", ["PS/2 controller (QEMU, VBox)", "COM1 16550 UART", "PCI bus", "xHCI → hub → USB keyboard", "(the only path on the real PC)"], "hw", size=11.5)
    d.box(20, 490, 450, 50, "earlytrap.cpp + earlyvec.S (step-06)", ["CPU exception → printed on screen, then stop (no silent reboot)"], "new", size=11.5)
    d.box(500, 490, 480, 50, "Not there yet (from Step 11)", ["locks, memory allocation, page tables, interrupts, processes, file system, shell"], "gray", size=11.5)
    d.legend(600, 278, (("chg", "from the C version"), ("new", "new (not in C)")))
    return d.svg("structure of the whole kernel")


def lines():
    tags = ["step-01", "step-02", "step-03", "step-04", "step-05", "step-06", "step-07", "step-08", "step-09", "step-10"]
    prev = ["v0.2-x86_64-c"] + tags[:-1]
    data = []
    for p, t in zip(prev, tags):
        rows = numstat(p, t)
        data.append((t, sum(r[2] for r in rows if not r[0].endswith("font.h")), sum(r[2] for r in rows if r[0].endswith("font.h")), sum(r[3] for r in rows)))
    d = D(1000, 380, "Lines added per tag (font.h, the font data, shown separately): step-01 deletes the C version")
    top = max(a + f for _, a, f, _ in data)
    base, hmax = 300, 220
    for i, (t, a, f, dl) in enumerate(data):
        x = 60 + i * 92
        ha = hmax * a / top; hf = hmax * f / top
        d.rect(x, base - ha, 56, ha, "new" if i >= 5 else "chg")
        if f:
            d.rect(x, base - ha - hf, 56, hf, "gray"); d.text(x + 28, base - ha - hf / 2 - 4, "font.h", 9.5); d.text(x + 28, base - ha - hf / 2 + 10, f"+{f}", 9.5, mono=True)
        d.text(x + 28, base - ha - hf - 6, f"+{a}" + (" code" if f else ""), 10.5, True, mono=True, color="#2c3e50")
        d.text(x + 28, base + 18, t, 10.5, mono=True)
        if dl > 500:
            d.text(x + 28, base + 36, f"−{dl}", 10, False, mono=True, color="#c0392b")
    d.line(50, base, 990, base, "#566573", 1.5)
    d.legend(430, 360, (("chg", "from the C version"), ("new", "USB keyboard"), ("gray", "font data")))
    return d.svg("lines added per tag")
