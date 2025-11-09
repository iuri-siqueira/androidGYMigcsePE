[app]
title = IGCSE GYM
package.name = igcsegym
package.domain = com.igcse
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0
source.main = main_android.py

# Dependencies - using proven working versions for Android
# pyjnius is required for Kivy Android - using version that compiles correctly
requirements = python3==3.11.6,kivy==2.2.1,pyjnius==1.4.2,xlsxwriter

# Assets
presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png

# Orientation
orientation = portrait
fullscreen = 0

# Android settings - using tested, stable configuration
android.presplash_color = #46008B
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET
android.api = 31
android.minapi = 21
android.ndk = 25b
android.archs = arm64-v8a,armeabi-v7a
android.accept_sdk_license = True
android.gradle_dependencies =

# Build settings - using stable p4a release
p4a.branch = master
p4a.bootstrap = sdl2
p4a.local_recipes =

# Skip byte-compile for faster builds
android.no_byte_compile_python = True

[buildozer]
log_level = 2
warn_on_root = 1
android_new_toolchain = True
