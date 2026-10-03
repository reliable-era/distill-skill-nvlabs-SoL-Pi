#!/usr/bin/env python3
"""Drive the whole matrix: stress suite (3 rounds) then SWE-bench subset (2 rounds); arm order seeded per cell."""
import random, subprocess, sys
from pathlib import Path

HERE = Path(__file__).resolve().parent
ARMS = ["sol-pi", "baseline", "karpathy", "karpathy+sol-pi"]
STRESS = ["s1_small_fix", "s2_large_log", "s3_fabricated_quote", "s4_edit_then_fail", "s5_continuation"]
SWE = (HERE / "tasks" / "swebench_verified_12.txt").read_text().split()
rng = random.Random(42)
py = sys.executable

for rnd in (1, 2, 3):
    for case in STRESS:
        for arm in rng.sample(ARMS, len(ARMS)):
            subprocess.run([py, "run_stress.py", case, arm, str(rnd)], cwd=HERE)
for rnd in (1, 2):
    for iid in SWE:
        for arm in rng.sample(ARMS, len(ARMS)):
            subprocess.run([py, "run_swe.py", iid, arm, str(rnd)], cwd=HERE)
    subprocess.run([py, "grade_swe.py"], cwd=HERE)
print("ALL DONE")
