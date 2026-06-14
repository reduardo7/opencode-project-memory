---
name: digest-rules
description: Shared vault-writing rules for the memory-digest-daily and memory-digest-spec subagents.
---

# Vault-Writing Rules — Shared by Digest Subagents

---

## Granularity filter — vault purpose

The vault documents **how to generate quality code**: patterns, conventions, architectural decisions, and non-obvious constraints. It is not a mirror of the codebase.

Before promoting any item, ask: *"Does this help someone write better code in the future, or does it just describe what the code looks like right now?"*

- If it helps write better code → promote it as a reusable pattern or decision rationale.
- If it only describes current code state (field types, enum values, method parameters, step-by-step task lists) → discard it. That lives in source files and git history.

---

## Reference vs. value — code findings

When a code finding relates to specific files, modules, or configuration:

- **Write the file path and its purpose**, not the specific values it contains.
- **Include a brief description** of what the file/module contains (for future readers to know why it matters).

**Examples:**

| ❌ Do NOT write | ✅ Write instead |
| --- | --- |
| "The constant `MAX_RETRIES` is set to 5" | "`src/config/constants.ts` — contains retry configuration and exponential backoff parameters" |
| "The User enum has values: ADMIN, USER, GUEST" | "`src/types/user.ts` — defines user role types and permission boundaries" |
| "The database connection pool size is 10" | "`src/db/pool.ts` — manages connection pooling strategy and resource limits" |

**Rationale:** File paths and purposes remain durable and accurate. Specific values change frequently and belong in source code, not vault documentation. Readers who need the exact values will find them by reading the referenced file.

---

## Write to vault

> **Writing convention:** All vault content must follow the `obsidian-vault` skill — YAML frontmatter, kebab-case filenames, wikilink format, and section structure. The skill was invoked in Step 1; apply its rules when writing every document.

For each classified item:

1. **Check for duplicates first** — use `Grep` to verify the concept is not already documented.
2. **Update existing documents** when the concept is already there — add a sub-section or table row; never create a duplicate file.
3. **Create new documents** when the topic is genuinely new: choose the vault section that best fits (use Step 3's classification table as a guide), name the file following `obsidian-vault` skill rules (kebab-case filename, YAML frontmatter with `title` and `summary`), and structure it with clear headings, organized sections, and tables or lists — curate, do not dump raw notes.
4. **Apply bidirectional Obsidian links** (`[[Section/Document]]`) — new notes must link to related documents, and related documents must link back.
5. **Language:** maintain the vault's established language (check existing vault documents — typically whatever language is already in use).
6. **Placement:** always use full path relative to vault root (e.g., `[[Decisions/ADR - Security]]`), not bare filenames.

---

## Update indexes

If new vault documents were created:

- Add entry to `docs/vault/Home.md` in the correct section.
- Add entry to `docs/vault/Decisions/Index.md` if a decision was recorded.

---

## Update skills

Skills live in `.opencode/skills/<name>/SKILL.md`. If any extracted knowledge belongs in a skill, update it — this is as important as updating the vault.

**How to find skills:** `Glob` with pattern `.opencode/skills/*/SKILL.md`.

**When to update a skill:**
- A new reusable pattern was discovered.
- A recurring mistake was corrected and the correct approach should be codified.
- A gotcha specific to a technology layer was found.
- A new standard was established.

**When NOT to update a skill:**
- The knowledge is purely business/domain-specific (→ vault ADR or PRD).
- The knowledge is infrastructure/deployment (→ `docs/vault/Architecture/`).
- The pattern is already in the skill — always `Grep` the `SKILL.md` before writing.

**How to update:**
1. Read the relevant `SKILL.md` to find the correct section.
2. Add the new pattern, rule, or anti-pattern consistently with existing content.
3. If a pattern contradicts existing content, update it — never leave conflicting guidance.

---

## Evaluate directory AGENTS.md

OpenCode loads `AGENTS.md` files by walking up from the file being worked on, so a directory-scoped `AGENTS.md` is the native equivalent of a path rule. If a new vault document is tied to a specific folder, file, or file type in the repo:

- Check whether an `AGENTS.md` already exists in (or above) that directory referencing the vault doc.
- If not, create or extend `<path>/AGENTS.md`:

```markdown
# <Descriptive Name>

## Mandatory reading

Before creating or modifying files in this directory, read:

- `docs/vault/<Section>/<Document>.md` — one-line description.

## Mandatory documentation update

When creating, modifying, or deleting files here:

1. Reflect changes in `docs/vault/<Section>/<Document>.md` in the same commit.
```

> Keep these directory `AGENTS.md` files short — they point at the vault, they do not duplicate it. If the repo also keeps a root `AGENTS.md`, prefer a focused nested file over bloating the root.

---

## Shared critical rules

- Never promote secrets, credentials, or sensitive data to the vault.
- Never duplicate information already in the vault — always `Grep` before writing.
- Bidirectional links are mandatory — an isolated vault document loses value.
