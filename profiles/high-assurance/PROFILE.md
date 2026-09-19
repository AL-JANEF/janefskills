# High-assurance profile

For work where a mistake is expensive or hard to reverse: authentication, authorization, tenant isolation, sessions, secrets, migrations, RLS, privilege boundaries, payments, personal data, infrastructure, and production changes.

## Operating rules

- Verification floor is `high`: integration or contract tests across the boundary, one denied path and one adversarial input, a security scan of the changed surface (or an explicit NOT RUN), and an independent defect-first review.
- Critical risk adds: real database or environment verification for schema, RLS, or privilege changes; a mutation check proving that weakening the enforcing control fails a required test; a verified rollback path; and recorded user authorization for destructive steps.
- `review-defect-first` is always applied. At critical risk `variant-hunt` sweeps for siblings of any finding.
- Still context-disciplined: at most five routed capabilities plus their dependencies. Depth comes from verification and review, not from loading every skill.
- Report coverage honestly: which layers ran, what they cannot cover, and the residual risk.
