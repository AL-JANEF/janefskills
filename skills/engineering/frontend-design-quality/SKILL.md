---
name: frontend-design-quality
description: >-
  Implement visual frontend work with an intentional design direction: inspect
  the existing design system and tokens, design mobile and desktop
  deliberately, implement every state (loading, empty, error, disabled,
  overflow, permission-denied), protect hierarchy and layout stability, and
  verify rendered behavior. Always composes with accessibility-quality. Use
  for UI implementation, styling, layout, and component work.
license: MIT
---

# Frontend Design Quality

Inspect before you style. The existing design system, brand, tokens, components, typography, spacing, and interaction patterns are the source of truth; one-off styling is drift.

## Direction

- Choose an intentional visual direction appropriate to the product. Avoid generic template aesthetics, decorative noise, and gradients-for-their-own-sake.
- Use reusable tokens and components instead of one-off values. Extend the system deliberately when it genuinely lacks something.
- Design mobile and desktop deliberately rather than compressing a desktop layout. Protect visual hierarchy, readability, contrast, alignment, and layout stability.

## Boundaries

- The server is authoritative for permissions and protected data; client checks improve UX, they are not authorization.
- Keep server state, URL state, form state, and transient UI state distinct. Reuse the project's data-fetching and error patterns; do not add a state library for local state without demonstrated cross-component need.
- Avoid unsafe HTML injection; encode for the rendering context and review any sanitizer configuration (`vuln-audit` for anything user-authored).

## States

Implement loading, empty, success, stale, error, disabled, read-only, permission-denied, overflow, and long-content states where applicable, before polishing the happy path. Prevent race-driven stale updates with cancellation, request identity, or the framework's data layer.

## Motion

Use motion to communicate hierarchy or state, never as decoration alone, and respect `prefers-reduced-motion`.

## Accessibility

Non-negotiable and always composed with this capability: semantic HTML, keyboard order, focus restoration, labels, contrast, zoom, and reflow (`accessibility-quality`).

## Verification

Verify rendered behavior, not source alone: mobile and desktop breakpoints, focus states, each implemented state, and the important flows. Measure bundle or render cost only when the task affects them (`performance-scalability`).
