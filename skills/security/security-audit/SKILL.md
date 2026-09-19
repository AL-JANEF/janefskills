---
name: security-audit
description: >-
  Audit-grade multi-layer security pass: Semgrep SAST, Gitleaks secret
  scanning, and dependency audit as deterministic ground truth, then
  specialist review, variant analysis, fix verification, timing review, and an
  honest coverage verdict naming what was and was not covered. Use for "full
  security pass", security audit, pre-launch review, or any serious security
  assessment. Defensive only.
license: MIT
---

# Security Audit

Operate at the level of a senior application security auditor: run real tools, apply professional audit methodology, cross-check findings, and report an honest verdict about what was and was not covered.

One model reading code once is never enough. Assurance comes from **independent layers that catch what the others miss**, **methodology that turns one finding into all its siblings**, and **verification that a fix actually fixed it**.

## Operating principles

1. **Layers, not a single read.** Automated static analysis + secret and dependency scanning + expert reasoning. Each finds a class the others cannot.
2. **Variant analysis.** Every confirmed finding triggers a sweep for the same pattern elsewhere (`variant-hunt`). One injection is never one; it is a habit.
3. **Fix verification.** After any fix, prove it closes the issue and introduces no new one. A fix is a change and gets reviewed like one.
4. **Honest coverage.** Never report "secure" unqualified. State which layers ran, what agreed, and what this pass structurally cannot cover (runtime/DAST, load, timing under real conditions, human pentest).
5. **Defensive only.** Describe impact to justify a fix; never produce a working exploit.

## Procedure

Exact commands, install one-liners, output parsing, and false-positive handling are in `references/orchestration.md`. Variant analysis, fix verification, and timing review are in `references/audit-methodology.md`.

**Layer 1 — automated scanners (run first, capture output):**
- `semgrep scan --config auto --error --json` for SAST
- `gitleaks detect -v` (history) and `gitleaks detect --no-git -v` (working tree)
- dependency audit for the stack (`npm audit` / `pnpm audit` / `pip-audit` / `cargo audit`)

If a tool is not installed, record that layer as **NOT RUN** with its install one-liner. Never imply coverage you did not achieve.

**Layer 2 — specialist review**, in order, loading each only when reached: `threat-model` → `secrets-guard` → `auth-hardening` → `vuln-audit` → `security-logging`. This layer reasons about what scanners cannot: business logic, authorization and tenant boundaries, design flaws.

**Layer 3 — audit methodology:** variant analysis on every confirmed finding; timing/constant-time review of every auth comparison, token check, and crypto path; fix verification for anything fixed in the session.

**Layer 4 — reconcile and verdict:** read every scanner finding and confirm or dismiss it with justification; elevate anything two layers agree on; state coverage honestly.

## Output

```
## Security pass: <target>

### Layers run
- Semgrep SAST:      <ran/NOT RUN>  <N findings>
- Gitleaks secrets:  <ran/NOT RUN>  <N>
- Dependency audit:  <ran/NOT RUN>  <N>
- Specialist review: <capabilities applied>
- Variant analysis:  <performed on: which findings>
- Fix verification:  <verified: which fixes>

### Critical    (exploitable now / secret exposed)
- [layer|capability] <finding> @ <loc> — <impact> → <fix>   (evidence: <tool line/test>)
  - variants found: <locations, or "none (searched via rg + semgrep rule <id>)">
### High
### Medium / Hardening
### Verified good

### Confidence & coverage
- Confirmed by 2+ layers: <list>
- NOT covered: runtime/DAST, load/perf, human pentest, <...>
- Honest verdict: <what "clean" here does and does not mean>
```

Every finding carries evidence. Every scanner dismissal carries a justification. Every fix carries its verification.

## The honesty gate

The strongest honest clean result is: *"All layers ran and agree: no findings at their coverage. This does NOT cover runtime attacks, load behavior, or human penetration testing; for a high-stakes launch a human pentest remains required."* Overclaiming safety is itself a security failure: it makes the team stop looking.
