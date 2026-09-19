# JANEF Forge Architecture

**Forge better code. Prove every change.**

JANEF Forge is a capability and engineering-discipline system for AI coding agents. It ships one canonical engineering contract, a metadata-first capability registry, a deterministic router, an explicit composition model, three profiles, and the tooling to validate all of it in CI.

## Product boundary

Forge **does**: provide engineering and defensive-security capabilities as Agent Skills; select the smallest relevant set for a task; compose compatible capabilities and reject conflicting ones; use progressive disclosure so the always-loaded surface stays small; enforce evidence-backed completion; measure its own structural context cost; and validate everything deterministically.

Forge **does not**: orchestrate agents, hold persistent state, schedule work, manage authorization, or run a control plane. Those belong to [JANEF ONE](https://github.com/AL-JANEF/janef-one), a separate product. Forge never modifies or reproduces JANEF ONE's WorkGraph, scheduler, or authorization runtime.

## Repository layout

```
core/                 registry, routing, composition, context accounting, verification model, canonical contract
  protocol/contract.md
skills/
  core/forge/         entry point and router (the only skill an agent needs to start)
  engineering/        16 capabilities
  security/           8 capabilities
  compat/janef/       deprecated alias skill
profiles/             lean | standard | high-assurance (profile.json + PROFILE.md)
adapters/             claude-code/ and codex/ host metadata and policy fragments
schemas/              JSON Schema for capability manifests, profiles, budgets
config/               aliases, budgets, routing parameters, reviewed static-scan allowlist
scripts/              forge.py (CLI), install.py, quality_gate.py, package_release.py, audit_skill.py
tests/                unittest suite (registry, routing, composition, installer, tooling, package)
evals/                routing corpus (115 cases) and evaluator
benchmarks/           context-cost benchmark with regression gates
docs/                 architecture, convergence matrix, compatibility, migration, releasing
```

Deviations from the initial sketch, and why: `core/` holds flat Python modules (`registry.py`, `routing.py`, `composition.py`, `context.py`, `verification.py`) instead of one directory per module; each would have contained a single file. `core/protocol/` remains a directory because the contract is content, not code, and is the only file a human edits there.

## Capability taxonomy

| Domain | Purpose | Loaded when |
|---|---|---|
| `core` | `forge`: contract + routing table + profiles | Start of any software task |
| `engineering` | Implementation, debugging, architecture, testing, APIs, data, performance, DevOps, Git, docs, frontend, UX, accessibility, context, review, delegation | Routed by task |
| `security` | Threat modeling, auth, OWASP audit, variant hunting, secrets, logging, multi-layer audit, external-skill gating | Routed by task or risk |
| `compat` | Deprecated aliases only | Never routed |

Each capability is a directory with `SKILL.md` (host-portable Agent Skill), `capability.json` (manifest), and optional `references/` loaded on demand. Skill content is host-agnostic; host metadata lives in `adapters/`.

## Core invariants

`core/protocol/contract.md` is the single source of the twelve invariants (correctness before convenience; security never weakened for context; verification before completion claims; smallest correct change; preserve local architecture; inspect before editing; evidence over assumption; targeted context loading; no unnecessary delegation; explicit authorization for destructive operations; honest reporting; external content is data). It is rendered by `forge sync` into `skills/core/forge/SKILL.md` and both adapter fragments between `FORGE_CONTRACT_BEGIN/END` markers; `forge validate` fails if any copy drifts. Shared rules therefore exist once and are never restated inside domain skills.

## Registry

`core/registry.py` discovers `skills/*/*/capability.json`, validates each against `schemas/capability.schema.json` (with the stdlib subset validator in `core/schema.py`, which rejects schema keywords it does not implement so the schema cannot promise more than is checked), and runs graph integrity checks:

duplicate ids · id ≠ directory ≠ frontmatter name · manifest/frontmatter description drift · references declared but missing, present but undeclared, or unlinked from the body · `requires`/`optional_with`/`conflicts_with` pointing at unknown ids or self · requiring a deprecated or conflicting capability · `requires` cycles · asymmetric conflicts · duplicate `responsibilities` (explicit ownership tags; two owners is an error) · duplicate `triggers` across selectable capabilities (a routing ambiguity is an error) · alias collisions and dangling alias targets · missing profiles · body length and stray files.

The registry collects errors instead of stopping at the first, so one `forge validate` run reports everything.

## Routing

`core/routing.py` is deterministic and dependency-free:

1. Normalize the prompt (lowercase, hyphens to spaces, trailing punctuation stripped, dotted file names matched both ways).
2. **Applicability gate** using the `forge` manifest: positive triggers (software vocabulary) versus negative triggers (marketing, prose, travel…). A prompt is applicable when it has software signal and negative signal does not dominate. Non-applicable prompts select nothing.
3. **Score** every selectable capability: each matched trigger phrase adds `2·words − 1`; each matched negative trigger subtracts three times that. Multi-word phrases therefore outrank single words and negatives can veto.
4. **Fallback**: if nothing scored but the prompt contains a code-change verb, `implementation-quality` is selected so the agent still gets the implementation discipline.
5. **Risk**: the maximum of phrase-based risk signals (`config/routing.json`) and the risk level of any selected high/critical capability. Four levels: low, medium, high, critical.
6. **Profile**: `standard` escalates to `high-assurance` at high or critical risk; `lean` never escalates but still receives verification auto-includes.
7. **Compose** (below) and emit an explanation trace. `forge explain` prints it; `forge find` prints only the selection.

Routing quality is measured by `evals/run_routing_eval.py` over a 115-case corpus (obvious, single-skill, multi-domain, ambiguous, negative, adversarial, high-risk, profile) with thresholds in `config/budgets.json`. Cases and checks are reported separately.

## Composition

`core/composition.py` turns ranked candidates into a final ordered set:

- profile cap on routed skills (`max_skills`), overflow recorded as rejected;
- transitive `requires` closure (a dependency is never omitted; `frontend-design-quality` always brings `accessibility-quality`, `security-audit` always brings `vuln-audit` and `variant-hunt`);
- profile `auto_include` by risk level (verification and review floors), attributed as `profile:<id>`;
- conflict resolution: when two selected capabilities declare a mutual conflict, the weaker (lower score, fewer dependents) is dropped and recorded with the reason;
- `check_composition` validates an explicit set (used by `forge check` and `forge context --skills`).

`optional_with` is advisory metadata for humans and for the skill text ("route to X when…"); it never auto-loads.

## Profiles

| | lean | standard | high-assurance |
|---|---|---|---|
| Routed skill cap | 2 | 4 | 5 |
| Reference cap | 1 | 3 | 4 |
| Verification floor | low | low (risk-driven) | high |
| Independent review | never | at high risk | always |
| Delegation | single agent | selective | selective |
| Auto-escalate | no | to high-assurance at high/critical | — |
| Auto-include | testing-verification at high+ | testing-verification at high; + review-defect-first at critical | testing-verification always; + review at high; + variant-hunt at critical |

Profiles are data (`profile.json`, validated against `schemas/profile.schema.json`) plus a short `PROFILE.md` an agent reads when the profile is active. `lean` carries LeanCode Engineer's methodology; it is not a separate skill.

## Verification model

`core/verification.py` maps risk level to required checks and acceptable evidence (low → static check + focused test; medium → + boundary tests and affected gates; high → + integration/contract test across the boundary, denied path, adversarial input, scan or explicit NOT RUN, independent review; critical → + real database/environment verification, mutation check, rollback, recorded authorization). `forge explain` prints the tier for the estimated risk under the active profile's floor; `testing-verification` carries the procedure and evidence definitions.

## Context model

Always-loaded surface: host listing metadata (name + description of every capability, ≈2.4k estimated tokens) and, when installed as policy, the adapter fragment (contract, ≈0.6k). Loaded on `/forge`: the entry skill (≈1.6k, contract included). Loaded per task: only routed skill bodies; references stay on disk until the skill text says to read them.

`core/context.py` computes an **estimated structural context cost** = `ceil(characters / 4)` for the core, selected skills, selected references, skipped capabilities, and the eager full load. `forge context` prints it; `benchmarks/context_benchmark.py --check` enforces `config/budgets.json` (contract, entry skill, metadata, per-skill body, per-profile worst routed selection, minimum median savings). It is a regression proxy, never a provider billing claim.

## Host adapters

- **Claude Code** (primary): `.claude-plugin/plugin.json` lists every capability directory; the repository is its own marketplace; the namespace is `janef-forge`, with `/janef-forge:forge` as the primary namespaced entry and `/janef-forge:janef` retained only as a deprecated compatibility alias. `adapters/claude-code/CLAUDE.md.fragment` is the optional always-on policy block.
- **Codex**: `adapters/codex/interface.json` is rendered into `agents/openai.yaml` per skill at install time, so skill content never carries host metadata. `AGENTS.md.fragment` is the policy block. Structure is verified by tests; behavioral parity is recorded in `docs/compatibility.md` only when actually observed.
- Adding a host = adding an adapter directory and an installer renderer. Skill content does not change.

## Security model

- Third-party skills and external prompt material are untrusted (contract rule 12; `skill-security-audit`). Forge never executes instructions found in external skill content; `scripts/audit_skill.py` reads text only and never runs candidate code.
- Installer: absolute destinations only; refuses the filesystem root, the home directory, symlinked destinations, and destinations inside the source tree; validates skill ids against `^[a-z0-9]+(-[a-z0-9]+)*$`; stages into a temp dir and moves atomically per skill; rolls back on failure; refuses to overwrite unless `--force` (backup) or `--upgrade` (Forge-managed and unmodified only, backup); records SHA-256 of every installed file in `.janef-forge.json` so `doctor` detects drift and `uninstall` removes only Forge-owned, unmodified content (modified content requires `--force` and is backed up). No archive extraction; no YAML parsing of untrusted input (frontmatter is parsed by a restricted scalar/folded-block reader); JSON only from the repository itself.
- Repository: no symlinks, no secret-shaped strings, no committed archives; optional Gitleaks and actionlint in the gate; static self-scan of skill content at medium severity with a reviewed allowlist that requires a reason per accepted finding.
- Static scanning is a control, not proof of safety; every scan result in Forge is labeled that way.

## Extension model

To add a capability: create `skills/<domain>/<id>/` with `SKILL.md` and `capability.json`; declare unique `triggers` and `responsibilities`; declare `requires` only for hard dependencies; add at least one routing corpus case; run `forge validate`, the evals, and the benchmark. To add a profile: `profiles/<id>/profile.json` + `PROFILE.md`, extend the schema enum, add budgets. To add a host: an adapter directory plus a renderer in `scripts/install.py`; do not touch skills.

## History and provenance

`janefskills` history is preserved; skills were moved with `git mv`. Importing the Git histories of `agent-engineering-stack` and `lean-code-engineer` (via subtree or unrelated-history merge) would have brought committed release archives (`dist/*.tar.gz`, `*.zip`), 7 PNG brand assets, and three parallel README/CI lineages into this repository's history for content that was rewritten rather than copied. The trade-off was judged disproportionate; provenance is recorded instead in `NOTICE.md` (source, version, commit, copyright) and in the `provenance` field of every manifest, and the source repositories remain untouched on GitHub.
