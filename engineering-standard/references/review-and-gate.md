# Review Checklist & Completion Gate

The full review checklist and the completion-gate procedure. Read this when
reviewing code or before declaring any task complete.

## Code review checklist

Walk every dimension. A gap in any is a finding, not an oversight.

**Correctness** — Does it do what was asked? Edge cases, boundary values, empty
and error inputs handled? Off-by-one, null/undefined, timezone, encoding traps
checked?

**Architecture** — Does it fit the existing design, or fight it? Are boundaries
and responsibilities respected (Clean Architecture / DDD)? Any SOLID violation
introduced?

**Security** — Red-team it. Injection (SQL/NoSQL/command), XSS, CSRF, SSRF, IDOR,
privilege escalation, path traversal, secrets exposure, broken auth/authz. In
multi-tenant code: is every query tenant-scoped? (Deep fixes: the janefskills
security skills.)

**Performance** — N+1 queries, unindexed lookups, memory leaks, excessive
allocations, blocking calls on hot paths, concurrency races/deadlocks.

**Maintainability** — Will someone understand this in six months? Naming,
cohesion, coupling. No dead code, no duplication, no commented-out blocks.

**Readability** — Clear intent, honest names, no cleverness that obscures.

**Reusability** — Is logic factored so it isn't re-implemented elsewhere? (Without
over-abstracting — YAGNI.)

**Logging** — Are security-sensitive and diagnostically-important events logged,
without leaking secrets/PII into the logs? (See `security-logging`.)

**Error handling** — Failures caught and handled meaningfully, not swallowed. No
empty catch blocks. Errors surface actionable information.

**Observability** — Can you tell what happened in production from what's emitted?

## The forbidden list (fast scan)

Reject on sight, in your own output and in review:
`TODO`/`FIXME` in shipped code · placeholder/stub business logic · mock logic
for real behavior · dead code · copy-paste duplication · disabled tests ·
disabled lint · `@ts-ignore` · unjustified `any`.

## Completion gate procedure

A task is complete only when applicable checks pass **with evidence shown**.

1. **Identify the stack's commands.** Map the four gates to real commands:
   - JS/TS (pnpm): `pnpm lint` · `pnpm typecheck` · `pnpm test` · `pnpm build`
   - JS/TS (npm): `npm run lint` · `npm run typecheck` · `npm test` · `npm run build`
   - Rust: `cargo clippy` · `cargo check` · `cargo test` · `cargo build --release`
   - Go: `golangci-lint run` · `go vet` · `go test ./...` · `go build ./...`
   - Python: `ruff check` · `mypy .` · `pytest` · (build/package as applicable)

2. **Run each applicable gate.** Skip a gate only if it genuinely doesn't apply
   (e.g. no typecheck in an untyped project) — and say which you skipped and why.

3. **Show the evidence.** Paste or summarize the actual output. "Tests pass" alone
   is not evidence; the run is.

4. **On any failure:** the task is not complete. Report the failure honestly, fix
   the underlying cause, and re-run. Never weaken or disable the check to pass.

## What counts as acceptable evidence

- **Tests pass** → the test-runner output (counts, pass/fail), not a claim.
- **Bug fixed** → a demonstration: the failing case now behaves correctly, ideally
  a regression test that fails before and passes after.
- **Performance improved** → a before/after measurement, not "should be faster."
- **Security fixed** → the exploit path now blocked, shown (e.g. the IDOR request
  now returns 404; the injection input is handled harmlessly).
- **Builds** → the successful build output.

If evidence can't be produced in the current environment, say so explicitly and
state exactly what the user must run to verify — never paper over the gap with a
confident claim.

## The honest-completion sentence

End a completed task with a truthful status, e.g.:
"Complete: lint/typecheck/tests/build green (output above). Security reviewed for
the OWASP classes relevant to this change; tenant scoping verified. Open item:
<x> deferred because <reason>."

If it's not done, say that instead — with what's blocking and the path to green.
