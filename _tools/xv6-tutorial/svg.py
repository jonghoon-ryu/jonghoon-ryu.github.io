# a tiny SVG helper for the xv6 tutorial pages: boxes, arrows, text, memory maps,
# register bit fields. output is one line of inline SVG (kramdown keeps it as HTML).
from html import escape

KINDS = {  # fill, stroke
    "base": ("#eef2f7", "#34495e"),
    "new": ("#eafaf1", "#1e8449"),      # added in this tag
    "chg": ("#fef9e7", "#b7950b"),      # changed in this tag
    "del": ("#fdedec", "#c0392b"),      # removed in this tag
    "hw": ("#f4ecf7", "#7d3c98"),       # hardware / firmware
    "mem": ("#ebf5fb", "#2874a6"),      # memory
    "gray": ("#f4f6f7", "#7f8c8d"),
    "white": ("#ffffff", "#566573"),
}
FONT = "'Pretendard Variable','Pretendard','Apple SD Gothic Neo','Malgun Gothic','Noto Sans KR','Noto Sans CJK KR','NanumGothic',sans-serif"
MONO = "'JetBrains Mono',ui-monospace,Menlo,Consolas,monospace"


class D:
    def __init__(self, w, h, title=None):
        self.w, self.h, self.p = w, h, []
        if title:
            self.text(w / 2, 22, title, 14, True, color="#2c3e50")

    def text(self, x, y, s, size=11.5, bold=False, anchor="middle", color="#4d5656", mono=False):
        size = max(size, 11.5)  # readable when the page shows the diagram smaller than 1000px
        est = sum((0.62 if mono else (0.58 if c.isupper() or c in "mwMW" else 0.5)) * size for c in str(s))
        left = x - est / 2 if anchor == "middle" else x - est if anchor == "end" else x
        if left < 0 or left + est > self.w:  # caption runs off the diagram
            import sys; print(f"OFFCANVAS {str(s)[:60]!r} ({left:.0f}..{left + est:.0f} of {self.w})", file=sys.stderr)
        fam = f' font-family="{MONO}" style="font-variant-ligatures:none"' if mono else ""
        self.p.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}"{" font-weight=\"700\"" if bold else ""}'
                      f' fill="{color}" text-anchor="{anchor}"{fam}>{escape(str(s))}</text>')

    def rect(self, x, y, w, h, kind="base", rx=0, sw=1.5):
        f, st = KINDS[kind]
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}" stroke="{st}" stroke-width="{sw}"/>')

    def box(self, x, y, w, h, title="", lines=(), kind="base", size=12.5, mono=False, dash=False, rx=8):
        f, st = KINDS[kind]
        d = ' stroke-dasharray="6 4"' if dash else ""
        self.p.append(f'<rect x="{x}" y="{y}" width="{w}" height="{h}" rx="{rx}" fill="{f}" stroke="{st}" stroke-width="2"{d}/>')
        n = (1 if title else 0) + len(lines)
        for i, t in enumerate(([title] if title else []) + list(lines)):  # warn when text will not fit
            sz = max(size if (title and i == 0) else size - 1.5, 11.5)
            est = sum((0.62 if mono else (0.58 if c.isupper() or c in "mwMW" else 0.5)) * sz for c in t)
            if est > w - 8:
                import sys; print(f"OVERFLOW {w}px box: {t[:60]!r} (~{est:.0f}px)", file=sys.stderr)
        if n > 1 and n * 16 + 8 > h:
            import sys; print(f"OVERFLOW {h}px tall box: {n} lines", file=sys.stderr)
        lh = 16
        y0 = y + h / 2 - (n - 1) * lh / 2 + 4
        if title:
            self.text(x + w / 2, y0, title, size, True, color="#2c3e50")
            y0 += lh
        for ln in lines:
            self.text(x + w / 2, y0, ln, size - 1.5, False, mono=mono)
            y0 += lh
        return (x, y, w, h)

    def arrow(self, x1, y1, x2, y2, label=None, dash=False, color="#7f8c8d", lx=None, ly=None):
        d = ' stroke-dasharray="5 4"' if dash else ""
        self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="2"{d} marker-end="url(#ae)"/>')
        if label:
            self.text(lx if lx is not None else (x1 + x2) / 2, ly if ly is not None else (y1 + y2) / 2 - 6, label, 10.5, color="#566573")

    def line(self, x1, y1, x2, y2, color="#bfc9ca", w=1.5, dash=False):
        d = ' stroke-dasharray="4 4"' if dash else ""
        self.p.append(f'<line x1="{x1}" y1="{y1}" x2="{x2}" y2="{y2}" stroke="{color}" stroke-width="{w}"{d}/>')

    def path(self, dstr, dash=False, color="#7f8c8d", arrow=True):
        d = ' stroke-dasharray="5 4"' if dash else ""
        a = ' marker-end="url(#ae)"' if arrow else ""
        self.p.append(f'<path d="{dstr}" fill="none" stroke="{color}" stroke-width="2"{d}{a}/>')

    def memmap(self, x, y, w, rows, title=None):
        """rows: (label, height, kind, addr_at_bottom_or_None), top (high) to bottom (low)."""
        if title:
            self.text(x + w / 2, y - 8, title, 12, True, color="#2c3e50")
        for label, h, kind, addr in rows:
            self.rect(x, y, w, h, kind)
            self.text(x + w / 2, y + h / 2 + 4, label, 11)
            if addr:
                self.text(x - 6, y + h + 4, addr, 10, anchor="end", mono=True, color="#566573")
            y += h
        return y

    def bits(self, x, y, w, nbits, fields, h=40, label=None, value=None):
        """register bit field, highest bit on the left. fields: (hi, lo, name, kind[, units]).
        units = display width share (default: the number of bits), so one-bit fields can be wide enough to read."""
        units = [f[4] if len(f) > 4 else f[0] - f[1] + 1 for f in fields]
        cw = w / sum(units)
        if label:
            self.text(x - 8, y + h / 2 + 4, label, 12, True, "end", "#2c3e50")
        bx = x
        for (hi, lo, name, kind, *_), u in zip(fields, units):
            bw = u * cw
            self.rect(bx, y, bw, h, kind)
            self.text(bx + bw / 2, y + h / 2 + 4, name, 10.5 if bw > 40 else 9.5)
            if hi != lo:
                self.text(bx + 2, y - 4, str(hi), 9, anchor="start", mono=True, color="#7f8c8d")
                self.text(bx + bw - 2, y - 4, str(lo), 9, anchor="end", mono=True, color="#7f8c8d")
            else:
                self.text(bx + bw / 2, y - 4, str(hi), 9, mono=True, color="#7f8c8d")
            if value is not None:
                v = (value >> lo) & ((1 << (hi - lo + 1)) - 1)
                self.text(bx + bw / 2, y + h + 15, f"{v:x}" if hi - lo >= 3 else str(v), 11, True, mono=True, color="#1e8449" if v else "#bfc9ca")
            bx += bw

    def legend(self, x, y, items=(("new", "새로 생김"), ("chg", "바뀜"), ("del", "지움"))):
        for k, label in items:
            f, st = KINDS[k]
            self.p.append(f'<rect x="{x}" y="{y - 10}" width="14" height="12" rx="2" fill="{f}" stroke="{st}" stroke-width="1.5"/>')
            self.text(x + 20, y, label, 10.5, anchor="start")
            x += 30 + 13 * len(label)

    def svg(self, aria):
        defs = ('<defs><marker id="ae" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="8" markerHeight="8" orient="auto">'
                '<path d="M0,0 L10,5 L0,10 z" fill="#7f8c8d"/></marker></defs>')
        return (f'<svg viewBox="0 0 {self.w} {self.h}" style="font-variant-ligatures:none;width:100%;max-width:{self.w}px;height:auto;display:block;margin:1rem auto;"'
                f' font-family="{FONT}" role="img" aria-label="{escape(aria)}">' + defs + "".join(self.p) + "</svg>")
