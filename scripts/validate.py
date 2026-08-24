#!/usr/bin/env python3
"""Validate janefskills packaging, metadata, links, and suite invariants."""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
SKILL_NAME = re.compile(r"^[a-z0-9]+(?:-[a-z0-9]+)*$")
MARKDOWN_LINK = re.compile(r"\[[^\]]+\]\(([^)]+)\)")


def load_json(path: Path, errors: list[str]) -> dict:
    try:
        payload = json.loads(path.read_text(encoding="utf-8"))
    except FileNotFoundError:
        errors.append(f"missing JSON file: {path.relative_to(ROOT)}")
        return {}
    except json.JSONDecodeError as exc:
        errors.append(f"invalid JSON in {path.relative_to(ROOT)}: {exc}")
        return {}
    if not isinstance(payload, dict):
        errors.append(f"JSON root must be an object: {path.relative_to(ROOT)}")
        return {}
    return payload


def parse_frontmatter(path: Path, errors: list[str]) -> dict[str, str]:
    try:
        lines = path.read_text(encoding="utf-8").splitlines()
    except FileNotFoundError:
        errors.append(f"missing file: {path.relative_to(ROOT)}")
        return {}
    if not lines or lines[0] != "---":
        errors.append(f"missing YAML frontmatter: {path.relative_to(ROOT)}")
        return {}
    try:
        end = lines.index("---", 1)
    except ValueError:
        errors.append(f"unterminated YAML frontmatter: {path.relative_to(ROOT)}")
        return {}

    result: dict[str, str] = {}
    index = 1
    while index < end:
        match = re.match(r"^([A-Za-z0-9_-]+):(?:\s*(.*))?$", lines[index])
        if not match:
            index += 1
            continue
        key, value = match.group(1), (match.group(2) or "").strip()
        if value in {">", ">-", "|", "|-"}:
            block: list[str] = []
            index += 1
            while index < end and (not lines[index] or lines[index][0].isspace()):
                block.append(lines[index].strip())
                index += 1
            result[key] = " ".join(part for part in block if part)
            continue
        result[key] = value.strip('"\'')
        index += 1
    return result


def validate_skills(skills: tuple[str, ...], errors: list[str]) -> None:
    for skill in skills:
        if not SKILL_NAME.fullmatch(skill):
            errors.append(f"invalid skill name: {skill}")
            continue
        directory = ROOT / skill
        skill_file = directory / "SKILL.md"
        metadata = parse_frontmatter(skill_file, errors)
        if metadata.get("name") != skill:
            errors.append(f"{skill}/SKILL.md name must match its directory")
        if len(metadata.get("description", "")) < 40:
            errors.append(f"{skill}/SKILL.md needs a discriminating description")
        if metadata.get("license") != "MIT":
            errors.append(f"{skill}/SKILL.md must declare license: MIT")
        if skill_file.exists() and len(skill_file.read_text(encoding="utf-8").splitlines()) > 500:
            errors.append(f"{skill}/SKILL.md exceeds the 500-line project limit")

        body = skill_file.read_text(encoding="utf-8") if skill_file.exists() else ""
        references = sorted((directory / "references").glob("*.md"))
        for reference in references:
            relative = f"references/{reference.name}"
            if relative not in body:
                errors.append(f"unlinked reference: {skill}/{relative}")

        openai_yaml = directory / "agents" / "openai.yaml"
        if not openai_yaml.is_file():
            errors.append(f"missing Codex metadata: {skill}/agents/openai.yaml")
        else:
            yaml_text = openai_yaml.read_text(encoding="utf-8")
            prompt_match = re.search(r'^\s*default_prompt:\s*"([^"]+)"\s*$', yaml_text, re.M)
            short_match = re.search(r'^\s*short_description:\s*"([^"]+)"\s*$', yaml_text, re.M)
            if not prompt_match or f"${skill}" not in prompt_match.group(1):
                errors.append(f"{skill}/agents/openai.yaml prompt must mention ${skill}")
            if not short_match or not 25 <= len(short_match.group(1)) <= 64:
                errors.append(
                    f"{skill}/agents/openai.yaml short_description must be 25-64 characters"
                )


def validate_packaging(skills: tuple[str, ...], version: str, errors: list[str]) -> None:
    plugin = load_json(ROOT / ".claude-plugin" / "plugin.json", errors)
    marketplace = load_json(ROOT / ".claude-plugin" / "marketplace.json", errors)
    expected_paths = [f"./{skill}" for skill in skills]
    if plugin.get("name") != "janefskills":
        errors.append("plugin name must be janefskills")
    if plugin.get("version") != version:
        errors.append("plugin version must match config/skills.json")
    if plugin.get("skills") != expected_paths:
        errors.append("plugin skills must match config/skills.json in order")

    entries = marketplace.get("plugins")
    if not isinstance(entries, list) or len(entries) != 1:
        errors.append("marketplace must contain exactly one janefskills plugin")
    else:
        entry = entries[0]
        if not isinstance(entry, dict) or entry.get("name") != "janefskills":
            errors.append("marketplace plugin name must be janefskills")
        elif entry.get("version") != version:
            errors.append("marketplace version must match config/skills.json")


def validate_links(errors: list[str]) -> None:
    for document in ROOT.rglob("*.md"):
        if ".git" in document.parts:
            continue
        text = document.read_text(encoding="utf-8")
        for raw_target in MARKDOWN_LINK.findall(text):
            target = raw_target.strip().strip("<>").split("#", 1)[0]
            if not target or re.match(r"^[a-z][a-z0-9+.-]*:", target, re.I):
                continue
            resolved = (document.parent / target).resolve()
            try:
                resolved.relative_to(ROOT)
            except ValueError:
                errors.append(
                    f"link escapes repository: {document.relative_to(ROOT)} -> {raw_target}"
                )
                continue
            if not resolved.exists():
                errors.append(
                    f"broken link: {document.relative_to(ROOT)} -> {raw_target}"
                )


def validate_suite(skills: tuple[str, ...], errors: list[str]) -> None:
    readme = (ROOT / "README.md").read_text(encoding="utf-8")
    orchestrator = (ROOT / "janef" / "SKILL.md").read_text(encoding="utf-8")
    for skill in skills:
        if skill not in readme:
            errors.append(f"README does not mention skill: {skill}")
        if skill != "janef" and f"`{skill}`" not in orchestrator:
            errors.append(f"janef orchestrator does not route to: {skill}")


def validate() -> list[str]:
    errors: list[str] = []
    manifest = load_json(ROOT / "config" / "skills.json", errors)
    raw_skills = manifest.get("skills")
    version = manifest.get("version")
    if not isinstance(raw_skills, list) or not all(isinstance(item, str) for item in raw_skills):
        errors.append("config/skills.json must declare a string skills list")
        return errors
    if len(raw_skills) != len(set(raw_skills)):
        errors.append("config/skills.json contains duplicate skills")
    if not isinstance(version, str) or not re.fullmatch(r"\d+\.\d+\.\d+", version):
        errors.append("config/skills.json version must use semantic versioning")
        version = ""
    skills = tuple(raw_skills)
    validate_skills(skills, errors)
    validate_packaging(skills, version, errors)
    validate_links(errors)
    validate_suite(skills, errors)
    return errors


def main() -> int:
    errors = validate()
    if errors:
        print("janefskills validation: FAIL")
        for error in errors:
            print(f"- {error}")
        return 1
    print("janefskills validation: PASS")
    print("8 skills, Claude plugin, marketplace, Codex metadata, and links verified.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
