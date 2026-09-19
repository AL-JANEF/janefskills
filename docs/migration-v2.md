# Migrating to JANEF Forge 2.0

JANEF Forge 2.0 consolidates janefskills 1.x, Agent Engineering Stack 1.x, and LeanCode Engineer 0.1 into one product in this repository. The plugin name and marketplace (`janefskills`) are unchanged, so existing Claude Code installs update in place.

## What changed

| Before | After |
|---|---|
| `/janef <task>`, `/janef full security pass` | `/forge <task>`, `/forge security pass` (`/janef` still works as a deprecated alias until 3.0) |
| Eight root skill directories | `skills/core/`, `skills/engineering/`, `skills/security/`, `skills/compat/` |
| `engineering-standard` | Split: truth policy and gate → core contract + `testing-verification`; forbidden list and workflow → `implementation-quality`; review checklist → `review-defect-first` |
| AES `engineering-router`, AES policy fragment, LCE `SKILL.md` | One router (`forge`) and one contract (`core/protocol/contract.md`) |
| AES `security-engineering` | Absorbed into the contract and `vuln-audit` |
| LCE references and modules | `root-cause-debugging`, `delegation-discipline`, and merged domain capabilities; LeanCode methodology lives in the `lean` profile |
| `config/skills.json` | Per-skill `capability.json` validated by `schemas/capability.schema.json` |
| Per-skill `agents/openai.yaml` | Rendered at Codex install time from `adapters/codex/interface.json` |
| `scripts/install.py --target … --force` | `scripts/install.py install --target … [--upgrade|--force]`, plus `uninstall`, `doctor`, `policy` |
| `make check` (validate + tests) | `python3 scripts/quality_gate.py` (validate, tests, evals, context gates, security scans, install and package smoke) |

## Upgrading a personal install

1. `python3 scripts/install.py doctor --target both` — lists legacy directories (`janef`, `engineering-standard`, `engineering-router`, `lean-code-engineer`, `security-engineering`) and unmanaged content.
2. `python3 scripts/install.py install --target claude --dry-run` — shows the plan. Legacy 1.x directories have no Forge marker, so replacing them needs `--force`; each is preserved as a timestamped backup.
3. `python3 scripts/install.py install --target claude --force`.
4. Optional always-on policy block: `python3 scripts/install.py policy --target claude`. This also removes the legacy `AGENT_ENGINEERING_STACK` block if present.
5. Remove legacy directories that Forge did not replace (for example `~/.claude/skills/engineering-router`) by hand after checking they contain no local edits; Forge only deletes what it installed.

## Aliases

`config/aliases.json` maps legacy names to capabilities for `--only`, `forge check`, and `forge context --skills`:

`janef`, `engineering-router`, `lean-code-engineer` → `forge` · `engineering-standard` → `implementation-quality` · `security-engineering` → `vuln-audit` · `architecture` → `architecture-integrity` · `debugging` → `root-cause-debugging` · `verification`, `testing` → `testing-verification` · `agent-orchestration` → `delegation-discipline` · `backend` → `api-contracts` · `database` → `database-integrity` · `devops`, `cloud` → `devops-reliability` · `frontend` → `frontend-design-quality` · `performance` → `performance-scalability` · `security` → `security-audit`.

## Deprecations

- `skills/compat/janef` (the `/janef` alias skill) will be removed in 3.0.
- All aliases above will be removed in 3.0.
- The AES SkillSpector installer script is not shipped; install SkillSpector from NVIDIA's repository if you want it. `skill-security-audit` uses it when present and falls back to `scripts/audit_skill.py`.

## Other repositories

`AL-JANEF/agent-engineering-stack` and `AL-JANEF/lean-code-engineer` are unchanged by this release. Archiving or redirecting them is a separate decision.
