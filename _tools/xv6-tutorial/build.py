#!/usr/bin/env python3
# build.py [PAGE...]: build xv6/tutorial pages from pages/*.md, resolving macros against
# the real code at each tag in ~/Ryu/xv6-x86_64. The tutorial is written in English.
#   @@L tag file pattern@@            -> [file:N](GitHub link at tag)
#   @@CODE tag | file | from | to [| lang]@@  -> code block from the first match of `from`
#                                        through the next match of `to` (regexes; no "|" inside)
#   @@STAT prev tag@@                 -> table of changed files (no docs, PDFs, TODO.md)
#   @@FIG module name@@               -> figs.<module>.<name>() between <!-- fig:name --> markers
#   @@IMG name caption@@              -> an image already in assets/image/
import importlib, os, re, subprocess, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
BLOG = os.path.abspath(os.path.join(HERE, "..", ".."))
REPO = os.path.expanduser("~/Ryu/xv6-x86_64")
GH = "https://github.com/jonghoon-ryu/xv6-x86_64/blob"
EX = ["--", ".", ":!docs", ":!*.pdf", ":!TODO.md"]
_cache = {}


def git(*a):
    return subprocess.run(["git", "-C", REPO, *a], capture_output=True, text=True, check=True).stdout


def show(tag, f):
    if (tag, f) not in _cache:
        _cache[(tag, f)] = git("show", f"{tag}:{f}").split("\n")
    return _cache[(tag, f)]


def find(lines, pat, start=0):
    r = re.compile(pat)
    for i in range(start, len(lines)):
        if r.search(lines[i]):
            return i
    raise SystemExit(f"pattern not found: {pat!r}")


def m_link(m):
    tag, f, pat = m.group(1), m.group(2), m.group(3)
    n = find(show(tag, f), pat) + 1
    return f"[`{f}:{n}`]({GH}/{tag}/{f}#L{n})"


def m_code(m):
    a = [x.strip() for x in m.group(1).split("|")]
    tag, f, frm, to = a[:4]
    lang = a[4] if len(a) > 4 else ("asm" if f.endswith(".S") else "cpp" if f.endswith((".cpp", ".h", ".c")) else "make" if f == "Makefile" else "")
    lines = show(tag, f)
    i = find(lines, frm)
    j = find(lines, to, i + 1) if to != "." else i
    return (f"[`{f}:{i + 1}–{j + 1}`]({GH}/{tag}/{f}#L{i + 1}-L{j + 1}) (tag `{tag}`)\n\n```{lang}\n" + "\n".join(lines[i:j + 1]) + "\n```")


def m_stat(m):
    prev, tag = m.group(1), m.group(2)
    st = {}
    for ln in git("diff", "--name-status", prev, tag, *EX).strip().split("\n"):
        p = ln.split("\t"); st[p[-1]] = {"A": "new", "D": "deleted", "M": "changed"}.get(p[0][0], "renamed")
    rows = ["| File | | Added | Removed |", "|---|---|---:|---:|"]
    ta = td = n = 0
    for ln in git("diff", "--numstat", prev, tag, *EX).strip().split("\n"):
        a, d, f = ln.split("\t"); a = int(a) if a != "-" else 0; d = int(d) if d != "-" else 0
        ta += a; td += d; n += 1
        rows.append(f"| `{f}` | {st.get(f, 'changed')} | {a} | {d} |")
    rows.append(f"| **Total** ({n} files) | | **{ta}** | **{td}** |")
    return "\n".join(rows)


def m_fig(m):
    mod, name = m.group(1), m.group(2)
    svg = getattr(importlib.import_module("figs." + mod), name)()
    return f"<!-- fig:{name} -->\n{svg}\n<!-- /fig:{name} -->"


def m_img(m):
    name, cap = m.group(1), m.group(2)
    if not os.path.exists(os.path.join(BLOG, "assets/image", name)):
        raise SystemExit(f"missing image assets/image/{name}")
    return f"![{cap}](/assets/image/{name})"


def build(slug):
    text = open(os.path.join(HERE, "pages", slug + ".md")).read()
    text = re.sub(r"@@L (\S+) (\S+) (.+?)@@", m_link, text)
    text = re.sub(r"@@CODE (.+?)@@", m_code, text)
    text = re.sub(r"@@STAT (\S+) (\S+)@@", m_stat, text)
    text = re.sub(r"@@FIG (\w+) (\w+)@@", m_fig, text)
    text = re.sub(r"@@IMG (\S+) (.+?)@@", m_img, text)
    left = re.findall(r"@@\w+", text)
    if left:
        raise SystemExit(f"{slug}: unresolved {left}")
    out = os.path.join(BLOG, "xv6/tutorial", "" if slug == "index" else slug, "index.md")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w").write(text)
    print("wrote", os.path.relpath(out, BLOG))


if __name__ == "__main__":
    for slug in sys.argv[1:] or sorted(f[:-3] for f in os.listdir(os.path.join(HERE, "pages")) if f.endswith(".md")):
        build(slug)
