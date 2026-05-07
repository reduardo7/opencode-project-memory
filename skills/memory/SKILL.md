---
name: memory
description: Operating instructions for the long-term memory system — what to record, when, and in what format during sessions.
version: 1.1.0
model: haiku
allowed-tools: [Read]
---

# Long-Term Memory — Operating Instructions

**Mandatory:** Read `skills/memory/context.md` now — it contains the full operational rules for session logging, what to record, and how to use the two memory systems.

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

skills/memory/
├── SKILL.md           ← this file (system architecture and activation)
└── context.md         ← operational rules injected at session start
```

- **`memory/daily/*.md`** is the **raw log**: records without filter every decision made, every error committed, every user correction, every non-obvious finding during the current session.
- **`docs/vault/`** is the **curated knowledge**: final destination of processed learnings.
- The `/claude-project-memory:memory-digest` command processes `daily/` files and promotes them to the vault, deleting them after processing.

---

## Activation mechanism

The operational rules in `context.md` reach Claude via three complementary paths — all three are needed; none is sufficient alone:

| Mechanism | File | When it fires |
| --- | --- | --- |
| **Hook** (SessionStart/PostCompact) | `hooks/memory_session_start_reminder.py` | Reads and injects `skills/memory/context.md` at session start and after compaction |
| **This skill** | `skills/memory/SKILL.md` | When invoked — mandates reading `context.md` via `Read` tool |
| **Rule** | `.claude/rules/memory.md` | When touching `memory/**/*` or `memory-digest` files |

### Memory hooks

| Hook | Type | When it fires | Behavior |
| --- | --- | --- | --- |
| `hooks/memory_session_start_reminder.py` | `SessionStart` + `PostCompact` | Session start and after compaction | Reads and injects `skills/memory/context.md` directly |
| `hooks/memory_search_reminder.py` | `UserPromptSubmit` | Each user prompt | Reminds to invoke `memory-search` before non-trivial tasks |
| `hooks/memory_log_reminder.py` | `UserPromptSubmit` | Each user prompt | Detects non-trivial work; reminds to create/update daily log before responding |
| `hooks/memory_pre_agent_reminder.py` | `PreToolUse[Agent]` | Before any sub-agent | Reminds to include vault context; skips memory system agents |
| `hooks/memory_stop_reminder.py` | `Stop` | End of each response | Reminds to update daily log or create one if there was significant work |
| `hooks/memory_pre_compact_reminder.py` | `PreCompact` | Before compaction | Reminds to persist daily log before context is discarded |
| `hooks/memory_post_compact_reminder.py` | `PostCompact` | After compaction | Reminds to re-read base vault docs to restore architectural context |

---

## Daily processing (`/claude-project-memory:memory-digest`)

Once a day (or when the user invokes it), the command:

1. Reads all files in `memory/daily/*.md`.
2. Processes each one **sequentially** with a **Sonnet model** sub-agent to extract durable knowledge.
3. Promotes each learning to the **correct location in the vault** (`docs/vault/`), creating or updating existing files.
4. Ensures **bidirectional linking** with related vault documents.
5. Updates `docs/vault/Home.md` and `.claude/commands/conditional-docs.md` (if it exists) if new documents appear.
6. **Deletes the processed files** in `memory/daily/` — the knowledge now lives in the curated vault.

See `skills/memory-digest/SKILL.md` for the complete procedure.

---

## Summary flow

```
session → memory/daily/<ts>.md  (raw, ephemeral)
               ↓  /claude-project-memory:memory-digest (Sonnet, sequential)
           docs/vault/...                 (curated, permanent, linked)
               ↓
           memory/daily/<ts>.md DELETED
```
