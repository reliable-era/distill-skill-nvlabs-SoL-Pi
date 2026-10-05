# Read-only fastText failure-path diagnosis and prospective gates

Original stage c4e1e285… remains immutable:2starts31POST/447594knownlowerbound+unknown31/candidateofficial0of2/BothcapturegradeUNAVAILABLE/noneKUNSTARTED. No native/actor/model/gold/test reruns, no recovered cost/grade, no canonical/live/shared service changes. Allownedstagecontainers/networksremoved. `coalesced-fasttext-failure-audit.json` coversALLstartedtraffic, unlike singlegradedcell audit249808 alone.

## Capture: historical exact cause remains unavailable

Pinned artifact_capture.py guard collapses four predicates into `unexpected member,type,name,or size`: count!=1, unexpectedbasename, nonregulartype/negative size, or size beyondfrozenbound. Bothcapture.json hasEMPTY artifacts/no payload/no durabletarheader, and actor removed. Neither native training messages nor that genericerror proves oversize/symlink/path/multiplemembers. Don't infer grade0, reconstructmissingmodel, rerunactor, raise160MiB bound, or useoracle output. Added UNDEPLOYED `prospective_capture_rejection.py` classifies sameguard predicates using boundedheader-onlyreason/index/namehash+length/type/size/no payload/no grade inference. It is NOTintegrated into scoredcapturer; originalfileunchanged.

## Accounting: failure cleanup bypasses passive completion

Pinned generatedcontroller stops actor atdeadline reserve, then immediatelycaptures. Exception on capture exits before `session.finish(True)`/accountingrows and goes to `finally`: stopproxy→removeownedcontainers→`session.abort_owned_connections()`→servercleanup. There is NOexplicit passive-drain gate before thatabort. Nominal240s completion-grace policy bounds request forwarding but doesn't ensure harvesting when earlier capture/grading fails. This is an evidence-backed lifecycle gap, NOT proof of exacthistorical stack.

Request31 raw evidence:HTTP200/26.243s/191902bytes/AttributeError/EOFfalse/usageunavailable/actor_budget_exhaustionfalse. Rawstream contains reasoningdeltas/no terminalusage;bridgefinalviewconsumer_detached=true. RawSession.abort shuts down socket and calls HTTPConnection.close() while forward thread canstill read. Python HTTPResponse._read1_chunked calls `_get_chunk_left` then `self.fp.read1`; closingtrackedresponse between those steps setsfpNone. Oldjournal storesexceptionCLASSonly/no traceback; historical exact31cause cannotbeproven, and abort couldalso be a consequence of anothererror. Missing cost remainsunknown.

## ONEcontrolled model-free proof, limited scope

`reproduce_completion_close_race.py`/`completion-close-race-proof.json`: realLOCALHTTP1.1 chunked upstream + deterministic barrier after_get_chunk_left, oneoldearly-close versusoneprospectivedrain-before-close. Old reproduces `'NoneType' object has no attribute 'read1'`/noEOF; new waits.050s/ACK/EOF/ownedworkersclosed. 0realmodel/native/scoredactor/benchmark/gold. InitialHTTP1.0 fixturedidNOTproduceerror becausewill-close semantics don'tretaintrackedresponse; prechangeexactsource+failure record retained `reproduce_completion_close_race_http10.py`/http10-failure.json. Thus HTTP1.1 mechanism proven, nothistoricalbackendresponse/stack or fullSession/SSE/native integration. Proofdeadlineassertionsameobject isnotindependentsnapshot; drain itself latchedandchecksimmutableepoch, and NEWunit test independentlysnapshotsdeadline/posts. No performance/quality/usage-recovery claim.

`prospective_completion_drain.py` UNDEPLOYED: stopactor/issuance first; latchactiveactor+ORIGINALdeadline+posts; waitconnection count AND forward_lock (so derivedledgerfinish notmistakenforconnectionclosure) untilORIGINALdeadline-10+240; rejectepoch/newPOSTchange; no retry/continuation/deadlineextension/newforward. If unresolved atcap markusageunavailable, then boundedownedabort. Eight `test_failure_path_diagnostics.py` tests PASS: completion/independentdeadline/posts conservation,expiredunknown,actor/postchanges,nonfinitefailclosed,writerbusy,exactcaptureboundary/distinctheaderreasons/no payload. Greens cover helper boundaries ONLY.

## Next bounded action

Before any new scored phase or resumingunstartednone/K: ONEfullmodel-free integration of helper against hash-pinned privateSession/SSE/broker on capture-error path with realfakeupstream: prove raw+derived EOF/completeFAKEusage harvested afteractorstop BEFOREproxy/connection teardown; no newActor/POST/deadline/semanticoutputrepair; finiteexpiredbranch stillpreservesunavailableusage; strictbody/source/epoch/cleanup. Prospectivecapture header classifier needsintegration gate too. Do NOTrepeatpastcompletednative/race/goldcontrols unchanged; newtestscoverchangedfailurepath. No oldcapture recovery or request31 reprice. If gatesfail, stopwithproof/blocker; no realmodel/protocolbudget escalation.

Fullrepresentative/fullcandidate9/majority3of5/3independentrounds/ALL3paired95%/≥5%complete-tokenpersolve/noqualityloss/USD/exposure/promotion requirements stillUNVERIFIED. GoalACTIVE—notcomplete.
