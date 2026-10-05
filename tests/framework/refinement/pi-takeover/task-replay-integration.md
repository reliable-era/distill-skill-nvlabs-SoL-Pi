# Shared capture -> trusted replay integration

`task_replay.py` validates task/image/stopped capture, exact descriptors and payload hashes before mutation. Trusted destination must be a never-started original image with fixed idle-shell entrypoint and no output-path host mounts. Directory destinations are replaced, preserving deletion/move state; executable modes are retained. TeX protected-input violations reject replay. Doom witnesses remain recorded but are not prohibited edits; trusted grader runtime inputs are not replaced by witnesses. Replay does not build submitted code,run tests,grant cost eligibility or declare official success.

47 capture/replay offline tests pass. Synthetic Docker regex transport verifies shared capture API -> fresh trusted image with byte-identical output. This is not a repeat of the completed baseline/gold control and is not a native actor/official grader result.

Preserved failures:
- v1: `CAP_DROP=ALL` trusted runtime could not read private captured0600payload owned by the host UID.
- v2: explicit ownership restoration failed because trusted container lacked CAP_CHOWN.
- v3: reused the exact v2 capture; only fresh trusted replay container granted CHOWN and DAC_OVERRIDE. Replay chowns payload to original trusted runtime UID/GID,without widening file modes or manufacturing executable permission. Byte readback passed; all containers removed. Actors' capability restrictions remain unchanged.

Evidence: `task-replay-docker-smoke-v1-failure.json`, `task-replay-docker-smoke-v2-failure.json`, `task-replay-docker-smoke.json`, `task-replay-integration-review.json`. No model POSTs, native actor starts or official grader runs. New grader creation recipes must explicitly include these trusted-only capabilities if dropping all defaults. Required task dependency/environment recipes, PMARS/Cython layout discovery, real native stopped-actor replay and official grading remain integration gates. Reuse existing nine controls/transfers rather than redoing them.
