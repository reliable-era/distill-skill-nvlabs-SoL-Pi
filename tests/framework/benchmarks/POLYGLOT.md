# Aider polyglot grader adapter

Python, Go, C++, Rust, and Java tracks have offline Docker grader sanity checks.
JavaScript remains TBD. Arbitrary-task dependency coverage remains TBD. This is an **adapted subset protocol**, not a
reproduction of Aider's published leaderboard: one fixed-budget native-agent
attempt; tests physically withheld; no second repair turn after grading.

Sources are pinned to:

- Exercises: `Aider-AI/polyglot-benchmark@7e0611e77b54e2dea774cdc0aa00cf9f7ed6144f`.
- Official runner mapping and 180-second timeout:
  `Aider-AI/aider@5dc9490bb35f9729ef2c95d00a19ccd30c26339c`,
  `benchmark/benchmark.py:run_unit_tests`.
- Official Go image: `golang:1.25.1-bookworm` at the digest in Dockerfile.polyglot.
- Native-agent base image: `sol-pi-eval-trial:2026-10-04`;
  actual built image ID is recorded in polyglot-sanity.json. The local base tag
  is not a portable remote-image digest; rebuilding requires the runtime images.

Prepare from a clean checkout at the exact exercise revision:

```sh
python3 tests/framework/benchmarks/polyglot.py \
  --source /path/to/polyglot-benchmark \
  --task go/exercises/practice/food-chain \
  --output /path/to/prepared-food-chain
```

Actor gets only `workspace/` and `prompt.txt`. Never mount the checkout,
`reference/`, or `grader/` in the actor container. The `grader/` directory is a
self-contained framework grader: mount it read-only as `/grader`, candidate
workspace read-only as `/workspace`, use command `python3 /grader/grade.py`,
and provide writable `/tmp` with `HOME=/tmp` and `GOCACHE=/tmp/go-cache`.
The grader also supports the framework mount `/grade`, deriving its directory
from its own script location. Run with network disabled and no credentials. The grader restores trusted
support and original tests, then overlays only configured solution files;
candidate edits to tests/build config and added files cannot affect grading.
Exit 0 means accepted with at least one executed test, 1 rejected, 2 infrastructure
failure. Rust runs ignored tests; Java removes `@Disabled` as the official runner
does. Go uses JSON events for test counts. Rust Cargo.toml is immutable trusted
support, an explicit additional protocol deviation preventing disabled suites.

`polyglot-sanity.json` records four offline checks: Python proverb and Go
food-chain original starter code reject, original Exercism examples pass.
Python proverb is an adapter smoke task, not the frozen scored development
selection. Go food-chain is in the existing metadata-selected pilot.
Neither sanity result is an agent benchmark result. No inference occurred.

Original exercise files remain in the external pinned checkout, not vendored
here. Preserve per-exercise LICENSE files when preparing actors. Python track
license attribution beyond the dataset README remains TBD; resolve before
redistributing exercise assets. The sanity artifact includes test output and
source hashes, not gold solutions.


The multilingual extension Dockerfiles build `sol-pi-eval-polyglot-multilingual`
and `sol-pi-eval-polyglot-java`. The latter adds a Gradle8.7 cache prewarmed on the
separate Java series smoke task. Cache/file hashes and CLI versions are in
polyglot-multilingual-provenance.json. Its build context is an external clean
Gradle cache, not the repository or credential directory. JDK17/CMake are from
Debian packages; exact image IDs pin this local environment, while apt versions
in the Dockerfile remain unpinned. Rust1.90.0 uses a pinned official image digest.

polyglot-multilingual-sanity.json exercises separate smoke tasks C++sublist,
Rustacronym and Javaseries, plus the earlier Python/Go tasks, under `/grade`.
Starters must reject; official examples must pass with nonzero test execution.
C++18/Rust10/Java11 test cases execute in reference checks. These are infrastructure
sanity checks, not model results or confirmation. Sealed task prompts/tests/gold
solutions were not inspected. Confirmation environments must be prepared and
checked after candidate freeze; this smoke cache does not prove dependencies
for every exercise. Missing offline dependencies are infrastructure errors.

## Corrected login-shell runtime

The first Go development image does not expose Go on `/bin/sh -lc`'s reset
PATH. This affected Codex tool checks and confounds that original stage's token
comparison. Its immutable image, attempts and grader results are retained;
no model attempts were repeated. Future Dockerfiles link Go/gofmt and Rust
proxies into `/usr/local/bin`. Build the corrected images under new tags:

```sh
docker build -f tests/framework/benchmarks/Dockerfile.polyglot \
  -t sol-pi-eval-polyglot-login:2026-10-04 tests/framework/benchmarks
docker build -f tests/framework/benchmarks/Dockerfile.polyglot-multilingual \
  -t sol-pi-eval-polyglot-multilingual-login:2026-10-04 tests/framework/benchmarks
docker build -f tests/framework/benchmarks/Dockerfile.polyglot-java-cache \
  -t sol-pi-eval-polyglot-java-login:2026-10-04 /path/to/clean-gradle-cache
```

`polyglot-login-probes.json` records native shell and login-shell resolution as
root and evaluator. `polyglot-login-sanity.json` repeats infrastructure-only
starter/reference checks under the corrected runtime. These checks do not
replace, rerun, or improve the historical model results.
