# G6 execution protocol

Design/sample are fixed by `preregistration.json` (initial contract commit `d1fe82a`). The plugin snapshot is commit `920c32eb69fff4227fe1e3991046b43a805ec61e`, not the dirty worktree. Hamilton proportional allocation gives150 issues; the single Flask issue receives quota0. Two independently seeded smoke issues are outside those150. No G5 model-outcome file is read by allocation or execution.

## Gates

1. Build the pinned2.1.302 tools image with `build.py`; no credentials enter its context. Per-issue actor images inherit the exact frozen G5 base image and add only the tools, an empty writable task directory and a nonroot account.
2. `plumbing.py` performs four real Docker fixtures: CLI version, normal local-marketplace installation in treatment only, separate HOME, blocked direct/other-domain egress, single-history sanitized source, source-only capture/replay, a harmless nonempty official-grade fixture and empty-patch bypasses. It never calls headless inference or reads the dedicated token.
3. `freeze_runner.py` runs unit tests and freezes every runner source, plugin-tree hash, image manifest and plumbing evidence. Commit `runner-stage.json` before inference. `runner.py --allowance-commit COMMIT --phase smoke` requires the exact committed allowance. Study is rejected before credential access because the only authorized phase is smoke.
4. After the2x2 smoke, generate `smoke-summary.json`/`smoke-report.md` with `summarize_smoke.py`, report to the supervisor and WAIT. A successful smoke does not authorize the300-run study. No `--go` shortcut exists.

## Identical prompt and isolation

The issue block and task instructions are byte-identical to G5 `prepare_source.py` in both arms. G5's Codex request-budget and inline-skill suffix is not reused: it would misdescribe Claude turns and conflict with normal plugin installation. Claude receives the prompt on stdin, with `--max-turns60` and a7200-second external wall cap. No output-token cap is invented.

Only treatment mounts the frozen marketplace; both arms use fresh tmpfs HOME, fresh single-commit task source and fixed runner settings. Control also disables all skills. Project/local settings, MCP, hooks, auto-memory, plugin sync telemetry and updater traffic are disabled; no host home/config/credentials are mounted. Treatment uses normal `plugin marketplace add` and `plugin install`, not a prompt-inlined skill or forced invocation. Activation/invocation is observational and never an exclusion criterion.

Actors have no capabilities or external route. An owned internal Docker network exposes only an owned CONNECT proxy allowing `api.anthropic.com:443`. No TLS payload/header logging. Preparation/grading stay offline. Subagents remain available; per-model root aggregate usage is cross-checked against result counters and observed forwarded subagent messages, without double-counting aggregate and child usage. The token is removed from Bash child environments; it is never supplied during plugin setup.

## Credentials and records

Only the dedicated owned mode600 setup-token file is accepted, without following symlinks. Runtime `docker exec --env-file` uses an owned mode600 file in tmpfs, removed in `finally`; the value is absent from Docker command arguments and container image/config environment. No host `.credentials.json` is read or copied. Streams and capture tar bytes are filtered before persistent writes. A credential occurrence in workspace capture stops grading/admissions rather than silently scoring an altered patch. Actor HOME/session state is not archived.

Raw model output, patches, grades and build/runtime logs stay in the new private G6 root. Git receives only code, allocation, sanitized summaries and hashes. Summaries contain all-attempt uncached input/cache-creation/cache-read/output counts per model, completeness, model IDs, version/commit, wall time, activation and grade/rate events. Missing usage remains unknown/lower-bounded. API-error observations make cost coverage conservative even if a later native result succeeds. If coverage is incomplete, scope the study to solve rate.

Token volume is U+C+R+O. The fixed cache-adjusted5-minute-volume proxy is U+1.25C+0.1R+O, not dollars, not an inferred TTL and not an exact billing estimate. Both are reported separately. No G5 request/turn equivalence or model-family cost equivalence is claimed.

## Ownership and repairs verified before inference

G5 adapter code is copied/pinned locally; official grading, source-only projection, legitimate binary-asset preservation and empty-source outcomes are unchanged. G6 uses its own source/grader names. Starter archive ownership is1000:1000 for the capability-dropped actor. Fresh snapshot Git auto-GC is disabled to avoid a background pack/archive race; source bytes and prompt are unchanged.

Classic local Docker builds use frozen image IDs (no registry tag substitution). Intermediate images are individually labeled and explicitly released leaf-first with `--no-prune`, never force/prune. The fixed152 selected issues have distinct frozen image IDs; a checked guard prevents unsafe independent release if that condition changes. Preexisting bases are preserved. Actor/grader/network cleanup is verified; uncertainty stops admissions and retains costs.

Offline checks caught and fixed image-ID/build-cache ownership, nonroot source-directory preparation and background Git GC before any Opus call. An initial setup-only launch was also held and drained before native start to verify/fix Docker stdin forwarding;zero native starts/streams/calls were observed,all setup evidence retained. Exact canonical prompt bytes were then round-tripped over the actual docker-exec stdin/env-file transport without calling the model. No allocation or treatment change followed a treatment result. Study inference/analysis remain descriptive; contamination cannot be ruled out.
