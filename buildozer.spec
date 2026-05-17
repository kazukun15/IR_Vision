
[app]
title = IR Vision
package.name = irvision
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0

# Android実機動作を支える厳密な要件
requirements = python3==3.10.11,kivy==2.2.1,pillow,pyjnius,sdl2

android.permissions = CAMERA
icon.filename = icon.png
orientation = portrait
fullscreen = 0

# Android 16耐性とNDKバージョンの黄金比
android.api = 33
android.minapi = 24
android.sdk = 33
android.ndk = 25b
android.target_sdk_version = 34
android.accept_sdk_license = True

# python-for-android 最新ブランチの確保
p4a.branch = master

[buildozer]
log_level = 2
warn_on_root = 1
