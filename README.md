# TWRP for Samsung Galaxy J Max (SM-T285YD) — review draft

**For SM-T285YD only** (`ro.product.device=gtexslteswa`, `ro.product.name=gtexsltedd`,
`ro.revision=4`). Not for SM-T285 or SM-T285Y: their board description has no
revision-4 entry.

Status: **configuration for review (v3). Not built, not tested, not flashed.**

## What is stock and what is new

| Part | Source | Verified |
|---|---|---|
| Kernel | Stock ARD3 `recovery.img`, unmodified | SHA-256 `379a1551…e154` (`HASHES.sha256`, checked by the workflow) |
| Board description (dt) | Stock ARD3 `recovery.img`, unmodified | SHA-256 `fb0b3c28…1745`; identical in stock boot and recovery |
| Image header layout | Copied from stock `recovery.img` | `tools/pack_recovery.py` re-creates stock recovery byte-for-byte (excluding Samsung's signed trailer) |
| Partition map | Derived from stock `/etc/recovery.fstab` | `tools/check_fstab.py` checks devices, mount points, filesystems, duplicates, tablet partition names, alternate device and `/data` `length=-16384` + `encryptable=footer`; also flag values (`backup=0/1`, non-empty `display`, no value on bare flags), duplicate flag keys and empty values. `tools/test_check_fstab.py` confirms the genuine fstab passes and 17 deliberate faults are each rejected for the expected reason. Both run in the workflow and must pass. |
| Recovery ramdisk | Built from TWRP `twrp-5.1` source | Not yet built |

## Why twrp-5.1

The stock kernel is SELinux **always-enforce** and the stock recovery uses SELinux
**policy version 26** (Android 5.1). A newer TWRP branch would ship a newer policy
format that this kernel may refuse, with no way to switch to permissive.
`sepolicy/recovery.te` marks only the recovery domain permissive.

## Workflow (manual trigger only)

- `test`: verifies the stock hashes, downloads the twrp-5.1 source, builds the
  Ubuntu 14.04/Java 7 environment and runs the configuration check. No compile.
  Purpose: confirm the runner's time and disk limits are sufficient.
- `build`: everything above, then compiles the recovery ramdisk, repacks it with the
  stock kernel and board description, and uploads `recovery.img`, an Odin
  `.tar.md5`, the full build log and SHA-256 sums.

## Verified against TWRP source (twrp-5.1 manifest → TeamWin recovery `android-9.0`)

- Alternate block device field (`/dev/block/mmcblk1`) is accepted in this v1 fstab format.
- `length=-16384` is only honoured when formatting if `encryptable=footer` is also set;
  both are set on `/data` (the flag comes from the stock boot fstab).
- `TW_INCLUDE_CRYPTO := false` keeps crypto off (only JB/L crypto flags force it on).
- `BOARD_HAS_FLIPPED_SCREEN := true` becomes `TW_ROTATION=180`; `ABGR_8888` is recognised.
- The Android 5.1 build system produces `ramdisk-recovery.img`; the workflow fails if it is missing.
- No Make assignment carries an inline comment or trailing whitespace.

## Known unknowns (not resolved by building)

1. **Secure download:** the image carries only the `SEANDROIDENFORCE` marker, not
   Samsung's signature. How the bootloader handles that on this tablet is untested.
   The first flash attempt is a risk to weigh, not a formality.
2. **Screen: UNVERIFIED.** Pixel format, both graphics flags and 180° rotation come from
   jedld's SM-T285 tree. Wrong values give a garbled, black or upside-down recovery screen.
3. **Brightness: UNVERIFIED.** Path and limits from jedld's tree; failure only affects the slider.
4. **Touch:** relies on the stock kernel's built-in Melfas driver; the YD-specific
   touch firmware reference is in the stock board description used here.
5. **Encryption state:** confirmed `unencrypted` on the tablet (`ro.crypto.state`, 2026-11-08),
   so `TW_INCLUDE_CRYPTO := false` is kept. Re-check if the tablet is ever encrypted.
6. **Build environment:** Ubuntu 14.04 package mirrors and the twrp-5.1 manifest
   must still work; the `test` run checks this.

## Restore route (must exist before any flash)

Verified stock firmware `…T285YDDDU0ARD3_…_NPL.zip`, SHA-256
`4A268EE8…AF4F6D`. Its AP file contains the stock `recovery.img`
(SHA-256 `9D59238B…DC393`), flashable with Odin.
