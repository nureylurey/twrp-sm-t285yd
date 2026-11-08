# TWRP device configuration for SM-T285YD ONLY (codename gtexsltedd/gtexslteswa, board revision 4).
# Not for SM-T285 or SM-T285Y. Kernel and board description are the unmodified
# stock ARD3 images; see HASHES.md.

# Do not set LOCAL_PATH here: every Android makefile reuses that name, so a
# deferred reference to it would resolve to whichever makefile ran last.
DEVICE_PATH := device/samsung/gtexsltedd

# Platform (stock: ro.board.platform=sc8830, ro.product.board=SC9830I)
TARGET_ARCH := arm
TARGET_ARCH_VARIANT := armv7-a-neon
TARGET_CPU_ABI := armeabi-v7a
TARGET_CPU_ABI2 := armeabi
TARGET_CPU_VARIANT := cortex-a7
TARGET_BOARD_PLATFORM := sc8830
TARGET_BOOTLOADER_BOARD_NAME := SC9830I
TARGET_NO_BOOTLOADER := true
TARGET_NO_RADIOIMAGE := true

# Stock kernel, used as-is (no kernel is compiled)
TARGET_PREBUILT_KERNEL := $(DEVICE_PATH)/prebuilt/kernel
BOARD_KERNEL_CMDLINE := console=ttyS1,115200n8
BOARD_KERNEL_BASE := 0x00000000
BOARD_KERNEL_PAGESIZE := 2048
# The final image is repacked by tools/pack_recovery.py with the stock board
# description (prebuilt/dt.img) and the stock header layout.

# Partition sizes in bytes (from /proc/partitions on the tablet)
BOARD_BOOTIMAGE_PARTITION_SIZE := 16777216
BOARD_RECOVERYIMAGE_PARTITION_SIZE := 16777216
BOARD_SYSTEMIMAGE_PARTITION_SIZE := 2147483648
BOARD_CACHEIMAGE_PARTITION_SIZE := 209715200
BOARD_FLASH_BLOCK_SIZE := 131072
TARGET_USERIMAGES_USE_EXT4 := true
BOARD_HAS_LARGE_FILESYSTEM := true
BOARD_HAS_NO_MISC_PARTITION := true

# Recovery
TARGET_RECOVERY_FSTAB := $(DEVICE_PATH)/recovery.fstab
RECOVERY_VARIANT := twrp
RECOVERY_SDCARD_ON_DATA := true
BOARD_HAS_NO_SELECT_BUTTON := true
# ---------------------------------------------------------------------------
# DISPLAY: UNVERIFIED ON SM-T285YD. Copied from jedld's SM-T285 tree.
# Supporting evidence only: stock YD sets ro.sf.hwrotation=180 and lcd_density 240.
# Possible failure if wrong: upside-down, mirrored, garbled or black recovery screen.
# The tablet stays usable: Download Mode does not depend on these settings.
# UNVERIFIED
TARGET_RECOVERY_PIXEL_FORMAT := "ABGR_8888"
# UNVERIFIED
RECOVERY_GRAPHICS_FORCE_USE_LINELENGTH := true
# UNVERIFIED
RECOVERY_GRAPHICS_FORCE_SINGLE_BUFFER := true
# UNVERIFIED (rotation 180)
BOARD_HAS_FLIPPED_SCREEN := true
# ---------------------------------------------------------------------------

# TWRP
TW_THEME := portrait_hdpi
TW_HAS_DOWNLOAD_MODE := true
TW_NO_REBOOT_BOOTLOADER := true
TW_EXCLUDE_SUPERSU := true
# CRYPTO: off. Stock /data is expected to be unencrypted (check: adb shell getprop
# ro.crypto.state -> "unencrypted"). Decryption support would need Samsung's
# proprietary keymaster libraries, which are not in this tree. Without it TWRP
# cannot read an ENCRYPTED /data, but the stock encryption footer is still
# preserved when formatting because recovery.fstab sets encryptable=footer
# alongside length=-16384 (TWRP only honours length= when that flag is present).
TW_INCLUDE_CRYPTO := false
TW_INTERNAL_STORAGE_PATH := "/data/media/0"
TW_INTERNAL_STORAGE_MOUNT_POINT := "data"
TW_EXTERNAL_STORAGE_PATH := "/external_sd"
TW_EXTERNAL_STORAGE_MOUNT_POINT := "external_sd"
TW_DEFAULT_EXTERNAL_STORAGE := true
# BRIGHTNESS: UNVERIFIED ON SM-T285YD. Path copied from jedld's SM-T285 tree.
# Possible failure if wrong: brightness slider does nothing; the screen still works.
# Checkable read-only on stock: adb shell ls /sys/devices/ | findstr backlight
# UNVERIFIED
TW_BRIGHTNESS_PATH := "/sys/devices/gen-panel-backlight.29/backlight/panel/brightness"
# UNVERIFIED
TW_MAX_BRIGHTNESS := 255
# UNVERIFIED
TW_DEFAULT_BRIGHTNESS := 162

# SELinux: stock kernel is "always enforce" and uses policy version 26 (Android 5.1),
# which is why this tree targets the twrp-5.1 branch.
# Literal path on purpose: "+=" on a new variable defers expansion, so any variable
# here would be expanded later inside external/sepolicy/Android.mk (build #3 failed
# because $(LOCAL_PATH) became external/sepolicy at that point).
BOARD_SEPOLICY_DIRS += device/samsung/gtexsltedd/sepolicy
BOARD_SEPOLICY_UNION += recovery.te
