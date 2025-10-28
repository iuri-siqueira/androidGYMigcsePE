[app]
title = IGCSE GYM
package.name = gymtracker
package.domain = com.fitness.gymtracker
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,json
version = 1.0.0
source.main = main_android.py

# Proven stable requirements for Android builds
requirements = python3==3.9.16,kivy==2.1.0,openpyxl==3.0.10,cython==0.29.33

presplash.filename = %(source.dir)s/assets/presplash.png
icon.filename = %(source.dir)s/assets/icon.png
orientation = portrait
fullscreen = 0

# Conservative Android settings that work
android.presplash_color = #0A0A1E
android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
android.api = 29
android.minapi = 21
android.ndk = 23b
android.archs = armeabi-v7a

# Stable p4a configuration
p4a.branch = master
p4a.bootstrap = sdl2
p4a.local_recipes =

android.accept_sdk_license = True
android.skip_update = False

# Optimization settings
android.gradle_dependencies =
android.java_options = -Xms512m -Xmx2048m

[buildozer]
log_level = 2
warn_on_root = 1
build_dir = ./.buildozer
bin_dir = ./bin