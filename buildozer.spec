

[app]

# (str) Title of your application
title = ExpenseTracker

# (str) Package name
package.name = expense_tracker

# (str) Package domain (needed for android/ios packaging)
package.domain = org.example

# (str) Source code where the main.py live
source.dir = .

# (list) Source files to include (let empty to include all the files)
source.include_exts = py,png,jpg,kv,json,mo,po,pot

# (list) List of inclusions using pattern matching
source.include_patterns = locales/*

# (list) Source files to exclude (let empty to not exclude anything)
#source.exclude_exts = spec

# (list) List of directory to exclude (let empty to not exclude anything)
#source.exclude_dirs = tests, bin

# (list) List of exclusions using pattern matching
#source.exclude_patterns = license,images/*/*.jpg

# (str) Application versioning (method 1)
version = 1.0

# (str) Application versioning (method 2)
# version.regex = __version__ = ['"](.*)['"]
# version.filename = %(source.dir)s/main.py

# (list) Application requirements
# comma separated e.g. requirements = sqlite3,kivy
requirements = python3==3.9.17,hostpython3==3.9.17,kivy,kivymd==1.1.1,tinydb

# (str) Custom source folders for requirements
# Sets custom source for any requirements with recipes
# requirements.source.kivy = ../../kivy

# (list) Garden requirements
#garden_requirements =

# (str) Presplash of the application
#presplash.filename = %(source.dir)s/data/presplash.png

# (str) Icon of the application
#icon.filename = %(source.dir)s/data/icon.png

# (str) Supported orientation (one of landscape, sensorLandscape, portrait or all)
orientation = portrait

# (list) List of service to declare
#services = NAME:ENTRYPOINT_TO_PY,NAME2:ENTRYPOINT2_TO_PY

#
# OSX Specific
#

#
# author = © Copyright Info

# change the major version if you make significant changes
osx.majorver = 1

#
# Android specific
#

# (bool) Indicate if the application should be fullscreen or not
fullscreen = 0

# (string) Presplash background color (for new android toolchain)
# Supported formats are: #RRGGBB #AARRGGBB or one of the following names:
# red, blue, green, black, white, gray, cyan, magenta, yellow, lightgray,
# darkgray, grey, lightgrey, darkgrey, aqua, fuchsia, lime, maroon, navy,
# olive, purple, silver, teal.
#android.presplash_color = #FFFFFF

# (list) Permissions
#android.permissions = INTERNET

# (int) Target Android API, should be as high as possible.
android.api = 33

# (int) Minimum API your APK will support.
#android.minapi = 21

# (int) Android SDK version to use
#android.sdk = 20

# (str) Android NDK version to use
android.ndk = 25b

# (bool) Use --private data embedding for apk
#android.private_storage = True

# (str) Android NDK directory (if empty, it will be automatically downloaded.)
#android.ndk_path =

# (str) Android SDK directory (if empty, it will be automatically downloaded.)
#android.sdk_path =

# (str) ANT directory (if empty, it will be automatically downloaded.)
#android.ant_path =

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you know that your specific version of the
# Android sdk has been successfully tested with your build pipeline.
# This option is only available when using the "android_old" target.
#android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements. This is intended for automation only.
# If set to False, the default, you will be shown the license when first running buildozer.
android.accept_sdk_license = True

# (str) Android entry point, default is ok for Kivy-based app
#android.entrypoint = org.renpy.android.PythonActivity

# (str) Android app theme, default is ok for Kivy-based app
# android.apptheme = "@android:style/Theme.NoTitleBar"

# (list) Pattern to whitelist for the whole project
#android.whitelist =

# (str) Path to a custom whitelist file
#android.whitelist_src =

# (str) Path to a custom blacklist file
#android.blacklist_src =

# (list) List of Java .jar files to add to the libs so that pyjnius can access
# their classes. Don't add jars that you do not need, since extra jars can slow
# down the build process. Allows wildcards matching, for example:
# OUYA-ODK/libs/*.jar
#android.add_jars = foo.jar,bar.jar,path/to/more/*.jar

# (list) List of Java files to add to the android project (can be java or a
# directory containing the files)
#android.add_src =

# (list) Android AAR archives to add (currently works only with sdl2_gradle
# bootstrap)
#android.add_aars =

# (list) Gradle dependencies to add (currently works only with sdl2_gradle
# bootstrap)
#android.gradle_dependencies =

# (list) add java compile options
# this can for example be necessary when importing certain java libraries using the 'android.gradle_dependencies' option
# see https://developer.android.com/studio/write/java8-support for further information
# android.add_compile_options = "sourceCompatibility = 1.8", "targetCompatibility = 1.8"

# (list) Gradle repositories to add {can be necessary for some android.gradle_dependencies}
# please enclose in double quotes 
# e.g. android.gradle_repositories = "maven { url 'https://kotlin.bintray.com/ktor' }"
#android.add_gradle_repositories =

# (list) packaging options to add 
# see https://developer.android.com/studio/build/shrink-code#packaging-dalvikdex
#android.add_packaging_options =

# (list) Android archs to build for (only applicable for android_new target)
# This should be a comma-separated list using one or more of: armeabi-v7a, arm64-v8a, x86, x86_64
android.archs = arm64-v8a

# (bool) If True, then skip trying to update the Android sdk
# This can be useful to avoid excess Internet downloads or save time
# when an update is due and you know that your specific version of the
# Android sdk has been successfully tested with your build pipeline.
# This option is only available when using the "android_old" target.
#android.skip_update = False

# (bool) If True, then automatically accept SDK license agreements. This is intended for automation only.
#android.accept_sdk_license = True

[buildozer]

# (int) Log level (0 = error only, 1 = info, 2 = debug)
log_level = 2

# (int) Display warning if buildozer is run as root (0 = False, 1 = True)
warn_on_root = 1

# (str) Path to build artifact storage, absolute or relative to spec file
# build_dir = ./.buildozer

# (str) Path to build output (i.e. .apk, .ipa) storage
# bin_dir = ./bin

#    -----------------------------------------------------------------------------
#    List as sections
#
#    You can define all the "list" as [section:key].
#    Each line will be considered as a option to the list.
#    Let's take [app] package_whitelist = devteam, github
#
#    Which is equivalent to [app] package_whitelist = devteam
github
#
#    -----------------------------------------------------------------------------

# (str) Permissions
# (See https://developer.android.com/reference/android/Manifest.permission.html)
#android.permissions = INTERNET, ACCESS_NETWORK_STATE

# (str) Requirements
#requirements = kivy, python3

# (str) Entry point
#android.entrypoint = org.kivy.android.PythonActivity

# (str) Bootstrap
#android.bootstrap = sdl2

# (str) Icon
#icon.filename = icon.png

# (str) Presplash
#presplash.filename = presplash.png

# (str) Distribution name
#android.distribution_name = kivy

# (str) Distribution title
#android.distribution_title = Kivy Distribution

# (str) Distribution version
#android.distribution_version = 1.0

# (str) Repository URL
#android.repository_url = https://github.com/kivy/python-for-android

# (str) Repository branch
#android.repository_branch = master

# (str) Recipe directory
#android.recipe_dir =

# (str) Local recipe directory
#android.local_recipes =

# (str) Android NDK version
#android.ndk = 23b

# (str) Android API level
#android.api = 31

# (str) Android SDK version
#android.sdk = 20

# (str) Android NDK directory
#android.ndk_path =

# (str) Android SDK directory
#android.sdk_path =

# (str) ANT directory
#android.ant_path =

# (str) Java key store
#android.keystore =

# (str) Java key alias
#android.keyalias =

# (str) Java key store password
#android.keypass =

# (str) Java key alias password
#android.keyaliaspass =

# (str) Orientation
#android.orientation = portrait

# (str) Fullscreen
#android.fullscreen = 0

# (str) Theme
#android.theme = @android:style/Theme.NoTitleBar

# (str) Presplash color
#android.presplash_color = #FFFFFF

# (str) Private storage
#android.private_storage = True

# (str) Whitelist
#android.whitelist =

# (str) Blacklist
#android.blacklist =

# (str) Whitelist source
#android.whitelist_src =

# (str) Blacklist source
#android.blacklist_src =

# (str) Add jars
#android.add_jars =

# (str) Add src
#android.add_src =

# (str) Add aars
#android.add_aars =

# (str) Gradle dependencies
#android.gradle_dependencies =

# (str) Add compile options
#android.add_compile_options =

# (str) Add gradle repositories
#android.add_gradle_repositories =

# (str) Add packaging options
#android.add_packaging_options =

# (list) Archs
#android.archs = arm64-v8a

# (str) Skip update
#android.skip_update = False

# (str) Accept SDK license
#android.accept_sdk_license = False

# (str) Entry point
#android.entrypoint = org.kivy.android.PythonActivity

# (str) App theme
#android.apptheme = @android:style/Theme.NoTitleBar