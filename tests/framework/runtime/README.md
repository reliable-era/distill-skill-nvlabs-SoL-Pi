# Agent containers and login

The source Node image contains Codex, GitHub Copilot CLI, Pi, OpenCode, Gemini CLI, OpenClaw, Cursor Agent CLI, and the Claude Code reference. Hermes is built in a Python source image, then both are combined into `sol-pi-eval-all:2026-10-03` for one shared evaluation toolchain. Installation and CLI help were checked without credentials or model requests; authenticated execution and accounting validation are **TBD**.

```sh
docker build -t sol-pi-eval-agents:2026-10-03 tests/framework/runtime
docker build -f tests/framework/runtime/Dockerfile.hermes -t sol-pi-eval-hermes:2026-10-03 tests/framework/runtime
docker build --network none -f tests/framework/runtime/Dockerfile.all -t sol-pi-eval-all:2026-10-03 tests/framework/runtime
```

The context contains only runtime files. Credentials never enter the build. Containers run as `evaluator` (UID 1000), with `HOME=/home/evaluator`. The runner mounts the task at `/workspace`; no Docker socket is mounted. Cursor's pinned Linux x64 download has an explicit SHA256 check; other architectures are TBD. npm top-level versions, Cursor archive checksum, and Hermes source commit are pinned; transitive npm dependencies and base image digests are not yet locked, so byte-identical rebuilds are TBD. Save the image digest with each campaign.

## Human login

List the available login commands with `python3 tests/framework/auth.py list`. Launch a human-operated login with `python3 tests/framework/auth.py login codex`, or add `--print-only` to see the Docker commands. This creates a separate volume for each login. Do not mount your ordinary home directory. Example:

```sh
docker volume create sol-pi-auth-codex
docker run --init --rm -it --mount type=volume,src=sol-pi-auth-codex,dst=/home/evaluator sol-pi-eval-all:2026-10-03 codex login --device-auth
```

Replace `codex` in the volume name and the final command using this table. Logins need network access and human interaction. The offline validation did not run these login commands.

| Agent | Login inside its container | Credential for isolated evaluation |
|---|---|---|
| Codex | `codex login --device-auth` | `.codex/auth.json` in dedicated volume |
| GitHub Copilot CLI | `copilot login` | `COPILOT_GITHUB_TOKEN` in private env-file; OAuth config import TBD |
| Pi | `pi`, then `/login` | `.pi/agent/auth.json` in dedicated volume, or provider API key |
| OpenCode | `opencode auth login` | `.local/share/opencode/auth.json` in dedicated volume |
| Gemini CLI | `gemini`, choose Google login | `GEMINI_API_KEY` recommended; Google OAuth headless auth-type selection TBD |
| OpenClaw | Provider API key | `OPENAI_API_KEY`, `ANTHROPIC_API_KEY`, or `GEMINI_API_KEY`; `agent exec --auth-env-only` |
| Cursor Agent CLI | `cursor-agent login` | `CURSOR_API_KEY` in private env-file; OAuth keychain import TBD |
| Hermes Agent | `hermes setup` | Provider API-key env-file or `.hermes/auth.json`; actual provider configuration TBD until login |
| Claude Code reference | `claude auth login` | `.claude/.credentials.json`, or `ANTHROPIC_API_KEY` |

Google Antigravity is a distinct product/harness. Gemini CLI is not Antigravity; a native Antigravity adapter and its container workflow are **TBD**. A Pi model provider named Antigravity would still be a Pi harness run.

For evaluation, mount the dedicated auth volume read-only at `/auth` instead of mounting it at HOME. The entrypoint copies only the allowlisted credential files into the container's disposable home. It does not import skills, memories, histories, hooks, or ordinary user preferences. Copilot's combined configuration file and Hermes' mixed `.env` file are deliberately excluded. Credentials refresh in the disposable home and are discarded after the run; refresh the login volume interactively if required.

```sh
# Authentication status only; no inference.
docker run --init --rm --mount type=volume,src=sol-pi-auth-codex,dst=/auth,readonly sol-pi-eval-all:2026-10-03 codex login status
```

For environment authentication, create a local file with mode `0600` containing only the required variable (never commit it), and pass `--env-file /absolute/private/agent.env`. The framework does not echo its contents. Inference is launched explicitly after human-provided authentication and freezing a campaign budget.

## Official references

- [Codex CLI](https://developers.openai.com/codex/cli/reference)
- [Copilot authentication](https://docs.github.com/en/copilot/how-tos/copilot-cli/set-up-copilot-cli/authenticate-copilot-cli) and [programmatic flags](https://docs.github.com/en/copilot/reference/copilot-cli-reference/cli-programmatic-reference)
- [Pi source and usage](https://github.com/earendil-works/pi)
- [OpenCode commands](https://opencode.ai/v2/docs/cli/commands/)
- [Gemini authentication](https://geminicli.com/docs/get-started/authentication/)
- [OpenClaw isolated agent execution](https://docs.openclaw.ai/cli/agent)
- [Cursor CLI](https://cursor.com/docs/cli)
- [Hermes source](https://github.com/NousResearch/hermes-agent)
- [Claude Code CLI](https://code.claude.com/docs/en/cli-reference)

Actual installed command help and versions are preserved in `probes.json` and `hermes-probes.json`. CLI probes establish installation readiness, not task quality or cost-accounting completeness.
