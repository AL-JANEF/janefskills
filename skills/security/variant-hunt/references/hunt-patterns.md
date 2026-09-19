# Hunt Patterns

Ready-to-adapt search patterns for the common vulnerability classes. For each: a
fast ripgrep sweep (candidate list) and a Semgrep rule sketch (structural match).
Adapt the specifics to the actual stack and finding.

A note on method: ripgrep casts wide and cheap — expect false positives, read each
hit. Semgrep matches structure — fewer false positives, survives reformatting.
Write the Semgrep rule for anything you'll want to re-check later; keep it in the
repo so the pattern can't silently return.

---

## SQL / query injection

**ripgrep — template literals and concatenation into queries:**
```bash
rg -n 'query\(.*(\$\{|\+ )' -t ts -t js
rg -n '(execute|raw)\(.*(\$\{|\+ )' -t ts -t js -t py
```
**Semgrep sketch:**
```yaml
rules:
  - id: sql-string-built-from-input
    languages: [typescript, javascript]
    message: query built from interpolated/concatenated input — parameterize
    severity: ERROR
    patterns:
      - pattern-either:
          - pattern: $DB.query(`...${$X}...`)
          - pattern: $DB.query("..." + $X)
```

## IDOR / missing ownership check

**ripgrep — objects fetched by id (candidates to verify a check guards):**
```bash
rg -n 'findUnique\(\{ where: \{ id' -t ts
rg -n 'findById|getById|\.get\(req\.(params|query)' -t ts -t js
```
**Semgrep sketch:**
```yaml
rules:
  - id: fetch-by-id-check-ownership
    languages: [typescript]
    message: object fetched by id — confirm ownership/tenant scoping guards it
    severity: WARNING
    pattern: $REPO.findUnique({ where: { id: $ID } })
```
This intentionally flags all by-id fetches for human confirmation — the danger is
the *absence* of a nearby check, which is hard to match positively.

## Non-constant-time secret comparison (timing leak)

**ripgrep — secrets compared with normal equality:**
```bash
rg -n '(token|secret|hash|signature|apiKey|password)\s*===?' -t ts -t js
rg -n '(hmac|digest|token)\s*==' -t py
```
**The fix to mandate:** `crypto.timingSafeEqual` (Node), `hmac.compare_digest`
(Python). Any secret compared with `==`/`===`/`.equals()` is a candidate leak.

## SSRF — server-side fetch of user input

**ripgrep:**
```bash
rg -n '(fetch|axios|request|http\.get)\(.*req\.' -t ts -t js
rg -n 'requests\.(get|post)\(.*request\.' -t py
```
**Semgrep sketch:**
```yaml
rules:
  - id: ssrf-user-controlled-fetch
    languages: [typescript, javascript]
    message: server-side fetch of user-controlled URL — allowlist + block private IPs
    severity: ERROR
    pattern: fetch($REQ.$FIELD)
```

## Unsafe file upload

**ripgrep:**
```bash
rg -n '(originalname|mimetype)' -t ts -t js          # trusting client-supplied name/type
rg -n 'save\(.*(public|uploads)' -t ts -t js         # storing in web-served path
```
Verify: content validated by inspection (not extension), server-generated filename,
stored outside web root, size-capped.

## XSS — unescaped output

**ripgrep:**
```bash
rg -n 'innerHTML|dangerouslySetInnerHTML|v-html' -t ts -t js -t jsx -t vue
rg -n '\|\s*safe|mark_safe|\|raw' -t html -t py            # template escaping disabled
```

---

## Writing a good rule fast

1. Take the confirmed finding. Identify the **sink** — the dangerous call.
2. Write the smallest Semgrep `pattern` that matches that sink shape.
3. Run it: `semgrep scan --config yourrule.yml`. Too many hits → tighten with
   `patterns:` + `pattern-inside:`/`metavariable-pattern`. Too few → loosen or add
   a `pattern-either`.
4. Confirm it matches the known instance, then trust it for the sweep.
5. Commit the rule to the repo. Now the pattern is guarded forever, and a future
   re-run proving zero matches is your eradication evidence.

The goal isn't a perfect rule — it's a rule good enough to surface every plausible
sibling for human confirmation. Precision can improve over time; coverage matters
first.
