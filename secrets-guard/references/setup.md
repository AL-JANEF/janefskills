# Secrets Prevention Setup

Copyable configuration to keep secrets out of the repo.

## .gitignore

```gitignore
# Environment / secrets
.env
.env.*
!.env.example
*.pem
*.key
secrets/
```

The `!.env.example` line re-includes the example file so the *names* of required
variables are documented and committed, while real values stay out.

## .env.example

Commit this; it documents required variables with placeholder values.

```dotenv
# Database
DATABASE_URL=postgres://user:password@localhost:5432/dbname

# Third-party services
STRIPE_SECRET_KEY=sk_test_placeholder
WHATSAPP_API_TOKEN=placeholder

# Auth
JWT_SECRET=replace_with_a_long_random_value

# Public (client-safe) values only
NEXT_PUBLIC_SUPABASE_URL=https://placeholder.supabase.co
NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY=placeholder
```

Note the split: only genuinely client-safe, publishable values carry a public
prefix. A secret key must never be prefixed for client exposure.

## Pre-commit secret scanning (gitleaks)

Install gitleaks, then add a pre-commit hook so secret-shaped strings are blocked
before they're ever committed.

`.pre-commit-config.yaml`:
```yaml
repos:
  - repo: https://github.com/gitleaks/gitleaks
    rev: v8.18.0
    hooks:
      - id: gitleaks
```

Or a bare git hook at `.git/hooks/pre-commit`:
```bash
#!/bin/sh
gitleaks protect --staged --redact --verbose || {
  echo "Potential secret detected — commit blocked."
  exit 1
}
```
Make it executable: `chmod +x .git/hooks/pre-commit`.

## Don't log secrets

Check request loggers and error handlers don't emit auth headers or tokens:
```js
// redact sensitive headers before logging
const safe = { ...req.headers };
delete safe.authorization;
delete safe.cookie;
logger.info({ headers: safe });
```
