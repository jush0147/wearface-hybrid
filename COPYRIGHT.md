# Content and copyright handling

This repository is designed to store **only project source code**. It is **not** a repository of Samsung watch faces, licensed graphical content, or extracted APK resources.

- No Samsung APKs, texture sprites, logos, extracted code, dial screenshots or rendered previews based on Samsung artwork should be committed, uploaded as Actions artifacts, or attached to releases.
- The default GitHub Actions workflow **always calls `python scripts/prepare_assets.py` without arguments**, which generates original generic drawings for compilation and schema verification. GitHub Actions artifacts therefore contain only the generic test art.
- The `prepare_assets.py --heritage ... --digital ...` mode is reserved for local analysis using independently obtained copies. Legal permission to reverse engineer, modify, reproduce, distribute, or upload copyrighted images depends on applicable terms and law; private/noncommercial use is not a universal exception.
- A `.gitignore` helps prevent accidental commits but cannot prevent `git add -f` or uploads by other methods. Check `git status` before pushing.
- Do not assume that the debug APK built by Actions contains the Samsung look: it intentionally does not.

If you want to publish a distributable face, use artwork you created or have permission to distribute, and consult the relevant trademark/licensing terms as appropriate.
