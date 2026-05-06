# Claude Project Memory

A long-term memory system for Claude Code. Captures session decisions, errors, and discoveries in raw daily logs, then distills them into a curated Obsidian vault via the `/memory-digest` command.

### Why this approach is different

Most memory systems store knowledge **per-user**, in a global location on the developer's machine. This system stores memory **inside the repository** — in `docs/vault/` — which means:

- **Shared across the team**: every developer who clones the repo inherits the accumulated context — past decisions, known pitfalls, architectural rationale
- **Versioned in git**: the knowledge base evolves alongside the code, and its history is fully auditable
- **Obsidian-compatible**: the vault uses wikilinks and bidirectional links, making it navigable as a knowledge graph — not just a flat log dump
- **Gets smarter over time**: each session adds context; Claude's answers improve as the vault grows, for everyone on the team

This makes the memory a **project asset**, not a personal one.

---

## How it works

```
Session work
  └─→ memory/daily/<timestamp>.md   (raw, ephemeral — Claude writes in real time)

/memory-digest  (orchestrator, Sonnet model)
  ├─→ [each daily log] → memory-digest-daily sub-agent
  │       └─→ extracts durable knowledge → docs/vault/...
  │       └─→ deletes memory/daily/<ts>.md
  │
  └─→ [each undigested spec] → memory-digest-spec sub-agent
          └─→ extracts decisions and rationale → docs/vault/...
          └─→ records basename in specs/digested.txt

docs/vault/  (curated, permanent, cross-linked Obsidian vault)
```

**Hooks** reinforce the system automatically:

| Hook                               | Trigger                          | Effect                                                              |
| ---------------------------------- | -------------------------------- | ------------------------------------------------------------------- |
| `memory_session_start_reminder.py` | Session start + after compaction | Injects memory instructions — no CLAUDE.md edit needed              |
| `memory_search_reminder.py`        | Every user prompt                | Reminds Claude to invoke `memory-search` before non-trivial tasks   |
| `memory_log_reminder.py`           | Every user prompt                | Reminds Claude to create/update the daily log before responding     |
| `memory_pre_agent_reminder.py`     | Before any sub-agent             | Reminds Claude to include vault context in the sub-agent prompt     |
| `memory_stop_reminder.py`          | End of every response            | Reminds Claude to log decisions/errors before the session closes    |
| `memory_pre_compact_reminder.py`   | Before context compaction        | Reminds Claude to persist the daily log before history is discarded |
| `memory_post_compact_reminder.py`  | After context compaction         | Reminds Claude to re-read base vault documents to restore context   |

---

## Installation

Install the plugin with a single command inside Claude Code:

```
/plugin install github.com/reduardo7/claude-project-memory
```

This installs the `/memory-digest` slash command, the three sub-agents (`memory-search`, `memory-digest-daily`, `memory-digest-spec`), and wires all hooks automatically.

**After installing the plugin**, complete the project setup:

### Step 1 — Initialize the project structure

```bash
uv run ~/.claude/plugins/long-term-memory/install.py /path/to/your-project
```

This creates `memory/daily/`, `docs/vault/`, and copies the operating instructions into your project. Existing files are never overwritten.

### Step 2 — Customize for your project

See [Customization](#customization) below.

---

## Usage

### During a session

Claude automatically records significant work in `memory/daily/<timestamp>.md`:

- Technical decisions → `## Decisions`
- User corrections → `## Errors and corrections`
- New discoveries → `## Learnings`
- Files touched → `## References`

You don't need to do anything — hooks and `CLAUDE.md` instructions handle this.

### Running `/memory-digest`

After one or more sessions, run:

```
/memory-digest
```

Claude will:

1. Process each `memory/daily/*.md` log with the `memory-digest-daily` sub-agent
2. Process any undigested files in `specs/*.md` with the `memory-digest-spec` sub-agent
3. Write durable knowledge to `docs/vault/`
4. Update relevant skill files in `.claude/skills/`
5. Create a git commit with all changes
6. Delete the processed daily logs

### Searching the vault

Before non-trivial tasks, Claude automatically invokes the `memory-search` sub-agent (triggered by the `UserPromptSubmit` hook). You can also invoke it manually:

```
Agent(subagent_type: "memory-search", prompt: "<task description>")
```

---

## Customization

### Vault language

The sub-agents are configured to maintain the vault's established language (they check existing documents and match the language already in use). To enforce a specific language, edit the language instruction in Step 4 of `.claude/agents/memory-digest-daily.md` and `.claude/agents/memory-digest-spec.md`.

### Vault root path

The default vault path is `docs/vault/`. To change it, update all references in:

- `memory/memory.md`
- `.claude/agents/memory-digest-daily.md`
- `.claude/agents/memory-digest-spec.md`
- `.claude/agents/memory-search.md`

### Conditional docs

Edit `.claude/commands/conditional-docs.md` — add entries that map your project's task types to the specific vault documents Claude should read before working on them.

### Skills table

Open `.claude/agents/memory-digest-daily.md` and `.claude/agents/memory-digest-spec.md`. Find the **Skills table** in Step 6 and replace the generic entries with your project's actual skill files (`.claude/skills/*/SKILL.md`).

### Specs pipeline

The specs pipeline (`specs/*.md` → `memory-digest-spec`) is optional. If you don't use spec files, remove steps 3 and 4 from `skills/memory-digest/SKILL.md`.

### Python interpreter

Hooks use `uv run` by default. To use plain `python3` instead, replace `uv run` with `python3` in each hook command in `.claude/settings.json`.

---

## File reference

| File                                             | Purpose                                                                      |
| ------------------------------------------------ | ---------------------------------------------------------------------------- |
| `.claude-plugin/plugin.json`                     | Plugin manifest — enables `/plugin install`                                  |
| `skills/memory-digest/SKILL.md`                  | `/memory-digest` slash command (plugin format)                               |
| `.claude-plugin/marketplace.json`                | Plugin marketplace registration                                              |
| `memory/memory.md`                               | Operating instructions for Claude — what to record, when, and in what format |
| `memory/daily/*.md`                              | Raw session logs — ephemeral, deleted after `/memory-digest`                 |
| `docs/vault/Home.md`                             | Vault master index — update as vault grows                                   |
| `docs/vault/Claude/Memory.md`                    | Memory system documentation in the vault                                     |
| `docs/vault/Decisions/Index.md`                  | ADR index — updated after every architectural decision                       |
| `docs/vault/Development/Obsidian Vault.md`       | Vault writing conventions (naming, wikilinks)                                |
| `.claude/commands/conditional-docs.md`           | Maps task types to vault documents — customize per project                   |
| `.claude/agents/memory-digest-daily.md`          | Sub-agent: distills one daily log → vault + skills                           |
| `.claude/agents/memory-digest-spec.md`           | Sub-agent: distills one spec file → vault + skills                           |
| `.claude/agents/memory-search.md`                | Sub-agent: retrieves vault docs before tasks                                 |
| `.claude/hooks/memory_session_start_reminder.py` | SessionStart + PostCompact hook: injects memory instructions automatically   |
| `.claude/hooks/memory_search_reminder.py`        | UserPromptSubmit hook: reminds Claude to search vault                        |
| `.claude/hooks/memory_log_reminder.py`           | UserPromptSubmit hook: reminds Claude to update daily log before responding  |
| `.claude/hooks/memory_pre_agent_reminder.py`     | PreToolUse[Agent] hook: reminds Claude to pass vault context                 |
| `.claude/hooks/memory_stop_reminder.py`          | Stop hook: reminds Claude to update session log                              |
| `.claude/hooks/memory_pre_compact_reminder.py`   | PreCompact hook: reminds Claude to persist daily log before compaction       |
| `.claude/hooks/memory_post_compact_reminder.py`  | PostCompact hook: reminds Claude to re-read vault after compaction           |
| `install.py`                                     | Bootstrap script — creates directories and copies files into your project    |

---

## Requirements

- Claude Code with hooks and plugin support
- Python 3.11+
- [`uv`](https://docs.astral.sh/uv/getting-started/installation/) — used to run the Python hook scripts

  ```bash
  curl -LsSf https://astral.sh/uv/install.sh | sh
  ```

  > If you prefer not to install `uv`, replace `uv run` with `python3` in every hook command inside `.claude/settings.json`.
