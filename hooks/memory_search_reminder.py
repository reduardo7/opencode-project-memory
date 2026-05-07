#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
UserPromptSubmit hook — injects a reminder to invoke the memory-search
sub-agent before executing non-trivial tasks.

Text printed to stdout is injected as additional context in the prompt
before Claude processes it (Claude Code hooks behavior).
"""

import sys


def main():
    reminder = (
        "<memory-search-reminder>"
        "Before executing the task, invoke the `claude-project-memory:memory-search` sub-agent to retrieve "
        "relevant documentation from the vault if the task is non-trivial "
        "(feature implementation, architectural changes, schema modifications, "
        "ADR creation/updates, questions about what exists in the project). "
        "Skip this step for trivial sessions (simple questions without implementation)."
        "</memory-search-reminder>"
    )
    print(reminder)
    sys.exit(0)


if __name__ == "__main__":
    main()
