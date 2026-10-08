from svg import D


def contexts():
    d = D(1000, 420, "입력 컨텍스트와 장치 컨텍스트 (32 바이트 항목, Address Device 의 예)")
    d.text(230, 50, "입력 컨텍스트 (inctx) : 소프트웨어가 쓴다", 12.5, True, color="#2c3e50")
    rows = [("0 : 입력 제어", "add 플래그 = A0 | A1 (slot + EP0)", "chg"), ("1 : slot", "route, 속도, 항목 수 1, 루트 포트, TT", "new"),
            ("2 : EP0 (DCI 1)", "종류 Control, mps0, 링 주소 | 1", "new"), ("3… : 다른 엔드포인트", "(step-09 : 키보드의 IN 엔드포인트)", "gray")]
    y = 62
    for a, b, k in rows:
        d.box(20, y, 160, 44, "", [a], k, size=11.5, rx=0)
        d.box(180, y, 300, 44, "", [b], "white", size=11, rx=0)
        y += 44
    d.text(760, 50, "장치 컨텍스트 (outctx) : 컨트롤러가 쓴다", 12.5, True, color="#2c3e50")
    rows2 = [("0 : slot", "slot 상태, USB 주소 (dw3 7:0)"), ("1 : EP0", "엔드포인트 상태"), ("2… : EP1 OUT, IN, …", "")]
    y = 62
    for a, b in rows2:
        d.box(540, y, 170, 44, "", [a], "mem", size=11.5, rx=0)
        d.box(710, y, 270, 44, "", [b], "white", size=11, rx=0)
        y += 44
    d.text(760, 210, "↑ dcbaa[slot] 이 이 페이지를 가리킨다", 11)
    d.text(500, 255, "slot 컨텍스트 dword 0 – 3", 12.5, True, color="#2c3e50")
    d.bits(120, 280, 840, 32, [(31, 27, "항목 수", "chg"), (26, 26, "Hub", "base", 2), (25, 24, "", "gray", 1), (23, 20, "속도", "new"), (19, 0, "route string", "mem", 10)], h=30, label="dw0")
    d.bits(120, 335, 840, 32, [(31, 24, "포트 수 (허브)", "base"), (23, 16, "루트 포트 번호", "new"), (15, 0, "max exit latency", "gray")], h=30, label="dw1")
    d.bits(120, 385, 840, 32, [(31, 22, "인터럽터", "gray"), (21, 18, "", "gray", 2), (17, 16, "TTT", "base", 3), (15, 8, "TT 포트", "chg"), (7, 0, "TT 허브 slot", "chg")], h=30, label="dw2")
    return d.svg("컨텍스트")


def lifecycle():
    d = D(1000, 200, "장치 하나의 일생 (slot 의 상태)")
    st = [("연결됨", "포트 리셋 끝", "hw"), ("Enabled", "Enable Slot", "base"), ("Addressed", "Address Device", "chg"), ("Configured", "Configure Endpoint (step-09)", "new"), ("Disabled", "Disable Slot (무시 / 떼어짐)", "del")]
    x = 15
    for i, (s, cmd, k) in enumerate(st):
        d.box(x, 60, 180, 60, s, [cmd], k, size=12)
        if i:
            d.arrow(x - 15, 90, x - 1, 90)
        x += 197
    d.text(500, 160, "키보드가 아닌 장치는 Addressed 에서 바로 Disabled (freedev).  slot 번호는 다음 장치가 다시 받는다 (튜토리얼 연습의 'slot 재사용')", 11.5)
    return d.svg("slot 상태")
