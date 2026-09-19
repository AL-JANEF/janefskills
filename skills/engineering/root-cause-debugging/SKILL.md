---
name: root-cause-debugging
description: >-
  Diagnose regressions, flaky behavior, crashes, build errors, and unclear
  failures with an evidence loop: reproduce, bound, hypothesize, observe, fix
  the cause at the narrowest correct boundary, then add a regression test. Use
  for any bug report or failure before patching a symptom.
license: MIT
---

# Root-Cause Debugging

A report names a symptom. The fix belongs at the mechanism that produced it, at the narrowest correct boundary, with a test that would have caught it. Shotgun edits, random retries, cache deletion, and dependency upgrades without a hypothesis are not debugging.

## Evidence loop

1. **State** expected and actual behavior precisely, with the exact error text or observation.
2. **Reproduce** with the smallest reliable command, input, or test. Preserve the first meaningful error, before wrapper noise.
3. **Bound** the failure by layer, data path, time, environment, and last known good state. Recent diffs, dependency or configuration changes, and environment differences are the usual suspects.
4. **Hypothesize** one falsifiable cause and pick the cheapest observation that distinguishes it from the alternatives.
5. **Fix the cause** at the narrowest correct boundary. Grep every caller of the function you are about to touch; a guard in the shared path beats a guard in one caller.
6. **Add a regression test** that fails for the original mechanism, then run nearby and broader checks (`testing-verification`).

## Useful evidence

- Stack traces and exit codes before wrapper noise.
- Data shape and lifecycle at the last good and first bad boundary.
- Timing, ordering, ownership, and cancellation for concurrent or flaky failures.
- Build errors: the first error, its file and line, and the toolchain version.

## Avoid

- Catch-all exception handling that hides the original failure.
- "Fixing" tests to match broken behavior unless the contract itself changed, and saying so.
- Large refactors before a minimal reproduction proves they are necessary.
- Declaring a flaky test fixed without reproducing the flake or explaining why it cannot be reproduced.

If reproduction is impossible, make observability the smallest next change and state what evidence it should collect. Route to `secrets-guard` or `security-logging` before adding logging near sensitive data.

## Output

```
## Bug: <symptom>
Reproduction: <command / input> → <observed>
Root cause: <mechanism at file:line>
Fix: <what changed and why here>
Regression test: <name> (fails before, passes after — output shown)
Nearby checks: <commands + results>
Residual risk: <what this does not cover>
```
