from svg import D


def ring():
    d = D(1000, 330, "cons.buf : 128 바이트 원형 버퍼와 세 인덱스 r, w, e")
    n = 16; x0 = 60; cw = 55
    txt = "ls\nech"
    for i in range(n):
        k = "new" if i < 3 else "chg" if i < 6 else "white"
        d.rect(x0 + i * cw, 80, cw, 50, k)
        ch = txt[i] if i < len(txt) else ""
        d.text(x0 + i * cw + cw / 2, 112, "\\n" if ch == "\n" else ch, 15, False, mono=True, color="#2c3e50")
        d.text(x0 + i * cw + cw / 2, 146, str(i), 9.5, mono=True, color="#7f8c8d")
    for idx, name, col in ((0, "r", "#c0392b"), (3, "w", "#1e8449"), (6, "e", "#b7950b")):
        x = x0 + idx * cw
        d.arrow(x, 185, x, 133, color=col); d.text(x, 200, name, 14, True, color=col, mono=True)
    d.text(x0 + 8 * cw, 70, "… 실제로는 128 칸, 인덱스는 % INPUT_BUF_SIZE 로 감는다", 11, False, "start")
    d.box(60, 225, 280, 85, "r ~ w : 다 친 줄", ["read() 가 가져갈 것", "(\"ls\\n\")"], "new", size=12)
    d.box(360, 225, 280, 85, "w ~ e : 치는 중인 줄", ["백스페이스, ^U 로 지울 수 있다", "(\"ech\")"], "chg", size=12)
    d.box(660, 225, 280, 85, "step-05 에서 다른 점", ["읽는 쪽 (consoleread) 이 아직 없어서", "줄이 끝나면 r = w (바로 버림)"], "white", size=12)
    return d.svg("콘솔 입력 버퍼")


def ps2bits():
    d = D(1000, 200, "PS/2 상태 포트 0x64 : kbd.cpp 가 보는 비트")
    d.bits(150, 60, 700, 8, [(7, 7, "", "gray"), (6, 6, "", "gray"), (5, 5, "AUX", "chg"), (4, 4, "", "gray"), (3, 3, "", "gray"), (2, 2, "", "gray"), (1, 1, "IBF", "base"), (0, 0, "DIB", "new")], h=44, label="0x64")
    d.text(500, 138, "DIB (0x01) : 읽을 바이트가 0x60 에 있다     IBF (0x02) : 컨트롤러가 아직 명령을 처리 중 (kbcwait 가 기다림)", 11.5)
    d.text(500, 162, "AUX (0x20) : 그 바이트는 마우스에서 왔다 → 버린다.   컨트롤러가 없으면 0xFF (모두 1) : kbdgetc 가 먼저 거른다", 11.5)
    return d.svg("PS/2 상태 비트")
