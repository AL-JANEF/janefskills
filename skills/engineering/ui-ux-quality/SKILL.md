---
name: ui-ux-quality
description: >-
  Make product flows clear and recoverable: primary action and next step
  obvious, forms with clear labels, validation timing, actionable errors,
  preserved input on failure, consistent navigation and terminology, and no
  hidden or surprising destructive actions. Use for user flows, forms,
  navigation, onboarding, dialogs, and interaction design.
license: MIT
---

# UI/UX Quality

Optimize for task clarity, confidence, error prevention, and recovery. The user should always know where they are, what happens next, and how to undo it.

## Principles

- Make the primary action, current state, context, and next step obvious.
- Keep navigation, terminology, and interaction patterns consistent with the rest of the product.
- Minimize unnecessary steps without hiding important decisions or risk.
- Avoid hidden critical actions, ambiguous icons, hover-only affordances, and surprising destructive behavior. Destructive actions confirm, are reversible where possible, or are clearly labeled as irreversible.

## Forms

Clear labels, sensible defaults, validation at the right moment (not on every keystroke, not only on submit), actionable error messages next to the field, and preserved input on recoverable failure. Never lose a user's work to a validation error.

## Flows

Verify first-use, empty, loading, failure, retry, permission-denied, and completion flows. Each has a clear message and a clear next step.

## Evidence

Prefer evidence from rendered flows and task completion over aesthetic opinion alone. Compose with `frontend-design-quality` for visual implementation and `accessibility-quality` for keyboard and assistive-technology behavior.
