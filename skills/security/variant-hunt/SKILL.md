---
name: variant-hunt
description: >-
  After any vulnerability or bug is confirmed, sweep the entire codebase for
  every other instance of the same pattern with ripgrep and custom Semgrep
  rules so the whole class is fixed, not one case. Use right after finding or
  fixing a security issue, when checking a fix is complete, or to prove a past
  pattern is eradicated. Defensive only.
license: MIT
---

# Variant Hunt

The single most common failure in code security is fixing the bug you were shown
and missing its siblings. The developer who wrote an unsafe query at one place
wrote it the same way in six others — it's a habit, not an accident. A review that
fixes one and stops leaves the codebase almost as exposed as before.

This skill exists to make that failure impossible. Given one confirmed finding, it
sweeps the whole codebase for the same pattern and reports every instance, so the
*class* is eradicated, not just the instance.

## When to reach for this skill

The moment a vulnerability or bug is confirmed — by a scanner, a review, or an
incident. Also when verifying that a fix is complete ("did we get all of them?"),
or when someone needs proof that a known-bad pattern from a past incident no longer
exists anywhere. If you just found or fixed a security issue and haven't swept for
variants, you're not done — that's the trigger.

## The method

### 1. Characterize the pattern

Reduce the finding to its root shape — the thing that makes it dangerous,
stripped of the specifics of this one location. Examples:
- "user input concatenated into a SQL string"
- "an object fetched by id with no ownership/tenant check"
- "a secret compared with `==` instead of a constant-time function"
- "a user-supplied URL fetched server-side without allowlisting"

The sharper the characterization, the better the hunt. Name the **sink** (the
dangerous operation) and the **source** (untrusted input) where relevant.

### 2. First sweep — fast text search (ripgrep)

Cast a wide net cheaply. ripgrep (`rg`) is fast and everywhere:
```bash
# examples — adapt the pattern to the finding
rg -n "query\(.*\$\{" --type ts          # template-literal SQL sinks
rg -n "==.*token|token.*==" --type js    # non-constant-time token compares
rg -n "fetch\((req|request)\." -t ts     # server-side fetch of request data
```
This over-matches on purpose — it's a candidate list, not a verdict. Read each hit
to confirm or dismiss.

### 3. Structural sweep — custom Semgrep rule

Text search misses structural variants (reformatted, renamed, split across lines).
A small Semgrep rule matches the *shape* regardless of formatting. Write a rule for
the sink and run it:
```yaml
# variant.yml — example: object fetched by id without an ownership check nearby
rules:
  - id: idor-fetch-without-ownership
    languages: [typescript]
    message: object fetched by id — verify an ownership/tenant check guards it
    severity: WARNING
    patterns:
      - pattern: $REPO.findUnique({ where: { id: $ID } })
```
```bash
semgrep scan --config variant.yml
```
See `references/hunt-patterns.md` for ready-to-adapt rules for the common classes
(injection, IDOR, weak compare, SSRF, unsafe upload). Writing a targeted rule per
finding is the professional move — it encodes *your* codebase's dangerous pattern
so it can be re-run forever.

### 4. Deep sweep — interprocedural (when the pattern crosses functions)

When the danger flows across functions/files (input enters here, reaches a sink
there), plain pattern matching isn't enough. CodeQL is the professional tool for
interprocedural taint tracking; if it's available, use it. If not, trace the call
paths explicitly and clearly flag any path you could not fully verify — an honest
"unverified path" is worth more than a false "clean."

### 5. Report the whole class

Group every instance under the original finding:
```
### Finding: <pattern> (originally at <location>)
Variants found (same pattern, same risk):
- <file:line> — <one-line context>
- <file:line> — ...
Searched by: ripgrep + Semgrep rule <id>  [+ CodeQL if run]
Result: <N> total instances — fix all, or justify any left.
```

If the sweep genuinely finds no siblings, say so explicitly: "searched via rg +
Semgrep, no other instances." Silence is not an acceptable result — the reader must
know the hunt happened.

## Proof before done

The hunt itself is the evidence: name the tools run and the patterns used, so the
search is reproducible. For eradication, a re-run of the same Semgrep rule
returning zero matches after fixes is the proof the class is closed. Keep the rule
in the repo so the pattern can never silently return.

## Composes with the suite

This skill is the natural follow-up to `vuln-audit` (which finds the first
instance) and is a required layer of the `security-audit` full pass.
Whatever finds the bug, this is what makes sure it was the last one of its kind.

## References
- `references/hunt-patterns.md` — Ready-to-adapt ripgrep and Semgrep patterns for
  the common vulnerability classes, plus guidance on writing a good rule fast.
