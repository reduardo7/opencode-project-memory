---
name: memory-digest
description: Distill daily memory logs into the vault.
version: 1.0.0
model: sonnet
allowed-tools: ["Glob", "Grep", "Read", "Edit", "Write", "Bash", "Agent"]
---

Processes the raw session logs (`memory/daily/*.md`) and undigested specs (`specs/*.md`), and promotes durable knowledge to the Obsidian vault (`docs/vault/`).

Each file is processed by an **independent sub-agent** to maintain clean context. This command acts as an orchestrator: discovers files, launches sub-agents, records results, and cleans up.

---

## Objective

Convert raw session notes and implementation specs into curated, linked, and permanent knowledge in the vault.

---

## Procedure

### 1. Discover pending logs

- List all files in `memory/daily/*.md` using `Glob` (exclude `.gitkeep`).
- Sort chronologically by name (names are timestamps).
- If there are no files, continue to step 3 (there may be specs).

### 2. Process each log with a sub-agent

Process **one at a time** (sequential) to avoid write conflicts in the same vault documents (e.g., `Decisions/Index.md`, `Home.md`):

1. Read the full content of `skills/memory-digest-daily/SKILL.md`.
2. For each file (in chronological order): spawn a **`general-purpose`** sub-agent with **`model: sonnet`** whose prompt consists of the full content of `skills/memory-digest-daily/SKILL.md` followed by a line `Input file: <absolute path>`. Wait for its result before continuing to the next.
3. If the sub-agent reports success: **delete** the corresponding `memory/daily/<ts>.md` file.
4. If the sub-agent reports error or unclassified items (`NOTES` not empty): leave the file, record the problem for the final report. If the sub-agent wrote partially to the vault, note it in the report for human review — do not revert manually.

### 3. Discover pending specs

1. Read `specs/digested.txt` and build the set of already-processed basenames. If the file does not exist, treat the set as empty (process all found specs).
2. List all files in `specs/*.md` with `Glob`.
3. Filter: keep only those **not** in `specs/digested.txt`.
4. If there are no new specs, continue to step 5 (automatic commit).

### 4. Process each spec with a sub-agent

Process **one at a time** (sequential) to avoid write conflicts in the same vault documents:

1. Read the full content of `skills/memory-digest-spec/SKILL.md`.
2. For each spec (in chronological order): spawn a **`general-purpose`** sub-agent with **`model: sonnet`** whose prompt consists of the full content of `skills/memory-digest-spec/SKILL.md` followed by a line `Input file: <absolute path>`. Wait for its result before continuing to the next.
3. If the sub-agent reports success: append the spec's basename to the end of `specs/digested.txt`.
4. If the sub-agent reports error: do not record in `digested.txt` — will retry on next execution. If the sub-agent wrote partially to the vault, note it in the report for human review.

> **Note:** Required Claude Rules are created by the sub-agents directly in their Step 7. The orchestrator does not create them — only report those that appear in the outputs.

### 5. Automatic commit

After processing all files (logs and specs), commit all generated changes:

1. Verify there are changes with `git status`.
2. Add only relevant files to staging (never blind `git add -A`):
   - `memory/daily/` (deletions)
   - `specs/digested.txt`
   - `docs/vault/`
   - `.claude/skills/`
   - `.claude/rules/`
   - `.agents/rules/`
   - `CLAUDE.md` (if modified by any sub-agent)
3. Create the commit with the following format:
   - **Title:** `AI - Memory Digest`
   - **Body:** summary of changes made during this digest, including:
     - Logs processed and deleted (with what was extracted from each).
     - Specs processed and what was updated in vault/skills for each.
     - Claude Rules created or updated (if any).
4. **Do not push** — local commit only in the current branch.
5. If there are no changes to commit, inform the user and skip the commit.

### 6. Final report

Show the user a concise summary:

- Logs processed and deleted / skipped (with reason).
- Specs processed and recorded in `digested.txt` / failed.
- Vault files created and modified (with paths).
- Skills updated (`.claude/skills/*/SKILL.md`).
- Claude Rules created or updated.
- Items pending human review (`NOTES` from sub-agents).
- Confirm the commit was made (or inform if there were no changes).

---

## Sub-agents

Both sub-agents are spawned as **`general-purpose`** agents with **`model: sonnet`**. Their instructions are loaded at runtime by reading the skill file and embedding it into the prompt.

| Skill file (instructions source) | Agent type | Model | Purpose |
|----------------------------------|------------|-------|---------|
| `skills/memory-digest-daily/SKILL.md` | `general-purpose` | `sonnet` | Processes one `memory/daily/<ts>.md` → vault + skills |
| `skills/memory-digest-spec/SKILL.md` | `general-purpose` | `sonnet` | Processes one `specs/<name>.md` → vault + skills |

---

## Critical rules

- **Never** delete a `memory/daily/*.md` file without sub-agent success confirmation.
- **Never** record a spec in `digested.txt` without sub-agent success confirmation.
- **Never** promote secrets, credentials, or sensitive data to the vault.
- **Always** process one file at a time — never in parallel.
- **Always** respect the vault language (see sub-agent instructions for the configured language).
