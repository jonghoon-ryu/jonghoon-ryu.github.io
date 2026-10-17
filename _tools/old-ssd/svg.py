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
FONT = "'IBM Plex Sans KR','IBM Plex Sans','Apple SD Gothic Neo','Malgun Gothic',sans-serif"
MONO = "'IBM Plex Mono','IBM Plex Sans KR',ui-monospace,Menlo,Consolas,monospace"


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
            self.text(x + w / 2, y0, title, size, True, color="#2c3e50", mono=mono and title.isascii())
            y0 += lh
        for ln in lines:
            self.text(x + w / 2, y0, ln, size - 1.5, False, mono=mono and ln.isascii())
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


# ---- additions for the old-SSD pages: charts, colours, rotated text ----------------------------
KINDS.update({
    "teal": ("#e8f3ef", "#1f6f5c"),
    "slc": ("#e8f3ef", "#1f6f5c"),
    "tlc": ("#ebf5fb", "#2874a6"),
    "warn": ("#fdedec", "#c0392b"),
    "gold": ("#fef9e7", "#b7950b"),
})
C = {"teal": "#1f6f5c", "red": "#c0392b", "blue": "#2874a6", "gold": "#b7950b", "purple": "#7d3c98",
     "gray": "#7f8c8d", "ink": "#2c3e50", "light": "#d5dbdb"}


def _vtext(self, x, y, s, size=11.5, color="#4d5656", bold=False):
    self.p.append(f'<text x="{x:.1f}" y="{y:.1f}" font-size="{size}" fill="{color}" text-anchor="middle"'
                  f'{" font-weight=\"700\"" if bold else ""} transform="rotate(-90 {x:.1f} {y:.1f})">{escape(str(s))}</text>')


def _poly(self, pts, color="#1f6f5c", w=2.5, dash=False, fill=None, opacity=1.0):
    d = ' stroke-dasharray="7 5"' if dash else ""
    f = fill if fill else "none"
    self.p.append(f'<polyline points="{" ".join(f"{x:.1f},{y:.1f}" for x, y in pts)}" fill="{f}" fill-opacity="{opacity}"'
                  f' stroke="{color}" stroke-width="{w}"{d} stroke-linejoin="round" stroke-linecap="round"/>')


def _circle(self, x, y, r, fill="#1f6f5c", stroke="none", sw=1.5):
    self.p.append(f'<circle cx="{x:.1f}" cy="{y:.1f}" r="{r}" fill="{fill}" stroke="{stroke}" stroke-width="{sw}"/>')


def _fillrect(self, x, y, w, h, fill, opacity=1.0, stroke="none", sw=1.0, rx=0):
    self.p.append(f'<rect x="{x:.1f}" y="{y:.1f}" width="{w:.1f}" height="{h:.1f}" rx="{rx}" fill="{fill}"'
                  f' fill-opacity="{opacity}" stroke="{stroke}" stroke-width="{sw}"/>')


D.vtext, D.poly, D.circle, D.fillrect = _vtext, _poly, _circle, _fillrect


class Chart:
    """data -> SVG coordinates inside D, with axes, ticks and grid."""

    def __init__(self, d, x, y, w, h, xr, yr, xlabel="", ylabel="", xticks=(), yticks=(), grid=True):
        self.d, self.x, self.y, self.w, self.h, self.xr, self.yr = d, x, y, w, h, xr, yr
        if grid:
            for t, _ in yticks:
                d.line(x, self.Y(t), x + w, self.Y(t), "#eaeded", 1)
        d.line(x, y + h, x + w, y + h, "#566573", 1.5)
        d.line(x, y, x, y + h, "#566573", 1.5)
        for t, s in xticks:
            d.line(self.X(t), y + h, self.X(t), y + h + 5, "#566573", 1.2)
            d.text(self.X(t), y + h + 19, s, 11.5)
        for t, s in yticks:
            d.line(x - 5, self.Y(t), x, self.Y(t), "#566573", 1.2)
            d.text(x - 9, self.Y(t) + 4, s, 11.5, anchor="end")
        if xlabel:
            d.text(x + w / 2, y + h + 40, xlabel, 12, color="#2c3e50")
        if ylabel:
            d.vtext(x - 52, y + h / 2, ylabel, 12, color="#2c3e50")

    def X(self, v):
        return self.x + (v - self.xr[0]) / (self.xr[1] - self.xr[0]) * self.w

    def Y(self, v):
        return self.y + self.h - (v - self.yr[0]) / (self.yr[1] - self.yr[0]) * self.h

    def curve(self, pts, color="#1f6f5c", w=2.5, dash=False):
        self.d.poly([(self.X(a), self.Y(b)) for a, b in pts], color, w, dash)

    def area(self, pts, color, opacity=0.15):
        P = [(self.X(a), self.Y(b)) for a, b in pts]
        P = [(P[0][0], self.Y(self.yr[0]))] + P + [(P[-1][0], self.Y(self.yr[0]))]
        self.d.poly(P, "none", 0, fill=color, opacity=opacity)

    def band(self, x0, x1, fill, label=None, opacity=0.12, color="#566573", ly=None):
        self.d.fillrect(self.X(x0), self.y, self.X(x1) - self.X(x0), self.h, fill, opacity)
        if label:
            self.d.text((self.X(x0) + self.X(x1)) / 2, ly if ly else self.y + 16, label, 11.5, True, color=color)

    def hline(self, v, color="#7f8c8d", dash=True, label=None, at="end"):
        self.d.line(self.x, self.Y(v), self.x + self.w, self.Y(v), color, 1.4, dash)
        if label:
            xx = self.x + self.w - 4 if at == "end" else self.x + 6
            self.d.text(xx, self.Y(v) - 6, label, 11.5, anchor="end" if at == "end" else "start", color=color)

    def vline(self, v, color="#7f8c8d", dash=True, label=None, ly=None):
        self.d.line(self.X(v), self.y, self.X(v), self.y + self.h, color, 1.4, dash)
        if label:
            self.d.text(self.X(v) + 5, ly if ly else self.y + 14, label, 11.5, anchor="start", color=color)

    def dot(self, a, b, color="#1f6f5c", r=4.5):
        self.d.circle(self.X(a), self.Y(b), r, color)

    def note(self, a, b, s, color="#2c3e50", anchor="start", size=11.5, bold=False):
        self.d.text(self.X(a), self.Y(b), s, size, bold, anchor=anchor, color=color)
