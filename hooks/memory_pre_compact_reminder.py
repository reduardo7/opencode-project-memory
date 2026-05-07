#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
PreCompact hook — injects a reminder to persist session memory before the
context window is compacted and prior conversation details are lost.

If an active daily log exists, asks Claude to update it now. If no log
exists but git changes are present, asks Claude to create one. The
compaction will discard unsaved context, so this reminder fires before
that happens.
"""

import glob
import json
import os
import subprocess
import sys


def has_git_changes(project_dir: str) -> bool:
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
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    daily_dir = os.path.join(project_dir, "memory", "daily") if project_dir else ""

    existing = []
    if daily_dir:
        existing = [f for f in glob.glob(os.path.join(daily_dir, "*.md"))
                    if not f.endswith(".gitkeep")]

    if existing:
        message = (
            "<memory-pre-compact-reminder>"
            "BEFORE COMPACTION: update memory/daily/ now with everything relevant "
            "from this session — Decisions, Errors and corrections, Learnings, References. "
            "Compaction will discard the conversation history; anything not in the "
            "session file will be permanently lost."
            "</memory-pre-compact-reminder>"
        )
    elif project_dir and has_git_changes(project_dir):
        message = (
            "<memory-pre-compact-reminder>"
            "BEFORE COMPACTION: files were modified in this session but memory/daily/ does not exist. "
            "Create NOW memory/daily/YYYY-MM-DD_HHMMSS.md with topic, "
            "Context, Decisions, Errors and corrections, Learnings, and References. "
            "Compaction will discard the history — save before it is lost."
            "</memory-pre-compact-reminder>"
        )
    else:
        message = (
            "<memory-pre-compact-reminder>"
            "BEFORE COMPACTION: if there were decisions, errors, or learnings in this session, "
            "create memory/daily/YYYY-MM-DD_HHMMSS.md now (see the claude-project-memory:memory skill for the format). "
            "Compaction will discard the conversation history."
            "</memory-pre-compact-reminder>"
        )

    print(json.dumps({"systemMessage": message}))
    sys.exit(0)


if __name__ == "__main__":
    main()
