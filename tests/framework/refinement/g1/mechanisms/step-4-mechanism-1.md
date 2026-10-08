# Step 4: measured sink and candidate 1 — bounded reasoning/action loop

Source inventory: development-sink-inventory.json, produced read-only by
analyze_development_sinks.py from all three G1 calibration cohorts and the
explicit exposed historical trace prefixes listed there. Eleven historical
roots were discovered; ten contain ledgers, one is marked unavailable. These
are descriptive separate cohorts, not a pooled performance estimate. No old
stage entrypoint, output-contract stage, excluded harness or sealed model
trace was read/executed. Candidate count: one new mechanism so far; two slots
remain, and no additional mechanism is authorized by a failed single-task test.

## Ranked measured sinks

1. **Accumulated reasoning/trajectory input dominates complete gross cost.**
   Input fractions for the verified-solvable G1 tasks are HTML 97.25%, TeX
   96.79%, food-chain 96.34%, SPARQL recovery 93.44%. Request body grows from
   29,952 to 352,581 bytes across 38 HTML requests; 29,752 to 354,659 across
   33 TeX requests; 32,104 to 105,007 across 18 Go requests; 30,676 to 253,049
   across 13 SPARQL recovery requests. In HTML's final native input list,
   reasoning items occupy 245,655 serialized bytes versus 34,205 function
   output bytes. TeX's final list has 247,324 reasoning-item bytes versus
   47,383 function-output bytes. These bytes include serialized summary,
   content and encrypted fields, not a token attribution or causal estimate.
   Native completed reasoning text totals 117,459 chars for HTML and 117,045
   for TeX; both generate long history before returning tool actions.
2. **Command outputs also remain in subsequent history.** G1 tool-output
   totals and request item growth are recorded per native trace/request.
   Pure read versus mutation/test classification is only a shell-regex proxy:
   heredocs and compound commands overlap; do not claim these are pure reads.
   Canonical skill already addresses output shortening/batching, so a duplicate
   reread clause is not selected merely because those proxies are numerous.
3. **Exact repeated commands are not the dominant observed sink.** There are
   no exact command repeats in the G1 HTML/TeX/Go traces and one in SPARQL
   recovery. Necessary changed-code rechecks cannot be inferred from these
   counts. The candidate will not skip required tests or rely on a purported
   repeated-command saving unsupported by this inventory.

Regex is a special case: one call, 16,382 output tokens/45,554 reasoning chars,
no tool action or artifact. Its failure supports the risk of unbounded mental
case enumeration, but it is not a solvable screening task and is not rerun.
The initial SPARQL 429 interruption and six failed zero-model startups are
preserved separately; they are not skill-effect observations.

## Mechanism

Candidate 1 adds exactly one bullet to the unchanged canonical skill:

> Before the next tool call, reason only to the next concrete decision. Do not
> re-derive settled facts or mentally enumerate many cases across long turns;
> use a small executable probe when uncertainty can be checked locally. Act on
> the decisive result, keeping the required correctness checks and repairs.

This targets generation of long reasoning items that subsequently recur in
input, not removal of already-sent history. It introduces no task cards,
extra agents, compaction, runtime context rewriting, model-cap changes or
benchmark-specific solutions. Supporting files are copied unchanged from the
canonical skill. The canonical skill itself remains unchanged.

Expected development target: approximately 25% or greater reduction in complete
tokens per verified solve versus all three comparators with no solve loss. If
reasoning-related future history were roughly halved, the observed large byte
share makes that magnitude plausible; bytes are not tokens and this is a
hypothesis, not measured savings. A four-arm screen is necessary and may reject
it if the model ignores the instruction, probes add work, or quality decreases.

Candidate SKILL SHA256:
e11948951958094ea411a5da55610c9ba8f68404d352950830a35d7c4161096d
Canonical SKILL SHA256:
68ea78dcb9ee8a565f99c8a1b8bfec13f4c6d65c5695ce847eb5577b0449b1ef

## Predeclared screen tasks and decision

Take the first three task IDs in sorted order from the four-task verified
No-skill pool: break-filter-js-from-html, go/exercises/practice/food-chain,
overfull-hbox. This gives two Terminal tasks and one Aider/Go task, all verified
solvable with the frozen caps; SPARQL remains eligible but is not substituted by
candidate outcome. Use fresh matched No skill / frozen Karpathy / candidate /
same candidate + Karpathy cells, one round each. Prior calibration grades or
costs cannot be borrowed for the controls. Retain every failed or unknown-cost
cell; no retries chosen for low score, heavy load or high spend. Keep original
graders, role isolation, routes, resource profiles and per-run caps identical
across arms; use precommitted bounded windows.

Screen ratio = total complete tokens over all attempts divided by verified
solves, candidate compared with each comparator on the same tasks. Candidate
must not lose solved count overall or within a represented family. Seek about
25% savings against all three; point screens do not satisfy B3(a) confirmation.
If this fails, classify improvement/quality before considering another measured
mechanism; stop after two consecutive non-improving candidates or no qualifying
candidate within three. No sealed model cell before committed winner freeze.
