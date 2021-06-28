include $(THEOS)/makefiles/common.mk

BUNDLE_NAME = picnicprefs

picnicprefs_FILES = PNCRootListController.m
picnicprefs_INSTALL_PATH = /Library/PreferenceBundles
picnicprefs_FRAMEWORKS = UIKit CepheiPrefs
picnicprefs_PRIVATE_FRAMEWORKS = Preferences
picnicprefs_CFLAGS = -fobjc-arc

include $(THEOS_MAKE_PATH)/bundle.mk

internal-stage::
	$(ECHO_NOTHING)mkdir -p $(THEOS_STAGING_DIR)/Library/PreferenceLoader/Preferences$(ECHO_END)
	$(ECHO_NOTHING)cp entry.plist $(THEOS_STAGING_DIR)/Library/PreferenceLoader/Preferences/picnicprefs.plist$(ECHO_END)
