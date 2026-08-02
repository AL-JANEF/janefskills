# GitHub Repository Setup

Copy-paste values for setting up the public repository. Not part of the skills —
just a helper for publishing.

## Repository name
```
janefskills
```

## Description (the "About" field, ~120 chars)
```
Defensive security & production-grade engineering skills for Claude Code — auth, OWASP audit, threat modeling, secrets, logging.
```

## Topics (add these in the About → ⚙ → Topics field, for discoverability)
```
claude-code
claude
anthropic
agent-skills
security
appsec
owasp
authentication
threat-modeling
devsecops
secure-coding
skills
```

## Suggested first-release steps

1. Create the repo on GitHub as **public**, name `janefskills`, no auto-README
   (this repo already has one).
2. From inside the unzipped `janefskills/` folder:
   ```bash
   git init
   git add .
   git commit -m "feat: janefskills 1.0.0 — 6 skills for secure, production-grade engineering"
   git branch -M main
   git remote add origin https://github.com/AL-JANEF/janefskills.git
   git push -u origin main
   ```
3. In the repo's **About** panel, paste the description and add the topics above.
4. Optionally cut a release tagged `v1.0.0` (Releases → Draft a new release),
   using the `CHANGELOG.md` entry as the notes.

## Recommended before going public

Try the skills on a real project first. Start a task in a skill's area
(e.g. "review the login flow for security") and confirm the right skill engages.
If a skill doesn't trigger when expected, tighten the `description` in its
`SKILL.md` — the description is what decides activation.
