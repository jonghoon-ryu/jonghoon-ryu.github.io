from svg import D

DELETED = ("acpi.c bio.c buf.h console.c defs.h elf.h entryother.S exec.c fbcons.c fcntl.h file.c file.h font.h fs.c fs.h "
           "ioapic.c kalloc.c kbd.c kbd.h kernelvec.S lapic.c log.c main.c pipe.c printk.c proc.c proc.h ramdisk.c "
           "sleeplock.c sleeplock.h spinlock.c spinlock.h start.c stat.h string.c swtch.S syscall.c syscall.h sysfile.c "
           "sysproc.c trampoline.S trap.c uart.c vm.c vm.h").split()


def files():
    d = D(1000, 380, "kernel/ in step-01: almost every kernel file deleted, only the boot skeleton kept")
    x0, y0, w, h = 20, 50, 118, 26
    for i, f in enumerate(DELETED):
        d.box(x0 + (i % 8) * (w + 4), y0 + (i // 8) * (h + 4), w, h, "", [f], "del", size=11.5, rx=3)
    y = y0 + 6 * (h + 4) + 20
    d.text(20, y, "kept (unchanged or slightly changed)", 12, True, "start", "#2c3e50")
    keep = [("entry.S", "chg"), ("kernel.ld", "chg"), ("x86.h", "chg"), ("bootinfo.h", "base"), ("memlayout.h", "base"), ("param.h", "base"), ("types.h", "base"), ("boot/loader.c", "chg"), ("boot/efi.h", "chg")]
    for i, (f, k) in enumerate(keep):
        d.box(20 + i * 108, y + 12, 102, 28, "", [f], k, size=11.5, rx=3)
    d.legend(640, y, (("new", "new"), ("chg", "changed"), ("del", "deleted")))
    y += 70
    d.text(20, y, "new (C++)", 12, True, "start", "#2c3e50")
    d.box(20, y + 12, 150, 28, "", ["start.cpp"], "new", size=12, rx=3)
    d.box(178, y + 12, 150, 28, "", ["main.cpp"], "new", size=12, rx=3)
    d.text(345, y + 31, "also deleted: 26 files in user/ and mkfs/mkfs.c (they return in the plan's parts 6 and 7)", 11, False, "start")
    return d.svg("files in step-01")


def flow():
    d = D(1000, 250, "What runs in step-01: loader → entry.S → start() → main() → hlt")
    items = [("boot/loader.c", ["reads kernel, fs.img", "fills bootinfo"], "chg"), ("entry.S", ["sets a stack", "call start"], "base"),
             ("start.cpp", ["copies bootinfo", "runs global constructors"], "new"), ("main.cpp", ["two lines on COM1", "paints the screen, \"xv6\""], "new"), ("for (;;) hlt", ["CPU rests"], "gray")]
    x = 15
    for i, (t, ls, k) in enumerate(items):
        d.box(x, 60, 180, 80, t, ls, k)
        if i:
            d.arrow(x - 18, 100, x - 1, 100)
        x += 198
    d.box(15, 165, 970, 65, "Nothing that the C version's main() did (kinit, kvminit, trapinit, …, scheduler) is left", [
        "The next steps bring it back in C++, one piece at a time, and the kernel always boots in between"], "white", size=12.5)
    return d.svg("execution flow of step-01")


def ctors():
    d = D(1000, 270, "Constructors of C++ global objects: with no runtime, start() calls them itself")
    d.box(20, 60, 260, 100, "compiler (g++)", ["for each global object, emits", "a function that runs its constructor,", "and puts its address in .init_array"], "base")
    d.box(330, 60, 300, 100, "kernel.ld (linker script)", ["gathers .init_array and defines", "__init_array_start", "__init_array_end"], "chg")
    d.box(680, 60, 300, 100, "start.cpp: start()", ["for (ctor = start; ctor != end; ctor++)", "  (*ctor)();", "main();"], "new", mono=True)
    d.arrow(280, 110, 328, 110); d.arrow(630, 110, 678, 110)
    d.box(20, 185, 960, 65, "In an ordinary C++ program", ["the C runtime (crt0, __libc_start_main) does this before main(). A kernel has no such runtime.",
                                                         "kernel.ld also lost the trampoline section (trampsec): it returns with trampoline.S in Step 23"], "white", size=12)
    return d.svg("running global constructors")


def usbimg():
    d = D(1000, 230, "usb.img: a disk a real PC can boot (GPT + EFI System Partition)")
    d.box(20, 60, 140, 80, "GPT", ["protective MBR,", "partition table"], "hw", size=12.5)
    d.box(160, 60, 560, 80, "partition 1: EFI System (FAT32, 64 MB) = esp.img", ["EFI/BOOT/BOOTX64.EFI (loader)   /kernel   /fs.img"], "new", size=12.5)
    d.box(720, 60, 120, 80, "GPT backup", [], "hw", size=12)
    for x, t, a in ((20, "0", "start"), (160, "1MB", "start"), (720, "65MB", "start"), (840, "66MB", "end")):
        d.text(x, 165, t, 10.5, False, a, "#566573", True)
    d.box(870, 55, 115, 90, "", ["QEMU,", "VirtualBox and", "real PCs all", "boot this image"], "white", size=11.5)
    d.text(500, 205, "Makefile: sgdisk writes the table, dd puts esp.img at 1 MB. To a USB stick: sudo dd if=usb.img of=/dev/sdX", 11)
    return d.svg("layout of usb.img")


def mangle():
    d = D(1000, 260, "Name mangling: C++ puts the parameter types into a function's name")
    d.box(20, 55, 300, 70, "the function in start.cpp", ["void start(struct bootinfo *bi)"], "base", size=12.5, mono=True)
    d.box(400, 40, 280, 50, "without extern \"C\"", ["_Z5startP8bootinfo"], "del", size=12.5, mono=True)
    d.box(400, 105, 280, 50, "with extern \"C\"", ["start"], "new", size=12.5, mono=True)
    d.arrow(320, 85, 398, 65); d.arrow(320, 95, 398, 130)
    d.box(740, 40, 240, 115, "entry.S", ["call start", "", "assembly knows only C names", "→ extern \"C\" is needed"], "chg", size=12.5)
    d.text(500, 190, "_Z 5start P 8bootinfo = \"start, a name of length 5, taking a pointer (P) to bootinfo\"   (c++filt decodes it)", 11.5)
    d.text(500, 215, "stack0 is extern \"C\" for the same reason. main() is the exception: the language never mangles it", 11.5)
    return d.svg("name mangling")


def pipeline():
    d = D(1000, 330, "Building: source → kernel ELF → disk image (step-01's Makefile)")
    d.box(20, 50, 170, 60, "*.cpp", ["start, main"], "new", size=12.5)
    d.box(20, 130, 170, 60, "entry.S", [], "base", size=12.5)
    d.box(230, 50, 220, 60, "g++ -std=c++20", ["-fno-exceptions -fno-rtti …"], "chg", size=12, mono=True)
    d.box(230, 130, 220, 60, "gcc (assembler)", [], "base", size=12)
    d.box(490, 90, 160, 60, "*.o", [], "gray", size=12.5, mono=True)
    d.box(690, 90, 140, 60, "ld", ["-T kernel.ld"], "chg", size=12.5, mono=True)
    d.box(860, 90, 120, 60, "kernel", ["ELF, 0x100000"], "base", size=12)
    d.arrow(190, 80, 228, 80); d.arrow(190, 160, 228, 160); d.arrow(450, 80, 488, 112); d.arrow(450, 160, 488, 128)
    d.arrow(650, 120, 688, 120); d.arrow(830, 120, 858, 120)
    d.box(20, 220, 200, 60, "boot/loader.c", ["clang + lld-link (PE)"], "chg", size=12)
    d.box(250, 220, 170, 60, "BOOTX64.EFI", [], "base", size=12, mono=True)
    d.box(460, 220, 200, 60, "esp.img (FAT32)", ["BOOTX64.EFI, kernel, fs.img"], "base", size=11.5)
    d.box(700, 220, 280, 60, "usb.img (GPT)", ["booted by QEMU, VirtualBox, real PCs"], "new", size=12)
    d.arrow(220, 250, 248, 250); d.arrow(420, 250, 458, 250); d.arrow(660, 250, 698, 250)
    d.path("M920,150 L920,190 L560,190 L560,218")
    return d.svg("build pipeline")
