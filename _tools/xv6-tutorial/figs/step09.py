from svg import D


def dci():
    d = D(1000, 230, "장치 컨텍스트 인덱스 (DCI) : 엔드포인트 번호와 방향으로 정해진다")
    cells = [("0", "slot", "gray"), ("1", "EP0 (양방향)", "base"), ("2", "EP1 OUT", "white"), ("3", "EP1 IN", "new"), ("4", "EP2 OUT", "white"), ("5", "EP2 IN", "white"), ("…", "", "white"), ("31", "EP15 IN", "white")]
    x = 40
    for n, what, k in cells:
        d.box(x, 60, 110, 60, n, [what], k, size=12)
        x += 115
    d.text(500, 150, "DCI = 2 × 엔드포인트 번호 + (IN 이면 1).  QEMU 키보드의 interrupt IN 엔드포인트 1 → DCI 3", 12)
    d.text(500, 175, "doorbell 에 쓰는 값 (db[slot] = kbddci) 도, 입력 컨텍스트의 add 플래그 (1 << dci) 도 이 번호", 12)
    d.text(500, 200, "입력 컨텍스트에서는 한 칸 밀린다 : 0 번이 입력 제어라서 DCI n 의 항목은 n + 1 번째 (ictx(d, dci + 1))", 12)
    return d.svg("DCI")


def keypath():
    d = D(1000, 380, "키 하나가 화면에 나오기까지 (step-09, 폴링)")
    lanes = [("키보드", 75), ("xHCI 컨트롤러", 255), ("이벤트 링", 435), ("usbintr → poll", 600), ("usb.cpp", 760), ("console", 905)]
    for name, x in lanes:
        d.box(x - 65, 40, 130, 30, name, [], "hw" if x < 500 else "base", size=11.5)
        d.line(x, 70, x, 360, dash=True)
    msgs = [(75, 255, "a 누름 : 리포트 [0 0 4 0 …]", 95), (255, 435, "전송 이벤트 (Normal TRB 완료)", 130), (600, 435, "cycle 비트 맞는 TRB 읽기", 165),
            (600, 760, "usbkbdreport(d, 8)", 200), (760, 905, "consoleintr('a')", 235), (905, 905, "", 0), (760, 255, "queuein() : 다음 리포트 요청 + doorbell", 270),
            (255, 75, "8 ms 마다 묻기 (NAK …)", 305)]
    for a, b, lab, y in msgs:
        if not lab:
            continue
        d.arrow(a, y, b + (4 if b < a else -4), y, color="#1e8449")
        d.text((a + b) / 2, y - 6, lab, 10.5)
    d.text(905, 258, "에코 →", 10.5); d.text(905, 273, "화면, 시리얼", 10.5)
    return d.svg("키 경로")
