# Economic evaluation framework

Compare task quality, failure-inclusive tokens, dollars, time, and repeat stability across agents and skill configurations. All inference is containerized. Credentials are provided after the build; they never enter an image or Git.

**Built:** nine agent CLIs, immutable sampling and run plans, isolated runner/grader, conservative telemetry, timeout recovery, reports, and offline Docker smoke checks. [A native four-configuration pilot](trials/README.md) has completed for Pi, Codex, Copilot, Cursor Auto and native Antigravity `agy`: 40 actual attempts, independently regraded. **TBD:** authenticated checks for remaining agents, common-backend routing, dollar billing and published-benchmark environment/grader integration. A CLI installation check is not an evaluation result.

## Agents and login

The shared `sol-pi-eval-all:2026-10-03` image contains Codex, GitHub Copilot CLI, Pi, OpenCode, Gemini CLI, Hermes, OpenClaw, Cursor Agent CLI, and Claude Code as the historical reference. Every agent uses the same installed toolchain; agent harness versions remain separate from backend model identifiers.

[Human login commands and credential mounts](runtime/README.md) · [Pinned versions and commands](agents.json) · [Offline installation evidence](runtime/installation-check.json).

**Antigravity is a separate harness, not another name for Gemini CLI.** Its native headless trial adapter is now tested using a host binary mounted read-only; packaging it into the shared image and generic registry remains TBD. Pi with an Antigravity provider would count as Pi.

## Benchmarks

[Six published benchmark sources](BENCHMARKS.md): SWE-bench Verified, SWE-bench Multilingual, Terminal-Bench 2.0, Aider polyglot, BugsInPy, and Defects4J.

The first breadth pilot is **8 tasks: 2 each from the first four benchmarks**, selected from 1,114 public inventory entries using seed 42. Selection balances benchmarks, then prioritizes language/repository breadth. Eighteen previously exposed SWE issues are excluded. Selection used metadata, not outcomes. `code-from-image` needs verified image transport and model capability before it is eligible for a scored comparison. The multilingual inventory has no language column; those labels remain TBD. Eight tasks are a cheap breadth check, not a representative population estimate.

| Benchmark | Frozen tasks | Official grader integration |
|---|---|---|
| SWE-bench Verified | `pydata__xarray-4966`, `pallets__flask-5014` | TBD |
| SWE-bench Multilingual | `apache__lucene-12196`, `phpoffice__phpspreadsheet-4114` | TBD |
| Terminal-Bench 2.0 | `code-from-image`, `sanitize-git-repo` | TBD |
| Aider polyglot | JavaScript `bowling`, Go `food-chain` | TBD |

[Selected IDs and sampling digest](examples/pilot-selection.json) · [Pinned source revisions](examples/pilot-sources.json). Published test data and gold solutions must stay outside the actor workspace. Each benchmark needs its official environment and grader wired to the task contract before a scored campaign. The local smoke task below only checks plumbing.

Recreate the pinned inventory and selection (HF extraction needs `pyarrow`; runtime itself uses Python stdlib):

```sh
python3 -m pip install pyarrow
python3 tests/framework/benchmarks/fetch.py \
  --benchmark swe-bench-verified --benchmark swe-bench-multilingual \
  --benchmark terminal-bench-2 --benchmark aider-polyglot \
  --revisions tests/framework/examples/pilot-revisions.json \
  --output /tmp/pilot-inventory.jsonl
python3 tests/framework/benchmarks/select.py /tmp/pilot-inventory.jsonl \
  --size 8 --seed 42 --strata benchmark --balance-within language repo \
  --exclude tests/framework/examples/prior-exposures.json \
  --source https://github.com/reliable-era/distill-skill-nvlabs-SoL-Pi \
  --revision pinned-in-pilot-sources.json --output /tmp/pilot-selection.json
```

## Build and verify before login

From the repository root:

```sh
docker build -t sol-pi-eval-agents:2026-10-03 tests/framework/runtime
docker build -f tests/framework/runtime/Dockerfile.hermes \
  -t sol-pi-eval-hermes:2026-10-03 tests/framework/runtime
docker build --network none -f tests/framework/runtime/Dockerfile.all \
  -t sol-pi-eval-all:2026-10-03 tests/framework/runtime
python3 tests/framework/runtime/probe.py
python3 tests/framework/verify.py --output /tmp/runner-check.json
python3 -m unittest discover -s tests/framework -p 'test_*.py'
python3 -m unittest discover -s tests/framework/benchmarks -p 'test_*.py'
```

The manually dispatched GitHub workflow `Validate multi-agent evaluation runtime` repeats the image build, probes, and offline Docker checks without credentials. The normal upgrade workflow tests accounting/sampling and the mock runner.

Run the no-login, no-model smoke check with the same shared image:

```sh
python3 tests/framework/run.py freeze tests/framework/examples/smoke.json \
  --output /tmp/eval-smoke-plan.json
python3 tests/framework/run.py run /tmp/eval-smoke-plan.json \
  --output /tmp/eval-smoke-results
```

It repairs a deterministic fixture and runs independent regression tests. Both mock configurations should solve 2/2; tokens and dollars stay TBD because no LLM runs. It cannot measure skill quality.

## Run contract

Copy `examples/campaign.template.json` outside Git, prepare task workspaces and independent graders, and replace every TBD. `freeze` hashes source files, graders, skill resources, commands, the registry, and local Docker image IDs. It refuses changed inputs and overwriting a plan. Actor copies omit `.git` history/config; executable source bits are retained. Inputs with symlinks currently require a prepared plain-file snapshot. The matrix is all tasks × configurations × declared rounds, scheduled once; there are no automatic retries.

```sh
python3 tests/framework/run.py freeze /private/campaign.json --output /private/plan.json
python3 tests/framework/run.py run /private/plan.json \
  --output /private/results --env-file /private/agent.env
python3 tests/framework/run.py report /private/results
```

For a multi-agent plan, supply `--agent-env codex=/private/codex.env --agent-env cursor=/private/cursor.env` (repeat per agent). A single `--env-file` is accepted only for a one-agent plan, so unrelated credentials are not distributed across clients. A configuration can mount its dedicated `credential_volume` read-only at `/auth`; the entrypoint copies only allowlisted auth artifacts into a disposable home. Agent task mounts are writable, the skill bundle is read-only, graders receive no credentials, and no actor receives the Docker socket. Agent network access is explicit; graders run with network disabled. CPU, RAM, and wall-time limits apply to both.

Task fields: `id`, `benchmark`, `workspace`, `prompt`, `grader_dir`, `grader_argv`, optionally `grader_image`. The grader exits **0** for solved, **1** for a completed rejection, and any other code for infrastructure failure. A grader timeout/error stays ungraded. Actor failure/timeouts still receive grading if their workspace is available. Grader source is mounted only in the grader container. The cumulative time allowance also clamps the remaining grader timeout. Its tests must be authoritative and work offline; do not use actor self-reports as grades.

Skills use one common portable mechanism: prepend the frozen SKILL.md text and mount its resources at `/opt/eval-skill`. Baselines receive no skill. This measures portable instructions plus accessible resources; native marketplace/plugin behavior is not assumed. Existing historical Claude plugin results remain separate.

If the runner is interrupted, preserve the attempted work and classify it before resuming:

```sh
python3 tests/framework/run.py recover /private/results
python3 tests/framework/run.py run /private/plan.json --output /private/results --env-file /private/agent.env
```

Recovery removes the named containers and records unknown cost/quality for interrupted attempts. Completed attempts are skipped. It does not silently replay paid work.

## Economic comparison rules

- **Same-model mode:** use compatible agent-specific model identifiers for one verified backend. Record `backend_id`; routing compatibility still needs an authenticated check. A matching name alone does not prove the same model.
- **Native mode:** each agent uses its supported model/provider. Report agent + actual backend together; this is a system comparison, not a harness-only comparison. Unknown actual model is TBD.
- Compare **no skill**, **ours**, **Karpathy**, and **both** when their frozen resources are available. Start with no skill versus ours to minimize spend; do not discard unsuccessful configurations or rerun until ours wins.
- Report each benchmark separately. Include all attempts, timeouts, ungraded errors, failure-inclusive tokens/dollars/time per solve, quality bounds for ungraded attempts, and round variation. Unknown grades do not shrink the displayed attempt denominator. A scheduling seed does not control model sampling randomness.
- Agent seconds measure the actor container, including startup/cleanup; grader seconds are recorded separately in each result. Hardware dollars and framework preparation costs remain TBD.
- Prices are explicit USD per million tokens with uncached input, output, cache read, and cache write separately. No price is inferred. Subscription costs, missing usage, auxiliary models without their own prices, and external tool charges remain TBD. See [telemetry contracts](USAGE.md).
- Real campaigns require frozen maximum attempts and cumulative run time. Known-dollar caps are checked between attempts; they cannot guarantee a hard spend cap when usage/prices are unknown or one attempt exceeds the remaining allowance. `require_priced_usage` stops after an unpriced attempt. Provider-side spend limits are needed for a strict dollar cap.

The two-fixture native pilot is measured; published benchmark performance remains TBD. A stable efficiency claim requires held-out quality, complete comparable cost telemetry, and repeated matched runs; the eight-task pilot cannot establish one by itself.
