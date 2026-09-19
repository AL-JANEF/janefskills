# Contributing to JANEF Forge

Thanks for helping make coding agents more disciplined. Please read this before opening a pull request.

## Ground rules

- **Defensive only.** Security capabilities harden, audit, and verify. Anything that facilitates unauthorized access, exfiltration, or attack is rejected.
- **One contract.** Shared invariants live in `core/protocol/contract.md` only. Do not restate them inside skills; link to the capability that owns the detail instead.
- **Evidence.** A PR that changes behavior includes the command you ran and its result.

## Adding or changing a capability

1. Create or edit `skills/<domain>/<id>/SKILL.md` and `capability.json`. The frontmatter `name` must equal the directory name and the `description` must equal the manifest description verbatim.
2. Declare unique `triggers` and `responsibilities`; the registry rejects duplicates across capabilities. Use `negative_triggers` to prevent known false activations.
3. Declare `requires` only for hard dependencies that must always load together. Use `optional_with` for advisory relationships. Conflicts must be declared on both sides.
4. Put deep, copyable detail in `references/` and list each file in the manifest and in the body.
5. Add at least one case to `evals/routing_corpus.json` that exercises the new or changed trigger, including a negative or adversarial case when relevant.
6. Run `python3 scripts/quality_gate.py`. It must pass; if a budget in `config/budgets.json` needs to change, say why in the PR.

## Changing the contract, a profile, or routing rules

These are architecture changes. Update `docs/architecture/JANEF_FORGE_ARCHITECTURE.md`, run `python3 scripts/forge.py sync` after editing the contract, and expect a request for a second reviewer.

## Tooling

Standard library only. A new dependency needs a measured benefit, an owner, and an update policy; open an issue first.

## Commit and PR conventions

Conventional commit types (`feat`, `fix`, `refactor`, `docs`, `test`, `chore`, `ci`). Work on a branch; do not force-push shared branches. PR descriptions summarize the whole range, name the tests run, and list anything intentionally left out.

## Reporting a security concern

See [SECURITY.md](./SECURITY.md). Do not open a public issue for a security concern.
