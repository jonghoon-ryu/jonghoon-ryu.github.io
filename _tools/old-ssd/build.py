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
    ("linux-commands", "SSD 를 다루는 Linux 명령"),
    ("0-setup", "0. 준비"),
    ("1-old-data", "1. 오래된 데이터 읽기"),
    ("2-slc-cache", "2. SLC 캐시"),
    ("3-trim", "3. TRIM 과 매핑 없는 읽기"),
    ("4-write-cliff", "4. Write cliff"),
    ("5-over-provisioning", "5. Over-provisioning"),
    ("6-waf", "6. WAF (SMART)"),
    ("7-retention", "7. Retention"),
    ("8-endurance", "8. 끝까지 쓰기"),
    ("9-teardown", "9. 열어 보기"),
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
    src = open(os.path.join(HERE, "pages", slug + ".md")).read()
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
