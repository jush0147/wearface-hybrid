#!/usr/bin/env bash
set -euo pipefail

mkdir -p emulator-results

APK="watchface/build/outputs/apk/debug/watchface-debug.apk"
PACKAGE="dev.local.wear.hybridface"

echo "Emulator: $(adb devices -l)"
echo "Android API: $(adb shell getprop ro.build.version.sdk)"
echo "Wear OS: $(adb shell getprop ro.build.version.release)"

adb install -r "$APK"
adb shell pm path "$PACKAGE" | tee emulator-results/installed-package.txt

# Google official WFF debugging interface selects a face by its package ID.
adb shell am broadcast \
  -a com.google.android.wearable.app.DEBUG_SURFACE \
  --es operation set-watchface \
  --es watchFaceId "$PACKAGE" \
  | tee emulator-results/set-watchface.txt
adb shell am broadcast \
  -a com.google.android.wearable.app.DEBUG_SYSUI \
  --es operation show-watchface \
  | tee emulator-results/show-watchface.txt

# The renderer may need a few seconds to initialize after switching.
adb shell input keyevent KEYCODE_WAKEUP
sleep 12
adb exec-out screencap -p > emulator-results/interactive.png

# AOD works only if the emulator system actually enables ambient mode.
# KEYCODE_SLEEP/WAKEUP are documented by Android for Wear OS testing.
adb shell settings put secure doze_enabled 1 || true
adb shell input keyevent KEYCODE_SLEEP
sleep 8
adb exec-out screencap -p > emulator-results/ambient.png

adb shell input keyevent KEYCODE_WAKEUP
sleep 4
adb exec-out screencap -p > emulator-results/wake-again.png

adb shell settings get secure doze_enabled > emulator-results/doze-setting.txt || true
adb shell dumpsys power > emulator-results/power-state.txt || true
adb logcat -d -t 800 > emulator-results/logcat-tail.txt || true

python - <<'PY'
from PIL import Image, ImageChops, ImageStat
from pathlib import Path
base=Path("emulator-results")
names=("interactive.png", "ambient.png", "wake-again.png")
images=[]
notes=[]
for name in names:
    p=base/name
    im=Image.open(p).convert("RGB")
    im.load()
    images.append(im)
    notes.append(f"{name}: {im.width}x{im.height}, mean brightness {ImageStat.Stat(im.convert('L')).mean[0]:.1f}")
if images[0].size==images[1].size:
    diff=ImageChops.difference(images[0],images[1])
    score=sum(ImageStat.Stat(diff).mean)/3
    notes.append(f"interactive/ambient mean RGB difference: {score:.2f}")
    if score<3:
        notes.append("WARNING: screenshots nearly identical; ambient mode may not have activated.")
    if ImageStat.Stat(images[1].convert("L")).mean[0]<1:
        notes.append("WARNING: ambient screenshot nearly black; check AOD configuration.")
else:
    notes.append("WARNING: screenshots have different sizes.")
notes.append("Screenshot differences alone do not prove the correct watch face is displayed. Inspect images and logs.")
(base/"report.txt").write_text("\n".join(notes)+"\n",encoding="utf-8")
print("\n".join(notes))
PY
