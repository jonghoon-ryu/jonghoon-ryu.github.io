#!/usr/bin/env python3
"""sweepplot.py results.csv OUTDIR : one PNG per swept parameter (throughput | latency, two panels)."""
import csv, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker

BLUE, ORANGE, AQUA = "#2a78d6", "#eb6834", "#1baf7a"     # reference categorical slots 1-3
INK, INK2, GRID, SURF = "#0b0b0b", "#52514e", "#e6e5e0", "#fcfcfb"

rows = list(csv.DictReader(open(sys.argv[1])))
OUT = sys.argv[2]
os.makedirs(OUT, exist_ok=True)
NUMERIC = {"bs", "iodepth", "numjobs", "size", "wbs"}
TITLES = {
    "rw": "--rw (I/O pattern)", "bs": "--bs (block size, randread)", "iodepth": "--iodepth (requests in flight)",
    "numjobs": "--numjobs (copies of the job, each at iodepth 32)", "ioengine": "--ioengine",
    "direct": "--direct (0 = through the page cache)", "size": "--size (region the reads cover)",
    "random_distribution": "--random_distribution", "thread": "--thread (threads instead of processes)",
    "io_uring_opt": "io_uring options", "fsync": "--fsync (randwrite: FLUSH every N writes)",
    "wbs": "--bs (randwrite)", "wdirect": "--direct (randwrite)", "baseline": "baseline repeated 3 times",
}


def f(r, k):
    try:
        return float(r.get(k) or 0)
    except ValueError:
        return 0.0


def style(ax, ylabel):
    ax.set_facecolor(SURF)
    ax.grid(axis="y", color=GRID, lw=0.8)
    ax.set_axisbelow(True)
    for s in ("top", "right"):
        ax.spines[s].set_visible(False)
    for s in ("left", "bottom"):
        ax.spines[s].set_color(GRID)
    ax.tick_params(colors=INK2, labelsize=9)
    ax.set_ylabel(ylabel, color=INK2, fontsize=9)


def fmt(v):
    return f"{v/1e3:.0f}k" if v >= 1e4 else (f"{v/1e3:.1f}k" if v >= 1e3 else f"{v:.0f}")


groups = []
for r in rows:
    if r["group"] not in groups:
        groups.append(r["group"])

for g in groups:
    rs = [r for r in rows if r["group"] == g and not r.get("error")]
    bad = [r for r in rows if r["group"] == g and r.get("error")]
    if not rs:
        continue
    labels = [r["value"] for r in rs]
    x = list(range(len(rs)))
    rd = [f(r, "read_iops") for r in rs]
    wr = [f(r, "write_iops") for r in rs]
    big_bs = g in ("bs", "wbs")
    fig, (a1, a2) = plt.subplots(1, 2, figsize=(10, 3.6), dpi=110, facecolor=SURF)
    # left : throughput
    if big_bs:
        mb = [f(r, "read_mbps") + f(r, "write_mbps") for r in rs]
        a1.plot(x, mb, color=BLUE, lw=2, marker="o", ms=6)
        for xi, v in zip(x, mb):
            a1.annotate(f"{v:,.0f}", (xi, v), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8, color=INK)
        style(a1, "MB/s")
    elif g in NUMERIC:
        tot = [a + b for a, b in zip(rd, wr)]
        a1.plot(x, tot, color=BLUE, lw=2, marker="o", ms=6)
        for xi, v in zip(x, tot):
            a1.annotate(fmt(v), (xi, v), textcoords="offset points", xytext=(0, 6), ha="center", fontsize=8, color=INK)
        style(a1, "IOPS")
    else:
        a1.bar(x, rd, width=0.55, color=BLUE, label="read", edgecolor=SURF, lw=2)
        if any(wr):
            a1.bar(x, wr, width=0.55, bottom=rd, color=ORANGE, label="write", edgecolor=SURF, lw=2)
            a1.legend(frameon=False, fontsize=8, labelcolor=INK2)
        for xi, a, b in zip(x, rd, wr):
            a1.annotate(fmt(a + b), (xi, a + b), textcoords="offset points", xytext=(0, 4), ha="center", fontsize=8, color=INK)
        style(a1, "IOPS")
    a1.set_xticks(x, labels, rotation=0 if len(labels) < 7 else 30, fontsize=8)
    a1.set_ylim(bottom=0)
    if not big_bs:
        a1.yaxis.set_major_formatter(matplotlib.ticker.FuncFormatter(lambda v, _: fmt(v)))
    a1.set_title("throughput", fontsize=10, color=INK, loc="left")
    # right : latency (the side that did the I/O; reads first)
    side = ["read" if f(r, "read_iops") >= f(r, "write_iops") else "write" for r in rs]
    mean = [f(r, s + "_lat_us") for r, s in zip(rs, side)]
    p99 = [f(r, s + "_p99_us") for r, s in zip(rs, side)]
    ls = "-" if g in NUMERIC else "none"          # categories: dots only, no line implying an order
    a2.plot(x, mean, color=BLUE, lw=2, ls=ls, marker="o", ms=7, label="mean (lat)")
    a2.plot(x, p99, color=ORANGE, lw=2, ls=ls, marker="s", ms=7, label="99% (clat)")
    a2.set_yscale("log")
    style(a2, "latency (µs, log scale)")
    a2.set_xticks(x, labels, rotation=0 if len(labels) < 7 else 30, fontsize=8)
    a2.legend(frameon=False, fontsize=8, labelcolor=INK2)
    a2.set_title("latency per I/O", fontsize=10, color=INK, loc="left")
    fig.suptitle(TITLES.get(g, g) + (f"   (failed: {', '.join(r['value'] for r in bad)})" if bad else ""),
                 fontsize=11, color=INK, x=0.01, ha="left")
    fig.tight_layout()
    fig.savefig(f"{OUT}/{g}.png", facecolor=SURF)
    plt.close(fig)
    print(f"{OUT}/{g}.png")
