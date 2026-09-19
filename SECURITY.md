# Security Policy

## Scope

This repository contains Markdown skills, illustrative code snippets, and small
standard-library utilities for installation, validation, routing, and packaging. It
ships no service, privileged daemon, dependency bundle, or remote execution
component. The installer copies only selected skill directories, refuses to replace
an existing installation unless the user explicitly chooses `--force` or
`--upgrade` (both back up the previous content), records what it owns, and removes
only that on uninstall. `scripts/audit_skill.py` reads external skill text; it never
executes candidate code, and its result is a control, not proof of safety.

Threats considered and their controls are summarized in
`docs/architecture/JANEF_FORGE_ARCHITECTURE.md` § "Security model".

That said, the *content* still matters: a skill that gave wrong or dangerous
guidance would be a real problem. This policy covers that.

## What counts as a reportable concern

- A skill that recommends an **insecure pattern** as if it were safe.
- A code sample containing a **vulnerability** that a reader might copy.
- Guidance that could be **misused offensively**, or that drifts from the
  defensive-only principle.
- A factual error in a security claim that could lead someone to ship unsafe code.
- Installer behavior that overwrites, escapes the requested destination, follows a
  symlink, or fails to preserve an existing skill as documented.
- A routing or composition rule that would load a security capability less often than
  the task warrants, or a profile that lowers a verification floor.
- A static-triage pattern gap that lets a clearly malicious skill pass the gate.

## How to report

Please **do not** open a public issue for a security concern about the content.
Instead:

- Use GitHub's **private vulnerability reporting** on this repository
  (Security tab → "Report a vulnerability"), or
- Contact the maintainer through the profile at
  [github.com/AL-JANEF](https://github.com/AL-JANEF).

Include the skill and section involved, what's wrong, and — if you have one — the
corrected guidance.

Never attach live credentials, private source code, or personal data. Use a
minimal redacted reproduction.

## What to expect

- Acknowledgement of your report as soon as it's reviewed.
- An honest assessment of whether it's in scope and how it'll be addressed.
- Credit for the finding if you'd like it (or anonymity if you prefer).

## Responsible use

These skills are provided to help people build **more secure** software. Using the
guidance here to attack systems you don't own or have permission to test is
against the spirit and terms under which this is shared. Keep it defensive.
