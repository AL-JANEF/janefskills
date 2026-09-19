---
name: testing-verification
description: >-
  Select tests by risk, design strong regression and boundary tests, handle
  flaky suites, and run the completion gate with evidence: exact command,
  result, scope, and every skipped or blocked check. Use when choosing what to
  test, judging whether work is done, or producing release evidence. Never
  weaken a failing test to get green.
license: MIT
---

# Testing & Verification

Completion means the requested behavior and the relevant invariants are supported by evidence, not merely that the edit is finished. Evidence is the command, its meaningful result, and its scope.

## Truth policy

- Never fabricate test output, benchmark numbers, or passing checks.
- Never claim success without a shown run. "Tests pass" requires the runner output.
- Never hide or downplay a failure. Never weaken, delete, skip, or mock away a failing test, lint rule, or type check to get green. If a test is wrong, fix it honestly and say why.
- When uncertain, say so and state how to resolve it.

## Risk-based ladder

Run the cheapest check that can disprove the change, then expand as risk warrants:

1. Static or structural check on edited files (lint, type check, syntax).
2. One focused test that exercises the changed behavior or the regression.
3. Neighboring unit or integration tests across the affected boundary.
4. Build, type check, lint, migration validation, or end-to-end journey when the change can affect them.
5. Security, performance, compatibility, or rollback checks for high-impact paths.

Match evidence to risk: public contract or schema → compatibility and consumer checks; auth, payment, privacy, or destructive path → denied cases, audit behavior, rollback; concurrency or retry → ordering, cancellation, idempotency, race-sensitive tests; UI → loading, empty, error, keyboard, responsive, accessibility states; configuration or deployment → parse, dry-run, environment differences, safe rollback.

## Design strong tests

- Test behavior at the lowest level that observes the real failure mechanism. Use integration or contract tests when serialization, persistence, framework wiring, or service boundaries matter. Keep a small end-to-end set for critical journeys.
- Cover the happy path plus meaningful validation, authorization, boundary, concurrency, and failure cases according to risk.
- Prefer real behavior over excessive mocking; mock only unstable or external boundaries, and only with a mock that can fail like the real dependency.
- Deterministic clocks, identifiers, randomness, and schedulers over sleeps and retries.
- Avoid tests that mirror implementation, snapshots with unreviewed noise, or assertions that cannot fail.
- For a bug: reproduce first, then add a regression test that fails on the original mechanism.

## Flaky suites

Reproduce and classify the cause: timing, order, shared state, network, resource, or environment. Fix isolation or synchronization. Quarantine only with an owner, an issue, evidence, and an expiry.

## Completion gate

Run every applicable repository gate once implementation is complete, with evidence shown. Skip a gate only when it genuinely does not apply, and say which and why. On any failure the task is not done: report it, fix the cause, re-run. Procedure, per-stack commands, and what counts as evidence: `references/completion-gate.md`.

End with an honest status line: what passed (with output), what was skipped and why, what remains.
