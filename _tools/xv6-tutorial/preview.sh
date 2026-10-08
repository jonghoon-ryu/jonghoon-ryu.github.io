#!/bin/bash
# preview.sh MODULE FUNC... : render diagrams to .preview/xv6-preview.png
cd "$(dirname "$0")"; mkdir -p .preview
M=$1; shift
python3 -c "
import sys, importlib; m=importlib.import_module('figs.'+sys.argv[1])
print('<html><head><link rel=stylesheet href=https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/variable/pretendardvariable-dynamic-subset.min.css><link rel=stylesheet href=\"https://fonts.googleapis.com/css2?family=JetBrains+Mono&display=swap\"></head><body style=\"margin:0;width:1000px;background:#fff\">' + ''.join(getattr(m,f)() for f in sys.argv[2:]) + '</body></html>')" "$M" "$@" > .preview/xv6-preview.html
H=$(( $# * 560 + 2000 ))
google-chrome --headless=new --disable-gpu --hide-scrollbars --virtual-time-budget=6000 --window-size=1000,$H --screenshot=.preview/xv6-preview.png file://$PWD/.preview/xv6-preview.html 2>/dev/null
