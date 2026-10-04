# Native SWE-bench actor preparation

Dockerfile.swe-native layers the existing pinned native Codex/Pi runtime onto an
official SWE task image. Actual image IDs must be frozen in each campaign; default
local tags are convenience names, not portable reproducibility guarantees.

prepare_swe.py takes a private pinned dataset JSON and the official source image,
restores base_commit, copies original source and public issue, then replaces full
upstream Git history with one fresh snapshot commit. Native images remove their
/testbed/.git too. Gold/test patches stay private. Actor imports use /workspace/src
and /workspace, rather than editable dependencies pointing at the image's /testbed.

Validated development fixture: Flask5014 at dataset revision78f471bf655a3137b2e8a75af1501690ec009ec3.
Official task tests reject baseline (1failed/59passed) and accept gold (60passed).
Evidence: ../refinement/swe-native-sanity/. No model inference has run here.
Three unrelated cookie-domain tests in original test_basic.py fail with the
original image dependencies even after gold. Do not claim the entire source suite
is clean; preserve official task grading and disclose those known failures.

When using generic run.py, its workspace copy excludes .git. Initialize a fresh
snapshot Git repo before the model starts, or use a runner that preserves only the
prepared single-commit repo. Never restore upstream history into actor scope.
After actors stop, extract patches and grade them with the official swebench
harness using the private pinned dataset, without credentials. Snapshot-only
pytest checks are infrastructure sanity, not a substitute for official reports.

Next integration: frozen native model campaign and automatic snapshot-to-patch
bridge. This development fixture is excluded from sealed confirmation.
