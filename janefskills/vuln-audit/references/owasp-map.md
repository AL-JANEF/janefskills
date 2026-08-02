# OWASP Top 10 Map

Maps the vulnerability classes in this skill to the OWASP Top 10 (2021)
categories, for reporting findings in standard terms.

| This skill's class | OWASP Top 10 (2021) |
|--------------------|---------------------|
| Broken access control / IDOR | A01: Broken Access Control |
| Injection (SQL/NoSQL/command) | A03: Injection |
| XSS | A03: Injection (XSS folded in here) |
| Insecure deserialization | A08: Software and Data Integrity Failures |
| Security misconfiguration | A05: Security Misconfiguration |
| SSRF | A10: Server-Side Request Forgery |
| CSRF | A01 / A05 (access control + config) |
| Unsafe file upload | A04: Insecure Design / A05 |
| Weak crypto / password storage | A02: Cryptographic Failures |
| Missing logging/monitoring | A09: Security Logging and Monitoring Failures |

Notes:
- A02 (Cryptographic Failures) and parts of authentication are covered more
  fully by the `auth-hardening` skill.
- A09 (Logging & Monitoring) is covered by the `security-logging` skill.
- A04 (Insecure Design) is addressed proactively by the `threat-model` skill at
  design time.

The OWASP Top 10 is a living list; when reporting to a team, confirm which
edition they use, as category numbers shift between revisions.
