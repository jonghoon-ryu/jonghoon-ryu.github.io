# xv6 tutorial tools (not published: Jekyll skips folders starting with "_")

- `svg.py`       — tiny SVG helper (boxes, arrows, memory maps, bit fields). Fonts: Pretendard / JetBrains Mono.
- `figs/*.py`    — diagram functions, one module per tutorial page (`figs/step07.py` …) plus `figs/common.py`.
- `fig.py`       — `python3 fig.py PAGE NAME AFTER_REGEX` inserts/replaces the SVG `NAME()` in
                   `xv6/tutorial/PAGE/index.md` between `<!-- fig:NAME -->` markers, after the first line matching AFTER_REGEX.
- `changemap.py` — the "change map" of a tag (files touched, lines added/removed), from `git diff` in ~/Ryu/xv6-x86_64.
- `preview.sh`   — render diagrams to .preview/xv6-preview.png (git-ignored), to check them by eye.
- `apply.sh`     — re-insert every figure into every page (idempotent).
