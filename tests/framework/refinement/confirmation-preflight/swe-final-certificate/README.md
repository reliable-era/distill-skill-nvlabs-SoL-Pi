# SWE grader preflight certificate

All four fixed selected task pairs now pass their intended unchanged-negative and gold-positive controls. Fourteen total control attempts are preserved: eight validated and six failed/ungraded. This certificate is a read-only official-parser/full-ID gate recheck, not another grader run or model benchmark result.

| Task | Negative F2P failed | Negative P2P passed | Gold F2P passed | Gold P2P passed |
|---|---:|---:|---:|---:|
| astropy__astropy-13236 | 2 | 644 | 2 | 644 |
| matplotlib__matplotlib-22865 | 3 | 57 | 3 | 57 |
| psf__requests-1921 | 1 | 107 | 6 | 107 |
| scikit-learn__scikit-learn-10844 | 1 | 16 | 1 | 16 |

Requests uses an adapted isolated authentic HTTPbin/private-CA trusted setup, and Astropy uses a pinned offline bootstrap wheelhouse. Original code/tests/gold/parser and fixed task selection remain unchanged. No official leaderboard environment equivalence or model skill improvement is inferred. Certificate JSON binds reports, actual resource limits, cleanup and consumed plan/source provenance. No actor inference is authorized by this preflight certificate.
