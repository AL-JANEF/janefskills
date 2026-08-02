---
name: vuln-audit
description: >-
  Audit web application code for common vulnerabilities — the OWASP Top 10 class
  of bugs: injection (SQL/NoSQL/command), XSS, CSRF, SSRF, IDOR / broken access
  control, insecure deserialization, unsafe file upload, and security
  misconfiguration. Use this skill whenever the user asks to review code for
  security, find vulnerabilities, do a security pass before shipping, or is
  writing code that handles user input, database queries, file uploads, or
  external requests — even if they only say "review this" or "is this safe?".
  Defensive only: this skill finds and fixes weaknesses, it does not write
  exploits.
license: MIT
---

# Vulnerability Audit

Most application vulnerabilities are a handful of recurring shapes. This skill
teaches Claude to recognize those shapes in real code, explain why each is
dangerous, and fix it — producing a severity-ranked report rather than a vague
"looks fine."

The through-line: **all input is hostile until validated on the server, and all
output must be encoded for the context it lands in.** Nearly every bug below is a
violation of one of those two rules.

## When to reach for this skill

Use it for any explicit security review ("audit this," "find vulnerabilities,"
"is this safe to ship?") and proactively whenever code handles untrusted input:
building database queries, rendering user content, accepting file uploads, making
outbound requests from user-supplied URLs, or exposing objects by ID. You don't
need the word "vulnerability" — working in these areas is the trigger.

## The audit, by vulnerability class

Work through the classes relevant to the code in front of you. For each, the
pattern to hunt and the fix are given. Deeper, copyable remediation for each lives
in `references/remediation.md` — read it when implementing a fix.

### Injection (SQL / NoSQL / command)

Hunt for: user input concatenated into a query or shell command as a string.
```
`SELECT * FROM users WHERE id = ${req.params.id}`   // vulnerable
```
Fix: parameterized queries / prepared statements always. With an ORM (Prisma,
etc.), use its query builder, never raw string interpolation. For OS commands,
avoid the shell entirely — use argument arrays, never build a command string from
input. NoSQL is not immune: object injection (`{ $gt: '' }`) bypasses auth if
input isn't type-checked.

### Cross-site scripting (XSS)

Hunt for: user-controlled data written into HTML without encoding —
`innerHTML = userInput`, `dangerouslySetInnerHTML`, template output with escaping
disabled. Fix: encode output for its context (HTML, attribute, JS, URL). Prefer
frameworks' auto-escaping; never disable it for user data. Add a Content-Security
-Policy header as defense in depth. Sanitize rich HTML with a vetted library
(DOMPurify), not a hand-rolled regex.

### Broken access control / IDOR

Hunt for: an endpoint that reads an object by ID from the request but never
checks the caller owns it — `GET /orders/:id` returning any order. This is the
most common serious bug in real apps and the easiest to miss because the code
"works." Fix: every object access verifies ownership/authorization server-side.
In multi-tenant systems, scope every query to the tenant; a missing tenant filter
leaks data across customers. Never rely on the UI hiding a button — the endpoint
must enforce.

### Cross-site request forgery (CSRF)

Hunt for: state-changing endpoints (POST/PUT/DELETE) authenticated only by a
cookie, with no anti-CSRF token. Fix: `SameSite=Lax/Strict` cookies plus a CSRF
token for sensitive actions, or a header-based token pattern for APIs. Pure
bearer-token APIs (no cookies) are generally not CSRF-prone — note the
distinction rather than adding ceremony where it isn't needed.

### Server-side request forgery (SSRF)

Hunt for: the server fetching a URL supplied by the user (webhooks, "import from
URL," image proxies). An attacker points it at internal addresses
(`169.254.169.254`, `localhost`, internal services). Fix: allowlist destinations,
block private/link-local IP ranges after DNS resolution, and disable redirects to
internal hosts.

### Unsafe file upload

Hunt for: accepting uploads by extension/MIME alone, storing them in a
web-served path, or trusting the filename. Fix: validate content type by
inspection, generate server-side filenames, store outside the web root or in
object storage, and cap size. Never execute or include uploaded files.

### Insecure deserialization & misconfiguration

Hunt for: deserializing untrusted data into objects, debug mode on in
production, verbose errors leaking stack traces, default credentials, permissive
CORS (`Access-Control-Allow-Origin: *` with credentials), missing security
headers. Fix: don't deserialize untrusted input into live objects; disable debug
and stack traces in prod; set restrictive CORS and security headers; change
defaults.

## Output format

Produce a severity-ranked report so it's scannable and actionable:

```
## Vulnerability Audit: <target>

### Critical   (exploitable now)
- [class] <location> — <what an attacker can do> → <fix>

### High
- ...

### Medium / Hardening
- ...

### Verified good
- <controls already correctly in place — name them>
```

Name the vulnerability class, the location, the concrete impact, and the fix.
Don't include a working exploit — describing the impact ("an attacker can read
other users' orders") is enough to justify the fix without handing over an attack.

## Proof before done

A fix isn't finished until demonstrated. For an IDOR fix, show that a request for
another user's object now returns 403/404. For an injection fix, show the
parameterized query rejects the malicious input harmlessly. Prefer a real test
over assertion; if the stack has a test runner, write the test.

## References

- `references/remediation.md` — Copyable before/after fixes for each
  vulnerability class. Read it when implementing a remediation rather than
  reconstructing the pattern from memory.
- `references/owasp-map.md` — Maps each class here to its OWASP Top 10 category,
  for users who need to report findings in OWASP terms.
