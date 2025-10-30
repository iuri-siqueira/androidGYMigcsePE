 [app]
  title = GYM
  package.name = gymtracker
  package.domain = com.fitness.gymtracker
  source.dir = .
  source.include_exts = py,png,jpg,kv,atlas,json
  version = 1.0.0
  source.main = main_android.py

  requirements = python3,kivy,xlsxwriter

  presplash.filename = %(source.dir)s/assets/presplash.png
  icon.filename = %(source.dir)s/assets/icon.png
  orientation = portrait
  fullscreen = 0

  android.presplash_color = #0A0A1E
  android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE,INTERNET
  android.api = 33
  android.minapi = 21
  android.ndk = 25b
  android.sdk = 33
  android.build_tools_version = 33.0.2
  android.archs = arm64-v8a,armeabi-v7a
  android.enable_androidx = True

  p4a.branch = develop
  p4a.bootstrap = sdl2

  android.gradle_dependencies =

  android.accept_sdk_license = True
  android.skip_update = False
  android.auto_backup = False
  android.backup_rules =

  android.release_artifact = apk
  android.debug_artifact = apk

  [buildozer]
  log_level = 2
  warn_on_root = 1
  build_dir = ./.buildozer
  bin_dir = ./bin
