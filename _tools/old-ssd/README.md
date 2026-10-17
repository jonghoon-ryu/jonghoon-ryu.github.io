# old-SSD experiment pages (not published: Jekyll skips folders starting with "_")

Pages under /old-ssd-experiments/ are Korean (the rest of the blog's rule; only /xv6/tutorial/ is English).

- `pages/<slug>.md` — page sources. Macros: `@@FIG name@@` (figs.name()), `@@STYLE@@` (pages/_style.txt), `@@NAV@@` (prev/next),
  and ```` ```table ```` blocks (first line = header, cells split by " | ") which become `<table class="t">` (plain markdown tables overflow on this theme)
- `figs.py` — all diagrams (inline SVG). `svg.py` = the xv6 helper + `Chart` (axes, curves, bands) and rotated text
- `build.py [SLUG...]` — writes `old-ssd-experiments/<slug>/index.md` (index → `old-ssd-experiments/index.md`). `PAGES` sets order + sidebar titles
- `preview.sh FUNC...` — render figures to `.preview/p.png` to check them by eye (OVERFLOW / OFFCANVAS warnings on stderr)

New page: add `pages/<slug>.md`, add it to `PAGES` in build.py, add the `<li>` in `_layouts/default.html` (the "헌 SSD 로 하는 실험" group), run `python3 build.py`.
Results: when Ryu runs an experiment, results land in ~/Ryu/old_ssd_results/<date>-<name>/; analysis goes into the page's "결과" section
(edit `pages/<slug>.md`, then rebuild). Scripts that run the experiments: `old-ssd-experiments/scripts/` (published, so Ryu can read them).
