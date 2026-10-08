from svg import D


def kbdflow():
    d = D(1000, 470, "kbdgetc() : 바이트 하나가 글자가 되기까지 (kbd.c)")
    d.box(380, 45, 240, 44, "상태 포트 0x64 읽기", [], "hw", size=12.5)
    d.box(380, 115, 240, 44, "비트 0 (DIB) = 0 ?", [], "white", size=12.5); d.arrow(500, 89, 500, 113)
    d.box(700, 115, 260, 44, "return -1 (기다리는 바이트 없음)", [], "gray", size=11.5); d.arrow(620, 137, 698, 137, "예")
    d.box(380, 185, 240, 44, "데이터 포트 0x60 읽기 → data", [], "hw", size=12.5); d.arrow(500, 159, 500, 183, "아니오", lx=545, ly=176)
    rows = [("data == 0xE0 ?", "shift |= E0ESC  (다음 바이트는 확장 키)", "return 0"),
            ("data & 0x80 ?  (키를 뗌)", "shift &= ~shiftcode[data]", "return 0"),
            ("(키를 누름)", "shift |= shiftcode, shift ^= togglecode", "표에서 글자 찾기")]
    y = 255
    for q, act, ret in rows:
        d.box(40, y, 300, 44, q, [], "white", size=12)
        d.box(370, y, 380, 44, "", [act], "chg", size=12, mono=True)
        d.box(780, y, 180, 44, ret, [], "new" if "글자" in ret else "gray", size=12)
        d.arrow(340, y + 22, 368, y + 22); d.arrow(750, y + 22, 778, y + 22)
        y += 56
    d.path("M500,229 L500,242 L190,242 L190,253")
    d.box(40, 425, 920, 36, "", ["글자 = charcode[shift & (CTL | SHIFT)][data]   (normalmap, shiftmap, ctlmap, ctlmap)   + Caps Lock 이면 대소문자 바꿈"], "white", size=12, mono=True)
    return d.svg("kbdgetc 흐름")


def backspace():
    d = D(1000, 250, "화면에서 글자 지우기 : consputc(BACKSPACE) = '\\b', ' ', '\\b'")
    steps = [("처음", "ls_", 2), ("'\\b'", "ls", 1), ("' '", "l _", 2), ("'\\b'", "l_", 1)]
    x = 30
    for i, (lab, txt, cur) in enumerate(steps):
        d.text(x + 100, 60, lab, 12, True, color="#2c3e50")
        for c in range(4):
            ch = txt[c] if c < len(txt) and txt[c] not in "_ " else ""
            d.rect(x + 20 + c * 40, 72, 40, 54, "white")
            d.text(x + 40 + c * 40, 106, ch, 20, False, mono=True, color="#2c3e50")
        d.rect(x + 22 + cur * 40, 118, 36, 5, "base")
        if i < 3:
            d.arrow(x + 190, 99, x + 222, 99)
        x += 240
    d.box(30, 150, 940, 80, "", ["한 칸 뒤로 (\\b) → 공백으로 덮어쓰기 → 다시 한 칸 뒤로.  화면 (fbconsputc) 과 시리얼 (uartputc_sync) 에 같은 세 글자를 보낸다",
                                   "시리얼 터미널도 같은 방법으로 지운다. 커서는 칸 아래의 막대 (fbcons.c 의 cursor())"], "white", size=12)
    return d.svg("백스페이스")
