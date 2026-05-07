#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
SessionStart / PostCompact hook — injects the long-term memory system
operational context at the start of every session and after context compaction.

Reads skills/memory/context.md from the plugin root dynamically so any update
to that file is automatically picked up without modifying this hook.
"""

import os
import sys


def main():
    plugin_root = os.environ.get("CLAUDE_PLUGIN_ROOT", "")
    context_path = os.path.join(plugin_root, "skills", "memory", "context.md") if plugin_root else ""

    if context_path and os.path.exists(context_path):
        with open(context_path, "r", encoding="utf-8") as f:
            content = f.read().strip()
    else:
        content = (
            "Memory system context not found. "
            "Read `skills/memory/context.md` and invoke the `claude-project-memory:memory` skill."
        )

    print(f"<memory-session-instructions>\n{content}\n</memory-session-instructions>")
    sys.exit(0)


if __name__ == "__main__":
    main()
