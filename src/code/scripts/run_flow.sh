#!/usr/bin/env bash
# Usage: ./run_flow.sh session01 com.instagram.android
SESSION=$1
APP_PKG=${2:-com.instagram.android}

# 1) Ensure device connected & authorized
adb devices

# 2) Launch app manually once or let script launch
adb shell monkey -p $APP_PKG -c android.intent.category.LAUNCHER 1
sleep 2

# 3) Dump UI to /sdcard/window_dump.xml and pull to host
adb shell uiautomator dump /sdcard/ui.xml
adb pull /sdcard/ui.xml ./ui.xml

# 4) Run calibration: find node centers for "Reels" and bottom nav estimate
./calibrate_ui.py ui.xml "Reels"

# 5) Run automation
./scripts/adb_automation.sh $SESSION $APP_PKG
