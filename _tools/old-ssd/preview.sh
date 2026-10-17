#!/bin/bash
# preview.sh FUNC... : render figs.FUNC() to .preview/p.png (git-ignored) to check them by eye
cd "$(dirname "$0")"; mkdir -p .preview
python3 -c "
import sys, figs
print('<html><head><meta charset=utf-8><link rel=stylesheet href=\"https://fonts.googleapis.com/css2?family=IBM+Plex+Sans+KR:wght@400;700&family=IBM+Plex+Mono&display=swap\"></head><body style=\"margin:0;width:800px;background:#fff\">' + ''.join(getattr(figs,f)() for f in sys.argv[1:]) + '</body></html>')" "$@" > .preview/p.html || exit 1
H=$(( $# * 520 + 200 ))
google-chrome --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 --window-size=800,$H --screenshot=.preview/p.png file://$PWD/.preview/p.html 2>/dev/null
echo .preview/p.png
