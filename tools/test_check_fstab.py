#!/usr/bin/env python3
"""
Self-test for check_fstab.py. Read-only on the repository (mutations go to a temp dir).
1. The genuine fstab must PASS.
2. Every deliberately broken copy must FAIL, with the expected reason in the output.
Exit code 0 only if all expectations hold.
"""
import os, re, subprocess, sys, tempfile

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
FSTAB = os.path.join(ROOT, "device/samsung/gtexsltedd/recovery.fstab")
REFS = [os.path.join(ROOT, p) for p in (
    "reference/stock-recovery.fstab", "reference/stock-boot-fstab.sc8830",
    "reference/tablet-partitions.txt")]
CHECKER = os.path.join(ROOT, "tools/check_fstab.py")

# (description, regex substitution applied to the genuine file, text expected in output)
CASES = [
    ("missing encryptable on /data", (r"^(/data .*) flags=encryptable=footer", r"\1"), "encryptable=None"),
    ("wrong /data length", (r"^(/data .*)length=-16384", r"\1length=-4096"), "length -4096"),
    ("wrong filesystem", (r"^/efs(\s+)ext4", r"/efs\1vfat"), "filesystem vfat"),
    ("wrong mount point", (r"^/preload ", "/hidden  "), "expected /preload"),
    ("missing stock entry", (r"^/l_warm .*\n", ""), "missing stock entry"),
    ("extra entry", (r"\Z", "/extra ext4 /dev/block/platform/sdio_emmc/by-name/SBOOT\n"), "extra entry"),
    ("nonexistent partition", (r"by-name/pm_sys ", "by-name/pm_sysx "), "pm_sys"),
    ("wrong alternate device", (r"/dev/block/mmcblk1  flags", "/dev/block/mmcblk0  flags"), "unexpected device path"),
    ("unbalanced quote", (r'display="EFS";', 'display="EFS;'), "unbalanced quotes"),
    ("duplicate entry", (r"\Z", "/efs ext4 /dev/block/platform/sdio_emmc/by-name/efs\n"), "duplicate dev"),
    ("unknown flag", (r"backup=1", "bakup=1"), "unknown flag 'bakup'"),
    # Added in v3
    ("invalid flag value backup=banana", (r'(display="EFS");backup=1', r"\1;backup=banana"), "must be 0 or 1"),
    ("duplicate flag key", (r'(display="EFS");backup=1', r"\1;backup=1;backup=0"), "duplicate flag 'backup'"),
    ("empty flag value backup=", (r'(display="EFS");backup=1', r"\1;backup="), "flag 'backup' needs a value"),
    ("empty display text", (r'display="EFS"', 'display=""'), "flag 'display' needs a value"),
    ("value on bare flag", (r";storage;", ";storage=1;"), "takes no value"),
    ("empty encryptable value", (r"^(/data .*)encryptable=footer", r"\1encryptable="), "flag 'encryptable' needs a value"),
]


def run(path):
    r = subprocess.run([sys.executable, "-I", CHECKER, *REFS, path], capture_output=True, text=True)
    return r.returncode, r.stdout + r.stderr


def main():
    ok = True
    code, out = run(FSTAB)
    print(("PASS " if code == 0 else "FAIL ") + "genuine fstab passes the checker")
    ok &= code == 0
    original = open(FSTAB).read()
    with tempfile.TemporaryDirectory() as tmp:
        for desc, (pat, repl), expect in CASES:
            mutated, count = re.subn(pat, repl, original, count=1, flags=re.M)
            def entries(text):
                return [l for l in text.splitlines() if l.strip() and not l.lstrip().startswith("#")]
            if count == 0 or entries(mutated) == entries(original):
                print(f"FAIL {desc}: mutation did not change any fstab entry (test is broken)")
                ok = False
                continue
            path = os.path.join(tmp, "fstab")
            open(path, "w").write(mutated)
            code, out = run(path)
            caught = code != 0 and expect in out
            reason = next((l[7:] for l in out.splitlines() if l.startswith("FAIL   ")), "no failure reported")
            print(("PASS " if caught else "FAIL ") + f"{desc} is rejected -> {reason}")
            ok &= caught
    print("SELF-TEST: " + ("ALL PASSED" if ok else "PROBLEMS FOUND"))
    sys.exit(0 if ok else 1)


if __name__ == "__main__":
    main()
