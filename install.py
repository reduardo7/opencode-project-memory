#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Bootstrap script — creates the required directories and copies all
claude-project-memory files into the target project.

Usage:
    uv run install.py /path/to/target-project
    python install.py /path/to/target-project

Existing vault files are never overwritten so project customizations are
preserved across re-runs.
"""

import shutil
import sys
from pathlib import Path


def copy_if_missing(src: Path, dst: Path) -> None:
    if dst.exists():
        print(f"  SKIP (exists): {dst}")
    else:
        shutil.copy2(src, dst)
        print(f"  CREATED: {dst}")


def main() -> None:
    if len(sys.argv) < 2:
        print("Usage: uv run install.py /path/to/target-project")
        sys.exit(1)

    plugin_dir = Path(__file__).resolve().parent
    target = Path(sys.argv[1]).resolve()

    if not target.is_dir():
        print(f"Error: target directory '{target}' does not exist")
        sys.exit(1)

    print(f"Installing claude-project-memory into: {target}")
    print()

    # Create directories
    for sub in [
        "memory/daily",
        "docs/vault/Claude",
        "docs/vault/Decisions",
        "docs/vault/Architecture",
        "docs/vault/Development",
        "docs/vault/Project",
        ".claude/commands",
        "specs"
    ]:
        (target / sub).mkdir(parents=True, exist_ok=True)

    # Create memory directory structure
    print("→ Creating memory/")
    (target / "memory/daily/.gitkeep").touch()

    # Create specs directory with .gitkeep
    print("→ Creating specs/")
    (target / "specs/.gitkeep").touch()

    # Copy vault templates (skip existing files)
    print("→ Copying docs/vault/ (skipping existing files)")
    for f in [
        "docs/vault/Home.md",
        "docs/vault/Claude/Memory.md",
        "docs/vault/Architecture/Database.md",
        "docs/vault/Architecture/Project Structure.md",
        "docs/vault/Decisions/Index.md",
        "docs/vault/Development/Obsidian Vault.md",
        "docs/vault/Development/Expected Behaviors.md",
    ]:
        copy_if_missing(plugin_dir / f, target / f)

    print()
    print("Installation complete.")
    print()
    print("Next steps:")
    print("  1. Customize docs/vault/Home.md for your project")
    print()
    print("See README.md for full details.")


if __name__ == "__main__":
    main()
