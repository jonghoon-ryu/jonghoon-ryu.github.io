# diagrams for "Code explanation up to step 10" (pages/code-explanation-step-10.md):
# the whole program as it stands at tag step-10, not the diff of one tag.
from svg import D


def bigpicture():
    d = D(1000, 560, "The whole program at step-10: boot, print, then echo every key")
    # firmware + loader
    d.box(15, 50, 200, 70, "UEFI firmware", ["in the PC's flash chip"], "hw", size=12.5)
    d.box(15, 150, 200, 90, "boot/loader.c", ["BOOTX64.EFI on the USB stick", "loads kernel + fs.img,", "fills struct bootinfo"], "base", size=12.5)
    d.box(15, 270, 200, 70, "entry.S → start()", ["stack, bootinfo copy,", "C++ constructors"], "base", size=12.5)
    d.arrow(115, 120, 115, 148)
    d.arrow(115, 240, 115, 268, "jump to 0x100000", lx=180, ly=258)
    d.arrow(215, 305, 268, 305)
    # main
    d.box(270, 50, 300, 490, "", [], "white")
    d.text(420, 75, "main()  (kernel/main.cpp)", 13, True, color="#2c3e50")
    steps = [("consoleinit()", "UART + screen ready", "base"), ("earlytrapinit()", "CPU exceptions → screen", "base"),
             ("printbootinfo()", "screen, ACPI, memory map", "base"), ("kbdinit()", "PS/2 controller: mouse off", "base"),
             ("usbinit()", "PCI scan → xHCI → devices", "base")]
    for i, (t, s, k) in enumerate(steps):
        d.box(290, 95 + i * 62, 260, 50, t, [s], k, size=12, mono=False)
    d.box(290, 415, 260, 110, "for (;;) loop", ["kbdintr()", "uartintr()", "usbintr()", "pause"], "chg", size=12.5)
    for i in range(5):
        d.arrow(420, 145 + i * 62, 420, 157 + i * 62) if i < 4 else d.arrow(420, 393, 420, 413)
    # devices
    d.box(640, 50, 340, 70, "output: printk() → consputc()", ["→ fbconsputc() screen", "→ uartputc_sync() serial COM1"], "new", size=12)
    d.box(640, 330, 105, 80, "PS/2", ["port 0x60", "0x64"], "hw", size=12)
    d.box(757, 330, 105, 80, "serial", ["COM1", "0x3F8"], "hw", size=12)
    d.box(874, 330, 106, 80, "USB", ["xHCI ring", "in memory"], "hw", size=12)
    d.box(640, 200, 340, 80, "consoleintr(c)", ["edit the line (backspace, ^U)", "echo c with consputc()"], "new", size=12.5)
    d.arrow(692, 330, 692, 282); d.arrow(810, 330, 810, 282); d.arrow(927, 330, 927, 282)
    d.arrow(810, 200, 810, 122, "echo", lx=840, ly=165)
    d.path("M550,470 L600,470 L600,440 L927,440 L927,412", dash=True)
    d.text(770, 460, "the loop asks each device: anything new?", 11.5, color="#566573")
    d.arrow(550, 120, 638, 85, "prints", lx=600, ly=92)
    d.text(810, 505, "No interrupts, no processes, no memory allocator yet:", 11.5, True, color="#2c3e50")
    d.text(810, 525, "one CPU runs main() and polls forever.", 11.5, color="#566573")
    return d.svg("the whole program")


def filemap():
    d = D(1000, 420, "Every file at step-10, by job (width ~ lines of code)")
    groups = [
        ("Boot", "#7d3c98", [("loader.c", 387, "hw"), ("efi.h", 191, "hw"), ("entry.S", 18, "base"), ("start.cpp", 38, "base"), ("kernel.ld", 50, "base")]),
        ("Output", "#1e8449", [("uart.cpp", 127, "new"), ("console.cpp", 120, "new"), ("printk.cpp", 133, "new"), ("fbcons.cpp", 153, "new"), ("font.h", 547, "new")]),
        ("Input", "#b7950b", [("kbd.cpp", 138, "chg"), ("kbd.h", 154, "chg")]),
        ("Safety net", "#c0392b", [("earlytrap.cpp", 61, "del"), ("earlyvec.S", 38, "del")]),
        ("USB keyboard", "#2874a6", [("pci.cpp", 61, "mem"), ("xhci.cpp", 807, "mem"), ("xhci.h", 185, "mem"), ("usb.cpp", 351, "mem")]),
        ("Shared", "#566573", [("main.cpp", 91, "gray"), ("x86.h", 310, "gray"), ("defs.h", 52, "gray"), ("string.cpp", 101, "gray"), ("memlayout.h", 56, "gray")]),
    ]
    y = 50
    scale = 0.5
    for name, col, files in groups:
        d.text(20, y + 26, name, 12.5, True, "start", col)
        x = 150
        total = sum(n for _, n, _ in files)
        for f, n, k in files:
            w = max(95, n * scale)
            d.box(x, y, w, 42, f, [str(n)], k, size=11.5, rx=4)
            x += w + 6
        d.text(990, y + 26, f"{total}", 11.5, True, "end", col)
        y += 58
    d.text(500, 405, "font.h is mostly bitmap data; xhci.cpp + usb.cpp (the USB keyboard) are a third of the kernel", 11.5, color="#566573")
    return d.svg("file map")


def build():
    d = D(1000, 330, "make usb.img: two compilers, one disk image")
    d.box(15, 50, 190, 60, "boot/loader.c", ["+ efi.h, bootinfo.h"], "hw", size=12)
    d.box(250, 50, 230, 60, "clang + lld-link", ["Windows-style PE file"], "base", size=12)
    d.box(525, 50, 170, 60, "BOOTX64.EFI", ["UEFI runs this"], "hw", size=12)
    d.box(15, 140, 190, 60, "kernel/*.cpp, *.S", ["14 objects"], "new", size=12)
    d.box(250, 140, 230, 60, "g++ / gcc, then ld", ["-ffreestanding, kernel.ld"], "base", size=12)
    d.box(525, 140, 170, 60, "kernel", ["ELF, linked at 0x100000"], "new", size=12)
    d.box(525, 225, 170, 50, "fs.img", ["1 KB of zeros (for now)"], "gray", size=12)
    for y in (80, 170):
        d.arrow(205, y, 248, y); d.arrow(480, y, 523, y)
    d.box(745, 90, 235, 120, "esp.img (64 MB FAT32)", ["/EFI/BOOT/BOOTX64.EFI", "/kernel", "/fs.img"], "mem", size=12, mono=False)
    d.arrow(695, 80, 743, 120); d.arrow(695, 170, 743, 160); d.arrow(695, 250, 743, 195)
    d.box(745, 235, 235, 70, "usb.img", ["GPT disk: one EFI System", "Partition = esp.img"], "mem", size=12)
    d.arrow(862, 210, 862, 233)
    d.text(380, 300, "make qemu / make vbox boot usb.img; dd it to a USB stick for the real PC", 11.5, color="#566573")
    return d.svg("build")


def loader():
    d = D(1000, 470, "boot/loader.c efi_main(): what the loader does, in order")
    steps = [
        ("1", "watchdog off, print \"xv6 loader\"", "else the firmware resets the PC after 5 minutes", "hw"),
        ("2", "open the partition it came from", "LoadedImage → SimpleFileSystem → root directory", "hw"),
        ("3", "a page for struct bootinfo", "AllocatePages below PHYSTOP (128 MB)", "base"),
        ("4", "loadkernel(): read \\kernel (ELF)", "copy each LOAD segment to its paddr (0x100000)", "new"),
        ("5", "read \\fs.img into RAM", "below PHYSTOP; the kernel will use it as a RAM disk", "base"),
        ("6", "a page below 640 KB (apboot)", "for starting other CPUs, later", "gray"),
        ("7", "find ACPI RSDP, GOP frame buffer", "configuration table; Graphics Output Protocol", "base"),
        ("8", "memory map, ExitBootServices()", "retry if the map changed; firmware services end here", "chg"),
        ("9", "jump to the kernel's entry", "sysv_abi call: %rdi = &bootinfo", "new"),
    ]
    for i, (n, t, s, k) in enumerate(steps):
        y = 45 + i * 46
        d.box(15, y, 40, 38, n, [], k, size=13, rx=19)
        d.box(65, y, 400, 38, t, [], k, size=12)
        d.text(480, y + 24, s, 11.5, anchor="start", color="#566573")
    d.text(500, 462, "between 7 and 8 it waits 3 seconds: on a real PC, the only chance to read these lines before the kernel clears the screen", 11.5, color="#7d3c98")
    return d.svg("loader steps")


def bootinfo():
    d = D(1000, 330, "struct bootinfo: everything the kernel knows about the machine")
    rows = [("memmap, memmap_size, memmap_descsize", "the UEFI memory map: which RAM is free", "mem"),
            ("fsimg, fsimg_size", "fs.img in RAM (1 KB placeholder until the file system)", "gray"),
            ("rsdp", "ACPI root pointer (CPUs, interrupt controllers, later)", "gray"),
            ("apboot", "a free page below 640 KB (other CPUs, later)", "gray"),
            ("fb_base, fb_size", "the frame buffer: pixel memory of the screen", "new"),
            ("fb_width, fb_height, fb_stride", "screen size; pixels per scan line", "new")]
    for i, (f, s, k) in enumerate(rows):
        y = 45 + i * 40
        d.box(15, y, 400, 32, f, [], k, size=11.5, mono=True, rx=4)
        d.text(430, y + 21, s, 11.5, anchor="start")
    d.text(500, 300, "12 fields, all 64-bit: the loader (clang, Microsoft ABI) and the kernel (g++, System V ABI) must agree on the layout", 11.5, color="#566573")
    d.text(500, 320, "start() copies it into the kernel's own global, bootinfo; green = used now, gray = kept for later steps", 11.5, color="#566573")
    return d.svg("bootinfo")


def memory():
    d = D(1000, 560, "Physical memory while main() runs (QEMU, 512 MB; addresses from the boot log)")
    rows = [("xHCI registers (MMIO)", 40, "hw", "0xC0_0000_0000"),
            ("…", 26, "white", None),
            ("frame buffer (screen pixels)", 40, "hw", "0x8000_0000"),
            ("…  nothing above 512 MB of RAM here", 26, "white", "0x2000_0000 (512 MB)"),
            ("free RAM: xhci.cpp dmapage() takes pages here", 70, "mem", "0x0800_0000 (PHYSTOP, 128 MB)"),
            ("bootinfo, memory map, fs.img (loader pages)", 34, "base", None),
            ("free RAM (below PHYSTOP): for kalloc later", 90, "gray", None),
            ("kernel: text, rodata, data, bss (97 KB)", 40, "new", "0x0010_0000 (1 MB)"),
            ("low memory: firmware data, apboot page", 40, "gray", "0"),
            ]
    d.memmap(260, 50, 420, rows)
    d.text(840, 80, "device memory:", 12, True, color="#7d3c98")
    d.text(840, 98, "reading/writing these", 11.5)
    d.text(840, 114, "addresses talks to hardware", 11.5)
    d.text(840, 280, "UEFI's page tables map", 12, True, color="#2874a6")
    d.text(840, 298, "every address to itself", 11.5)
    d.text(840, 314, "(virtual = physical);", 11.5)
    d.text(840, 330, "the kernel has no own yet", 11.5)
    d.box(700, 400, 285, 110, "", ["kernel ends at symbol end", "(kernel.ld); stack0 is in .bss:", "8 × 4 KB, only CPU 0's is used"], "white", size=12)
    d.text(470, 545, "not to scale. Addresses on a real PC differ: the loader asks the firmware, and the kernel reads bootinfo", 11.5, color="#566573")
    return d.svg("physical memory")


def startpath():
    d = D(1000, 300, "From the loader's jump to main()")
    d.box(15, 60, 210, 110, "entry.S  _entry", ["cli", "rsp = stack0 + 4096", "call start"], "base", size=12.5, mono=True)
    d.box(275, 60, 260, 110, "start.cpp  start(bi)", ["bootinfo = *bi", "run __init_array", "main()"], "base", size=12.5, mono=True)
    d.box(585, 60, 190, 110, "main.cpp  main()", ["never returns"], "new", size=12.5, mono=True)
    d.arrow(225, 115, 273, 115); d.arrow(535, 115, 583, 115)
    d.box(820, 60, 165, 110, "if it returned:", ["entry.S: hlt;", "jmp spin"], "gray", size=12)
    d.arrow(775, 115, 818, 115, dash=True)
    d.text(120, 200, "interrupts off for good", 11.5, color="#c0392b")
    d.text(120, 216, "(nothing could handle one)", 11.5, color="#566573")
    d.text(405, 200, "the loader's page may be reused", 11.5, color="#566573")
    d.text(405, 216, "C++ has no runtime here to", 11.5, color="#566573")
    d.text(405, 232, "call global constructors", 11.5, color="#566573")
    d.text(500, 285, "UEFI already put the CPU in 64-bit mode with paging on, so there is no mode switching (unlike old x86 xv6's bootasm.S)", 11.5, color="#566573")
    return d.svg("start path")


def output():
    d = D(1000, 330, "Output: one printk() call, two devices")
    d.box(15, 60, 200, 60, "printk(\"%d\", 42)", ["printk.cpp"], "new", size=12, mono=True)
    d.box(255, 60, 200, 60, "consputc('4')", ["one char at a time"], "new", size=12, mono=True)
    d.arrow(215, 90, 253, 90)
    d.box(520, 30, 220, 60, "fbconsputc(c)", ["fbcons.cpp: screen"], "new", size=12, mono=True)
    d.box(520, 120, 220, 60, "uartputc_sync(c)", ["uart.cpp: serial"], "new", size=12, mono=True)
    d.arrow(455, 80, 518, 60, "1st"); d.arrow(455, 100, 518, 150, "2nd")
    d.box(790, 30, 195, 60, "frame buffer", ["write pixels to memory"], "hw", size=12)
    d.box(790, 120, 195, 60, "16550 UART @ 0x3F8", ["wait LSR bit 5, outb THR"], "hw", size=12)
    d.arrow(740, 60, 788, 60); d.arrow(740, 150, 788, 150)
    d.box(15, 210, 970, 100, "", ["printk walks the format string: plain chars go to consputc; %d %u %x %ld %lu %lx %p %s %c %% format numbers/strings first",
                                  "the screen goes first: a real PC has no COM1, its port reads 0xFF (\"ready\") so the bytes vanish instead of hanging",
                                  "panic(s): prints \"panic: s\" and spins forever: the only way to stop on an error yet"], "white", size=12)
    return d.svg("output path")


def glyph():
    d = D(1000, 360, "fbcons.cpp: how a character becomes pixels (16×32 font; 32×64 on screens ≥ 2560 wide)")
    # bitmap grid of 'A' approximation 8 cols x 10 rows for illustration
    pat = ["00011000", "00111100", "01100110", "11000011", "11000011", "11111111", "11000011", "11000011", "11000011", "00000000"]
    x0, y0, c = 40, 50, 22
    for j, row in enumerate(pat):
        for i, b in enumerate(row):
            d.rect(x0 + i * c, y0 + j * c, c, c, "new" if b == "1" else "white", sw=1)
        d.text(x0 + 8 * c + 12, y0 + j * c + 15, row, 11.5, anchor="start", mono=True)
    d.text(130, 290, "font16x32['A'][row] = bits", 11.5, mono=True)
    d.text(130, 308, "(drawing shows 8 × 10 for size)", 11.5, color="#566573")
    d.box(430, 50, 555, 120, "drawchar(col, row, c)", ["for each pixel row j of the glyph:", "  p = fb + (row·charh + j)·stride + col·charw", "  pixel = bit set ? FG (light gray) : BG (black)"], "base", size=12, mono=True)
    d.box(430, 190, 270, 110, "cursor", ["an underline, 4 pixels tall,", "erased before each char,", "redrawn after"], "base", size=12)
    d.box(715, 190, 270, 110, "scroll()", ["copy every pixel row up", "by one text line, then", "clear the bottom line"], "base", size=12)
    d.text(700, 330, "stride ≥ width: a scan line can be longer than the visible screen", 11.5, color="#566573")
    return d.svg("glyph")


def loop():
    d = D(1000, 430, "Input: main()'s loop polls three devices, all feed consoleintr()")
    d.box(15, 50, 210, 330, "", [], "chg")
    d.text(120, 75, "for (;;) {", 12.5, True, mono=True)
    for i, (f, s) in enumerate([("kbdintr();", "≤ 16 bytes per call"), ("uartintr();", "until LSR says empty"), ("usbintr();", "read the event ring"), ("pause", "spin-loop hint")]):
        d.text(50, 115 + i * 62, f, 12.5, True, "start", mono=True)
        d.text(50, 133 + i * 62, s, 11.5, anchor="start", color="#566573")
    d.text(120, 365, "}", 12.5, True, mono=True)
    d.box(285, 60, 250, 70, "PS/2: inb(0x64) & 1?", ["inb(0x60) = scancode", "→ shift state, keymap → char"], "hw", size=12)
    d.box(285, 150, 250, 70, "UART: LSR & 1?", ["inb(0x3F8) = the byte", "(a terminal's key)"], "hw", size=12)
    d.box(285, 240, 250, 90, "xHCI: new event TRB?", ["transfer event → 8-byte", "key report → usbkey()", "→ char"], "hw", size=12)
    d.arrow(225, 105, 283, 95); d.arrow(225, 167, 283, 185); d.arrow(225, 229, 283, 280)
    d.box(600, 60, 385, 170, "consoleintr(c)", ["^U: erase the line", "^H, DEL: erase one char", "else: echo c, store in cons.buf", "'\\r' becomes '\\n'", "line complete → consumed at once", "(no reader until processes exist)"], "new", size=12.5)
    d.arrow(535, 95, 598, 120); d.arrow(535, 185, 598, 150); d.arrow(535, 285, 598, 200)
    d.box(600, 260, 385, 120, "cons.buf: 128-char circular buffer", ["r: next to read (by a reader, later)", "w: end of the last finished line", "e: where editing is (cursor)"], "white", size=12)
    d.text(500, 415, 'this is "polling": the CPU keeps asking. Steps 15-19 switch to interrupts, where devices tell the CPU', 11.5, color="#566573")
    return d.svg("input loop")


def ps2():
    d = D(1000, 280, "PS/2 keyboard: a scancode is a key position, not a character")
    d.box(15, 60, 150, 70, "press Shift", ["0x2A"], "hw", size=12, mono=True)
    d.box(185, 60, 150, 70, "press A", ["0x1E"], "hw", size=12, mono=True)
    d.box(355, 60, 150, 70, "release A", ["0x9E = 0x1E|0x80"], "hw", size=12, mono=True)
    d.box(525, 60, 150, 70, "release Shift", ["0xAA"], "hw", size=12, mono=True)
    d.box(15, 160, 150, 60, "shift |= SHIFT", ["returns 0"], "base", size=12, mono=True)
    d.box(185, 160, 150, 60, "shiftmap[0x1E]", ["= 'A' → console"], "new", size=12, mono=True)
    d.box(355, 160, 150, 60, "key up", ["returns 0"], "base", size=12, mono=True)
    d.box(525, 160, 150, 60, "shift &= ~SHIFT", ["returns 0"], "base", size=12, mono=True)
    for x in (90, 260, 430, 600):
        d.arrow(x, 130, x, 158)
    d.box(720, 60, 265, 160, "kbd.cpp kbdgetc()", ["0xE0 prefix: an extended key", "bit 7 set: key released", "shiftcode[]: Shift/Ctrl/Alt", "togglecode[]: Caps/Num Lock", "4 tables: normal, shift, ctl"], "base", size=12)
    d.text(500, 260, "kbdinit() first turns the PS/2 mouse off: its bytes share the one output buffer with the keys", 11.5, color="#566573")
    return d.svg("ps2")


def earlytrap():
    d = D(1000, 300, "earlytrap.cpp: a CPU exception prints a message instead of rebooting the PC")
    d.box(15, 60, 190, 70, "a bad pointer", ["e.g. page fault (14)"], "del", size=12)
    d.box(250, 60, 200, 70, "IDT entry 14", ["32 interrupt gates", "lidt(idt)"], "base", size=12)
    d.box(495, 60, 220, 70, "earlyvec.S stub 14", ["push vector (and a 0 if", "the CPU pushed no error code)"], "base", size=12)
    d.box(760, 60, 225, 70, "earlytrap(f)", ["print vector, name, rip,", "cr2 → panic()"], "new", size=12)
    d.arrow(205, 95, 248, 95); d.arrow(450, 95, 493, 95); d.arrow(715, 95, 758, 95)
    d.box(15, 170, 470, 90, "without it", ["no IDT entry → double fault → triple fault", "QEMU stops; a real PC reboots with no message"], "gray", size=12)
    d.box(515, 170, 470, 90, "with it", ["\"CPU exception 14 (page fault) ... rip ... cr2\"", "stays on screen: something a photo can show"], "new", size=12)
    return d.svg("early trap")


def pci():
    d = D(1000, 300, "pci.cpp: finding the USB controller on the PCI bus")
    d.bits(150, 60, 820, 32, [(31, 31, "enable", "new", 3), (30, 24, "", "gray", 3), (23, 16, "bus", "chg"), (15, 11, "device", "chg"), (10, 8, "func", "chg"), (7, 2, "register", "base"), (1, 0, "0", "gray", 2)], h=44, label="0xCF8 ←")
    d.text(560, 138, "outl(0xCF8, address); then inl(0xCFC) reads that 32-bit register of that function", 11.5)
    d.box(15, 170, 300, 100, "pciscan(class, found)", ["256 buses × 32 devices", "× (1 or 8) functions", "vendor 0xFFFF = nothing there"], "base", size=12)
    d.box(345, 170, 300, 100, "register 0x08 >> 8 = class", ["0x0C0330 = serial bus,", "USB, xHCI"], "base", size=12)
    d.box(675, 170, 310, 100, "found() → Xhci::init()", ["BAR0 (reg 0x10/0x14) =", "the controller's register address", "(QEMU: 0xC0_0000_0000)"], "new", size=12)
    d.arrow(315, 220, 343, 220); d.arrow(645, 220, 673, 220)
    return d.svg("pci")


def xhciinit():
    d = D(1000, 470, "Xhci::init(): the registers, and the memory the controller shares with the CPU")
    d.text(250, 50, "registers (BAR0, MMIO)", 12.5, True, color="#7d3c98")
    for i, (t, s) in enumerate([("capability", "ports, slots, sizes"), ("operational", "USBCMD run/reset, CRCR, DCBAAP"), ("ports (PORTSC × n)", "connected? speed? reset"), ("runtime: interrupter 0", "event ring base, ERDP"), ("doorbells", "db[0] commands, db[slot] devices")]):
        d.box(60, 65 + i * 62, 380, 50, t, [s], "hw", size=12)
    d.text(750, 50, "RAM pages from dmapage()", 12.5, True, color="#2874a6")
    for i, (t, s) in enumerate([("DCBAA", "a pointer per slot → device context"), ("command ring", "TRBs the CPU writes, controller reads"), ("event ring + segment table", "TRBs the controller writes, CPU reads"), ("scratchpad pages", "if the controller asks for some"), ("per device: contexts, ep0 ring, buffer", "made by newdev()")]):
        d.box(560, 65 + i * 62, 380, 50, t, [s], "mem", size=12)
    d.arrow(440, 152, 558, 90, "DCBAAP"); d.arrow(440, 160, 558, 152, "CRCR"); d.arrow(440, 276, 558, 214, "ERSTBA")
    d.box(15, 385, 970, 70, "init order", ["PCI: memory + bus master on → read BAR0 → handoff() from firmware → protocols() (USB 2/3 ports) → reset()",
                                           "→ DCBAA, command ring, event ring → USBCMD.RUN → power ports, mark all as \"look at me\""], "white", size=12)
    return d.svg("xhci init")


def ring():
    d = D(1000, 330, "A ring of TRBs (one 4 KB page = 256 × 16 bytes) and its cycle bit")
    for i in range(10):
        x = 40 + i * 92
        k = "new" if i < 4 else "gray"
        if i == 9:
            k = "chg"
        d.box(x, 70, 84, 60, "LINK" if i == 9 else f"TRB {i}", ["cycle 1" if i < 4 else ("→ TRB 0" if i == 9 else "cycle 0")], k, size=12)
    d.path("M914,130 L914,160 L82,160 L82,132")
    d.text(500, 180, "the last TRB links back to the first and flips the cycle bit for the next lap", 11.5, color="#566573")
    d.arrow(408, 230, 408, 133, "idx (next free)", lx=470, ly=222)
    d.box(15, 245, 470, 70, "producer (CPU, command ring)", ["write param, status, then control with the", "cycle bit last; then ring the doorbell"], "base", size=12)
    d.box(515, 245, 470, 70, "consumer (controller)", ["takes TRBs while their cycle bit = its own;", "a stale bit means \"not written yet\""], "hw", size=12)
    return d.svg("ring")


def enumerate_():
    d = D(1000, 560, "usbattach(): what happens when a device is found on a port")
    steps = [
        ("Enable Slot", "command ring", "the controller gives a slot number", "base"),
        ("newdev()", "dmapage × 5", "UsbDev, ep0 ring, input/output contexts, buffer", "base"),
        ("Address Device", "command ring", "controller sends SET_ADDRESS, starts endpoint 0", "base"),
        ("GET_DESCRIPTOR device (8, then 18 bytes)", "control transfer", "max packet size; vendor, product, class", "new"),
        ("GET_DESCRIPTOR configuration", "control transfer", "interfaces and endpoints", "new"),
    ]
    for i, (t, how, s, k) in enumerate(steps):
        y = 45 + i * 56
        d.box(15, y, 380, 46, t, [], k, size=12)
        d.text(410, y + 20, how, 11.5, True, "start", "#2874a6")
        d.text(410, y + 37, s, 11.5, anchor="start")
        if i:
            d.arrow(205, y - 10, 205, y - 1)
    d.box(15, 342, 300, 120, "class 9: a hub", ["SET_CONFIGURATION", "hub descriptor → sethub()", "power + reset each port", "→ usbattach() for each child"], "chg", size=12)
    d.box(345, 342, 300, 120, "a boot keyboard", ["(HID, subclass 1, protocol 1)", "Configure Endpoint (interrupt IN)", "SET_CONFIGURATION, SET_PROTOCOL", "queue the first report request"], "new", size=12)
    d.box(675, 342, 310, 120, "anything else", ["\"not a keyboard: ignored\"", "freedev(): Disable Slot,", "pages back to the free list"], "gray", size=12)
    d.line(205, 321, 205, 330, color="#7f8c8d", w=2); d.line(165, 330, 830, 330, color="#7f8c8d", w=2)
    d.arrow(165, 330, 165, 340); d.arrow(495, 330, 495, 340); d.arrow(830, 330, 830, 340)
    d.path("M15,440 L8,440 L8,68 L13,68", dash=True)
    d.text(165, 485, "recursion: a hub's children", 11.5, color="#b7950b")
    d.text(165, 501, "go through usbattach() too", 11.5, color="#b7950b")
    d.box(345, 485, 640, 60, "", ["the QEMU boot above: port 5 = a hub (class 9) → its port 1 = a keyboard", "the real PC: keyboard on root port 6 directly; two hubs, mouse, storage, Wi-Fi ignored"], "white", size=12)
    return d.svg("enumeration")


def control():
    d = D(1000, 300, "A control transfer: three TRBs on endpoint 0's ring (Xhci::control)")
    d.box(15, 60, 300, 90, "Setup TRB", ["8 bytes inside the TRB:", "reqtype, req, value, index, len"], "base", size=12)
    d.box(345, 60, 300, 90, "Data TRB (if len > 0)", ["points at d.buf;", "IN: the device fills it"], "base", size=12)
    d.box(675, 60, 310, 90, "Status TRB", ["the other direction;", "IOC: \"tell me when done\""], "base", size=12)
    d.arrow(315, 105, 343, 105); d.arrow(645, 105, 673, 105)
    d.box(15, 180, 470, 90, "ring doorbell db[slot] = 1", ["then wait(): call poll() until a Transfer Event", "for this slot's endpoint 0 sets d.ctldone"], "chg", size=12)
    d.box(515, 180, 470, 90, "result", ["SUCCESS: copy d.buf to the caller", "STALL: the device says \"not supported\";", "Reset Endpoint + Set TR Dequeue to recover"], "white", size=12)
    return d.svg("control transfer")


def keypress():
    d = D(1000, 560, "Pressing 'a' on a USB keyboard, start to finish")
    steps = [
        ("keyboard", "a report: 00 00 04 00 00 00 00 00", "byte 0 = modifiers, bytes 2-7 = keys down (0x04 = A)", "hw"),
        ("xHCI", "copies it to d.report (DMA)", "it was asking the keyboard every interval (queuein)", "hw"),
        ("xHCI", "writes a Transfer Event TRB", "on the event ring, with its cycle bit", "hw"),
        ("main loop", "usbintr() → service() → poll()", "a TRB with the expected cycle bit = new", "chg"),
        ("Xhci::event()", "type 32, this slot, keyboard's dci", "→ usbkbdreport(), then queuein() again", "base"),
        ("usbkbdreport()", "0x04 was not in prev[] → new key", "usbkey(0x04, 0) = usbmap[0][4] = 'a'", "new"),
        ("consoleintr('a')", "echo + store in cons.buf", "consputc('a') → screen and serial", "new"),
        ("release", "a report with no keys: 00 00 00 …", "nothing new → nothing typed; prev[] updated", "gray"),
    ]
    for i, (who, t, s, k) in enumerate(steps):
        y = 45 + i * 62
        d.box(15, y, 160, 50, who, [], k, size=12)
        d.box(190, y, 360, 50, t, [], k, size=11.5, mono=True)
        d.text(565, y + 30, s, 11.5, anchor="start")
        if i:
            d.arrow(95, y - 12, 95, y - 1)
    d.text(500, 548, "holding a key does not repeat it: the keyboard sends no new report, and repeating needs a timer (a later step)", 11.5, color="#566573")
    return d.svg("keypress")


def notyet():
    d = D(1000, 300, "What step-10 has, and what the next 32 steps add")
    have = [("boot", "new"), ("console out", "new"), ("PS/2 + serial in", "new"), ("USB keyboard", "new")]
    nxt = [("11-14 memory: spinlock, kalloc, page tables (vm)", "gray"), ("15-19 traps, interrupts: ACPI, IDT, LAPIC, IOAPIC", "gray"),
           ("20-26 processes, scheduler, system calls, several CPUs", "gray"), ("27-33 file system (fs.img as a RAM disk)", "gray"),
           ("34-39 user programs, shell, usertests", "gray"), ("40-42 C++ cleanup, real PC, v1.0-cpp", "gray")]
    d.text(130, 50, "at step-10", 12.5, True, color="#1e8449")
    for i, (t, k) in enumerate(have):
        d.box(30, 62 + i * 52, 200, 42, t, [], k, size=12)
    d.text(610, 50, "to come (from the progress page)", 12.5, True, color="#566573")
    for i, (t, k) in enumerate(nxt):
        d.box(300, 62 + i * 38, 620, 32, t, [], k, size=12, rx=4)
    return d.svg("what is not here yet")


def threemachines():
    d = D(1000, 470, "One usb.img, three machines: the same bytes boot on all of them")
    d.box(370, 45, 260, 60, "usb.img", ["BOOTX64.EFI + kernel + fs.img"], "mem", size=12.5)
    cols = [("QEMU (make qemu)", "hw", ["firmware: OVMF (UEFI)", "screen: 1280×800 → 16×32 font", "serial: COM1 → your terminal",
                                       "PS/2: emulated", "xHCI: only with USB=1", "RAM: 512 MB"]),
            ("VirtualBox (make vbox)", "hw", ["firmware: VirtualBox EFI", "screen: 2560×1440 → 32×64 font", "serial: COM1 → vbox/serial.log",
                                              "PS/2: emulated (the window)", "xHCI: none (needs ext. pack)", "RAM: 512 MB, 2 CPUs (1 used)"]),
            ("real PC (barebone)", "new", ["firmware: the board's UEFI", "screen: the monitor's mode", "serial: none (reads 0xFF)",
                                          "PS/2: none (reads junk)", "xHCI: Intel 8086:7a60, 25 ports", "RAM: 32 GB"])]
    for i, (t, k, ls) in enumerate(cols):
        x = 15 + i * 330
        d.path(f"M500,105 L500,125 L{x + 152},125 L{x + 152},143")
        d.box(x, 145, 305, 190, t, ls, k, size=12.5)
    d.box(15, 360, 970, 90, "how the same code copes", ["the UEFI standard hides the firmware differences from the loader; the loader writes what it found into bootinfo",
                                                         "the kernel then asks the hardware at run time (no #ifdef): screen size from bootinfo, devices from PCI, missing ports read 0xFF"], "white", size=12)
    return d.svg("three machines")


def runtime():
    d = D(1000, 520, "Compile time vs run time: where the kernel decides, and what it looks at")
    rows = [("which screen, how big?", "bootinfo.fb_base / fb_width (from UEFI GOP)", "fb_base = 0 → serial only; width ≥ 2560 → big font", "fbcons.cpp"),
            ("how much RAM, where?", "bootinfo memory map (from UEFI)", "dmapage() uses whatever regions are free", "xhci.cpp"),
            ("is there a serial port?", "inb(0x3F8 + 5): 0xFF means nothing there", "output thrown away, input ignored", "uart.cpp"),
            ("is there a PS/2 keyboard?", "inb(0x64): 0xFF or junk", "≤ 16 bytes per call; status 0xFF → none", "kbd.cpp"),
            ("is there a USB controller?", "PCI scan for class 0x0C0330", "none found → \"usb: no xHCI controller\"", "pci.cpp"),
            ("where are its registers?", "PCI BAR0, then capability registers", "QEMU 0xC0_0000_0000, real PC 0x60_0110_0000", "xhci.cpp"),
            ("how many ports, scratchpad?", "HCSPARAMS1/2 registers", "QEMU 8 ports / 0 pages; real PC 25 / 34", "xhci.cpp"),
            ("does the firmware still own it?", "USB Legacy Support capability", "BIOS-owned bit set → ask it to let go", "xhci.cpp"),
            ("Intel 7/8/9 series chipset?", "PCI vendor/device ID", "route sockets to xHCI, else skip", "xhci.cpp")]
    d.text(160, 52, "question", 12, True, color="#2c3e50"); d.text(450, 52, "what the code reads", 12, True, color="#2c3e50")
    d.text(760, 52, "what happens", 12, True, color="#2c3e50")
    for i, (q, how, what, f) in enumerate(rows):
        y = 62 + i * 46
        d.box(15, y, 290, 38, q, [], "base", size=11.5, rx=4)
        d.text(320, y + 17, how, 11.5, anchor="start")
        d.text(320, y + 33, f, 11.5, anchor="start", mono=True, color="#7f8c8d")
        d.text(985, y + 24, what, 11.5, anchor="end", color="#1e8449")
    d.text(500, 500, "the binary is identical everywhere; only the answers differ. No #ifdef QEMU anywhere in the kernel", 12, True, color="#2c3e50")
    return d.svg("runtime detection")
