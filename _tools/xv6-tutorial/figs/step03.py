from svg import D


def printkflow():
    d = D(1000, 300, "printk(fmt, …) : 형식 문자열을 한 글자씩")
    d.box(20, 60, 200, 50, "fmt[i]", [], "base", size=13, mono=True)
    d.box(280, 30, 260, 44, "'%' 가 아니면", ["consputc(c)"], "gray", size=12)
    d.box(280, 95, 260, 44, "'%' 이면 뒤의 c0 c1 c2 를 본다", [], "white", size=12)
    d.arrow(220, 75, 278, 52); d.arrow(220, 95, 278, 117)
    rows = [("d", "printint(int, 10, 부호)"), ("ld / lld", "printint(uint64, 10, 부호)"), ("u / lu / llu", "printint(…, 10, 부호 없음)"),
            ("x / lx / llx", "printint(…, 16)"), ("p", "printptr : 0x + 16 자리"), ("s", "문자열 (nullptr 면 \"(null)\")"), ("c", "글자 하나"), ("%", "'%'"),
            ("그 밖", "'%' 와 그 글자를 그대로 (눈에 띄게)")]
    y = 30
    for k, v in rows:
        d.box(600, y, 110, 26, "", [k], "chg", size=11.5, mono=True, rx=3)
        d.text(720, y + 17, v, 11, False, "start")
        y += 29
    d.arrow(540, 117, 598, 117)
    d.text(300, 200, "va_arg(ap, 타입) 로 다음 인자를 꺼낸다 (<stdarg.h> : 컴파일러가 주는 헤더)", 11.5)
    d.text(300, 225, "%ld 처럼 두 글자면 i 를 더 넘긴다 (i += 1, %lld 는 i += 2)", 11.5)
    return d.svg("printk 흐름")


def printint():
    d = D(1000, 250, "printint(255, 16, 0) : 아래 자리부터 버퍼에 쌓고 거꾸로 출력")
    steps = [("x = 255", "255 % 16 = 15 → 'f'", "x = 15"), ("x = 15", "15 % 16 = 15 → 'f'", "x = 0")]
    y = 55
    for a, b, c in steps:
        d.box(30, y, 140, 40, "", [a], "base", size=12.5, mono=True)
        d.box(200, y, 260, 40, "", [b], "chg", size=12.5, mono=True)
        d.box(490, y, 140, 40, "", [c], "base", size=12.5, mono=True)
        d.arrow(170, y + 20, 198, y + 20); d.arrow(460, y + 20, 488, y + 20)
        y += 52
    d.text(800, 60, "buf", 12, True)
    for i, ch in enumerate("ff"):
        d.rect(740 + i * 50, 70, 46, 46, "new"); d.text(763 + i * 50, 100, ch, 18, True, mono=True)
        d.text(763 + i * 50, 132, f"buf[{i}]", 10, mono=True)
    d.text(800, 165, "→ buf[1], buf[0] 순서로 consputc", 11.5)
    d.text(500, 215, "음수 (%d) 는 부호를 떼고 계산한 뒤 '-' 를 마지막에 쌓아서 맨 앞에 나오게 한다.  digits[] = \"0123456789abcdef\" (constexpr)", 11.5)
    return d.svg("printint")
