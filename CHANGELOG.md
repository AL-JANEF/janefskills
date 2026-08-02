# Changelog

All notable changes to janefskills are documented here. The format follows
[Keep a Changelog](https://keepachangelog.com/), and the project aims to follow
[Semantic Versioning](https://semver.org/).

## [1.1.0] — 2026

### Added
- **`variant-hunt`** — after any finding, sweeps the whole codebase for every
  other instance of the same pattern (ripgrep + custom Semgrep rules), so the class
  is eradicated, not just the reported case.
- **`janef` upgraded to an audit-grade orchestrator** — now combines real
  automated tooling (Semgrep SAST, Gitleaks, dependency audit) with LLM expert
  review, professional audit methodology (variant analysis, fix verification,
  constant-time/timing review), and an honest coverage verdict. Also serves as the
  suite's technical reference index.

## [1.0.0] — 2026

Initial public release.

### Added
- **`janef`** — single entry point / router for the whole suite; `/janef <task>`
  routes to the right specialist or runs a coordinated full security pass.
- **`engineering-standard`** — strict production-grade engineering bar: truth
  policy, forbidden-patterns list, red-team review, and a lint/typecheck/test/
  build completion gate requiring evidence.
- **`threat-model`** — STRIDE threat-modeling pass for the design stage, with a
  worked multi-tenant example.
- **`auth-hardening`** — authentication and session hardening: login, logout,
  password storage, tokens, and brute-force protection, with copyable session
  patterns.
- **`vuln-audit`** — OWASP Top 10 code audit (injection, XSS, CSRF, SSRF, IDOR,
  unsafe upload, misconfiguration) with before/after remediations.
- **`secrets-guard`** — secrets hygiene across code, git history, logs, and client
  bundles, with prevention setup and leak-response procedure.
- **`security-logging`** — audit logging and suspicious-activity detection without
  leaking sensitive data, with copyable patterns.
- Repository scaffolding: README, LICENSE (MIT), CONTRIBUTING, SECURITY,
  banner, and per-skill `references/`.
