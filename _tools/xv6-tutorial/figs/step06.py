from svg import D


def pcitree():
    d = D(1000, 300, "QEMU q35 의 PCI 버스 0 (step-06 의 목록, make qemu USB=1)")
    d.box(400, 45, 200, 50, "버스 0", ["PCI 루트"], "hw", size=12.5)
    devs = [("0:0.0", "8086:29c0", "host bridge", "gray"), ("0:1.0", "1234:1111", "VGA (화면)", "base"), ("0:2.0", "8086:10d3", "Ethernet", "base"),
            ("0:3.0", "1b36:000d", "xHCI (USB 3)", "new"), ("0:31.2", "8086:2922", "SATA AHCI", "base")]
    x = 20
    for addr, ids, what, k in devs:
        d.path(f"M500,95 L500,120 L{x + 90},120 L{x + 90},140")
        d.box(x, 142, 180, 80, addr, [ids, what], k, size=12.5)
        x += 194
    d.text(500, 250, "버스:장치.기능 (bus:device.function).  0:31.2 = 장치 31 의 기능 2 : 한 칩 (ICH9) 의 여러 기능", 11.5)
    d.text(500, 274, "실제 PC 의 xHCI : 0:20.0, 8086:7a60 (Intel 700 시리즈)", 11.5, color="#7d3c98")
    return d.svg("PCI 장치 나무")


def gate():
    d = D(1000, 230, "IDT 항목 하나 (struct gatedesc, 16 바이트) : earlytrapinit() 이 32 개 채운다")
    d.bits(60, 60, 880, 0, [(127, 96, "rsvd (0)", "gray", 3), (95, 64, "off_63_32", "mem", 4), (63, 48, "off_31_16", "mem", 3),
                            (47, 40, "type_attr 0x8E", "new", 3), (39, 32, "ist (0)", "gray", 2), (31, 16, "cs (코드 셀렉터)", "base", 3), (15, 0, "off_15_0", "mem", 3)], h=44)
    d.text(500, 140, "off_* 세 조각 = 처리 코드 주소 (earlyvectors + 16 × n).  cs = 지금의 코드 세그먼트 (mov %cs)", 11.5)
    d.text(500, 164, "0x8E = 1000 1110 : P (있음) = 1, DPL = 0 (커널만), 종류 0xE = 64비트 interrupt gate (들어가면 인터럽트 끔)", 11.5)
    d.text(500, 188, "lidt(idt, sizeof(idt)) 로 CPU 에 표의 주소와 크기를 알린다", 11.5)
    return d.svg("IDT 게이트")
