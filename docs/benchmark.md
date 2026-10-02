
for the follow select one , limit the scope  of dataset ,  for example, dataset size is 100, its smallest dataset for this repo is 1/10 . 


**I recommend SWE-bench Verified as the primary benchmark, plus a small stress suite for evidence handling.** Add Terminal-Bench 4.0 to check whether the savings transfer to broader terminal tasks.
i


| Benchmark | What it evaluates | Role for this bundle |
|---|---|---|
| [SWE-bench Verified](https://www.swebench.com/verified.html) | 500 human-validated repository issues | **Primary:** does the agent fix issues correctly at lower cost? :chatgpt-content-reference{index="0"} |
| [Terminal-Bench 4.0](https://www.tbench.ai/news/terminal-bench-4-0) | Terminal-agent tasks with calibrated environments and resources | **Secondary:** tool use, debugging, and longer execution workflows. Pin the dataset version. :chatgpt-content-reference{index="1"} |
| [SWE-Bench Pro V2](https://labs.scale.com/leaderboard/swe_bench_pro_public_v2) | More demanding, long-horizon software engineering; refreshed public split of 642 tasks | **Later:** test context management on harder repository work. :chatgpt-content-reference{index="2"} |
| [EdgeBench](https://edge-bench.org/) | Extended environment-learning tasks; 51 public tasks | **Optional:** closest comparison with the SoL-Pi paper, which evaluated this public set. :chatgpt-content-reference{index="3"} |
| Custom stress suite | Controlled log, continuation, and verification cases | **Required supplement:** isolates the bundle’s specific mechanisms. |

For the custom suite, include these cases:

| Case | Required outcome |
|---|---|
| Small, straightforward fix | Correct completion without excessive planning overhead |
| Large log with the decisive error in its middle | Recall the omitted evidence and repair correctly |
| Fabricated quote or modified archive | Reject the receipt and recover original evidence |
| Successful edit followed by failing tests | Continue repairing; never report completion |
| Interrupted task with a continuation note | Resume without losing requirements or repeating substantial work |
| Worker handoff, in a separately authorized multi-agent track | Owner verifies and integrates the result |

**Run a matched A/B comparison:** the same agent without the bundle versus the same agent with it. Keep the model, reasoning level, tools, repository snapshot, budgets, and acceptance tests identical. Use fresh workspaces and sessions, charge skill-loading overhead, and keep grading tests outside the agent’s control.

Measure:

- **Verified resolution rate**—the quality constraint.
- **Total API cost**, including failed attempts, retries, reducers, and compaction.
- **Cost per verified solved task:** total cost across all attempts ÷ verified solved tasks.
- Uncached input, cache reads, cache writes, output tokens, model requests, and wall time.
- False completion claims and evidence-recovery failures.

Start with **20–30 SWE-bench Verified tasks and 10 stress cases**, then repeat each condition three times. Freeze the bundle before expanding to a larger held-out evaluation; report paired differences and uncertainty.

The existing helper tests establish correctness of the archive and accounting utilities. **They do not yet demonstrate token savings.** The bundle succeeds when it lowers whole-task cost while preserving verified completion quality.

