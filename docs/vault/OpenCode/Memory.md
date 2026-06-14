---
title: OpenCode — Long-Term Memory System
summary: Sistema de memoria persistente por sesión. Captura notas en memory/daily/, las destila al vault con /digest, y consulta el vault antes de cada tarea no trivial.
tags: [opencode, memory, vault, knowledge, log, digest]
---

# OpenCode — Long-Term Memory System

System for capturing and distilling knowledge per session. Converts raw session notes and implementation specs into curated, permanent knowledge inside the vault.

See also: [[Development/Obsidian Vault]] | [[Decisions/Index]] | [[Architecture/Project Structure]]

---

## Purpose

Capture decisions, errors, corrections, and learnings from each work session and progressively convert them into curated knowledge inside the vault (`docs/vault/`). Memory is **project-scoped**, not personal: everything saved in `memory/` ends up in the repository for the entire team's benefit.

---

## Layers

| Layer                | Purpose                                | Lifecycle                                  |
| -------------------- | -------------------------------------- | ------------------------------------------ |
| `memory/daily/*.md`  | Raw log — no filter, in real time      | Ephemeral: deleted after `/digest`         |
| `specs/*.md`         | Implementation specs per feature/issue | Immutable: never modified or deleted       |
| `specs/digested.txt` | Registry of already-digested specs     | Accumulative: only lines added             |
| `docs/vault/`        | Curated, linked, permanent knowledge   | Permanent                                  |

---

## Complete flow

```
SESSION → memory/daily/<ts>.md   (the agent writes: context, decisions, errors, learnings)
SPECS   → specs/<name>.md         (immutable)

/digest  (orchestrator command)
  ├─→ [each daily, sequential]    → memory-digest-daily subagent → docs/vault/... ; deletes the log
  └─→ [each new spec, sequential] → memory-digest-spec subagent  → docs/vault/... ; records basename in specs/digested.txt

docs/vault/  (curated knowledge, permanent, linked with [[wikilinks]])
```

Sequential processing is mandatory — one file at a time avoids write conflicts in shared vault documents (e.g., `Decisions/Index.md`, `Home.md`).

---

## Session log (`memory/daily/<ts>.md`)

**The agent is solely responsible for creating and completing this file.** No hook creates it — if the agent does not write it, it does not exist.

Named with timestamp `YYYY-MM-DD_HHMMSS` for chronological order. **Created only when there is something significant to record** — never blank at session start.

```markdown
---
session_start: YYYY-MM-DD HH:MM
topic: <main topic, one line>
---
# Session <date>
## Context
## Decisions
## Errors and corrections
## Learnings
## References
```

Complete `topic:` and `## Context` in the same step the file is created. Update the other sections incrementally, not at the end.

**Record:** non-trivial decisions, errors + user corrections (literal if possible), findings not in the vault, recurring patterns, explicit user feedback.
**Do NOT record:** content already in `AGENTS.md` or the vault, ephemeral state, git history, secrets.

---

## Activation — the memory plugin

A single OpenCode plugin (`.opencode/plugin/memory.js`) drives the system. OpenCode loads it automatically from `.opencode/plugin/`.

| OpenCode hook | Behavior |
| --- | --- |
| `experimental.chat.system.transform` | Injects the operating context (`.opencode/skills/memory/context.md`), the search reminder, the log reminder, and (once after compaction) the re-read-base-docs reminder — into the system prompt on every inference |
| `experimental.session.compacting` | Reminds to persist the daily log before compaction discards history |
| `tool.execute.before` (`task`) | Prepends a vault-consult reminder to subagent prompts (memory-system agents skipped) |
| `event` → `session.idle` | TUI toast: update/create the daily log if there was significant work |
| `event` → `session.compacted` | Arms the one-shot re-read-base-docs reminder |

Because `system.transform` runs before *every* inference, the persistent context survives compaction without a dedicated post-compaction hook — the plugin only needs to add a one-shot "re-read base docs" nudge.

---

## `/digest` command

**File:** `.opencode/command/digest.md` — a pure orchestrator. It discovers files, delegates each to a subagent via the `task` tool, records results, and commits.

- **Daily logs:** lists `memory/daily/*.md` (excludes `.gitkeep`), processes each with the `memory-digest-daily` subagent, and deletes the log on confirmed success.
- **Specs:** lists `specs/*.md` not present in `specs/digested.txt`, processes each with the `memory-digest-spec` subagent, and appends the basename on success.
- **Commit:** stages only `memory/daily/`, `specs/digested.txt`, `docs/vault/`, `.opencode/skills/`, and any `AGENTS.md` changes; commits locally (no push).

---

## Subagents

| Subagent | File | Role |
| --- | --- | --- |
| `memory-search` | `.opencode/agent/memory-search.md` | Read-only retrieval: returns relevant vault docs before a non-trivial task. Delegate with `@memory-search <task>`. |
| `memory-digest-daily` | `.opencode/agent/memory-digest-daily.md` | Distills one `memory/daily/<ts>.md` into the vault. Spawned by `/digest`. |
| `memory-digest-spec` | `.opencode/agent/memory-digest-spec.md` | Distills one `specs/<name>.md` into the vault. Spawned by `/digest`. |

Each digest subagent loads the shared `digest-rules` and `obsidian-vault` skills in its Step 1 (skills are not auto-loaded in subagent context — they must be invoked explicitly with the `skill` tool).

---

## Path rules → nested `AGENTS.md`

OpenCode loads `AGENTS.md` files by walking up from the file being edited. A directory-scoped `AGENTS.md` is therefore the native equivalent of a path-scoped rule: when a vault document is tied to a code path, the digest subagents create or extend `<path>/AGENTS.md` pointing at that vault doc.

---

## What is NOT long-term memory

- **OpenCode user config (`~/.config/opencode/`)**: personal preferences only. Never store project decisions there.
- **Code comments**: point-in-time intent documentation.
- **`.opencode/skills/memory/SKILL.md`**: operating instructions, not content.
