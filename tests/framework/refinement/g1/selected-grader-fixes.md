# Selected-task grader fixes

The user authorized only task-required repairs, with about two hours of fixes per
selected task, no replacement and no repetition of passing control pairs.
The repair start is recorded in selected-fix-budget.json.

## C++ meetup

Original metadata lists meetup.cpp and meetup.h but supplies only .meta/example.h.
The adapter now maps that official header to meetup.h and leaves the original
starter translation unit in the reference workspace. No reference body or task
answer was reconstructed. This special case applies only to selected meetup.

The first compiled pair failed because the base grader image lacked Boost.
Both original exit-1 records remain unchanged. They are infrastructure failures,
not evidence that a correctly running grader rejected the starter. The grader now
classifies the missing-Boost diagnostic as infrastructure failure (exit 2).
The selected-task image adds only libboost-date-time-dev, with image ID recorded
in cpp-meetup-repair.json. Only the invalid C++ pair was repeated; the repaired
starter rejects and the unmodified official reference passes. Cleanup verified.

## JavaScript alphametics

The adapter is restricted to this selected JavaScript task. It copies the original
npm-test.sh from pinned Aider revision 5dc9490bb35f9729ef2c95d00a19ccd30c26339c.
The script enables xtest cases and runs the original npm test command.
The dependency cache was built from the original package.json, with install
scripts disabled. Exact package and generated lock hashes are recorded in
javascript-dependencies.json. Two pre-install mount-permission failures are
retained; no npm installation or model inference occurred in those attempts.
The successful installation uses no host credentials or model configuration.

Grading mounts dependencies read-only, runs with network disabled, restores
original tests and overlays only configured solution files. Accepted-test counting
uses Jest's passed-test count; zero executed tests cannot be a success.
The starter rejects and official reference passes. Both controls and hashes are
recorded in polyglot-remaining-result.json, with raw logs kept private.

## Reuse and limits

The three initial passing pairs were not repeated. Five other previously unstarted
pairs passed in the remaining phase. These records plus the repaired C++ pair
cover all nine Aider tasks. Separate phases and failures remain distinct; no
model outcomes or costs were borrowed, and no confirmation model traces exist.
These controls establish grader/environment validity, not skill performance.
The selected Terminal-Bench control worker remains a separate, bounded phase.
Step 2 is incomplete until every selected task's official gold/no-op pair is valid,
cleanup is verified, and the completion audit and commit are made.
