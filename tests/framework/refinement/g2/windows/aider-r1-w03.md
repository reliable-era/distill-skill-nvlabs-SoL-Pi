# G2 Aider round 1, bounded window 03

Standing authorization; commit time starts four hours; latest native start
commit time plus two hours, leaving the full 7200-second run allowance.
Retire all unused wave-02 allowance (48deb5b). Its worker and owned resources
are verified absent. Direct18001 only, valid running<8 with waiting allowed,
bounded ≤600s admission backoff, 60 requests / 7200 seconds / 16384 output.
No retries of cells reaching model, substitutions or shared-server changes.
Only these next six immutable scheduled cells may start:

- g2-aider-r1-t3-candidate — cpp/exercises/practice/meetup / candidate
- g2-aider-r1-t3-K — cpp/exercises/practice/meetup / K
- g2-aider-r1-t3-Both — cpp/exercises/practice/meetup / Both
- g2-aider-r1-t3-none — cpp/exercises/practice/meetup / none
- g2-aider-r1-t1-K — java/exercises/practice/transpose / K
- g2-aider-r1-t1-Both — java/exercises/practice/transpose / Both

Futility remains due after all 36 round-1 cells, never this partial wave.
No later round or Terminal inference is authorized by this window.
