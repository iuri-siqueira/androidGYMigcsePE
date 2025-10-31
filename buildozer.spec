 [app]
  title = IGCSE GYM
  package.name = gymtracker
  package.domain = com.fitness.gymtracker
  source.dir = .
  source.include_exts = py,png,jpg,kv,atlas,json
  version = 2.0.0
  source.main = main_android.py

  requirements = python3,kivy==2.3.0,xlsxwriter,android

  presplash.filename = %(source.dir)s/assets/presplash.png
  icon.filename = %(source.dir)s/assets/icon.png
  orientation = portrait
  fullscreen = 0

  android.presplash_color = #46008B
  # Updated permissions for Android 13+ (API 33)
  # Using MANAGE_EXTERNAL_STORAGE for full storage access (required for Downloads folder)
  android.permissions = INTERNET,MANAGE_EXTERNAL_STORAGE,WRITE_EXTERNAL_STORAGE,READ_EXTERNAL_STORAGE
  android.api = 33
  android.minapi = 21
  android.ndk = 25b
  android.sdk = 33
  android.build_tools_version = 33.0.2
  android.archs = arm64-v8a,armeabi-v7a
  android.enable_androidx = True

  # Request legacy external storage for better compatibility
  android.manifest.application_request_legacy_external_storage = True

  # Add meta-data for storage access
  android.add_src = java

  # Additional Gradle configuration for modern Android
  android.gradle_dependencies = androidx.appcompat:appcompat:1.6.1,androidx.core:core:1.12.0

  p4a.branch = develop
  p4a.bootstrap = sdl2

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
