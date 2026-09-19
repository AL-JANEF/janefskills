# Review Checklist

Walk every dimension that the diff touches. A gap in any is a finding, not an oversight.

**Correctness** — Does it do what was asked? Edge cases, boundary values, empty and error inputs handled? Off-by-one, null/undefined, timezone, encoding traps checked?

**Architecture** — Does it fit the existing design or fight it? Are boundaries and responsibilities respected? Any dependency-direction or ownership violation introduced?

**Security** — Red-team it. Injection (SQL/NoSQL/command), XSS, CSRF, SSRF, IDOR, privilege escalation, path traversal, secrets exposure, broken authentication or authorization. In multi-tenant code: is every query tenant-scoped? Deep remediation: `vuln-audit`, `auth-hardening`, `secrets-guard`.

**Data** — Migrations reversible or forward-fixable? Constraints preserved? Transactions around multi-step writes? Backfills batched?

**Performance** — N+1 queries, unindexed lookups, memory growth, blocking calls on hot paths, concurrency races and deadlocks.

**Error handling** — Failures caught and handled meaningfully, not swallowed. No empty catch blocks. Errors surface actionable information without leaking internals.

**Logging and observability** — Security-relevant and diagnostically important events logged without secrets or PII (`security-logging`). Can production behavior be reconstructed from what is emitted?

**Tests** — Do new tests assert behavior that matters? Could they fail? Are critical paths (auth, money, data integrity, tenant boundaries) covered by a denied case and a failure case?

**Maintainability and readability** — Honest names, cohesion, no dead code, no duplication, no commented-out blocks, no cleverness that obscures intent.

## Forbidden-pattern scan

Reject on sight: `TODO`/`FIXME` presented as complete · placeholder or stub business logic · mock logic for real behavior · dead code · copy-paste duplication · disabled tests · disabled lint or type checks · `@ts-ignore` · unjustified `any` · hard-coded secrets.

## Acceptable evidence for a finding

A file and line range plus the call site, invariant, or test gap that makes it a defect. Describe the impact; do not write a working exploit.
