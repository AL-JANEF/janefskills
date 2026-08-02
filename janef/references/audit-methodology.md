# Audit Methodology

The professional techniques that lift a review from "read the code" to "audit the
code." Adapted from established security-audit practice (the kind used by
dedicated security firms). Read this during a full pass, after findings exist.

Three techniques, each targeting a failure mode of ordinary review.

---

## 1. Variant analysis — one finding is never one

**The failure it fixes:** an ordinary review finds a SQL injection at `users.ts:40`,
fixes it, and moves on. But the developer who wrote it wrote the same pattern in
eight other places. The audit fixed one bug; seven remain.

**The method:** every time a finding is *confirmed*, treat it as a *pattern to
hunt*, not an incident to close. For that finding:

1. Characterize the shape — what's the root pattern? (e.g. "user input
   concatenated into a query string", "object fetched by id without an ownership
   check", "comparison of a secret with `==`").
2. Search the whole codebase for that shape. Use the tools, not just reading:
   - `grep`/ripgrep for the literal pattern as a first sweep.
   - A targeted Semgrep rule for structural matches — this is where Semgrep shines.
     Write a small rule matching the sink and run `semgrep scan --config <rule.yml>`.
   - For deep interprocedural cases (input flows across functions/files), note that
     CodeQL is the professional tool; if available, use it, otherwise reason
     through the call paths explicitly and flag the ones you couldn't verify.
3. Report every instance found, grouped under the original finding as "variants."

**Rule of thumb:** if you found it once and didn't look for siblings, the audit
isn't done. The report must say, per finding, either the variants found or
"searched, none found" — never silence.

---

## 2. Fix verification — a fix is a change, and changes get reviewed

**The failure it fixes:** a fix is applied, everyone assumes it worked, and either
(a) it didn't actually close the hole, or (b) it introduced a new bug. Both are
common; both are caught by verifying rather than assuming.

**The method:** for every fix made in the session, prove two things:

1. **It closes the finding.** Demonstrate the original attack path no longer works.
   - For an IDOR fix: the request for another user's object now returns 403/404 —
     shown, not asserted.
   - For an injection fix: the malicious input is now handled harmlessly — shown.
   - Ideally a regression test that *fails on the old code and passes on the new*.
     That test failing-then-passing IS the proof.
2. **It introduces nothing new.** Re-review the fix as its own change: does it break
   behavior, add a new code path, weaken something else? Run the gate
   (lint/typecheck/tests/build) after the fix, and re-run the relevant scanner on
   the changed files.

A fix without verification is a hope. State, per fix: what proved it closed, and
what proved it regressed nothing.

---

## 3. Timing & constant-time review — the class reading can't see

**The failure it fixes:** two pieces of code look identical and both "work," but one
leaks information through *how long it takes to respond*. A login that returns
faster for a wrong username than a wrong password reveals which usernames exist. A
token check that bails on the first wrong byte reveals the token one byte at a time.
No amount of reading the logic reveals this — it's in the execution, not the text.

**Where to look:** any comparison of a secret or security-sensitive value —
password checks, token/HMAC/signature verification, API-key comparison, coupon or
reset-code checks.

**The method:**
1. Flag every secret comparison. Is it using a normal `==` / `===` / `.equals()`?
   That's usually short-circuiting and therefore timing-variable.
2. Require a **constant-time comparison** for secrets:
   - Node: `crypto.timingSafeEqual(a, b)`
   - Python: `hmac.compare_digest(a, b)`
   - and equivalents. These take the same time regardless of where the difference
     is, closing the side channel.
3. Flag early-return authentication logic that branches on secret-derived values
   before a uniform response is produced.
4. Note honestly: *detecting* a real timing leak in production requires measurement
   under load (the dynamic layer), not just code review. This step finds the
   code-level smell and mandates the constant-time fix; it does not replace runtime
   timing tests. Say so.

---

## How these fit the pass

Run these in Layer 3 of the full pass, after Layer 1 (scanners) and Layer 2 (expert
review) have produced findings:

- Take each confirmed finding → **variant analysis** → expand it to all its siblings.
- Review every secret comparison in the code → **timing review** → mandate
  constant-time where missing.
- For anything fixed during the session → **fix verification** → prove closed +
  no regression.

These three are what a senior auditor does that a first-pass reviewer doesn't. They
are also honest about their own edges — variant analysis is only as deep as the
tools run, and timing review finds the smell but defers the measurement to the
dynamic layer. That honesty is part of the rigor, not a weakness in it.
