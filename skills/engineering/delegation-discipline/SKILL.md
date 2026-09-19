---
name: delegation-discipline
description: >-
  Decide whether subagents, parallel agents, or agent teams are justified and,
  if so, delegate safely: one agent unless work is bounded, independent, and
  clearly owned; explicit outcome, ownership, constraints, and return format
  per worker; the integrating agent owns final correctness, security review,
  and verification. Use whenever delegation or parallel execution is being
  considered.
license: MIT
---

# Delegation Discipline

One agent by default. Delegation is an optimization for genuinely independent work, not a quality badge, and never a way to bypass approvals or expand scope.

## Selection gate

Use a single agent unless at least one condition holds:

- A bounded investigation would consume substantial context and can return a concise evidence summary.
- Two or more subtasks are independent, have non-overlapping ownership, and can proceed concurrently.
- A specialist or independent review is required by the repository or by the change's risk.

Do not delegate a small edit, a sequential dependency chain, or work whose integration needs continuous shared context.

## Cost check

Expected value must exceed setup, duplicated reading, communication, review, and merge costs. If ownership cannot be stated in one sentence, the split is not ready.

## Delegation contract

Give each worker one concrete outcome; explicit file or subsystem ownership; acceptance criteria, constraints, and permitted side effects; the minimum raw context needed, without leading it to a preferred conclusion; and a required return format: findings or files changed, tests run, risks, unresolved questions.

Workers preserve other agents' and the user's changes and avoid overlapping writes. The integrating agent owns final correctness, security review, conflict resolution, and verification. Delegated results are evidence to check, not conclusions to repeat.

## Completion

Never end a turn while delegated work is outstanding; collect every result, integrate, verify, then report. Return to one agent when tasks become coupled, agents duplicate investigation, merge cost grows, or the next decision needs the same context.
