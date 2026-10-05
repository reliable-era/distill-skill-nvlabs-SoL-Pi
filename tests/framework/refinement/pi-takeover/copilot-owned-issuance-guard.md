# Owned-issuer cutoff guard — new offline prototype, not deployed

Added copilot_owned_issuance_guard.py/test_copilot_owned_issuance_guard.py;7new testsPASS/0native/provider/model/process/networkcalls. One narrow mechanism: synchronous known-HTTP-length truncation detection closes admission, calls exact-owned stop, durably records verification result, then permits exception/EOF teardown. No native retry knob, sharedserverpatch, epoch bypass or replacement actor. Actual existing prospective_owned_epoch.stop reused in tests with fakeDocker: current arm/deadline/exactcontainerID/image/ownedname and stopped-state checks; wrongID rejects BEFOREstop. Existing unchanged ownership controls not rerun.

Tests cover byte-write→ownedstop→receipt→EOFteardown ordering; HTTP-complete no unnecessary stop; unknown length failclosed; sticky unverified stop/no repeated kill; admittedcap/deniedcounter; actual existing stopfunction identity checks. Failed callback closes admission and raises unsafe-boundary error; not a verified stop. Caller MUSTbind exact currentownedprocess/epoch and bound callback latency. Negative result cached before invoking callback, preventing repeated arbitrary stop. No loose PID/name-only action implemented.

## Boundaries

Only prototype/knownHTTPContentLength supported. No actual native integration, chunked unknownlengthSSE completion, providerusage extraction or passive drain proof. It stops on unknownlength rather than pretending completeness. Acceptedrequest admission cap is NOTproof nativeallPOSTheaders never exceed cap; deniedrequests tracked and can still make all-attemptgate fail. Thread ordering tested synchronously with controlled mocks, not live transport/client concurrency. StockCLI/skills unchanged; no benchmark or actualQwen generation.

Native cutoff fixture's prior4attempts/3denials/30sSIGTERM/emptyusage remains immutable/negative. This software does not retrospectively eliminate retries, invent responseusage, regrade or turn cleanup into model performance. Missing providerusage remains unavailable despite ownedstop success; any future realactor still requires independentreceipts and capture/originalgrading.

## Next integration

Separately freeze a host-owned broker/controller that binds existing identity-checked stop to exact created container/current epoch, journals partial response/usage BEFOREstopping, and closes native-facing EOF only after stop verified. Reuse existing bounded drain/failure-safe persistence and stoppedartifact capture. Account every admitted/deniedheader; do not claim totalcap compliance from admissioncap alone. A native zero-inference gate would be distinct changedbehavior and must preserve oldnegatives and exact scopedlimits; none launched/authorized by this prototype artifact. No unchangedpositive/cutoffprobererun or implicit realQwen/schedulerbudget renewal.

Canonical unchanged, fixed9/89/twosources/localQwen scope intact, noactiveworker/candidateunstarted/schedulerwait0. ActualQwen/realfullaccounting/delivery/quality/economy/majorityconfirmation stillunverified; goal incomplete.
