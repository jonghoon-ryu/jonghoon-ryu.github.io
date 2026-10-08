# shared diagrams: the change map of a tag, built from the real git diff.
import math, subprocess
from svg import D

REPO = "/home/ryuj/Ryu/xv6-x86_64"


def numstat(prev, tag):
    run = lambda *a: subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, check=True).stdout
    ex = ["--", ".", ":!docs", ":!*.pdf", ":!TODO.md"]
    st = {}
    for ln in run("diff", "--name-status", prev, tag, *ex).strip().split("\n"):
        p = ln.split("\t"); st[p[-1]] = p[0][0]
    rows = []
    for ln in run("diff", "--numstat", prev, tag, *ex).strip().split("\n"):
        a, d, f = ln.split("\t")
        rows.append((f, st.get(f, "M"), int(a) if a != "-" else 0, int(d) if d != "-" else 0))
    return rows


def changemap(prev, tag, maxrows=1000, note=None):
    rows = numstat(prev, tag)
    order = {"A": 0, "M": 1, "D": 2}
    rows.sort(key=lambda r: (order.get(r[1], 1), -(r[2] + r[3])))
    shown, rest = rows[:maxrows], rows[maxrows:]
    big = max(max(r[2], r[3]) for r in rows) or 1
    scale = lambda n: 0 if n == 0 else 6 + 230 * math.sqrt(n / big)
    rh = 22
    h = 70 + rh * (len(shown) + (1 if rest else 0)) + 40
    d = D(1000, h, f"Change map: {prev} → {tag}  (lines added / removed per file; bar length ∝ √lines)")
    kind = {"A": "new", "M": "chg", "D": "del"}
    label = {"A": "new", "M": "changed", "D": "deleted"}
    y = 50
    d.text(300, y, "removed ←", 11, True, "end", "#c0392b"); d.text(320, y, "file", 11, True, "start", "#2c3e50")
    d.text(620, y, "→ added", 11, True, "start", "#1e8449")
    y += 10
    for f, s, a, dl in shown:
        k = kind.get(s, "chg")
        d.rect(305, y + 3, 10, rh - 6, k, rx=2)
        d.text(320, y + 15, f, 11, False, "start", mono=True)
        d.text(570, y + 15, label.get(s, "changed"), 10, False, "end", "#7f8c8d")
        if dl:
            w = scale(dl); d.rect(295 - w, y + 4, w, rh - 8, "del"); d.text(290 - w, y + 15, f"−{dl}", 10, False, "end", "#c0392b", True)
        if a:
            w = scale(a); d.rect(615, y + 4, w, rh - 8, "new"); d.text(620 + w, y + 15, f"+{a}", 10, False, "start", "#1e8449", True)
        y += rh
    if rest:
        ra, rd = sum(r[2] for r in rest), sum(r[3] for r in rest)
        kinds = {}
        for r in rest:
            kinds[label.get(r[1], "changed")] = kinds.get(label.get(r[1], "changed"), 0) + 1
        what = ", ".join(f"{k} {v}" for k, v in kinds.items())
        d.text(320, y + 15, f"… {len(rest)} more files ({what}): +{ra} −{rd}", 11, False, "start", "#566573")
        y += rh
    ta, td = sum(r[2] for r in rows), sum(r[3] for r in rows)
    d.text(500, y + 26, note or f"Total: {len(rows)} files, +{ta} −{td} lines (docs and PDFs not counted)", 11.5, True, color="#2c3e50")
    return d.svg(f"files changed from {prev} to {tag}")
