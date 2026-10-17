#!/usr/bin/env python3
"""smartdiff.py RESULT_DIR [--before before] [--after after] [--raw-gib 128]

Compares smart-<before>.json and smart-<after>.json (written by lab.sh) and prints every SMART
attribute that changed. If the drive has 241 Total_LBAs_Written (host writes, 512-byte units)
and 177 Wear_Leveling_Count (average erase count of all blocks), it also estimates

  NAND written  ~ (change of 177) x raw NAND size   (every block erased once more = raw size programmed)
  WAF           ~ NAND written / host written

The 840 EVO 120GB is reported to carry 128 GiB of NAND (--raw-gib). One step of 177 is about
137 GB of NAND writes, so the estimate is coarse: write enough data for 177 to rise by 5 or more.
"""
import argparse, json, os, sys


def attrs(path):
    d = json.load(open(path))
    return {a["id"]: a for a in d.get("ata_smart_attributes", {}).get("table", [])}


def main():
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("dir")
    ap.add_argument("--before", default="before")
    ap.add_argument("--after", default="after")
    ap.add_argument("--raw-gib", type=float, default=128)
    a = ap.parse_args()
    b = attrs(os.path.join(a.dir, f"smart-{a.before}.json"))
    c = attrs(os.path.join(a.dir, f"smart-{a.after}.json"))
    if not b or not c:
        sys.exit("smartdiff.py: no ATA SMART attribute table in the JSON files")
    print(f"{'id':>4} {'name':<28} {'before':>14} {'after':>14} {'change':>12}")
    for i in sorted(set(b) | set(c)):
        rb = b.get(i, {}).get("raw", {}).get("value")
        rc = c.get(i, {}).get("raw", {}).get("value")
        name = (c.get(i) or b.get(i))["name"]
        mark = "" if rb == rc else f"{(rc or 0) - (rb or 0):+12d}"
        print(f"{i:>4} {name:<28} {rb!s:>14} {rc!s:>14} {mark}")
    if 241 in b and 241 in c:
        host = (c[241]["raw"]["value"] - b[241]["raw"]["value"]) * 512
        print(f"\nhost writes (241):  {host / 1e9:10.1f} GB")
        if 177 in b and 177 in c:
            pe = c[177]["raw"]["value"] - b[177]["raw"]["value"]
            nand = pe * a.raw_gib * (1 << 30)
            print(f"erase count (177):  +{pe}  ->  NAND writes ~ {nand / 1e9:.0f} GB")
            if host > 0 and pe > 0:
                lo = max(pe - 1, 0) * a.raw_gib * (1 << 30) / host
                hi = (pe + 1) * a.raw_gib * (1 << 30) / host
                print(f"WAF ~ {nand / host:.2f}   (177 counts whole steps, so between {lo:.2f} and {hi:.2f})")


if __name__ == "__main__":
    main()
