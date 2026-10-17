#!/usr/bin/env python3
"""fileage.py ROOT OUT.csv [--min-mib 16] [--per-year 25] [--per-file-mib 16] [--seed 1]

Read speed of old files versus how long ago they were written. Read-only.

For every file of at least --min-mib under ROOT, "written" = the later of the NTFS creation time
(xattr system.ntfs_crtime, given by the ntfs-3g driver) and the modification time: the last time its
data was put on this drive. Up to --per-year files are picked from each year (random, fixed seed),
the page cache for each file is dropped with posix_fadvise(DONTNEED) so the read really goes to the
drive, the first --per-file-mib of the file are read in 1 MiB requests, and one CSV row is written:

  written      date the data was last written (YYYY-MM-DD)
  age_days     days between then and now
  mib          MiB read
  mbps         read speed (MB/s)
  max_ms       slowest 1 MiB read
  path         file path (relative to ROOT)

Files whose allocated size is clearly below their length (sparse, or NTFS/WOF-compressed) are skipped:
holes read as zeros without touching NAND, and compressed reads measure the CPU. Files that fail to
read are not put in the CSV (a 0 MB/s row would look like a very old file); they go to OUT-errors.csv.

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
    a = ap.parse_args()

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
            if not os.path.isfile(p) or os.path.islink(p) or st.st_size < a.min_mib * MIB:
                continue
            if st.st_blocks * 512 < 0.9 * st.st_size:   # sparse or compressed
                skipped += 1
                continue
            files.append((written_time(p, st), p, st.st_size))
    print(f"{len(files)} files >= {a.min_mib} MiB ({skipped} sparse/compressed skipped)", file=sys.stderr)
    by_year = collections.defaultdict(list)
    for f in files:
        by_year[f[0].year].append(f)
    rng = random.Random(a.seed)
    pick = []
    for y in sorted(by_year):
        g = by_year[y]
        rng.shuffle(g)
        pick += g[:a.per_year]
        print(f"{y}: {len(g)} files >= {a.min_mib} MiB, using {min(len(g), a.per_year)}", file=sys.stderr)
    rng.shuffle(pick)                      # mixed order: the drive's state does not drift with age

    now = datetime.datetime.now()
    buf = bytearray(MIB)
    errpath = os.path.splitext(a.out)[0] + "-errors.csv"
    nerr = 0
    with open(a.out, "w") as out, open(errpath, "w") as errs:
        out.write("written,age_days,mib,mbps,max_ms,path\n")
        errs.write("written,mib_read,error,path\n")
        for i, (wt, p, size) in enumerate(pick):
            try:
                fd = os.open(p, os.O_RDONLY)
            except OSError as e:
                print(f"\nskip {p}: {e}", file=sys.stderr)
                errs.write(f'{wt:%Y-%m-%d},0,{e.strerror},"{os.path.relpath(p, a.root)}"\n')
                nerr += 1
                continue
            os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
            want = min(size, a.per_file_mib * MIB)
            got = 0
            worst = 0.0
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
                print(f"\nread error {p}: {e}", file=sys.stderr)
            secs = time.monotonic() - t0
            os.posix_fadvise(fd, 0, 0, os.POSIX_FADV_DONTNEED)
            os.close(fd)
            mbps = got / secs / 1e6 if secs > 0 else 0
            rel = os.path.relpath(p, a.root).replace('"', "'")
            if err is not None:            # EIO here = an uncorrectable read: a result in itself
                errs.write(f'{wt:%Y-%m-%d},{got / MIB:.1f},{err.strerror},"{rel}"\n')
                errs.flush()
                nerr += 1
                continue
            out.write(f'{wt:%Y-%m-%d},{(now - wt).days},{got / MIB:.0f},{mbps:.1f},{worst * 1e3:.1f},"{rel}"\n')
            out.flush()
            print(f"\r{i + 1}/{len(pick)}  {wt:%Y-%m-%d}  {mbps:7.1f} MB/s  ", end="", file=sys.stderr, flush=True)
    print(f"\n-> {a.out}" + (f"   ({nerr} files failed -> {errpath})" if nerr else ""), file=sys.stderr)


if __name__ == "__main__":
    main()
