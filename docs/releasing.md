# Releasing

Forge does not publish from CI. A release is prepared locally, verified, and published by a maintainer. Nothing below is executed for 2.0.0 until the release checklist is signed off.

## Release checklist

1. Version is `2.0.0` in `core/__init__.py`, every `capability.json`, `.claude-plugin/plugin.json`, and `.claude-plugin/marketplace.json` (`forge validate` enforces this).
2. `CHANGELOG.md` has an ISO-dated entry for the version.
3. `python3 scripts/quality_gate.py --json dist/quality-gate.json` passes on the exact release commit, with no required step failed and every optional step either passed or explicitly SKIPPED.
4. `claude plugin validate .` passes (part of the gate when the CLI is installed).
5. `gitleaks dir .` and `gitleaks git .` pass (the former is part of the gate when installed).
6. CI is green on the release commit.
7. `python3 scripts/package_release.py --evidence dist/quality-gate.json` produces `dist/janef-forge-<version>.tar.gz`, `.zip`, `SHA256SUMS`, and `release-evidence.json`. Rebuild once and confirm `SHA256SUMS` is byte-identical (reproducibility).
8. Review the diff since the previous tag for offensive content, secrets, broken references, and silent capability removals (compare against `docs/architecture/CONVERGENCE_MATRIX.md`).
9. Tag the exact validated commit `v<version>` and publish a GitHub Release with the archives, `SHA256SUMS`, `release-evidence.json`, and the changelog entry. **Not done for 2.0.0 in the consolidation PR.**

## Versioning

- **Patch**: wording or correctness fixes that preserve capability ids, paths, and routing behavior.
- **Minor**: additive capability, profile, adapter, or tooling; alias additions.
- **Major**: capability rename or removal, contract change, routing contract change, alias removal.

Never reuse or move a published tag.

## Release evidence

`release-evidence.json` records product, version, commit, `SOURCE_DATE_EPOCH`, per-file SHA-256, archive SHA-256, the embedded quality-gate report, and `"published": false` until the maintainer flips it in the release notes. It is the artifact a consumer can use to verify that the archive they downloaded is the one the gate validated.
