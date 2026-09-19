# Worked Example: Multi-Tenant API Endpoint

A worked threat model for a common feature — a multi-tenant SaaS endpoint that
lets an authenticated user fetch and update their organization's records. Shows
the method end to end so it can be adapted.

## Feature

`GET /api/records/:id` and `PUT /api/records/:id` — an authenticated user reads
or updates a record belonging to their organization (tenant). Auth is a JWT in an
httpOnly cookie.

## Assets & trust boundaries

**Assets:** organization records (business data), the tenant boundary itself
(org A must never see org B), user session tokens.

**Boundaries:** client → API server (untrusted input crossing in); user → tenant
(the critical one — a user is trusted within their org, not across orgs).

## Threats (STRIDE)

| # | Boundary | STRIDE | Threat | Likelihood | Impact | Mitigation |
|---|----------|--------|--------|-----------|--------|------------|
| 1 | user→tenant | Info disclosure | User fetches another org's record by changing `:id` (IDOR / cross-tenant) | High | High | Scope query by `tenantId` from the session, not just record id; return 404 on mismatch |
| 2 | user→tenant | Elevation | User updates a record in another org via PUT | High | High | Same tenant scoping on write; verify ownership before update |
| 3 | client→API | Tampering | Client sends a `tenantId` or `role` field the server trusts | Medium | High | Derive tenant and role from the verified session, never from request body |
| 4 | client→API | Spoofing | Stolen/forged JWT | Medium | High | Pin algorithm, validate exp/iss/aud, short lifetime + revocation (see auth-hardening) |
| 5 | client→API | Denial of service | Unauthenticated or unbounded listing hammered to exhaust DB | Medium | Medium | Rate limit per IP and per session; paginate; cap page size |
| 6 | user actions | Repudiation | Malicious update with no trace of who did it | Low | Medium | Audit-log record mutations with actor, timestamp, before/after (see security-logging) |
| 7 | client→API | Info disclosure | Response includes internal fields (owner emails, internal flags) | Medium | Medium | Return an explicit DTO; never serialize the raw DB row |

## Priorities

1. **Cross-tenant access (threats 1 & 2)** → enforce `tenantId` scoping on every
   read and write; add a test proving org A cannot touch org B's record →
   before any ship.
2. **Trusting client-supplied identity (threat 3)** → derive tenant/role from
   session only → same PR.
3. **Token security (threat 4)** → hand off to `auth-hardening`.
4. **Rate limiting & response shaping (5, 7)** → hardening pass.
5. **Audit logging (6)** → hand off to `security-logging`.

## Handing off to build

The top mitigations become concrete build tasks:
- Every records query includes `where: { id, tenantId }`.
- A regression test: user in org A requesting an org B record gets 404.
- Update handler rejects any `tenantId`/`role` present in the request body.

Threats 4 and 6 are delegated to the auth and logging skills — the threat model's
job is to make sure they're not forgotten, not to re-solve them here.
