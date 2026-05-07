# Claude Project Memory

A long-term memory system for Claude Code. Captures session decisions, errors, and discoveries in raw daily logs, then distills them into a curated Obsidian vault via the `/claude-project-memory:memory-digest` command.

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
  ├─→ [each daily log] → sub-agent from claude-project-memory:memory-digest-daily skill
  │       └─→ extracts durable knowledge → docs/vault/...
  │       └─→ deletes memory/daily/<ts>.md
  │
  └─→ [each undigested spec] → sub-agent from claude-project-memory:memory-digest-spec skill
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

This installs the `/claude-project-memory:memory-digest` slash command, the `/claude-project-memory:install` slash command, the skills used as sub-agents (`claude-project-memory:memory-search`, `claude-project-memory:memory-digest-daily`, `claude-project-memory:memory-digest-spec`), and wires all hooks automatically.

**After installing the plugin**, complete the project setup:

### Step 1 — Initialize the project structure

Open Claude Code inside your target project and run:

```
/claude-project-memory:install
```

This detects the current directory automatically, ensures `uv` is installed (installing it if needed), and runs the bootstrap script. It creates `memory/daily/`, `docs/vault/`, and copies the operating instructions. Existing files are never overwritten.

**Manual alternative** — if you prefer to run the script directly:

```bash
uv run ~/.claude/plugins/claude-project-memory/install.py /path/to/your-project
```

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

### Running `/claude-project-memory:memory-digest`

After one or more sessions, run:

```
/claude-project-memory:memory-digest
```

Claude will:

1. Process each `memory/daily/*.md` log using a sub-agent from the `claude-project-memory:memory-digest-daily` skill
2. Process any undigested files in `specs/*.md` using a sub-agent from the `claude-project-memory:memory-digest-spec` skill
3. Write durable knowledge to `docs/vault/`
4. Update relevant skill files in `.claude/skills/`
5. Create a git commit with all changes
6. Delete the processed daily logs

### Searching the vault

Before non-trivial tasks, Claude automatically creates a sub-agent from the `claude-project-memory:memory-search` skill (triggered by the `UserPromptSubmit` hook). You can also invoke it manually:

```
Agent(subagent_type: "memory-search", prompt: "<task description>")
```

---

## Customization

### Vault language

The sub-agent skills are configured to maintain the vault's established language (they check existing documents and match the language already in use). To enforce a specific language, edit the language instruction in Step 4 of `skills/memory-digest-daily/SKILL.md` and `skills/memory-digest-spec/SKILL.md`.

### Vault root path

The default vault path is `docs/vault/`. To change it, update all references in:

- `skills/memory/SKILL.md`
- `skills/memory-digest-daily/SKILL.md`
- `skills/memory-digest-spec/SKILL.md`
- `skills/memory-search/SKILL.md`

### Conditional docs

Edit `.claude/commands/conditional-docs.md` — add entries that map your project's task types to the specific vault documents Claude should read before working on them.

### Specs pipeline

The specs pipeline (`specs/*.md` → `claude-project-memory:memory-digest-spec`) is optional. If you don't use spec files, remove steps 3 and 4 from `skills/memory-digest/SKILL.md`.

### Python interpreter

Hooks use `uv run` by default. To use plain `python3` instead, replace `uv run` with `python3` in each hook command in `.claude/settings.json`.

---

## File reference

| File                                             | Purpose                                                                      |
| ------------------------------------------------ | ---------------------------------------------------------------------------- |
| `.claude-plugin/plugin.json`                     | Plugin manifest — enables `/plugin install`                                  |
| `skills/memory/SKILL.md`                         | Operating instructions for Claude — what to record, when, and in what format |
| `skills/memory-digest/SKILL.md`                  | `/memory-digest` slash command (plugin format)                               |
| `skills/memory-digest-daily/SKILL.md`            | Skill used as sub-agent: distills one daily log → vault + skills             |
| `skills/memory-digest-spec/SKILL.md`             | Skill used as sub-agent: distills one spec file → vault + skills             |
| `skills/memory-search/SKILL.md`                  | Skill used as sub-agent: retrieves vault docs before tasks                   |
| `skills/install/SKILL.md`                        | `/install` slash command: bootstraps the plugin into the current project     |
| `.claude-plugin/marketplace.json`                | Plugin marketplace registration                                              |
| `memory/daily/*.md`                              | Raw session logs — ephemeral, deleted after `/memory-digest`                 |
| `docs/vault/Home.md`                             | Vault master index — update as vault grows                                   |
| `docs/vault/Claude/Memory.md`                    | Memory system documentation in the vault                                     |
| `docs/vault/Decisions/Index.md`                  | ADR index — updated after every architectural decision                       |
| `docs/vault/Development/Obsidian Vault.md`       | Vault writing conventions (naming, wikilinks)                                |
| `.claude/commands/conditional-docs.md`           | Maps task types to vault documents — customize per project                   |
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
