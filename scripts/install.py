#!/usr/bin/env python3
"""Install janefskills without silently overwriting an existing installation."""

from __future__ import annotations

import argparse
import json
import os
import shutil
import sys
import tempfile
from datetime import datetime, timezone
from pathlib import Path
from typing import Iterable


class InstallError(RuntimeError):
    """Raised when installation cannot complete safely."""


def project_root() -> Path:
    return Path(__file__).resolve().parents[1]


def load_skill_names(source_root: Path) -> tuple[str, ...]:
    manifest = source_root / "config" / "skills.json"
    try:
        payload = json.loads(manifest.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError) as exc:
        raise InstallError(f"cannot read skill manifest: {manifest}: {exc}") from exc

    skills = payload.get("skills")
    if not isinstance(skills, list) or not skills or not all(
        isinstance(item, str) and item for item in skills
    ):
        raise InstallError("config/skills.json must contain a non-empty skills list")
    if len(skills) != len(set(skills)):
        raise InstallError("config/skills.json contains duplicate skill names")
    return tuple(skills)


def default_root(target: str) -> Path:
    home = Path.home()
    if target == "claude":
        return Path(os.environ.get("CLAUDE_CONFIG_DIR", home / ".claude")) / "skills"
    if target == "codex":
        return Path(os.environ.get("CODEX_HOME", home / ".codex")) / "skills"
    raise InstallError(f"unsupported target: {target}")


def resolve_targets(target: str, destination: Path | None) -> tuple[tuple[str, Path], ...]:
    if destination is not None and not destination.is_absolute():
        raise InstallError("--dest must be an absolute path")
    if destination is not None and target == "both":
        raise InstallError("--dest cannot be combined with --target both")

    names = ("claude", "codex") if target == "both" else (target,)
    return tuple((name, destination or default_root(name)) for name in names)


def choose_skills(all_skills: tuple[str, ...], requested: Iterable[str]) -> tuple[str, ...]:
    selected = tuple(requested)
    if not selected:
        return all_skills
    unknown = sorted(set(selected) - set(all_skills))
    if unknown:
        raise InstallError(f"unknown skill(s): {', '.join(unknown)}")
    if len(selected) != len(set(selected)):
        raise InstallError("the same skill was selected more than once")
    return selected


def backup_path(destination: Path, stamp: str) -> Path:
    candidate = destination.with_name(f"{destination.name}.backup.{stamp}")
    counter = 1
    while candidate.exists():
        candidate = destination.with_name(
            f"{destination.name}.backup.{stamp}.{counter}"
        )
        counter += 1
    return candidate


def remove_path(path: Path) -> None:
    if path.is_symlink() or path.is_file():
        path.unlink()
    elif path.is_dir():
        shutil.rmtree(path)


def install(
    source_root: Path,
    targets: tuple[tuple[str, Path], ...],
    skills: tuple[str, ...],
    *,
    force: bool,
    dry_run: bool,
) -> list[tuple[str, Path, Path | None]]:
    """Install selected skills and return (target, destination, backup) records."""

    source_root = source_root.resolve()
    for skill in skills:
        source = source_root / skill
        if not (source / "SKILL.md").is_file():
            raise InstallError(f"invalid skill source: {source}")

    plans = [
        (target_name, root.expanduser().resolve(), skill)
        for target_name, root in targets
        for skill in skills
    ]
    conflicts = [root / skill for _, root, skill in plans if (root / skill).exists()]
    if conflicts and not force:
        joined = "\n  - ".join(str(path) for path in conflicts)
        raise InstallError(
            "existing installation(s) found; use --force to preserve and replace:\n"
            f"  - {joined}"
        )

    if dry_run:
        for target_name, root, skill in plans:
            destination = root / skill
            action = "backup and replace" if destination.exists() else "install"
            print(f"DRY RUN [{target_name}] {action}: {destination}")
        return []

    stamp = datetime.now(timezone.utc).strftime("%Y%m%dT%H%M%SZ")
    completed: list[tuple[str, Path, Path | None]] = []

    with tempfile.TemporaryDirectory(prefix="janefskills-install-") as temp_dir:
        stage_root = Path(temp_dir)
        for target_name, _, skill in plans:
            staged = stage_root / target_name / skill
            staged.parent.mkdir(parents=True, exist_ok=True)
            shutil.copytree(source_root / skill, staged)

        try:
            for target_name, root, skill in plans:
                root.mkdir(parents=True, exist_ok=True)
                destination = root / skill
                backup = None
                if destination.exists():
                    backup = backup_path(destination, stamp)
                    shutil.move(str(destination), str(backup))
                completed.append((target_name, destination, backup))
                shutil.move(str(stage_root / target_name / skill), str(destination))
                if not (destination / "SKILL.md").is_file():
                    raise InstallError(
                        f"post-install verification failed: {destination}"
                    )
        except Exception as exc:
            for _, destination, backup in reversed(completed):
                remove_path(destination)
                if backup is not None and backup.exists():
                    shutil.move(str(backup), str(destination))
            raise InstallError(f"installation failed and was rolled back: {exc}") from exc
    return completed


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Install janefskills for Claude Code, Codex, or both."
    )
    parser.add_argument(
        "--target",
        choices=("claude", "codex", "both"),
        default="claude",
        help="installation host (default: claude)",
    )
    parser.add_argument(
        "--dest",
        type=Path,
        help="custom absolute skills directory; unavailable with --target both",
    )
    parser.add_argument(
        "--only",
        nargs="+",
        metavar="SKILL",
        default=(),
        help="install only the named skills (default: all)",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="preserve existing skills as timestamped backups, then replace them",
    )
    parser.add_argument(
        "--dry-run", action="store_true", help="show the plan without writing files"
    )
    return parser


def main(argv: list[str] | None = None) -> int:
    parser = build_parser()
    args = parser.parse_args(argv)
    try:
        source_root = project_root()
        all_skills = load_skill_names(source_root)
        skills = choose_skills(all_skills, args.only)
        targets = resolve_targets(args.target, args.dest)
        completed = install(
            source_root,
            targets,
            skills,
            force=args.force,
            dry_run=args.dry_run,
        )
    except InstallError as exc:
        print(f"ERROR: {exc}", file=sys.stderr)
        return 1

    for target_name, destination, backup in completed:
        print(f"Installed [{target_name}] {destination}")
        if backup is not None:
            print(f"Preserved previous install: {backup}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
