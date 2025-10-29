 [app]
  title = GYM
  package.name = gymtracker
  package.domain = com.fitness.gymtracker
  source.dir = .
  source.include_exts = py,png,jpg,kv,atlas,json
  version = 1.0.0
  source.main = main_android.py

  requirements = python3,kivy,openpyxl,et_xmlfile,jdcal

  presplash.filename = %(source.dir)s/assets/presplash.png
  icon.filename = %(source.dir)s/assets/icon.png
  orientation = portrait
  fullscreen = 0

  android.presplash_color = #0A0A1E
  android.permissions = WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
  android.api = 30
  android.minapi = 21
  android.ndk = 25b
  android.archs = arm64-v8a

  p4a.branch = master
  p4a.bootstrap = sdl2

  android.accept_sdk_license = True
  android.skip_update = False

  [buildozer]
  log_level = 2
  warn_on_root = 1
  build_dir = ./.buildozer
  bin_dir = ./bin
