---
name: janef
description: >-
  Deprecated compatibility alias for /janef from janefskills 1.x. Forwards to
  the forge entry point; /janef <task> behaves like /forge <task> and /janef
  full security pass behaves like /forge security pass. Do not use for new work.
license: MIT
---

# janef → forge

`janef` was the janefskills 1.x command layer. In JANEF Forge 2.0 it is an alias:

- `/janef <task>` → apply the `forge` capability to `<task>`.
- `/janef full security pass` → apply `forge` with `security-audit`.
- `/janef audit <target>` → `forge` routes to `vuln-audit` (and `variant-hunt` after a finding).

Load `forge` and continue there. Do not load both. This alias will be removed in 3.0; see `docs/migration-v2.md`.
