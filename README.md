# Galaxy Watch8 Classic: hybrid AOD/digital WFF proof of concept (GitHub CI)

**Status: project structure tested locally, GitHub Actions workflow prepared but NOT run, no Android APK compilation or device verification yet.**

This edition is **repository-safe by default**: it contains WFF XML, Gradle sources, image-generation scripts, and an official-validator + APK-compilation workflow. It intentionally contains **no pre-rendered images** or Samsung APK files. The workflow generates **original generic placeholders**, not Samsung artwork.

## What GitHub Actions tests

1. Generate original generic digits, dial ticks, and hands.
2. Check XML structure, image references, AOD/awake logic (`scripts/verify_project.py`).
3. Build Google's upstream WFF validator and validate `watchface.xml` against WFF **version 2**.
4. Install Android SDK 35, run Gradle `:watchface:assembleDebug`.
5. Attach `watchface-debug.apk` to the workflow run (generic placeholders only).

The action workflow lives in `.github/workflows/build.yml` and runs on `main` pushes, pull requests, and manually via **Actions > Validate and build generic WFF APK > Run workflow**. It does not upload to Google Play.

## Using this on GitHub

Create a repository, upload all files from **this folder** at the repository root, and push to `main`. Open the `Actions` tab. If the workflow passes, use the run page's **Artifacts** panel to retrieve `generic-hybrid-watchface-debug`. Note that GitHub zips workflow artifacts for download; unzip to get the APK.

The first CI run may fail and expose a WFF validator, Gradle, or Android resource problem. The workflow has **not** been executed on GitHub and therefore is not evidence of successful compilation. Fix issues based on the run logs.

## For Samsung artwork: local only

Do not upload proprietary APKs or extracted images to the repo. Locally, on a system with Python and Pillow:

```powershell
py -m pip install Pillow lxml
py scripts/prepare_assets.py --heritage "C:\path\HeritageClassic.apk" --digital "C:\path\MinimalDigital.apk"
py scripts/verify_project.py
```

The `.gitignore` excludes generated images and all APKs, but **check `git status` before every push**. Compile the locally extracted version using Android Studio, rather than publishing the derived imagery in GitHub Actions.

To restore public-safe placeholders:

```powershell
py scripts/prepare_assets.py
```

See `COPYRIGHT.md` for legal boundaries. The watch face is a third-party new package, not a modified Samsung-signed package. Wear OS 5+ WFF 2 intended. It has not been validated on Watch8 Classic hardware.

References:
- Official Android WFF: https://developer.android.com/training/wearables/wff
- Official validator: https://github.com/google/watchface/tree/main/third_party/wff
- GitHub CI Gradle: https://github.com/gradle/actions
