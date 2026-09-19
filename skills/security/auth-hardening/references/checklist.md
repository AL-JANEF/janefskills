# Auth Pre-Ship Checklist

A fast final pass before shipping any auth change. Each line is a yes/no with the
answer that should be "yes." If any is "no," it's a finding.

## Password storage
- [ ] Passwords hashed with argon2id or bcrypt (cost >= 12), never a fast hash
- [ ] Salts unique per password (handled automatically by argon2/bcrypt)
- [ ] No password, token, or secret written to logs

## Sessions & logout
- [ ] Session model is explicit (stateful vs. stateless) and documented
- [ ] Logout actually invalidates server-side (record deleted, version bumped,
      or token denylisted) — not just cleared from the client
- [ ] Sessions/tokens expire; access tokens are short-lived
- [ ] Password change / reset invalidates existing sessions

## Cookies & tokens
- [ ] Session cookies are HttpOnly + Secure + SameSite
- [ ] JWT algorithm pinned server-side; `alg: none` rejected
- [ ] JWT `exp`, `iss`, `aud` validated
- [ ] Refresh tokens rotate on use; reuse is detected and revokes the family

## Brute-force & enumeration
- [ ] Rate limiting on login and reset (per account and per IP)
- [ ] Lockout/throttling after repeated failures (without enabling easy DoS)
- [ ] Login errors are uniform — no "user not found" vs "wrong password" leak
- [ ] Password reset response is identical whether or not the account exists

## Authorization (adjacent, but check it)
- [ ] Every protected endpoint verifies authorization server-side
- [ ] Object access checks ownership (no IDOR via changing an id)
- [ ] Multi-tenant: queries are scoped to the tenant; no cross-tenant leakage

## Reset & MFA
- [ ] Reset tokens are single-use, short-lived, high-entropy
- [ ] MFA/OTP delivery tradeoffs understood (SMS is weakest)

## Proof
- [ ] The fix is demonstrated with a real request/response or test, not asserted
