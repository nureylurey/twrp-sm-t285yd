# TWRP-only product for Samsung Galaxy J Max (SM-T285YD), board revision 4.
$(call inherit-product, $(SRC_TARGET_DIR)/product/full_base_telephony.mk)
$(call inherit-product, vendor/omni/config/common.mk)

PRODUCT_DEVICE := gtexsltedd
PRODUCT_NAME := omni_gtexsltedd
PRODUCT_BRAND := samsung
PRODUCT_MODEL := SM-T285YD
PRODUCT_MANUFACTURER := samsung

# Report the same device identity as stock (ro.product.device=gtexslteswa).
PRODUCT_BUILD_PROP_OVERRIDES += \
    TARGET_DEVICE=gtexslteswa \
    PRODUCT_NAME=gtexsltedd
