# Notice

JANEF Forge is an independent open-source project by ALJANEF. It is not an official
OpenAI or Anthropic product and is not endorsed by either company. References to
Claude Code, Codex, Semgrep, Gitleaks, NVIDIA SkillSpector, and other tools are
nominative references to compatible or optional tooling; their licenses apply.

## Provenance

JANEF Forge 2.0.0 consolidates three MIT-licensed projects by the same author. The
copyright notices below are preserved as required by the MIT license. Full
per-capability provenance is in `docs/architecture/CONVERGENCE_MATRIX.md` and in the
`provenance` field of every `capability.json`.

| Source | Version imported | Commit | Copyright |
|---|---|---|---|
| AL-JANEF/janefskills | 1.2.0 | 915adf6 | Copyright (c) 2026 ALJANEF (janefskills) |
| AL-JANEF/agent-engineering-stack | 1.1.0 | 22f7b66 | Copyright (c) 2026 Agent Engineering Stack contributors |
| AL-JANEF/lean-code-engineer | 0.1.0 | 2cbf56f | Copyright (c) 2026 ALJANEF |

Git history of `janefskills` is preserved in this repository (skill files were moved
with `git mv`). The other two repositories' histories were not imported; see
`docs/architecture/JANEF_FORGE_ARCHITECTURE.md` § "History and provenance" for the
trade-off and the exact source commits.

## Third-party tools (not bundled)

NVIDIA SkillSpector (Apache-2.0), Semgrep, Gitleaks, pip-audit, npm audit, and CodeQL
are referenced as optional external tools. Nothing here installs or vendors them.
