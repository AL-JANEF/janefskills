---
name: secrets-guard
description: >-
  Prevent secrets from leaking into code, git history, logs, or client bundles —
  API keys, database credentials, tokens, private keys, and connection strings.
  Detects hardcoded secrets, guides correct secret management (env vars, secret
  managers), and sets up prevention (gitignore, pre-commit scanning). Use this
  skill whenever the user is handling API keys or credentials, setting up
  environment variables, connecting to external services, committing config, or
  asks about keeping secrets safe — even a casual "where do I put my API key?".
  Defensive only.
license: MIT
---

# Secrets Guard

A leaked secret is one of the fastest paths to a breach — a single committed API
key can hand an attacker the whole system. This skill keeps secrets out of the
places they leak from, and cleans them up when they've already landed there.

The rule underneath everything: **a secret belongs in the runtime environment,
never in the source.** If it's in a file that gets committed, shipped to the
browser, or printed to a log, treat it as compromised.

## When to reach for this skill

Use it whenever code touches credentials: adding an API key, wiring up a database
connection, configuring an external service (payment, messaging, storage),
setting up `.env` files, or committing configuration. Also whenever the user asks
where to store a key or whether something is safe to commit. The presence of a
credential is the trigger.

## What to do

### 1. Detect secrets already present

Scan for hardcoded credentials in the code and config: high-entropy strings,
`apiKey = "..."`, connection strings with embedded passwords, private key blocks,
tokens in source. Common shapes: cloud keys, database URLs like
`postgres://user:pass@host`, JWT signing secrets, third-party service keys
(payment, messaging). Also check what's already committed to git history, not
just the working tree — a secret removed from the current code but still in
history is still leaked.

If a real secret is found in code or history: flag it as **compromised** and
requiring rotation, not just removal. Once a secret has been committed to a shared
repo, deleting it doesn't un-leak it — it must be rotated (regenerated) at the
provider. See `references/leak-response.md`.

### 2. Move secrets to the environment

Secrets load from environment variables (or a secret manager), never from source:
```
// wrong — in source
const key = "sk_live_abc123";

// right — from environment
const key = process.env.STRIPE_SECRET_KEY;
```
Provide a committed `.env.example` with the *names* and dummy values, and keep the
real `.env` untracked. For production, prefer a managed secret store (the
platform's secret manager) over shipping `.env` files around.

### 3. Watch the client boundary

The most dangerous secret leak in modern frameworks: putting a secret in code
that ships to the browser. In Next.js and similar, anything prefixed for client
exposure (e.g. `NEXT_PUBLIC_*`) is embedded in the bundle and readable by anyone.
A secret must never carry a public/client prefix. Only truly public values
(publishable keys designed for the client) belong there. Verify which side of the
client/server boundary each key lives on.

### 4. Prevent recurrence

Set up guards so secrets can't slip in again:
- `.gitignore` includes `.env`, `.env.*` (but allow `.env.example`).
- A pre-commit secret scanner (gitleaks, or a hook) blocks commits containing
  secret-shaped strings.
- Never log secrets — check that error handlers and request loggers don't print
  auth headers, tokens, or connection strings.

See `references/setup.md` for concrete gitignore, `.env.example`, and pre-commit
scanner configuration.

## Output format

When auditing, report clearly and rank by exposure:

```
## Secrets Audit: <target>

### Exposed / compromised   (rotate immediately)
- <secret type> at <location> — committed / in history / in client bundle → rotate + remove

### Misplaced   (move to environment)
- <secret> hardcoded at <location> → move to env var <NAME>

### Prevention gaps
- <e.g. .env not gitignored, no pre-commit scan>

### Verified good
- <secrets correctly externalized>
```

Do not print the full secret value in the report — reference it by type and
location (`Stripe secret key in config.js:12`), show at most a masked fragment.
Printing it in full just copies the leak into a new place.

## Proof before done

Demonstrate the fix: the secret no longer appears in the built client bundle
(grep the build output), the app still runs reading from env, and the pre-commit
scanner actually blocks a test secret. For a rotated key, confirm the old one is
revoked at the provider.

## References

- `references/setup.md` — Copyable `.gitignore`, `.env.example`, and pre-commit
  secret-scanner config. Read it when setting up prevention.
- `references/leak-response.md` — Step-by-step response when a real secret has
  already been committed (rotate, purge, prevent). Read it when a live leak is
  found.
