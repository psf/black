#!/usr/bin/env python3
"""Sync the security/release scaffolding from this repo into another repository.

Example:
    python scripts/sync_scaffolding.py ../Black --slug myorg/black --include-docs --force

The script copies CI workflows, config, scripts, packaging, and (optionally) docs
into the target repo, then replaces template placeholders like
`hollowsunhc/black` with your provided slug. Existing files are left intact
unless --force is supplied.
"""

from __future__ import annotations

import argparse
import shutil
import sys
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, Iterable, List, Set


# Paths (relative to the repository root) that contain the scaffolding.
DEFAULT_PATHS: List[str] = [
    ".github/workflows",
    "config",
    "scripts",
    "packaging",
]

# Optional docs to include when --include-docs is set.
DOC_PATHS: List[str] = [
    "docs/distribution",
    "docs/security",
    "docs/setup",
    "docs/README.md",
]

# Single files worth syncing for configuration hints.
SINGLE_FILES: List[str] = [
    ".env.example",
    ".env.minimal",
]

# Files/directories we never copy.
SKIP_NAMES = {
    ".git",
    "__pycache__",
    ".mypy_cache",
    ".pytest_cache",
    ".ruff_cache",
    ".nox",
    ".tox",
    "dist",
}


@dataclass
class SyncOptions:
    target: Path
    source_root: Path
    include_docs: bool
    dry_run: bool
    force: bool
    replacements: Dict[str, str]
    extra_paths: List[str]
    verbose: bool


def parse_args(repo_root: Path) -> SyncOptions:
    parser = argparse.ArgumentParser(
        description=(
            "Copy CI/security/packaging scaffolding from this repo into a target "
            "repository and update placeholders."
        )
    )
    parser.add_argument(
        "target",
        nargs="?",
        default="../Black",
        help="Path to the target repository (default: ../Black)",
    )
    parser.add_argument(
        "--slug",
        help="GitHub owner/repo to replace hollowsunhc/black (e.g., myorg/black)",
    )
    parser.add_argument(
        "--owner",
        help="GitHub owner to replace hollowsunhc (used if slug is not provided)",
    )
    parser.add_argument(
        "--repo",
        help="Repo name to replace black in repo-specific placeholders (optional)",
    )
    parser.add_argument(
        "--replace",
        action="append",
        default=[],
        metavar="OLD:NEW",
        help="Additional literal replacement (can be passed multiple times)",
    )
    parser.add_argument(
        "--include-docs",
        action="store_true",
        help="Copy selected docs (distribution/security/setup)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Show actions without writing files",
    )
    parser.add_argument(
        "--force",
        action="store_true",
        help="Overwrite files if they already exist in the target",
    )
    parser.add_argument(
        "--paths",
        nargs="+",
        default=None,
        help="Override the default list of paths to copy (relative to repo root)",
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Print all copy operations (not just a summary)",
    )
    args = parser.parse_args()

    paths = args.paths if args.paths is not None else list(DEFAULT_PATHS)
    if args.include_docs:
        paths += DOC_PATHS
    paths += SINGLE_FILES

    replacements: Dict[str, str] = {}
    if args.slug:
        replacements["hollowsunhc/black"] = args.slug
        if "/" in args.slug and not args.owner:
            replacements["hollowsunhc"] = args.slug.split("/", 1)[0]
    if args.owner and "hollowsunhc" not in replacements:
        replacements["hollowsunhc"] = args.owner
    # Repo name replacement is intentionally conservative; only apply if provided.
    if args.repo:
        replacements["black"] = args.repo

    for pair in args.replace:
        if ":" not in pair:
            parser.error(f"--replace expects OLD:NEW, got {pair!r}")
        old, new = pair.split(":", 1)
        if not old:
            parser.error("--replace requires a non-empty OLD value")
        replacements[old] = new

    target = (Path(args.target)).resolve()
    source_root = repo_root.resolve()
    return SyncOptions(
        target=target,
        source_root=source_root,
        include_docs=args.include_docs,
        dry_run=args.dry_run,
        force=args.force,
        replacements=replacements,
        extra_paths=paths,
        verbose=args.verbose,
    )


def should_skip(path: Path) -> bool:
    parts = set(path.parts)
    return bool(parts & SKIP_NAMES)


def is_text_file(path: Path) -> bool:
    try:
        data = path.read_bytes()
    except OSError:
        return False
    # Heuristic: if null byte present, assume binary.
    return b"\0" not in data


def apply_replacements(path: Path, replacements: Dict[str, str]) -> bool:
    if not replacements or not is_text_file(path):
        return False
    try:
        content = path.read_text(encoding="utf-8")
    except UnicodeDecodeError:
        return False

    original = content
    for old, new in replacements.items():
        if old in content:
            content = content.replace(old, new)

    if content != original:
        path.write_text(content, encoding="utf-8")
        return True
    return False


def copy_tree(
    source_root: Path,
    relative_path: str,
    target_root: Path,
    *,
    force: bool,
    dry_run: bool,
    replacements: Dict[str, str],
    verbose: bool,
) -> tuple[Set[Path], Set[Path], Set[Path]]:
    copied: Set[Path] = set()
    skipped: Set[Path] = set()
    replaced: Set[Path] = set()

    rel_path = Path(relative_path)
    src = source_root / rel_path
    if not src.exists():
        print(f"[skip] Missing source: {relative_path}")
        return copied, skipped, replaced

    if src.is_file():
        files = [src]
        base = src.parent
    else:
        files = [p for p in src.rglob("*") if p.is_file()]
        base = src

    for file in files:
        if should_skip(file):
            continue
        dest_base = target_root / rel_path
        if src.is_file():
            dest = dest_base
        else:
            dest = dest_base / file.relative_to(base)
        if dest.exists() and not force:
            skipped.add(dest)
            if verbose:
                print(f"[keep] {dest} (exists)")
            continue

        action = "[copy]" if not dest.exists() else "[over]"
        if verbose:
            print(f"{action} {dest}")
        copied.add(dest)
        if dry_run:
            continue

        dest.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(file, dest)
        if apply_replacements(dest, replacements):
            replaced.add(dest)

    return copied, skipped, replaced


def main() -> int:
    repo_root = Path(__file__).resolve().parents[1]
    opts = parse_args(repo_root)

    if not opts.target.exists():
        if opts.dry_run:
            print(f"[dry-run] Would create target directory {opts.target}")
        else:
            opts.target.mkdir(parents=True, exist_ok=True)

    copied_all: Set[Path] = set()
    skipped_all: Set[Path] = set()
    replaced_all: Set[Path] = set()

    for rel_path in opts.extra_paths:
        copied, skipped, replaced = copy_tree(
            opts.source_root,
            rel_path,
            opts.target,
            force=opts.force,
            dry_run=opts.dry_run,
            replacements=opts.replacements,
            verbose=opts.verbose,
        )
        copied_all |= copied
        skipped_all |= skipped
        replaced_all |= replaced

    print("\nSummary:")
    print(f"  Copied:   {len(copied_all)} file(s)")
    print(f"  Skipped:  {len(skipped_all)} existing file(s)")
    print(f"  Replaced: {len(replaced_all)} file(s) had placeholder substitutions")
    if opts.dry_run:
        print("  Mode:     dry-run (no files written)")
    if opts.replacements:
        print("  Replacements:")
        for old, new in opts.replacements.items():
            arrow = "->" if old != new else "(unchanged)"
            print(f"    {old} {arrow} {new}")
    else:
        print("  Replacements: none")

    if not opts.verbose:
        print("\nUse --verbose to list individual file operations.")
    print("Done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
