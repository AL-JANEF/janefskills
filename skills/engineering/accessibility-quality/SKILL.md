---
name: accessibility-quality
description: >-
  Ship UI that works with keyboard and assistive technology: semantic HTML and
  native controls first, ARIA only to supplement, logical focus order with
  visible focus and escape paths, programmatic labels and error association,
  contrast and non-color meaning, alt text, reduced motion, zoom and reflow.
  Use for any user-facing UI change and for WCAG audits; never knowingly ship
  an accessibility regression.
license: MIT
---

# Accessibility Quality

Accessibility is a correctness requirement for user-facing UI, not a polish step. Never knowingly ship an accessibility regression.

## Rules

- Semantic HTML and native controls first. ARIA supplements semantics; it does not replace a correct element.
- Keyboard access for everything interactive: logical focus order, visible focus, focus return after dialogs, and an escape path for overlays and traps.
- Every input has a programmatic label. Errors and status messages are associated with their field and announced.
- Do not convey meaning by color alone. Check contrast for text and non-text indicators.
- Meaningful images get meaningful alternative text; decorative images stay out of the accessibility tree.
- Respect reduced motion, zoom and text scaling, and responsive reflow.
- Check headings, landmarks, tables, names/roles/states, and touch targets on the changed surface.

## Verification

A keyboard-only pass of the changed surface; names, roles, states, and contrast checked for changed controls; a screen-reader or automated check (for example axe) where available. Report what was checked and what was not.
