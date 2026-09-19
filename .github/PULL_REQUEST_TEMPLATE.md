## Outcome

Describe the user-visible improvement and the capability, profile, routing, or packaging area affected.

## Safety boundary

- [ ] The change is defensive only.
- [ ] Examples do not provide working exploits, bypasses, or live secrets.
- [ ] Existing capabilities and references remain available, or a documented migration and alias are included.
- [ ] No verification floor, security control, or CI gate was weakened.

## Verification

- [ ] `python3 scripts/quality_gate.py` passes (paste the summary line)
- [ ] New or changed triggers have a case in `evals/routing_corpus.json`
- [ ] Relevant capability behavior was exercised with a realistic request

## Compatibility

Note any Claude Code, Codex, installer, alias, or budget behavior that changed.
