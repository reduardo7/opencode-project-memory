---
title: Expected Behaviors (NOT bugs)
summary: Non-obvious but intentional behaviors in the claude-project-memory plugin. Check before flagging as a bug or requesting a change.
tags: [development, gotchas, expected-behaviors]
---

# Expected Behaviors (NOT bugs)

Intentional design decisions and non-obvious behaviors that reviewers or new developers might mistakenly flag as bugs. Entries are added here by the `/claude-project-memory:memory-digest` process when a gotcha is discovered during a session.

See also: [[Claude/Memory]] | [[Development/Obsidian Vault]]

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

### Claude Code Agent — SKILL.md `model:` frontmatter ignored when content is injected into Agent prompt

**Behavior:** When a SKILL.md file's content is read and injected into a `general-purpose` Agent's prompt (as done by `memory-digest` for `memory-digest-daily` and `memory-digest-spec`), the `model:` field in the SKILL.md frontmatter has no effect. The sub-agent uses whatever model is the default unless `model:` is passed explicitly in the `Agent(...)` tool call.

**Why it's intentional:** The SKILL.md frontmatter is only processed by the Claude Code skill invocation mechanism (`Skill(skill: "...")` tool). When SKILL.md content is embedded into a `general-purpose` Agent prompt as plain text, the frontmatter is just string content — no metadata parsing occurs.

**Where it appears:** `skills/memory-digest/SKILL.md` — must explicitly pass `model: sonnet` in every `Agent(...)` spawn for `memory-digest-daily` and `memory-digest-spec`. Contrast with `memory-search`, which is invoked via `Skill(skill: "claude-project-memory:memory-search")` so its `model: haiku` frontmatter is applied automatically.

**Rule:** Any skill invoked via `Agent(subagent_type: "general-purpose", prompt: <SKILL.md content>)` must have `model:` passed explicitly as a parameter. Any skill invoked via `Skill(skill: "plugin:name")` automatically picks up the `model:` from its frontmatter.
