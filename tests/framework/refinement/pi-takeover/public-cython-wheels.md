# Public Cython dependency wheels — offline install verified

23hashed dependency wheels (74429854bytes) prepared in original CPython3.13 task image. Existing trusted dependency lock retained;generic Cython/setuptools/wheel added from stable public releases before image-date20251031:3.1.6/80.9.0/0.45.1. Selection metadata JSON hashes retained. Building dependency wheels is permitted preparation;target pyknotid was never built/installed or included in cache.

A separate original-image probe used networknone,CAP_DROPALL,read-only wheel/requirements mounts and no-index installation. Dependency imports succeeded:NumPy2.3.0,Cython3.1.6,planarity0.6. It explicitly checked pyknotid remained absent. Cache hashes unchanged and helper containers removed. No model/native actor/benchmark control/official grader run. This verifies dependency installation,not target compilation or correctness.

Use `public-cython-wheels-binding.json` together with the existing original-source binding. Mount/environment/cache guidance must be identical for allarms and verified beforestarts. The public requirements constraint prevents drift while source/compiled target artifacts remain actor responsibility. Do not rebuild submitted pyknotid in a trusted grader to disguise missing actor installation.

Remaining gates: Doom cross-toolchain and fastText software access;complete uniform input recipe;native actor->shared capture->trusted official grader integration;fresh real-provider/backend-matched conformance and scoring. No repeated source fetch or nine-control rerun is needed.
