#!/usr/bin/env python3
"""plot.py OUT.png INPUT[=LABEL]...

Draws one figure from experiment results. The kind of plot follows from the inputs:
  scan.csv        read speed across the drive (x = position in GiB)
  fileage.csv     read speed of each file vs when it was written
  NAME_bw.log     write/read speed over the run (x = GB transferred so far), e.g. slc_bw.log
  NAME_iops.log   IOPS over the run (x = GB transferred so far), e.g. cliff_iops.log
  NAME_lat.log    latency distribution (histogram), e.g. rd-mapped_lat.log
Several inputs of the same kind are drawn on top of each other; "=LABEL" names a curve.
fio logs have one line per second: time_ms, value, direction, block_size, offset.
"""
import csv, os, sys

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

COLORS = ["#1f6f5c", "#c0392b", "#2874a6", "#b7950b", "#7d3c98", "#566573"]


def fio_log(path):
    t, v, bs = [], [], []
    with open(path) as f:
        for line in f:
            p = [x.strip() for x in line.split(",")]
            if len(p) >= 2:
                t.append(int(p[0]) / 1000)
                v.append(float(p[1]))
                bs.append(int(p[3]) if len(p) > 3 and p[3].isdigit() and int(p[3]) > 0 else 0)
    return t, v, bs


def bw_gb_axis(path):
    """x axis 'GB so far' from the bw log next to an iops/lat log (bw log values are KiB/s)."""
    base = path.rsplit("_", 1)[0]
    t, v, _ = fio_log(base + "_bw.log")
    x, s, last = [], 0.0, 0.0
    for ti, vi in zip(t, v):
        s += vi * 1024 * (ti - last) / 1e9
        last = ti
        x.append(s)
    return x


def smooth(v, n):
    if n <= 1:
        return v
    out, acc = [], 0.0
    for i, x in enumerate(v):
        acc += x
        if i >= n:
            acc -= v[i - n]
        out.append(acc / min(i + 1, n))
    return out


def main():
    if len(sys.argv) < 3:
        print(__doc__)
        sys.exit(1)
    out, inputs = sys.argv[1], sys.argv[2:]
    fig, ax = plt.subplots(figsize=(10, 5), dpi=110)
    kind = None
    for i, arg in enumerate(inputs):
        path, _, label = arg.partition("=")
        label = label or os.path.basename(os.path.dirname(os.path.abspath(path))) or path
        c = COLORS[i % len(COLORS)]
        name = os.path.basename(path)
        if name.endswith("scan.csv") or name.startswith("scan"):
            kind = "scan"
            rows = list(csv.DictReader(open(path)))
            x = [float(r["offset_gib"]) for r in rows]
            y = [float(r["mbps"]) for r in rows]
            ax.plot(x, y, color=c, lw=1.4, label=label)
            z = [float(r["zero_frac"]) > 0.99 for r in rows]
            ax.scatter([a for a, b in zip(x, z) if b], [a for a, b in zip(y, z) if b], s=6, color=c, alpha=.5)
            ax.set_xlabel("position on the drive (GiB)")
            ax.set_ylabel("read speed (MB/s)")
            ax.set_title("Read speed across the drive (dots: chunks that read back as all zeros)")
        elif name.startswith("fileage"):
            kind = "age"
            rows = list(csv.DictReader(open(path)))
            import datetime as dt
            x = [dt.date.fromisoformat(r["written"]) for r in rows]
            y = [float(r["mbps"]) for r in rows]
            ax.scatter(x, y, s=10, color=c, alpha=.6, label=label)
            years = sorted({d.year for d in x})
            for yr in years:
                ys = sorted(v for d, v in zip(x, y) if d.year == yr)
                if ys:
                    ax.plot([dt.date(yr, 1, 1), dt.date(yr, 12, 31)], [ys[len(ys) // 2]] * 2, color="#c0392b", lw=2)
            ax.set_xlabel("data last written")
            ax.set_ylabel("read speed (MB/s)")
            ax.set_title("Read speed of each file vs when it was written (red: median per year)")
        elif name.endswith("_bw.log"):
            kind = "bw"
            t, v, _ = fio_log(path)
            x = bw_gb_axis(path)
            ax.plot(x, [a * 1024 / 1e6 for a in v], color=c, lw=0.8, alpha=.35)
            ax.plot(x, smooth([a * 1024 / 1e6 for a in v], 10), color=c, lw=1.8, label=label)
            ax.set_xlabel("data transferred so far (GB)")
            ax.set_ylabel("MB/s (thin: every second, thick: 10 s average)")
        elif name.endswith("_iops.log"):
            kind = "iops"
            t, v, _ = fio_log(path)
            x = bw_gb_axis(path)
            ax.plot(x, v, color=c, lw=0.6, alpha=.3)
            ax.plot(x, smooth(v, 30), color=c, lw=1.8, label=label)
            ax.set_xlabel("data written so far (GB)")
            ax.set_ylabel("IOPS (thin: every second, thick: 30 s average)")
        elif name.endswith("_lat.log"):
            kind = "lat"
            _, v, _ = fio_log(path)
            us = [a / 1000 for a in v]         # fio lat logs are in ns
            ax.hist(us, bins=60, color=c, alpha=.55, label=label)
            ax.set_xlabel("mean latency per second (µs)")
            ax.set_ylabel("seconds")
        else:
            sys.exit(f"plot.py: do not know how to plot {path}")
    ax.grid(alpha=.3)
    ax.set_ylim(bottom=0) if kind != "lat" else None
    ax.legend()
    fig.tight_layout()
    fig.savefig(out)
    print(f"-> {out}")


if __name__ == "__main__":
    main()
