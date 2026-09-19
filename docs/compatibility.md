# Compatibility

| Host | Status | Install path | Verified how |
|---|---|---|---|
| Claude Code 2.1.278 | **Primary** | Marketplace (`/plugin marketplace add AL-JANEF/janefskills`, `/plugin install janefskills@janefskills`), `claude --plugin-dir .`, or `python3 scripts/install.py install --target claude` | `claude plugin validate .` passes on the release commit (run in the quality gate when the CLI is present); installer tests cover managed install, upgrade, uninstall, doctor, policy merge |
| Codex | **Structure verified; behavior not yet observed** | `python3 scripts/install.py install --target codex` renders `agents/openai.yaml` per skill from `adapters/codex/interface.json` | Installer tests assert the rendered metadata and the `$CODEX_HOME/skills/<id>/SKILL.md` layout. No interactive Codex session has been recorded yet; parity is not claimed until a smoke run is added to this table |
| Cursor, OpenCode, Gemini CLI, other Agent Skills hosts | **Not supported** | Copy skill directories manually at your own risk | Nothing verified. Adapters can be added without changing skill content (see architecture § Host adapters) |

"Primary" means packaging, installer, and automated validation exist and are exercised in CI. "Structure verified" means the files Forge writes match the host's documented layout, nothing more.

## Python

Tooling is standard-library only. Supported: Python 3.10 – 3.14 (CI runs 3.10 and 3.13 on Ubuntu, 3.13 on macOS and Windows).

## Optional external tools

Referenced, never bundled or installed by Forge: Semgrep, Gitleaks, pip-audit / npm audit / cargo audit, CodeQL, NVIDIA SkillSpector (Apache-2.0; install from the upstream repository), actionlint, shellcheck. When a tool is absent, every Forge skill instructs the agent to report the layer as **NOT RUN** rather than imply coverage.

## Compatibility aliases

Legacy names resolve via `config/aliases.json` in the installer (`--only`), `forge check`, and `forge context --skills`. `/janef` remains available as a deprecated alias skill. See `docs/migration-v2.md`.
