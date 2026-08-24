## Outcome

Describe the user-visible improvement and the skill or packaging area affected.

## Safety boundary

- [ ] The change is defensive only.
- [ ] Examples do not provide working exploits, bypasses, or live secrets.
- [ ] Existing skills and references remain available unless a documented migration is included.

## Verification

- [ ] `python scripts/validate.py`
- [ ] `python -m unittest discover -s tests -p "test_*.py" -v`
- [ ] Relevant skill behavior was exercised with a realistic request.

## Compatibility

Note any Claude Code, Codex, filesystem, or installation behavior that changed.
