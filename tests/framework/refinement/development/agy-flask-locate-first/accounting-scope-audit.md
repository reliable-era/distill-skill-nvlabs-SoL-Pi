# Native agy accounting scope

Read-only audit, 2026-10-04; zero additional model calls. Frozen results and plans are unchanged. Machine evidence is in [accounting-scope-audit.json](accounting-scope-audit.json).

All 18 saved streams (four Flask, six Go, eight synthetic pilot) have a terminal counter vector equal to the sum of unique usage-bearing steps, deduplicated by conversation ID and step index. Each terminal has one user turn. Repeated ACTIVE/DONE events must not be summed; terminal counters must not be added to step counters. All 18 report `total_tokens = input_tokens + output_tokens`. The pilot with 2,158 thinking tokens satisfies the same equation. This arithmetic does not establish whether thinking is included in output or omitted from SDK total; thinking/output containment remains TBD. Preserve the separately reported thinking counter without blindly adding it.

The [official headless documentation](https://www.antigravity.google/docs/cli/headless/) describes usage as cumulative over a session. Its resumed-turn example reports input 278, cache read 30,214, output 4, total 282 for a step; the session terminal accumulates the preceding turn. Its other example accumulates an agent response and checkpoint. This supports the observed serialized SDK arithmetic and a separately reported cache counter. It does not by itself prove semantic disjointness between input and cache categories across all implementations. Documentation is current, rather than verified implementation source for our pinned 1.2.16 ELF. Official distribution repository reference: commit `65a3c69e388148c9327f307efe82ddb1c0c8d7d4`; implementation correspondence remains TBD.

| Flask arm | SDK input | SDK output | SDK cache read | SDK total |
|---|---:|---:|---:|---:|
| No skill |329429|4118|747762|333547|
| Karpathy |194310|2359|401362|196669|
| Locate-first |166636|1743|149996|168379|
| Both |141771|1528|113555|143299|

These are SDK-reported counters, not dollars. The SDK total arithmetic does not add the cache counter, but semantic input/cache disjointness and whether thinking is included in output remain TBD. Summing these fields does not establish complete provider traffic coverage: hidden retries, cache writes, internal requests, and billing conversion remain TBD. A separately labeled arithmetic sum could describe reported input/output/cache counters only; it must not become a gross-traffic acceptance gate without implementation or provider proof. SDK ERROR in prior Go retains observed partial counters; completeness of failed-attempt cost remains TBD. None of these findings changes independent correctness grading.

Consequently, retain existing figures as **SDK-reported total tokens**, show cache separately, and leave complete gross traffic and monetary savings TBD. Cross-harness counters need matching definitions before ranking economics. The candidate’s 49.5%/14.4% reductions against No skill/Karpathy and 17.5% increase against Both refer only to SDK totals in this one exposed development fixture.

Category-definition check: the official headless field table lists counters without defining containment. The pinned official repository recursive tree contains documentation, issue templates and shell status/title examples, but no SDK usage-mapping implementation. The changelog describes cache reporting for prompt-cache attribution without defining input/cache disjointness. No primary definition tied to our 1.2.16 native binary was located; output/thinking and input/cache containment therefore remain TBD. Third-party billing mappings are not evidence for this binary.
