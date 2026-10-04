# Native agy cloud-tool confirmation gate

Status: **TBD / not cleared** for the pinned native CLI. Local Docker egress controls do not block provider-side search. No model requests, credential output, binary changes or replacement harness were used in this investigation.

## Local evidence

Inspected `/home/wangjian/.local/bin/agy`: stripped Linux ELF, SHA256 `a759ce7c7a235d9b6c281a25ead97cbbf2e92314a3ffd224e2f9144f3fae7a86`. `agy --help` exposes `--agent`, `--sandbox`, `--mode`, `--disable-slash-commands`, and permission bypass, but no explicit built-in tool allow/deny flag. `agy help agent` describes only listing agents; `agy help mcp` can enable/disable MCP servers, which does not establish control over built-in search/browser tools. Read-only `agy agent` with `HOME=/tmp/solpi-refinement-auth-cache/agy` exited0 without listing agents. No inference prompt was supplied. The mounted/private auth contents were not read or printed.

Binary schema strings contain `disabledTools` and `enabledTools` in MCP configuration, `allowedTools` in skill/genai/safety protobufs, and `BrowserEnabled` in multiple admin/browser protobufs. These show internal types, not a supported CLI setting or enforcement contract. Counts/strings cannot justify writing guessed configuration keys. No `enableWebSearch` or `enableBrowserTools` literal was found. Embedded SDK examples mention `CapabilitiesConfig`, but that is not evidence the CLI accepts it.

Saved agy actor init events expose native `search_web`, `read_url_content`, browser tools and browser subagents. Development traces already show web research. Tool availability plus network restrictions is not a proof those capabilities are disabled server-side.

## Primary official documentation

[Antigravity SDK tools](https://www.antigravity.google/docs/sdk/tools/) documents `CapabilitiesConfig.enabled_tools` / `disabled_tools`, with `BuiltinTools.SEARCH_WEB` and `READ_URL_CONTENT` enabled by default. This is a supported **SDK** filtering interface. It does not verify native CLI configuration, and switching our frozen CLI benchmark to an SDK actor would change source/harness fidelity. Do not silently substitute it.

[CLI permissions](https://www.antigravity.google/docs/permissions?tab=cli) documents settings-based deny/ask/allow policies and `read_url(*)` / `execute_url(*)`. URL read permissions cover URL fetching, browser navigation and terminal sandbox destinations; browser actuation has a separate permission. This provides a documented candidate restriction for those operations. It does not document a `search_web(*)` permission or establish that denying URL reads suppresses search result acquisition. Do not label it a complete cloud-search seal. Preserve explicit deny rules and avoid blanket permission bypass in any separately authorized integration test.

[CLI features](https://www.antigravity.google/docs/cli/features) documents `enableTerminalSandbox` and local command permissions. Terminal confinement is useful defense in depth, not provider-search disabling. [Browser overview](https://www.antigravity.google/docs/browser) documents a browser-tools setting on the browser/IDE surface; no binding of that setting to this pinned headless CLI was verified.

These documents are current primary-source evidence read during investigation, not version-pinned specifications for the ELF. CLI behavior at the frozen binary remains to verify. No known settings were written into actor or host HOME.

## What is verified versus unresolved

| Claim | Status |
|---|---|
| Local isolated Docker actor cannot directly fetch public tests under tested controls | Verified separately by Docker evidence; scope remains local networking |
| Official SDK can filter built-in tools | Documented, not exercised; unsuitable as an unannounced native CLI replacement |
| CLI documented URL permissions can express denials | Documented; enforcement on pinned CLI not model-tested |
| CLI URL denial disables provider-side search or inherited browser/subagent tools | **Unverified** |
| `--agent` can select a supported coding-only persona with search/browser disabled | **Unverified**; private read-only listing gave no entries |
| Native model/auth/coding fidelity retained with all external research blocked | **Not established** |

## Required next gate

Obtain an official native CLI tool-policy/agent configuration that explicitly excludes search, URL-fetch, browser and cloud-research subagents while retaining the same native coding tools/model. Bind policy to this binary/version and ensure inheritance to subagents. A separately authorized benign integration control should verify emitted tool inventory and actual denial against a nonbenchmark canary without exposing selected solutions or changing candidates. Review behavior under permission bypass and cloud-side tools; lack of local network traffic alone is insufficient evidence. If only SDK filtering is supported, report native CLI confirmation as blocked/TBD or explicitly preregister a distinct SDK benchmark rather than claiming native CLI fidelity.

Provider proxy stays necessary for shell/direct URL paths but is insufficient for server-side research. No sealed confirmation claim should proceed from this investigation alone.
