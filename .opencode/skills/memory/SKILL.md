---
name: memory
description: Memory system — what and when to record during sessions.
metadata:
  version: 2.0.0
---

# Long-Term Memory — Operating Instructions

**Mandatory:** Read `.opencode/skills/memory/context.md` now — it contains the full operational rules for session logging, what to record, and how to use the two memory systems.

---

## Purpose

Capture decisions, errors, corrections, and learnings from each work session and progressively convert them into curated knowledge inside the Obsidian vault (`docs/vault/`). Memory is **project-scoped**, not personal: everything saved here ends up in the repository for the entire team's benefit.

---

## Architecture

```
memory/
└── daily/             ← raw session log (ephemeral)
    └── <timestamp>.md ← one file per chat/session

docs/vault/            ← curated knowledge (permanent destination)

.opencode/skills/memory/
├── SKILL.md           ← this file (system architecture and activation)
└── context.md         ← operational rules injected at session start
```

- **`memory/daily/*.md`** is the **raw log**: records without filter every decision made, every error committed, every user correction, every non-obvious finding during the current session.
- **`docs/vault/`** is the **curated knowledge**: final destination of processed learnings.
- The `/digest` command processes `daily/` files and promotes them to the vault, deleting them after processing.

---

## Activation mechanism

The operational rules in `context.md` reach the model through two complementary paths:

| Mechanism | Source | When it fires |
| --- | --- | --- |
| **Plugin** (`experimental.chat.system.transform`) | `.opencode/plugin/memory.js` reads `context.md` | Injected into the system prompt on every inference (covers session start and post-compaction automatically) |
| **This skill** | `.opencode/skills/memory/SKILL.md` | When invoked — mandates reading `context.md` |

### Memory plugin hooks

A single plugin (`.opencode/plugin/memory.js`) implements all memory behaviors:

| OpenCode hook | When it fires | Behavior |
| --- | --- | --- |
| `experimental.chat.system.transform` | Before every model inference | Injects `context.md`, the search reminder, the log reminder, and (once after compaction) the re-read-base-docs reminder |
| `experimental.session.compacting` | Before compaction | Reminds to persist the daily log before context is discarded |
| `tool.execute.before` (`task`) | Before any subagent launch | Reminds the subagent to consult the vault via `memory-search` (memory-system agents are skipped) |
| `event` → `session.idle` | End of each turn | TUI toast: update or create the daily log if there was significant work |
| `event` → `session.compacted` | After compaction | Arms the one-shot re-read-base-docs reminder |

---

## Daily processing (`/digest`)

Once a day (or when the user invokes it), the command:

1. Reads all files in `memory/daily/*.md`.
2. Processes each one **sequentially** with the `memory-digest-daily` subagent to extract durable knowledge.
3. Promotes each learning to the **correct location in the vault** (`docs/vault/`), creating or updating existing files.
4. Ensures **bidirectional linking** with related vault documents.
5. Updates `docs/vault/Home.md` if new documents appear.
6. **Deletes the processed files** in `memory/daily/` — the knowledge now lives in the curated vault.

See `.opencode/command/digest.md` for the complete procedure.

---

## Summary flow

```
session → memory/daily/<ts>.md  (raw, ephemeral)
               ↓  /digest (sequential subagents)
           docs/vault/...                 (curated, permanent, linked)
               ↓
           memory/daily/<ts>.md DELETED
```
