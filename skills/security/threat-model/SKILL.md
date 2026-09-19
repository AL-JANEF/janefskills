---
name: threat-model
description: >-
  Structured STRIDE threat modeling at design time, before code exists: name
  assets, actors, and trust boundaries, walk
  Spoofing/Tampering/Repudiation/Information disclosure/Denial of
  service/Elevation of privilege at each boundary, rate and prioritize, and
  turn mitigations into build tasks. Use when designing a system, feature, or
  API or asking what could go wrong. Defensive only.
license: MIT
---

# Threat Model

The cheapest security fix is the one made before the code exists. This skill runs
a disciplined pass over a design to surface risks early, using STRIDE so the
analysis is systematic rather than "whatever we happen to think of."

The core question repeated at every trust boundary: **what does an attacker gain
by spoofing, tampering, denying, disclosing, disrupting, or escalating here?**

## When to reach for this skill

Use it at design time: a new system or service, a new feature touching data or
auth, an architecture diagram, a set of API contracts, or any "how should we
build X?" where X handles sensitive data, money, identity, or multi-tenant
access. If the user is still deciding *how* to build something, this is the
moment — cheaper than auditing it later.

## The method

### 1. Establish scope and assets

Name what you're protecting before hunting threats. Identify: the sensitive
assets (user data, credentials, money, tenant boundaries, PII), the actors
(anonymous users, authenticated users, admins, external services), and the trust
boundaries (where data crosses from less-trusted to more-trusted — client→server,
service→service, user→tenant). Threats live at trust boundaries; that's where to
look hardest.

### 2. Apply STRIDE at each boundary

For each trust boundary and data flow, walk the six STRIDE categories and ask
whether each applies:

- **Spoofing** — can an attacker pretend to be someone else? (weak auth, stealable
  tokens, no service-to-service authentication)
- **Tampering** — can data be modified in transit or at rest? (no integrity
  checks, mutable client-side values trusted by server, missing TLS)
- **Repudiation** — can someone deny an action with no trace? (no audit log of
  sensitive operations)
- **Information disclosure** — can data leak? (verbose errors, IDOR, unencrypted
  storage, over-broad API responses, cross-tenant leakage)
- **Denial of service** — can availability be destroyed? (no rate limiting,
  unbounded queries, expensive operations triggerable by anyone)
- **Elevation of privilege** — can a low-privilege actor gain higher rights?
  (missing authorization checks, insecure direct role assignment, injection
  leading to code execution)

Not every category applies to every flow — the discipline is in *asking* each one,
then recording the ones that hit.

### 3. Rate and prioritize

For each identified threat, judge likelihood and impact roughly (high/medium/low
each). Focus mitigation effort on high-impact threats first. Don't demand a
formal scoring system for a small feature — proportional rigor.

### 4. Assign mitigations

Every accepted threat gets one of: a mitigation (a control that reduces it), an
acceptance (a documented decision to live with it and why), or a transfer (push
it to a provider/library). "We'll think about it later" is not an outcome — name
the decision.

See `references/stride-prompts.md` for a fuller set of guiding questions per
category, and `references/example.md` for a worked threat model of a typical
multi-tenant API feature.

## Output format

Produce a threat model table plus a prioritized mitigation list:

```
## Threat Model: <feature/system>

### Assets & trust boundaries
- Assets: ...
- Boundaries: ...

### Threats (STRIDE)
| # | Boundary | STRIDE | Threat | Likelihood | Impact | Mitigation |
|---|----------|--------|--------|-----------|--------|------------|
| 1 | ...      | Info disclosure | ... | High | High | ... |

### Priorities
1. <highest-impact threat> → <mitigation> → <owner/when>
```

Keep threats concrete and tied to *this* design, not generic. A threat the reader
can't act on isn't worth listing.

## Handing off to build

A threat model is only useful if its mitigations become work. End by turning the
top mitigations into concrete build tasks — the things that must be true in the
implementation. This is where `threat-model` connects to `auth-hardening` and
`vuln-audit`: the mitigations named here become the checks those skills enforce
later.

## References

- `references/stride-prompts.md` — Expanded question prompts per STRIDE category
  to drive a thorough pass. Read it when running the analysis.
- `references/example.md` — A worked example threat model for a multi-tenant API
  endpoint, showing the method end to end.
