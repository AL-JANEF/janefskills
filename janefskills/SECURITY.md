# Security Policy

## Scope

This repository contains **documentation-only** skills — Markdown instructions and
illustrative code snippets for [Claude Code](https://docs.claude.com/en/docs/claude-code).
It ships no runnable application, service, or binary. There is no server to
compromise and no dependency to exploit.

That said, the *content* still matters: a skill that gave wrong or dangerous
guidance would be a real problem. This policy covers that.

## What counts as a reportable concern

- A skill that recommends an **insecure pattern** as if it were safe.
- A code sample containing a **vulnerability** that a reader might copy.
- Guidance that could be **misused offensively**, or that drifts from the
  defensive-only principle.
- A factual error in a security claim that could lead someone to ship unsafe code.

## How to report

Please **do not** open a public issue for a security concern about the content.
Instead:

- Use GitHub's **private vulnerability reporting** on this repository
  (Security tab → "Report a vulnerability"), or
- Contact the maintainer through the profile at
  [github.com/AL-JANEF](https://github.com/AL-JANEF).

Include the skill and section involved, what's wrong, and — if you have one — the
corrected guidance.

## What to expect

- Acknowledgement of your report as soon as it's reviewed.
- An honest assessment of whether it's in scope and how it'll be addressed.
- Credit for the finding if you'd like it (or anonymity if you prefer).

## Responsible use

These skills are provided to help people build **more secure** software. Using the
guidance here to attack systems you don't own or have permission to test is
against the spirit and terms under which this is shared. Keep it defensive.
