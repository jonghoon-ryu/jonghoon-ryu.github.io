---
layout: default
title: Code explanation up to step 10
permalink: /xv6/tutorial/code-explanation-step-10/
---
<style>
.check { background:#f7f9fb; border-left:4px solid #5d6d7e; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.tip { background:#eef8f1; border-left:4px solid #1e8449; padding:10px 14px; margin:1.2rem 0; font-size:0.92rem; }
.step-nav { display:flex; justify-content:space-between; gap:1rem; margin:2rem 0 0; font-size:0.95rem; }
table { font-size:0.88rem; }
.subtitle { font-size:1.35rem; color:#555; margin:-6px 0 18px; }
</style>

# Code explanation up to step 10

<p class="subtitle">What the program does at tag step-10, from power-on to a typed key</p>

The other tutorial pages each explain **one tag's changes**. This page explains **the whole program as it stands at `step-10`**: the files, what runs in what order, and how a key you press ends up on the screen. You don't need to study every line. The aim is a clear mental picture of the starting point before Step 11 (spinlock), where the real operating system parts start coming back.

| | |
|---|---|
| **Tag** | `step-10` (commit `c9bbb18`, the same code as branch `cpp` today) |
| **Size** | the UEFI loader (`boot/`, 578 lines) and the kernel (`kernel/`, 3,646 lines in 24 files) |
| **In one line** | boots on a UEFI PC, prints what it learned about the machine, finds the keyboards (PS/2, serial, USB) and echoes every key you type. Nothing else yet |

```sh
cd ~/Ryu/xv6-x86_64
git checkout step-10
make clean && make qemu            # PS/2 keyboard in the QEMU window, serial in the terminal
make clean && make qemu USB=1      # adds a USB controller, a hub, and a USB keyboard behind it
```

## 1. The whole picture

@@FIG code10 bigpicture@@

The program has three stages.

1. **The loader** (`boot/loader.c`). This is a small UEFI application, the file the PC's firmware runs from the USB stick. It copies the kernel into memory, collects facts about the machine into `struct bootinfo`, shuts down the firmware's services and jumps to the kernel.
2. **Kernel start-up** (`entry.S` → `start()` → `main()`). It gives the CPU a stack, copies `bootinfo`, then `main()` sets up each device in turn: the console, the exception screen, the PS/2 keyboard, the USB controller.
3. **The loop.** `main()` never returns. It asks the three input devices "anything new?" over and over, and hands every character to `consoleintr()`, which echoes it to the screen and the serial port.

Just as important is what is **missing**. Compared with the full C version on branch `main`:
- There are no interrupts. The CPU's interrupt flag is cleared in `entry.S` and never set again.
- There is no memory allocator and no page table of the kernel's own.
- There are no processes, no system calls, no file system and no user programs.

The kernel runs on one CPU in kernel mode, inside the page tables the firmware left behind. That is enough to boot and show text, and nothing more is needed yet.

<div class="check" markdown="1">
**Why is so much of it about USB?** The original plan had only the console (steps 1–5) here. When the kernel was first tried on the real PC (the barebone), it turned out to have no PS/2 keyboard controller, and its firmware stops emulating one when the kernel starts. So steps 6–10 added a USB keyboard driver, and the kernel can now be typed at on that machine. That driver (`pci.cpp`, `xhci.cpp`, `usb.cpp`) is a third of the kernel, and it is **not** in the C version.
</div>

## 2. The files

@@FIG code10 filemap@@

| Group | File | What it is |
|---|---|---|
| Boot | `boot/loader.c`, `boot/efi.h` | the UEFI loader (C, built by clang as a Windows-style `.EFI` file) and the UEFI definitions it needs |
| | `kernel/entry.S` | the kernel's first instructions: interrupts off, a stack, call `start()` |
| | `kernel/start.cpp` | copies `bootinfo`, runs C++ global constructors, calls `main()` |
| | `kernel/kernel.ld` | the linker script: the kernel starts at `0x100000`, `entry.o` first |
| | `kernel/bootinfo.h` | `struct bootinfo`, shared by the loader and the kernel |
| Output | `uart.cpp` | the serial port (16550 UART at I/O port `0x3F8`) |
| | `fbcons.cpp`, `font.h` | text on the screen: draws font bitmaps into the frame buffer |
| | `console.cpp` | `consputc()` (one char to both outputs), `consoleintr()` (input line editing) |
| | `printk.cpp` | `printk()` (the kernel's `printf`) and `panic()` |
| Input | `kbd.cpp`, `kbd.h` | the PS/2 keyboard: scancodes → characters |
| Safety net | `earlytrap.cpp`, `earlyvec.S` | prints CPU exceptions on the screen instead of a silent reboot |
| USB | `pci.cpp` | reads and writes PCI configuration space; scans for a device class |
| | `xhci.cpp`, `xhci.h` | the USB 3 host controller (xHCI): rings, commands, events, ports |
| | `usb.cpp` | USB devices: descriptors, hubs, keyboards, key reports → characters |
| Shared | `main.cpp` | the order of everything, and the loop |
| | `x86.h` | x86-64 helpers: `inb`/`outb`, `rdtsc`, `microdelay`, `lidt`, page-table macros |
| | `defs.h` | one declaration per function other files use |
| | `string.cpp` | `memset`, `memmove`, `strlen`… (there is no C library) |
| | `types.h`, `param.h`, `memlayout.h` | integer types, limits (`NCPU` …), memory addresses (`KERNBASE`, `PHYSTOP`) |

Some headers describe things that aren't there yet: `memlayout.h` already defines `TRAMPOLINE` and `KSTACK`, `param.h` defines `NPROC` and `NFILE`, and `x86.h` defines the GDT selectors. They were kept from the C version so that later steps only need to add code.

## 3. Building: what `make` produces

@@FIG code10 build@@

Two different compilers are needed:
- **The loader** is built with `clang -target x86_64-unknown-windows` and `lld-link`, because UEFI runs **PE** files (the Windows executable format) and uses the Microsoft calling convention.
- **The kernel** is built with the normal Linux `g++`/`gcc` and `ld` into an **ELF** file, using the flags that make it freestanding:

@@CODE step-10 | Makefile | ^# flags shared by C\+\+ and assembly | ^CXXFLAGS \+= -Wno-main@@

The important ones:
- **`-ffreestanding -nostdlib`**: there is no C library and no operating system underneath; the kernel *is* the bottom layer.
- **`-mno-red-zone`**: an interrupt would overwrite the 128 bytes below the stack pointer that normal user programs may use.
- **`-mgeneral-regs-only`**: no SSE/floating point registers, which the kernel would otherwise have to save on every switch.
- **`-fno-exceptions -fno-rtti -fno-threadsafe-statics -fno-use-cxa-atexit`**: C++ features that need runtime support the kernel doesn't have.

`fs.img` is a 1 KB placeholder: the loader insists on loading one, and the real file system comes back in steps 27–33. `esp.img` is a 64 MB FAT32 partition with the three files, and `usb.img` wraps it in a GPT partition table so that a real PC's firmware accepts it as a bootable USB stick.

## 4. Stage 1: the UEFI loader

When a UEFI PC starts, its firmware initializes the hardware, then looks for `EFI/BOOT/BOOTX64.EFI` on a FAT partition and runs it. At that point the CPU is already in **64-bit mode with paging on**, and every address is mapped to itself (virtual = physical). That is a big difference from the old x86 xv6, which started in 16-bit mode from a 512-byte boot sector. The loader can call firmware services: read files, allocate memory, query the screen.

@@FIG code10 loader@@

Step 4, `loadkernel()`, is a small ELF loader. The kernel file has *program headers* that say "copy these bytes of the file to this physical address". The loader first reserves exactly that memory from the firmware (so nothing else is there), then copies:

@@CODE step-10 | boot/loader.c | ^  for \(int i = 0; i < elf->phnum; i\+\+\) \{$ | ^  return elf->entry;@@

The memory is reserved as `EfiLoaderCode`, not `EfiLoaderData`: newer PC firmware maps data pages as no-execute, and the kernel will run from these pages inside the firmware's page tables.

The last step leaves the firmware. `ExitBootServices()` only succeeds if the caller has the newest memory map, which the call to `GetMemoryMap()` itself can change, hence the retry loop. After it succeeds, the firmware's services are gone for good. The loader then calls the kernel with `sysv_abi`, so that the pointer to `bootinfo` arrives in `%rdi` as `g++` code expects:

@@CODE step-10 | boot/loader.c | ^  for \(int tries = 0;; tries\+\+\) \{ | ^}@@

### What the loader hands over: `struct bootinfo`

@@FIG code10 bootinfo@@

Only the memory map and the frame buffer fields are used at step-10. The others (the file system image, the ACPI pointer and the page for starting other CPUs) are collected now so that the loader doesn't have to change later.

## 5. Memory while the kernel runs

@@FIG code10 memory@@

The QEMU boot log below gives the real addresses: the kernel occupies `0x100000`–`0x1181d8` (about 97 KB), `fs.img` sits just under 128 MB, and the screen's frame buffer is at `0x80000000`. Note the following:

- **Paging is on, but the kernel did not set it up.** It runs inside the firmware's page tables, which map every RAM address (and most device addresses) to itself. Step 13–14 (`vm.cpp`) builds the kernel's own. Until then, `xhci.cpp` checks with `ismapped()` that the controller's registers are reachable before touching them. A real PC's firmware does not have to map them.
- **`PHYSTOP` = 128 MB** is the limit the kernel will use for its own page allocator later (`kalloc`, step 12). The USB driver needs pages now, so it has a tiny allocator of its own, `dmapage()`. It takes free RAM from the UEFI memory map, preferably *above* `PHYSTOP` and below 4 GB, so it never collides with what `kalloc` will hand out.
- **Device memory**: the frame buffer and the xHCI registers are not RAM. Writing to the frame buffer changes pixels; reading or writing the xHCI addresses talks to the USB controller. This is called memory-mapped I/O (MMIO). The UART and the PS/2 controller use the older **I/O ports** instead (`inb`/`outb` instructions).

## 6. Stage 2: from `_entry` to `main()`

@@FIG code10 startpath@@

@@CODE step-10 | kernel/entry.S | ^_entry: | ^        jmp spin@@

`cli` turns interrupts off, and they stay off for the whole of step-10: there is no IDT entry that could handle a device interrupt yet. `stack0` is a global array in `start.cpp` (4 KB per CPU, `NCPU` = 8). Only CPU 0 runs, so only the first 4 KB is used.

@@CODE step-10 | kernel/start.cpp | ^start\(struct bootinfo \*bi\) | ^}@@

Two things happen before `main()`:
1. **`bootinfo` is copied** into the kernel's own global variable. The loader's copy is in memory the firmware called "loader data", which the kernel may reuse later.
2. **Global constructors run.** In a normal C++ program, the C++ runtime calls constructors of global objects before `main()`. There is no runtime here, so `kernel.ld` collects their addresses in `.init_array` and `start()` calls each one. (At step-10 the globals are plain data with no constructors, so the list is empty, but the mechanism is in place.)

Then `main()`:

@@CODE step-10 | kernel/main.cpp | ^main\(\) | ^}@@

## 7. Output: `printk()` → screen and serial port

@@FIG code10 output@@

Every character the kernel prints goes through `consputc()`:

@@CODE step-10 | kernel/console.cpp | ^consputc\(int c\) | ^}@@

**The serial port** (`uart.cpp`) is the 16550 UART chip of old PCs, at I/O port `0x3F8` (COM1). `uartinit()` sets 38400 baud, 8 data bits, no parity, and turns on its FIFO buffers. To send a byte, `uartputc_sync()` waits until the *Line Status Register* says the transmitter is empty (bit 5), then writes the byte:

@@CODE step-10 | kernel/uart.cpp | ^uartputc_sync\(int c\) | ^}@@

QEMU and VirtualBox emulate this chip: `make qemu` connects it to your terminal, which is why you see the boot messages there. Most real PCs have no COM1. Reading a missing I/O port returns `0xFF`, and with every bit set, bit 5 reads as "ready". Output simply disappears instead of hanging. This is also why the screen is drawn *first*.

**The screen** (`fbcons.cpp`). The loader found the frame buffer through UEFI's Graphics Output Protocol: a block of memory where each 32-bit word is one pixel. To show text, the kernel draws every character itself, from a bitmap font (Spleen, in `font.h`):

@@FIG code10 glyph@@

`fbconsputc()` handles the cursor position: newline, carriage return, backspace, tab, wrapping at the right edge, and scrolling at the bottom. Scrolling copies every pixel of the screen up by one text line, which is slow for a big screen, but simple.

**`printk()`** (`printk.cpp`) is a small `printf`: it walks the format string and sends plain characters to `consputc()`, formatting `%d`, `%u`, `%x` (also with `l`/`ll`), `%p`, `%s`, `%c`. `g++` checks every call's arguments against its format string (`__attribute__((format(printf, 1, 2)))` in `defs.h`), something the C version did not do. `panic()` prints its message and spins forever.

## 8. Input: the polling loop

@@FIG code10 loop@@

At the end of `main()`, the CPU circles through three functions forever. Each one checks its device and returns immediately if nothing is waiting. This is **polling**: the CPU is 100 % busy even when nobody types. Later steps switch to **interrupts**, where the device signals the CPU, which can sleep in between: steps 15–18 bring back the IDT, the local APIC, the I/O APIC and UART interrupts, and step 19 the keyboard interrupt.

All three paths end in the same function:

@@CODE step-10 | kernel/console.cpp | ^consoleintr\(int c\) | ^}@@

`consoleintr()` is the line editor. It echoes each character, handles backspace and Ctrl-U (erase the whole line) and keeps the line in a 128-byte circular buffer with three positions: `e` where editing happens, `w` the end of the last complete line, `r` what a reader has consumed. In the C version a reader, `consoleread()`, would be woken up when a line is complete. There are no processes to wake yet, so a finished line is simply dropped (`r = w`), which keeps the buffer from filling up.

### The PS/2 keyboard

@@FIG code10 ps2@@

The PS/2 keyboard controller has two I/O ports: `0x64` (status: bit 0 = "a byte is waiting") and `0x60` (the byte). The keyboard sends **scancodes**, numbers for key positions, separately for press and release (release = press + `0x80`). `kbdgetc()` keeps track of Shift, Ctrl, Alt and the lock keys, and looks the scancode up in one of four tables. This code comes from the old x86 xv6.

`kbdinit()` turns the PS/2 *mouse* off first: mouse bytes go through the same one-byte buffer, and unread ones would block the keyboard. `kbdintr()` reads at most 16 bytes per call, because on some PCs without a controller the status port reads "byte waiting" forever, and the loop must still reach the USB keyboard.

### The serial port

`uartintr()` reads bytes while the UART's *Line Status Register* bit 0 says one is waiting. With `make qemu`, what you type in the terminal arrives here. A missing UART reads `0xFF`, which `uartgetc()` treats as "nothing".

## 9. The safety net: early exceptions

@@FIG code10 earlytrap@@

If the kernel touches a bad address, the CPU raises an **exception** and looks up its handler in the **IDT** (interrupt descriptor table). The firmware's IDT can't be relied on after `ExitBootServices()` (its handlers live in memory the firmware has given up), and the kernel's own comes back only in step 16 (`trap.cpp`). With no valid handler, the exception escalates to a double fault and then a **triple fault**: QEMU stops, and a real PC just reboots, with no message at all.

So step 6 added a minimal IDT with 32 entries, one per CPU exception. Each points to a 16-byte stub in `earlyvec.S` that pushes the vector number and jumps to `earlytrap()`, which prints the exception's name, the instruction address (`rip`) and, for a page fault, the faulting address (`cr2`), then panics. On a real PC this is what makes a crash something you can photograph and debug.

## 10. The USB keyboard

This is the largest part of the kernel. USB devices don't sit at fixed addresses; the CPU talks to a **host controller** (xHCI, for USB 3 controllers, which also handle USB 2 and 1 devices), and the controller talks to the devices. Getting from "power on" to "a key report arrives" takes five layers, one per step:

| Layer | Step | File | Job |
|---|---|---|---|
| PCI | 6 | `pci.cpp` | find the controller and its register address |
| controller | 7 | `xhci.cpp` | take it from the firmware, reset it, give it its rings in memory, start it |
| devices | 8 | `usb.cpp` + `xhci.cpp` | for each connected port: a slot, an address, descriptors (what is it?) |
| keyboard | 9 | `usb.cpp` | configure its interrupt endpoint, receive 8-byte reports, convert to characters |
| hubs | 10 | `usb.cpp` + `xhci.cpp` | devices behind hubs (route string, transaction translator) |

### 10.1 Finding the controller: PCI

@@FIG code10 pci@@

Every PCI device has a 256-byte *configuration space*: who made it (vendor and device ID), what it is (a class code) and where its registers are (the BARs, base address registers). PCs read it through two I/O ports: write an address to `0xCF8`, read the data at `0xCFC`. `pciscan()` simply tries every bus, device and function, 8,192 probes, and calls `found()` for each function whose class is `0x0C0330` (serial bus controller, USB, xHCI).

### 10.2 Starting the controller: xHCI

@@FIG code10 xhciinit@@

The controller has four groups of registers (from BAR0), and it works on data structures **in RAM** that both it and the CPU read and write. This is *DMA*, direct memory access. The important ones:

- **The command ring**: the CPU writes commands ("enable a slot", "address this device", "configure an endpoint") and rings **doorbell 0**.
- **The event ring**: the controller writes events: "command finished", "a port changed", "a transfer finished".
- **The DCBAA**: one pointer per device slot to that device's *context*, the controller's record of the device and its endpoints.
- **One transfer ring per endpoint** of every device: the CPU puts transfer requests there and rings that device's doorbell.

Before using the controller, `handoff()` asks the firmware to let go of it: the firmware used it for its own keyboard support before the kernel started. `protocols()` learns which ports are USB 2 and which are USB 3, because each physical USB 3 socket appears as two ports. QEMU's controller lists its USB 2 ports after its USB 3 ports, which is why the keyboard hub appears as **port 5** in the boot log.

### 10.3 Rings and the cycle bit

@@FIG code10 ring@@

Every ring is one 4 KB page of 16-byte **TRBs** (transfer request blocks). How does the controller know which TRBs are new? Each TRB has a **cycle bit**. On the first lap around the ring, new TRBs have cycle = 1. The last TRB is a *link* back to the start, and following it flips the expected value, so on the second lap new TRBs have cycle = 0, and so on. A TRB whose cycle bit is "from the previous lap" hasn't been written yet. `Ring::push()` writes the cycle bit **last**, so the controller can never see a half-written TRB:

@@CODE step-10 | kernel/xhci.cpp | ^Ring::push\(uint64 param | ^}@@

The event ring works the same way in the other direction: `Xhci::poll()` reads events while their cycle bit matches the expected one, then tells the controller how far it has read (`ERDP`).

### 10.4 Setting up a device

@@FIG code10 enumerate_@@

When a port reports a connected device, `portchange()` skips USB 3 ports (keyboards are USB 2 devices), resets the port (a USB 2 port is enabled only by a reset), reads the device's speed and calls `usbattach()`. Each device gets one try per connection: unplug and replug to try again. Talking to a new device always goes through **endpoint 0** with **control transfers**, standard requests every USB device understands:

@@FIG code10 control@@

The device's descriptors decide what happens next: a **hub** (class 9) gets its ports powered and reset, and each connected port goes through `usbattach()` again (recursion, up to 5 hubs deep). A **boot keyboard** (HID class, boot subclass, keyboard protocol) gets its interrupt endpoint configured. **Anything else** (mouse, storage, Wi-Fi…) is ignored and its slot given back. Devices plugged into a hub *after* boot are not noticed: the kernel doesn't watch hubs yet.

### 10.5 From a key press to a character

@@FIG code10 keypress@@

A keyboard in **boot protocol** sends a fixed 8-byte report whenever the set of pressed keys changes: byte 0 has the modifier keys (Ctrl, Shift, Alt, GUI; left and right), and bytes 2–7 hold up to six keys that are down, as HID *usage IDs* (`0x04` = A, `0x05` = B, …). `usbkbdreport()` compares each report with the previous one and turns every **newly pressed** key into a character:

@@CODE step-10 | kernel/usb.cpp | ^usbkbdreport\(UsbDev &d, int len\) | ^}@@

## 11. What you see

QEMU with `make qemu USB=1` (serial output, firmware lines removed). The loader's lines come first, then the kernel's:

```
xv6 loader
  kernel: 0x0000000000100000 - 0x00000000001181d8
  screen: 1280x800, frame buffer at 0x0000000080000000, pixel format 1
  ACPI: 0x000000001f77e014
starting kernel
xv6 kernel is booting (C++, step 10)
screen: 1280x800, frame buffer at 0x0000000080000000
ACPI root pointer at 0x000000001f77e014
fs.img: 1024 bytes at 0x0000000007ffe000
UEFI memory map: 131 entries
  reserved: 3211392 pages (12544 MB)
  loader code: 48 pages (0 MB)
  loader data: 69 pages (0 MB)
  boot services code: 1030 pages (4 MB)
  boot services data: 10204 pages (39 MB)
  runtime code: 256 pages (1 MB)
  runtime data: 581 pages (2 MB)
  free: 118129 pages (461 MB)
  ACPI tables: 18 pages (0 MB)
  ACPI NVS: 513 pages (2 MB)
  MMIO: 1024 pages (4 MB)
xhci0: PCI 0:3.0, vendor 1b36 device d, registers at 0x000000c000000000
xhci0: version 100, 8 ports, 32 slots, 32-byte contexts, 0 scratchpad pages
usb: port 5: full speed, id 409:55aa, class 9, a hub
usb: port 5.1: full speed, id 627:1, class 0, a keyboard
usb: keyboard ready: type on it
type on the keyboard (or the serial console):
```

- **"loader code: 48 pages"** is the kernel itself, reserved as `EfiLoaderCode` (97 KB is 25 pages; the loader's own code is the rest).
- **"free: 461 MB"**: RAM nobody uses yet. `kalloc` (step 12) will hand it out.
- **"reserved: 12544 MB"** is not RAM: QEMU's firmware reserves address space for PCI devices.
- **Class 0** for the keyboard means "see the interface descriptors", where the HID boot keyboard interface is found.

The same kernel on the screen, in QEMU and on the real PC (2026-10-07):

@@IMG xv6-tut-step-10-step10-qemu.png step-10 in QEMU@@

@@IMG xv6-tut-step-10-step10-realpc.jpg step-10 on the real PC: the USB keyboard is on a root port, two hubs and other devices are ignored, typing works@@

## 12. A good starting point, with almost zero OS?

Yes, with some caveats.

**Why it is a good starting point**

- **You can see what's happening on every machine you'll use.** `printk` goes to the screen and the serial port, `panic` stops on errors, and a CPU exception prints a message instead of rebooting. Every later step will lean on that, especially on the real PC.
- **It already runs on the hardware that matters.** The hardest "works in QEMU but not on the real PC" problems are solved: UEFI boot from a USB stick, a screen without a serial port, and a USB-only keyboard. From step 11 on, failures should be about OS logic, not about getting a machine to boot.
- **The OS part really is close to zero.** Nothing manages anything: one CPU, no interrupts, no memory allocator, no address spaces, no processes, no system calls, no files. Each concept from step 11 onward arrives into a clean space.

**Where "zero OS" isn't quite true**

- **It runs on the firmware's setup, not its own.** UEFI chose 64-bit mode, paging and the page tables, and it also left the GDT (segment table) the kernel runs with. So the kernel never does the classic boot work of switching CPU modes and turning paging on, which old x86 xv6 did in `bootasm.S` and `entry.S`. You won't learn that from this code; in this design it is the firmware's job.
- **There are a few small OS-like pieces already.** `consoleintr()` is a real line editor, `dmapage()` is a tiny page allocator, and the polling loop is a crude driver scheduler. They're simple, but they're there.
- **The USB driver isn't OS, but it is the most complex code in the kernel.** It is hardware plumbing. You don't need to understand it to follow steps 11–42; treat it as a black box that calls `consoleintr(c)`.

<div class="check" markdown="1">
**One thing to watch later: the firmware's page tables.** Some of step-10 only works because the firmware's page tables map every address to itself. In steps 13–14, when the kernel builds its own page tables, they must also map:

- the frame buffer,
- the xHCI registers, wherever they are (`0xC0_0000_0000` in QEMU),
- the `dmapage()` memory above `PHYSTOP`.

Otherwise the screen and the USB keyboard stop working the moment the new page tables are switched on. On the real PC, that is exactly the kind of failure that looks like a silent hang. It is the main debt this starting point carries.
</div>

So: a working, debuggable machine with no OS on top. That is a good place for step 11 (spinlock) to begin.

### What if there were no OS at all?

There are two ways to read "remove the OS".

**1. Remove the three OS-like pieces, keep the rest.**

| Remove | What happens |
|---|---|
| `consoleintr()` line editing (echo the raw character instead) | typing still shows letters, but Backspace no longer erases, and Enter sends `'\r'`, which only moves the cursor to the start of the line, so the next line overwrites the old one. It looks broken, but nothing crashes |
| `dmapage()` (use fixed arrays in `.bss` instead) | works just as well: the kernel sits at 1 MB, well below 4 GB, so the controller can reach those arrays. You lose only freeing and reusing pages when a device is unplugged, so the number of devices is fixed |
| the polling loop | nothing reads the keyboards any more. With interrupts off, `main()` returning lands in `entry.S`'s `hlt`, and the CPU stops for good. The boot messages stay on the screen; typing does nothing |

The line editor and the allocator are conveniences, but the loop is essential: without interrupts, something has to keep asking the devices.

What is left is a **bare-metal "superloop" program**, the same shape as the firmware in a microwave or inside a keyboard: initialize the hardware, then loop forever. That is really what step-10 already is. An OS starts when the machine is **shared**: several programs, isolated from each other, taking turns on the CPU and memory. Nothing in step-10 does that, with or without those three pieces.

**2. No OS at all: don't leave the firmware.** The loader could skip `ExitBootServices()` and never jump to the kernel. It would stay a UEFI application and use the firmware's own services: `ConOut->OutputString()` to print (on the screen, and maybe the serial port) and `ConIn->ReadKeyStroke()` to read keys, with the firmware's own USB keyboard driver. About 30 lines of C would do what steps 2–10 do, including typing on the real PC's USB keyboard.

In that sense **UEFI is already a small OS**: it has drivers, a memory allocator, a file system and a console. xv6 calls `ExitBootServices()` on purpose, because an OS has to **own** the hardware: its own interrupts, page tables, scheduling and drivers, which the firmware's services can't provide and would get in the way of. Leaving the firmware has a price, and steps 1–10 are mostly that bill: re-doing the screen, the keyboard and USB, which the firmware had been doing for us.

### Should some of this code be removed, to learn OS from scratch?

**No: keep it.**

**None of it is OS, so it doesn't spoil anything.** Learning OS "from scratch" means building the things that share the machine: locks, memory allocation, page tables, traps, processes, scheduling, system calls, files. None of those exist at step-10. Each one arrives in steps 11–42 into a clean space.

**Removing code would cost, not teach:**

- **remove USB:** the real PC has no PS/2 controller, so there would be no typing on the test machine. Real-PC testing would only come back once the driver was rewritten
- **remove the early exception screen:** a mistake on the real PC turns back into a silent reboot, just when bugs get harder (page tables, traps)
- **remove the screen console:** blind on the real PC, which has no serial port
- **remove the loader:** nothing boots

These are tools, like a lab bench. Rebuilding them teaches hardware plumbing, not OS ideas.

**What to do instead:**

1. **Treat USB as a black box.** `xhci.cpp` and `usb.cpp` never need reading to follow the OS steps. Their only contact with the rest of the kernel is `usbinit()`, `usbintr()` and the `consoleintr(c)` call.
2. **Know the few functions everything uses:** `main()`, `printk()` / `panic()`, `consputc()` / `consoleintr()`, `memset` / `memmove`. That is the part of steps 1–10 worth knowing well.
3. **Watch later steps change this code where the OS needs it:**
   - step 11: locks go into `console.cpp` and `printk.cpp`
   - steps 13–14: the kernel's page tables must also map the screen and the USB registers (the debt above)
   - steps 18–19: interrupts replace the polling loop

   The "no OS" code turning into "OS" code, one step at a time, is a good way to see what an OS actually adds.

To still get a taste of building from scratch, a cheap way is an optional exercise: rewrite `uart.cpp` or `printk.cpp` yourself from the step-02 and step-03 pages, then compare. Same lesson, without losing the working machine.

## 13. What comes next

@@FIG code10 notyet@@

From step 11 on, the C version's operating system comes back piece by piece, converted to C++. The first users of the new parts are already here:
- **Locks** (step 11) protect `cons` and `printk` once several CPUs or interrupts exist.
- **`kalloc`** (step 12) may take over from `dmapage()`, and the kernel's **own page tables** (steps 13–14) end the dependency on the firmware's.
- **Interrupts** (steps 15–19) replace the polling loop.

The USB driver's open items (devices plugged into hubs later, key repeat, interrupts instead of polling) are listed on the [progress page](/xv6/plan/) (in Korean).

<div class="tip" markdown="1">
**If you read only five places in the code**, read these in this order: `main()` in `kernel/main.cpp` (the order of everything), `consputc()` and `consoleintr()` in `kernel/console.cpp` (where all output goes, where all input arrives), `Ring::push()` and `Xhci::poll()` in `kernel/xhci.cpp` (how the CPU and the USB controller talk), and `usbkbdreport()` in `kernel/usb.cpp` (a key becomes a character).
</div>

<div class="step-nav"><span>← <a href="/xv6/tutorial/step-10/">step-10</a></span><span><a href="/xv6/tutorial/">Tutorial</a> →</span></div>
