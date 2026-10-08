from svg import D


def portsc():
    d = D(1000, 300, "PORTSC (포트 상태·제어) : 리셋 전 0xee1, 리셋 후 0xe03 (QEMU 에서 실제로 읽은 값)")
    f = [(31, 22, "…", "gray", 3), (21, 21, "PRC", "chg", 2), (20, 18, "…", "gray", 2), (17, 17, "CSC", "chg", 2), (16, 14, "…", "gray", 2),
         (13, 10, "속도", "base", 3), (9, 9, "PP", "base", 2), (8, 5, "링크 상태", "base", 3), (4, 4, "PR", "new", 2), (3, 2, "…", "gray", 1), (1, 1, "PED", "new", 2), (0, 0, "CCS", "new", 2)]
    d.bits(150, 60, 820, 0, f, h=40, label="0xee1", value=0xee1)
    d.bits(150, 160, 820, 0, f, h=40, label="0xe03", value=0xe03)
    d.text(560, 252, "CCS 연결됨 · PED 사용 가능 (1 을 쓰면 꺼짐!) · PR 리셋 · 링크 상태 7 (Polling) → 0 (U0) · PP 전원 · 속도 3 = high", 11.5)
    d.text(560, 276, "CSC, PRC 같은 '바뀜' 비트는 1 을 써서 지운다 (RW1C) → neutral() 로 위험한 비트를 빼고 쓴다", 11.5)
    return d.svg("PORTSC 비트")


def regspace():
    d = D(1000, 380, "BAR0 에서 시작하는 xHCI 레지스터 공간")
    rows = [("capability (base + 0)", "CAPLENGTH, HCSPARAMS1/2, HCCPARAMS1, DBOFF, RTSOFF", "base"),
            ("operational (base + CAPLENGTH)", "USBCMD, USBSTS, PAGESIZE, CRCR, DCBAAP, CONFIG, PORTSC[n] (0x400 + 0x10·(n−1))", "chg"),
            ("runtime (base + RTSOFF)", "인터럽터 0 : ERSTSZ (+0x28), ERSTBA (+0x30), ERDP (+0x38)", "mem"),
            ("doorbell (base + DBOFF)", "db[0] = 명령 링, db[slot] = 그 장치의 엔드포인트 번호", "new"),
            ("확장 능력 (HCCPARAMS1 31:16 × 4)", "ID 1 : USB Legacy Support (handoff) → ID 2 : Supported Protocol (USB 2 / 3 포트)", "hw")]
    y = 50
    for name, regs, k in rows:
        d.box(20, y, 300, 52, name, [], k, size=12)
        d.text(335, y + 31, regs, 11.5, False, "start")
        y += 60
    d.text(500, 368, "Xhci::init() 은 이 주소들을 base, op, rt, db 포인터로 기억한다.  QEMU 의 확장 능력은 ID 2 둘뿐 (handoff 할 것이 없다)", 11.5)
    return d.svg("xHCI 레지스터 공간")


def dcbaa():
    d = D(1000, 250, "DCBAA : slot 마다 장치 컨텍스트의 주소. 0 번은 scratchpad")
    for i in range(6):
        d.rect(60, 50 + i * 30, 160, 30, "mem" if i else "hw")
        d.text(140, 70 + i * 30, f"dcbaa[{i}]" + ("  scratchpad" if i == 0 else ""), 11, mono=True)
    d.text(140, 240, "한 페이지 (DCBAAP 레지스터)", 10.5)
    d.box(300, 40, 260, 70, "scratchpad 배열", ["sp[0], sp[1], … sp[33]", "(실제 PC : 34 쪽, QEMU : 0)"], "hw", size=12)
    d.box(620, 40, 340, 70, "페이지 34 개", ["컨트롤러가 자기 일에 쓰는 메모리", "소프트웨어는 건드리지 않는다"], "gray", size=12)
    d.arrow(220, 65, 298, 75); d.arrow(560, 75, 618, 75)
    d.box(300, 140, 660, 70, "dcbaa[slot] → 그 장치의 장치 (출력) 컨텍스트", ["step-08 의 newdev() 가 채운다. Enable Slot 명령이 slot 번호를 준다"], "new", size=12)
    d.arrow(220, 95, 298, 175)
    return d.svg("DCBAA")
