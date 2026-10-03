# Codex four-arm pilot

Two existing held-out synthetic fixtures (`d2_interfaces`, `d5_small_control`), four instruction configurations, one round. This is a harness smoke pilot, not a published benchmark or a general ranking.

Native OpenAI ChatGPT OAuth backend, explicitly configured `gpt-6.1-sol`. Actor: shared pinned trial image. Grader: independent network-disabled Docker container with pytest 9.1.1 and only hidden grader/workspace mounts. Credential-only ephemeral HOME; no host instructions, config, memory, or history.

Instructions enter through identical prompt wrapping for both skill arms. `both/SKILL.md` concatenates frozen Karpathy guidance and the canonical current skill; its supporting resources are the current skill bundle. Native skill-discovery overhead is not measured.

`plan.json` freezes task inputs, skill resources, order, images, and an eight-attempt / 1,300-second cap. Model random seed is uncontrolled. All attempts count toward reported economics, unknown billing stays TBD. Temporary auth volume must be recreated from credential-only data to rerun.

```bash
python3 tests/framework/run.py freeze tests/framework/trials/codex/campaign.json --output /private/new-plan.json
python3 tests/framework/run.py run /private/new-plan.json --output /private/new-results
```

See `results/summary.md`, result records, redacted actor logs, and external grader logs.

All eight attempts completed and passed external hidden tests. Observed total tokens per solve: no skill 66,811; Karpathy 89,775.5; ours 69,870; both 83,157.5. All terminal token fields were present, including cache-write zero. Dollar cost remains TBD for subscription billing. The tiny pilot cannot establish statistical superiority or stability. Temporary credential volume was removed after execution.
