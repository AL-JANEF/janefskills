---
name: review-defect-first
description: >-
  Independent review of a diff, PR, or file that hunts concrete defects
  introduced by the change: correctness, security, data loss, authorization or
  tenant escape, production failure, broken contracts, performance
  regressions, missing critical tests. Severity-ordered findings citing a real
  code path; no style inflation; "no qualifying defect" is valid. Use for code
  review and as the independent gate at high risk.
license: MIT
---

# Defect-First Review

A review exists to find concrete, actionable defects introduced by the change. Style preferences, speculative concerns, and unsupported findings are noise; "no qualifying defect found" is a valid, honest result.

## Method

1. Read applicable repository instructions and the complete relevant diff, plus enough surrounding code to trace behavior end to end.
2. Continue through the whole diff; do not stop at the first finding.
3. Prioritize: correctness, security, data loss, authorization or tenant escape, production failure, broken contracts, performance regressions, missing critical tests. Then maintainability issues that will cause defects.
4. Confirm each finding from a real code path, call site, invariant, or test gap. If you cannot point at it, it is not a finding.
5. Order by severity and cite the smallest useful path and line range.
6. End with residual risks and material verification gaps only.

The dimension checklist and the forbidden-pattern scan are in `references/review-checklist.md`.

## Severity

- **Blocking**: correctness or security defect, data loss, authorization escape, broken contract.
- **Should fix**: real issue that is not blocking merge.
- **Consider**: hardening or improvement with a concrete benefit.
- **Verified good**: what is demonstrably correct; say so.

## Output

```
## Review: <target>
### Blocking
- <file:line> — <defect> → <fix>  (evidence: <path/test/invariant>)
### Should fix
### Consider
### Verified good
### Residual risk / not verified
```

Reviewers report; they do not edit. Route security-class findings to `vuln-audit` for remediation and to `variant-hunt` to sweep for siblings.
