#!/usr/bin/env python3
"""Build reproducible release archives with SHA-256 sums and a release-evidence record.

Deterministic: fixed file order, normalized mtimes (SOURCE_DATE_EPOCH or the commit
time), uid/gid 0, no platform metadata. Two builds of the same commit produce
byte-identical archives. Does not tag or publish anything.
"""

from __future__ import annotations

import argparse
import hashlib
import io
import json
import os
import subprocess
import sys
import tarfile
import zipfile
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from core import VERSION  # noqa: E402

NAME = f"janef-forge-{VERSION}"
INCLUDE = ("skills", "core", "profiles", "adapters", "schemas", "scripts", "config", "docs", ".claude-plugin",
           "LICENSE", "NOTICE.md", "README.md", "CHANGELOG.md", "SECURITY.md", "CONTRIBUTING.md", "Makefile")
EXCLUDE_PARTS = {"__pycache__", ".DS_Store"}


def release_files() -> list[Path]:
    files: list[Path] = []
    for entry in INCLUDE:
        path = ROOT / entry
        if path.is_file():
            files.append(path)
        elif path.is_dir():
            files.extend(p for p in path.rglob("*") if p.is_file() and not (EXCLUDE_PARTS & set(p.parts)))
    for path in files:
        if path.is_symlink():
            raise SystemExit(f"refusing to package symlink: {path}")
    return sorted(files, key=lambda p: p.relative_to(ROOT).as_posix())


def source_epoch() -> int:
    if os.environ.get("SOURCE_DATE_EPOCH"):
        return int(os.environ["SOURCE_DATE_EPOCH"])
    try:
        return int(subprocess.check_output(["git", "log", "-1", "--format=%ct"], cwd=ROOT, text=True).strip())
    except (subprocess.CalledProcessError, OSError, ValueError):
        return 0


def git_sha() -> str:
    try:
        return subprocess.check_output(["git", "rev-parse", "HEAD"], cwd=ROOT, text=True).strip()
    except (subprocess.CalledProcessError, OSError):
        return "unknown"


def build_tar(files: list[Path], epoch: int) -> bytes:
    buffer = io.BytesIO()
    with tarfile.open(fileobj=buffer, mode="w:gz", compresslevel=9, format=tarfile.PAX_FORMAT) as tar:
        for path in files:
            info = tar.gettarinfo(str(path), arcname=f"{NAME}/{path.relative_to(ROOT).as_posix()}")
            info.uid = info.gid = 0
            info.uname = info.gname = ""
            info.mtime = epoch
            info.mode = 0o755 if path.stat().st_mode & 0o100 else 0o644
            info.pax_headers = {}
            with path.open("rb") as handle:
                tar.addfile(info, handle)
    data = buffer.getvalue()
    # gzip header stores a timestamp at bytes 4..8; normalize it for reproducibility
    return data[:4] + (0).to_bytes(4, "little") + data[8:]


def build_zip(files: list[Path], epoch: int) -> bytes:
    stamp = datetime.fromtimestamp(max(epoch, 315532800), tz=timezone.utc).timetuple()[:6]
    buffer = io.BytesIO()
    with zipfile.ZipFile(buffer, "w", zipfile.ZIP_DEFLATED, compresslevel=9) as archive:
        for path in files:
            info = zipfile.ZipInfo(f"{NAME}/{path.relative_to(ROOT).as_posix()}", date_time=stamp)
            info.compress_type = zipfile.ZIP_DEFLATED
            info.external_attr = (0o755 if path.stat().st_mode & 0o100 else 0o644) << 16
            archive.writestr(info, path.read_bytes())
    return buffer.getvalue()


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def build(out_dir: Path, evidence: dict | None = None) -> dict:
    files = release_files()
    epoch = source_epoch()
    tar_bytes = build_tar(files, epoch)
    zip_bytes = build_zip(files, epoch)
    out_dir.mkdir(parents=True, exist_ok=True)
    (out_dir / f"{NAME}.tar.gz").write_bytes(tar_bytes)
    (out_dir / f"{NAME}.zip").write_bytes(zip_bytes)
    sums = {f"{NAME}.tar.gz": sha256(tar_bytes), f"{NAME}.zip": sha256(zip_bytes)}
    (out_dir / "SHA256SUMS").write_text("".join(f"{digest}  {name}\n" for name, digest in sums.items()), encoding="utf-8")
    record = {
        "product": "JANEF Forge",
        "version": VERSION,
        "commit": git_sha(),
        "source_date_epoch": epoch,
        "file_count": len(files),
        "artifacts": sums,
        "file_hashes": {p.relative_to(ROOT).as_posix(): sha256(p.read_bytes()) for p in files},
        "quality_gate": evidence,
        "published": False,
    }
    (out_dir / "release-evidence.json").write_text(json.dumps(record, indent=2, sort_keys=True) + "\n", encoding="utf-8")
    return record


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--out", type=Path, default=ROOT / "dist")
    parser.add_argument("--evidence", type=Path, help="quality gate JSON report to embed")
    args = parser.parse_args(argv)
    evidence = json.loads(args.evidence.read_text(encoding="utf-8")) if args.evidence else None
    record = build(args.out, evidence)
    print(f"built {NAME} ({record['file_count']} files) in {args.out}")
    for name, digest in record["artifacts"].items():
        print(f"  {digest}  {name}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
