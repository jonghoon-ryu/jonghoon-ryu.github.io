# diagrams for /old-ssd-experiments/ (Korean labels). each function returns one inline <svg>.
from svg import D, Chart, C

T, R, B, G, P, K = C["teal"], C["red"], C["blue"], C["gold"], C["purple"], C["ink"]


# ------------------------------------------------------------------ overview
def overview_map():
    d = D(760, 370, "실험 순서 : 읽기만 하는 것 → 성능 → GC · 마모 → 기다리기 · 소모")
    phases = [
        (10, "A. 지우기 전", "읽기만 한다", "gold", [("0", "준비 · SMART"), ("1", "오래된 데이터"), ("2", "기능 · 자가 진단")]),
        (160, "B. 기본 성능", "SATA · 막 지운 상태", "teal", [("3", "SLC 캐시"), ("4", "TRIM · 빈 읽기"), ("5", "성능 지도"),
                                                       ("6", "쓰기 크기 · 정렬"), ("7", "쓰기 캐시 · FLUSH")]),
        (310, "C. GC 와 여유", "꽉 찬 상태", "tlc", [("8", "Write cliff"), ("9", "쉬는 동안 GC"), ("10", "Over-provisioning"),
                                                  ("11", "뜨거운 데이터"), ("12", "WAF (SMART)")]),
        (460, "D. 간섭 · 지우기", "읽기와 쓰기 사이", "hw", [("13", "읽기 · 쓰기 간섭"), ("14", "Secure Erase"), ("15", "Read disturb")]),
        (610, "E. 마지막", "기다리기 · 소모", "warn", [("16", "Retention"), ("17", "전원 차단"), ("18", "끝까지 쓰기"), ("19", "열어 보기")]),
    ]
    for x, title, sub, kind, items in phases:
        d.box(x, 42, 140, 50, title, [sub], kind, size=13)
        for i, (n, s) in enumerate(items):
            y = 108 + i * 42
            d.box(x + 4, y, 132, 34, "", [], "white", rx=6)
            d.text(x + 20, y + 22, n, 12.5, True, color=K)
            d.text(x + 34, y + 22, s, 11.5, anchor="start")
    for x in (150, 300, 450, 600):
        d.arrow(x, 67, x + 10, 67)
    d.text(380, 335, "실험 12 (WAF) 는 따로도 돌리지만, 실험 3–11 의 SMART 앞뒤 기록으로도 계산한다", 11.5, color="#566573")
    d.text(380, 355, "17 (전원 차단) 은 드라이브를 망가뜨릴 수 있어서, 18 (끝까지 쓰기) 은 드라이브를 소모해서 뒤에 둔다", 11.5, color="#566573")
    return d.svg("실험 순서")


# ------------------------------------------------------------------ Linux commands
def cmd_layers():
    d = D(760, 470, "디스크가 보이는 층과, 각 층을 보는 명령")
    rows = [
        ("응용 프로그램", "cp, 브라우저, fio …", "white", "ps, iotop"),
        ("파일 시스템", "ext4, NTFS, vfat : 파일 이름 → 위치", "base", "df, findmnt, mount"),
        ("페이지 캐시 (RAM)", "읽은 것 · 쓸 것을 잠시 담아 둔다", "mem", "free, dd oflag=direct"),
        ("블록 장치", "/dev/sdg, /dev/sdg3 : 512 B 섹터의 줄", "chg", "lsblk, blockdev, /dev/disk/by-id"),
        ("드라이버 · 연결", "SATA (ahci) 또는 USB (uas) · NVMe", "hw", "lsusb -t, /sys/block, journalctl -k"),
        ("SSD 컨트롤러 (FTL)", "LBA → NAND 위치, GC, 마모 평준화", "teal", "smartctl, hdparm -I, nvme"),
        ("NAND 플래시", "실제로 데이터가 사는 곳", "tlc", "(직접은 못 본다 : 실험으로 추측)"),
    ]
    for i, (name, sub, kind, cmd) in enumerate(rows):
        y = 40 + i * 60
        d.box(20, y, 400, 50, name, [sub], kind, size=13)
        d.box(450, y + 6, 290, 38, "", [cmd], "white", mono=True, size=13)
        d.arrow(420, y + 25, 448, y + 25)
    return d.svg("디스크 층과 명령")


def cmd_names():
    d = D(760, 300, "장치 이름 읽는 법")
    d.box(20, 50, 180, 60, "/dev/sdg", ["디스크 하나 (SATA · USB)"], "chg", mono=True)
    parts = [("sdg1", "100 MB vfat", "EFI 부트"), ("sdg2", "16 MB", "MSR (예약)"),
             ("sdg3", "111 GB ntfs", "Windows C:"), ("sdg4", "532 MB ntfs", "복구")]
    for i, (n, s, u) in enumerate(parts):
        y = 30 + i * 45
        d.box(260, y, 230, 38, "", [f"{n}   {s}"], "base", mono=True, size=13)
        d.text(505, y + 24, u, 12, anchor="start")
        d.path(f"M200,80 C230,80 230,{y + 19} 258,{y + 19}")
    d.box(20, 225, 180, 55, "/dev/nvme0n1", ["NVMe 디스크"], "teal", mono=True)
    d.box(260, 225, 230, 55, "", ["nvme0n1p1, nvme0n1p2", "(파티션 앞에 p 가 붙는다)"], "base", mono=True, size=13)
    d.arrow(200, 252, 258, 252)
    d.text(625, 232, "sd = SCSI disk : SATA · USB 디스크 이름", 11.5)
    d.text(625, 249, "a, b, … g 는 연결 순서로 붙어 바뀔 수 있다", 11.5)
    d.text(625, 272, "→ 실험에서는 시리얼로 찾는다", 11.5, True, color=R)
    return d.svg("장치 이름")


def cmd_trim():
    d = D(760, 260, "파일을 지우면 SSD 는 언제 알게 되나 : TRIM")
    steps = [("rm file", "파일 시스템 표에서만 지움", "base"), ("fstrim / discard", "\"이 LBA 들은 이제 안 쓴다\"", "chg"),
             ("TRIM 명령", "SATA 의 DSM 명령", "hw"), ("FTL", "LBA → NAND 연결을 끊는다", "teal")]
    for i, (t, s, k) in enumerate(steps):
        x = 15 + i * 188
        d.box(x, 50, 170, 62, t, [s], k, size=13)
        if i:
            d.arrow(x - 18, 81, x - 2, 81)
    d.box(15, 150, 355, 85, "TRIM 이 없으면", ["SSD 는 지운 데이터를 아직 \"유효\" 로 여긴다", "→ GC 가 쓸모없는 데이터까지 복사한다", "→ 느려지고, 더 닳는다"], "warn", size=13)
    d.box(390, 150, 355, 85, "TRIM 이 있으면", ["그 페이지는 \"무효\" : GC 가 건너뛴다", "그 LBA 를 읽으면 NAND 를 안 읽고", "0 을 돌려줄 수 있다 (실험 4)"], "new", size=13)
    return d.svg("TRIM 흐름")


def cmd_cache():
    d = D(760, 250, "같은 dd 인데 숫자가 다른 이유 : 페이지 캐시")
    d.box(20, 45, 150, 50, "dd (보통)", [], "white", size=13)
    d.box(250, 45, 200, 50, "페이지 캐시 (RAM)", ["\"다 썼다\" 고 바로 대답"], "mem", size=13)
    d.box(540, 45, 200, 50, "디스크", ["나중에 천천히 쓴다"], "chg", size=13)
    d.arrow(170, 70, 248, 70, "4.6 GB/s ?!")
    d.arrow(450, 70, 538, 70, "나중에", dash=True)
    d.box(20, 150, 150, 50, "dd oflag=direct", [], "white", size=13, mono=True)
    d.box(540, 150, 200, 50, "디스크", ["다 쓴 뒤에 대답"], "chg", size=13)
    d.arrow(170, 175, 538, 175, "2.7 GB/s : 디스크의 진짜 속도 (캐시를 건너뜀)")
    d.text(380, 235, "실험의 모든 측정은 direct I/O (fio --direct=1, O_DIRECT) 로 한다", 12, True, color=T)
    return d.svg("페이지 캐시")


# ------------------------------------------------------------------ setup
def setup_sata():
    d = D(760, 300, "SATA 포트 4개가 모두 차 있다 : 실험 동안 840 EVO 500GB 와 자리를 바꿨다")
    ports = [("SATA (ata5)", "sda", "840 EVO 120GB (실험용)", "new"), ("SATA (ata6)", "sdb", "750 EVO 500GB", "base"),
             ("SATA (ata7)", "sdc", "WD 1TB HDD", "base"), ("SATA (ata8)", "sdd", "Seagate 2TB HDD", "base")]
    d.box(20, 45, 170, 230, "메인보드", ["MAG B760M", "MORTAR II", "", "Intel B760", "SATA 컨트롤러"], "hw", size=13)
    for i, (p, n, m, k) in enumerate(ports):
        y = 50 + i * 57
        d.box(230, y, 120, 44, "", [p], "white", size=13)
        d.line(190, y + 22, 230, y + 22, "#7d3c98", 2)
        d.box(380, y, 170, 44, n, [m], k, size=13)
        d.line(350, y + 22, 380, y + 22, "#7f8c8d", 2)
    d.box(590, 120, 155, 60, "sde", ["840 EVO 500GB", "USB 어댑터로"], "warn", size=13)
    d.path("M552,72 C575,72 575,135 590,135", color=R)
    d.text(668, 206, "120GB 는 USB 의 sdg 였다", 12, color=R)
    d.text(668, 223, "끝나면 500GB 를 ata5 로", 12, color=R)
    return d.svg("SATA 포트")


def setup_safety():
    d = D(760, 210, "lab.sh 가 지우기 전에 하는 확인")
    steps = [("시리얼로 찾기", "S1D6NSAFB40389K", "base"), ("시스템 디스크?", "/ 가 있으면 중단", "warn"),
             ("마운트됨?", "있으면 중단", "warn"), ("TRIM 되나?", "USB 면 중단", "chg"), ("시리얼 끝 5자리", "직접 입력", "gold")]
    for i, (t, s, k) in enumerate(steps):
        x = 10 + i * 150
        d.box(x, 50, 135, 60, t, [s], k, size=12.5)
        if i:
            d.arrow(x - 13, 80, x - 2, 80)
    d.box(250, 140, 260, 50, "실행 → 결과 폴더", ["~/Ryu/old_ssd_results/날짜-실험/"], "new", size=13)
    d.arrow(680, 110, 512, 160)
    return d.svg("안전 확인")


# ------------------------------------------------------------------ exp 1 : old data
import math


def _bell(c, mu, sig, x0, x1, amp):
    pts = []
    n = 60
    for i in range(n + 1):
        x = x0 + (x1 - x0) * i / n
        pts.append((x, amp * math.exp(-((x - mu) ** 2) / (2 * sig * sig))))
    return pts


def _states(title, shift, widen, note):
    d = D(760, 310, title)
    ch = Chart(d, 50, 45, 690, 170, (0, 8.2), (0, 1.1), "", "", grid=False)
    d.text(745, 256, "셀의 문턱 전압 (Vth) →", 11.5, anchor="end")
    names = ["111", "110", "100", "101", "001", "000", "010", "011"]
    for i in range(8):
        mu = 0.55 + i * 1.0 - (shift * (i / 7) if i else 0)
        sig = 0.13 + widen * (i / 7)
        pts = _bell(ch, mu, sig, mu - 4 * sig, mu + 4 * sig, 1.0 - 1.5 * widen)
        ch.area(pts, [B, T][i % 2], 0.25)
        ch.curve(pts, [B, T][i % 2], 2)
        d.text(ch.X(0.55 + i * 1.0), 237, names[i], 11.5, mono=True)
    for i in range(7):
        ch.vline(1.05 + i * 1.0, R, True)
    d.text(380, 280, "빨간 점선 = 읽기 기준 전압 (Vref) 7개 : 셀 하나에 3비트 = 상태 8개", 11.5, color=R)
    d.text(380, 300, note, 11.5, True, color=K)
    return d.svg(title)


def old_states_fresh():
    return _states("TLC 셀 : 막 썼을 때", 0.0, 0.0, "봉우리 8개가 좁고 떨어져 있다 → 기준 전압으로 깨끗하게 구분된다")


def old_states_drift():
    return _states("TLC 셀 : 오래 전원 없이 둔 뒤 (전하가 빠져나감)", 0.55, 0.16, "봉우리가 왼쪽으로 밀리고 넓어진다 → 기준선을 넘은 셀 = 비트 오류")


def old_retry():
    d = D(760, 300, "읽기 한 번이 길어지는 이유 : ECC 와 read retry")
    d.box(20, 50, 140, 50, "읽기 요청", ["LBA → NAND 위치"], "white", size=13)
    d.box(200, 50, 150, 50, "페이지 읽기", ["기준 전압 그대로"], "tlc", size=13)
    d.box(390, 50, 150, 50, "ECC 로 고침", ["오류 수 ≤ 한계?"], "teal", size=13)
    d.box(590, 50, 150, 50, "호스트로", ["빠름 (수십 µs)"], "new", size=13)
    d.arrow(160, 75, 198, 75)
    d.arrow(350, 75, 388, 75)
    d.arrow(540, 75, 588, 75, "예")
    d.box(390, 170, 150, 55, "기준 전압 옮기기", ["(read retry)"], "warn", size=13)
    d.arrow(465, 100, 465, 168, "아니오", lx=490)
    d.path("M390,197 C300,197 275,150 275,102")
    d.text(300, 215, "다시 읽기", 11.5, color=R)
    d.text(380, 262, "오래된 데이터는 이 고리를 여러 번 돈다 : 읽을 때마다 페이지 읽기 시간이 더해진다", 12, True, color=K)
    d.text(380, 282, "840 EVO 는 2014년, 오래된 데이터의 읽기 속도가 크게 떨어지는 문제로 알려졌다", 11.5)
    return d.svg("read retry")


def old_history():
    d = D(760, 300, "이 드라이브가 지나온 시간")
    ch = Chart(d, 40, 60, 680, 120, (2018, 2027), (0, 1), "", "", [(y, str(y)) for y in range(2018, 2028)], [], grid=False)
    d.fillrect(ch.X(2018), ch.Y(0.45), ch.X(2024.95) - ch.X(2018), 34, T, 0.25)
    d.text((ch.X(2018) + ch.X(2024.95)) / 2, ch.Y(0.45) + 22, "Windows 디스크로 사용 : 가끔 켜짐, 파일을 쓰고 지움", 12, True, color=K)
    d.fillrect(ch.X(2024.95), ch.Y(0.45), ch.X(2026.79) - ch.X(2024.95), 34, "#566573", 0.18)
    d.text((ch.X(2024.95) + ch.X(2026.79)) / 2, ch.Y(0.45) + 22, "전원 없음 : 1년 이상", 12, True, color=K)
    for x, col in ((2024.94, T), (2026.79, R)):
        ch.vline(x, col, True)
    d.text(ch.X(2024.94) - 6, ch.Y(0.85), "2024.12 마지막 사용 (hiberfil.sys)", 11.5, color=T, anchor="end")
    d.text(ch.X(2026.79) - 6, ch.Y(1.0) + 4, "2026.10.17 다시 연결", 11.5, True, color=R, anchor="end")
    d.box(40, 205, 220, 70, "켜져 있던 동안", ["펌웨어가 오래된 데이터를", "다시 쓸 수 있었다 (펌웨어에 따라)"], "teal", size=12.5)
    d.box(275, 205, 220, 70, "전원이 없던 동안", ["다시 쓰기는 없다", "전하만 빠져나간다 : 모든 데이터 같이"], "gray", size=12.5)
    d.box(510, 205, 230, 70, "다시 연결한 날", ["Ryu 가 파일 몇 개를 읽고, 몇 개를 씀", "→ '새 데이터' 와 '한 번 읽은 데이터'"], "warn", size=12.5)
    return d.svg("드라이브의 역사")


def old_expect():
    d = D(760, 360, "예상 : 세 무리로 나뉜다 (가설)")
    ch = Chart(d, 85, 45, 640, 230, (2018, 2027), (0, 600), "데이터를 쓴 해", "읽기 속도 (MB/s)",
               [(y, str(y)) for y in range(2018, 2028)], [(v, str(v)) for v in (0, 100, 200, 300, 400, 500)])
    ch.band(2024.95, 2026.79, "#566573", "전원 없음", 0.10)
    ch.hline(500, B, True)
    ch.note(2018.6, 515, "새로 쓴 파일 (2026.10.17) : 빠르다", B, bold=True)
    ch.dot(2026.79, 480, B, 6)
    ch.curve([(2018.5, 60), (2020, 75), (2022, 95), (2024.5, 120)], T, 3)
    ch.note(2018.6, 205, "손대지 않은 파일 : 모두 느리다", T, size=12, bold=True)
    ch.note(2018.6, 175, "오래 썼을수록 더? (평평하면 그것도 결과)", T)
    for x, y in ((2019.4, 380), (2021.3, 420), (2023.6, 400)):
        ch.dot(x, y, G, 5)
    ch.note(2019.0, 330, "10.17 에 한 번 읽은 파일 : 펌웨어가 다시 썼다면 빠르다", G, bold=True)
    d.text(400, 345, "모양은 예시일 뿐이다 : 실제 숫자는 측정해 보기 전에는 모른다", 11.5, color="#566573")
    return d.svg("예상 그래프")


def old_method():
    d = D(760, 300, "측정 방법 : 파일마다 '언제 썼나', '그 뒤 읽혔나', '얼마나 빨리 읽히나'")
    steps = [("파일 고르기", "세 무리로 나눔 (아래)", "base"), ("쓴 날짜", "생성 · 수정 시각 중 늦은 쪽", "chg"),
             ("캐시 비우기", "posix_fadvise DONTNEED", "mem"), ("16 MiB 읽기", "1 MiB 씩, 시간 재기", "teal")]
    for i, (t, s, k) in enumerate(steps):
        x = 10 + i * 188
        d.box(x, 50, 172, 62, t, [s], k, size=13)
        if i:
            d.arrow(x - 16, 81, x - 2, 81)
    groups = [("new", "쓴 날 ≥ 10.17", "새 데이터 : 비교 기준", "tlc"), ("read", "접근 시각 ≥ 10.17", "한 번 읽힘 : 다시 쓰였나?", "gold"),
              ("old", "그 밖", "손대지 않음 : 해마다 25개", "teal")]
    for i, (g, rule, s, k) in enumerate(groups):
        d.box(10 + i * 250, 140, 235, 62, g, [rule, s], k, size=13, mono=False)
    d.box(130, 230, 500, 50, "fileage.csv  +  fileage-reread.csv", ["가장 느린 old 10개는 한 번 더 읽는다 : 읽기만으로 빨라지나"], "new", size=13)
    return d.svg("측정 방법")


# ------------------------------------------------------------------ exp 3 : SLC cache
def slc_concept():
    d = D(760, 300, "TurboWrite : TLC 의 일부를 SLC 처럼 써서 빠르게 받아 둔다")
    d.box(20, 110, 130, 60, "호스트 쓰기", [], "white", size=13)
    d.box(230, 45, 220, 80, "SLC 버퍼 (약 3 GB)", ["셀 하나에 1비트 : 빠르게 쓴다", "120GB 모델 기준 (알려진 값)"], "slc", size=13)
    d.box(230, 165, 220, 80, "TLC 영역", ["셀 하나에 3비트 : 느리게 쓴다", "데이터가 최종적으로 사는 곳"], "tlc", size=13)
    d.arrow(150, 130, 228, 90, "평소", lx=175, ly=100)
    d.arrow(150, 150, 228, 200, "버퍼가 다 차면", dash=True, lx=150, ly=205)
    d.path("M450,85 C540,85 540,205 452,205")
    d.text(600, 140, "쉬는 동안 옮겨 쓴다", 12, True, color=T)
    d.text(600, 158, "(그래서 버퍼가 다시 빈다)", 11.5)
    d.text(380, 278, "SLC 는 쓰기가 빠르고 덜 닳는다. 대신 같은 셀에 1/3 만 담는다", 11.5, color="#566573")
    return d.svg("TurboWrite")


def slc_expect():
    d = D(760, 340, "예상 : 순차 쓰기 속도, 처음 몇 GB 만 빠르다")
    ch = Chart(d, 85, 45, 640, 220, (0, 120), (0, 500), "지금까지 쓴 양 (GB)", "쓰기 속도 (MB/s)",
               [(v, str(v)) for v in range(0, 121, 20)], [(v, str(v)) for v in range(0, 501, 100)])
    ch.band(0, 3, T, "SLC", 0.15, T)
    ch.curve([(0, 400), (3, 400), (3.3, 140), (120, 140)], R, 3)
    ch.note(6, 420, "사양 : 최대 약 410 MB/s (SATA, 120GB 모델)", K)
    ch.note(30, 165, "버퍼가 차면 TLC 에 바로 : 약 140 MB/s 로 알려져 있다", R, bold=True)
    ch.note(30, 70, "꺾이는 위치 = 버퍼 크기, 낮은 쪽 높이 = TLC 쓰기 속도", K)
    d.text(400, 330, "숫자는 리뷰 · 사양에서 기억하는 값 : 이 드라이브에서 직접 잰다", 11.5, color="#566573")
    return d.svg("SLC 예상")


def slc_idle():
    d = D(760, 300, "버퍼는 쉬면 다시 빈다 : 얼마나 쉬어야 할까")
    ch = Chart(d, 85, 45, 640, 170, (0, 5), (0, 4), "쉰 시간 (분)", "빠르게 쓴 양 (GB)",
               [(i + 1, str(v)) for i, v in enumerate((0, 1, 5, 15))], [(v, str(v)) for v in range(0, 5)])
    for x, y in ((1, 0.2), (2, 1.5), (3, 3), (4, 3)):
        d.fillrect(ch.X(x) - 30, ch.Y(y), 60, ch.Y(0) - ch.Y(y), T, 0.55)
    ch.hline(3, R, True, "버퍼 크기 (약 3 GB)")
    d.text(400, 290, "막대 높이는 상상한 값 : slc-idle 0 1 5 15 로 잰 뒤 진짜 막대로 바꾼다", 11.5, color="#566573")
    return d.svg("버퍼 회복")


# ------------------------------------------------------------------ exp 4 : TRIM
def trim_table():
    d = D(760, 325, "FTL 의 매핑 표 : LBA 마다 'NAND 의 어디' 를 적어 둔다")
    rows = [("0", "블록 12, 페이지 3"), ("1", "블록 12, 페이지 4"), ("2", "블록 40, 페이지 0"), ("3", "블록 7, 페이지 9")]
    rows2 = [("4", "없음"), ("5", "없음"), ("6", "없음"), ("7", "없음")]
    d.text(160, 52, "LBA → NAND 위치", 12.5, True, color=K)
    for i, (l, p) in enumerate(rows + rows2):
        y = 62 + i * 27
        d.box(60, y, 60, 24, "", [l], "white", rx=0, size=12.5)
        d.box(120, y, 180, 24, "", [p], "new" if i < 4 else "gray", rx=0, size=12.5)
    d.box(360, 70, 380, 70, "LBA 0–3 : 쓴 적 있음", ["읽으면 → 표에서 위치 찾기 → NAND 읽기", "→ 수십 µs 이상"], "new", size=13)
    d.box(360, 170, 380, 70, "LBA 4–7 : TRIM 됨 (또는 쓴 적 없음)", ["읽으면 → 표에 없음 → 바로 0 을 돌려줌", "→ NAND 를 안 건드린다 : 훨씬 빠름"], "gray", size=13)
    d.arrow(300, 115, 358, 105)
    d.arrow(300, 225, 358, 205)
    d.text(380, 312, "시뮬레이터의 Unmapped_Reads_Return_Zeros 와 같은 동작", 11.5, True, color=T)
    return d.svg("매핑 표")


def trim_expect():
    d = D(760, 330, "예상 : 4 KiB 랜덤 읽기 지연 (QD1)")
    ch = Chart(d, 85, 45, 640, 210, (0, 200), (0, 1.1), "읽기 한 번의 지연 (µs)", "비율",
               [(v, str(v)) for v in range(0, 201, 25)], [], grid=False)
    p1 = _bell(ch, 35, 6, 10, 70, 1.0)
    p2 = _bell(ch, 115, 18, 50, 190, 0.6)
    ch.area(p1, T, 0.3)
    ch.curve(p1, T, 2.5)
    ch.area(p2, B, 0.3)
    ch.curve(p2, B, 2.5)
    ch.note(45, 0.95, "매핑 없음 (TRIM 된 절반)", T, bold=True)
    ch.note(125, 0.66, "매핑 있음 (쓴 절반) : NAND 읽기", B, bold=True)
    d.text(400, 320, "위치와 폭은 예시 : USB 로는 어댑터 지연이 둘 다에 더해지므로 SATA 에서 잰다", 11.5, color="#566573")
    return d.svg("TRIM 예상")


def trim_gc():
    d = D(760, 270, "TRIM 이 GC 를 돕는 이유 : 지운 파일은 복사할 필요가 없다")
    def blk(x, title, states):
        d.text(x + 140, 52, title, 12.5, True, color=K)
        for i, s in enumerate(states):
            k = {"v": "new", "i": "gray", "d": "warn"}[s]
            d.box(x + (i % 8) * 35, 62 + (i // 8) * 35, 32, 32, "", [], k, rx=3)
    blk(20, "TRIM 없이 : 지운 파일 (빨강) 도 '유효'", "vvdddiivvdddivvi")
    blk(400, "TRIM 뒤 : 지운 파일은 '무효'", "vviiiiivviiiivvi")
    d.text(160, 160, "GC 가 옮길 페이지 : 12개", 12.5, True, color=R)
    d.text(540, 160, "GC 가 옮길 페이지 : 6개", 12.5, True, color=T)
    d.legend(150, 200, (("new", "유효"), ("gray", "무효"), ("warn", "지웠지만 SSD 는 모름")))
    d.text(380, 245, "블록 하나 (페이지 16개) 를 비울 때 : 옮길 페이지가 적을수록 WAF 가 작다", 11.5, color="#566573")
    return d.svg("TRIM 과 GC")


# ------------------------------------------------------------------ exp 8 : write cliff
def cliff_fill():
    d = D(760, 330, "빈 블록이 바닥나는 순간 GC 가 시작된다")
    stages = [("1. 막 지운 드라이브", "fffffffffffffff"), ("2. 쓰는 중", "vvvvvvfffffffff"),
              ("3. 빈 블록이 바닥", "vvmvmvvmvmvmvff"), ("4. GC", "vvmvmvvmvGvmvfn")]
    for i, (t, st) in enumerate(stages):
        x = 15 + i * 188
        d.text(x + 85, 50, t, 12.5, True, color=K)
        for j, c in enumerate(st):
            k = {"f": "white", "v": "new", "m": "chg", "G": "warn", "n": "teal"}[c]
            d.box(x + (j % 5) * 34, 62 + (j // 5) * 34, 31, 31, "", [], k, rx=3)
    d.legend(60, 200, (("white", "빈 블록"), ("new", "유효 데이터로 가득"), ("chg", "유효 + 무효 섞임"),
                       ("warn", "GC 대상 (victim)"), ("teal", "옮겨 받는 블록")))
    d.box(80, 230, 600, 80, "4. GC 한 번", ["무효 페이지가 가장 많은 블록을 고른다 → 유효 페이지만 새 블록으로 복사 → 지운다",
                                           "복사하는 동안 호스트 쓰기는 기다린다 : 이것이 IOPS 가 떨어지는 이유"], "warn", size=13)
    return d.svg("블록과 GC")


def cliff_expect():
    d = D(760, 360, "예상 : 4 KiB 랜덤 쓰기 IOPS, 용량의 2배를 쓰는 동안 (가설)")
    ch = Chart(d, 90, 50, 630, 220, (0, 240), (0, 50), "지금까지 쓴 양 (GB)", "IOPS (천)",
               [(v, str(v)) for v in range(0, 241, 40)], [(v, str(v)) for v in range(0, 51, 10)])
    ch.band(0, 95, T, "FOB (빈 드라이브)", 0.10, T)
    ch.band(95, 150, G, "전환", 0.12, G)
    ch.band(150, 240, R, "steady state", 0.08, R)
    pts = [(0, 38), (20, 37), (60, 36), (90, 34), (100, 18), (110, 9), (125, 5), (150, 3.5), (240, 3.3)]
    ch.curve(pts, B, 3)
    ch.vline(120, "#566573", True, "용량 120 GB", ly=150)
    ch.note(160, 12, "수천 IOPS : GC 가 쓰기를 막는다", R, bold=True)
    d.text(400, 340, "높이와 위치는 예시 (사양서 최대 랜덤 쓰기는 수만 IOPS) : 진짜 곡선은 실험으로", 11.5, color="#566573")
    return d.svg("cliff 예상")


def cliff_cost():
    d = D(760, 270, "GC 한 번의 비용 : 블록에 유효 페이지가 v 개 남아 있으면")
    for j in range(8):
        d.box(40 + j * 40, 60, 36, 36, "", [], "new" if j < 3 else "gray", rx=3)
    d.text(200, 52, "victim 블록 (페이지 N = 8, 유효 v = 3)", 12, True, color=K)
    d.arrow(200, 100, 200, 140, "유효 3개를 복사", lx=270)
    for j in range(8):
        d.box(40 + j * 40, 145, 36, 36, "", [], "new" if j < 3 else "white", rx=3)
    d.text(200, 200, "빈 자리 5개가 생긴다 → 호스트가 5개 쓸 때마다 NAND 에는 8개", 12)
    d.box(430, 60, 310, 125, "WAF = N / (N − v)", ["v = 0 → 1.0 (공짜)", "v = 3 → 8/5 = 1.6", "v = 6 → 8/2 = 4.0",
                                                "빈 공간 (OP) 이 적을수록 v 가 크다"], "teal", size=14)
    d.text(380, 250, "steady state 의 IOPS ≈ 빈 드라이브 IOPS ÷ WAF (대략)", 12, True, color=R)
    return d.svg("GC 비용")


# ------------------------------------------------------------------ exp 10 : over-provisioning
def _lambert_w0(x):
    w = -0.5 if x < -0.3 else 0.0
    for _ in range(100):
        e = math.exp(w)
        w -= (w * e - x) / (e * (w + 1))
    return w


def waf_model(rho):
    """uniform random writes, FIFO/greedy-like GC: WAF = a / (a + W0(-a e^-a)), a = 1 + rho (Desnoyers 2012)."""
    a = 1 + rho
    return a / (a + _lambert_w0(-a * math.exp(-a)))


RAW, SLC_TLC = 137.4, 9.0      # GB : 128 GiB of NAND (reported), 3 GB SLC buffer uses ~9 GB of TLC


def rho_of(span_gb):
    return (RAW - SLC_TLC - span_gb) / span_gb


def op_span():
    d = D(760, 300, "같은 NAND, 다른 여유 : 앞쪽 80% 만 쓰면 나머지 20% 도 여유 공간이 된다")
    def bar(y, label, parts):
        d.text(20, y + 24, label, 12.5, True, anchor="start", color=K)
        x = 140
        for gb, kind, t in parts:
            w = gb / RAW * 600
            d.box(x, y, w, 38, "", [t] if w > 50 else [], kind, rx=0, size=12)
            if w <= 50:
                d.text(x + w / 2, y - 6, t, 11.5, True)
            x += w
    bar(60, "span 100%", [(120, "tlc", "사용자 LBA 120 GB (전부 씀)"), (9, "slc", "SLC"), (8.4, "warn", "여유")])
    bar(140, "span 80%", [(96, "tlc", "쓰는 LBA 96 GB"), (24, "gray", "TRIM 된 24 GB"), (9, "slc", "SLC"), (8.4, "warn", "여유")])
    d.text(440, 205, "NAND 전체 약 137 GB (128 GiB) = 사용자 120 GB + 숨은 공간 약 17 GB", 12, color=K)
    d.text(440, 228, "숨은 공간에서 SLC 버퍼 (3 GB × 3) 를 빼면 진짜 여유는 약 8 GB 일 것으로 가정", 12, color=K)
    d.text(440, 262, "ρ (여유 ÷ 쓰는 데이터) : 100% → 8.4/120 = 0.07,  80% → 32.4/96 = 0.34", 12.5, True, color=R)
    return d.svg("OP span")


def op_curve():
    d = D(760, 380, "모델이 예측하는 WAF : 여유 비율 ρ 가 작으면 WAF 가 급히 커진다")
    ch = Chart(d, 90, 50, 630, 240, (0, 1.2), (0, 10), "ρ = 여유 공간 ÷ 쓰는 데이터", "WAF",
               [(v / 10, f"{v / 10:.1f}") for v in range(0, 13, 2)], [(v, str(v)) for v in range(0, 11, 2)])
    pts = [(r / 100, waf_model(r / 100)) for r in range(5, 121)]
    ch.curve([(a, min(b, 10)) for a, b in pts if b <= 10.5], T, 3)
    for span, col in ((100, R), (90, G), (80, B), (70, P)):
        r = rho_of(span * 1.2)
        w = waf_model(r)
        ch.dot(r, w, col, 6)
        ch.note(r + 0.03, w + 0.35, f"span {span}% : ρ {r:.2f}, WAF {w:.1f}", col, bold=True)
    d.text(400, 350, "모델 : 균일한 랜덤 쓰기 + FIFO/greedy 류 GC (Desnoyers 2012). 실제 펌웨어는 다를 수 있다", 11.5, color="#566573")
    d.text(400, 368, "가정 (NAND 128 GiB, SLC 버퍼 9 GB 차지) 이 틀리면 점들이 옆으로 움직인다 : 측정으로 거꾸로 추정한다", 11.5, color="#566573")
    return d.svg("WAF-OP 곡선")


def op_expect():
    d = D(760, 300, "예상 : steady state IOPS 는 1/WAF 에 비례 (span 100% = 1 로 놓고)")
    ch = Chart(d, 90, 45, 630, 180, (0, 5), (0, 5), "", "상대 IOPS",
               [(i + 1, f"span {s}%") for i, s in enumerate((100, 90, 80, 70))], [(v, str(v)) for v in range(0, 6)])
    base = waf_model(rho_of(120))
    for i, (s, col) in enumerate(((100, R), (90, G), (80, B), (70, P))):
        v = base / waf_model(rho_of(s * 1.2))
        d.fillrect(ch.X(i + 1) - 35, ch.Y(v), 70, ch.Y(0) - ch.Y(v), col, 0.6)
        d.text(ch.X(i + 1), ch.Y(v) - 8, f"× {v:.1f}", 12.5, True, color=col)
    d.text(400, 270, "필수는 100% (실험 8) 와 80%. 90% · 70% 는 시간이 되면 : 점이 많을수록 곡선과 비교하기 좋다", 11.5, color="#566573")
    return d.svg("OP 예상")


# ------------------------------------------------------------------ exp 12 : WAF from SMART
def waf_flow():
    d = D(760, 230, "호스트가 쓴 양과 NAND 에 쓴 양")
    d.box(20, 70, 160, 60, "호스트", ["100 GB 를 쓰라고 함"], "white", size=13)
    d.box(260, 70, 200, 60, "FTL", ["쓸 자리 마련 = GC"], "teal", size=13)
    d.box(540, 40, 200, 50, "새 데이터 100 GB", [], "new", size=13)
    d.box(540, 110, 200, 50, "GC 복사 (WAF−1)×100 GB", [], "warn", size=13)
    d.arrow(180, 100, 258, 100, "241 이 센다", ly=90)
    d.arrow(460, 90, 538, 65)
    d.arrow(460, 110, 538, 135)
    d.text(640, 190, "합계 = NAND 쓰기 : 177 로 추정", 12, True, color=R)
    d.text(380, 218, "WAF = NAND 쓰기 ÷ 호스트 쓰기", 13, True, color=K)
    return d.svg("WAF 흐름")


def waf_177():
    d = D(760, 290, "177 Wear_Leveling_Count : 블록들의 평균 지움 횟수")
    counts = [412, 413, 412, 414, 413, 412, 413, 413]
    for i, c in enumerate(counts):
        d.box(30 + i * 62, 60, 56, 56, "", [str(c)], "tlc", rx=4, size=13)
    d.text(270, 52, "블록마다 지운 횟수 (예)", 12, True, color=K)
    d.text(270, 140, "평균 413 → 177 의 raw 값", 12.5, True, color=T)
    d.box(560, 60, 180, 80, "모든 블록을 한 번씩", ["더 지우면 +1", "= NAND 전체를 한 번", "더 쓴 것 (약 137 GB)"], "teal", size=13)
    d.box(30, 175, 700, 85, "그래서", ["NAND 쓰기 ≈ (177 이 늘어난 수) × 137 GB",
                                    "눈금이 137 GB 씩이라 거칠다 : 177 이 5 이상 늘 만큼 써야 오차가 ±20% 안쪽",
                                    "smartdiff.py 가 이 계산과 오차 범위를 함께 출력한다"], "base", size=13)
    return d.svg("177")


def waf_expect():
    d = D(760, 300, "예상 WAF (모델 · 가설)")
    ch = Chart(d, 90, 45, 630, 180, (0, 4), (0, 9), "", "WAF",
               [(1, "순차 쓰기"), (2, "랜덤 span 100%"), (3, "랜덤 span 80%")], [(v, str(v)) for v in range(0, 10, 2)])
    for x, v, col, s in ((1, 1.1, T, "≈ 1"), (2, waf_model(rho_of(120)), R, f"≈ {waf_model(rho_of(120)):.1f}"),
                         (3, waf_model(rho_of(96)), B, f"≈ {waf_model(rho_of(96)):.1f}")):
        d.fillrect(ch.X(x) - 45, ch.Y(v), 90, ch.Y(0) - ch.Y(v), col, 0.6)
        d.text(ch.X(x), ch.Y(v) - 8, s, 13, True, color=col)
    d.text(400, 272, "순차 쓰기는 블록이 통째로 무효가 되어 GC 복사가 거의 없다 : WAF ≈ 1", 11.5, color="#566573")
    d.text(400, 290, "랜덤 쓰기 값은 실험 10 의 모델 값 : SMART 로 잰 값과 맞춰 본다", 11.5, color="#566573")
    return d.svg("WAF 예상")


# ------------------------------------------------------------------ exp 16 : retention
def ret_leak():
    d = D(760, 300, "전원이 없어도 셀의 전하는 조금씩 빠져나간다")
    d.box(60, 50, 260, 40, "제어 게이트", [], "base", rx=2, size=13)
    d.box(60, 95, 260, 50, "", [], "chg", rx=2, size=13)
    d.text(190, 112, "전하 저장층 (전자 = 데이터)", 12.5, True, color=K)
    d.box(60, 150, 260, 30, "얇은 절연막", [], "white", rx=2, size=12)
    d.box(60, 185, 260, 40, "채널 (실리콘)", [], "gray", rx=2, size=13)
    for x in (100, 150, 200, 250, 290):
        d.circle(x, 132, 6, B)
    d.arrow(150, 140, 135, 200, dash=True, color=R)
    d.arrow(250, 140, 265, 200, dash=True, color=R)
    d.text(210, 250, "새는 전자 → 문턱 전압이 내려간다", 12, True, color=R)
    d.box(400, 50, 340, 175, "빨리 새게 만드는 것", ["온도 : 따뜻할수록 빠르다", "닳은 정도 : P/E 가 많을수록 절연막이 약하다",
                                               "시간 : 몇 주 → 몇 년", "", "JEDEC 클라이언트 SSD 기준 : 수명이 다한 뒤에도",
                                               "30 °C 에서 1년 보관 (기준으로 알려진 값)"], "warn", size=13)
    return d.svg("전하 누설")


def ret_timeline():
    d = D(760, 200, "실험 16 의 시간표")
    pts = [(40, "0일", "ret-write", "전체에 검사 가능한 패턴"), (300, "", "보관", "전원 없이 2–4주"), (560, "N일", "ret-check", "속도 + 체크섬 확인")]
    d.line(60, 120, 700, 120, "#566573", 3)
    for x, day, t, s in pts:
        d.box(x, 50, 170, 50, t, [s], "teal" if t != "보관" else "gold", size=13)
        d.circle(x + 85, 120, 7, K)
        d.text(x + 85, 145, day, 12, True)
    d.text(380, 185, "실험 1 의 '1년 넘게 전원 없이 둔 데이터' 와 같은 그래프에 놓는다", 11.5, color="#566573")
    return d.svg("시간표")


def ret_expect():
    d = D(760, 310, "예상 : 같은 드라이브, 데이터 나이만 다르게 (가설)")
    ch = Chart(d, 90, 45, 630, 190, (0, 4), (0, 450), "", "읽기 속도 (MB/s)",
               [(1, "막 쓴 데이터"), (2, "2–4주 보관"), (3, "1년+ 전원 없음 (실험 1)")], [(v, str(v)) for v in range(0, 451, 100)])
    for x, v, col in ((1, 400, T), (2, 360, G), (3, 60, R)):
        d.fillrect(ch.X(x) - 45, ch.Y(v), 90, ch.Y(0) - ch.Y(v), col, 0.6)
        d.text(ch.X(x), ch.Y(v) - 8, "?", 14, True, color=col)
    d.text(400, 282, "몇 주 만으로는 차이가 작을 수 있다 : 차이가 없다는 것도 결과다", 11.5, color="#566573")
    d.text(400, 300, "체크섬 오류가 0 이 아니면 : 드라이브가 ECC 로도 못 고친 데이터", 11.5, True, color=R)
    return d.svg("retention 예상")


# ------------------------------------------------------------------ exp 18 : endurance
def life_chart():
    d = D(760, 380, "끝까지 쓰면 SMART 에서 보일 것 (가설)")
    ch = Chart(d, 90, 50, 630, 220, (0, 100), (0, 100), "시간 (쓴 양) →", "",
               [], [], grid=False)
    ch.curve([(0, 20), (100, 92)], T, 3)
    ch.note(60, 72, "177 : 평균 지움 횟수 (꾸준히 증가)", T, bold=True)
    ch.curve([(0, 2), (60, 3), (80, 8), (90, 25), (96, 60)], R, 3)
    ch.note(55, 30, "179 · 5 : 쓴 예비 블록 · 재할당 (끝에 급증)", R, bold=True)
    ch.vline(96, "#566573", True)
    ch.note(94, 97, "끝 : 읽기 전용? 응답 없음?", "#566573", anchor="end")
    d.text(400, 350, "177 의 '정규화 값' (100 에서 시작해 내려감) 은 펌웨어가 보는 남은 수명 %", 11.5, color="#566573")
    d.text(400, 368, "끝나는 모습 (읽기 전용으로 바뀌는지, 갑자기 사라지는지) 이 이 실험의 핵심 관찰", 11.5, True, color=K)
    return d.svg("수명 그래프")


def life_budget():
    d = D(760, 250, "얼마나 걸릴까 : 거친 계산 (가정이 많다)")
    items = [("P/E 한도", "TLC 약 1,000회?", "gold"), ("× NAND 137 GB", "= 137 TB", "tlc"),
             ("÷ WAF ≈ 7.8", "≈ 18 TB 호스트 쓰기", "warn"), ("÷ 12 MB/s", "≈ 17일", "teal")]
    for i, (t, s, k) in enumerate(items):
        x = 15 + i * 188
        d.box(x, 50, 170, 62, t, [s], k, size=13)
        if i:
            d.arrow(x - 16, 81, x - 2, 81)
    d.text(380, 150, "TLC 840 은 공개된 내구성 실험에서 한도보다 훨씬 오래 버틴 것으로 알려져 있다", 12, color=K)
    d.text(380, 172, "→ 몇 주에서 몇 달 : 시작하기 전에 기간 (HOURS) 과 멈출 기준을 정한다", 12, True, color=R)
    d.text(380, 210, "이미 쓴 만큼 (지금 177 값) 은 빼야 한다 : 실험 0 의 SMART 로 다시 계산한다", 11.5, color="#566573")
    return d.svg("수명 계산")


# ------------------------------------------------------------------ exp 19 : teardown
def board():
    d = D(760, 345, "SSD 기판에서 찾을 것")
    d.box(20, 120, 90, 80, "SATA", ["커넥터"], "white", size=13)
    d.box(160, 100, 200, 120, "컨트롤러 (MEX)", ["ARM 코어 3개 (알려진 값)", "FTL 펌웨어가 도는 곳", "ECC, SATA, NAND 채널"], "hw", size=13)
    d.box(160, 250, 200, 55, "DRAM", ["매핑 표 · 캐시"], "mem", size=13)
    d.arrow(110, 160, 158, 160)
    d.line(260, 220, 260, 250, "#7d3c98", 2)
    for i in range(4):
        y = 50 + i * 65
        d.box(470, y, 240, 52, f"NAND 패키지 {i + 1}?", ["안에 die 여러 장"], "tlc", size=13)
        d.path(f"M360,160 C420,160 420,{y + 26} 468,{y + 26}")
    d.text(415, 337, "패키지 수 · 표기는 열어 봐야 안다 : 사진을 찍어 오면 부품 번호로 찾아본다", 11.5, color="#566573")
    return d.svg("기판")


def sim_map():
    d = D(760, 220, "시뮬레이터의 계층과 실제 부품")
    lv = [("채널", "컨트롤러 핀 묶음"), ("칩", "NAND 패키지 안 die"), ("plane", "die 안"), ("블록", "지움 단위"), ("페이지", "읽기 · 쓰기 단위")]
    for i, (t, s) in enumerate(lv):
        x = 10 + i * 150
        d.box(x, 50, 135, 55, t, [s], "teal" if i < 2 else "tlc", size=13)
        if i:
            d.arrow(x - 13, 77, x - 2, 77)
    d.text(380, 150, "열어서 볼 수 있는 것은 앞의 둘 (채널은 배선, 칩은 패키지) 까지", 12, color=K)
    d.text(380, 175, "나머지는 데이터시트와 실험 (블록 크기 · 페이지 크기 추정) 으로", 12, color=K)
    return d.svg("계층")
