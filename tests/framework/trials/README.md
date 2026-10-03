# Four configurations across five native harnesses

Two previously exposed synthetic diagnostic fixtures × four configurations × five harnesses = **40 real attempts**, one round. Every attempt was graded separately in Docker; this is a small integration pilot, not a fresh held-out benchmark or a stability result.

| Harness | Model selection | No skill | Karpathy | Ours | Both |
|---|---|---:|---:|---:|---:|
| pi | GPT-6.1-Sol | 2/2 | 2/2 | 2/2 | 2/2 |
| codex | GPT-6.1-Sol | 2/2 | 2/2 | 2/2 | 2/2 |
| copilot | Auto: GPT-6-Luna; one Both task MAI-Code-1.1-Flash | 2/2 | 1/2 | 2/2 | 2/2 |
| agy | Gemini 3.8 Flash Low | 2/2 | 2/2 | 2/2 | 2/2 |
| cursor | Auto; resolved model TBD | 2/2 | 2/2 | 2/2 | 2/2 |

Each cell above is solved attempts. Both loads Karpathy and ours together. Ours is the unchanged shipped revision (SKILL.md SHA256 starts `68ea78dc`).

## Reported tokens per solve

| Harness | No skill | Karpathy | Ours | Both |
|---|---:|---:|---:|---:|
| pi | 9,074.5 | 18,485.0 | 14,564.0 | 22,099.0 |
| codex | 66,811.0 | 89,775.5 | 69,870.0 | 83,157.5 |
| copilot | TBD | TBD | TBD | TBD |
| agy | 148,265.0 | 170,405.0 | 160,655.0 | 157,648.0 |
| cursor | TBD | TBD | TBD | TBD |

Codex/Pi totals sum verified exclusive input, output, cache-read and cache-write counters once. Antigravity uses the terminal SDK `total_tokens` without adding cache or thinking counters again; separate billing-component completeness remains unverified. Cursor cache semantics and Copilot full-run token counts remain TBD. **All actual dollar billing is TBD**, including subscription costs.

## Time and cutoffs

| Harness | Configuration | Agent seconds / solve | 120-second cutoffs |
|---|---|---:|---:|
| pi | No skill | 41.2 | 0 |
| pi | Karpathy | 50.5 | 0 |
| pi | Ours | 45.2 | 0 |
| pi | Both | 52.4 | 0 |
| codex | No skill | 38.8 | 0 |
| codex | Karpathy | 44.6 | 0 |
| codex | Ours | 37.4 | 0 |
| codex | Both | 39.9 | 0 |
| copilot | No skill | 80.7 | 1 |
| copilot | Karpathy | 187.6 | 1 |
| copilot | Ours | 75.8 | 1 |
| copilot | Both | 70.7 | 0 |
| agy | No skill | 41.6 | 0 |
| agy | Karpathy | 64.1 | 0 |
| agy | Ours | 52.3 | 0 |
| agy | Both | 41.6 | 0 |
| cursor | No skill | 41.9 | 0 |
| cursor | Karpathy | 46.8 | 0 |
| cursor | Ours | 39.9 | 0 |
| cursor | Both | 44.8 | 0 |

Actor seconds include failed attempts; graders run after the actor stops. A cutoff can still leave a correct patch, so solved and timed out are distinct outcomes. Wrapper startup/cleanup timing differs across harnesses.

## Finding

Quality ties across all configurations in Pi, Codex, Antigravity and Cursor Auto. Copilot Karpathy loses one interface task at the cutoff. Ours uses more reported tokens than no skill in Pi (+60.5%), Codex (+4.6%), and Antigravity (+8.4%). This pilot does not show ours beating the baseline.

Interpret comparisons within each harness cautiously: native models and effort settings differ; Copilot Auto switches models for one Both task; Cursor Auto does not disclose its resolved model. Pi/Cursor/Antigravity load mounted skill files through a read-follow prompt; Codex/Copilot receive inline skill text plus mounted resources. Only one round was run, and the two synthetic fixtures were used in earlier experiments. No general efficiency or stability winner is established.

## Availability failures

Earlier requests rejected by account or model availability are retained separately and do not become quality failures: Pi Anthropic quota exhausted; Cursor free plan rejects named models; Copilot rejects the initially selected GPT-5.4. The successful provider/default-routing pilots are separate frozen plans. [Availability ledger](availability.json) retains attempted and skipped records; their token/billing usage is unknown, not free.

## Evidence

[Normalized attempts](collection.json) · [CSV](summary.csv) · [Independent regrading audit](independent-audit.json). Original plans, transcripts, returned workspaces and grader outputs are under `codex/`, `copilot/results-auto/`, `pi_openai/`, `agy/`, and `cursor_auto/`. [Antigravity headless protocol](https://www.antigravity.google/docs/cli/headless/).

Rebuild the shared pytest-equipped image with `docker build -f tests/framework/runtime/Dockerfile.trial -t sol-pi-eval-trial:2026-10-04 tests/framework/runtime`. Collection can be regenerated without model calls: `python3 tests/framework/trials/collect.py`.
