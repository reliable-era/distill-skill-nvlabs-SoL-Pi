# Repository default CA — verified read-only copy

One authorized cached-image container was created and never started. Only the two requested repository files were copied with single-file safe tar checks, capped at one MiB. The 308,978 content bytes include certs.py and the 149-root original CA bundle. Actual network-none, read-only filesystem, one CPU/512 MiB and verified removal are recorded in execution-audit.json. No HTTP, test, grader, model, build or pull occurred.

The repository certs.where function selects adjacent cacert.pem, proving the default path /testbed/requests/cacert.pem. Its bytes/hash match the previously inspected installed bundle exactly. Source/code/tests are unchanged. A separately prepared additive public-CA overlay now has a verified target; no control execution is authorized by this copy phase.
