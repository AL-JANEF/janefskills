---
name: security-logging
description: >-
  Design and review security audit logging and monitoring — recording who did
  what and when, detecting suspicious activity (repeated failed logins, unusual
  access), and doing it without leaking sensitive data into the logs themselves.
  Use this skill whenever the user is building audit trails, adding logging to
  sensitive actions, setting up monitoring or alerting, investigating an incident,
  or asks "how do I track who did X?" — especially for auth events, data changes,
  and admin actions. Defensive only.
license: MIT
---

# Security Logging

When something goes wrong, logs are how you find out what happened, who did it,
and whether it's still happening. Yet logging is easy to get wrong in two opposite
directions: too little (you can't reconstruct an incident) or too much (the logs
themselves become a data leak). This skill gets the balance right.

Two rules run through it: **log enough to answer "who did what, when" for anything
sensitive** — and **never log the sensitive thing itself** (passwords, tokens,
full card numbers, personal data beyond what's needed).

## When to reach for this skill

Use it when adding logging to authentication events, data mutations, admin
actions, or permission changes; when building an audit trail; when setting up
monitoring or alerts; or when investigating an incident and asking what to look
for. Also when reviewing existing logging for gaps or for accidental leakage of
secrets.

## What to do

### 1. Decide what to log

Security-relevant events worth recording (the "who/what/when"):
- **Authentication**: login success and failure, logout, password change/reset,
  MFA events. Failed logins especially — they're the signal for brute-force.
- **Authorization**: access denied events, privilege changes, role assignments.
- **Sensitive data actions**: creation/modification/deletion of important records,
  exports, bulk operations.
- **Admin actions**: anything an administrator does that affects others.

Each entry should capture: timestamp, actor (user id — not full PII), action,
target (what was affected), source (IP / request id), and outcome
(success/failure). For mutations, capturing before/after (or a diff) makes the log
genuinely useful for reconstruction.

### 2. Never leak into the logs

Logs are frequently shipped to third parties, cached, and widely readable — so
they must not contain: passwords (even hashed), full tokens or session ids, full
payment card numbers, API keys, or personal data beyond what the log needs.
Redact or mask before writing. Reference a user by id, not by dumping their whole
record. This is the failure mode that turns a helpful audit log into a breach.

### 3. Make logs trustworthy (anti-repudiation)

For the log to be evidence, it must resist tampering: prefer append-only storage,
ship logs off the machine that generates them (so an attacker who compromises a
box can't rewrite its own trail), and timestamp consistently (UTC). Without this,
a sophisticated attacker just edits the logs.

### 4. Detect and alert

Logging enables detection only if something watches:
- Repeated failed logins per account or IP → possible brute-force → alert /
  throttle (ties into `auth-hardening`).
- Access-denied spikes → possible enumeration or privilege probing.
- Unusual patterns → logins from new geographies, off-hours admin actions, bulk
  exports.
Define a few high-value alerts rather than drowning in noise. An alert nobody acts
on is worse than none.

See `references/patterns.md` for concrete log-entry structure, redaction helpers,
and example detection rules.

## Output format

When reviewing, report gaps and leaks separately — both matter:

```
## Logging Review: <target>

### Leaks   (sensitive data in logs — fix now)
- <what's being logged> at <location> → redact <field>

### Gaps   (sensitive actions not logged)
- <action> has no audit entry → log <fields>

### Integrity
- <e.g. logs writable in place / not shipped off-box> → <fix>

### Detection
- <missing high-value alert, e.g. failed-login threshold>

### Verified good
- <events already logged correctly>
```

## Proof before done

Demonstrate it works: perform a sensitive action and show the audit entry appears
with the right fields; perform a login with a password and show the password is
*not* in the log; trip the failed-login threshold and show the alert/throttle
fires. Evidence, not assertion.

## References

- `references/patterns.md` — Copyable audit-log entry structure, redaction
  helpers, and example detection rules (failed-login threshold, etc.). Read it
  when implementing logging or detection.
