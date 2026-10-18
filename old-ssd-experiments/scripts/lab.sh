#!/usr/bin/env bash
# lab.sh — runs the old-SSD experiments (https://jonghoon-ryu.github.io/old-ssd-experiments/)
#
#   sudo ./lab.sh check                    drive, connection, TRIM, SMART (no writes)
#   sudo ./lab.sh smart LABEL              SMART snapshot only
#        ./lab.sh oldfiles MOUNTPOINT [fileage.py options, e.g. --seed 2]   exp 1: read speed of old files vs their age (read-only)
#   sudo ./lab.sh scan LABEL [SAMPLE_MIB]  read speed across the whole drive (read-only)
#   sudo ./lab.sh reread OLDFILES_DIR     exp 1: read the 10 slowest old files again, page cache dropped (no writes)
#   sudo ./lab.sh features                 exp 2: every ATA feature, log and statistic the drive reports (no writes)
#   sudo ./lab.sh selftest [short|long]    exp 2: the drive's own self-test, timed (no writes)
#   sudo ./lab.sh slc                      exp 3: SLC cache (whole-drive sequential write)       ERASES
#   sudo ./lab.sh slc-idle MIN...          exp 3: cache recovery after MIN minutes idle          WRITES
#   sudo ./lab.sh trim                     exp 4: TRIM and reads of unmapped LBAs                ERASES
#   sudo ./lab.sh perfmap                  exp 5: speed for every block size x queue depth       ERASES
#   sudo ./lab.sh pattern                  exp 5: does the data (zeros, random, compressible) change the speed?  ERASES
#   sudo ./lab.sh wsize                    exp 6: write sizes 512 B .. 64 KiB, and misaligned 4 KiB  ERASES
#   sudo ./lab.sh flush                    exp 7: write cache on/off and a FLUSH after every write  ERASES
#   sudo ./lab.sh cliff [SPAN%] [TIMES] [DIST]  exp 8/10/11: 4 KiB random writes over SPAN% (100), TIMES x capacity (2),
#                                          fio random_distribution DIST (random; e.g. zipf:1.2)  ERASES
#   sudo ./lab.sh idlegc MIN...            exp 9: after cliff: idle MIN minutes, then 2 min of random writes  WRITES
#   sudo ./lab.sh seqwaf [TIMES]           exp 12: sequential writes of the whole drive TIMES (5) times, WAF from SMART  ERASES
#   sudo ./lab.sh mixed                    exp 13: read latency alone and while writes run    ERASES
#   sudo ./lab.sh secerase [enhanced]      exp 14: ATA SECURITY ERASE UNIT, timed, then checked  ERASES
#   sudo ./lab.sh disturb [HOURS]          exp 15: read the same 1 MiB for HOURS (6), then check the neighbours  ERASES
#   sudo ./lab.sh ret-write                exp 16: write a checked pattern before storing the drive unpowered  ERASES
#   sudo ./lab.sh ret-check                exp 16: read it back after weeks (scan + verify, no writes)
#   sudo ./lab.sh pl-write [GB]            exp 17: write numbered records until the power is cut (or GB, then idle)  ERASES
#   sudo ./lab.sh pl-check RESULT_DIR      exp 17: after power comes back: which acknowledged writes survived (no writes)
#   sudo ./lab.sh endurance [HOURS]        exp 18: random writes until the drive fails or HOURS pass (default 720)  ERASES
#
# The drive is found by its serial number, never by /dev/sdX (that name changes between USB and SATA).
# Results go to $RESULTS/<date>-<name>/ (default /home/ryuj/Ryu/old_ssd_results).
set -euo pipefail

readonly SERIAL=S1D6NSAFB40389K   # the old 840 EVO 120GB; edit here (not via the environment) for another drive
RESULTS=${RESULTS:-/home/ryuj/Ryu/old_ssd_results}
FIO=${FIO:-fio}
ENGINE=${ENGINE:-libaio}
HERE=$(cd "$(dirname "$0")" && pwd)
OWNER=${SUDO_USER:-$(id -un)}

die()  { echo "lab.sh: $*" >&2; exit 1; }
note() { echo "== $*"; }

find_dev() {
    if [ -n "${LAB_TESTDEV:-}" ]; then   # self-test against a plain file (no TRIM, no SMART)
        DEV=$LAB_TESTDEV; MODEL=testfile; TRAN=test; BYTES=$(stat -c %s "$DEV"); return
    fi
    [[ "$SERIAL" =~ ^[A-Za-z0-9]{8,}$ ]] || die "SERIAL '$SERIAL' is not a full serial number"
    local links devs
    links=$(ls /dev/disk/by-id/ 2>/dev/null | grep -E "^(ata|nvme|usb)-.*_${SERIAL}$" || true)
    [ -n "$links" ] || die "no drive with serial $SERIAL is connected (lsblk -o NAME,MODEL,SERIAL)"
    devs=$(for l in $links; do readlink -f "/dev/disk/by-id/$l"; done | sort -u)
    [ "$(echo "$devs" | wc -l)" = 1 ] || die "serial $SERIAL matches more than one device: $devs"
    DEV=$devs
    [ "$(lsblk -dno SERIAL "$DEV" | tr -d ' ')" = "$SERIAL" ] || die "$DEV does not report serial $SERIAL — refusing"
    MODEL=$(lsblk -dno MODEL "$DEV" | sed 's/ *$//')
    TRAN=$(lsblk -dno TRAN "$DEV" | tr -d ' ')
    BYTES=$(blockdev --getsize64 "$DEV" 2>/dev/null || echo $(( $(cat /sys/block/${DEV#/dev/}/size) * 512 )))
    # never the disk that holds /
    local rootdisk
    rootdisk=$(lsblk -no PKNAME "$(findmnt -no SOURCE /)" 2>/dev/null | head -1)
    [ "/dev/$rootdisk" != "$DEV" ] || die "$DEV holds / — refusing"
}

need_root() { [ -n "${LAB_TESTDEV:-}" ] || [ "$(id -u)" = 0 ] || die "run with sudo: sudo $0 $*"; }

smart_args() { if [ "$TRAN" = usb ]; then echo "-d sat"; fi; }

not_mounted() {
    [ -z "${LAB_TESTDEV:-}" ] || return 0
    if lsblk -nro MOUNTPOINTS "$DEV" | grep -q .; then
        lsblk -o NAME,SIZE,FSTYPE,MOUNTPOINTS "$DEV"
        die "a partition of $DEV is mounted — unmount it first (sudo umount ...)"
    fi
}

need_trim() {
    [ -z "${LAB_TESTDEV:-}" ] || return 0
    local max
    max=$(lsblk -dno DISC-MAX "$DEV" | tr -d ' ')
    [ "$max" != "0B" ] || die "$DEV ($TRAN) does not accept TRIM here (DISC-MAX 0B). Connect it to an internal SATA port."
}

confirm_erase() {
    echo
    [ -n "${LAB_TESTDEV:-}" ] || lsblk -o NAME,MODEL,SERIAL,SIZE,TRAN "$DEV"
    echo
    echo "  !!! This ERASES everything on $DEV ($MODEL, serial $SERIAL)."
    local want=${SERIAL: -5}
    read -r -p "  Type the last 5 characters of the serial ($want) to continue: " ans
    [ "$ans" = "$want" ] || die "not confirmed — nothing was written"
}

new_out() {
    OUT="$RESULTS/$(date +%Y%m%d-%H%M%S)-$1"
    mkdir -p "$OUT"
    {
        echo "experiment: $1"
        echo "date:       $(date '+%Y-%m-%d %H:%M:%S %z')"
        echo "command:    $0 ${ARGS[*]}"
        echo "device:     $DEV  model: $MODEL  serial: $SERIAL  transport: $TRAN  bytes: $BYTES"
        echo "kernel:     $(uname -r)"
        echo "fio:        $($FIO --version 2>/dev/null || echo none)"
    } > "$OUT/meta.txt"
    note "results -> $OUT"
}

finish() { chown -R "$OWNER": "$RESULTS" 2>/dev/null || true; note "done: $OUT"; }

smart() {   # smart LABEL : text + JSON snapshot into $OUT
    # shellcheck disable=SC2046
    smartctl -x $(smart_args) "$DEV" > "$OUT/smart-$1.txt" 2>&1 || true
    # shellcheck disable=SC2046
    smartctl -x --json=c $(smart_args) "$DEV" > "$OUT/smart-$1.json" 2>/dev/null || true
    grep -E "^ *(5|9|12|177|179|181|182|183|187|190|195|199|235|241) [A-Z][A-Za-z_]+ " "$OUT/smart-$1.txt" | sed 's/^/   /' || true
}

discard_all() {
    note "blkdiscard $DEV (TRIM every LBA)"
    if [ -n "${LAB_TESTDEV:-}" ]; then fallocate --punch-hole -o 0 -l "$BYTES" "$DEV"; else blkdiscard -f "$DEV"; fi   # -f: newer blkdiscard refuses a disk with a partition table; confirm_erase already asked
    note "let the drive settle for ${SETTLE:-120} s"
    sleep "${SETTLE:-120}"
}

fill_all() {   # sequential 1 MiB writes over the whole drive, so later reads really go to NAND
    note "fill the whole drive sequentially (1 MiB, QD8)"
    run_fio fill --rw=write --bs=1M --iodepth=8 --size=100%
}

summary() {   # summary : one CSV row per fio run in $OUT (fiosum.py)
    python3 "$HERE/fiosum.py" "$OUT/summary.csv" "$OUT"/*.json | column -s, -t
}

mib_round() { echo $(( $1 / 1048576 * 1048576 )); }

run_fio() {   # run_fio NAME fio-args... : common options, logs every second, JSON report
    local name=$1; shift
    $FIO --name="$name" --filename="$DEV" --direct=1 --ioengine="$ENGINE" \
         --group_reporting --per_job_logs=0 --log_avg_msec=1000 \
         --write_bw_log="$OUT/$name" --write_iops_log="$OUT/$name" --write_lat_log="$OUT/$name" \
         --output-format=json --output="$OUT/$name.json" --verify_state_save=0 \
         --eta=always --eta-newline=30 "$@"
}

ARGS=("$@")
cmd=${1:-}; shift || true

case "$cmd" in
check)
    need_root check; find_dev
    new_out check
    note "$DEV  $MODEL  serial $SERIAL  via $TRAN  $(( BYTES / 1000000000 )) GB"
    lsblk -o NAME,MODEL,SERIAL,SIZE,TRAN,ROTA,DISC-GRAN,DISC-MAX,REV,FSTYPE,MOUNTPOINTS "$DEV" | tee "$OUT/lsblk.txt"
    note "TRIM through this connection: $(lsblk -dno DISC-MAX "$DEV" | tr -d ' ') per request (0B = no TRIM)"
    hdparm -I "$DEV" > "$OUT/hdparm-I.txt" 2>&1 || true
    grep -iE "model|firmware|trim|sanitize|erase unit" "$OUT/hdparm-I.txt" | sed 's/^/   /' || true
    note "SMART"
    smart check
    grep -iE "firmware|power_on|SMART overall|result" "$OUT/smart-check.txt" | head -5 | sed 's/^/   /' || true
    finish ;;
smart)
    need_root smart; find_dev
    new_out "smart-${1:-now}"; smart "${1:-now}"; finish ;;
oldfiles)
    [ -n "${1:-}" ] || die "usage: $0 oldfiles MOUNTPOINT"
    find_dev
    findmnt -n "$1" >/dev/null || die "$1 is not a mount point — mount the partition first (setup page, step 5)"
    new_out oldfiles
    mnt=$1; shift
    findmnt -no SOURCE,FSTYPE,OPTIONS "$mnt" | tee -a "$OUT/meta.txt"
    findmnt -no OPTIONS "$mnt" | grep -qE '(^|,)ro(,|$)' || echo "   (warning: $mnt is not mounted read-only)"
    python3 "$HERE/fileage.py" "$mnt" "$OUT/fileage.csv" "$@" 2>&1 | tee "$OUT/fileage.log"
    finish ;;
scan)
    need_root scan; find_dev
    [ -n "${1:-}" ] || die "usage: $0 scan LABEL [SAMPLE_MIB]"
    new_out "scan-$1"
    smart before
    python3 "$HERE/readscan.py" "$DEV" "$OUT/scan.csv" --chunk-mib 256 --sample-mib "${2:-0}"
    smart after
    finish ;;
slc)
    need_root slc; find_dev; not_mounted; need_trim; confirm_erase
    new_out slc
    discard_all
    smart before
    note "sequential 1 MiB writes over the whole drive (watch the speed drop when the SLC cache is full)"
    run_fio slc --rw=write --bs=1M --iodepth=8 --size=100%
    smart after
    finish ;;
slc-idle)
    need_root slc-idle; find_dev; not_mounted
    [ $# -gt 0 ] || die "usage: $0 slc-idle MINUTES... (e.g. 0 1 5 15)"
    confirm_erase
    new_out slc-idle
    note "first fill the cache: 8 GiB at offset 0"
    run_fio fill --rw=write --bs=1M --iodepth=8 --size=8G
    for m in "$@"; do
        note "idle $m min, then 8 GiB sequential write"
        sleep $(( m * 60 ))
        run_fio "idle${m}" --rw=write --bs=1M --iodepth=8 --size=8G
    done
    finish ;;
trim)
    need_root trim; find_dev; not_mounted; need_trim; confirm_erase
    new_out trim
    discard_all
    half=$(mib_round $(( BYTES / 2 )))
    note "1) scan right after TRIM (32 MiB of every 256 MiB)"
    python3 "$HERE/readscan.py" "$DEV" "$OUT/scan-trimmed.csv" --chunk-mib 256 --sample-mib 32
    note "2) write the first half sequentially"
    run_fio fillhalf --rw=write --bs=1M --iodepth=8 --size="$half"
    note "3) 4 KiB random reads, QD1, 60 s: first half (mapped) vs second half (unmapped)"
    run_fio rd-mapped   --rw=randread --bs=4k --iodepth=1 --size="$half" --time_based --runtime=60 --randrepeat=0
    run_fio rd-unmapped --rw=randread --bs=4k --iodepth=1 --offset="$half" --size="$half" --time_based --runtime=60 --randrepeat=0
    note "4) the same at QD32 (IOPS)"
    run_fio rd32-mapped   --rw=randread --bs=4k --iodepth=32 --size="$half" --time_based --runtime=60 --randrepeat=0
    run_fio rd32-unmapped --rw=randread --bs=4k --iodepth=32 --offset="$half" --size="$half" --time_based --runtime=60 --randrepeat=0
    note "5) scan again (first half data, second half still trimmed)"
    python3 "$HERE/readscan.py" "$DEV" "$OUT/scan-half.csv" --chunk-mib 256 --sample-mib 32
    finish ;;
cliff)
    need_root cliff; find_dev; not_mounted; need_trim
    span=${1:-100}; times=${2:-2}; dist=${3:-random}
    [ "$span" -ge 10 ] && [ "$span" -le 100 ] || die "SPAN% must be 10..100"
    [[ "$dist" =~ ^[a-z]+(:[0-9.:/,]+)?$ ]] || die "DIST '$dist' is not a fio random_distribution (random, zipf:1.2, zoned:80/20:20/80 ...)"
    confirm_erase
    if [ "$dist" = random ]; then new_out "cliff-span${span}"; else new_out "cliff-span${span}-${dist//[:\/]/_}"; fi
    sbytes=$(mib_round $(( BYTES * span / 100 )))
    total=$(mib_round $(( BYTES * times )))
    echo "span_bytes: $sbytes  io_bytes: $total" >> "$OUT/meta.txt"
    discard_all
    smart before
    note "4 KiB random writes ($dist), QD32, over the first ${span}% ($(( sbytes / 1000000000 )) GB), $(( total / 1000000000 )) GB in total"
    run_fio cliff --rw=randwrite --bs=4k --iodepth=32 --size="$sbytes" --io_size="$total" \
                  --norandommap --randrepeat=0 --random_generator=tausworthe64 --random_distribution="$dist"
    smart after
    finish ;;
seqwaf)
    need_root seqwaf; find_dev; not_mounted; need_trim
    times=${1:-5}
    confirm_erase
    new_out "seqwaf-x${times}"
    discard_all
    smart before
    note "sequential 128 KiB writes of the whole drive, $times times"
    run_fio seq --rw=write --bs=128k --iodepth=16 --size=100% --loops="$times"
    smart after
    finish ;;
ret-write)
    need_root ret-write; find_dev; not_mounted; confirm_erase
    new_out ret-write
    smart before
    note "write the whole drive with a checked pattern (crc32c header in every 4 KiB block)"
    run_fio ret --rw=write --bs=1M --iodepth=8 --size=100% --verify=crc32c --verify_interval=4096 --do_verify=0
    smart after
    date '+%Y-%m-%d %H:%M' > "$OUT/written-at.txt"
    note "now: sudo poweroff, take the drive out (or unplug its power) and store it for 2-4 weeks"
    finish ;;
ret-check)
    need_root ret-check; find_dev; not_mounted
    new_out ret-check
    smart before
    note "1) first read of the stored data: speed and slow reads across the drive"
    python3 "$HERE/readscan.py" "$DEV" "$OUT/scan.csv" --chunk-mib 256
    note "2) check every block against its checksum (reads only)"
    run_fio ret --rw=write --bs=1M --iodepth=8 --size=100% --verify=crc32c --verify_interval=4096 \
                --verify_only --verify_fatal=0 --verify_dump=0 2>&1 | tee "$OUT/verify.log" || true
    bad=$(grep -c "verify failed" "$OUT/verify.log" || true)
    echo "bad 4 KiB blocks: $bad" | tee "$OUT/verify-summary.txt"
    smart after
    finish ;;
reread)
    need_root reread; find_dev
    [ -f "${1:-}/fileage.csv" ] || die "usage: $0 reread RESULT_DIR_OF_oldfiles"
    mnt=$(findmnt -nro TARGET "$(readlink -f "$DEV")3" | head -1)
    [ -n "$mnt" ] || die "partition 3 of $DEV is not mounted (setup page, step 5)"
    OUT=$1
    python3 "$HERE/fileage.py" "$mnt" "$OUT/fileage-reread.csv" --reread-from "$OUT/fileage.csv"
    finish ;;
features)
    need_root features; find_dev
    new_out features
    hdparm -I "$DEV" > "$OUT/hdparm-I.txt" 2>&1 || true
    note "ATA features (whole list: hdparm-I.txt)"
    grep -E "Model Number|Firmware Revision|LBA48 +user|Logical +Sector size|Queue depth|Write cache|FLUSH_CACHE_EXT|Gen3|Native Command Queueing|TRIM|ZEROs|encrypts|Sanitize" \
        "$OUT/hdparm-I.txt" | sed 's/^/   /' || true
    sed -n '/^Security:/,/^Logical Unit/p' "$OUT/hdparm-I.txt" | sed '$d; s/^/   /' || true
    note "visible / native max sectors (HPA), write cache, read look-ahead, APM"
    hdparm -N -W -A -B "$DEV" 2>&1 | tee "$OUT/hdparm-NWAB.txt" | sed 's/^/   /' || true
    note "SMART: attributes, logs, device statistics, temperature history"
    smart features
    # shellcheck disable=SC2046
    for l in devstat error xerror selftest scttemp sataphy directory; do
        smartctl -l "$l" $(smart_args) "$DEV" > "$OUT/smart-log-$l.txt" 2>&1 || true
    done
    note "error log, self-test log, device statistics"
    for l in error selftest devstat; do grep -hE "No Errors|No self-tests|not supported|Error [0-9]+ |# ?[0-9]+ " "$OUT/smart-log-$l.txt" | head -5 | sed "s/^/   $l: /"; done || true
    note "SATA link counters that are not zero (counted since power-on)"
    awk '$1 ~ /^0x/ && $3 != 0' "$OUT/smart-log-sataphy.txt" | sed 's/^/   /' || true
    note "temperature history (every 10 min)"
    grep -E "^ +[0-9]+ +20[0-9-]+ [0-9:]+ +[0-9]+ " "$OUT/smart-log-scttemp.txt" | tail -12 | sed 's/^/   /' || true
    finish ;;
selftest)
    need_root selftest; find_dev
    kind=${1:-long}
    [ "$kind" = short ] || [ "$kind" = long ] || die "usage: $0 selftest [short|long]"
    new_out "selftest-$kind"
    smart before
    # shellcheck disable=SC2046
    smartctl -c $(smart_args) "$DEV" | grep -A1 -i "self-test routine" | sed 's/^/   /' || true
    t0=$(date +%s)
    # shellcheck disable=SC2046
    smartctl -t "$kind" $(smart_args) "$DEV" | tail -4
    note "waiting for the drive (checked every 30 s; do not use the drive meanwhile)"
    last=
    while sleep 30; do
        # shellcheck disable=SC2046
        st=$(smartctl -c $(smart_args) "$DEV" | grep -A1 "Self-test execution status" | tr -s ' \n\t' ' ')
        [ "$st" = "$last" ] || echo "   $(( ($(date +%s) - t0) / 60 )) min: $st" | cut -c1-150   # only when it changes
        last=$st
        echo "$st" | grep -q "in progress" || break
    done
    echo "seconds: $(( $(date +%s) - t0 ))" | tee -a "$OUT/meta.txt"
    # shellcheck disable=SC2046
    smartctl -l selftest $(smart_args) "$DEV" | tee "$OUT/selftest-log.txt" | sed -n '1,12p'
    smart after
    finish ;;
perfmap)
    need_root perfmap; find_dev; not_mounted; need_trim; confirm_erase
    new_out perfmap
    discard_all
    fill_all
    smart before
    note "reads: 4 block sizes x 3 queue depths x (random, sequential), 20 s each (about 17 min)"
    for rw in randread read; do for bs in 4k 16k 128k 1m; do for qd in 1 4 32; do
        run_fio "${rw}-${bs}-qd${qd}" --rw=$rw --bs=$bs --iodepth=$qd --size=100% --time_based --runtime=20 --ramp_time=2 \
                --randrepeat=0 >/dev/null
        echo "   ${rw} ${bs} QD${qd} done"
    done; done; done
    note "writes: the same grid, 15 s each (the SLC buffer refills between runs, so these are buffered speeds)"
    for rw in randwrite write; do for bs in 4k 128k 1m; do for qd in 1 32; do
        run_fio "${rw}-${bs}-qd${qd}" --rw=$rw --bs=$bs --iodepth=$qd --size=100% --time_based --runtime=15 \
                --randrepeat=0 >/dev/null
        echo "   ${rw} ${bs} QD${qd} done"; sleep 30
    done; done; done
    smart after
    rm -f "$OUT"/fill.json
    summary
    finish ;;
pattern)
    need_root pattern; find_dev; not_mounted; need_trim; confirm_erase
    new_out pattern
    discard_all
    smart before
    # 16 GiB each (well past the ~3 GB SLC buffer), each into its own fresh 16 GiB region, 3 min rest between
    i=0
    for p in zeros random comp50 comp90 deadbeef; do
        case $p in
            zeros)    opt=(--zero_buffers) ;;
            random)   opt=(--refill_buffers) ;;
            comp50)   opt=(--refill_buffers --buffer_compress_percentage=50 --buffer_compress_chunk=4k) ;;
            comp90)   opt=(--refill_buffers --buffer_compress_percentage=90 --buffer_compress_chunk=4k) ;;
            deadbeef) opt=(--buffer_pattern=0xdeadbeef) ;;
        esac
        note "$p: 16 GiB sequential at offset $(( i * 16 )) GiB"
        run_fio "$p" --rw=write --bs=1M --iodepth=8 --offset=$(( i * 16 ))G --size=16G "${opt[@]}" >/dev/null
        smart "after-$p" >/dev/null
        i=$(( i + 1 )); sleep 180
    done
    summary
    finish ;;
wsize)
    need_root wsize; find_dev; not_mounted; need_trim; confirm_erase
    new_out wsize
    discard_all
    fill_all
    smart before
    note "random writes inside the first 8 GiB, QD1 and QD32, 30 s each, 60 s rest (lets the SLC buffer drain)"
    for bs in 512 1k 2k 4k 8k 16k 32k 64k; do for qd in 1 32; do
        run_fio "bs${bs}-qd${qd}" --rw=randwrite --bs=$bs --iodepth=$qd --size=8G --time_based --runtime=30 --randrepeat=0 >/dev/null
        echo "   ${bs} QD${qd} done"; sleep 60
    done; done
    note "4 KiB writes that start 512 B off a 4 KiB boundary"
    for qd in 1 32; do
        run_fio "mis4k-qd${qd}" --rw=randwrite --bs=4k --blockalign=4k --offset=512 --iodepth=$qd --size=8G --time_based --runtime=30 \
                --randrepeat=0 >/dev/null
        sleep 60
    done
    smart after
    rm -f "$OUT"/fill.json
    summary
    finish ;;
flush)
    need_root flush; find_dev; not_mounted; need_trim; confirm_erase
    new_out flush
    trap 'hdparm -W1 "$DEV" >/dev/null 2>&1 || true' EXIT
    discard_all
    hdparm -W "$DEV" | tee -a "$OUT/meta.txt"
    note "write cache ON"
    hdparm -W1 "$DEV" >/dev/null
    run_fio wc1-4k        --rw=randwrite --bs=4k --iodepth=1 --size=8G --time_based --runtime=30 --randrepeat=0 >/dev/null; sleep 60
    run_fio wc1-4k-fsync  --rw=randwrite --bs=4k --iodepth=1 --size=8G --time_based --runtime=30 --randrepeat=0 --fsync=1 >/dev/null; sleep 60
    run_fio wc1-1m-fsync  --rw=write --bs=1M --iodepth=1 --offset=16G --size=8G --time_based --runtime=30 --fsync=1 >/dev/null; sleep 60
    note "write cache OFF (hdparm -W0): every write must be on NAND before it completes"
    hdparm -W0 "$DEV" >/dev/null
    run_fio wc0-4k        --rw=randwrite --bs=4k --iodepth=1 --size=8G --time_based --runtime=30 --randrepeat=0 >/dev/null; sleep 60
    run_fio wc0-4k-qd32   --rw=randwrite --bs=4k --iodepth=32 --size=8G --time_based --runtime=30 --randrepeat=0 >/dev/null; sleep 60
    run_fio wc0-1m        --rw=write --bs=1M --iodepth=1 --offset=32G --size=8G --time_based --runtime=30 >/dev/null
    hdparm -W1 "$DEV" >/dev/null
    note "write cache back ON"
    summary
    finish ;;
idlegc)
    need_root idlegc; find_dev; not_mounted
    [ $# -gt 0 ] || die "usage: $0 idlegc MINUTES... (e.g. 0 1 5 15 30), right after 'cliff 100'"
    confirm_erase
    new_out idlegc
    note "10 min of 4 KiB random writes first, so the drive is surely in steady state"
    run_fio pre --rw=randwrite --bs=4k --iodepth=32 --size=100% --norandommap --randrepeat=0 --time_based --runtime=600
    for m in "$@"; do
        note "idle $m min, then 2 min of 4 KiB random writes (IOPS every second)"
        sleep $(( m * 60 ))
        run_fio "idle${m}" --rw=randwrite --bs=4k --iodepth=32 --size=100% --norandommap --randrepeat=0 --time_based --runtime=120 >/dev/null
    done
    summary
    finish ;;
mixed)
    need_root mixed; find_dev; not_mounted; need_trim; confirm_erase
    new_out mixed
    discard_all
    fill_all
    note "random 4 KiB writes for 10 min first, so writes later make the drive do GC"
    run_fio pre --rw=randwrite --bs=4k --iodepth=32 --size=100% --norandommap --randrepeat=0 --time_based --runtime=600
    rd=(--name=rd --rw=randread --bs=4k --iodepth=1 --randrepeat=0 --per_job_logs=0)
    for case in alone seqwrite randwrite; do
        case $case in
            alone)     wr=() ;;
            seqwrite)  wr=(--name=wr --rw=write --bs=1M --iodepth=8 --offset=50% --size=50%) ;;
            randwrite) wr=(--name=wr --rw=randwrite --bs=4k --iodepth=32 --norandommap --randrepeat=0) ;;
        esac
        note "4 KiB random reads, QD1, 60 s, with: $case"
        $FIO --filename="$DEV" --direct=1 --ioengine="$ENGINE" --time_based --runtime=60 --size=100% \
             --log_avg_msec=1000 --log_max_value=1 --output-format=json --output="$OUT/$case.json" \
             "${rd[@]}" --write_lat_log="$OUT/$case-rd" "${wr[@]}" >/dev/null
        sleep 60
    done
    rm -f "$OUT"/pre.json "$OUT"/fill.json
    summary
    finish ;;
secerase)
    need_root secerase; find_dev; not_mounted
    mode=${1:-normal}
    [ "$mode" = normal ] || [ "$mode" = enhanced ] || die "usage: $0 secerase [enhanced]"
    hdparm -I "$DEV" > /tmp/lab-secerase-I.txt 2>&1 || true
    sec=$(sed -n '/^Security:/,/^Logical/p' /tmp/lab-secerase-I.txt)
    echo "$sec" | sed 's/^/   /'
    echo "$sec" | grep -qE "^\s+not\s+frozen" || die "the drive is 'frozen' (the BIOS locks security commands at boot).
   Unfreeze: 'sudo systemctl suspend', wake the PC, then run this again. The drive must report 'not frozen'."
    echo "$sec" | grep -qE "^\s+supported$" || die "the drive does not report the ATA security feature set"
    echo "$sec" | grep -qE "^\s+not\s+enabled" || die "a security password is already set — see the page (exp 14) to unlock or disable it first"
    confirm_erase
    new_out "secerase-$mode"
    cp /tmp/lab-secerase-I.txt "$OUT/hdparm-I-before.txt"
    fill_all
    run_fio before-4k --rw=randwrite --bs=4k --iodepth=32 --size=100% --norandommap --randrepeat=0 --time_based --runtime=600
    smart before
    note "set a temporary user password 'lab' (needed for the erase command; the erase clears it again)"
    echo "password: lab (if the erase is interrupted: hdparm --user-master u --security-disable lab $DEV)" >> "$OUT/meta.txt"
    hdparm --user-master u --security-set-pass lab "$DEV" > /dev/null
    opt=--security-erase; [ "$mode" = enhanced ] && opt=--security-erase-enhanced
    note "SECURITY ERASE UNIT ($mode): the command blocks until the drive is done"
    t0=$(date +%s)
    hdparm --user-master u $opt lab "$DEV" | tail -2
    echo "erase_seconds: $(( $(date +%s) - t0 ))" | tee -a "$OUT/meta.txt"
    hdparm -I "$DEV" > "$OUT/hdparm-I-after.txt" 2>&1 || true
    sed -n '/^Security:/,/^Logical/p' "$OUT/hdparm-I-after.txt" | sed 's/^/   /'
    smart after
    note "1) is everything zero now? scan 8 MiB of every 256 MiB"
    python3 "$HERE/readscan.py" "$DEV" "$OUT/scan.csv" --chunk-mib 256 --sample-mib 8
    note "2) are the free blocks back? 10 min of 4 KiB random writes (compare with before-4k)"
    run_fio after-4k --rw=randwrite --bs=4k --iodepth=32 --size=100% --norandommap --randrepeat=0 --time_based --runtime=600
    rm -f "$OUT"/fill.json
    summary
    finish ;;
disturb)
    need_root disturb; find_dev; not_mounted; confirm_erase
    hours=${1:-6}
    new_out "disturb-${hours}h"
    note "write the whole drive with a checked pattern (crc32c in every 4 KiB block)"
    run_fio ret --rw=write --bs=1M --iodepth=8 --size=100% --verify=crc32c --verify_interval=4096 --do_verify=0
    note "first look at the first 1 GiB (QD1 4 KiB reads, 60 s) before hammering"
    run_fio near-before --rw=randread --bs=4k --iodepth=1 --size=1G --time_based --runtime=60 --randrepeat=0 >/dev/null
    smart before
    note "read the same 1 MiB (256 x 4 KiB) at QD32 for $hours h: latency max every second shows relocations"
    $FIO --name=hammer --filename="$DEV" --direct=1 --ioengine="$ENGINE" --rw=randread --bs=4k --iodepth=32 --size=1M \
         --time_based --runtime=$(( hours * 3600 )) --log_avg_msec=1000 --log_max_value=1 --per_job_logs=0 \
         --write_lat_log="$OUT/hammer" --write_iops_log="$OUT/hammer" --output-format=json --output="$OUT/hammer.json" \
         --eta=always --eta-newline=300
    smart after
    note "check: the first 1 GiB again, then every block on the drive against its checksum"
    run_fio near-after --rw=randread --bs=4k --iodepth=1 --size=1G --time_based --runtime=60 --randrepeat=0 >/dev/null
    run_fio ret --rw=write --bs=1M --iodepth=8 --size=100% --verify=crc32c --verify_interval=4096 \
                --verify_only --verify_fatal=0 --verify_dump=0 2>&1 | tee "$OUT/verify.log" || true
    bad=$(grep -c "verify failed" "$OUT/verify.log" || true)
    echo "bad 4 KiB blocks: $bad" | tee "$OUT/verify-summary.txt"
    rm -f "$OUT"/ret.json
    summary
    finish ;;
pl-write)
    need_root pl-write; find_dev; not_mounted; confirm_erase
    new_out pl-write
    smart before
    note "writing numbered 4 KiB records; FLUSH every 8 MiB; acknowledged counts go to $OUT/acked.csv (on this PC's disk)"
    note "cut the drive's power whenever you like (pull the USB cable of the adapter), then run: sudo $0 pl-check $OUT"
    echo "stop_gb: ${1:-0}" >> "$OUT/meta.txt"
    python3 "$HERE/plcheck.py" write "$DEV" "$OUT/acked.csv" --stop-gb "${1:-0}" || true
    finish ;;
pl-check)
    need_root pl-check; find_dev; not_mounted
    [ -f "${1:-}/acked.csv" ] || die "usage: $0 pl-check RESULT_DIR_OF_pl-write"
    W=$1
    OUT=$W
    smart after
    python3 "$HERE/plcheck.py" check "$DEV" "$W/acked.csv" | tee "$W/check.txt"
    finish ;;
endurance)
    need_root endurance; find_dev; not_mounted; need_trim
    hours=${1:-720}
    confirm_erase
    new_out endurance
    discard_all
    smart h0000
    echo "hour,date,status" > "$OUT/hours.csv"
    for ((h = 1; h <= hours; h++)); do
        status=ok
        run_fio "w$(printf %04d $h)" --rw=randwrite --bs=4k --iodepth=32 --size=100% \
              --norandommap --randrepeat=0 --time_based --runtime=3600 >/dev/null 2>&1 || status=fio-error
        smart "h$(printf %04d $h)" > /dev/null
        echo "$h,$(date '+%F %T'),$status" >> "$OUT/hours.csv"
        chown -R "$OWNER": "$OUT" 2>/dev/null || true
        note "hour $h: $status"
        [ "$status" = ok ] || { note "the drive stopped accepting writes"; break; }
    done
    finish ;;
*)
    sed -n '2,/^set -euo/p' "$0" | sed '$d; s/^# \{0,1\}//'
    exit 1 ;;
esac
