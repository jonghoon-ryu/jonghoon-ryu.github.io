#!/usr/bin/env python3
"""fiosweep.py FIO TESTFILE OUTDIR : one-parameter-at-a-time fio sweep against a fixed baseline.

Every run = BASE with exactly one option changed (write-only options use WBASE = BASE with rw=randwrite).
Each run's JSON goes to OUTDIR/<group>__<value>.json; results.csv collects one row per run.
"""
import csv, json, os, subprocess, sys, time

FIO, FILE, OUT = sys.argv[1:4]
os.makedirs(OUT, exist_ok=True)

BASE = dict(rw="randread", bs="4k", iodepth="32", numjobs="1", ioengine="io_uring", direct="1",
            size="4G", runtime="10", ramp_time="2", time_based="1", group_reporting="1")
WBASE = dict(BASE, rw="randwrite")

SWEEPS = [  # (group, option, values, base)
    ("baseline", None, ["run1", "run2", "run3"], BASE),
    ("rw", "rw", ["randread", "read", "randwrite", "write", "randrw", "rw"], BASE),
    ("bs", "bs", ["512", "4k", "16k", "64k", "128k", "1m"], BASE),
    ("iodepth", "iodepth", ["1", "2", "4", "8", "16", "32", "64", "128", "256"], BASE),
    ("numjobs", "numjobs", ["1", "2", "4", "8", "16"], BASE),
    ("ioengine", "ioengine", ["io_uring", "psync", "sync", "pvsync2", "posixaio", "mmap"], BASE),
    ("direct", "direct", ["1", "0"], BASE),
    ("size", "size", ["16M", "256M", "1G", "4G"], BASE),
    ("random_distribution", "random_distribution", ["random", "zipf:1.2", "pareto:0.9"], BASE),
    ("thread", "thread", ["0", "1"], BASE),
    ("io_uring_opt", None, ["none", "fixedbufs", "registerfiles", "sqthread_poll", "hipri"], BASE),
    ("fsync", "fsync", ["0", "1", "32"], WBASE),
    ("wbs", "bs", ["4k", "64k", "1m"], WBASE),
    ("wdirect", "direct", ["1", "0"], WBASE),
]


def args_of(opts):
    a = []
    for k, v in opts.items():
        if k in ("time_based", "group_reporting") and v == "1":
            a.append(f"--{k}")
        elif k == "thread":
            if v == "1":
                a.append("--thread")
        else:
            a.append(f"--{k}={v}")
    return a


def summarize(js):
    j = js["jobs"][0]
    row = {}
    for d in ("read", "write"):
        s = j[d]
        clat = s.get("clat_ns", {}); lat = s.get("lat_ns", {}); slat = s.get("slat_ns", {})
        p = clat.get("percentile", {})
        row[d + "_iops"] = s.get("iops", 0)
        row[d + "_mbps"] = s.get("bw_bytes", 0) / 1e6
        row[d + "_lat_us"] = lat.get("mean", 0) / 1e3
        row[d + "_slat_us"] = slat.get("mean", 0) / 1e3
        row[d + "_p50_us"] = p.get("50.000000", 0) / 1e3
        row[d + "_p99_us"] = p.get("99.000000", 0) / 1e3
        row[d + "_p999_us"] = p.get("99.900000", 0) / 1e3
        row[d + "_max_us"] = clat.get("max", 0) / 1e3
    row["usr"] = j.get("usr_cpu", 0)
    row["sys"] = j.get("sys_cpu", 0)
    depths = j.get("iodepth_level", {})
    row["depth_top"] = max(depths, key=lambda k: depths[k]) if depths else ""
    return row


rows = []
for group, opt, values, base in SWEEPS:
    for v in values:
        opts = dict(base)
        if group == "io_uring_opt":
            if v != "none":
                opts[v] = "1"
        elif opt:
            opts[opt] = v
        name = f"{group}__{v.replace(':', '_')}"
        cmd = [FIO, f"--name={name}", f"--filename={FILE}", "--output-format=json",
               f"--output={OUT}/{name}.json"] + args_of(opts)
        t0 = time.time()
        r = subprocess.run(cmd, capture_output=True, text=True)
        row = {"group": group, "value": v, "seconds": round(time.time() - t0, 1), "error": ""}
        try:
            text = open(f"{OUT}/{name}.json").read()
            row.update(summarize(json.loads(text[text.index("{"):])))
        except Exception as e:  # noqa: BLE001  (record the failure, keep sweeping)
            row["error"] = (r.stderr.strip().splitlines() or [str(e)])[-1][:200]
        rows.append(row)
        print(f"{group:20} {v:14} read {row.get('read_iops', 0):10.0f} IOPS  write {row.get('write_iops', 0):10.0f} IOPS"
              f"  {row['error']}", flush=True)
        time.sleep(3)

keys = sorted({k for r in rows for k in r}, key=lambda k: (k not in ("group", "value", "error", "seconds"), k))
with open(f"{OUT}/results.csv", "w", newline="") as f:
    w = csv.DictWriter(f, fieldnames=keys)
    w.writeheader()
    w.writerows(rows)
print("->", f"{OUT}/results.csv")
