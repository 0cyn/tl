TARGET := iphone:clang:latest:7.0
INSTALL_TARGET_PROCESSES = SpringBoard


include $(THEOS)/makefiles/common.mk

TWEAK_NAME = working

working_FILES = Tweak.x
working_CFLAGS = -fobjc-arc

include $(THEOS_MAKE_PATH)/tweak.mk
