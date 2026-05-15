
[app]
title = IR Vision
package.name = irvision
package.domain = org.test
source.dir = .
source.include_exts = py,png,jpg,kv,atlas
version = 1.0
requirements = python3,kivy,pillow,android
android.permissions = CAMERA
icon.filename = icon.png
orientation = portrait
osx.python_version = 3
osx.kivy_version = 2.2.0

[buildozer]
log_level = 2
warn_on_root = 1
