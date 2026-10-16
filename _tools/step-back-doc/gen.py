#!/usr/bin/env python3
"""Builds ftl-visual-simulator/reference/step-back/index.md (blog) with inline SVGs."""
import sys

FONT = "'IBM Plex Sans KR','IBM Plex Sans','Noto Sans KR','NanumGothic','Apple SD Gothic Neo','Malgun Gothic',sans-serif"
MONO = "'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,monospace"
INK, SUB, MUTE, LINE = '#2c3e50', '#4d5656', '#7f8c8d', '#7f8c8d'
C = {  # fill, stroke
    'blue': ('#ebf5fb', '#2874a6'), 'green': ('#e9f7ef', '#1e8449'), 'yellow': ('#fef9e7', '#b7950b'),
    'red': ('#fdedec', '#c0392b'), 'purple': ('#f4ecf7', '#7d3c98'), 'gray': ('#f4f6f7', '#7f8c8d'),
    'orange': ('#fdf2e9', '#ca6f1e'),
}


def esc(s):
    return s.replace('&', '&amp;').replace('<', '&lt;').replace('>', '&gt;')


class Svg:
    def __init__(self, w, h, label, mid):
        self.w, self.h, self.label, self.mid = w, h, label, mid
        self.parts = []

    def add(self, s):
        self.parts.append(s)

    def text(self, x, y, s, size=11, weight=None, fill=SUB, anchor='middle', mono=False, italic=False):
        a = f' font-weight="{weight}"' if weight else ''
        if mono:
            a += f' font-family="{MONO}"'
        if italic:
            a += ' font-style="italic"'
        self.add(f'<text x="{x}" y="{y}" font-size="{size}"{a} fill="{fill}" text-anchor="{anchor}">{esc(s)}</text>')

    def box(self, x, y, w, h, color, title=None, lines=(), dashed=False, sw=2, rx=8, title_size=12.5, line_size=11, mono_lines=False):
        f, st = C[color]
        d = ' stroke-dasharray="6 4"' if dashed else ''
        self.add(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}" stroke="{st}" stroke-width="{sw}"{d}/>')
        n = (1 if title else 0) + len(lines)
        step = 17
        y0 = y + h / 2 - (n - 1) * step / 2 + 4
        i = 0
        if title:
            self.text(x + w / 2, y0, title, title_size, '700', INK)
            i = 1
        for ln in lines:
            self.text(x + w / 2, y0 + i * step, ln, line_size, None, SUB, mono=mono_lines)
            i += 1

    def arrow(self, x1, y1, x2, y2, label=None, lx=None, ly=None, color=LINE, dashed=False):
        d = ' stroke-dasharray="5 4"' if dashed else ''
        self.add(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2"{d} marker-end="url(#{self.mid})"/>')
        if label:
            self.text(lx if lx is not None else (x1 + x2) / 2, ly if ly is not None else (y1 + y2) / 2 - 6, label, 10.5, None, '#566573')

    def path(self, d, dashed=False, color=LINE):
        da = ' stroke-dasharray="5 4"' if dashed else ''
        self.add(f'<path d="{d}" fill="none" stroke="{color}" stroke-width="2"{da} marker-end="url(#{self.mid})"/>')

    def render(self):
        head = (f'<svg viewBox="0 0 {self.w} {self.h}" style="font-variant-ligatures:none;width:100%;max-width:{self.w}px;height:auto;display:block;margin:1rem auto;" '
                f'font-family="{FONT}" role="img" aria-label="{esc(self.label)}"><defs><marker id="{self.mid}" viewBox="0 0 10 10" refX="9" refY="5" '
                f'markerWidth="8" markerHeight="8" orient="auto"><path d="M0,0 L10,5 L0,10 z" fill="{LINE}"/></marker></defs>')
        return head + ''.join(self.parts) + '</svg>'


# ---------------------------------------------------------------- figures

def fig_two_places():
    s = Svg(980, 330, '시뮬레이터 상태가 있는 두 곳', 'asbtwo')
    s.text(490, 20, '되돌려야 하는 상태는 두 군데에 있다', 13, '700', INK)
    # worker
    s.add(f'<rect x="15" y="40" width="430" height="250" rx="10" fill="#fbfcfc" stroke="#d5d8dc"/>')
    s.text(230, 62, 'Web Worker — WASM 으로 컴파일한 MQSim', 12, '700', INK)
    s.box(35, 80, 190, 60, 'blue', '이벤트 큐', ['다음에 일어날 일들 (시간순)'])
    s.box(235, 80, 190, 60, 'blue', '매핑 테이블', ['LPN → 물리 page'])
    s.box(35, 150, 190, 60, 'blue', 'block · page 상태', ['valid / invalid / free, erase 횟수'])
    s.box(235, 150, 190, 60, 'blue', '칩 · TSU 큐', ['진행 중인 read/program/erase'])
    s.box(35, 220, 390, 55, 'blue', 'GC/WL 진행 상태, 캐시, 통계, 난수 생성기 …', [])
    # main thread
    s.add(f'<rect x="535" y="40" width="430" height="250" rx="10" fill="#fbfcfc" stroke="#d5d8dc"/>')
    s.text(750, 62, '메인 스레드 — React 화면', 12, '700', INK)
    s.box(555, 80, 190, 60, 'green', '로그', ['최근 50줄, 줄 번호'])
    s.box(755, 80, 190, 60, 'green', '격자 테두리', ['방금 쓴/옮긴/지운 칸'])
    s.box(555, 150, 190, 60, 'green', '차트 기록', ['빈 block 수, 읽기 지연'])
    s.box(755, 150, 190, 60, 'green', '통계 카운터', ['호스트 쓰기/읽기, GC 이동'])
    s.box(555, 220, 390, 55, 'green', 'LPN 여정, GC victim 설명, WL 발동 기록 …', [])
    s.arrow(445, 120, 535, 120, '이벤트', 490, 112)
    s.arrow(445, 190, 535, 190, 'getState()', 490, 182)
    s.text(490, 316, '화면의 상태는 엔진이 보낸 이벤트를 쌓아서 만든 것이다 — 엔진만 되돌리면 화면은 그대로 "미래" 를 보여 준다', 11, None, '#566573', italic=True)
    return s.render()


def fig_two_options():
    s = Svg(980, 300, '두 가지 방법 비교', 'asbopt')
    s.text(490, 20, '"한 줄 뒤로" 를 만드는 두 가지 방법', 13, '700', INK)
    # timeline of lines
    x0, dx = 150, 42
    for row, (title, color, y) in enumerate([('A. 처음부터 다시', 'orange', 60), ('B. 스냅샷', 'purple', 170)]):
        f, st = C[color]
        s.text(20, y + 24, title, 12, '700', st, anchor='start')
        for i in range(17):
            x = x0 + i * dx
            filled = i < 16
            s.add(f'<rect x="{x}" y="{y + 8}" width="{dx - 6}" height="26" rx="4" fill="{"#fbfcfc" if not filled else f}" stroke="{st if filled else "#d5d8dc"}" stroke-width="1.5"/>')
            s.text(x + (dx - 6) / 2, y + 26, str(i + 1) if i < 16 else '…', 10, None, SUB)
    # A: arrow from 0 replay to 15
    s.path(f'M{x0 + 16 * dx - 20},{60 + 4} L{x0 + 16 * dx - 20},{48} L{x0 + 4},{48} L{x0 + 4},{64}')
    s.text(x0 + 8 * dx, 42, '⏪ = init() 후 1 ~ 15 줄을 다시 실행 → 늦게 누를수록 오래 걸리고, 화면 상태도 전부 다시 쌓아야 함', 10.5, None, '#566573')
    s.text(490, 120, '줄 16 을 보고 있을 때 ⏪ 를 누르면 → 줄 15 까지의 상태가 필요하다', 11, '700', INK)
    # B: snapshots under each box
    for i in range(16):
        x = x0 + i * dx
        s.add(f'<rect x="{x + 6}" y="{214}" width="{dx - 18}" height="16" rx="3" fill="#f4ecf7" stroke="#7d3c98" stroke-width="1"/>')
    s.text(x0 - 10, 226, '스냅샷', 10, None, '#7d3c98', anchor='end')
    s.path(f'M{x0 + 15 * dx + 12},{230} L{x0 + 15 * dx + 12},{250} L{x0 + 14 * dx + 12},{250} L{x0 + 14 * dx + 12},{232}', color='#7d3c98')
    s.text(x0 + 11 * dx, 268, '⏪ = 줄 16 직전에 찍어 둔 사본 하나를 되돌려 씀 → 언제 누르든 약 1 ms', 10.5, None, '#566573')
    s.text(490, 292, '이 시뮬레이터는 B 를 골랐다 (각 줄을 진행하기 직전에 사본을 하나씩 만든다)', 11, None, '#566573', italic=True)
    return s.render()


def fig_memory():
    s = Svg(980, 330, 'WASM 선형 메모리 배치', 'asbmem')
    s.text(490, 20, 'WASM 선형 메모리 하나 — MQSim 의 모든 것이 이 바이트 배열 안에 있다', 13, '700', INK)
    y, h = 70, 60
    # segments (not to scale)
    segs = [
        (40, 110, 'green', '정적 데이터', ['약 77 KB'], False),
        (150, 260, 'gray', 'C++ 스택', ['16 MB (STACK_SIZE)'], True),
        (410, 230, 'green', '힙', ['약 2.2 ~ 2.4 MB'], False),
        (640, 300, 'gray', '아직 안 쓴 공간', ['128 MB 까지 (필요하면 자람)'], True),
    ]
    for x, w, color, title, lines, dashed in segs:
        s.box(x, y, w, h, color, title, lines, dashed=dashed, rx=2)
    # addresses
    for x, lab in [(40, '0'), (150, 'stackLow = 79,152'), (410, 'stackHigh = 16,856,368'), (640, 'heapEnd = sbrk(0) ≈ 19.2 MB')]:
        s.add(f'<line x1="{x}" y1="{y - 8}" x2="{x}" y2="{y + h + 8}" stroke="{INK}" stroke-width="1.5"/>')
        s.text(x, y - 14, lab, 10.5, None, INK, mono=True)
    s.text(940, y - 14, '128 MB', 10.5, None, INK, mono=True)
    # copy / skip labels
    s.text(95, y + h + 30, '복사 ✔', 12, '700', '#1e8449')
    s.text(280, y + h + 30, '건너뜀 — 호출이 없을 땐 비어 있다', 11.5, '700', MUTE)
    s.text(525, y + h + 30, '복사 ✔', 12, '700', '#1e8449')
    s.text(790, y + h + 30, '건너뜀 — 아무것도 없다', 11.5, '700', MUTE)
    # what's inside
    s.box(40, 200, 370, 95, 'green', '정적 데이터', ['전역/static 변수 (Stats 카운터, 이벤트 콜백 포인터 …)', '+ 힙 끝 위치를 기억하는 sbrk 포인터 자체'], line_size=10.5)
    s.box(430, 200, 510, 95, 'green', '힙 (new / malloc 으로 만든 모든 것)', ['SSD_Device, FTL, 매핑 테이블, block pool, 이벤트 트리,', 'TSU 큐, 트랜잭션 객체, malloc 의 빈칸 장부 …'], line_size=10.5)
    s.text(490, 320, '스냅샷 = [0, stackLow) + [stackHigh, heapEnd) — GC 시연 기준 약 2.5 MB', 11, None, '#566573', italic=True)
    return s.render()


def fig_stack_idle():
    s = Svg(980, 230, '스택이 비어 있는 시점', 'asbidle')
    s.text(490, 20, '스냅샷은 WASM 함수가 실행 중이지 않을 때만 찍는다', 13, '700', INK)
    s.text(20, 75, '워커 (JS)', 11.5, '700', INK, anchor='start')
    s.text(20, 145, 'WASM', 11.5, '700', INK, anchor='start')
    s.add(f'<line x1="110" y1="70" x2="960" y2="70" stroke="#d5d8dc" stroke-width="2"/>')
    s.add(f'<line x1="110" y1="140" x2="960" y2="140" stroke="#d5d8dc" stroke-width="2"/>')
    calls = [(170, 180, 'stepEvent()'), (430, 90, 'getState()'), (640, 180, 'stepEvent()')]
    for x, w, name in calls:
        s.box(x, 122, w, 36, 'blue', None, [], rx=4)
        s.text(x + w / 2, 145, name, 11, '700', INK, mono=True)
        s.arrow(x, 74, x, 120, color='#2874a6')
        s.arrow(x + w, 120, x + w, 74, color='#2874a6')
    s.text(260, 182, '스택 사용 중 — 이 안에서는 찍을 수 없다', 10.5, None, '#2874a6')
    for x in (140, 395, 590):
        s.add(f'<circle cx="{x}" cy="70" r="8" fill="#f4ecf7" stroke="#7d3c98" stroke-width="2"/>')
        s.text(x, 52, '찍을 수 있음', 10.5, '700', '#7d3c98')
    s.text(490, 215, '함수가 return 하면 스택 포인터는 맨 위로 돌아가 있다 → 스택 내용은 다시는 읽히지 않는 쓰레기라 복사할 필요가 없다', 11, None, '#566573', italic=True)
    return s.render()


def fig_flow():
    s = Svg(980, 400, '한 줄 진행과 되돌리기의 흐름', 'asbflow')
    s.text(490, 20, '"1 step" 과 "⏪ 1 step" 이 하는 일', 13, '700', INK)
    # forward
    s.text(20, 55, '1 step', 12.5, '700', '#1e8449', anchor='start')
    fw = [
        ('green', '① 엔진 사본', ['worker 가 메모리 복사', '→ 엔진 스택에 push']),
        ('green', '② 화면 사본', ['각 hook 의 snapshot()', '→ 화면 스택에 push']),
        ('blue', '③ stepEvent()', ['로그 한 줄이 생길 때까지', '엔진 진행 (이벤트 발생)']),
        ('blue', '④ getState + commit', ['격자·로그·차트를', '새 상태로 그림']),
    ]
    for i, (c, t, ls) in enumerate(fw):
        x = 20 + i * 240
        s.box(x, 70, 210, 75, c, t, ls)
        if i:
            s.arrow(x - 30, 107, x, 107)
    # stacks
    s.add(f'<rect x="250" y="170" width="480" height="100" rx="10" fill="#fbfcfc" stroke="#d5d8dc"/>')
    s.text(490, 190, '두 스택은 항상 같은 높이 (최대 30)', 11.5, '700', INK)
    for j, lab in enumerate(['엔진 사본 (worker)', '화면 사본 (메인 스레드)']):
        yy = 205 + j * 32
        s.text(270, yy + 17, lab, 10.5, None, SUB, anchor='start')
        for k in range(5):
            f, st = C['purple']
            s.add(f'<rect x="{430 + k * 56}" y="{yy}" width="50" height="24" rx="4" fill="{f}" stroke="{st}" stroke-width="1.5"/>')
            s.text(430 + k * 56 + 25, yy + 16, f'줄 {k + 12}' if k < 4 else '줄 16', 10, None, SUB)
    s.path('M125,145 L125,217 L248,217', color='#1e8449', dashed=True)
    s.path('M365,145 L365,168', color='#1e8449', dashed=True)
    s.text(135, 208, '① push', 10.5, '700', '#1e8449', anchor='start')
    s.text(375, 162, '② push', 10.5, '700', '#1e8449', anchor='start')
    # back
    s.text(20, 300, '⏪ 1 step', 12.5, '700', '#7d3c98', anchor='start')
    bw = [
        ('purple', '① 엔진 사본 pop', ['메모리에 그대로', '되돌려 씀 (≈1 ms)']),
        ('purple', '② getState()', ['되돌린 엔진에서', '격자·통계를 다시 읽음']),
        ('purple', '③ 화면 사본 pop', ['각 hook 의 restore()', '로그·테두리·차트 복원']),
        ('gray', '④ 다시 진행하면', ['같은 이벤트가', '같은 순서로 또 일어남']),
    ]
    for i, (c, t, ls) in enumerate(bw):
        x = 20 + i * 240
        s.box(x, 315, 210, 75, c, t, ls)
        if i:
            s.arrow(x - 30, 352, x, 352)
    s.path('M730,220 L850,220 L850,300 L125,300 L125,315', color='#7d3c98', dashed=True)
    s.text(760, 212, '①③ pop (맨 위)', 10.5, '700', '#7d3c98', anchor='start')
    return s.render()


def fig_verify():
    s = Svg(980, 220, '되돌리기 검증 방법', 'asbver')
    s.text(490, 20, '검증: 같은 지점에서 두 번 달려 보기', 13, '700', INK)
    s.box(20, 70, 150, 60, 'gray', '줄 N 까지 진행', [])
    s.box(220, 40, 170, 50, 'purple', '스냅샷', ['메모리 복사'])
    s.box(440, 40, 230, 50, 'blue', '5줄 진행 → 기록 A', ['이벤트 전부 + getState()'])
    s.box(220, 120, 170, 50, 'purple', '스냅샷 되돌림', [])
    s.box(440, 120, 230, 50, 'blue', '5줄 진행 → 기록 B', ['이벤트 전부 + getState()'])
    s.box(730, 75, 230, 60, 'green', 'A === B', ['글자 하나까지 같아야 통과'])
    s.arrow(170, 95, 220, 68)
    s.arrow(390, 65, 440, 65)
    s.path('M555,90 L555,105 L305,105 L305,120')
    s.arrow(390, 145, 440, 145)
    s.arrow(670, 65, 730, 95)
    s.arrow(670, 145, 730, 115)
    s.text(490, 205, '되돌림이 조금이라도 빠뜨린 게 있으면 B 는 A 와 다른 시점에서 출발하므로 결과가 달라진다', 11, None, '#566573', italic=True)
    return s.render()


FIGS = {
    'two_places': fig_two_places, 'two_options': fig_two_options, 'memory': fig_memory,
    'stack_idle': fig_stack_idle, 'flow': fig_flow, 'verify': fig_verify,
}

if __name__ == '__main__':
    src, out = sys.argv[1], sys.argv[2]
    text = open(src, encoding='utf-8').read()
    for name, fn in FIGS.items():
        text = text.replace(f'@@SVG {name}@@', fn())
    assert '@@SVG' not in text, 'unknown figure'
    open(out, 'w', encoding='utf-8').write(text)
