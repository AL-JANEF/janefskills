# Codex adapter

Codex loads skills from `$CODEX_HOME/skills/<id>/SKILL.md` and reads optional UI metadata from `agents/openai.yaml` inside each skill directory.

JANEF Forge keeps skill content host-agnostic: no `openai.yaml` is stored in `skills/`. The installer renders one per capability at install time from `capability.json` plus `interface.json` in this directory (`python3 scripts/install.py install --target codex`).

`AGENTS.md.fragment` is the compact policy block for `$CODEX_HOME/AGENTS.md`; `python3 scripts/install.py policy --target codex` merges it between markers and backs up the previous file. The contract text inside the fragment is generated from `core/protocol/contract.md` by `forge sync`.

Status: structure verified (installer tests render and validate the metadata); behavioral parity with Claude Code is not claimed until a Codex smoke run is recorded in `docs/compatibility.md`.
