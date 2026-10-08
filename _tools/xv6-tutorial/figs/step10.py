from svg import D


def route():
    d = D(1000, 250, "route string (slot 컨텍스트 dw0 의 19:0) : 허브마다 4 비트")
    d.bits(150, 60, 760, 20, [(19, 16, "5단 허브 포트", "gray"), (15, 12, "4단", "gray"), (11, 8, "3단", "gray"), (7, 4, "2단 : 2", "new"), (3, 0, "1단 : 3", "new")], h=44, label="route")
    d.text(530, 140, "port 5.3.2 = 루트 포트 5 → 첫 허브의 포트 3 → 둘째 허브의 포트 2 → route 0x23 (루트 포트는 따로, dw1 에)", 12)
    d.text(530, 165, "hub() 가 자식에게 : route | (p << (4 × depth)), depth + 1.  허브 깊이는 최대 5 (MAXDEPTH)", 12)
    d.text(530, 190, "실제 PC 의 Wi-Fi (port 11.1) : 루트 포트 11, route 0x1", 12, color="#7d3c98")
    return d.svg("route string")


def tt():
    d = D(1000, 280, "Transaction Translator : high speed 허브 안의 속도 변환기")
    d.box(30, 100, 180, 70, "xHCI", ["480 Mb/s 로 말한다"], "hw", size=12)
    d.box(300, 70, 280, 130, "high speed 허브", ["포트마다 (또는 허브에 하나) TT", "", "480 Mb/s ↔ 12 / 1.5 Mb/s", "split transaction"], "chg", size=12)
    d.box(670, 60, 290, 60, "키보드 (full / low speed)", ["ttslot = 허브의 slot, ttport = 포트"], "new", size=12)
    d.box(670, 150, 290, 60, "Wi-Fi (high speed)", ["TT 필요 없음 (ttslot = 0)"], "base", size=12)
    d.arrow(210, 135, 298, 135, "480"); d.arrow(580, 110, 668, 90, "12 / 1.5"); d.arrow(580, 160, 668, 180, "480")
    d.text(500, 240, "QEMU 의 usb-hub 는 full speed 허브라서 TT 가 쓰이지 않는다 → 이 길은 실제 PC 에서만 시험할 수 있다", 12)
    return d.svg("TT")


def hubstatus():
    d = D(1000, 230, "허브 포트 상태 (GET_STATUS 4 바이트 = wPortChange : wPortStatus)")
    d.bits(120, 60, 840, 0, [(31, 21, "", "gray", 2), (20, 20, "C_RESET", "chg", 2), (19, 17, "", "gray", 1), (16, 16, "C_CONN", "chg", 2), (15, 11, "", "gray", 2),
                            (10, 10, "HS", "base", 2), (9, 9, "LS", "base", 2), (8, 8, "전원", "base", 2), (7, 5, "", "gray", 1), (4, 4, "리셋", "new", 2), (3, 2, "", "gray", 1), (1, 1, "사용", "new", 2), (0, 0, "연결", "new", 2)], h=44)
    d.text(540, 140, "hub() : 연결 (비트 0) → SET_FEATURE(PORT_RESET) → C_RESET (비트 20) 기다림 → 사용 가능 (비트 1) 확인", 12)
    d.text(540, 165, "속도 : 비트 9 면 low, 10 이면 high, 둘 다 아니면 full.  CLEAR_FEATURE 로 C_ 비트를 지운다 (16, 20)", 12)
    return d.svg("허브 포트 상태")
