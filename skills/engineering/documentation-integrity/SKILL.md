---
name: documentation-integrity
description: >-
  Document implemented, verified reality in the repository's existing source
  of truth: READMEs, API references, ADRs, runbooks, migration notes,
  changelogs, and code comments. Use when documentation must be written,
  updated, or checked for drift; never document unverified capabilities.
license: MIT
---

# Documentation Integrity

Document implemented and verified reality, not intent. A document that promises unverified behavior is a defect.

## Rules

- Update the repository's existing source of truth instead of creating a competing document. If there is no obvious location, ask before adding a top-level file.
- Record material architecture changes in the established ADR or design mechanism (`architecture-integrity`).
- Update API contracts, examples, migration notes, operational runbooks, and configuration guidance when those surfaces change, in the same change.
- Keep documentation concise, searchable, version-consistent, and explicit about invariants, ownership, failure behavior, and recovery where relevant.
- Repair stale documentation encountered in the changed scope when it would mislead future maintainers; mention, do not silently rewrite, stale docs outside the scope.
- Never claim capabilities, guarantees, compatibility, or performance that were not verified. Mark illustrative examples as illustrative.
- Comments explain why, not what; remove comments that restate the code or that are no longer true.

## Verification

Cross-check documented commands, paths, and behavior against the code or an actual run. Verify links and examples. State what was verified and what is documented from design only.
