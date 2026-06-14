# AGENTS.md

This file provides guidance to OpenCode (and compatible agents) when working with code in this repository.

## Overview

This is an **OpenCode plugin** — not a software package with a build step. It provides a drop-in long-term memory system for OpenCode projects: raw session notes are recorded during work and later distilled into a curated Obsidian vault via the `/digest` command.

It can be installed globally (copy `.opencode/` into `~/.config/opencode/`) or per-project via `install.mjs`.

## Installation

### Per-project (recommended)

```bash
node install.mjs /path/to/target-project
```

The script copies the plugin tooling (`.opencode/plugin`, `command`, `agent`, `skills`) into the target project and scaffolds the data directories (`memory/`, `specs/`) and the vault (`docs/vault/`). Tooling files are overwritten on re-install so updates propagate; existing vault files are never overwritten so project customizations are preserved.

### Global

Copy this repo's `.opencode/` contents into `~/.config/opencode/` so the plugin, agents, commands, and skills are available in every project. Then run `/install` (or `node install.mjs <dir>`) inside each project to scaffold its `memory/`, `specs/`, and vault.

**Post-install steps:**

1. Customize `docs/vault/Home.md` for the target project.
2. Commit `.opencode/`, `docs/vault/`, `memory/`, and `specs/` so the team shares the memory system.
3. Restart OpenCode so it loads the new plugin, agents, and commands.

**Runtime requirements:** Node 18+ or Bun (for `install.mjs`). The plugin itself runs inside OpenCode's runtime — no Python / uv.

## Architecture

### Core Data Flow

```
Work session → memory/daily/YYYY-MM-DD_HHMMSS.md   (raw log)
                       ↓ /digest
              docs/vault/**/*.md                     (curated knowledge)
                       ↓ @memory-search subagent
              Retrieved context before any implementation
```

### Key Components

| Path                                    | Role                                                                       |
| --------------------------------------- | -------------------------------------------------------------------------- |
| `.opencode/plugin/memory.js`            | The plugin — all memory hooks in one module (see Hooks below)              |
| `.opencode/command/digest.md`           | `/digest` slash command — orchestrates the distillation pipeline           |
| `.opencode/command/install.md`          | `/install` slash command — runs `install.mjs` against the current project  |
| `.opencode/agent/memory-search.md`      | Subagent: retrieves vault docs before tasks (read-only)                    |
| `.opencode/agent/memory-digest-daily.md`| Subagent: distills one daily log → vault                                   |
| `.opencode/agent/memory-digest-spec.md` | Subagent: distills one spec → vault                                        |
| `.opencode/skills/memory/`              | Operating instructions (SKILL.md + context.md injected by the plugin)      |
| `.opencode/skills/digest-rules/SKILL.md`| Shared vault-writing rules invoked by both digest subagents                |
| `.opencode/skills/obsidian-vault/SKILL.md`| Vault naming/wikilink/size conventions                                    |
| `docs/vault/Home.md`                    | Vault master index — customize per target project                          |
| `docs/vault/Decisions/Index.md`         | ADR registry with next ADR number                                          |
| `specs/digested.txt`                    | Registry of already-processed spec files                                   |
| `install.mjs`                           | Bootstrap script — copies tooling + scaffolds the target project           |
| `opencode.json`                         | Project config — `instructions` glob, schema reference                     |

### Hooks

All memory behaviors live in **one plugin module**, `.opencode/plugin/memory.js`, which exports an async function returning a hooks object. OpenCode loads it automatically from `.opencode/plugin/`.

| OpenCode hook | Replaces (Claude Code) | Behavior |
| --- | --- | --- |
| `experimental.chat.system.transform` | `SessionStart` + `PostCompact` + both `UserPromptSubmit` hooks | Injects `skills/memory/context.md`, the search reminder, the log reminder, and (once after compaction) the re-read-base-docs reminder into the system prompt on every inference |
| `experimental.session.compacting` | `PreCompact` | Reminds to persist the daily log before compaction discards history |
| `tool.execute.before` (`task`) | `PreToolUse[Agent]` | Prepends a vault-consult reminder to subagent prompts (memory-system agents skipped) |
| `event` → `session.idle` | `Stop` | TUI toast: update/create the daily log if there was significant work |
| `event` → `session.compacted` | (part of `PostCompact`) | Arms the one-shot re-read-base-docs reminder for the next inference |

**Why fewer hooks:** OpenCode's `system.transform` runs before *every* inference, so the persistent context that Claude Code re-injected via separate `SessionStart`/`PostCompact`/`UserPromptSubmit` hooks collapses into one place and survives compaction for free.

The experimental hook surface still shifts between OpenCode versions — keep every hook body defensive (optional chaining, array guards, `try/catch`).

### `/digest` Pipeline

Processes files **sequentially** (not in parallel) to avoid write conflicts in shared vault documents like `Decisions/Index.md`:

1. Find all `memory/daily/*.md` → delegate each to the `memory-digest-daily` subagent via `task` → delete on success.
2. Find all `specs/*.md` not in `specs/digested.txt` → delegate each to the `memory-digest-spec` subagent → append to `digested.txt` on success.
3. Commit all vault changes to git (local only, no push).

### Vault Conventions

- **Wikilinks required**: `[[Section/Document]]` full-path format; never bare filenames.
- **Bidirectional links**: every new doc must link to and be linked from related docs.
- **No duplicates**: subagents `Grep` before writing; always update existing docs.
- **Language consistency**: detect existing vault language and maintain it.
- **Specs are immutable**: never modified or deleted after creation.
- **Path rules → nested `AGENTS.md`**: a directory-scoped `AGENTS.md` (loaded by OpenCode walking up from a file) is the native equivalent of a path-scoped rule.
