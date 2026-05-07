# Long-Term Memory — Operational Context

## Session log

Create `memory/daily/YYYY-MM-DD_HHMMSS.md` **only when there is something significant to record** (never blank at session start). Reuse if one already exists for this session.

```markdown
---
session_start: YYYY-MM-DD HH:MM
topic: <one line>
---
# Session <date>
## Context
## Decisions
## Errors and corrections
## Learnings
## References
```

Update **immediately** when it happens — never batch for the end:

| Event | Section |
| --- | --- |
| What the user asked for and why | `## Context` |
| Technical decision made | `## Decisions` |
| User corrected an error (quote literally) | `## Errors and corrections` |
| Discovery not in vault | `## Learnings` |
| File / issue / PR touched | `## References` |

**Record:** non-trivial decisions, errors + corrections, vault gaps, recurring gotchas, user feedback on how to work.  
**Do NOT record:** content already in `CLAUDE.md`/vault, ephemeral state, git history, secrets.

## Before non-trivial tasks

Invoke `claude-project-memory:memory-search` before features, architectural changes, schema changes, ADR work, or questions about what exists:

```
Agent(subagent_type: "claude-project-memory:memory-search", prompt: "<task>")
```

Skip for: simple bug fixes, questions already answered in context, trivial sessions.

## Two memory systems

| | Path | Use for |
| --- | --- | --- |
| **Project** | `memory/daily/<ts>.md` → vault | Decisions, corrections, patterns — team knowledge |
| **Personal** | `~/.claude/projects/.../memory/` | User preferences (style, detail level, etc.) |
