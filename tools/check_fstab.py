#!/usr/bin/env python3
"""
Validate the TWRP fstab for SM-T285YD against stock references. Read-only.

Usage:
  check_fstab.py STOCK_RECOVERY_FSTAB STOCK_BOOT_FSTAB TABLET_PARTITIONS TWRP_FSTAB

Checks:
  1. Both stock files and the TWRP file parse; no duplicate block devices or mount points.
  2. Every stock recovery entry appears in TWRP exactly once, with the same block device,
     the same filesystem type, and the same mount point (only the renames listed in
     ALLOWED_RENAMES are accepted).
  3. TWRP has no entries that are not in the stock recovery fstab.
  4. Every by-name block device exists on the actual tablet (TABLET_PARTITIONS).
  5. /data: length= matches stock recovery, and encryptable= matches the stock boot fstab.
  6. An alternate block device, if present, is the whole-disk parent of the primary
     (e.g. /dev/block/mmcblk1 for /dev/block/mmcblk1p1).
  7. flags= contains only known keys, no key twice, and every value is valid for its
     key (e.g. backup=0/1, display="non-empty"); quotes are balanced on every line.
TWRP format (v1): <mount> <fs> <device> [<alt device>] [length=N] [flags=k=v;k;...]
"""
import re
import sys

ALLOWED_RENAMES = {"/sdcard": "/external_sd"}   # stock mount point -> TWRP mount point
BYNAME = "/dev/block/platform/sdio_emmc/by-name/"
# Allowed TWRP flags and their value rules.
#   "bool01": value must be exactly 0 or 1      "bare": no value allowed
#   "text":   non-empty quoted text             "word": non-empty, letters/digits/_ only
FLAG_RULES = {
    "display": "text",
    "backup": "bool01",
    "storage": "bare",
    "wipeingui": "bare",
    "removable": "bare",
    "encryptable": "word",
}

errors = []


def fail(msg):
    errors.append(msg)
    print("FAIL   " + msg)


def lines(path):
    for n, raw in enumerate(open(path), 1):
        line = raw.split("#")[0].strip() if not raw.lstrip().startswith("#") else ""
        if line:
            yield n, line


def parse_stock(path):
    """Android v2 fstab: <device> <mount> <fs> <mnt opts> <fs_mgr flags>"""
    out = []
    for n, l in lines(path):
        f = l.split()
        if len(f) < 3 or not f[0].startswith("/dev/"):
            continue  # skips vold 'auto' entries
        out.append({"dev": f[0], "mnt": f[1], "fs": f[2],
                    "opts": " ".join(f[3:]), "line": n})
    return out


def parse_twrp(path):
    out = []
    for n, l in lines(path):
        if l.count('"') % 2:
            fail(f"twrp line {n}: unbalanced quotes")
        toks = re.findall(r'(?:[^\s"]|"[^"]*")+', l)
        e = {"mnt": toks[0], "fs": toks[1], "dev": toks[2], "alt": None,
             "length": None, "flags": {}, "line": n}
        for t in toks[3:]:
            if t.startswith("/"):
                e["alt"] = t
            elif t.startswith("length="):
                e["length"] = t[7:]
            elif t.startswith("flags="):
                for item in t[6:].split(";"):
                    k, has_eq, v = item.partition("=")
                    rule = FLAG_RULES.get(k)
                    if rule is None:
                        fail(f"twrp line {n}: unknown flag '{k}'")
                        continue
                    if k in e["flags"]:
                        fail(f"twrp line {n}: duplicate flag '{k}'")
                    if rule == "bare":
                        if has_eq:
                            fail(f"twrp line {n}: flag '{k}' takes no value, got '{item}'")
                    elif not has_eq or v in ("", '""'):
                        fail(f"twrp line {n}: flag '{k}' needs a value")
                    elif rule == "bool01" and v not in ("0", "1"):
                        fail(f"twrp line {n}: flag '{k}' must be 0 or 1, got '{v}'")
                    elif rule == "text" and not (len(v) > 2 and v[0] == v[-1] == '"'):
                        fail(f"twrp line {n}: flag '{k}' must be non-empty quoted text, got '{v}'")
                    elif rule == "word" and not re.fullmatch(r"\w+", v):
                        fail(f"twrp line {n}: flag '{k}' has invalid value '{v}'")
                    e["flags"][k] = v.strip('"')
            else:
                fail(f"twrp line {n}: unrecognised field '{t}'")
        out.append(e)
    return out


def dupes(entries, key, label):
    seen = {}
    for e in entries:
        if e[key] in seen:
            fail(f"{label}: duplicate {key} {e[key]} (lines {seen[e[key]]} and {e['line']})")
        seen[e[key]] = e["line"]


def main():
    stock_rec, stock_boot, parts_file, twrp_file = sys.argv[1:5]
    srec = parse_stock(stock_rec)
    sboot = {e["dev"]: e for e in parse_stock(stock_boot)}
    tw = parse_twrp(twrp_file)
    parts = {l.strip() for l in open(parts_file) if l.strip() and not l.startswith("#")}

    for entries, label in ((srec, "stock recovery"), (tw, "twrp")):
        dupes(entries, "dev", label)
        dupes(entries, "mnt", label)

    twd = {e["dev"]: e for e in tw}
    for s in srec:
        t = twd.get(s["dev"])
        if not t:
            fail(f"missing stock entry {s['dev']} ({s['mnt']})")
            continue
        want_mnt = ALLOWED_RENAMES.get(s["mnt"], s["mnt"])
        if t["mnt"] != want_mnt:
            fail(f"{s['dev']}: mount point {t['mnt']}, expected {want_mnt}")
        if t["fs"] != s["fs"]:
            fail(f"{s['dev']}: filesystem {t['fs']}, stock {s['fs']}")
        m = re.search(r"length=(-?\d+)", s["opts"])
        if (m.group(1) if m else None) != t["length"]:
            fail(f"{s['dev']}: length {t['length']}, stock {m.group(1) if m else None}")
        note = f"  (renamed from {s['mnt']})" if t["mnt"] != s["mnt"] else ""
        print(f"OK     {t['mnt']:13s} {t['fs']:5s} {s['dev']}{note}")

    stock_devs = {s["dev"] for s in srec}
    for t in tw:
        if t["dev"] not in stock_devs:
            fail(f"extra entry not in stock recovery fstab: {t['dev']} ({t['mnt']})")
        for dev in filter(None, (t["dev"], t["alt"])):
            if dev.startswith(BYNAME) and dev[len(BYNAME):] not in parts:
                fail(f"{dev}: partition name not present on the tablet")
            if not dev.startswith(BYNAME) and not re.fullmatch(r"/dev/block/mmcblk1(p1)?", dev):
                fail(f"{dev}: unexpected device path")
        if t["alt"] and not t["dev"].startswith(t["alt"] + "p"):
            fail(f"{t['mnt']}: alternate device {t['alt']} is not the parent of {t['dev']}")
        elif t["alt"]:
            print(f"OK     {t['mnt']:13s} alternate device {t['alt']} is parent of {t['dev']}")

    # /data encryption footer, cross-checked against the stock boot fstab
    data = next((t for t in tw if t["mnt"] == "/data"), None)
    boot_data = sboot.get(data["dev"]) if data else None
    m = re.search(r"encryptable=(\w+)", boot_data["opts"]) if boot_data else None
    want = m.group(1) if m else None
    if not data or data["flags"].get("encryptable") != want:
        fail(f"/data: encryptable={data['flags'].get('encryptable') if data else None}, stock boot fstab has {want}")
    else:
        print(f"OK     /data         length={data['length']} encryptable={want} (stock recovery + stock boot)")

    print("RESULT: " + ("ALL CHECKS PASSED" if not errors else f"{len(errors)} PROBLEM(S)"))
    sys.exit(1 if errors else 0)


if __name__ == "__main__":
    main()
