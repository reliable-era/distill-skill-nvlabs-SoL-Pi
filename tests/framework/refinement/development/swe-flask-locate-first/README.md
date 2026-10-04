# Locate-first SWE development screen — prepared

Four arms: No skill, frozen Karpathy, locate-first candidate, and candidate + Karpathy (Both). Pi and Codex each get four attempts on the previously exposed public SWE-bench Verified issue `pallets__flask-5014`; maximum eight starts, 180 seconds each, one round, randomized order seed 106. Resolution, tokens, time, and actual billing: **TBD**. No actor has launched.

Exact native image, original snapshot/public issue, configured models, uniform inline delivery and readonly skill resources match the preceding SWE development screen. Pi selects OpenAI `gpt-6.1-sol` with thinking low; Codex selects `gpt-6.1-sol` with native default effort and ChatGPT OAuth. Actual separately observed backend labels remain **TBD** until recorded. Candidate instruction changes only the first context/read bullet; canonical skill and sealed tasks stay unchanged.

`plan.json` freezes image, source/skill/prompt hashes, runner source, standalone bridge, accounting and transcript collector before model calls. Frozen runtime files are loaded at launch; altered hashes abort. The launch command requires a frozen global stage file and writes its digest before any model calls. Root must first verify the preceding terminal stage has stopped and freeze the global sixteen-start stage.

Preparation runs a trusted empty snapshot-to-patch check without models. At launch, official `swebench 5.0.2` independently grades a harmless marker no-op and must reject it before actors begin; empty patches are not used as grader controls. Each stopped actor's patch is rebuilt against the trusted source snapshot and graded separately by the official harness. Dataset/gold/tests and credentials are never shared into the actor/grader across that boundary. Three known unrelated cookie-domain source-suite failures remain disclosed. Dollar costs are **TBD**.

Launch only when authorized for this stage:

```sh
python3 tests/framework/refinement/development/swe-flask-locate-first/run_screen.py --launch --global-stage PATH_TO_FROZEN_GLOBAL_STAGE_JSON
```

The exclusive launch manifest prevents automatic replay; a started attempt counts even when authentication fails. Stop remaining attempts in the affected harness on auth/quota rejection. Use `SOLPI_PRIVATE_AUTH_CACHE` pointing outside the repository, with one writable persistent HOME per harness. Seed each cache once externally, then preserve refreshed credentials across attempts under a per-harness `fcntl` lock; never recopy the stale host seed. Actor workspace temporary files are removed; private auth remains available for later attempts. Original host credentials are never written. `audit.py` checks frozen hashes, the eight-start cap, duplicate records, patch/transcript/report hashes, scores and exact secret values without model calls. Independent confirmation and economic superiority are unproven.

Availability gate: the preceding terminal Pi Both startup reported `invalid_grant` with zero model calls. This new phase remains prepared-only. Root must verify the private auth cache or obtain a fresh human login before any explicit launch; file presence alone does not establish valid credentials. No auth refresh or model probe is run by preparation/audit.
