---
name: api-contracts
description: >-
  Design and change REST, GraphQL, RPC, and webhook contracts and the backend
  services and jobs behind them: validation, authorization scope, error
  semantics, pagination, idempotency, rate limits, retries, timeouts,
  versioning, and contract tests. Use for any endpoint, external integration,
  worker, or queue consumer.
license: MIT
---

# API Contracts & Backend Services

Every external request and every upstream response is untrusted. A contract is a promise to callers you may never see; change it deliberately or not at all.

## Contract

- Specify input validation, authentication, authorization scope (object and tenant), response shape, status and error semantics, timeouts, and observability for every endpoint.
- Bound request bodies, pagination, retries, concurrency, and external response sizes. Explicit pagination for every unbounded collection.
- Idempotency for retriable side effects. Rate limits and retry/backoff where abuse or downstream saturation is plausible.
- Keep transport parsing separate from domain decisions and infrastructure adapters.
- Never break a contract silently: version or stage the change, then update callers, docs, and tests together.
- Error responses are useful to the caller without leaking stack traces, internal identifiers, or sensitive implementation detail.

## Webhooks and external integrations

Verify authenticity (signature, timestamp window), resist replay or make processing idempotent, bound processing time, and retry safely. Set timeouts and cancellation on all outbound calls; retry only transient, idempotent operations with jitter and limits.

## Reliability

- Make transaction boundaries and side-effect ordering explicit. When atomicity ends, use an outbox or a compensating action.
- Design jobs and queue consumers for at-least-once delivery unless the platform proves otherwise; make duplicate handling safe.
- Preserve error cause and correlation context without exposing internals. Avoid shared mutable process state when multiple workers or restarts are possible.

## Verification

- Contract or integration tests for material changes, exercising the real serialization and persistence boundary, not only mocked domain methods.
- Test validation failures, unauthorized and forbidden requests, duplicate or retried deliveries, and dependency failure where relevant.
- Confirm observability can distinguish caller errors, server faults, and dependency failures.

Route to `database-integrity` when persistence decisions are central and to `auth-hardening` when the endpoint issues or validates credentials.
