Diagnostic suite v1: five mechanism families, one development and one held-out fixture each.

Cases are intentionally small dependency-free Python repositories. All use genuine
functional hidden invariants; no tests inspect prose, tool strategy, or skill wording.
Only repo/ and prompt.txt enter the agent container. hidden/ and reference/ must
remain outside it until after agent completion. Do not copy the whole case directory.

Families:
d1_large_log: 14,000 realistic worker status lines, actionable middle partial-batch
error, public test only covers exact batches. Tests include empty and partial batches.
d2_interfaces: shared producer/consumer contract with trim and Unicode casefold.
d3_stale_resume: outdated continuation conflicts with current percent contract.
d4_integrated_failure: name normalization and complete name preservation in export;
public tests expose both layers, hidden tests cover empty/single/multiword components.
d5_small_control: direct pagination fix where skill-loading overhead may dominate.

Dev and heldout vary module/symbol names, Unicode examples, numeric cases and log error
location. They deliberately share mechanism and structure, so heldout measures transfer
within these families, not general real-world capability. Task solutions are short;
there is no native compaction implementation, no interruption of a running session,
and no enforced repeated investigation. d2 supplies multiple relevant modules but
cannot force the agent to repeat work. These limitations matter when interpreting cost.

Selection is fixed before model runs; include all five families and all failed runs.
Seeds 42/73/101 should randomize execution order and, if backend supports it, sampling;
otherwise call them independent rounds rather than claiming backend RNG control.
Use identical fixture files for all arms and rounds; manifest.json pins SHA256 per file.
Do not tune skill using heldout results. If any heldout feedback reaches skill author,
mark the resulting skill unvalidated and generate a new prospectively pinned holdout.

Validation: python eval/pruned/diagnostics/build.py regenerates fixtures and validates
buggy hidden tests fail (exit 1) and reference public + hidden tests pass (exit 0).
Reference files overlay the buggy repo in a temporary directory. Manifest records
exit codes and pass counts. Do not regenerate during active runs.
