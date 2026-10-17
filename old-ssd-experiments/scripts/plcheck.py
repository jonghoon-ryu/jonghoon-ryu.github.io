#!/usr/bin/env python3
"""plcheck.py write DEV ACKED.csv [--sync-mib 8] [--stop-gb N]
   plcheck.py check DEV ACKED.csv

Power-loss test (exp 17). Run "write", cut the drive's power while it runs, power it back, run "check".

write: fills DEV from the start with 4 KiB records, slot i holding record i:
         magic "PLREC001" | run id (8 B) | i (8 B) | crc32 of the rest | random bytes
       written with O_DIRECT, 1 MiB at a time. After every --sync-mib it calls fdatasync (the kernel sends a
       FLUSH CACHE to the drive) and, once that returns, appends "count,time" to ACKED.csv on the PC's own disk
       and fsyncs that file. So every record below the last count in ACKED.csv was acknowledged as durable.
       It stops at the end of the drive, after --stop-gb GB (then it waits, so the power can be cut while the
       drive is idle but still busy inside), or when the drive disappears (the power cut).

check: reads the slots back and sorts each into
         ok       this run's record i, checksum right
         zero     all zeros (never written, or trimmed)
         other    a record from an earlier run (different run id), or no record at all
         torn     this run's magic and id but a wrong checksum: a half-written record
       Slots below the acknowledged count must all be ok. Anything else there means the drive acknowledged
       a FLUSH and then lost the data. Above it, survivors show how much of the unflushed tail made it.
       Reading stops 1 GiB past the last ok slot.
"""
import argparse, mmap, os, struct, sys, time, zlib

REC = 4096
CHUNK = 256                       # records per write (1 MiB)
MAGIC = b"PLREC001"
HEAD = struct.Struct("<8s8sQ")    # magic, run id, index ; then crc32 (4 B), then payload


def make(buf, off, run_id, i, payload):
    h = HEAD.pack(MAGIC, run_id, i)
    body = h + payload
    buf[off:off + REC] = body[:HEAD.size] + struct.pack("<I", zlib.crc32(body)) + payload


def classify(rec, run_id, i):
    if rec.count(0) == REC:
        return "zero"
    magic, rid, idx = HEAD.unpack_from(rec)
    if magic != MAGIC or rid != run_id:
        return "other"
    crc, = struct.unpack_from("<I", rec, HEAD.size)
    payload = rec[HEAD.size + 4:]
    if idx != i or zlib.crc32(rec[:HEAD.size] + payload) != crc:
        return "torn"
    return "ok"


def open_dev(path, flags):
    try:
        return os.open(path, flags | os.O_DIRECT)
    except OSError:                       # files on tmpfs (self-test) do not take O_DIRECT
        return os.open(path, flags)


def size_of(fd):
    return os.lseek(fd, 0, os.SEEK_END)


def write(a):
    fd = open_dev(a.dev, os.O_WRONLY)
    total = size_of(fd) // REC
    if a.stop_gb:
        total = min(total, int(a.stop_gb * 1e9) // (CHUNK * REC) * CHUNK)
    run_id = os.urandom(8)
    buf = mmap.mmap(-1, CHUNK * REC)      # page aligned, as O_DIRECT wants
    sync_every = a.sync_mib * (1 << 20) // (CHUNK * REC)
    log = open(a.acked, "w")
    log.write(f"# run_id {run_id.hex()} records {total} rec_bytes {REC} sync_mib {a.sync_mib}\n")
    log.write("acked_records,time\n")
    log.flush(); os.fsync(log.fileno())
    i, n, t0 = 0, 0, time.monotonic()
    try:
        while i < total:
            k = min(CHUNK, total - i)
            payload = os.urandom(k * (REC - HEAD.size - 4))
            step = REC - HEAD.size - 4
            for j in range(k):
                make(buf, j * REC, run_id, i + j, payload[j * step:(j + 1) * step])
            os.pwrite(fd, memoryview(buf)[:k * REC], i * REC)
            i += k
            n += 1
            if n % sync_every == 0 or i == total:
                os.fdatasync(fd)
                log.write(f"{i},{time.time():.3f}\n")
                log.flush(); os.fsync(log.fileno())
                el = time.monotonic() - t0
                print(f"\racked {i * REC / 1e9:7.2f} GB  {i * REC / el / 1e6:6.1f} MB/s  ", end="", file=sys.stderr, flush=True)
    except OSError as e:
        print(f"\nwrite stopped at record {i}: {e}  (expected after a power cut)", file=sys.stderr)
        return
    if a.stop_gb:
        print(f"\nwrote and flushed {a.stop_gb} GB; now idle. Cut the power whenever you like (Ctrl+C just quits).", file=sys.stderr)
        try:
            while True:
                time.sleep(60)
        except KeyboardInterrupt:
            return
    print(f"\nreached the end of the drive without a power cut ({total} records)", file=sys.stderr)


def check(a):
    lines = [l for l in open(a.acked) if l.strip()]
    run_id = bytes.fromhex(lines[0].split()[2])
    acked = int(lines[-1].split(",")[0]) if lines[-1][0].isdigit() else 0
    fd = open_dev(a.dev, os.O_RDONLY)
    total = size_of(fd) // REC
    buf = mmap.mmap(-1, CHUNK * REC)
    below = {"ok": 0, "zero": 0, "other": 0, "torn": 0}
    above = dict(below)
    first_bad, last_ok, i = None, -1, 0
    while i < total:
        k = min(CHUNK, total - i)
        got = os.preadv(fd, [memoryview(buf)[:k * REC]], i * REC)
        for j in range(got // REC):
            c = classify(bytes(buf[j * REC:(j + 1) * REC]), run_id, i + j)
            if i + j < acked:
                below[c] += 1
                if c != "ok" and first_bad is None:
                    first_bad = i + j
            else:
                above[c] += 1
            if c == "ok":
                last_ok = i + j
        i += k
        if i >= acked and i > last_ok + (1 << 30) // REC:
            break
    mb = lambda r: f"{r * REC / 1e6:.1f} MB"
    print(f"run id {run_id.hex()}, records of {REC} B")
    print(f"acknowledged (FLUSH returned): {acked} records = {mb(acked)}")
    print(f"below the acknowledged mark : " + ", ".join(f"{k} {v}" for k, v in below.items()))
    print(f"above it (unflushed tail)   : " + ", ".join(f"{k} {v}" for k, v in above.items()))
    print(f"last ok record               : {last_ok} ({mb(last_ok + 1 - acked)} past the mark)")
    if first_bad is None:
        print("RESULT: every acknowledged record survived.")
    else:
        print(f"RESULT: LOST ACKNOWLEDGED DATA, first bad slot {first_bad} ({mb(first_bad)} into the drive)")


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("mode", choices=["write", "check"])
    ap.add_argument("dev")
    ap.add_argument("acked")
    ap.add_argument("--sync-mib", type=int, default=8)
    ap.add_argument("--stop-gb", type=float, default=0)
    a = ap.parse_args()
    write(a) if a.mode == "write" else check(a)


if __name__ == "__main__":
    main()
