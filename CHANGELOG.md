# Changelog

All notable changes are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/) and the project follows
[Semantic Versioning](https://semver.org/).

## [2.0.0] — Unreleased (prepared 2026-09-19, not tagged or published)

JANEF Forge: consolidation of janefskills 1.2.0, Agent Engineering Stack 1.1.0, and
LeanCode Engineer 0.1.0 into one engineering-discipline system. See
`docs/migration-v2.md` and `docs/architecture/CONVERGENCE_MATRIX.md`.

### Added
- Canonical engineering contract (`core/protocol/contract.md`) rendered into the
  `forge` entry skill and host policy fragments with drift detection.
- Machine-readable capability manifests (`capability.json`) validated by a stable
  JSON Schema and a dependency-free registry with graph integrity checks
  (duplicates, broken or cyclic dependencies, asymmetric conflicts, duplicate
  ownership, duplicate triggers, alias collisions).
- Deterministic router (`forge find` / `forge explain`) with applicability gate,
  weighted phrase triggers, negative triggers, risk estimation, profile escalation,
  and an explanation trace.
- Explicit composition model: profile caps, transitive `requires`, risk-based
  auto-includes, conflict rejection.
- Profiles `lean`, `standard`, `high-assurance` as validated data plus guidance.
- Risk-based verification model (low/medium/high/critical) shared by router, profiles,
  and `testing-verification`.
- Estimated structural context accounting (`forge context`) and a benchmark with
  CI regression gates.
- New capabilities: `forge`, `root-cause-debugging`, `delegation-discipline`,
  `security-audit`, `skill-security-audit`; merged engineering capabilities from
  Agent Engineering Stack and LeanCode Engineer modules.
- Routing evaluation corpus (115 cases across eight categories) with thresholds.
- Installer rewrite: managed-file markers with SHA-256, `--upgrade`, `uninstall`,
  `doctor`, `policy` merge for CLAUDE.md/AGENTS.md, Codex metadata rendering,
  symlink and unsafe-destination refusal.
- Static external-skill triage (`scripts/audit_skill.py`) with a reasoned allowlist.
- One canonical quality gate (`scripts/quality_gate.py`), reproducible release
  packaging with SHA-256 sums and a release-evidence record.
- Architecture, convergence, compatibility, migration, and release documentation.

### Changed
- Skills moved from the repository root to `skills/core`, `skills/engineering`,
  `skills/security`, `skills/compat`. Plugin name and marketplace remain `janefskills`.
- `janef` is now a deprecated alias for `forge`; `/janef full security pass` maps to
  `security-audit`.
- `engineering-standard` split into the contract, `implementation-quality`,
  `testing-verification`, and `review-defect-first`; kept as an alias.
- Codex `agents/openai.yaml` is generated at install time instead of stored per skill.
- CI consolidated into one workflow running the quality gate on Python 3.10/3.13.

### Removed
- `config/skills.json`, shell wrappers (`install.sh`, `test.sh`, `validate.sh`),
  `PUBLISHING.md`, and the old `docs/architecture.md` and `docs/compatibility.md`
  (replaced by the documents above).

### Deprecated
- `/janef` alias skill and all names in `config/aliases.json`; removal planned for 3.0.

## [1.2.0] — 2026-08-24

### Added
- Claude Code plugin and marketplace manifests without moving the eight existing
  skill directories.
- Codex `agents/openai.yaml` metadata for every skill.
- Safe cross-host installer with dry-run, selective installation, overwrite
  refusal, timestamped backups, and rollback.
- Repository validator, installer tests, cross-platform CI, structured issue
  templates, and release documentation.
- Privacy and retention guidance for security audit logs.

### Changed
- Installation documentation now recommends the Claude Code marketplace and
  supports Claude Code plus Codex from the same source tree.
- NoSQL and SSRF remediation examples now use strict validation and stronger DNS
  and egress guidance.
- Secret examples use unmistakable placeholders, with exact historical false
  positives documented for reproducible secret scanning.
- Copyright presentation is normalized to `ALJANEF`.

## [1.1.0] — 2026

### Added
- **`variant-hunt`** — after any finding, sweeps the whole codebase for every
  other instance of the same pattern (ripgrep + custom Semgrep rules).
- **`janef` upgraded to an audit-grade orchestrator** combining real automated
  tooling with expert review, audit methodology, and an honest coverage verdict.

## [1.0.0] — 2026

Initial public release: `janef`, `engineering-standard`, `threat-model`,
`auth-hardening`, `vuln-audit`, `secrets-guard`, `security-logging`.
