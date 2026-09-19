# Claude Code adapter

Primary host. Two install paths:

1. **Plugin / marketplace** — `.claude-plugin/plugin.json` lists every capability directory under `skills/`; `.claude-plugin/marketplace.json` makes the repository its own one-plugin marketplace. Namespace stays `janefskills`, so `/janefskills:forge` (and the deprecated `/janefskills:janef`) work.
2. **Personal skills** — `python3 scripts/install.py install --target claude` copies capability directories into `$CLAUDE_CONFIG_DIR/skills/<id>/` with a managed-file marker so `doctor` and `uninstall` only touch files Forge owns.

`CLAUDE.md.fragment` is the compact always-on policy block for `$CLAUDE_CONFIG_DIR/CLAUDE.md`; `python3 scripts/install.py policy --target claude` merges it between markers and backs up the previous file. The contract text inside the fragment is generated from `core/protocol/contract.md` by `forge sync`; validation fails if it drifts.
