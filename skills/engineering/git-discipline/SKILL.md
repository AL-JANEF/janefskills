---
name: git-discipline
description: >-
  Keep history safe and meaningful: inspect status and diff before and after
  editing, preserve unrelated user work, scope commits logically, write
  accurate messages, resolve conflicts by understanding both sides, and never
  rewrite shared history, force-push, or discard work without explicit
  authorization. Use for commits, branches, merges, rebases, and PR hygiene.
license: MIT
---

# Git Discipline

History is shared state. Preserve it and the user's uncommitted work.

## Before and after

- Inspect `git status` and the relevant diff before editing; inspect the final diff before reporting completion.
- Preserve unrelated user changes and untracked files. Never stage or revert work you did not create without being asked.

## Commits and branches

- Keep changes logically scoped; avoid unrelated formatting churn. One coherent change per commit.
- Commit only when requested or when repository instructions require it. Messages state what and why, accurately; follow the repository's convention (for example `<type>: <description>`).
- Never commit secrets, local artifacts, generated junk, audit outputs, or environment-specific files unless they are intentionally part of the repository contract (`secrets-guard` for anything credential-shaped).
- Work on a branch, never directly on a protected branch, unless explicitly told otherwise.

## Never without explicit authorization

Destructive `reset --hard`, `clean -f`, `checkout --` over local changes; rewriting shared history (rebase or amend of pushed commits); force-push; deleting branches or tags; changing remotes; merging to protected branches.

## Conflicts

Resolve by understanding both sides and the intent of each change, not by mechanically choosing one. Re-run the affected tests after resolution.

## Pull requests

Summarize the full commit range (`git diff <base>...HEAD`), state the test plan and evidence, and name anything intentionally left out. Push with `-u` for a new branch.
