from svg import D


def cursorrules():
    d = D(1000, 360, "fbconsputc(c) : 글자 하나와 커서 (cx, cy) 의 규칙")
    rows = [("'\\n'", "cx = 0, cy + 1"), ("'\\r'", "cx = 0"), ("'\\b'", "cx − 1 (0 이면 그대로)"), ("'\\t'", "cx 를 다음 8 의 배수로"), ("그 밖", "drawchar(cx, cy, c), cx + 1")]
    y = 50
    for c, act in rows:
        d.box(30, y, 90, 32, "", [c], "chg", size=12.5, mono=True, rx=3)
        d.text(135, y + 21, act, 12, False, "start")
        y += 38
    d.box(470, 50, 240, 60, "cx ≥ cols ?", ["→ cx = 0, cy + 1 (줄 바꿈)"], "white", size=12.5)
    d.box(470, 130, 240, 60, "cy ≥ rows ?", ["→ scroll(), cy = rows − 1"], "white", size=12.5)
    d.arrow(590, 110, 590, 128)
    d.box(740, 50, 240, 140, "앞뒤로", ["cursor(BG) : 옛 커서 지우기", "… 위의 처리 …", "cursor(FG) : 새 커서 그리기"], "new", size=12.5)
    d.box(30, 245, 950, 95, "화면 크기 → 글자 칸 (실제 값)", ["QEMU : 1280 × 800, 16 × 32 글꼴 → 80 열 × 25 줄", "VirtualBox : 2560 × 1440, 32 × 64 글꼴 (2560 이상) → 80 열 × 22 줄", "베어본 : 1920 × 1080, 16 × 32 글꼴 → 120 열 × 33 줄"], "white", size=12.5)
    return d.svg("커서 규칙")


def beforeafter():
    d = D(1000, 260, "step-03 → step-04 : printk 가 어디로 나가나")
    d.text(250, 50, "step-03", 13, True, color="#2c3e50"); d.text(750, 50, "step-04", 13, True, color="#2c3e50")
    d.box(40, 65, 140, 44, "printk", [], "base"); d.box(200, 65, 140, 44, "consputc", [], "base"); d.box(360, 65, 120, 44, "UART", [], "hw")
    d.arrow(180, 87, 198, 87); d.arrow(340, 87, 358, 87)
    d.box(40, 130, 440, 100, "화면", ["main.cpp 가 직접 칠한 남색 바탕", "+ 손그림 8×8 \"xv6\"", "(printk 는 화면에 안 나온다)"], "del", size=12)
    d.box(540, 65, 130, 44, "printk", [], "base"); d.box(690, 65, 130, 44, "consputc", [], "chg")
    d.box(840, 40, 140, 44, "fbconsputc", [], "new"); d.box(840, 100, 140, 44, "UART", [], "hw")
    d.arrow(670, 87, 688, 87); d.arrow(820, 80, 838, 62); d.arrow(820, 95, 838, 120)
    d.box(540, 165, 440, 65, "화면", ["부팅 메시지가 화면에 글자로 (Spleen 글꼴)", "→ 시리얼이 없는 실제 PC 에서도 보인다"], "new", size=12)
    return d.svg("step-04 전후")
