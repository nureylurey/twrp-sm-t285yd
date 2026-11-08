#!/usr/bin/env python3
"""
Pack a recovery image for SM-T285YD using the exact header layout of the
stock ARD3 recovery.img (Android boot image v0 + Samsung/Spreadtrum dt section).

Inputs are never modified. Standard library only.

  pack_recovery.py --kernel K --ramdisk R --dt D --out OUT [--seandroid] [--id-from STOCK]

Layout (all values copied from stock ARD3 recovery.img):
  page size        2048
  kernel_addr      0x00008000
  ramdisk_addr     0x01000000
  second_addr      0x00f00000  (second size 0)
  tags_addr        0x00000100
  cmdline          "console=ttyS1,115200n8"
  sections         header | kernel | ramdisk | dt   (each padded to page size)

--seandroid appends the 16-byte "SEANDROIDENFORCE" marker only. Samsung's real
trailer also carries a signature we cannot produce; the bootloader's reaction
to an unsigned image is UNTESTED.
"""
import argparse, hashlib, struct, sys

PAGE = 2048
KERNEL_ADDR, RAMDISK_ADDR, SECOND_ADDR, TAGS_ADDR = 0x00008000, 0x01000000, 0x00f00000, 0x00000100
CMDLINE = b"console=ttyS1,115200n8"
PARTITION_SIZE = 16777216  # RECOVERY partition, from /proc/partitions (16384 KB)


def pad(b):
    return b + b"\0" * ((-len(b)) % PAGE)


def build(kernel, ramdisk, dt, image_id=None):
    if image_id is None:
        # AOSP v0 id: SHA-1 over each section followed by its size (second is empty).
        h = hashlib.sha1()
        for blob in (kernel, ramdisk, b""):
            h.update(blob); h.update(struct.pack("<I", len(blob)))
        if dt:
            h.update(dt); h.update(struct.pack("<I", len(dt)))
        image_id = h.digest()
    hdr = bytearray(PAGE)
    hdr[0:8] = b"ANDROID!"
    struct.pack_into("<10I", hdr, 8, len(kernel), KERNEL_ADDR, len(ramdisk), RAMDISK_ADDR,
                     0, SECOND_ADDR, TAGS_ADDR, PAGE, len(dt), 0)
    hdr[64:64 + len(CMDLINE)] = CMDLINE
    hdr[576:576 + len(image_id)] = image_id
    return bytes(hdr) + pad(kernel) + pad(ramdisk) + pad(dt)


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--kernel", required=True)
    ap.add_argument("--ramdisk", required=True)
    ap.add_argument("--dt", required=True)
    ap.add_argument("--out", required=True)
    ap.add_argument("--seandroid", action="store_true")
    ap.add_argument("--id-from", help="copy the 32-byte id field from this image (for round-trip tests)")
    a = ap.parse_args()
    k, r, d = (open(p, "rb").read() for p in (a.kernel, a.ramdisk, a.dt))
    image_id = open(a.id_from, "rb").read()[576:608] if a.id_from else None
    img = build(k, r, d, image_id)
    if a.seandroid:
        img += b"SEANDROIDENFORCE"
    if len(img) > PARTITION_SIZE:
        sys.exit(f"ERROR: image {len(img)} bytes exceeds RECOVERY partition {PARTITION_SIZE}")
    open(a.out, "wb").write(img)
    for label, blob in (("kernel", k), ("ramdisk", r), ("dt", d), ("image", img)):
        print(f"{label:8s} {len(blob):>9}  sha256={hashlib.sha256(blob).hexdigest()}")
    print(f"free in RECOVERY partition: {PARTITION_SIZE - len(img)} bytes")


if __name__ == "__main__":
    main()
