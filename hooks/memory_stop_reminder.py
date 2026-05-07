#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
Stop hook — injects a reminder to record decisions, errors, and learnings
in memory/daily/ before ending the session.

If a session file already exists in memory/daily/, the reminder asks to
update it. If none exists, detects git changes to determine whether the
session was non-trivial — in that case the reminder is imperative.

The JSON printed to stdout is injected as systemMessage at the end of
the response (Claude Code Stop hook behavior).
"""

import glob
import json
import os
import subprocess
import sys


def is_git_available() -> bool:
    try:
        subprocess.run(["git", "--version"], capture_output=True, timeout=3)
        return True
    except Exception:
        return False


def is_git_repo(project_dir: str) -> bool:
    try:
        result = subprocess.run(
            ["git", "rev-parse", "--is-inside-work-tree"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=3,
        )
        return result.returncode == 0
    except Exception:
        return False


def has_git_changes(project_dir: str) -> bool:
    """Detects changes in the worktree (staged, unstaged, or untracked)."""
    try:
        result = subprocess.run(
            ["git", "status", "--porcelain"],
            cwd=project_dir,
            capture_output=True,
            text=True,
            timeout=5,
        )
        return bool(result.stdout.strip())
    except Exception:
        return False


def main():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR")
    if not project_dir:
        message = (
            "<memory-stop-reminder>"
            "MANDATORY if there was non-trivial work: create memory/daily/YYYY-MM-DD_HHMMSS.md "
            "with topic, Context, Decisions, Errors and corrections, Learnings, References."
            "</memory-stop-reminder>"
        )
        print(json.dumps({"systemMessage": message}))
        sys.exit(0)

    daily_dir = os.path.join(project_dir, "memory", "daily")
    pattern = os.path.join(daily_dir, "*.md")
    existing_files = [f for f in glob.glob(pattern) if not f.endswith(".gitkeep")]

    if existing_files:
        message = (
            "<memory-stop-reminder>"
            "There is an active session file in memory/daily/. "
            "Update the relevant sections now: "
            "Decisions, Errors and corrections, Learnings, References."
            "</memory-stop-reminder>"
        )
    else:
        git_changed = (
            is_git_available()
            and is_git_repo(project_dir)
            and has_git_changes(project_dir)
        )
        if git_changed:
            message = (
                "<memory-stop-reminder>"
                "WARNING: files were modified in this session but memory/daily/ does NOT exist. "
                "Create NOW memory/daily/YYYY-MM-DD_HHMMSS.md with topic, Context, "
                "Decisions, Errors and corrections, Learnings, and References. "
                "Do not skip — mandatory when there was non-trivial work."
                "</memory-stop-reminder>"
            )
        else:
            message = (
                "<memory-stop-reminder>"
                "If there were decisions, errors, or learnings in this session (even if no "
                "files were modified), create memory/daily/YYYY-MM-DD_HHMMSS.md as per the claude-project-memory:memory skill."
                "</memory-stop-reminder>"
            )

    print(json.dumps({"systemMessage": message}))
    sys.exit(0)


if __name__ == "__main__":
    main()
