INSTALL_TARGET_PROCESSES = SpringBoard

include $(THEOS)/makefiles/common.mk

TWEAK_NAME = picnic

picnic_FILES = Tweak.x
picnic_EXTRA_FRAMEWORKS = Cephei
picnic_CFLAGS = -fobjc-arc

include $(THEOS_MAKE_PATH)/tweak.mk
SUBPROJECTS += picnicprefs
include $(THEOS_MAKE_PATH)/aggregate.mk
