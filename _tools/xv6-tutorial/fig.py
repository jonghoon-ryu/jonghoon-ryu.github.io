#!/usr/bin/env python3
# fig.py PAGE NAME AFTER_REGEX: put figs.<module>.NAME() into xv6/tutorial/PAGE/index.md,
# between <!-- fig:NAME --> markers, after the first line matching AFTER_REGEX.
# re-running replaces the figure in place.
import importlib, os, re, sys
HERE = os.path.dirname(os.path.abspath(__file__)); sys.path.insert(0, HERE)
BLOG = os.path.abspath(os.path.join(HERE, "..", ".."))


def put(page, name, after, module):
    fn = getattr(importlib.import_module("figs." + module), name)
    svg = fn()
    path = os.path.join(BLOG, "xv6/tutorial", page, "index.md") if page != "index" else os.path.join(BLOG, "xv6/tutorial/index.md")
    s = open(path).read()
    block = f"<!-- fig:{name} -->\n{svg}\n<!-- /fig:{name} -->"
    pat = re.compile(rf"<!-- fig:{name} -->\n.*?\n<!-- /fig:{name} -->", re.S)
    if pat.search(s):
        s = pat.sub(lambda m: block, s)
    else:
        m = re.search(after, s, re.M)
        if not m:
            raise SystemExit(f"{page}: anchor not found: {after}")
        end = s.index("\n", m.end()) + 1 if "\n" in s[m.end():] else len(s)
        # inside a code block? then after its closing fence
        if s[:m.start()].count("\n```") % 2 == 1:
            close = s.index("\n```", m.start())
            end = s.index("\n", close + 1) + 1
        s = s[:end] + "\n" + block + "\n" + s[end:]
    open(path, "w").write(s)


if __name__ == "__main__":
    put(sys.argv[1], sys.argv[2], sys.argv[3], sys.argv[4] if len(sys.argv) > 4 else sys.argv[1].replace("-", "").replace(".", "")[:6])
