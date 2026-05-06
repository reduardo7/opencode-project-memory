# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Overview

This is a **Claude Code plugin** — not a software package with a build step. It provides a drop-in long-term memory system for Claude Code projects: raw session notes are recorded during work and later distilled into a curated Obsidian vault via the `/memory-digest` command.

It can be installed as a Claude plugin (recommended) or manually via `install.py`.

## Installation

### Plugin (recommended)

```
/plugin install github.com/reduardo7/claude-project-memory
```

After installing the plugin, run `install.py` to set up the vault/memory directory structure in the target project, then complete the post-install steps below.

### Manual

```bash
uv run install.py /path/to/target-project
```

The script copies memory system files (commands, agents, rules, hooks, vault templates) into the target project. It skips existing vault files to avoid overwriting customizations.

**Post-install steps (both options):**

1. Customize `docs/vault/Home.md` for the target project
2. Update the skills table in `.claude/agents/memory-digest-daily.md`

**Runtime requirements:** Python 3.11+, `uv` (for hooks execution).

## Architecture

The system has three activation layers that must all be present in the target project:

1. **CLAUDE.md snippet** — loaded every session, ensures memory instructions apply everywhere
2. **Claude Rules** (`.claude/rules/`) — context-specific instructions fired when touching memory/vault files
3. **Hooks** (`.claude/hooks/`) — real-time Python reminders triggered by Claude Code events

### Core Data Flow

```
Work session → memory/daily/YYYY-MM-DD_HHMMSS.md   (raw log)
                       ↓ /memory-digest
              docs/vault/**/*.md                     (curated knowledge)
                       ↓ memory-search agent
              Retrieved context before any implementation
```

### Key Components

| Path                                    | Role                                                                        |
| --------------------------------------- | --------------------------------------------------------------------------- |
| `.claude-plugin/plugin.json`            | Plugin manifest — enables `/plugin install`                                 |
| `skills/memory-digest/SKILL.md`         | `/memory-digest` slash command in plugin format                             |
| `.claude-plugin/marketplace.json`       | Plugin marketplace registration                                             |
| `memory/memory.md`                      | Operating instructions for what/when to record                              |
| `.claude/commands/memory-digest.md`     | `/memory-digest` slash command (legacy format, kept for manual install)     |
| `.claude/agents/memory-digest-daily.md` | Sub-agent: distills one daily log → vault (uses Sonnet)                     |
| `.claude/agents/memory-digest-spec.md`  | Sub-agent: distills one spec → vault (uses Sonnet)                          |
| `.claude/agents/memory-search.md`       | Sub-agent: retrieves vault docs before tasks (uses Haiku)                   |
| `docs/vault/Home.md`                    | Vault master index — customize per target project                           |
| `docs/vault/Decisions/Index.md`         | ADR registry with next ADR number                                           |
| `specs/digested.txt`                    | Registry of already-processed spec files                                    |
| `install.py`                            | Bootstrap script — creates directories and copies files into target project |

### Hooks

**When adding or modifying hooks, update:**

- `.claude-plugin/plugin.json` — used when installed via `/plugin install` (paths use `${CLAUDE_PLUGIN_ROOT}`)

Seven Python hooks fire on Claude Code events:

- `memory_session_start_reminder.py` — `SessionStart` + `PostCompact`: injects the memory system instructions at session start and after compaction (replaces the need to append a snippet to `CLAUDE.md`)
- `memory_search_reminder.py` — `UserPromptSubmit`: suggests invoking `memory-search` before non-trivial tasks
- `memory_log_reminder.py` — `UserPromptSubmit`: reads the prompt; if non-trivial, reminds Claude to create/update the daily log **before** responding (not after)
- `memory_pre_agent_reminder.py` — `PreToolUse[Agent]`: reminds sub-agents to consult vault (skips memory system agents)
- `memory_stop_reminder.py` — `Stop`: reminds Claude to update the daily log before ending the session
- `memory_pre_compact_reminder.py` — `PreCompact`: reminds Claude to persist the daily log **before** context compaction discards conversation history
- `memory_post_compact_reminder.py` — `PostCompact`: reminds Claude to re-read base vault documents after compaction to restore architectural context

### `/memory-digest` Pipeline

Processes files **sequentially** (not in parallel) to avoid write conflicts in shared vault documents like `Decisions/Index.md`:

1. Find all `memory/daily/*.md` → run `memory-digest-daily` for each → delete on success
2. Find all `specs/*.md` not in `specs/digested.txt` → run `memory-digest-spec` for each → append to `digested.txt` on success
3. Commit all vault changes to git

### Vault Conventions

- **Wikilinks required**: `[[Section/Document]]` full-path format; never bare filenames
- **Bidirectional links**: every new doc must link to and be linked from related docs
- **No duplicates**: sub-agents `Grep` before writing; always update existing docs
- **Language consistency**: detect existing vault language and maintain it
- **Specs are immutable**: never modified or deleted after creation
