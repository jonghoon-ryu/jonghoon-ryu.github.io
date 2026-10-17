#!/usr/bin/env python3
"""fiosum.py OUT.csv RUN.json...

One CSV row per fio job from fio's JSON reports (--output-format=json), and the same table on stdout.

  run          the JSON file name without .json
  job          fio job name (several jobs in one run: one row each)
  rw bs qd     what the job did: rw pattern, block size, iodepth
  dir          read or write (the side of the job that moved data)
  iops mbps    average IOPS and MB/s
  lat_mean_us  mean completion latency (clat), microseconds
  p50_us p99_us p999_us max_us   clat percentiles and the slowest single I/O
"""
import csv, json, os, sys


def load(path):
    text = open(path).read()
    return json.loads(text[text.index("{"):])      # fio may print warnings before the JSON


def main():
    if len(sys.argv) < 3:
        sys.exit(__doc__)
    out, paths = sys.argv[1], sys.argv[2:]
    cols = ["run", "job", "rw", "bs", "qd", "dir", "iops", "mbps", "lat_mean_us", "p50_us", "p99_us", "p999_us", "max_us"]
    rows = []
    for path in paths:
        try:
            rep = load(path)
        except (ValueError, OSError) as e:
            print(f"fiosum: skip {path}: {e}", file=sys.stderr)
            continue
        run = os.path.basename(path)[:-5]
        g = rep.get("global options", {})
        for job in rep.get("jobs", []):
            o = {**g, **job.get("job options", {})}
            for d in ("read", "write"):
                s = job.get(d, {})
                if not s.get("io_bytes"):
                    continue
                clat = s.get("clat_ns", {})
                pct = clat.get("percentile", {})
                us = lambda k: f'{pct.get(k, 0) / 1000:.0f}'
                rows.append([run, job["jobname"], o.get("rw", ""), o.get("bs", ""), o.get("iodepth", "1"), d,
                             f'{s["iops"]:.0f}', f'{s["bw_bytes"] / 1e6:.1f}', f'{clat.get("mean", 0) / 1000:.0f}',
                             us("50.000000"), us("99.000000"), us("99.900000"), f'{clat.get("max", 0) / 1000:.0f}'])
    with open(out, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)
    w = csv.writer(sys.stdout)
    w.writerow(cols)
    w.writerows(rows)


if __name__ == "__main__":
    main()
