#!/usr/bin/env python3
"""Grade finished SWE-bench agent runs with the official harness; writes graded.json next to each run."""
import json, subprocess, sys
from collections import defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
RUNS = HERE / "runs" / "swebench"

groups = defaultdict(list)
for res in RUNS.glob("*/*/r*/result.json"):
    run = res.parent
    if (run / "graded.json").exists():
        continue
    r = json.loads(res.read_text())
    groups[(r["arm"], r["round"])].append((r["instance_id"], run))

for (arm, rnd), items in sorted(groups.items()):
    tag = arm.replace("+", "-")
    run_id = f"{tag}-r{rnd}"
    preds = HERE / "grading" / f"{run_id}.jsonl"
    preds.parent.mkdir(exist_ok=True)
    preds.write_text("".join(json.dumps({"instance_id": iid, "model_name_or_path": tag,
                                         "model_patch": (run / "patch.diff").read_text()}) + "\n"
                             for iid, run in items))
    subprocess.run([sys.executable, "-m", "swebench.harness.run_evaluation",
                    "--dataset_name", "princeton-nlp/SWE-bench_Verified",
                    "--predictions_path", str(preds), "--run_id", run_id,
                    "--instance_ids", *[i for i, _ in items],
                    "--max_workers", "8", "--namespace", "swebench", "--cache_level", "instance"],
                   cwd=HERE / "grading", check=False)
    for iid, run in items:
        rep = HERE / "grading" / "logs" / "run_evaluation" / run_id / tag / iid / "report.json"
        if rep.exists():
            resolved = json.loads(rep.read_text())[iid]["resolved"]
        elif not (run / "patch.diff").read_text().strip():
            resolved = False  # empty patch: harness skips it, counts as unresolved
        else:
            print("no report for", run); continue
        (run / "graded.json").write_text(json.dumps({"resolved": resolved}))
        print(run_id, iid, resolved)
