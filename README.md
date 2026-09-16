<p align="center">
  <img src="./assets/banner.svg" alt="janefskills — eight defensive security and engineering skills for Claude Code" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-D4AF61" alt="MIT License">
  <img src="https://img.shields.io/badge/skills-8-16273F" alt="8 skills">
  <img src="https://img.shields.io/badge/version-1.2.0-D4AF61" alt="Version 1.2.0">
  <img src="https://img.shields.io/badge/scope-defensive%20only-0E1A2B" alt="Defensive only">
  <img src="https://img.shields.io/badge/methodology-audit--grade-1A2E4A" alt="Audit-grade methodology">
  <img src="https://img.shields.io/badge/Claude%20Code-primary-9DB0C8" alt="Claude Code primary">
  <img src="https://img.shields.io/badge/Codex-metadata-16273F" alt="Codex metadata">
  <br>
  <img src="https://img.shields.io/github/stars/AL-JANEF/janefskills?style=flat&color=D4AF61" alt="GitHub stars">
  <img src="https://img.shields.io/github/last-commit/AL-JANEF/janefskills?color=16273F" alt="Last commit">
</p>

<h1 align="center">janefskills</h1>

<p align="center">
  <strong>Eight defensive-security and engineering skills that give Claude the instincts of a security-minded staff engineer.</strong><br>
  Built for <a href="https://code.claude.com/docs/en/overview">Claude Code</a>, with Codex UI metadata and portable Agent Skills structure.
</p>

---

## Why this exists

Most breaches don't come from exotic exploits — they come from ordinary mistakes:
a logout that never invalidates its token, a query built from user input, a secret
committed to git, an endpoint that forgets to check ownership. These are known,
preventable patterns. What's missing is usually a reviewer disciplined enough to
catch them *every time* and honest enough to prove the fix.

That's what janefskills is. It makes Claude review and build software to a strict,
verifiable standard, and refuses to call code "done" until the fix is
demonstrated — not asserted. Every skill is **defensive only**: it hardens,
audits, and verifies; it never attacks or bypasses.

Built for modern web stacks (TypeScript, Node, Next.js, multi-tenant systems),
with principles that transfer anywhere.

---

## The suite at a glance

| Phase | Skill | What it does |
|-------|-------|--------------|
| **Orchestrate** | [`janef`](./janef) | One command (`/janef`) that routes to the right skill or runs a full audit-grade pass. Also the suite's technical reference. |
| **Design** | [`threat-model`](./threat-model) | STRIDE risk analysis before code exists — the cheapest place to fix. |
| **Build** | [`auth-hardening`](./auth-hardening) | Login, logout, sessions, passwords, tokens, MFA, brute-force. |
| **Build** | [`secrets-guard`](./secrets-guard) | Keeps credentials out of code, git history, logs, and client bundles. |
| **Audit** | [`vuln-audit`](./vuln-audit) | OWASP Top 10 review: injection, XSS, CSRF, SSRF, IDOR, uploads. |
| **Audit** | [`variant-hunt`](./variant-hunt) | After one bug is found, sweeps the codebase for every sibling. |
| **Audit** | [`security-logging`](./security-logging) | Audit trails & anomaly detection, without leaking data into logs. |
| **Enforce** | [`engineering-standard`](./engineering-standard) | Truth policy, no dead code, red-team review, evidence-gated completion. |

---

## What's inside

### `janef` — the command layer
One command for the whole suite. Type `/janef` followed by what you need — it
routes to the right specialist, or runs the **audit-grade full pass** that layers
real automated tooling (Semgrep SAST, Gitleaks, dependency audit) with expert
review, professional audit methodology (variant analysis, fix verification,
constant-time review), and an *honest coverage verdict*.

```
/janef review the login flow → routes to auth-hardening
/janef audit this file → routes to vuln-audit
/janef full security pass → runs all layers, one consolidated report
```

It never claims "secure" unqualified — it states which layers ran and what class
of attack it structurally can't cover. That honesty is the point.

### `engineering-standard`
The quality bar for any serious coding work. It enforces a **truth policy** (never
claim success without evidence, never modify a test to make it pass, never hide a
failure), bans placeholder and dead code, runs a red-team pass over every change,
and gates completion on lint + typecheck + tests + build — each with shown
evidence. Triggers on any real implementation, review, refactor, or "is this
production-ready?" question.

### `threat-model`
A structured **STRIDE** threat-modeling pass at design time — before code exists,
when fixes are cheapest. It names the assets and trust boundaries, walks Spoofing
/ Tampering / Repudiation / Information disclosure / Denial of service / Elevation
of privilege at each boundary, and turns the findings into concrete build tasks.
Triggers when you're designing a system, feature, or API.

### `auth-hardening`
Hardens the front door: **login, logout, sessions, password storage, tokens, and
brute-force protection.** It knows the traps — logout that doesn't actually
invalidate a JWT, passwords under a fast hash, tokens in `localStorage`, login
errors that leak which accounts exist — and fixes them with proven patterns.
Triggers on any auth or session work.

### `vuln-audit`
Audits code for the **OWASP Top 10** class of bugs: injection (SQL/NoSQL/command),
XSS, CSRF, SSRF, IDOR / broken access control, unsafe file upload, and
misconfiguration. Produces a severity-ranked report where every finding names the
concrete fix — no working exploits, just the impact and the remedy. Triggers when
reviewing code or handling untrusted input.

### `variant-hunt`
The professional follow-up to any finding: **one bug is almost never alone.** When
a vulnerability is confirmed, this skill sweeps the entire codebase for every other
instance of the same pattern — using ripgrep for a fast first pass and custom
Semgrep rules for structural matches — so the whole *class* gets fixed, not just
the reported case. It keeps the rule in the repo as permanent eradication evidence.
Triggers right after finding or fixing a security issue.

### `secrets-guard`
Keeps secrets out of the places they leak from: **code, git history, logs, and
client bundles.** It detects hardcoded credentials, catches the dangerous
`NEXT_PUBLIC_*`-style client-exposure mistake, guides secrets into the
environment, and sets up prevention (gitignore, pre-commit scanning). When a real
secret has leaked, it walks the rotate-first response. Triggers on any credential
or env work.

### `security-logging`
Designs **audit logging and suspicious-activity detection** that answers "who did
what, when" — without turning the logs themselves into a data leak. Covers what to
log (auth events, data changes, admin actions), what never to log (passwords,
tokens, PII), log integrity, and a few high-value detection rules like
failed-login thresholds. Triggers on audit trails, logging, and monitoring work.

### How they fit together

```
┌───────────────────────────────┐
│           /janef               │  ← one command,
│  orchestrates + references     │    routes to any skill
└───────────────────────────────┘
              │
┌─────────── DESIGN ───────────┬─────── BUILD ───────┬──────── AUDIT ─────────┐
│                               │                      │                        │
▼                               ▼                      ▼                        ▼
threat-model              auth-hardening          vuln-audit ──► variant-hunt
(risks, pre-code)         secrets-guard            (find the bug)  (find its siblings)
                           security-logging
│                               │                      │                        │
└──────────────────────────────┴─────────────────────┴────────────────────────┘
                                          │
                                          ▼
                        ┌───────────────────────────┐
                        │   engineering-standard      │  ← the bar under all of it:
                        │   truth · evidence · gate   │    proof before "done"
                        └───────────────────────────┘
```

`threat-model` names the risks before code exists; `auth-hardening` and
`secrets-guard` build the front door safely; `vuln-audit` finds bugs and
`variant-hunt` eradicates every sibling of each one; `security-logging` covers the
operational edge; `engineering-standard` holds all of it to an evidence-based bar;
and `/janef` ties them together into a single command and reference.

---

## Install

### Claude Code marketplace (recommended)

Inside Claude Code:

```text
/plugin marketplace add AL-JANEF/janefskills
/plugin install janefskills@janefskills
```

The plugin keeps every skill namespaced under `janefskills`, supports versioned
updates, and can be refreshed with `/plugin marketplace update`.

### Local development

```bash
git clone https://github.com/AL-JANEF/janefskills.git
cd janefskills
claude --plugin-dir .
```

Use `/janefskills:janef` for the orchestrator, or let Claude select a specialist
from the task description.

### Personal installation for Claude Code and Codex

The installer refuses to overwrite existing skills. With `--force`, it preserves
every previous skill directory as a timestamped backup before replacement.

```bash
python3 scripts/install.py --target both --dry-run
python3 scripts/install.py --target both
```

On Windows PowerShell, use the same installer with `python`:

```powershell
python scripts\install.py --target both --dry-run
python scripts\install.py --target both
```

Install a subset with `--only`, for example:

```bash
python3 scripts/install.py --target claude --only janef vuln-audit secrets-guard
```

If a dry run reports an existing installation, review the listed destinations.
Add `--force` only when you want the installer to preserve each current directory
as a timestamped backup and replace it.

Claude Code detects changes live when the skills directory was already being
watched; if the directory is new, restart once. Codex loads newly installed
skills on the next task.

---

## Usage

Skills can trigger from what you're doing, and you can invoke the orchestrator
explicitly when you want a coordinated pass. Examples:

- *"Review this authentication code before I ship it."* → `auth-hardening` +
  `vuln-audit`
- *"I'm designing a multi-tenant billing API — what could go wrong?"* →
  `threat-model`
- *"Is it safe to commit this config?"* → `secrets-guard`
- *"Add an audit trail for admin actions."* → `security-logging`
- *"Implement this feature to production quality."* → `engineering-standard`

Each produces a severity-ranked report or an implementation with evidence — and
holds itself to proving claims rather than asserting them.

### Example: a `/janef audit` pass

Illustrative shape of a finding, condensed from a real login-flow review:

```text
$ /janef audit src/api/auth/login.ts

[HIGH]   Session token stored in localStorage
         → readable by any injected script; move to an httpOnly, Secure,
           SameSite=Strict cookie.

[MEDIUM] Login error message differs for "no such user" vs "wrong password"
         → account-enumeration leak; return one generic error for both.

Layers run: static pattern review, OWASP Top 10 checklist.
Layers not run: Semgrep SAST, dependency audit — `/janef full security pass`
for full coverage.
```

The report format is real; the file and findings above are illustrative, not a
captured run.

---

## How these skills work

Each skill is a folder with a `SKILL.md` — the instructions Claude loads when the
skill triggers — plus `references/` files holding deeper, copyable detail that's
loaded only when needed. This keeps the always-on footprint small while giving
Claude real depth on demand (a pattern called *progressive disclosure*).

Every skill shares the same shape: **when to trigger**, **the method**, a
**severity-ranked output format**, and a **proof-before-done** step that requires
the fix be demonstrated — a real test or request/response — not merely asserted.

---

## Design principles

- **Defensive only.** No exploit code, no bypasses. These skills make systems
  harder to break, never easier.
- **The server is the only place trust lives.** Client-side checks are UX, not
  security.
- **Proof before done.** A fix isn't finished until it's demonstrated with
  evidence.
- **Readable findings.** Reviews are severity-ranked and actionable — every
  finding names the concrete fix, not just the problem.
- **They compose.** Design, auth, review, secrets, operations, and an overall
  quality bar reinforce each other.

---

## Compatibility

Written primarily for modern web stacks — **TypeScript, Node.js, Next.js**, and
similar — with patterns that transfer to other languages. The security principles
are stack-agnostic; the code examples are illustrative and meant to be adapted.

Claude Code is the primary and fully packaged host. Codex receives an
`agents/openai.yaml` interface for each skill. Other Agent Skills hosts can use
the portable `SKILL.md` directories, but behavioral parity is not claimed until
tested. See [compatibility](./docs/compatibility.md).

---

## Development

Run the complete local gate before proposing or publishing a change:

```bash
make check
```

See the [architecture](./docs/architecture.md), [compatibility matrix](./docs/compatibility.md),
and [release guide](./docs/releasing.md) for maintenance details.

---

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](./CONTRIBUTING.md).

Because these are security skills, contributions must stay **strictly
defensive**. Anything that facilitates unauthorized access, data exfiltration, or
attack will not be accepted. See [SECURITY.md](./SECURITY.md) for how to report a
concern.

---

## Built by a practitioner

janefskills comes out of real production work, not a classroom exercise.
[ALJANEF](https://github.com/AL-JANEF) is a solo founder building a portfolio of
AI-native ventures for Gulf markets, and wrote this suite to hold Claude to the
same evidence-before-done standard those systems are built under. More projects
on the [profile](https://github.com/AL-JANEF?tab=repositories).

---

## License

[MIT](./LICENSE) © 2026 ALJANEF

Free to use, modify, and distribute. If these skills help you ship safer
software, a star on the repo helps others find them.
