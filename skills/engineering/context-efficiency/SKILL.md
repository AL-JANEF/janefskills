---
name: context-efficiency
description: >-
  Tactics for large repositories, noisy tool output, long sessions, and token
  pressure: search before reading, read ranges not files, keep logs and
  generated output out of context, never reread unchanged files or rerun
  unchanged passing checks, prefer deterministic scripts. Use when context
  volume materially affects execution quality; never reduces necessary
  reasoning, security, or verification.
license: MIT
---

# Context Efficiency

Efficiency removes waste, never evidence. It must not reduce necessary reasoning, security review, or verification.

## Load by decision

- Start with repository instructions, the target symbol, its callers, and its focused tests.
- Search filenames, symbols, call sites, and Git history before opening files; read narrow ranges around matches rather than entire files.
- Load one capability or reference when it changes the next decision. Do not preload the catalog.
- Keep dependencies, lockfile bodies, generated output, build artifacts, and large logs out of context unless directly required. Store large raw outputs as files and inspect slices or summaries.

## Avoid repeated work

- Do not reread unchanged files or rerun unchanged passing checks.
- Avoid duplicate agents, duplicate reviews, and overlapping skills.
- Prefer deterministic local scripts for repeatable parsing, discovery, counting, and validation.
- Run targeted tests first; broaden only when change risk requires it.

## Spend context where risk lives

Keep API contracts, security boundaries, migrations, concurrency, and failures visible. Compress boilerplate and settled facts, not unresolved evidence.

## Stop conditions

Stop exploring when acceptance criteria, affected boundaries, and a falsifiable implementation path are clear. Re-open context when a test contradicts the model, a hidden caller appears, or scope changes.

Character-based token estimates are useful for regressions but are not provider billing measurements or quality evidence. Delegation (`delegation-discipline`) is justified only when isolation or parallelism saves more than coordination costs.
