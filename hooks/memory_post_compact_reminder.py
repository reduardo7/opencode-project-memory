#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
PostCompact hook — injects a reminder to re-read base vault documents after
context compaction, restoring the architectural context that was in the
compacted conversation history.

Lists the specific documents Claude should read to rebuild working context:
vault index, memory instructions, ADR registry, and any active session log.
"""

import glob
import os
import sys


def main():
    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    daily_dir = os.path.join(project_dir, "memory", "daily") if project_dir else ""

    existing_logs = []
    if daily_dir:
        existing_logs = sorted(
            [f for f in glob.glob(os.path.join(daily_dir, "*.md"))
             if not f.endswith(".gitkeep")]
        )

    base_docs = [
        "docs/vault/Home.md",
    ]

    docs_list = "\n".join(f"  - {d}" for d in base_docs)

    if existing_logs:
        latest_log = os.path.relpath(existing_logs[-1], project_dir) if project_dir else existing_logs[-1]
        log_line = f"\n  - {latest_log}  ← active session"
    else:
        log_line = ""

    reminder = (
        "<memory-post-compact-reminder>"
        "Context was just compacted. Restore the architectural context of the session:\n"
        "  1. Invoke the `claude-project-memory:memory` skill to reload the memory system instructions.\n"
        f"  2. Read the base documents:\n{docs_list}{log_line}\n"
        "These documents contain decisions, conventions, and project state "
        "that are not in the compacted history."
        "</memory-post-compact-reminder>"
    )

    print(reminder)
    sys.exit(0)


if __name__ == "__main__":
    main()
