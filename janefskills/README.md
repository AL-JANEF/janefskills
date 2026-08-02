<p align="center">
  <img src="./assets/banner.svg" alt="janefskills — eight defensive security and engineering skills for Claude Code" width="100%">
</p>

<p align="center">
  <img src="https://img.shields.io/badge/license-MIT-D4AF61" alt="MIT License">
  <img src="https://img.shields.io/badge/skills-8-16273F" alt="8 skills">
  <img src="https://img.shields.io/badge/scope-defensive%20only-0E1A2B" alt="Defensive only">
  <img src="https://img.shields.io/badge/methodology-audit--grade-1A2E4A" alt="Audit-grade methodology">
  <img src="https://img.shields.io/badge/for-Claude%20Code-9DB0C8" alt="For Claude Code">
</p>

<h1 align="center">janefskills</h1>

<p align="center">
  <strong>Eight defensive-security and engineering skills that give Claude the instincts of a security-minded staff engineer.</strong><br>
  Built for <a href="https://docs.claude.com/en/docs/claude-code">Claude Code</a> and any agent supporting the <a href="https://docs.claude.com">Agent Skills</a> format.
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
/janef review the login flow      → routes to auth-hardening
/janef audit this file            → routes to vuln-audit
/janef full security pass         → runs all layers, one consolidated report
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
                         │            /janef             │  ← one command,
                         │   orchestrates + references   │    routes to any skill
                         └───────────────────────────────┘
                                       │
   ┌─────────── DESIGN ───────────┬─────── BUILD ───────┬──────── AUDIT ─────────┐
   │                              │                     │                        │
   ▼                              ▼                     ▼                        ▼
threat-model            auth-hardening          vuln-audit  ──►  variant-hunt
(risks, pre-code)       secrets-guard           (find the bug)   (find its siblings)
                                                security-logging
   │                              │                     │                        │
   └──────────────────────────────┴─────────────────────┴────────────────────────┘
                                       │
                                       ▼
                          ┌───────────────────────────┐
                          │    engineering-standard   │  ← the bar under all of it:
                          │   truth · evidence · gate │    proof before "done"
                          └───────────────────────────┘
```

`threat-model` names the risks before code exists; `auth-hardening` and
`secrets-guard` build the front door safely; `vuln-audit` finds bugs and
`variant-hunt` eradicates every sibling of each one; `security-logging` covers the
operational edge; `engineering-standard` holds all of it to an evidence-based bar;
and `/janef` ties them together into a single command and reference.

---

## Install

### Claude Code

```bash
git clone https://github.com/AL-JANEF/janefskills.git
```

Copy the skills you want into your Claude Code skills directory.

**macOS / Linux:**
```bash
cp -r janefskills/janef \
      janefskills/engineering-standard \
      janefskills/threat-model \
      janefskills/auth-hardening \
      janefskills/vuln-audit \
      janefskills/variant-hunt \
      janefskills/secrets-guard \
      janefskills/security-logging \
      ~/.claude/skills/
```

**Windows (PowerShell):**
```powershell
Copy-Item -Recurse janefskills\janef                $env:USERPROFILE\.claude\skills\
Copy-Item -Recurse janefskills\engineering-standard $env:USERPROFILE\.claude\skills\
Copy-Item -Recurse janefskills\threat-model         $env:USERPROFILE\.claude\skills\
Copy-Item -Recurse janefskills\auth-hardening       $env:USERPROFILE\.claude\skills\
Copy-Item -Recurse janefskills\vuln-audit           $env:USERPROFILE\.claude\skills\
Copy-Item -Recurse janefskills\variant-hunt         $env:USERPROFILE\.claude\skills\
Copy-Item -Recurse janefskills\secrets-guard        $env:USERPROFILE\.claude\skills\
Copy-Item -Recurse janefskills\security-logging     $env:USERPROFILE\.claude\skills\
```

> **Note:** Claude Code reads skills from `~/.claude/skills` (the `.claude`
> folder), **not** `~/.agents/skills`. Verify with `ls ~/.claude/skills`
> (or `dir $env:USERPROFILE\.claude\skills` on Windows).

Restart Claude Code. The skills appear automatically and trigger on relevant
tasks — you don't call them by name. To confirm a skill is active, start a task in
its area (e.g. "review the login flow for security") and watch it engage.

---

## Usage

You don't invoke these skills manually — they trigger on what you're doing. Some
examples of prompts that engage them:

- *"Review this authentication code before I ship it."* → `auth-hardening` +
  `vuln-audit`
- *"I'm designing a multi-tenant billing API — what could go wrong?"* →
  `threat-model`
- *"Is it safe to commit this config?"* → `secrets-guard`
- *"Add an audit trail for admin actions."* → `security-logging`
- *"Implement this feature to production quality."* → `engineering-standard`

Each produces a severity-ranked report or an implementation with evidence — and
holds itself to proving claims rather than asserting them.

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

Requires [Claude Code](https://docs.claude.com/en/docs/claude-code) or another
agent supporting the Agent Skills (`SKILL.md`) format.

---

## Contributing

Issues and pull requests are welcome — see [CONTRIBUTING.md](./CONTRIBUTING.md).

Because these are security skills, contributions must stay **strictly
defensive**. Anything that facilitates unauthorized access, data exfiltration, or
attack will not be accepted. See [SECURITY.md](./SECURITY.md) for how to report a
concern.

---

## License

[MIT](./LICENSE) © 2026 aljanef

Free to use, modify, and distribute. If these skills help you ship safer
software, a star on the repo helps others find them.
