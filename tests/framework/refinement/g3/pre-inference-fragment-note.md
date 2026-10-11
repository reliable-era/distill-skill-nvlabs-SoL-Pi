# Pre-inference bounded fragment implementation clarification

No model calls yet. Freeze5d9ca19 full queue/seeds/math/arms unchanged.
Add explicit max-primary bound(default72) to each rolling18-slot window,
so an initial fixed36-cell fragment can verify actual receipts/runtime before
more inference. It is not a pilot, extra sample, stop gate or treatment-selected
schedule: all attempted cells count toward the same784-cell round in exact
frozen order; all784 needed before futility and no early win. Later fragments
continue remaining queue. Once-only infra retries do not alter primary roster.
Record updated scheduler SHA in plan before first call; preserve old introducing
freeze commit in history. No cells/results yet, no preregistered outcome change.
