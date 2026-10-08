# xv6 tutorial tools (not published: Jekyll skips folders starting with "_")

The tutorial (/xv6/tutorial/) is written in **English**. The rest of the blog is Korean.

- `pages/<tag>.md` — page sources, with macros (`pages/_style.txt` is the shared style block)
- `build.py [PAGE...]` — builds `xv6/tutorial/<tag>/index.md` from the sources, resolving macros against
  the real code at each tag in ~/Ryu/xv6-x86_64:
  - `@@CODE tag | file | from | to@@`  code excerpt (regexes; no "|" inside them) with a link to that tag and line
  - `@@L tag file pattern@@`           link to a line
  - `@@STAT prev tag@@`                table of changed files
  - `@@FIG module name@@`              diagram `figs/<module>.py: name()`
  - `@@IMG file caption@@`             image already in assets/image/
- `svg.py`        — the SVG helper (boxes, arrows, memory maps, bit fields). Fonts: Pretendard / JetBrains Mono, no ligatures
- `figs/*.py`     — diagrams per page; `figs/common.py` + `figs/maps.py` make the change map of each tag from `git diff`
- `preview.sh MODULE FUNC...` — render diagrams to `.preview/xv6-preview.png` (git-ignored) to check them by eye

For a new tag (e.g. step-11): write `pages/step-11.md`, add `figs/step11.py`, add `"step-11": "step-10"` to `PREV` in
`figs/maps.py`, add the sidebar entry in `_layouts/default.html`, add a row to `pages/index.md`, run `python3 build.py`.
