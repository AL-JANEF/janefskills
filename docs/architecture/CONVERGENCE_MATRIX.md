# Convergence Matrix

Technical convergence audit of the three source repositories into JANEF Forge 2.0.0.
Every skill, module, reference, script, and policy surface is listed with its decision.
No capability disappears silently: every row has a target and a decision.

Decisions: **KEEP** (moved, content preserved) · **MERGE** (combined with another source into one canonical capability) · **ABSORB** (unique content folded into a stronger capability or the core contract; source ceases to exist as a unit) · **REWRITE** (concept kept, text rewritten for the new architecture) · **DEPRECATE** (kept only as a compatibility alias, removed in 3.0).

Sources: **JS** = janefskills 1.2.0 (`915adf6`) · **AES** = agent-engineering-stack 1.1.0 (`22f7b66`) · **LCE** = lean-code-engineer 0.1.0 (`2cbf56f`).

## Routing, orchestration, and core policy

| Source unit | Current responsibility | Overlap | Unique value | Target | Decision |
|---|---|---|---|---|---|
| JS `janef` (SKILL.md) | Command layer: routes to specialists, runs full audit-grade security pass, suite reference index | Routing duplicates AES `engineering-router` and LCE context router; reference index duplicates README | Multi-layer security pass, honesty gate, coverage verdict | `forge` (routing), `security-audit` (full pass) | MERGE; `janef` name → DEPRECATE (alias skill `skills/compat/janef`) |
| JS `janef/references/orchestration.md` | Exact scanner commands, install one-liners, degraded-mode handling | None | Real tooling procedure | `security-audit/references/orchestration.md` | KEEP |
| JS `janef/references/audit-methodology.md` | Variant analysis, fix verification, timing review | Partly `variant-hunt` | Fix verification and constant-time review method | `security-audit/references/audit-methodology.md` | KEEP |
| AES `engineering-router` | Classify task, load smallest skill set, process rules | Duplicates JS `janef` routing and LCE router | Route-by-concern table across engineering domains | `forge` routing table + `core/routing.py` | MERGE |
| AES `adapters/*/*.fragment` (global policy block) | Always-on engineering defaults for CLAUDE.md / AGENTS.md | Duplicates JS `engineering-standard` truth policy and LCE `SKILL.md` guardrails | Priority order, "never weaken a guard", inspect Git before/after | `core/protocol/contract.md`, rendered into `adapters/*/*.fragment` | MERGE |
| LCE `SKILL.md` (core loop, priority order, guardrails, completion gate) | Lean entrypoint and context router | Duplicates AES policy fragment and JS engineering-standard | Priority order wording, single-agent default, "load only what changes the next decision" | `core/protocol/contract.md` + `profiles/lean` | MERGE; `lean-code-engineer` name → DEPRECATE (alias → `forge`) |
| LCE `config/routing.json` + `scripts/route_context.py` | Signal-based reference/module router with caps | Duplicates AES `agent-skill-find.py` | Deterministic scoring, activation gate, negative signals, caps | `core/routing.py`, `core/composition.py`, per-manifest `triggers` / `negative_triggers` | REWRITE |
| AES `scripts/agent-skill-find.py` | Rank skills by query terms with alias expansion | Duplicates LCE router | Alias expansion idea | `core/routing.py` (phrase weighting), `config/aliases.json` | ABSORB |
| LCE `references/context-efficiency.md` | Load-by-decision, stop conditions, honest estimates | Overlaps AES `context-efficiency` | Stop conditions, "spend context where risk lives" | `context-efficiency` skill + contract rule 8 | MERGE |
| LCE `references/agent-orchestration.md` | Delegation selection gate, cost check, safe delegation contract | None in JS/AES | The whole gate | `delegation-discipline` (new) + contract rule 9 | REWRITE |
| LCE `scripts/benchmark.py`, `docs/benchmarking.md` | Character-based context estimate with gates | None | Honest estimate framing, regression gates | `core/context.py`, `benchmarks/context_benchmark.py`, `config/budgets.json` | REWRITE |

## Engineering domain

| Source unit | Current responsibility | Overlap | Unique value | Target | Decision |
|---|---|---|---|---|---|
| JS `engineering-standard` | Truth policy, workflow, forbidden list, red-team review, completion gate | Truth policy ≈ AES fragment; gate ≈ AES `testing-verification`; review ≈ AES `review-defect-first` | Forbidden-pattern list, refuse-unsafe-work rule, per-stack gate commands, evidence definitions | Truth policy → contract rules 3/11 and `testing-verification`; forbidden list + workflow → `implementation-quality`; gate → `testing-verification/references/completion-gate.md`; review checklist → `review-defect-first/references/review-checklist.md` | ABSORB; name → DEPRECATE (alias → `implementation-quality`) |
| AES `implementation-quality` | Production-code rules | JS engineering-standard, LCE engineering.md | Compatibility/migration-path rule, root-cause-before-patch | `implementation-quality` | MERGE |
| LCE `references/engineering.md` | Establish contract, smallest slice, manage uncertainty, review diff | AES implementation-quality | "Least irreversible design", diff review checklist | `implementation-quality` | ABSORB |
| LCE `references/debugging.md` | Evidence loop for failures | None | Entire debugging method | `root-cause-debugging` (new) | REWRITE |
| AES `architecture-integrity` | Boundaries, dependency direction, no unnecessary infra | LCE architecture.md | "Do not introduce a service/queue/cache unless…", validate against reality | `architecture-integrity` | MERGE |
| LCE `references/architecture.md` | Decision frame, design rules, when to write an ADR | AES architecture-integrity | Decision frame questions, ADR criteria | `architecture-integrity` | ABSORB |
| AES `testing-verification` | Risk-based test selection, never weaken tests, evidence | JS gate, LCE verification.md, LCE testing module | "Mock only unstable boundaries" | `testing-verification` | MERGE |
| LCE `references/verification.md` | Risk ladder, evidence rules | AES testing-verification | Five-step ladder, "a passing test proves only what it asserts" | `testing-verification` | ABSORB |
| LCE `modules/testing` | Test boundary choice, strong tests, flakiness | AES testing-verification | Flaky-test classification and quarantine rule | `testing-verification` | ABSORB |
| AES `api-contracts` | Contract rules, webhooks, idempotency, versioning | LCE backend module | Webhook authenticity/replay, contract tests | `api-contracts` | MERGE |
| LCE `modules/backend` | Contracts, reliability (outbox, at-least-once), verification | AES api-contracts | Outbox/compensation, at-least-once delivery, observability distinction | `api-contracts` | ABSORB |
| AES `database-integrity` | Schema/migration risk, constraints, RLS, backfills | LCE database module, JS engineering-standard DB discipline | Deploy-compatible migrations, write amplification | `database-integrity` | MERGE |
| LCE `modules/database` | Invariants in constraints, expand/migrate/contract, verification | AES database-integrity | Expand/migrate/contract phases, "ORM convenience is syntax" | `database-integrity` | ABSORB |
| AES `performance-scalability` | Measure hot path, frontend/backend metrics, evidence | LCE performance module | Capacity/endurance/spike/recovery distinction | `performance-scalability` | MERGE |
| LCE `modules/performance` | Measure first, optimize order, verify variance | AES performance-scalability | "Bound caches by tenant/security scope", variance reporting | `performance-scalability` | ABSORB |
| AES `devops-reliability` | CI/CD, IaC, rollout/rollback, backups | LCE devops + cloud modules | "Backups incomplete without restore verification" | `devops-reliability` | MERGE |
| LCE `modules/devops` | Supply chain, delivery, operations | AES devops-reliability | Artifact promotion, "separate validation from mutation" | `devops-reliability` | ABSORB |
| LCE `modules/cloud` | Service choice, IAM, networking, reliability/cost | AES devops-reliability (partial) | Workload identity, blast-radius separation, RPO/RTO, unit cost | `devops-reliability` (Cloud and IAM section) | ABSORB |
| AES `git-discipline` | Git safety and hygiene | Contract rule 10 | Conflict-resolution rule, no artifacts committed | `git-discipline` | KEEP (rewritten prose) |
| AES `documentation-integrity` | Document verified reality | None | "Update the existing source of truth" | `documentation-integrity` | KEEP (rewritten prose) |
| AES `frontend-design-quality` | Visual direction, states, motion, verification | LCE frontend module | Anti-generic-aesthetic rule, state list | `frontend-design-quality` (requires `accessibility-quality`) | MERGE |
| LCE `modules/frontend` | Boundaries, state separation, a11y, race-safe updates | AES frontend + accessibility | Server-authoritative permissions, state kinds, cancellation for stale updates | `frontend-design-quality` + `accessibility-quality` | ABSORB |
| AES `ui-ux-quality` | Flow clarity, forms, destructive-action safety | None | The whole flow discipline | `ui-ux-quality` | KEEP (rewritten prose) |
| AES `accessibility-quality` | Semantic HTML, keyboard, contrast, motion | LCE frontend a11y bullets | Complete a11y rule set | `accessibility-quality` | KEEP (rewritten prose) |
| AES `context-efficiency` | Search-before-read, no rereads, deterministic scripts | LCE context-efficiency.md, contract rule 8 | Tool-output hygiene tactics | `context-efficiency` | MERGE |
| AES `review-defect-first` | Defect-only review, severity ordering | JS engineering-standard review checklist | "No qualifying defect is valid", confirm from a real code path | `review-defect-first` | MERGE |

## Security domain

| Source unit | Current responsibility | Overlap | Unique value | Target | Decision |
|---|---|---|---|---|---|
| JS `threat-model` + 2 references | STRIDE at design time | LCE security module "scope the threat"; AES security-engineering bullet 1 | Full method, prompts, worked example | `threat-model` | KEEP |
| JS `auth-hardening` + 2 references | Login, sessions, passwords, tokens, MFA | AES security-engineering (authn/authz bullets) | Logout-doesn't-revoke-JWT class, session patterns | `auth-hardening` (+ roles/permissions triggers) | KEEP |
| JS `vuln-audit` + 2 references | OWASP Top 10 detection and remediation | AES security-engineering, LCE security.md hazards | Before/after remediations, OWASP map | `vuln-audit` | KEEP |
| JS `variant-hunt` + 1 reference | Sweep for siblings of a finding | None | Entire method, Semgrep rule patterns | `variant-hunt` (required by `security-audit`) | KEEP |
| JS `secrets-guard` + 2 references | Secret hygiene and leak response | AES security-engineering bullet 6 | Client-bundle prefix trap, rotate-first response | `secrets-guard` | KEEP |
| JS `security-logging` + 2 references | Audit trails, redaction, detection | None | Privacy/retention guidance, detection rules | `security-logging` | KEEP |
| AES `security-engineering` | Generic secure-change checklist | ≈ 80 % covered by `vuln-audit`, `auth-hardening`, `secrets-guard`, `threat-model`, contract rule 2 | "Treat agent/tool outputs as untrusted", "never weaken a control to pass" | Contract rules 2 and 12; remaining hazards → `vuln-audit` | ABSORB; name → DEPRECATE (alias → `vuln-audit`) |
| LCE `references/security.md` | Threat-first checklist, hazards, agent/tool safety | vuln-audit, threat-model, contract | Path/symlink/archive handling, "test one denied path and one adversarial input" | `vuln-audit`, `core/verification.py` high tier, contract rule 12 | ABSORB |
| LCE `modules/security` | Scope threat, remediation, evidence | threat-model, vuln-audit, variant-hunt | "Fix the violated invariant at the narrowest shared boundary", coordinated-disclosure note | `vuln-audit`, `variant-hunt` | ABSORB |
| AES `skill-security-audit` | Gate for external skills/plugins/MCP | None | Whole gate, SkillSpector integration, fail-closed rule | `skill-security-audit` | KEEP (rewritten prose) |
| AES `scripts/audit-skill.py` | Deterministic static triage | None | Pattern set | `scripts/audit_skill.py` (+ symlink, pipe-to-shell, hidden-content, allowlist with reasons) | REWRITE |
| AES `scripts/install-skillspector.sh`, `docs/integrations/skillspector.md` | Install NVIDIA SkillSpector wrappers | None | Wrapper procedure | Not shipped; documented as optional external tool in `skill-security-audit` and `docs/compatibility.md` | DEPRECATE (install steps referenced upstream; no third-party installer shipped) |

## Tooling, packaging, and repository surfaces

| Source unit | Current responsibility | Overlap | Unique value | Target | Decision |
|---|---|---|---|---|---|
| JS `scripts/install.py` | Safe installer: refuse overwrite, backup on `--force`, rollback | LCE `install.sh` (same semantics) | Staged copy + rollback | `scripts/install.py` (+ managed-file markers, upgrade, uninstall, doctor, Codex metadata rendering, policy merge) | REWRITE |
| LCE `scripts/install.sh` | Same for one skill | JS installer | Unsafe-destination refusal | `scripts/install.py` destination checks | ABSORB |
| AES `scripts/bootstrap-global-policy.sh` / `uninstall-global-policy.sh` | Merge policy block into CLAUDE.md/AGENTS.md with markers and backup | None | Marker-block merge | `scripts/install.py policy` (also removes the legacy AES block) | REWRITE |
| JS `scripts/validate.py`, AES `scripts/validate.py`, LCE `scripts/validate.py` | Repository invariants | Three validators | Link checking, frontmatter checks, symlink/placeholder checks | `core/registry.py` + `scripts/forge.py validate` | MERGE |
| AES `agent-stack-doctor.py` | Manifest and tool check | None | Optional-tool report | `scripts/forge.py doctor` | ABSORB |
| AES `scripts/package-release.sh` | zip/tar + SHA256SUMS | None | Release archive shape | `scripts/package_release.py` (reproducible, evidence record) | REWRITE |
| JS `config/skills.json` | Canonical inventory | AES REQUIRED_SKILLS set, LCE routing.json | — | Per-skill `capability.json` + `schemas/capability.schema.json` | REWRITE |
| JS/AES/LCE `tests/` | Installer, manifest, routing, activation, budget, security tests | Three suites | Rollback test (JS), route fixtures (LCE), audit fixtures (AES) | `tests/` (64 tests) + `evals/routing_corpus.json` (115 cases) | MERGE |
| JS/AES/LCE `.github/workflows/ci.yml` | CI | Three workflows | OS matrix (JS), shellcheck/actionlint (AES), budget check (LCE) | one `ci.yml` running `scripts/quality_gate.py` | MERGE |
| JS `.claude-plugin/*` | Plugin + marketplace | AES plugin manifests | Historical namespace `janefskills` | `.claude-plugin/*` (renamed to `janef-forge`, displayName "JANEF Forge") | REWRITE |
| JS per-skill `agents/openai.yaml`, LCE `agents/openai.yaml`, AES `.codex-plugin` | Codex UI metadata | Three formats | — | Rendered at install time from `adapters/codex/interface.json` | REWRITE |
| JS `docs/architecture.md`, `docs/compatibility.md`, `docs/releasing.md`; LCE `docs/*`; AES `README`, `THIRD_PARTY.md`, `NOTICE.md` | Documentation | Overlapping | LCE threat model of the tooling itself; AES third-party boundary | `docs/architecture/JANEF_FORGE_ARCHITECTURE.md`, `docs/compatibility.md`, `docs/releasing.md`, `NOTICE.md`, `SECURITY.md` | MERGE |
| LCE `examples/*` | Illustrative routing walk-throughs | README examples | — | `evals/routing_corpus.json` (executable) + README example | ABSORB |
| AES `docs/assets/*.png`, LCE `assets/*`, JS `assets/banner.svg` | Brand artwork | — | — | JS banner kept; source-repo artwork not imported (branding changes to JANEF Forge) | DEPRECATE |
| AES `dist/*` | Committed release archives | — | — | Not imported; `dist/` is gitignored and built by the release script | DEPRECATE |

## Resulting capability set (26 manifests)

- **Core (1):** `forge`
- **Engineering (16):** `implementation-quality`, `root-cause-debugging`, `architecture-integrity`, `testing-verification`, `api-contracts`, `database-integrity`, `performance-scalability`, `devops-reliability`, `git-discipline`, `documentation-integrity`, `frontend-design-quality`, `ui-ux-quality`, `accessibility-quality`, `context-efficiency`, `review-defect-first`, `delegation-discipline`
- **Security (8):** `threat-model`, `auth-hardening`, `vuln-audit`, `variant-hunt`, `secrets-guard`, `security-logging`, `security-audit`, `skill-security-audit`
- **Compat (1, deprecated):** `janef`

Source counts for reference: JS 8 skills, AES 17 skills, LCE 1 skill + 7 references + 8 modules = 41 units. They converge into 24 selectable capabilities plus one entry point; the reduction comes from removing three routers, three policy statements, and duplicated verification, security, and context-efficiency text, not from dropping knowledge.
