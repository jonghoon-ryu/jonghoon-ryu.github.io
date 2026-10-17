#!/usr/bin/env python3
"""fileage.py ROOT OUT.csv [--since 2026-10-17] [--min-mib 16] [--per-year 25] [--per-file-mib 16] [--reread 10] [--seed 1]

Read speed of old files versus how long ago they were written. Read-only.

This drive sat unpowered for more than a year and was reconnected on --since (2026-10-17), when a few
files were read and written. So every file falls in one of three groups:

  new     written on/after --since: fresh data, the control group (files >= 1 MiB, all of them, up to --per-year)
  read    written before, but accessed (atime) on/after --since: read once since reconnecting, so the
          firmware may already have rewritten them (read reclaim); up to --per-year of them
  old     untouched since the drive was last powered: the real measurement, --per-year per year

atime only proves a read when the mount kept access times (relatime, the default); a file that was read
under noatime still lands in "old". The last write before --since (printed) is a proxy for when the drive
was last powered: from then until --since it sat unpowered.

For every file of at least --min-mib under ROOT, "written" = the later of the NTFS creation time
(xattr system.ntfs_crtime, given by the ntfs-3g driver) and the modification time: the last time its
data was put on this drive. Up to --per-year files are picked from each year (random, fixed seed),
the page cache for each file is dropped with posix_fadvise(DONTNEED) so the read really goes to the
drive, the first --per-file-mib of the file are read in 1 MiB requests, and one CSV row is written:

  written      date the data was last written (YYYY-MM-DD)
  age_days     days between then and now
  group        new / read / old (above)
  accessed     last access time (YYYY-MM-DD) as the file system recorded it
  mib          MiB read
  mbps         read speed (MB/s)
  max_ms       slowest 1 MiB read
  path         file path (relative to ROOT)

Files whose allocated size is clearly below their length (sparse, or NTFS/WOF-compressed) are skipped:
holes read as zeros without touching NAND, and compressed reads measure the CPU. Files that fail to
read are not put in the CSV (a 0 MB/s row would look like a very old file); they go to OUT-errors.csv.

Afterwards the --reread slowest "old" files are read a second time (same 16 MiB, cache dropped again):
OUT-reread.csv has both speeds. Much faster the second time = the firmware rewrote the data right after
the slow read; the same = it did not (or not yet: it may do it later in the background).

Mount the volume read-only first (see the setup page), so not even access times are written.
"""
import argparse, collections, datetime, os, random, struct, sys, time

MIB = 1 << 20
NTFS_EPOCH = datetime.datetime(1601, 1, 1)


def written_time(path, st):
    t = datetime.datetime.fromtimestamp(st.st_mtime)
    try:
        v = os.getxattr(path, "system.ntfs_crtime", follow_symlinks=False)
        ct = NTFS_EPOCH + datetime.timedelta(microseconds=struct.unpack("<Q", v[:8])[0] / 10)
        ct = ct.replace(tzinfo=datetime.timezone.utc).astimezone().replace(tzinfo=None)
        t = max(t, ct)
    except OSError:
        pass
    return t


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("root")
    ap.add_argument("out")
    ap.add_argument("--min-mib", type=int, default=16)
    ap.add_argument("--per-year", type=int, default=25)
    ap.add_argument("--per-file-mib", type=int, default=16)
    ap.add_argument("--seed", type=int, default=1)
    ap.add_argument("--since", default="2026-10-17", help="date the drive was reconnected (YYYY-MM-DD)")
    ap.add_argument("--reread", type=int, default=10)
    a = ap.parse_args()
    since = datetime.datetime.fromisoformat(a.since)

    files = []
    skipped = 0
    print(f"listing files under {a.root} (reads only metadata; can take minutes on a slow drive)", file=sys.stderr)
    for d, dirs, names in os.walk(a.root):
        for n in names:
            p = os.path.join(d, n)
            try:
                st = os.lstat(p)
            except OSError:
                continue
            if not os.path.isfile(p) or os.path.islink(p) or st.st_size < MIB:
                continue
            if st.st_blocks * 512 < 0.9 * st.st_size:   # sparse or compressed
                skipped += 1
                continue
            wt = written_time(p, st)
            at = datetime.datetime.fromtimestamp(st.st_atime)
            group = "new" if wt >= since else "read" if at >= since else "old"
            if group != "new" and st.st_size < a.min_mib * MIB:
                continue
            files.append((wt, p, st.st_size, group, at))
    print(f"{len(files)} files ({skipped} sparse/compressed skipped)", file=sys.stderr)
    before = [f[0] for f in files if f[3] != "new"]
    if before:
        last = max(before)
        print(f"last write before {a.since}: {last:%Y-%m-%d} -> unpowered for about {(since - last).days} days "
              f"(if the drive was not used without writing anything)", file=sys.stderr)
    rng = random.Random(a.seed)
    pick = []
    for grp in ("new", "read"):
        g = [f for f in files if f[3] == grp]
        rng.shuffle(g)
        pick += g[:a.per_year]
        print(f"{grp}: {len(g)} files, using {min(len(g), a.per_year)}", file=sys.stderr)
    by_year = collections.defaultdict(list)
    for f in files:
        if f[3] == "old":
            by_year[f[0].year].append(f)
    for y in sorted(by_year):
        g = by_year[y]
        rng.shuffle(g)
        pick += g[:a.per_year]
        print(f"old {y}: {len(g)} files >= {a.min_mib} MiB, using {min(len(g), a.per_year)}", file=sys.stderr)
    rng.shuffle(pick)                      # mixed order: the drive's state does not drift with age

    now = datetime.datetime.now()
    buf = bytearray(MIB)
    base = os.path.splitext(a.out)[0]
    errpath = base + "-errors.csv"
    nerr = 0
    rows = []
    with open(a.out, "w") as out, open(errpath, "w") as errs:
        out.write("written,age_days,group,accessed,mib,mbps,max_ms,path\n")
        errs.write("written,group,mib_read,error,path\n")
        for i, (wt, p, size, grp, at) in enumerate(pick):
            rel = os.path.relpath(p, a.root).replace('"', "'")
            got, mbps, worst, err = read_head(p, size, a.per_file_mib, buf)
            if err is not None:            # EIO here = an uncorrectable read: a result in itself
                print(f"\nread error {p}: {err}", file=sys.stderr)
                errs.write(f'{wt:%Y-%m-%d},{grp},{got / MIB:.1f},{err.strerror},"{rel}"\n')
                errs.flush()
                nerr += 1
                continue
            out.write(f'{wt:%Y-%m-%d},{(now - wt).days},{grp},{at:%Y-%m-%d},{got / MIB:.0f},{mbps:.1f},{worst * 1e3:.1f},"{rel}"\n')
            out.flush()
            rows.append((mbps, worst, wt, p, size, grp, rel))
            print(f"\r{i + 1}/{len(pick)}  {grp:4} {wt:%Y-%m-%d}  {mbps:7.1f} MB/s  ", end="", file=sys.stderr, flush=True)
    print(f"\n-> {a.out}" + (f"   ({nerr} files failed -> {errpath})" if nerr else ""), file=sys.stderr)

    slow = sorted(r for r in rows if r[5] == "old")[:a.reread]
    if slow:
        with open(base + "-reread.csv", "w") as out:
            out.write("written,mbps1,mbps2,max_ms1,max_ms2,path\n")
            for mbps, worst, wt, p, size, grp, rel in slow:
                _, mbps2, worst2, err = read_head(p, size, a.per_file_mib, buf)
                if err is None:
                    out.write(f'{wt:%Y-%m-%d},{mbps:.1f},{mbps2:.1f},{worst * 1e3:.1f},{worst2 * 1e3:.1f},"{rel}"\n')
                    print(f"reread {wt:%Y-%m-%d}  {mbps:7.1f} -> {mbps2:7.1f} MB/s", file=sys.stderr)
        print(f"-> {base}-reread.csv", file=sys.stderr)


def read_head(p, size, per_file_mib, buf):
    """Read the first per_file_mib of p with the page cache dropped: (bytes, MB/s, slowest 1 MiB in s, error)."""
    got, worst = 0, 0.0
    try:
        fd = os.open(p, os.O_RDONLY)
    except OSError as e:
        return 0, 0.0, 0.0, e
    os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
    want = min(size, per_file_mib * MIB)
    err = None
    t0 = time.monotonic()
    try:
        while got < want:
            t1 = time.monotonic()
            n = os.readv(fd, [buf])
            worst = max(worst, time.monotonic() - t1)
            if n <= 0:
                break
            got += n
    except OSError as e:
        err = e
    secs = time.monotonic() - t0
    os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
    os.close(fd)
    return got, (got / secs / 1e6 if secs > 0 else 0.0), worst, err


if __name__ == "__main__":
    main()
