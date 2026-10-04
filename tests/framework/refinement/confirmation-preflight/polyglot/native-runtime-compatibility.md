# Native runtime compatibility

All four pinned language control images already contain usable Codex and Pi installations. Offline version probes pass both through their existing entry points and through the explicit `/usr/local/bin/node` runtime. No new actor image or executable mount is required for CLI startup. This is startup compatibility evidence only; authentication, model access, agent execution, and task success remain untested.

| Track | Existing image ID | Explicit Node | Codex | Pi |
| --- | --- | --- | --- | --- |
| java | `sha256:95b20c222db5063b990a542842c4a286fa2d82dec5abb1b4775b2d16bd8a5b0c` | 24.21.0 | 0.160.0 | 1.0.0 |
| cpp | `sha256:3d73526aba5c3e157473cd374780f426fa6209ad3c3633956ad55ef1ead0c676` | 24.21.0 | 0.160.0 | 1.0.0 |
| go | `sha256:be1506c27383f1294c827041f4705d45a7342ca01273e7fbb47ff69df875b118` | 24.21.0 | 0.160.0 | 1.0.0 |
| rust | `sha256:a712c8a6efaddd4cbc6da50152c544f7b9b8f586c3847948e2d0c652966aa4d4` | 24.21.0 | 0.160.0 | 1.0.0 |

The inherited PATH resolves `node` to `/opt/cursor/bin/node` (24.5.0); the separately pinned `/usr/local/bin/node` is 24.21.0. Both routes pass these version probes. A future frozen actor plan should explicitly select its Node route to avoid silently changing the runtime. Codex emits a warning about refusing helper alias creation under temporary HOME; its version command still exits successfully. A private writable HOME outside `/tmp` should be specified by the actor plan and checked separately without treating this version probe as an auth check.

Full probe commands, stdout, stderr, image IDs, selected control summary hash, dataset/harness revisions, CLI entry file hashes, native Codex binary hashes, and both Node hashes are in `native-runtime-probes.json`. Containers had networking disabled and no credential, task, test, reference, or skill mounts. Frozen controls and selected task content were unchanged. No model calls or authentication calls occurred.
