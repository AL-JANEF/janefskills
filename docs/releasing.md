# Releasing

## Release gate

1. Update the version in `config/skills.json`, `.claude-plugin/plugin.json`, and
   `.claude-plugin/marketplace.json`.
2. Add an ISO-dated entry to `CHANGELOG.md`.
3. Run `make check`.
4. Run `claude plugin validate .` when Claude Code is available.
5. Run `gitleaks dir .` and `gitleaks git .` when Gitleaks is available.
6. Review the diff for offensive content, secrets, broken references, and
   accidental skill removals.
7. Tag the exact validated commit with `v<version>` and publish release notes
   from the changelog.

## Versioning

- **Patch** — wording or correctness fixes that preserve behavior and paths.
- **Minor** — additive skill capability, metadata, packaging, or tooling.
- **Major** — a breaking skill rename, removal, or behavior contract change.

Never reuse or silently move a published tag. A release should always identify
the exact content users validated and installed.
