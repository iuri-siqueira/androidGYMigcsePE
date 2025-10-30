[app]
title = IGCSE GYM
package.name = igcsegym
package.domain = com.igcse
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
source.main = main_android.py

# Pure Python dependencies only - no C compilation needed
requirements = python3,kivy,xlsxwriter

# Assets
presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png

# Orientation
orientation = portrait
fullscreen = 0

# Android settings
android.presplash_color = #46008B
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET
android.api = 33
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a
android.accept_sdk_license = True
android.skip_update = False
android.release_artifact = apk
android.debug_artifact = apk

# Gradle settings
android.gradle_dependencies =

# Build settings - use develop branch for Python 3.11 compatibility
p4a.branch = develop
p4a.bootstrap = sdl2

[buildozer]
log_level = 2
warn_on_root = 1
