# Architecture

janefskills keeps its runtime surface small and its distribution surfaces
additive. The eight existing skill directories remain the source of truth.

## Layers

1. **Discovery** — each directory exposes a precise `SKILL.md` description.
2. **Progressive disclosure** — detailed methods stay under that skill's
   `references/` directory and load only when relevant.
3. **Orchestration** — `janef` routes focused tasks or coordinates the complete
   defensive review without copying the specialists' instructions.
4. **Host metadata** — `.claude-plugin/` packages the suite for Claude Code;
   each `agents/openai.yaml` describes the same skill to Codex.
5. **Quality controls** — `config/skills.json` is the canonical inventory used
   by the installer, validator, tests, and release process.

## Compatibility invariant

Do not move or rename the eight root skill directories without a documented
migration. Personal installations and the Claude plugin both consume those same
directories, so existing users keep working while newer hosts gain metadata.

## Security boundary

The repository contains instructions and deterministic packaging utilities. It
does not install scanners, execute third-party code, send source code to a
service, or grant itself access. Skills may recommend tools, but actual installs
and external actions remain subject to the user's authorization and environment.
