---
title: Expected Behaviors (NOT bugs)
summary: Non-obvious but intentional behaviors in the opencode-project-memory plugin. Check before flagging as a bug or requesting a change.
tags: [development, gotchas, expected-behaviors]
---

# Expected Behaviors (NOT bugs)

Intentional design decisions and non-obvious behaviors that reviewers or new developers might mistakenly flag as bugs. Entries are added here by the `/digest` process when a gotcha is discovered during a session.

See also: [[OpenCode/Memory]] | [[Development/Obsidian Vault]]

---

## How to use this document

Before flagging something as a bug or requesting a change, check this document. If a behavior is listed here, it is intentional.

---

## Template for new entries

```markdown
### [Technology/Layer] — [Short description]

**Behavior:** [What happens]
**Why it's intentional:** [Reason]
**Where it appears:** [File/class/pattern]
```

---

### Subagents — skills are NOT auto-loaded; they must be invoked explicitly

**Behavior:** The `memory-digest-daily` and `memory-digest-spec` subagents invoke the `digest-rules` and `obsidian-vault` skills explicitly in their Step 1 (via the `skill` tool), even though the parent context may already have loaded them.

**Why it's intentional:** A subagent runs with a fresh context. Skills loaded by the orchestrator do not carry over, so each subagent must load the shared rules itself or it will write to the vault without the naming/wikilink/size conventions.

**Where it appears:** `.opencode/agent/memory-digest-daily.md` and `.opencode/agent/memory-digest-spec.md`, Step 1.

---

### Plugin — experimental hooks are wrapped defensively on purpose

**Behavior:** Every hook body in `.opencode/plugin/memory.js` is wrapped in `try/catch` with optional chaining and array guards (e.g. it checks whether `output.system` is an array before pushing).

**Why it's intentional:** The `experimental.chat.system.transform` and `experimental.session.compacting` surfaces still change field names between OpenCode versions. Defensive code degrades gracefully (a reminder silently no-ops) instead of throwing and breaking the user's turn.

**Where it appears:** `.opencode/plugin/memory.js` — `pushSystem()` helper and the `try/catch` around each hook.

---

### Plugin — reminders live in the system prompt every turn, not on discrete events

**Behavior:** The search reminder and log reminder are injected on *every* inference via `system.transform`, not only on the first prompt of a session.

**Why it's intentional:** OpenCode has no per-prompt hook that can inject text conditioned on the user's message — `system.transform` runs before every inference but does not yet receive the user message (so keyword heuristics are impossible). Always-on injection is simpler and survives compaction for free.

**Where it appears:** `.opencode/plugin/memory.js` — `experimental.chat.system.transform`.
