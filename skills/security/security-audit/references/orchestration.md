# Orchestration Reference

Exact commands and procedure for the `/janef full security pass`. This is what
turns janef from an LLM-only reviewer into a coordinator of real tooling. Read it
before running the full pass.

## The three automated tools

All three are free, run locally, and work on Windows/macOS/Linux. None sends code
anywhere by default.

### 1. Semgrep — static analysis (SAST)

Scans every code path for known-dangerous patterns across 30+ languages. This is
the layer that catches what reading skips.

**Install:**
- pipx (recommended): `pipx install semgrep`
- pip: `pip install semgrep`
- Docker: `docker pull semgrep/semgrep`
- macOS: `brew install semgrep`

**Run (from the repo root):**
```bash
# Broad first pass, machine-readable, non-zero exit on findings
semgrep scan --config auto --json --output semgrep.json --error

# Security-focused packs (more signal for appsec)
semgrep scan --config p/security-audit --config p/owasp-top-ten --config p/secrets

# PR/diff mode — only new code vs. main (fast, for gating)
semgrep scan --config auto --baseline-commit=$(git merge-base HEAD origin/main) --error
```
Start with `--config auto` (tuned, less noise). Broader packs like
`p/security-audit` find more but are noisier — introduce after tuning.

**Reading output:** each finding has a rule id, file:line, severity
(ERROR/WARNING/INFO), and a message. Treat ERROR as candidate High/Critical,
verify by reading the actual code before ranking — Semgrep is precise but not
infallible; justify any dismissal.

### 2. Gitleaks — secret scanning

Catches exposed credentials in the working tree **and full git history** — the
latter is impossible to find reliably by reading. It's a Go binary, not an npm
package.

**Install:**
- Windows: download the release binary from github.com/gitleaks/gitleaks, or
  `winget install gitleaks`
- macOS: `brew install gitleaks`
- Docker: `docker pull zricethezav/gitleaks`

**Run:**
```bash
# Scan the working directory (uncommitted + current files)
gitleaks detect --no-git --source . -v

# Scan the full commit history (finds secrets committed then "removed")
gitleaks detect --source . -v

# Machine-readable
gitleaks detect --source . --report-format json --report-path gitleaks.json
```
Any hit is treated as **Critical** and — critically — as **requiring rotation**,
not just deletion. A secret in history is compromised even after removal (see the
`secrets-guard` skill's leak-response reference).

### 3. Dependency audit — known-vulnerable libraries

Catches CVEs in the dependency tree. Use what matches the stack:
```bash
npm audit --json           # npm
pnpm audit --json          # pnpm
yarn npm audit             # yarn berry
pip-audit                  # Python (pip install pip-audit)
```
Rank by severity AND reachability: a critical CVE in a dependency you never call
is lower priority than a medium one in your request path. Note that distinction in
the report rather than blindly echoing the tool's severity.

## The full-pass procedure

1. **Detect the stack** — read package.json / lockfiles / config to know which
   commands apply. Don't run npm audit on a Python repo.

2. **Run Layer 1 (automated), capture evidence.** Run Semgrep, Gitleaks, and the
   dependency audit. Save their output. For each tool that isn't installed, record
   it as **NOT RUN** with the one-line install command — never imply a layer ran
   when it didn't.

3. **Run Layer 2 (LLM expert review).** Apply the specialists in order:
   threat-model → secrets-guard → auth-hardening → vuln-audit → security-logging →
   engineering-standard. Reason about logic, auth, tenant isolation, design —
   what scanners can't see.

4. **Run Layer 3 (reconcile).** For every scanner finding, read the code and
   confirm or dismiss (with justification). Elevate findings two layers agree on.
   List explicitly what nothing here covered.

5. **Consolidate** into the single report in SKILL.md, with the "Layers run" table
   and the honest coverage/verdict section.

## Handling "tool not installed"

If none of the scanners are installed, the pass degrades to LLM-only review — say
so plainly at the top of the report:

> "Automated layers (Semgrep/Gitleaks/dependency audit) were NOT run — not
> installed. This was an LLM-only review: one layer of three. Install the tools
> below and re-run for real multi-layer coverage."

Then give the install one-liners. Never let an LLM-only pass masquerade as a full
one — that false confidence is the exact failure this command exists to prevent.

## What this pass still does NOT cover

State these in every report so the boundary is visible:
- **Runtime/DAST** — attacking the live running app (OWASP ZAP, Burp).
- **Load/performance** under stress, timing side-channels.
- **Human penetration testing** — a skilled human adversary. Irreplaceable before
  a high-stakes or government launch.
- **Formal verification** — mathematical proof of correctness.

`/janef` makes the static and review layers exhaustive and honest. The dynamic and
human layers are a deliberate, stated gap — not a silent one.
