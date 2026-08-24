# Contributing to janefskills

Thanks for your interest in improving these skills. Contributions that make them
sharper, clearer, or more correct are very welcome.

## The one hard rule: defensive only

These are **defensive** security skills. Every contribution must keep them that
way. We will not accept anything that:

- provides working exploit code, attack payloads, or bypass techniques;
- facilitates unauthorized access, privilege escalation, or data exfiltration;
- weakens a control rather than strengthening it;
- teaches how to attack a system rather than how to defend or verify one.

Describing an *impact* to justify a fix ("an attacker could read other users'
records, so scope the query") is fine and expected. Handing over a runnable
attack is not. When in doubt, err toward defense.

## What makes a good contribution

- **Correctness fixes.** If a pattern, code sample, or claim is wrong or outdated,
  fix it and say why.
- **Clarity.** Tighter wording, better structure, clearer examples.
- **Coverage gaps.** A missing case within an existing skill's scope (e.g. another
  common injection sink in `vuln-audit`).
- **New skills.** A genuinely new defensive skill that fits the suite. Open an
  issue to discuss scope first — skills should be focused, not sprawling.

## Skill quality standards

If you add or edit a skill, keep it to the same bar as the rest:

- **Valid frontmatter.** `name`, a precise `description` that states *when* the
  skill should trigger (written in the third person), and `license`.
- **Focused scope.** One skill, one job. If it's trying to do everything, split it.
- **Under ~500 lines** in `SKILL.md`. Deeper material goes in `references/`,
  loaded only when needed (progressive disclosure).
- **Imperative, concrete instructions** — tell Claude what to do and how to verify,
  not vague principles.
- **A proof-before-done step.** Every skill must require evidence for its claims.
- **A severity-ranked output format**, consistent with the others.
- **Host metadata.** Keep `agents/openai.yaml` consistent with the skill name,
  description, and intended prompt.

## Local verification

Run the complete repository gate before opening a pull request:

```bash
make check
```

When Claude Code is available, also validate the plugin package:

```bash
claude plugin validate .
```

The installer test uses temporary directories and never writes to your personal
Claude Code or Codex configuration.

## Submitting

1. Fork the repo and create a branch (`fix/vuln-audit-nosql`, `skill/csp-header`).
2. Make your change; keep commits focused with clear messages.
3. Run the local verification gate and include the evidence.
4. Open a pull request describing what changed and why. If it's a new skill or a
   scope change, link the discussion issue.
5. Confirm your change is defensive-only.

## Reporting problems

- **Bugs / inaccuracies in a skill:** open a GitHub issue.
- **A security concern about the skills themselves:** see
  [SECURITY.md](./SECURITY.md).

By contributing, you agree your contributions are licensed under the repository's
[MIT License](./LICENSE).
