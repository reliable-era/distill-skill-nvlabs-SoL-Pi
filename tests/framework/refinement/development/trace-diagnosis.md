# Development trace diagnosis: Go screens

Read-only analysis of saved `agy-go`, `pi-go-v2` and `codex-go-v2` transcripts. No actors rerun, no canonical skill changes, no confirmation-task inspection. Transcript references below are physical JSONL lines, not inferred turns. One reused food-chain exercise, one stochastic attempt per arm/harness: observations identify possible waste, not instruction-level causes or a general winner. Both means the candidate plus Karpathy, not shipped plus Karpathy. Authoritative independent grades supersede Codex v2's infrastructure-failed original grader summaries.

## What the records establish

| Harness | None | Karpathy | Shipped | Candidate | Both |
|---|---:|---:|---:|---:|---:|
| Pi v2 reported tokens | 11,429 | TBD; ≥11,273 observed | 13,877 | 12,544 | 16,895 |
| Pi v2 tool starts | 4 | 5 | 4 | 4 | 5 |
| Codex v2 reported tokens | 62,164 | 65,766 | 64,000 | 63,481 | 83,097 |
| Codex v2 calls | 4 | 4 | 4 | 5 | 5 |
| agy complete SDK tokens | 200,303 | 152,832 | TBD | 206,546 | 190,675 |
| agy completed tool events | 18 | 12 | 32 | 13 | 13 |

All Pi/Codex v2 patches pass independently restored official tests. agy shipped fails and ends SDK ERROR/503 with incomplete observed 263,286 tokens. agy parent, separate from the candidate, passes at145,196 tokens/10 completed tools. Count unique Pi `tool_execution_start`, Codex completed tool items, and agy DONE tool steps; do not count streaming updates as additional calls. Native token telemetry and effort differ across harnesses and are not pooled. Pi Karpathy final model event lacks usage; process exit0 does not supply missing accounting.

### Codex: unnecessary reread and absent-test probe are concrete

Candidate `codex-go-v2/results/00000-4c4006ad9850/agent.log:7` enumerates `*test.go` and `SKILL.md`; line9 nonetheless executes `cat food_chain_test.go`, returning `No such file or directory` and exit1. Line11 reads `/opt/eval-skill/SKILL.md` although the skill was already inline in the actor prompt, then repeats enumeration and instruction-file checks. The absent filename probe supplies no positive test evidence. This is a plausible avoidable read in this known fixture; it does not prove the candidate text caused it.

None (`00004-56a586780841/agent.log:7,9,13`) enumerates, reads source/module, edits and formats/build-checks without a skill reread. Shipped (`00002-d870ce81f49d/agent.log:7,9,13`) follows the same broad path. Karpathy (`00003-2ed8ac25277f/agent.log:9`) also rereads inline skill, but batches it with source/module rather than creating another call. Both (`00001-236106a1849e/agent.log:9,11`) lists skill resources then reads the inline skill in a separate call. Thus reread avoidance is a delivery/runtime opportunity; not a candidate-only defect.

Candidate's 5 calls versus None's4 accompany only2.1% more reported tokens. Both's5 calls cost33.7% more than None, so an extra call alone cannot explain its larger traffic. Inline context length, model reasoning/output and replay are competing hypotheses; no counterfactual attribution is available.

`go test ./...` returns `[no test files]`; it validates compilation, not the official exercise behavior. The original Codex v2 grader raises NameError before tests run; use `regrade.json`/`regrade.log`, not the stale zero-solve table in `results/summary.md`. The earlier login-PATH confound was corrected in v2 and must not be presented as a v2 failure.

### Pi: the small task has little tool-turn slack

None `pi-go-v2/none/stdout.jsonl:38,66,630,661` runs discovery, reads source, edits and formats/tests. Candidate lines38,66,620,658 does the same four starts, adding `go vet` to the final shell command. Shipped lines42,70,634,670 also has four starts. Shipped's discovery command already prints function lines and module text before the source read; source overlap exists but is not a full redundant file read. Candidate's9.8% and shipped's21.4% excess over None cannot be explained by additional tool turns: call counts are identical.

Karpathy lines39–40 and Both lines94–95 separately read the26-byte module after source; combining independent tiny reads could remove one model/tool boundary if the harness permits it. Their final shell calls also build temporary behavior checks. Those checks supply additional verification; do not remove them merely to win token counts. Both line1218 includes formatting, compilation and a temporary verification program in one Bash call, so observed batching is already substantial.

No saved Pi trace here demonstrates a need for long-log reduction or compaction. Claims that a shorter portable skill implements native context packing would be unsupported.

### agy: broad discovery, verification recovery and model failure dominate

None `agy-go/none/stdout.jsonl:11,14,17` repeats local enumeration, scans the entire filesystem for a food-chain filename and invokes git in a workspace without `.git`. Karpathy lines20,23 likewise scans `/` and gets git errors. Both lines11,14,20 has the same local/global search and failed git probe. This waste is shared across configurations, not evidence of a unique shipped failure.

Candidate lines16,20 polls a task and reads its log; the returned log is only two lines. Line24 still invokes git and fails. Line33 runs `go run -e . || go build .`, receiving `flag provided but not defined: -e`; line36 runs another build and line39 another `go test` returning no tests. Line42 reads source only to print its character count. These are concrete opportunities: avoid invalid Go command forms, stop searching after manifest discovery, and avoid status/size checks without a decision purpose. Native async polling may be required by that harness; one short poll is not automatically gratuitous.

Both lines29,32 attempts `go run -e -` and then a nonexistent `scratch/verify.go`. Subsequent Python-based checks recover from these failed commands. Keep intended verification but use a documented working temporary-module recipe.

Shipped line23 also uses invalid `go run -e -`; lines29–44 repeatedly constructs/debugs temporary checks. It then issues16 completed `search_web` calls overall, compared with2 for None and0 for candidate/Both. Its SDK ERROR/503 and print timeout are observed failures, not proven effects of the skill. Some late searching may reflect missing task-spec clarity and lyric verification difficulty, not an instruction to browse. None successfully retrieves public Exercism tests through curl at lines35,38,41 and temporarily downloads/runs them at line52. That is actual external test exposure, and means its score/cost is not an unaided clean comparison. Distinguish this returned test content from search attempts.

## Pinned references: mechanism relevance, not borrowed performance claims

The three README byte hashes were checked against `../references.json`; all matched. Sources:

- [SoL-Pi at e1a586af](https://raw.githubusercontent.com/NVlabs/SoL-Pi/e1a586af0ad8956f42ae5b26bba20e48fbf30e00/README.md): edit-plus-validation fusion, stable observation handles with exact recall, evidence-preserving reduction and economically gated native compaction are runtime mechanisms. A skill can suggest batching; it cannot remove a mandatory harness boundary or change provider context replay. For this tiny task, fusion is the narrow relevant experiment; reductions add complexity without demonstrated large observations.
- [Ponytail at c982cd41](https://raw.githubusercontent.com/DietrichGebert/ponytail/c982cd411abb53323c4baa1baa3c2f020b8d0b08/README.md): minimal task scope while retaining validation supports deleting discovery/status work, not deleting verification. Its own repository benchmark percentages are not transferable to these traces.
- [Jev at923e521b](https://raw.githubusercontent.com/lazniak/jevskill/923e521b0521061637bbc486d9f9c2a3683e0374/README.md): structured/reversible context reduction with a measured ledger fits genuinely large observations. The catalog labels Jev identity provisional; retain that ambiguity. No observed large-log/context-pressure bottleneck justifies adding a reduction-model call here.

## Narrow next experiments

First test a runtime/delivery control, keeping the candidate and model constant: explicitly mark skill text as already loaded, provide authoritative workspace/test availability metadata without test answers, and compare normal edit→validation against an opt-in runtime fused edit+validation call. Preserve original tool outputs and independent official grading; never treat no-tests compilation as behavioral verification. Capture request count, per-request input/output/cache, result bytes, latency and actual billing where available. This separates real boundary/replay effects from prose brevity. A no-model structural adapter test can precede any authorized new actors.

A separately frozen next candidate should add only one local rule: after authoritative discovery, reuse loaded instructions and listed files; absent withheld tests are not searched for; use a known working language check recipe and report compilation-only honestly. Keep the acceptance criteria and independent grader unchanged. Do not forbid new reads when edits or new evidence require them, and do not remove useful temporary behavior checks.

Preregister comparisons against None, Karpathy, shipped and Both on a broader development panel before confirmation; include all failed/partial attempts. Measure reread/probe/invalid-command events as process outcomes. Hypothesis: the rule reduces avoidable discovery and recovery calls. Required causal evidence: matched runtime controls and repeated tasks showing those events and failure-inclusive cost fall without lowering official quality. Current saved single-task records do not establish that hypothesis, and do not authorize promotion or canonical edits.
