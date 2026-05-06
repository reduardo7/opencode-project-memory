# Long-Term Memory — Operating Instructions

This document defines how Claude Code should operate with the long-term memory system in this project. **Mandatory reading at the start of every session** (referenced from `CLAUDE.md`).

---

## Purpose

Capture decisions, errors, corrections, and learnings from each work session and progressively convert them into curated knowledge inside the Obsidian vault (`docs/vault/`). Memory is **project-scoped**, not personal: everything saved here ends up in the repository for the entire team's benefit.

---

## Architecture

```
memory/
├── memory.md          ← this file (how to operate)
└── daily/             ← raw session log (ephemeral)
    └── <timestamp>.md ← one file per chat/session

docs/vault/            ← curated knowledge (permanent destination)
```

- **`memory/daily/*.md`** is the **raw log**: records without filter every decision made, every error committed, every user correction, every non-obvious finding during the current session.
- **`docs/vault/`** is the **curated knowledge**: final destination of processed learnings.
- The `/memory-digest` command (see `skills/memory-digest/SKILL.md`) processes `daily/` files and promotes them to the vault, deleting them after processing.

---

## Activation mechanism

The instruction to create and maintain the session log is enforced via **3 complementary components** — all three are needed for correct operation; none is sufficient alone:

| Mechanism              | File                                     | When it fires                                        |
| ---------------------- | ---------------------------------------- | ---------------------------------------------------- |
| **CLAUDE.md** (inline) | `CLAUDE.md` — "Long-Term Memory" section | Always — CLAUDE.md loads in every session            |
| Specific Rule          | `.claude/rules/memory.md`                | When touching `memory/**/*` or `memory-digest` files |
| **Hooks**              | See table below                          | Each user prompt, agent launch, and end of response  |

The instruction is embedded directly in `CLAUDE.md` to guarantee it applies in any context, regardless of what domain is being worked on.

### Memory hooks

Four hooks complement the activation system:

| Hook                                         | Type                | When it fires                  | Behavior                                                                                                                                                                                                                          |
| -------------------------------------------- | ------------------- | ------------------------------ | --------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------------- |
| `.claude/hooks/memory_search_reminder.py`    | `UserPromptSubmit`  | Each user prompt               | Injects a reminder to `stdout` to invoke `memory-search` before non-trivial tasks. Claude decides whether to apply it based on the prompt's complexity.                                                                           |
| `.claude/hooks/memory_log_reminder.py`       | `UserPromptSubmit`  | Each user prompt               | Reads the prompt from stdin, uses keyword heuristics to detect non-trivial work, and injects a proactive reminder to create/update the daily log **before** responding. Skips trivial prompts (simple questions, clarifications). |
| `.claude/hooks/memory_pre_agent_reminder.py` | `PreToolUse[Agent]` | Before launching any sub-agent | Injects a reminder to include vault context in the sub-agent's prompt. Does not fire for memory system agents (`memory-search`, `memory-digest-daily`, `memory-digest-spec`).                                                     |
| `.claude/hooks/memory_stop_reminder.py`      | `Stop`              | At the end of each response    | Injects a `systemMessage` via JSON. If there are active files in `memory/daily/`, asks to update them. If none, reminds Claude to create one only if there was significant work.                                                  |

`UserPromptSubmit` and `PreToolUse` hooks print to `stdout` (additional context before the prompt/tool call). The `Stop` hook returns `{"systemMessage": "..."}` via `stdout`.

---

## Searching documentation before each task

**Before implementing any non-trivial task**, invoke the `memory-search` sub-agent to retrieve all relevant documentation from the vault:

```
Agent(subagent_type: "memory-search", prompt: "<task description>")
```

The agent reads `docs/vault/Home.md`, `conditional-docs.md` (if it exists), recent daily logs, and `Decisions/Index.md` — then follows all relevant cross-references in the vault. Returns the full content of each document — without summarizing or paraphrasing.

**When it is mandatory:**

- Before implementing an endpoint, feature, or architectural change
- Before modifying the DB schema
- Before answering questions about what exists in the project (scripts, components, integrations, decisions)
- Before creating or updating an ADR

**When it is not necessary:**

- Simple bug fixes without architectural impact
- Questions already answered in the current conversation context
- Trivial sessions without implementation work

---

## Operating rules during a session

### 1. Daily file — created on demand

**Claude creates the file only when there is something significant to record** — never blank at session start. Path:

```
memory/daily/YYYY-MM-DD_HHMMSS.md
```

If a file for the current session already exists, reuse it instead of creating a new one. When creating the file, fill in `topic:` in the frontmatter and `## Context` in the same step.

**Minimum file structure:**

```markdown
---
session_start: YYYY-MM-DD HH:MM
topic: <main topic of the session, one line>
---

# Session <date>

## Context

<what the user asked for, why>

## Decisions

- <decision>: <reason>

## Errors and corrections

- <what I did wrong>: <how the user corrected me / what I learned>

## Learnings

- <non-obvious finding, pattern, gotcha>

## References

- <files touched, issues, PRs>
```

In trivial sessions (one simple question with no actions) **do not create a file** — the log only exists when there is something worth recording.

### 2. Record during the session

**What to record:**

- Non-trivial technical decisions and their justification.
- Errors I made and how the user corrected me (literal if possible).
- Discoveries about the project not documented in the vault.
- Recurring patterns or gotchas.
- Any explicit user feedback about how to work.

**What NOT to record:**

- Information already in `CLAUDE.md` or the vault.
- Ephemeral conversation state (in-progress tasks, internal TODOs).
- Content already captured by `git log` / `git blame`.
- Secrets, credentials, sensitive data.

### 3. Update immediately — not at the end

**Every time something significant happens, update the file before continuing with the next action.** Do not accumulate for the end: at the end of the session it is easy to forget or summarize poorly.

| Event                                                     | Section to update           |
| --------------------------------------------------------- | --------------------------- |
| Session start — what the user asked for and why           | `## Context`                |
| A technical decision was made                             | `## Decisions`              |
| The user corrected an error (quote literally if possible) | `## Errors and corrections` |
| Something not documented in the vault was discovered      | `## Learnings`              |
| A file, issue, or PR was touched                          | `## References`             |

Use `Edit` to append to the file without rewriting it.

---

## Daily processing (`/memory-digest`)

Once a day (or when the user invokes it), the `/memory-digest` command:

1. Reads all files in `memory/daily/*.md`.
2. Processes each one **sequentially** with a **Sonnet model** sub-agent to extract durable knowledge.
3. Promotes each learning to the **correct location in the vault** (`docs/vault/`), creating or updating existing files.
4. Ensures **bidirectional linking** with related vault documents.
5. Updates `docs/vault/Home.md` and `.claude/commands/conditional-docs.md` (if it exists) if new documents appear.
6. **Deletes the processed files** in `memory/daily/` — the knowledge now lives in the curated vault.

See `skills/memory-digest/SKILL.md` for the complete procedure.

---

## The two memory systems — when to use each

| System                   | Path                             | Use it for                                                         | Do NOT use it for                                      |
| ------------------------ | -------------------------------- | ------------------------------------------------------------------ | ------------------------------------------------------ |
| **This repository**      | `memory/daily/<ts>.md` → vault   | Project decisions, corrections, patterns, gotchas — team knowledge | Personal user preferences                              |
| **Personal auto-memory** | `~/.claude/projects/.../memory/` | Personal user preferences (language, response style, etc.)         | Project decisions, coding standards, development rules |

**Golden rule:** when the user says "remember this", "save this", "add to your knowledge base" — determine the type first:

- If it's about the **project** (technical decision, pattern, correction, gotcha) → record in `memory/daily/<timestamp>.md` in this repository.
- If it's about **user preferences** (how they want Claude to communicate, level of detail, etc.) → record in personal auto-memory.

**What is NOT memory:**

- **Code comments**: not memory, they are point-in-time intent documentation.
- **`memory/memory.md`**: these are instructions, not content.

---

## Summary flow

```
session → memory/daily/<ts>.md  (raw, ephemeral)
               ↓  /memory-digest (Sonnet, sequential)
           docs/vault/...                 (curated, permanent, linked)
               ↓
           memory/daily/<ts>.md DELETED
```
