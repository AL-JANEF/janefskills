# Lean profile

Use for focused changes whose scope is already understood: a bug with a clear reproduction, a small feature inside an existing pattern, a refactor with tests in place. Lean removes waste, never evidence.

## Operating rules

- Load at most two capabilities and one reference. If a third seems necessary, the task is not lean; switch to `standard`.
- Read repository instructions, the target symbol, its callers, and its focused tests. Do not read whole files or directories without a named reason.
- Ship one coherent, reviewable diff. No speculative abstractions, no new dependencies, no unrelated cleanup.
- One agent. Delegation is off unless the user asks for it.
- Verification ladder: run the cheapest check that can disprove the change, then the focused test, then stop unless risk demands more.
- Stop exploring when acceptance criteria, affected boundaries, and a falsifiable implementation path are clear. Re-open context only when a test contradicts the model, a hidden caller appears, or scope changes.

## What Lean does not change

- The engineering contract and its security rules apply in full.
- High or critical risk still auto-includes `testing-verification`. Lean does not escalate to `high-assurance` on its own; it reports the risk so the user can choose.
- If a required check cannot run, say exactly why and what remains.
