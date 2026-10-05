# Copilot version metadata diagnostic

One authorized metadata-only container start; zero prompts/provider requests/model/auth/pull/install calls. Exact native hashes matched. Version command exited1 without timeout; retained stderr reports bundled-package extraction EFBIG. Container exit0/OOMFalse and absence verified.

The diagnostic applied a64KiB RLIMIT_FSIZE to bound logs, which also constrained runtime package extraction. This changed the observation conditions: the previous mock version preflight preceded its RLIMIT. Therefore this failure cannot identify the original cause. Next metadata-only capture should cap pipe-reader buffers instead of native file sizes. No repeat performed. Raw stdout/stderr/state remain private and are hash-bound in execution-audit.json.
