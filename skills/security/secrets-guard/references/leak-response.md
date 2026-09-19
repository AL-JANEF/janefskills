# Leak Response

What to do when a real secret has already been committed or exposed. The order
matters: rotate first, because a committed secret is compromised the moment it
lands in shared history.

## 1. Rotate immediately (most important)

Regenerate the secret at the provider so the leaked value stops working. This is
the only step that actually closes the exposure — everything else is cleanup.
- Cloud/API keys: revoke and reissue in the provider console.
- Database passwords: change the password, update the app's env.
- JWT signing secrets: rotate the secret (this invalidates existing tokens — plan
  for re-login).
- Third-party service tokens (payment, messaging): revoke and reissue.

Do this even if you're about to purge git history. History can be cloned, cached,
or forked faster than you can scrub it — assume the value is already out.

## 2. Remove from current code

Replace the hardcoded value with an environment variable read, and confirm the
app runs from env.

## 3. Purge from git history (if committed)

Removing a secret in a new commit does NOT remove it from history. Use a history-
rewriting tool:
```bash
# with git-filter-repo (preferred)
git filter-repo --path config.js --invert-paths   # or use --replace-text
```
Then force-push and have collaborators re-clone. Note: on shared repos this
rewrites history for everyone — coordinate. On many hosts the value may still
exist in cached views or forks, which is why step 1 (rotation) is non-negotiable.

## 4. Prevent recurrence

Add the prevention setup (see `setup.md`): gitignore the env files, add a
pre-commit secret scanner, and confirm no secret carries a client/public prefix.

## Summary

Rotate → remove from code → purge history → prevent. If you only have time for
one step, it's rotate — a revoked secret is harmless no matter where copies of it
still live.
