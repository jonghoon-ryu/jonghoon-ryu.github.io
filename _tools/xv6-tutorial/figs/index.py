from svg import D
from figs.common import numstat


def system():
    d = D(1000, 560, "step-10 의 커널 전체 : 어느 단계가 무엇을 더했나")
    d.text(20, 52, "부팅", 12.5, True, "start", "#2c3e50")
    boot = [("UEFI 펌웨어", "", "hw"), ("boot/loader.c", "v0.1 · step-01", "base"), ("entry.S", "step-01", "base"), ("start.cpp", "step-01", "base"), ("main.cpp", "step-01 … 10", "base")]
    x = 20
    for i, (n, s, k) in enumerate(boot):
        d.box(x, 62, 172, 52, n, [s] if s else [], k, size=12)
        if i:
            d.arrow(x - 22, 88, x - 1, 88)
        x += 194
    d.text(20, 150, "출력", 12.5, True, "start", "#2c3e50")
    d.box(20, 160, 200, 52, "printk / panic", ["step-03"], "chg", size=12)
    d.box(250, 160, 200, 52, "console.cpp", ["step-03, 04, 05"], "chg", size=12)
    d.box(480, 140, 200, 46, "fbcons.cpp + font.h", ["step-04 → 화면"], "chg", size=11.5)
    d.box(480, 192, 200, 46, "uart.cpp", ["step-02 → COM1"], "chg", size=11.5)
    d.arrow(220, 186, 248, 186); d.arrow(450, 180, 478, 163); d.arrow(450, 192, 478, 215)
    d.box(720, 140, 260, 98, "실제 PC 에서", ["화면 : 보인다 (1920 × 1080)", "COM1 : 대개 없다 → 0xFF", "출력이 그냥 사라진다 (멈추지 않는다)"], "white", size=11.5)
    d.text(20, 278, "입력 (main() 의 루프가 폴링)", 12.5, True, "start", "#2c3e50")
    d.box(20, 290, 190, 50, "kbd.cpp", ["step-05 : PS/2"], "chg", size=12)
    d.box(20, 350, 190, 50, "uart.cpp", ["step-05 : uartintr"], "chg", size=12)
    d.box(20, 410, 190, 50, "usb.cpp", ["step-08, 09, 10"], "new", size=12)
    d.box(250, 410, 190, 50, "xhci.cpp", ["step-07 … 10"], "new", size=12)
    d.box(480, 410, 190, 50, "pci.cpp", ["step-06"], "new", size=12)
    d.arrow(210, 435, 248, 435); d.arrow(440, 435, 478, 435, "찾기")
    d.box(250, 300, 220, 90, "consoleintr()", ["에코, 줄 편집", "(console.cpp, step-05)"], "chg", size=12)
    d.arrow(210, 315, 248, 330); d.arrow(210, 375, 248, 360); d.path("M115,410 L115,400 L240,400 L248,380")
    d.box(720, 290, 260, 170, "하드웨어", ["PS/2 컨트롤러 (QEMU, VBox)", "COM1 16550 UART", "PCI 버스", "xHCI → 허브 → USB 키보드", "(실제 PC 는 이 길만)"], "hw", size=11.5)
    d.box(20, 490, 450, 50, "earlytrap.cpp + earlyvec.S (step-06)", ["CPU 예외 → 화면에 찍고 멈춤 (조용한 재부팅 대신)"], "new", size=11.5)
    d.box(500, 490, 480, 50, "아직 없는 것 (Step 11 부터)", ["잠금, 메모리 할당, 페이지 테이블, 인터럽트, 프로세스, 파일 시스템, 셸"], "gray", size=11.5)
    d.legend(700, 278, (("chg", "C 판에서 옮김"), ("new", "새로 씀 (C 판에 없음)")))
    return d.svg("커널 전체 구조")


def lines():
    tags = ["step-01", "step-02", "step-03", "step-04", "step-05", "step-06", "step-07", "step-08", "step-09", "step-10"]
    prev = ["v0.2-x86_64-c"] + tags[:-1]
    data = []
    for p, t in zip(prev, tags):
        rows = numstat(p, t)
        a = sum(r[2] for r in rows if not r[0].endswith("font.h"))
        f = sum(r[2] for r in rows if r[0].endswith("font.h"))
        dl = sum(r[3] for r in rows)
        data.append((t, a, f, dl))
    d = D(1000, 380, "태그마다 더한 줄 (font.h 글꼴 데이터는 따로) : step-01 은 C 판을 지우는 단계")
    top = max(a + f for _, a, f, _ in data)
    base = 300; hmax = 220
    for i, (t, a, f, dl) in enumerate(data):
        x = 60 + i * 92
        ha = hmax * a / top; hf = hmax * f / top
        d.rect(x, base - ha, 56, ha, "new" if i >= 5 else "chg")
        if f:
            d.rect(x, base - ha - hf, 56, hf, "gray"); d.text(x + 28, base - ha - hf / 2 - 4, "font.h", 9.5); d.text(x + 28, base - ha - hf / 2 + 10, f"+{f}", 9.5, mono=True)
        d.text(x + 28, base - ha - hf - 6, f"+{a}" + (" 코드" if f else ""), 10.5, True, mono=True, color="#2c3e50")
        d.text(x + 28, base + 18, t, 10.5, mono=True)
        if dl > 500:
            d.text(x + 28, base + 36, f"−{dl}", 10, False, mono=True, color="#c0392b")
    d.line(50, base, 990, base, "#566573", 1.5)
    d.legend(430, 360, (("chg", "C 판에서 옮김"), ("new", "USB 키보드"), ("gray", "글꼴 데이터")))
    return d.svg("태그마다 더한 줄")
