---
name: architecture-integrity
description: >-
  Design or change system structure without breaking invariants: module and
  domain boundaries, dependency direction, new services, queues, caches,
  datastores, or frameworks, and lasting trade-offs recorded as ADRs. Use when
  a change crosses components, introduces a durable boundary, or is hard to
  reverse.
license: MIT
---

# Architecture Integrity

Architecture should reduce the cost of known change, not speculate about every future possibility. Preserve ownership, dependency direction, invariants, and clear boundaries; do not redesign unrelated layers to make a local change look cleaner.

## Decision frame

- Which current and expected use cases must the design serve? Which quality attributes matter here: reliability, security, latency, scale, operability, portability, cost?
- What is the smallest boundary that localizes change without hiding essential behavior?
- Which option is easiest to test, observe, migrate, and remove?
- Start from requirements, trust boundaries, failure modes, deployment constraints, and the existing sources of truth.

## Design rules

- Keep domain policy separate from transport, storage, framework, and vendor adapters.
- Depend toward stable contracts. Avoid circular dependencies, shared mutable authority, duplicated business rules, and cross-domain database ownership.
- Make ownership of data, transactions, retries, timeouts, and cleanup explicit.
- Do not introduce a service, queue, cache, datastore, framework, or abstraction unless the existing architecture cannot meet the requirement cleanly. Prefer boring, existing technology.
- Model failure, recovery, operability, and ownership, not only the happy path. Keep distributed systems no more complex than necessary.
- Design migrations for mixed versions, rollback, and partial failure. Add observability at boundaries where failures would otherwise be ambiguous.

## Record the decision

Write an ADR in the repository's established mechanism when the choice affects multiple components, introduces infrastructure or a dependency, changes a public contract, has meaningful alternatives, or will be costly to reverse. Capture context, decision, alternatives, consequences, migration, and rollback. Do not turn the ADR into a tutorial.

## Verify

Validate the architecture against implementation reality before claiming compliance: imports and dependency direction, ownership of data and transactions, and the actual deployment topology. A diagram that does not match the code is a finding.

## Output

```
## Design: <scope>
Requirements & constraints: ...
Options considered: <A> / <B> — chosen <X> because ...
Boundaries & ownership: ...
Failure & migration model: ...
ADR: <path or "not needed because ...">
```
