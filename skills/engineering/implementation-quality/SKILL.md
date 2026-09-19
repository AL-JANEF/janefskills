---
name: implementation-quality
description: >-
  Write or modify production code to a strict, evidence-gated standard:
  features, bug fixes, refactors, services, libraries, CLIs, workers, and
  application logic. Use whenever real application code is being implemented
  or changed, or when asked whether code is production-ready. Bans
  placeholders, dead code, silent failures, and unverified completion claims.
license: MIT
---

# Implementation Quality

Working code is not enough. The bar is code that is correct, verified, secure, maintainable, and proven, not asserted. This capability applies to any code that ships, touches data, handles auth, or that someone else will maintain. Throwaway scripts do not need the full gate; say so when you skip it.

## Workflow

1. **Understand** the requirement; restate the observable behavior, callers, inputs, outputs, invariants, and failure modes. Surface ambiguity before building.
2. **Inspect** repository instructions and the nearest analogous implementation before choosing a pattern. Distinguish a requested behavior change from an accidental compatibility break.
3. **Design** the smallest complete slice: existing architecture, idioms, dependency set, and error model. Name the approach and why.
4. **Identify risks** up front: security, data, performance, concurrency, failure modes. Route to the matching capability when one applies.
5. **Implement** to the standards below.
6. **Self-review** the diff as a red-teamer, then run the completion gate (`testing-verification`).

## Standards

- Keep validation at boundaries and domain invariants near the state they protect. Preserve error context; never turn failures into silent defaults or false success.
- Strong typing where the language offers it; no loosening the type system for convenience.
- Extract an abstraction only when current duplication or variation proves it useful. No speculative generality, no new dependency for a few lines of code.
- Treat generated files, lockfiles, migrations, public schemas, and API contracts as explicit change surfaces. Preserve compatibility and migration paths where callers or persisted data exist.
- For a bug, establish root cause first (`root-cause-debugging`); do not patch the symptom.
- If multiple designs are viable, choose the least irreversible one that meets current requirements. Surface a user decision only when alternatives materially change behavior, cost, safety, or compatibility.

## Forbidden in shipped code and in review

`TODO` / `FIXME` presented as complete · placeholder or stubbed business logic · mock logic standing in for real behavior · dead or unreachable code · copy-paste duplication · disabled tests · disabled lint rules or type checks (`@ts-ignore`, blanket suppressions) · `any` without a justifying comment · hard-coded secrets · fake production behavior behind a flag.

Finding any of these is a finding, not a nitpick. Name it and fix it.

## Refuse unsafe work

If a request would introduce a security risk, meaningful technical debt, or an architectural violation, say so plainly, decline the unsafe version, and offer the correct path. Firmness in the user's interest, with a concrete alternative, not a lecture.

## Review the diff before reporting

Every changed line supports the requested outcome, its tests, or required documentation. Edge cases at trust boundaries, empty states, retries, concurrency, and cleanup are handled. Temporary logging, dead branches, broad suppressions, and stale comments are removed.

## Output

```
## <task>
### Approach        — the design and why
### Changes         — files and behavior
### Verification    — commands run + evidence (see testing-verification)
### Risks addressed — security / data / performance handled
### Open items      — uncertain or deferred, stated honestly
```
