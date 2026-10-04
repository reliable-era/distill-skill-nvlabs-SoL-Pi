# Task contract

Use only when a task crosses owners or needs persistent shared state. Remove
irrelevant fields; do not expand a small fix into an administrative workflow.

- **Task / integration owner:**
- **Requested behavior and required output:**
- **Acceptance:** command or inspection criterion, including expected behavior.
- **Inputs / version:** source snapshot, paths, and agreed interfaces.
- **Owned scope:** files or artifact this worker may change.
- **Dependencies / readiness:** required input and who provides it.
- **Progress checkpoint:** concrete milestone or agreed resource limit.
- **Return:** artifact paths, changed behavior, actual checks, unmet conditions.
- **Current state / next action:**

Keep acceptance fixed unless the task owner explicitly revises the contract.
Use a checkpoint to reassess work; preserve unmet deliverables and continue
within authorized scope. Never count a submitted artifact as accepted work.
