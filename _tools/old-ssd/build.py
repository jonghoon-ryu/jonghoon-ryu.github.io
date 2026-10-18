#!/usr/bin/env python3
"""build.py : pages/<slug>.md -> old-ssd-experiments/<slug>/index.md (index -> old-ssd-experiments/index.md)

Macros in the page sources:
  @@FIG name@@         inline SVG from figs.name()
  @@STYLE@@            the shared <style> block (pages/_style.txt)
  @@NAV@@              previous / next links (order = PAGES below)
  ```table             a table: first line = header, cells split by " | ", `code` and **bold** work
"""
import html, os, re, sys

HERE = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, HERE)
import figs  # noqa: E402

SITE = os.path.abspath(os.path.join(HERE, "..", ".."))
OUT = os.path.join(SITE, "old-ssd-experiments")
PAGES = [  # slug, sidebar / nav title
    ("index", "헌 SSD 로 하는 실험"),
    ("ssd-tutorial", "SSD Q&A"),   # hand-written (no pages/ source): only listed for the nav
    ("linux-commands", "SSD 를 다루는 Linux 명령"),
    ("fio", "fio 사용법"),
    ("ref-fio-test", "Ref: fio test"),
    ("0-setup", "0. 준비"),
    ("1-old-data", "1. 오래된 데이터 읽기"),
    ("2-features", "2. 기능 · 자가 진단"),
    ("3-slc-cache", "3. SLC 캐시"),
    ("4-trim", "4. TRIM 과 매핑 없는 읽기"),
    ("5-perf-map", "5. 성능 지도"),
    ("6-write-size", "6. 쓰기 크기 · 정렬"),
    ("7-flush", "7. 쓰기 캐시 · FLUSH"),
    ("8-write-cliff", "8. Write cliff"),
    ("9-idle-gc", "9. 쉬는 동안 GC"),
    ("10-over-provisioning", "10. Over-provisioning"),
    ("11-hot-cold", "11. 뜨거운 데이터"),
    ("12-waf", "12. WAF (SMART)"),
    ("13-interference", "13. 읽기 · 쓰기 간섭"),
    ("14-secure-erase", "14. Secure Erase"),
    ("15-read-disturb", "15. Read disturb"),
    ("16-retention", "16. Retention"),
    ("17-power-loss", "17. 전원 차단"),
    ("18-endurance", "18. 끝까지 쓰기"),
    ("19-teardown", "19. 열어 보기"),
]


def url(slug):
    return "/old-ssd-experiments/" if slug == "index" else f"/old-ssd-experiments/{slug}/"


def inline(s):
    s = html.escape(s, quote=False)
    s = re.sub(r"`([^`]+)`", r"<code>\1</code>", s)
    s = re.sub(r"\*\*([^*]+)\*\*", r"<strong>\1</strong>", s)
    s = re.sub(r"\[([^\]]+)\]\(([^)]+)\)", r'<a href="\2">\1</a>', s)
    return s.replace("&lt;br&gt;", "<br>")


def table(body):
    rows = [r.split(" | ") for r in body.strip("\n").split("\n")]
    out = ['<div style="overflow-x:auto;"><table class="t">', "<thead><tr>"]
    out += [f"<th>{inline(c.strip())}</th>" for c in rows[0]]
    out.append("</tr></thead><tbody>")
    for r in rows[1:]:
        out.append("<tr>" + "".join(f"<td>{inline(c.strip())}</td>" for c in r) + "</tr>")
    out.append("</tbody></table></div>")
    return "\n".join(out)


def nav(slug):
    i = [p[0] for p in PAGES].index(slug)
    prev = f'<a href="{{{{ \'{url(PAGES[i - 1][0])}\' | relative_url }}}}">← {PAGES[i - 1][1]}</a>' if i > 0 else "<span></span>"
    nxt = f'<a href="{{{{ \'{url(PAGES[i + 1][0])}\' | relative_url }}}}">{PAGES[i + 1][1]} →</a>' if i + 1 < len(PAGES) else "<span></span>"
    return f'<div class="step-nav">{prev}{nxt}</div>'


def build(slug):
    path = os.path.join(HERE, "pages", slug + ".md")
    if not os.path.exists(path):          # a page written by hand in old-ssd-experiments/<slug>/
        return
    src = open(path).read()
    style = open(os.path.join(HERE, "pages", "_style.txt")).read().strip()
    src = src.replace("@@STYLE@@", style).replace("@@NAV@@", nav(slug))
    src = re.sub(r"@@FIG (\w+)@@", lambda m: getattr(figs, m.group(1))(), src)
    src = re.sub(r"```table\n(.*?)```", lambda m: table(m.group(1)), src, flags=re.S)
    dest = os.path.join(OUT, "index.md") if slug == "index" else os.path.join(OUT, slug, "index.md")
    os.makedirs(os.path.dirname(dest), exist_ok=True)
    open(dest, "w").write(src)
    left = re.findall(r"@@\w+[^@]*@@", src)
    print(f"{dest}" + (f"  UNRESOLVED {left}" if left else ""))


if __name__ == "__main__":
    for slug in sys.argv[1:] or [p[0] for p in PAGES]:
        build(slug)
