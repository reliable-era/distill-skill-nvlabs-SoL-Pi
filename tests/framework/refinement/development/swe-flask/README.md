# SWE-bench native development screen

Twelve bounded Docker actors on one public SWE-bench Verified development issue, `pallets__flask-5014`. One round; order seed 105 controls order, not model randomness. No held-out confirmation and no skill promotion.

| Harness | Skill | Solved | Reported tokens | Actor seconds |
|---|---|---:|---:|---:|
| pi | No skill | 1/1 | 23,428 | 51.5 |
| pi | Karpathy | 1/1 | 32,577 | 56.1 |
| pi | Shipped ours | 1/1 | 29,029 | 55.9 |
| pi | Lean parent | 1/1 | 38,296 | 47.0 |
| pi | No-reread candidate | 1/1 | 41,779 | 58.9 |
| pi | Candidate + Karpathy (Both) | 1/1 | 31,632 | 48.7 |
| codex | No skill | 1/1 | 82,389 | 30.2 |
| codex | Karpathy | 1/1 | 92,639 | 33.1 |
| codex | Shipped ours | 1/1 | 66,343 | 30.7 |
| codex | Lean parent | 1/1 | 132,404 | 45.2 |
| codex | No-reread candidate | 1/1 | 88,212 | 34.8 |
| codex | Candidate + Karpathy (Both) | 1/1 | 89,211 | 35.7 |

The no-reread candidate uses **78.3% more** reported tokens than no skill in Pi and **7.1% more** in Codex. Shipped ours uses **23.9%** more in Pi and **19.5%** fewer in Codex. These are single-task descriptive observations, not stability or statistical evidence. The candidate is not promoted.

Pi uses OpenAI `gpt-6.1-sol`, thinking low; its completed message events confirm that model label. Codex explicitly selects `gpt-6.1-sol` with native default effort and ChatGPT OAuth; a separately observed actual backend label is **TBD**. Complete terminal counters are summed once; they include reported cached usage and are not verified invoice amounts. Actual dollars: **TBD**. Cross-harness efforts and tools differ.

All actors received the original public issue and fresh single-commit source snapshot, uniform inline skill text, and readonly resources. Gold patches, private dataset and official tests were never mounted into actors. Actor cap 180 seconds, maximum 12 attempts, no retries; all 12 exited 0 without timeouts. `plan.json` froze the model matrix, skill/prompt hashes and image ID before inference. Runner/source hashes were omitted from that plan and recorded during execution; this limitation is explicit in `runtime-provenance.json`.

After actors stopped, `bridge-executed.py` rebuilt patches against trusted original snapshots while ignoring actor Git indexes/history. Each saved `model.patch` was independently graded with official `swebench 5.0.2` `run_evaluation` against the pinned private dataset, revision `78f471bf655a3137b2e8a75af1501690ec009ec3`. Official reports and test outputs are under `official/`; hashes appear in every result. An empty-patch sanity was initially skipped by the official harness, preserved as incomplete. Before any actor ran, a harmless marker no-op obtained a real official report with resolved=false and the expected target test failure; no model attempt was replayed. Prior gold sanity resolved=true is in `../../swe-native-sanity/` and `../../grader-sanity/`.

Runtime and trace limitations: Pi Bash tool calls report `rg` unavailable while Codex command tools resolve it; all Pi arms attempted it and recovered with other tools. The PATH/tool-wrapper mechanism is **TBD**. No environment was changed within this screen. Three unrelated `test_basic.py` cookie-domain failures persist with original official image dependencies even after gold. Codex Lean parent ran the full suite and encountered those failures; Karpathy ran broader basic tests. These failures are disclosed rather than interpreted as regressions in the official task result. Saved traces show no redundant SKILL.md reads in this fixture, so the no-reread sentence does not explain a measured causal benefit.

Full-suite cleanliness, generalization across tasks/harnesses, repeated-round stability, and real billing superiority remain **TBD**.

Complete final source snapshots remain local. Git retains each binary-capable model patch, pinned original source manifest, transcript and official grader report; reconstruct source from the pinned original plus the patch rather than storing twelve repeated copies.
