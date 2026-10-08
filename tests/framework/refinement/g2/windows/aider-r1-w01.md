# G2 Aider round 1, bounded window 01

Standing authorization applies to G2 by the explicit new contract (1401e9a).
This commit starts a new four-hour window; latest native start is commit time
plus two hours, preserving the full 7200-second per-run allowance. No exclusive
server use, fallback, shared changes or retries of cells that reached the model.
Retire all prior unused allowances; no G1 window is reopened. Admit running <8
with waiting allowed; finite 600-second backoff and unchanged 60/7200/16384 caps.
Only these six next preregistered cells may start:

- g2-aider-r1-t2-candidate — go/exercises/practice/connect / candidate
- g2-aider-r1-t2-none — go/exercises/practice/connect / none
- g2-aider-r1-t2-K — go/exercises/practice/connect / K
- g2-aider-r1-t2-Both — go/exercises/practice/connect / Both
- g2-aider-r1-t7-none — java/exercises/practice/queen-attack / none
- g2-aider-r1-t7-Both — java/exercises/practice/queen-attack / Both

Unstarted cells stay pending in the original order for another committed window.
No round-2 cell starts before all 36 round-1 cells and the futility decision.
