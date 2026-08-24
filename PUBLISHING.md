# Publishing and Repository Setup

This file records public repository metadata and the release workflow. Runtime
skills do not load it.

## Repository metadata

**Description**

```text
Defensive security and production-engineering skills for Claude Code and Codex — auth, OWASP, threats, secrets, and logging.
```

**Topics**

```text
agent-skills
appsec
authentication
claude-code
codex
defensive-security
devsecops
owasp
secure-coding
security
skills
threat-modeling
```

## Claude Code marketplace

The repository is its own marketplace. Users install it inside Claude Code with:

```text
/plugin marketplace add AL-JANEF/janefskills
/plugin install janefskills@janefskills
```

The plugin version is pinned in both files under `.claude-plugin/`. Bump both on
every release so installed users receive updates.

## Release workflow

Follow [docs/releasing.md](./docs/releasing.md). Do not create a tag until the
local gate and Claude plugin validation pass on the exact release commit.

## Recommended GitHub settings

- Keep private vulnerability reporting enabled.
- Keep secret scanning and push protection enabled when GitHub offers them.
- Require the CI workflow before merging changes to `main`.
- Review dependency and action updates manually; no automated update bot is
  required by this repository.
