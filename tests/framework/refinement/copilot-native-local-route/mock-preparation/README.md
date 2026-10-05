# Prepared native Copilot routing-only mock

Executed once: failed before any container or native start because the private Unix-socket path was too long. Eight offline guard tests pass; `run_mock.py` without `--launch` validates frozen sources without Docker starts or provider requests. Exact root authorization is required for launch.

The sole cached native Copilot 1.0.91 container uses network `none`, 1 CPU, 512 MiB, 128 PIDs, read-only rootfs, ALL capabilities dropped, no-new-privileges and a fresh empty HOME. The environment supplies no account/provider credentials. Native documented proxy variables target localhost; copied generic Python proxy components accept only `provider.example:8000` and relay solely to an owned Unix socket. They do not assume a Node runtime. The host mock returns HTTP400 and performs no inference.

Limits: one native start, 30 seconds native process, 45 seconds worker/container, 40 seconds cleanup, 256 KiB request, 2 MiB upstream tunnel, 1 MiB native output file. Worker owns and terminates the native process group; outer cleanup removes and verifies the owned container, drains the Docker client, closes broker sockets and records worker/socket absence. All raw bodies/logs remain private; the broker publishes only request body hashes/counts/status to private artifacts.

**Caps:** two accepted/body-read mock POSTs, at most sixteen accepted broker connections, and four active handlers. Every parsed POST header, including refused attempts, is counted separately. Accepted sockets get a three-second timeout before header parsing; outer cleanup closes all tracked sockets and proves zero workers. Root must review before execution. Native HTTP/CONNECT routing compatibility and offline usage-file emission remain untested. This fake400 probe cannot establish successful model support or complete gross token accounting.

The prior zero-call source and plan are retained in `superseded-zero-call-v1`. No plan is retroactively bound to an executed attempt. This phase changes neither harness identity nor the primary denominator.

Native worker verifies the actual installed loader and platform ELF SHA against the parent audit before any prompt. Routing PASS is computed only after successful container/client/broker/socket cleanup proofs and accepted fake400 statuses with the fixed provider authority.

The container runs as the frozen host UID:GID owning the private directories/socket; actual Config.User must match before start. Root with dropped capabilities is not used for these host-owned mounts.

Execution audit: 114-byte Unix socket path rejected at broker construction; native starts/POSTs/model calls all zero. Owned container and socket absence verified independently. No retry or repair was run. The plan, runner and authorization remain unchanged.
