---
description: Distill daily memory logs and specs into the Obsidian vault.
agent: build
---

**Execute the procedure below immediately. Do not ask for confirmation — just run it.**

You are the memory digest orchestrator. Your job is to process the raw session logs (`memory/daily/*.md`) and undigested specs (`specs/*.md`), and promote durable knowledge to the Obsidian vault (`docs/vault/`).

Each file is processed by an **independent subagent** to maintain clean context. This command acts as an orchestrator: it discovers files, delegates to subagents via the `task` tool, records results, and cleans up.

---

## Objective

Convert raw session notes and implementation specs into curated, linked, and permanent knowledge in the vault.

---

## Procedure

### 1. Discover pending logs

- List all files in `memory/daily/*.md` using `glob` (exclude `.gitkeep`).
- Sort chronologically by name (names are timestamps).
- If there are no files, continue to step 3 (there may be specs).

### 2. Process each log with a subagent

Process **one at a time** (sequential) to avoid write conflicts in the same vault documents (e.g., `Decisions/Index.md`, `Home.md`):

1. For each file (in chronological order): use the `task` tool to delegate to the **`memory-digest-daily`** subagent, passing a prompt whose body is `Input file: <absolute path>`. Wait for its result before continuing to the next.
2. If the subagent reports success: **delete** the corresponding `memory/daily/<ts>.md` file.
3. If the subagent reports an error or unclassified items (`NOTES` not empty): leave the file and record the problem for the final report. If the subagent wrote partially to the vault, note it for human review — do not revert manually.

### 3. Discover pending specs

1. Read `specs/digested.txt` and build the set of already-processed basenames. If the file does not exist, treat the set as empty (process all found specs).
2. List all files in `specs/*.md` with `glob`.
3. Filter: keep only those **not** in `specs/digested.txt`.
4. If there are no new specs, continue to step 5 (automatic commit).

### 4. Process each spec with a subagent

Process **one at a time** (sequential) to avoid write conflicts in the same vault documents:

1. For each spec (in chronological order): use the `task` tool to delegate to the **`memory-digest-spec`** subagent, passing a prompt whose body is `Input file: <absolute path>`. Wait for its result before continuing to the next.
2. If the subagent reports success: append the spec's basename to the end of `specs/digested.txt`.
3. If the subagent reports an error: do not record it in `digested.txt` — it will retry on the next run. If the subagent wrote partially to the vault, note it for human review.

> **Note:** Directory `AGENTS.md` files are created by the subagents directly in their Step 4–7. The orchestrator does not create them — it only reports those that appear in the outputs.

### 5. Automatic commit

After processing all files (logs and specs), commit all generated changes:

1. Verify there are changes with `git status`.
2. Add only relevant files to staging (never blind `git add -A`):
   - `memory/daily/` (deletions)
   - `specs/digested.txt`
   - `docs/vault/`
   - `.opencode/skills/`
   - `AGENTS.md` files created or updated by subagents (root and nested)
3. Create the commit with the following format:
   - **Title:** `docs: AI MemoryDigest`
   - **Body:** technical summary in English listing only section titles (no detail):
     - Logs processed (titles only).
     - Specs processed (titles only).
     - Vault files created or updated (titles only).
     - AGENTS.md files created or updated (titles only, if any).
4. **Do not push** — local commit only on the current branch.
5. If there are no changes to commit, inform the user and skip the commit.

### 6. Final report

Show the user a concise summary:

- Logs processed and deleted / skipped (with reason).
- Specs processed and recorded in `digested.txt` / failed.
- Vault files created and modified (with paths).
- Skills updated (`.opencode/skills/*/SKILL.md`).
- AGENTS.md files created or updated.
- Items pending human review (`NOTES` from subagents).
- Confirm the commit was made (or inform if there were no changes).

---

## Subagents

| Subagent | Purpose |
|----------|---------|
| `memory-digest-daily` | Processes one `memory/daily/<ts>.md` → vault + skills |
| `memory-digest-spec` | Processes one `specs/<name>.md` → vault + skills |

---

## Critical rules

- **Never** delete a `memory/daily/*.md` file without subagent success confirmation.
- **Never** record a spec in `digested.txt` without subagent success confirmation.
- **Never** promote secrets, credentials, or sensitive data to the vault.
- **Always** process one file at a time — never in parallel.
- **Always** respect the vault language (see subagent instructions for the configured language).
