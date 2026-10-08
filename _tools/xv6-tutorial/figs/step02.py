from svg import D


def uartinit():
    d = D(1000, 300, "uartinit() 이 쓰는 순서 (I/O 포트 COM1 = 0x3F8)")
    w = [("IER ← 0x00", "인터럽트 끔"), ("LCR ← 0x80", "속도 설정 모드 (DLAB)"), ("+0 ← 0x03", "나누는 수 하위"), ("+1 ← 0x00", "나누는 수 상위"),
         ("LCR ← 0x03", "8비트, 패리티 없음 (DLAB 끔)"), ("FCR ← 0x07", "FIFO 켜고 비우기")]
    x = 15
    for i, (op, why) in enumerate(w):
        d.box(x, 60, 152, 70, op, [why], "hw" if i in (2, 3) else "base", size=12, mono=False)
        if i:
            d.arrow(x - 13, 95, x - 1, 95)
        x += 165
    d.box(15, 160, 480, 110, "속도 : 115200 / 나누는 수", ["UART 의 기준 클럭 115200 baud 를 3 으로 나눠 38400 baud", "DLAB (LCR 비트 7) 이 켜진 동안에만", "+0, +1 이 '나누는 수' 레지스터가 된다", "(평소에는 +0 = THR/RHR, +1 = IER)"], "white", size=12)
    d.box(515, 160, 470, 110, "C 판과 다른 점", ["C 판은 마지막에 송수신 인터럽트 (IER) 를 켠다", "이 단계는 인터럽트 처리 코드가 없어서 켜지 않는다", "(인터럽트는 Step 18 에서)"], "chg", size=12)
    return d.svg("UART 초기화 순서")


def lsrbits():
    d = D(1000, 210, "LSR (line status, COM1 + 5) : xv6 가 보는 두 비트")
    d.bits(150, 60, 700, 8, [(7, 7, "", "gray"), (6, 6, "", "gray"), (5, 5, "TX_IDLE", "new"), (4, 4, "", "gray"), (3, 3, "", "gray"), (2, 2, "", "gray"), (1, 1, "", "gray"), (0, 0, "RX_READY", "new")], h=44, label="LSR")
    d.text(500, 140, "TX_IDLE (1 << 5) : THR 이 비어 다음 바이트를 받을 수 있다 → uartputc_sync() 가 이것을 기다린다", 11.5)
    d.text(500, 163, "RX_READY (1 << 0) : 받은 바이트가 RHR 에 있다 → uartgetc() 가 읽는다", 11.5)
    d.text(500, 186, "포트가 없으면 0xFF : 모든 비트가 1 로 보인다 → 출력은 그냥 사라지고, 입력은 uartgetc() 가 0xFF 를 걸러서 막는다", 11.5, color="#7d3c98")
    return d.svg("LSR 비트")
