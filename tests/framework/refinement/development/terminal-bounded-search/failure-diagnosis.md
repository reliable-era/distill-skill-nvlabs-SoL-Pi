# Bounded-search failure diagnosis

This reused development task produced a quality regression: bounded-search failed the official exact-replacement test, whereas No skill and Both passed all three tests. Its 14.5% lower reported token count than No skill is not an economic win because it did not solve the task. These are single observations, not evidence that the skill caused the failure.

## Contract and observed edits

The public instruction asks to replace credentials with specified, consistent placeholders, retain those placeholders, and avoid changing uncontaminated files. It does not explicitly ask to repair executable shell commands. The official verifier additionally compares each of the three contaminated files in full against a reference replacement; that is a stricter representation check than merely confirming that secrets disappeared. The candidate passed removal and untouched-file checks but failed this full equality check (`codex/candidate/verifier/grade.txt`, assertion at official test line 57). Fresh filesystem replay reproduced that outcome without models.

The candidate initially performed literal credential-to-placeholder substitution. In original private `codex/candidate/stdout.jsonl` line 15, its Python loop uses byte replacement and writes only changed files. At line 18 it makes a second edit to the YAML: it adds double quotes around both AWS placeholders, the GitHub clone URL containing a placeholder, and the Hugging Face token argument. Those additional quotes account for the difference from the passing replacement patch; the grader excerpt identifies the first AWS quote difference. This diagnosis does not require exposing any original credential values.

The subsequent checks validate a broader property. Candidate line 20 attempts to parse YAML and run `bash -n` on placeholder-containing commands; PyYAML is unavailable. Line 22 instead extracts such commands from raw YAML and checks their shell syntax successfully. Its final message reports Python, JSON, shell syntax, and diff checks. Quotes can have a legitimate shell syntax purpose because angle brackets have shell meaning, but successful shell parsing does not establish fidelity to the requested replacement representation. The trace contains no explicit explanation of why the second edit was chosen, so intent remains an inference from the edit/check sequence.

No skill uses literal substitution at line 22, followed by remaining-credential, Python/JSON parsing, and diff checks at lines 24 and 27. Both uses literal replacements in two passes (lines 16 and 23). At line 26, Both reconstructs each changed file from its original bytes by applying credential substitutions and asserts equality with the final bytes; it also checks removal and parsing. No skill and Both produce the same passing patch. Both has a nonzero command exit at line 16 from a separate malformed scan script and subsequently continues; that unsuccessful tool call remains in its cost ledger.

## Trace comparison

Counts below use original private unredacted `aggregated_output` strings, counted once per completed command. They are returned character counts, not a claim about exact model-visible context or dollars. Original transcript hashes were checked when generating `trace-metrics.json`. JSONL line numbers above are physical line numbers and remain the same in published redacted transcripts.

| Arm | Official solved | Commands | Original returned characters | Uncached input tokens | Cached input tokens | Output tokens | Total tokens | Seconds |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| No skill | Yes | 11 | 68,805 | 19,406 | 229,632 | 3,580 | 252,618 | 144.0 |
| Karpathy | No | 8 | 108,457 | 29,531 | 153,472 | 3,033 | 186,036 | 127.6 |
| Bounded-search candidate | No | 9 | 71,846 | 21,199 | 191,616 | 3,222 | 216,037 | 144.2 |
| Both (Karpathy + candidate) | Yes | 10 | 74,089 | 24,451 | 254,336 | 3,711 | 282,498 | 151.0 |

Karpathy's failure is a different contract violation: it changes an uncontaminated file. It passes removal and replacement tests, so its outcome should not be grouped with the candidate's quoting failure. Actual dollar costs remain TBD.

## Skill interpretation and next hypothesis

The frozen bounded-search change concerns finding paths/counts before reading long search matches; it does not instruct adding quotes or changing replacement syntax. The candidate's initial paths-first search at line 9 is consistent with that instruction. Its generic verification bullet asks for checks appropriate to the requested behavior. The trace supports a hypothesis that an inferred secondary property (runnable embedded shell commands) displaced a replacement-fidelity check. It cannot establish that the skill induced this choice: there is one run per arm, and Both includes the same candidate while succeeding.

A narrowly scoped next hypothesis is to clarify the existing verification guidance for literal transformations: derive the acceptance contract from the request, check that changes outside the requested transformation are necessary, and preserve non-target content unless the requested behavior requires changing it. If an optional syntax or runtime check conflicts with the requested representation, surface the conflict instead of silently adding a repair. Keep removal, scope, parsing, and other required checks; do not weaken verification to chase the reference output.

This rule is generic to configuration, redaction, migration, and data-editing tasks. It should not name this benchmark, its files, specific placeholders, or the grader's reference text. Test it on independently selected transformation tasks before any promotion. No candidate or canonical skill was changed during this diagnosis, and no model calls or retries were made.
