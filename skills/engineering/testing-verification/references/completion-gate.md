# Completion Gate

The procedure for the final gate, per-stack commands, and what counts as evidence. Read before declaring any task complete.

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
