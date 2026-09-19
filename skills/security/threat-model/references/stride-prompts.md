# STRIDE Prompts

Expanded guiding questions per STRIDE category. Walk these at each trust boundary
to drive a thorough pass. Not every question applies everywhere — the value is in
asking, then recording the hits.

## Spoofing (identity)
- How is each actor authenticated? Can that authentication be stolen or faked?
- Are service-to-service calls authenticated, or trusted by network position?
- Can a token/session from one user be replayed or reused by another?
- Is there any endpoint that assumes identity from a client-supplied value?

## Tampering (integrity)
- Which client-supplied values does the server trust without re-validating?
  (prices, roles, quantities, IDs, flags)
- Is data protected in transit (TLS) and where it matters, at rest?
- Can a request be modified in flight to change its effect?
- Are webhooks / callbacks integrity-checked (signatures)?

## Repudiation (accountability)
- Are security-sensitive actions logged (who, what, when)?
- Could a user perform a damaging action with no trace?
- Are logs themselves tamper-resistant (append-only, off-box)?

## Information disclosure (confidentiality)
- Can one user read another's data by changing an ID? (IDOR)
- In multi-tenant: is every query scoped to the tenant?
- Do error messages, stack traces, or API responses leak more than needed?
- Is sensitive data encrypted at rest? Are backups protected?
- Does the response include fields the caller shouldn't see?

## Denial of service (availability)
- Is there rate limiting on expensive or public endpoints?
- Can a request trigger an unbounded query, loop, or allocation?
- Can one tenant/user exhaust resources shared with others?
- Are uploads / inputs size-capped?

## Elevation of privilege (authorization)
- Is authorization checked on every protected action, server-side?
- Can a normal user reach admin functionality by guessing routes?
- Can a user set their own role/permissions via a mutable field?
- Could an injection or deserialization bug lead to code execution?

## Boundary reminder
Threats concentrate where data crosses a trust boundary: client→server,
service→service, user→tenant, untrusted-input→interpreter. Spend the most effort
at those crossings.
