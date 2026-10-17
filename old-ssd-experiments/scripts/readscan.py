#!/usr/bin/env python3
"""readscan.py DEV OUT.csv [--chunk-mib N] [--sample-mib N]

Read-only scan of a whole block device (or a file) with O_DIRECT, so the page cache never hides the drive.
The device is cut into chunks (default 256 MiB); for each chunk the script reads it in 1 MiB requests and
writes one CSV row:

  offset_gib   where the chunk starts
  mib          how much of it was read (all of it, or --sample-mib)
  mbps         read speed of the chunk (MB/s, 1 MB = 10^6 bytes)
  mean_ms      mean time of one 1 MiB read
  max_ms       slowest 1 MiB read in the chunk (read retries show up here first)
  zero_frac    fraction of the 1 MiB reads that returned only zero bytes (unwritten or trimmed LBAs)

It never opens the device for writing.
"""
import argparse, mmap, os, sys, time

MIB = 1 << 20


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dev")
    ap.add_argument("out")
    ap.add_argument("--chunk-mib", type=int, default=256)
    ap.add_argument("--sample-mib", type=int, default=0, help="read only the first N MiB of each chunk (0 = all)")
    a = ap.parse_args()

    fd = os.open(a.dev, os.O_RDONLY | os.O_DIRECT)
    size = os.lseek(fd, 0, os.SEEK_END)
    buf = mmap.mmap(-1, MIB)              # page-aligned, as O_DIRECT needs
    zero = bytes(MIB)
    chunk = a.chunk_mib * MIB
    per = min(a.sample_mib * MIB, chunk) if a.sample_mib else chunk
    nchunks = (size + chunk - 1) // chunk
    t_start = time.monotonic()
    total = 0
    with open(a.out, "w") as out:
        out.write("offset_gib,mib,mbps,mean_ms,max_ms,zero_frac\n")
        for i in range(nchunks):
            base = i * chunk
            end = min(base + per, size)
            n = zeros = 0
            worst = 0.0
            t0 = time.monotonic()
            off = base
            while off < end:
                want = min(MIB, end - off)
                if want < MIB:                # tail of the device: O_DIRECT needs whole sectors
                    want = (want // 512) * 512
                    if want == 0:
                        break
                t1 = time.monotonic()
                got = os.preadv(fd, [memoryview(buf)[:want]], off)
                dt = time.monotonic() - t1
                if got <= 0:
                    break
                worst = max(worst, dt)
                if buf[:got] == zero[:got]:
                    zeros += 1
                n += 1
                off += got
            secs = time.monotonic() - t0
            done = off - base
            total += done
            mbps = done / secs / 1e6 if secs > 0 else 0.0
            out.write(f"{base / (1 << 30):.3f},{done / MIB:.0f},{mbps:.1f},"
                      f"{secs / max(n, 1) * 1e3:.2f},{worst * 1e3:.2f},{zeros / max(n, 1):.3f}\n")
            out.flush()
            el = time.monotonic() - t_start
            eta = el / (i + 1) * (nchunks - i - 1)
            print(f"\r{i + 1}/{nchunks}  {base / (1 << 30):6.1f} GiB  {mbps:7.1f} MB/s  "
                  f"max {worst * 1e3:7.1f} ms  zero {zeros / max(n, 1):4.2f}  ETA {eta / 60:5.1f} min ",
                  end="", file=sys.stderr, flush=True)
    os.close(fd)
    el = time.monotonic() - t_start
    print(f"\nread {total / 1e9:.1f} GB in {el / 60:.1f} min, mean {total / el / 1e6:.1f} MB/s -> {a.out}",
          file=sys.stderr)


if __name__ == "__main__":
    main()
