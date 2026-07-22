"""Verify that development-only tooling is absent from built distributions."""

from __future__ import annotations

import argparse
import tarfile
import zipfile
from pathlib import Path


def _inspect_member(name: str, content: bytes) -> list[str]:
    errors: list[str] = []
    normalized = name.replace("\\", "/")
    lower = normalized.lower()
    if lower.startswith("niltest/") or "/niltest/" in lower or lower.endswith("/niltest.py"):
        errors.append(f"bundled niltest module: {name}")
    if lower.endswith(".dist-info/metadata") or lower.endswith("/pkg-info"):
        metadata = content.decode("utf-8", errors="replace").lower()
        if any(line.startswith("requires-dist: niltest") for line in metadata.splitlines()):
            errors.append(f"niltest runtime dependency in {name}")
    is_production_source = lower.startswith("nanasqlite/") or "/src/nanasqlite/" in lower
    if is_production_source and lower.endswith(".py"):
        source = content.decode("utf-8", errors="replace")
        if "import niltest" in source or "from niltest" in source:
            errors.append(f"production niltest import in {name}")
    return errors


def verify_archive(path: Path) -> list[str]:
    errors: list[str] = []
    if path.suffix == ".whl":
        with zipfile.ZipFile(path) as archive:
            for name in archive.namelist():
                if not name.endswith("/"):
                    errors.extend(_inspect_member(name, archive.read(name)))
    elif path.name.endswith(".tar.gz"):
        with tarfile.open(path, "r:gz") as archive:
            for member in archive.getmembers():
                if member.isfile():
                    extracted = archive.extractfile(member)
                    if extracted is not None:
                        errors.extend(_inspect_member(member.name, extracted.read()))
    else:
        errors.append(f"unsupported distribution format: {path}")
    return errors


def main() -> int:
    parser = argparse.ArgumentParser()
    parser.add_argument("dist", nargs="+", type=Path)
    args = parser.parse_args()
    errors = [error for path in args.dist for error in verify_archive(path)]
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    print(f"Verified {len(args.dist)} distribution artifact(s): niltest is development-only")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
