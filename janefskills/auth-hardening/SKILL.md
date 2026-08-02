---
name: auth-hardening
description: >-
  Review, harden, and design authentication and session management for web
  applications — login, logout, session lifecycle, password storage, token
  handling, and brute-force protection. Use this skill whenever the user is
  building or reviewing sign-in / sign-out flows, JWT or session cookies,
  password hashing, "remember me", refresh tokens, account lockout, OTP/MFA,
  or password reset — even if they only mention "login" or "auth" casually.
  Applies to Node.js, Next.js, and similar stacks. Defensive only: this skill
  hardens auth systems, it does not bypass or attack them.
license: MIT
---

# Auth Hardening

Authentication is the front door of an application. Most real breaches don't come
from exotic exploits — they come from ordinary mistakes in how login, sessions,
and logout are built. This skill's job is to catch those mistakes and replace
them with proven patterns, then prove the fix works.

The guiding rule throughout: **the server is the only place trust lives.** Any
check on the client is user experience, not security. If a control isn't enforced
server-side, treat it as absent.

## When to reach for this skill

Use it the moment a task touches any of: a login or logout endpoint, session
cookies or JWTs, password storage or reset, "remember me" / refresh tokens,
account lockout, or OTP/MFA. Reviewing existing auth code counts too — you don't
need the user to say "harden," just to be working in this area.

## Workflow

Work through these five areas in order. Each has a "get it right" standard and a
matching failure to hunt for. Don't skip to code before understanding which stack
and session model the user has — read what exists first, then apply the standards.

### 1. Password storage

The standard: hash with a slow, salted, memory-hard algorithm — **argon2id**
(preferred) or **bcrypt**. Never MD5, SHA-1, SHA-256, or HMAC-SHA256 for
passwords. Fast hashes exist to be fast; that is exactly wrong for passwords,
because it lets an attacker who steals the database try billions of guesses.

Note the distinction that trips people up: HMAC-SHA256 is a fine choice for
signing *tokens* (short, high-entropy, machine-generated) but a poor one for
*passwords* (human-chosen, low-entropy, needs deliberate slowness). Seeing
`saltHex:hashHex` in an `admin_users` table is a signal to check whether a fast
hash is guarding a human password — if so, migrate to argon2id.

Never roll a custom scheme. Use the platform's vetted library.

### 2. Session model — the logout problem

First decide the model, because logout behaves differently in each:

**Stateful sessions** (server stores a session record, client holds an opaque
ID in an httpOnly cookie). Logout is easy and correct here: delete the server
record and the session is genuinely dead everywhere.

**Stateless JWTs** (client holds a signed token; server verifies the signature
without storing anything). This is where most logout bugs live. A JWT stays
valid until it expires no matter what the client does — clearing it from the
browser does **not** invalidate it. A stolen token still works. So real logout
requires one of:
- short access-token lifetimes (5–15 min) plus a refresh token you *can* revoke, or
- a server-side revocation list / token blocklist checked on each request, or
- a per-user token version that you bump on logout so old tokens fail.

The failure to hunt: "logout" that only does `localStorage.removeItem('token')`
with no server-side invalidation. That is not logout; it is hiding the key under
the mat.

See `references/session-patterns.md` for concrete implementations of each model,
including refresh-token rotation.

### 3. Cookie and token handling

If using cookies: set `HttpOnly` (blocks JS/XSS theft), `Secure` (HTTPS only),
and `SameSite=Lax` or `Strict` (blunts CSRF). A token in `localStorage` is
readable by any XSS on the page — prefer httpOnly cookies for session material,
and if you must use `localStorage`, understand you've accepted that risk.

For JWTs: verify the signature with a strong secret or asymmetric key, pin the
algorithm server-side (reject `alg: none` and algorithm-confusion), and validate
`exp`, `iss`, and `aud`. Keep access tokens short-lived; put longevity in
revocable refresh tokens, and rotate refresh tokens on use so a stolen one is
single-use.

### 4. Brute-force and enumeration resistance

Login and reset endpoints are guessing targets. Defenses:
- **Rate limiting** per account and per IP, with escalating delay.
- **Account lockout** or throttling after repeated failures (balanced against
  denial-of-service — a pure hard-lock lets an attacker lock out real users).
- **CAPTCHA / proof-of-work** after a threshold.
- **Uniform responses** so the system never reveals whether an account exists.
  "Invalid email or password" for both cases; password reset says "if an account
  exists, we sent a link" regardless. Different messages or timings for
  existing vs. missing accounts leak a user list.

### 5. MFA, OTP, and password reset

Reset tokens must be single-use, short-lived, high-entropy, and invalidated once
used or once a new one is issued. Delivering OTP over SMS is weak (SIM-swap) but
common; note the tradeoff rather than assuming. On any password change or reset,
invalidate existing sessions — a reset is often a response to compromise, so
leaving old sessions alive defeats the point.

## Output format

When reviewing existing code, produce a findings report — not a vague opinion.
Use this structure so results are scannable and actionable:

```
## Auth Review: <component>

### Critical   (exploitable now — fix before shipping)
- [finding] — <what's wrong> → <the fix>

### High       (weakens security materially)
- ...

### Medium / Hardening   (defense in depth)
- ...

### Verified good   (things already done right — say so)
- ...
```

Each finding names the concrete fix, not just the problem. When designing new
auth rather than reviewing, output the implementation plus a short note on which
of the five areas above each part addresses.

## Proof before done

Consistent with a "no feature is complete without evidence" discipline: an auth
fix is not finished until it's demonstrated. For a logout fix, that means showing
the token is actually rejected after logout — e.g. call a protected endpoint with
the old token and show a 401, not just "the code looks right." Prefer a real test
run (unit or integration) over assertion. If the stack has a test runner, write
the test; if not, show the request/response evidence.

## References

- `references/session-patterns.md` — Concrete, copyable implementations for
  stateful sessions, JWT with revocation, and refresh-token rotation. Read it
  when implementing or fixing a session model rather than guessing the details.
- `references/checklist.md` — A condensed pre-ship checklist covering all five
  areas, for a fast final pass before shipping an auth change.
