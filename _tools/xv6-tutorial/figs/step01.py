from svg import D


def mangle():
    d = D(1000, 260, "이름 맹글링 : C++ 는 함수 이름에 인자 타입을 넣는다")
    d.box(20, 55, 300, 70, "start.cpp 의 함수", ["void start(struct bootinfo *bi)"], "base", size=12.5, mono=True)
    d.box(400, 40, 280, 50, "extern \"C\" 없이", ["_Z5startP8bootinfo"], "del", size=12.5, mono=True)
    d.box(400, 105, 280, 50, "extern \"C\" 로", ["start"], "new", size=12.5, mono=True)
    d.arrow(320, 85, 398, 65); d.arrow(320, 95, 398, 130)
    d.box(740, 40, 240, 115, "entry.S", ["call start", "", "어셈블리는 C 이름만 안다", "→ extern \"C\" 가 필요"], "chg", size=12.5, mono=False)
    d.text(500, 190, "_Z 5start P 8bootinfo = \"이름 길이 5 의 start, 인자는 bootinfo 를 가리키는 포인터 (P)\"   (c++filt 로 풀 수 있다)", 11.5)
    d.text(500, 215, "stack0 도 같은 이유로 extern \"C\".  main() 은 예외 : 언어 규칙상 맹글링하지 않는다", 11.5)
    return d.svg("이름 맹글링")


def pipeline():
    d = D(1000, 330, "만들기 : 소스 → 커널 ELF → 디스크 이미지 (step-01 의 Makefile)")
    d.box(20, 50, 170, 60, "*.cpp", ["start, main"], "new", size=12.5)
    d.box(20, 130, 170, 60, "entry.S", [], "base", size=12.5)
    d.box(230, 50, 220, 60, "g++ -std=c++20", ["-fno-exceptions -fno-rtti …"], "chg", size=12, mono=True)
    d.box(230, 130, 220, 60, "gcc (어셈블러)", [], "base", size=12)
    d.box(490, 90, 160, 60, "*.o", [], "gray", size=12.5, mono=True)
    d.box(690, 90, 140, 60, "ld", ["-T kernel.ld"], "chg", size=12.5, mono=True)
    d.box(860, 90, 120, 60, "kernel", ["ELF, 0x100000"], "base", size=12)
    d.arrow(190, 80, 228, 80); d.arrow(190, 160, 228, 160); d.arrow(450, 80, 488, 112); d.arrow(450, 160, 488, 128)
    d.arrow(650, 120, 688, 120); d.arrow(830, 120, 858, 120)
    d.box(20, 220, 200, 60, "boot/loader.c", ["clang + lld-link (PE)"], "chg", size=12)
    d.box(250, 220, 170, 60, "BOOTX64.EFI", [], "base", size=12, mono=True)
    d.box(460, 220, 200, 60, "esp.img (FAT32)", ["BOOTX64.EFI, kernel, fs.img"], "base", size=11.5)
    d.box(700, 220, 280, 60, "usb.img (GPT)", ["QEMU, VirtualBox, 실제 PC 가 부팅"], "new", size=12)
    d.arrow(220, 250, 248, 250); d.arrow(420, 250, 458, 250); d.arrow(660, 250, 698, 250)
    d.path("M920,150 L920,190 L560,190 L560,218")
    return d.svg("빌드 파이프라인")
