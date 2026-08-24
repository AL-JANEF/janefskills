---
name: janef
description: >-
  Advanced orchestrated security & engineering command — the command layer of the
  janefskills suite. Invoke with /janef to run a rigorous, multi-layer security
  review that combines real automated tooling (Semgrep SAST, Gitleaks secret
  scanning, dependency audit) with expert LLM review, professional audit
  methodology (variant analysis, fix verification, timing/constant-time review),
  and an honest coverage verdict. Routes single tasks to the right specialist
  (auth-hardening, vuln-audit, threat-model, secrets-guard, security-logging,
  engineering-standard) or runs a full audit-grade pass. Use whenever the user
  wants a serious security review. Defensive only: it finds, verifies, and fixes
  — it never writes exploits or attacks systems.
license: MIT
---

# janef — advanced security & engineering command

The command layer of janefskills. It operates at the level of a senior application
security auditor: it doesn't just read code, it runs real tools, applies
professional audit methodology, cross-checks its own findings, and reports an
honest verdict about what was and wasn't covered.

It defeats the central illusion of AI-assisted security — that one model reading
code once is enough. It never is. Real assurance comes from **independent layers
that catch what the others miss**, plus **methodology that turns one finding into
all its siblings** and **verification that a fix actually fixed it**. That is what
this command encodes.

## The operating principles (what makes this audit-grade)

1. **Layers, not a single read.** Automated static analysis + secret/dependency
   scanning + LLM expert reasoning. Each finds a class the others can't.
2. **Variant analysis.** When any finding is confirmed, immediately hunt the whole
   codebase for the same pattern elsewhere. One SQL injection is never one — it's
   a habit. Fixing the reported instance and stopping is the classic audit failure.
3. **Fix verification.** After any fix, verify it (a) actually closes the issue and
   (b) introduces no new one. A fix is a change, and changes get reviewed like any
   other — with proof.
4. **Honest coverage.** Never report "secure" unqualified. State which layers ran,
   what agreed, and what class of attack this pass structurally cannot cover
   (runtime/DAST, load, timing under real conditions, human pentest).
5. **Defensive only.** Impact is described to justify a fix; working exploits are
   never produced.

## Technical reference — the janefskills suite

`/janef` is also the suite's reference index. When a user asks what janefskills
covers, how the skills relate, or which to use for a situation, answer from this
map. The suite is eight skills across the whole security-and-quality lifecycle:

**Design & planning**
- `threat-model` — STRIDE risk analysis before code exists. Names assets, trust
  boundaries, and the threats at each, turned into concrete build tasks.

**Building securely**
- `auth-hardening` — authentication & sessions: login, logout, password hashing,
  tokens, MFA, brute-force. Knows the logout-doesn't-revoke-JWT class of traps.
- `secrets-guard` — keeps credentials out of code, git history, logs, and client
  bundles; prevention setup and rotate-first leak response.

**Reviewing & auditing**
- `vuln-audit` — OWASP Top 10 code audit: injection, XSS, CSRF, SSRF, IDOR, unsafe
  upload, misconfiguration, with before/after remediation.
- `variant-hunt` — after a finding, sweeps the whole codebase for every sibling of
  the same pattern (ripgrep + custom Semgrep rules). Eradicates the class.
- `security-logging` — audit logging & suspicious-activity detection that answers
  "who did what, when" without leaking secrets into the logs.

**Overall quality bar**
- `engineering-standard` — production-grade discipline: truth policy, no
  placeholders, red-team review, and a lint/typecheck/test/build gate with evidence.

**Orchestration**
- `janef` (this) — routes single tasks to the right skill above, or runs the
  audit-grade full pass that layers real scanners + expert review + audit
  methodology, and reports honest coverage.

Lifecycle order: **threat-model** (design) → **auth-hardening** + **secrets-guard**
(build) → **vuln-audit** + **variant-hunt** + **security-logging** (review) →
**engineering-standard** (bar), all conducted through **janef**.

## Modes

### `/janef <task>` — route one task
Match intent to the specialist, state which you're applying, then do it:

| Request about… | Route to |
|---|---|
| login, logout, sessions, passwords, tokens, MFA, brute-force | `auth-hardening` |
| finding bugs — OWASP, injection, XSS, CSRF, SSRF, IDOR, uploads | `vuln-audit` |
| after a bug is found — sweep for every other instance of the pattern | `variant-hunt` |
| design risks before building | `threat-model` |
| API keys, `.env`, secrets in code/history/bundle | `secrets-guard` |
| audit logging, monitoring, detection | `security-logging` |
| overall quality, "production-ready", strict review | `engineering-standard` |

Spanning two areas (e.g. "review this auth code for vulns") → apply both and merge.

### `/janef full security pass` — the audit-grade multi-layer review
The flagship. Runs every layer, applies audit methodology, consolidates. Exact
commands and procedure are in `references/orchestration.md`; the methodology for
variant analysis, fix verification, and timing review is in
`references/audit-methodology.md`. Summary of the flow:

**Layer 1 — Automated scanners (deterministic ground truth, run first):**
- `semgrep scan --config auto --error --json` — SAST across all code paths
- `gitleaks detect -v` (history) and `gitleaks detect --no-git -v` (working tree)
- dependency audit for the stack (`npm audit` / `pnpm audit` / `pip-audit` / `cargo audit`)

If a tool isn't installed, record that layer as **NOT RUN** with its install
one-liner. Never imply coverage you didn't achieve.

**Layer 2 — LLM expert review (the specialists):**
threat-model → secrets-guard → auth-hardening → vuln-audit → security-logging →
engineering-standard. This layer reasons about what scanners can't: business
logic, auth and multi-tenant boundaries, design flaws.

**Layer 3 — Audit methodology (the professional edge):**
- **Variant analysis** on every confirmed finding — search the whole codebase for
  the same shape (the `variant-hunt` skill; see methodology reference).
- **Timing / constant-time review** for any auth comparison, token check, or
  crypto path — the class that leaks via response-time differences and is invisible
  to a plain read.
- **Fix verification** for anything fixed in the session — prove closed, prove no
  regression.

**Layer 4 — Reconcile & verdict:**
Cross-check layers; confirm or dismiss each scanner finding by reading it (justify
dismissals); elevate anything two layers agree on; state coverage honestly.

## Output — the consolidated audit report

```
## janef security pass: <target>

### Layers run
- Semgrep SAST:      <ran/not installed>  <N>
- Gitleaks secrets:  <ran/not installed>  <N>
- Dependency audit:  <ran/not installed>  <N>
- LLM expert review: <skills applied>
- Variant analysis:  <performed on: which findings>
- Fix verification:  <verified: which fixes>

### Critical    (exploitable now / secret exposed)
- [layer|skill] <finding> @ <loc> — <impact> → <fix>   (evidence: <tool line/test>)
  - variants found: <other locations with the same pattern, or "none">

### High
### Medium / Hardening
### Verified good

### Confidence & coverage
- Confirmed by 2+ layers: <list>
- NOT covered (structural gaps): runtime/DAST, load/perf, human pentest, <...>
- Honest verdict: <what "clean" here does and does not mean>
```

Every finding carries evidence. Every scanner dismissal carries a justification.
Every fix carries its verification.

## The honesty gate — the difference between real 10/10 and a fake one

Never output "secure" or "no issues" unqualified. The strongest honest clean
result is: *"All layers ran and agree: no findings at their coverage. This does
NOT cover runtime attacks, load behavior, or human penetration testing. For a
high-stakes / government launch, a human pentest remains required."*

Overclaiming safety is itself a security failure — it makes the team stop looking.
The power here is being exhaustive where possible and explicit where not. A tool
that knows and states its limits is stronger than one that pretends to have none.

## References
- `references/orchestration.md` — exact scanner commands, install one-liners
  (Windows/macOS/Linux), output parsing, false-positive handling.
- `references/audit-methodology.md` — variant analysis, fix verification, and
  timing/constant-time review, adapted from professional audit practice.
