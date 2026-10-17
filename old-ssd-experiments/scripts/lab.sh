#!/usr/bin/env bash
# lab.sh — runs the old-SSD experiments (https://jonghoon-ryu.github.io/old-ssd-experiments/)
#
#   sudo ./lab.sh check                    drive, connection, TRIM, SMART (no writes)
#   sudo ./lab.sh smart LABEL              SMART snapshot only
#        ./lab.sh oldfiles MOUNTPOINT      exp 1: read speed of old files vs their age (read-only)
#   sudo ./lab.sh scan LABEL [SAMPLE_MIB]  read speed across the whole drive (read-only)
#   sudo ./lab.sh slc                      exp 2: SLC cache (whole-drive sequential write)       ERASES
#   sudo ./lab.sh slc-idle MIN...          exp 2: cache recovery after MIN minutes idle          WRITES
#   sudo ./lab.sh trim                     exp 3: TRIM and reads of unmapped LBAs                ERASES
#   sudo ./lab.sh cliff [SPAN%] [TIMES]    exp 4/5: 4 KiB random writes over SPAN% (default 100), TIMES x capacity (2)  ERASES
#   sudo ./lab.sh seqwaf [TIMES]           exp 6: sequential writes of the whole drive TIMES (5) times, WAF from SMART  ERASES
#   sudo ./lab.sh ret-write                exp 7: write a checked pattern before storing the drive unpowered       ERASES
#   sudo ./lab.sh ret-check                exp 7: read it back after weeks (scan + verify, no writes)
#   sudo ./lab.sh endurance [HOURS]        exp 8: random writes until the drive fails or HOURS pass (default 720)  ERASES
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
    grep -E "^ *(5|9|12|177|179|181|182|183|187|190|195|199|235|241) " "$OUT/smart-$1.txt" | sed 's/^/   /' || true
}

discard_all() {
    note "blkdiscard $DEV (TRIM every LBA)"
    if [ -n "${LAB_TESTDEV:-}" ]; then fallocate --punch-hole -o 0 -l "$BYTES" "$DEV"; else blkdiscard "$DEV"; fi
    note "let the drive settle for ${SETTLE:-120} s"
    sleep "${SETTLE:-120}"
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
    new_out oldfiles
    findmnt -no SOURCE,FSTYPE,OPTIONS "$1" | tee -a "$OUT/meta.txt"
    findmnt -no OPTIONS "$1" | grep -qE '(^|,)ro(,|$)' || echo "   (warning: $1 is not mounted read-only)"
    python3 "$HERE/fileage.py" "$1" "$OUT/fileage.csv"
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
    span=${1:-100}; times=${2:-2}
    [ "$span" -ge 10 ] && [ "$span" -le 100 ] || die "SPAN% must be 10..100"
    confirm_erase
    new_out "cliff-span${span}"
    sbytes=$(mib_round $(( BYTES * span / 100 )))
    total=$(mib_round $(( BYTES * times )))
    echo "span_bytes: $sbytes  io_bytes: $total" >> "$OUT/meta.txt"
    discard_all
    smart before
    note "4 KiB random writes, QD32, over the first ${span}% ($(( sbytes / 1000000000 )) GB), $(( total / 1000000000 )) GB in total"
    run_fio cliff --rw=randwrite --bs=4k --iodepth=32 --size="$sbytes" --io_size="$total" \
                  --norandommap --randrepeat=0 --random_generator=tausworthe64
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
    sed -n '2,21p' "$0" | sed 's/^# \{0,1\}//'
    exit 1 ;;
esac
