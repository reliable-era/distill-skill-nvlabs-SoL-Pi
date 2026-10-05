# Qwen load balancer on gpu02 and gpu01

OpenAI-compatible endpoint: **http://127.0.0.1:8000/v1** on gpu02.
Port 18080 remains a compatibility alias.

The model is Qwen3.8-27B-FP8 with Qwen3.8-27B-DFlash2 speculation.
Each request runs on one TP2 replica. Each host has two replicas; the service
has four replicas across eight GPUs.

| Host | GPUs | Backend | NCCL P2P |
| --- | --- | --- | --- |
| gpu02 | 0/1 | 127.0.0.1:18001 | Disabled; NCCL shared memory |
| gpu02 | 2/3 | 127.0.0.1:18002 | Enabled automatically |
| gpu01 | 0/1 | 10.193.104.97:18001 | Disabled; NCCL shared memory |
| gpu01 | 2/3 | 10.193.104.97:18002 | Disabled; NCCL shared memory |

## Serving settings

All four replicas use:

```text
--tp-size 2
--context-length 262144
--max-total-tokens 262144
--mem-fraction-static 0.90
--max-running-requests 8
--max-mamba-cache-size 48
--chunked-prefill-size 2048
--disable-prefill-cuda-graph
--reasoning-parser qwen3
--tool-call-parser qwen3_coder
--speculative-algorithm DFLASH
--speculative-draft-model-quantization fp8
--speculative-num-draft-tokens 8
```

Eight requests is the initial concurrency cap per replica, giving a configured
cap of 16 per host and 32 across both hosts. All requests share each replica's
262,144-token pool, so very long requests reduce actual concurrency. This is a
validated starting configuration, not a claim that eight is the throughput optimum
for every workload. Startup leaves approximately 7 GiB free per GPU.

Both gpu01 replicas and gpu02 GPU0/1 also use `--disable-custom-all-reduce` and
`NCCL_P2P_DISABLE=1`. gpu02 GPU2/3 retains its working custom all-reduce settings.
This preserves the hardware-specific collective choices; it does not imply
identical numerical outputs across replicas.

## Deployment and operation

On gpu01, weights are in `/data/a/wj/models`; scripts and separate per-replica
caches are in `/data/a/wj/qwen38-load-balancer`. `start-gpu01.sh` is copied there
as `start.sh`. Run `bash /data/a/wj/qwen38-load-balancer/start.sh` on gpu01 to
start the existing containers. The immutable base image is
`sha256:6305caa4b7bb7159ae4f079e24fdf628fafa5c208fe048ddfb44a8652e7c8efd`.
Both model directories were reconciled against the gpu02 source with rsync
checksums. The extra local image layer contains caches rather than SGLang
source changes. `sglang-source-config.json` records the original launch settings.

Containers restart unless stopped. `PYTHONDONTWRITEBYTECODE=1` avoids slow
bytecode writes during startup. gpu01 binds the private interface 10.193.104.97;
UFW permits ports 18001 and 18002 only from gpu02 (10.193.104.167).

Nginx uses weighted `least_conn`, with streaming/request buffering disabled and automatic
request retries disabled. Capacity weights were updated on 2026-10-05:

| Host | GPUs | Weight | Measured output tokens/s |
| --- | --- | ---: | ---: |
| gpu02 | 2/3 | 12 | 329.0 |
| gpu02 | 0/1 | 11 | 290.9 |
| gpu01 | 2/3 | 10 | 284.9 |
| gpu01 | 0/1 | 10 | 273.6 |

The measurements used eight concurrent requests per replica, two rounds of 16
requests, approximately 925 prompt tokens and 256 output tokens per request.
All four replicas ran simultaneously with live client traffic continuing.
These are initial capacity estimates for this workload. The weight formula is
`round(10 * capacity / minimum_capacity)`; weighted least-connections also
accounts for active connections, so actual shares vary with request duration
and load. GPU01 GPU0/1 has a nominal idle share of 10/43 (23.3%).
`nginx-weight-capacity-benchmark.json` contains the measurements;
`nginx-weight-update.json` records the backup, weights and verification.
Nginx syntax passed, 43 model-list requests routed 12/11/10/10, and streaming
responses with final usage succeeded through all four backends.
[NGINX least_conn documentation](https://nginx.org/en/docs/http/ngx_http_upstream_module.html#least_conn)
describes weight handling. These weights do not change the SGLang concurrency caps.
 `X-Solpi-Upstream` identifies the selected backend.
Logs contain routing metadata, not request bodies or authorization headers.
Nginx sees only traffic routed through it, not direct backend requests.

The read-only helper on 127.0.0.1:18003 aggregates `/get_load` for all four
replicas. It returns 503 if any backend is unavailable or malformed, including
during a rolling restart. `/healthz` describes configuration; it is not a
backend readiness check.

This dedicated Nginx daemon and load helper have no host-reboot autostart.
Only test/reload this instance, from this directory:

```sh
/usr/sbin/nginx -p /tmp/solpi-qwen-load-balancer-18080/ -c "$PWD/nginx.conf" -t
/usr/sbin/nginx -p /tmp/solpi-qwen-load-balancer-18080/ -c "$PWD/nginx.conf" -s reload
```

`update_concurrency.py` drained the gpu02 replicas one at a time, snapshotted
stopped writable layers, and preserved the original Docker settings and model
flags while changing the two concurrency/cache flags. Stopped backups have
restart disabled. `gpu02-concurrency-update.json` records their names and private
configuration backup directory. `gpu01-rollback.json` records the original Nginx
and helper backups. Drain requests before any rollback and operate only on the
identified containers and dedicated Nginx instance.

## GPU0/1 TP1 comparison (2026-10-05)

Two independent TP1 FP8/DFLASH containers were tested with a 32K context,
`--max-running-requests 2`, `--max-mamba-cache-size 16` and
`--mem-fraction-static 0.91` per GPU. Each had 3,470 MiB free after startup.
The original TP2 used a 262K context and eight running requests.

| Client concurrency | TP2 output tokens/s | Two TP1 output tokens/s |
| --- | ---: | ---: |
| 1 | 85.1 | 53.1 |
| 4 | 235.9 | 181.1 |
| 8 | 332.8 | 185.2 |

The workload used approximately 925 prompt tokens and fixed 256-token outputs,
with unique prefixes, temperature zero and EOS ignored. Both layouts were
isolated from gateway traffic. These results favor TP2 for this batch workload;
they do not establish an optimum for other request distributions.
`gpu02-layout-comparison.json` records the settings and raw evidence.
The TP1 containers are stopped with restart disabled; TP2 is restored in the
main pool. `start-gpu02-tp1.sh` is an experimental launch configuration and must
only run after draining/stopping the conflicting GPU0/1 TP2 container.
`gpu02-tp1-rollback.json` identifies the private configuration backups.

Fresh generation requests through the gpu02 gateway returned HTTP 200 from
both gpu01 backends; see `gpu01-nginx-routing-verification.json`.
After restoration, `gpu02-post-layout-verification.json` confirms streaming
generation with final usage from all four backends and four aggregate load rows.

## Verification and historical artifacts

- `gpu01-nccl-result.json`: four-GPU NCCL correctness and timing; actual transport
  was shared memory, despite CUDA reporting peer access for every pair.
- `gpu02-nccl-pair-results.json`: GPU2/3 P2P/CUMEM passed; GPU0/1 P2P/CUMEM and
  P2P/IPC stalled, while its P2P-disabled shared-memory test passed.
- `gpu02-nccl-idle-retest.json`: the requested GPU0/1 retest with its SGLang
  workload drained and stopped. Both GPUs had 1 MiB used and 0% utilization;
  P2P/CUMEM still timed out after 150 seconds. Serving was restored afterward.
- `gpu01-readiness-verification.json`: direct model-list, load and streaming
  generation checks on both remote replicas, including final token usage.
- `gpu01-concurrency-verification.json` and `gpu02-concurrency-verification.json`:
  eight concurrent 128-token generations per replica, peak active requests and
  startup memory. These are readiness checks, not steady-state benchmarks; the
  gpu02 checks ran alongside existing client traffic.
- `gpu01-deployment.json`: final deployment, current flags and routing checks.

The Oct 4 `deployment.json`, `migration.json`, and `port8000-verification.json`
are historical evidence for the initial two-backend deployment, not the current
configuration. The old four-arm evaluation panel finished before that migration;
its artifacts were preserved. New evaluations must record the current replica,
configuration and backend header rather than pooling old direct-route results.
