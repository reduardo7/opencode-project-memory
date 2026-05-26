#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
PreToolUse hook (matcher: Agent) — injects a reminder before launching
any sub-agent to ensure it consults vault documentation before working.

Text printed to stdout is injected as additional context before Claude
executes the tool call (Claude Code PreToolUse hook behavior).

Does not apply to memory system agents — they already have their own
defined flow and do not need the reminder.
"""

import json
import sys


def main():
    try:
        input_data = json.loads(sys.stdin.read())
        tool_input = input_data.get("tool_input", {})
        subagent_type = tool_input.get("subagent_type", "")

        reminder = (
            "<pre-agent-reminder>"
            "Before the sub-agent starts working, ensure its prompt includes relevant "
            "documentation context. If you haven't yet consulted the claude-project-memory:search "
            "skill (`Skill(skill: \"claude-project-memory:search\", args: \"<task>\")`) "
            "for this task, consider doing so first and then passing the "
            "retrieved documentation as context in the sub-agent's prompt."
            "</pre-agent-reminder>"
        )
        print(reminder)
        sys.exit(0)

    except Exception:
        sys.exit(0)


if __name__ == "__main__":
    main()
