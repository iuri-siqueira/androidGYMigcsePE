[app]

# (str) Title of your application
title = IGCSE GYM

# (str) Package name
package.name = igcsegym

# (str) Package domain (needed for android/ios packaging)
package.domain = com.igcse

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let python compile the source first)
source.include_exts = py,png,jpg,kv,atlas,json,txt

# (str) Application versioning (method 1)
version = 1.1

# (str) Application main entry point
source.main = main_android.py

# (list) Application requirements
# xlsxwriter is pure Python - no C compilation needed
# Let p4a master use its default Python 3.10.x version
requirements = python3,kivy==2.3.0,xlsxwriter

# (str) Custom source dirs for requirements
# requirements.source.kivy = ../../kivy

# (str) Presplash of the application
presplash.filename = %(source.dir)s/assets/presplash.png

# (str) Icon of the application
icon.filename = %(source.dir)s/assets/icon.png

# (str) Supported orientation (landscape, sensorLandscape, portrait or all)
orientation = portrait

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (list) Permissions
# Android 15 / Xiaomi HyperOS compatible permissions
# Modern approach: READ_MEDIA_* for Android 13+, legacy for older versions
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET,MANAGE_EXTERNAL_STORAGE,READ_MEDIA_IMAGES,READ_MEDIA_VIDEO,READ_MEDIA_AUDIO

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
android.minapi = 21

# (str) Android NDK version to use
# Leave blank to auto-download or use system NDK
android.ndk = 25b
android.ndk_path =

# (bool) Use --private data storage (True) or --dir public storage (False)
android.private_storage = True

# (list) The Android archs to build for
# arm64-v8a is the modern 64-bit ARM architecture
android.archs = arm64-v8a

# (bool) enables Android auto backup feature (Android API >=23)
android.allow_backup = True

# (str) XML file for Android backup rules
# android.backup_rules =

# (bool) Copy library instead of making a libpymodules.so
android.copy_libs = 1

# (str) The format used to package the app for release mode (aab or apk).
# android.release_artifact = aab
android.release_artifact = apk

# (str) The format used to package the app for debug mode (apk or aar).
android.debug_artifact = apk

# (list) Gradle dependencies to add
android.gradle_dependencies =

# (bool) Enable AndroidX support
android.enable_androidx = True

# (list) add java compile options
# android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

# (list) Gradle repositories to add {can be necessary for some android.gradle_dependencies}
# android.gradle_repositories =

# (list) Java classes to add as activities to the manifest.
# android.add_activities = com.example.ExampleActivity

# (str) OUYA Console category. Should be one of GAME or APP
# If you leave this blank, OUYA support will not be enabled
# android.ouya.category = GAME

# (str) Filename of OUYA Console icon. It must be a 732x412 png image.
# android.ouya.icon.filename = %(source.dir)s/data/ouya_icon.png

# (str) XML file to include as an intent filters in <activity> tag
# android.manifest.intent_filters =

# (str) launchMode to set for the main activity
android.manifest.launch_mode = standard

# (list) Android additional libraries to copy into libs/armeabi
# android.add_libs_armeabi = libs/android/*.so

# (bool) Indicate whether the screen should stay on
# Don't forget to add the WAKE_LOCK permission if you set this to True
# android.wakelock = False

# (list) Android application meta-data to set (key=value format)
android.meta_data = com.google.android.gms.version=12451000

# (str) Android manifest attributes
# Request legacy external storage for Android 10 (API 29) compatibility
android.manifest.application_attrs = android:requestLegacyExternalStorage="true"

# (list) Android additional features
# android.features = android.hardware.usb.host

# (str) Android logcat filters to use
# android.logcat_filters = *:S python:D

# (bool) Android logcat only display log for activity's pid
# android.logcat_pid_only = False

# (str) Android additional adb arguments
# android.adb_args = -H host.docker.internal

# (bool) Copy library instead of making a libpymodules.so
# android.no_compile_pyo = True

# (str) The Android arch to build for, choices: armeabi-v7a, arm64-v8a, x86, x86_64
# In the case of multiple archs, separate them with a comma: armeabi-v7a,arm64-v8a
# android.arch = arm64-v8a

#
# Python for android (p4a) specific
#

# (str) python-for-android fork to use, defaults to upstream (kivy)
# p4a.fork = kivy

# (str) python-for-android branch to use, defaults to master
# Using master for Python 3.10 compatibility (develop has issues)
p4a.branch = master

# (str) python-for-android git clone directory (if empty, it will be automatically cloned from github)
# p4a.source_dir =

# (str) The directory in which python-for-android should look for your own build recipes (if any)
# p4a.local_recipes =

# (str) Filename to the hook for p4a
# p4a.hook =

# (str) Bootstrap to use for android builds
# Run `buildozer android p4a -- bootstraps` for a list of valid bootstraps
# p4a.bootstrap = sdl2
p4a.bootstrap = sdl2

# (int) port number to specify an explicit --port= p4a argument (eg for bootstrap flask)
# p4a.port =

# (str) extra command line arguments to pass when invoking pythonforandroid.toolchain
# p4a.extra_args =

#
# iOS specific
#

# (str) Path to a custom kivy-ios folder
# ios.kivy_ios_dir = ../kivy-ios

# (str) Name of the certificate to use for signing the debug version
# ios.codesign.debug = "iPhone Developer: <lastname> <firstname> (<hexstring>)"

# (str) Name of the certificate to use for signing the release version
# ios.codesign.release = %(ios.codesign.debug)s

#
# Buildozer
#

# (int) Log level (0 = error only, 1 = info, 2 = debug (with command output))
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
# bin_dir = ./bin

#
# Advanced options
#

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
android.skip_update = False

# (bool) If True, then automatically accept SDK license
# agreements. This is intended for automation only. If set to False,
# the default, you will be shown the license when first running
# buildozer.
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
# android.entrypoint = org.kivy.android.PythonActivity

# (str) Full name including package path of the Java class that implements Python Service
# android.service_class_name = org.kivy.android.PythonService

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
# android.whitelist =

# (str) Path to a custom whitelist file
# android.whitelist_src =

# (str) Path to a custom blacklist file
# android.blacklist_src =

# (bool) If True, then skip trying to update the Android NDK
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you just want to test/build your package
# android.skip_update = False
