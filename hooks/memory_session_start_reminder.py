#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
SessionStart / PostCompact hook — injects the long-term memory system
instructions at the start of every session and after context compaction.

Replaces the need to manually append a snippet to the project's CLAUDE.md.
"""

import sys

MEMORY_INSTRUCTIONS = """\
# Long-Term Memory System

**Memory instructions (mandatory reading):** See the `claude-project-memory:memory` skill — defines how to record decisions, errors, and learnings in `memory/daily/*.md` during each session, and how `/claude-project-memory:memory-digest` promotes them to the Obsidian vault.

**Session log (mandatory):** In every session where decisions are made, files are modified, or non-trivial work is done:
1. **Create the file only when there is something significant to record** (not at session start, not blank). Path: `memory/daily/YYYY-MM-DD_HHMMSS.md` with the current timestamp.
2. When creating it, fill in `topic:` in the frontmatter and `## Context` with what the user requested and why — in the same step.
3. If a file for this session already exists, reuse it instead of creating a new one.
4. **Update the file immediately** whenever something significant happens — do not batch updates for the end of the session:
   - After making a technical decision → add to `## Decisions`.
   - After the user corrects an error → add to `## Errors and corrections` (quote the correction literally if possible).
   - When discovering something not documented in the vault → add to `## Learnings`.
   - When finishing, list touched files in `## References`.
5. Do not record: info already in `CLAUDE.md`/vault, ephemeral state, git history, secrets.

## Before non-trivial tasks

**Before implementing any non-trivial task** (features, architectural changes, schema modifications, ADR creation, questions about what exists in the project), invoke the `memory-search` sub-agent to retrieve all relevant documentation from the vault:

```
Agent(subagent_type: "memory-search", prompt: "<task description>")
```

Not necessary for: simple bug fixes without architectural impact, questions already answered in the current conversation context, trivial sessions without implementation work.\
"""


def main():
    print(f"<memory-session-instructions>\n{MEMORY_INSTRUCTIONS}\n</memory-session-instructions>")
    sys.exit(0)


if __name__ == "__main__":
    main()
