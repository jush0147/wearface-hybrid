#!/usr/bin/env bash
set -euo pipefail
mkdir -p emulator-results
APK="watchface/build/outputs/apk/debug/watchface-debug.apk"
PACKAGE="dev.local.wear.hybridface"

adb wait-for-device
for i in $(seq 1 36); do
  if [ "$(adb shell getprop sys.boot_completed | tr -d '\r')" = "1" ]; then break; fi
  sleep 5
done
printf 'Device: %s\nAPI: %s\n' "$(adb devices -l)" "$(adb shell getprop ro.build.version.sdk)" > emulator-results/device.txt
adb shell wm size >> emulator-results/device.txt
adb shell wm density >> emulator-results/device.txt
adb install -r "$APK"
adb shell pm path "$PACKAGE" | tee emulator-results/installed-package.txt

# sys.boot_completed does not imply Wear OS watch-face services are ready.
sleep 25
for i in $(seq 1 8); do
  adb shell input keyevent KEYCODE_WAKEUP
  adb shell am broadcast \
    -a com.google.android.wearable.app.DEBUG_SURFACE \
    --es operation set-watchface --es watchFaceId "$PACKAGE" \
    > emulator-results/set-watchface.txt
  adb shell am broadcast \
    -a com.google.android.wearable.app.DEBUG_SYSUI \
    --es operation show-watchface \
    > emulator-results/show-watchface.txt
  sleep 15
  adb exec-out screencap -p > emulator-results/interactive.png
  if python scripts/check_emulator_screen.py emulator-results/interactive.png --mode interactive; then
    echo "Interactive watch face detected on attempt $i" | tee emulator-results/interactive-status.txt
    break
  fi
  echo "Watch face not yet visible on attempt $i" | tee -a emulator-results/interactive-status.txt
done

adb shell settings put secure doze_enabled 1 || true
adb shell input keyevent KEYCODE_SLEEP
sleep 12
adb exec-out screencap -p > emulator-results/ambient.png
adb shell input keyevent KEYCODE_WAKEUP
sleep 8
adb exec-out screencap -p > emulator-results/wake-again.png

adb shell settings get secure doze_enabled > emulator-results/doze-setting.txt || true
adb shell dumpsys power > emulator-results/power-state.txt || true
adb logcat -d -t 1200 > emulator-results/logcat-tail.txt || true

failure=0
python scripts/check_emulator_screen.py emulator-results/interactive.png --mode interactive --save-report emulator-results/interactive-report.txt || failure=1
python scripts/check_emulator_screen.py emulator-results/ambient.png --mode ambient --save-report emulator-results/ambient-report.txt || failure=1
python scripts/check_emulator_screen.py emulator-results/wake-again.png --mode interactive --save-report emulator-results/wake-report.txt || failure=1
if [ "$failure" -ne 0 ]; then
  echo "Screen checks failed: inspect captured images and emulator logs." >&2
  exit 1
fi
