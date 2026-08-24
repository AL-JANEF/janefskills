# Compatibility

| Host | Status | Installation | Notes |
|---|---|---|---|
| Claude Code | Primary | Marketplace, `--plugin-dir`, or personal installer | Plugin namespace is `janefskills` |
| Codex | Supported metadata | Personal installer | Each skill includes `agents/openai.yaml`; newly installed skills load on the next task |
| Other Agent Skills hosts | Portable structure | Copy selected skill directories | Confirm the host's frontmatter and invocation behavior |

## Claude Code

The repository follows Claude Code's plugin layout without relocating legacy
skill paths. `.claude-plugin/plugin.json` lists every root skill explicitly, and
`.claude-plugin/marketplace.json` lets the GitHub repository act as a one-plugin
marketplace.

Validate the package with:

```bash
claude plugin validate .
```

## Codex

Codex-specific UI metadata is intentionally kept inside each skill. It does not
change Claude Code behavior. Install all skills with:

```bash
python3 scripts/install.py --target codex
```

## Compatibility policy

Primary support means packaging and automated validation are present. Portable
means the folder structure is expected to work, but the project does not claim
behavioral parity without a host-specific test.
