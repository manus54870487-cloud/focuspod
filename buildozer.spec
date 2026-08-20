[app]
title = FocusPods
package.name = focuspods
package.domain = org.example
source.dir = .
source.include_exts = py,png,jpg,kv,atlas,wav,ttf
version = 1.0
requirements = python3,kivy==2.3.1
orientation = portrait
fullscreen = 0

[android]
permissions = INTERNET, VIBRATE, POST_NOTIFICATIONS
android.api = 30
android.sdk = 30
android.minapi = 21
android.ndk = 25b
android.arch = arm64-v8a
