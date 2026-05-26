---
tags: [architecture, structure, plugin]
summary: Estructura de directorios y responsabilidades de cada componente del plugin claude-project-memory
---

# Project Structure

Plugin structure for `claude-project-memory`. Installed into target projects via `/plugin install` or `install.py`.

See also: [[Claude/Memory]] | [[Development/Obsidian Vault]]

---

## Plugin source layout

```
claude-project-memory/
├── .claude-plugin/
│   ├── plugin.json              ← plugin manifest (name, version, requirements)
│   └── marketplace.json         ← plugin marketplace registration
│
├── hooks/                       ← Python hooks; run from plugin root via ${CLAUDE_PLUGIN_ROOT}
│   ├── hooks.json               ← event → script mappings (used by /plugin install)
│   ├── memory_session_start_reminder.py
│   ├── memory_search_reminder.py
│   ├── memory_log_reminder.py
│   ├── memory_pre_agent_reminder.py
│   ├── memory_stop_reminder.py
│   ├── memory_pre_compact_reminder.py
│   └── memory_post_compact_reminder.py
│
├── skills/                      ← slash commands and sub-agent skills
│   ├── memory/SKILL.md          ← operating instructions (mandatory reading)
│   ├── digest/SKILL.md   ← /claude-project-memory:digest orchestrator
│   ├── digest-daily/SKILL.md  ← sub-agent: processes one memory/daily/ file
│   ├── digest-spec/SKILL.md   ← sub-agent: processes one specs/ file
│   ├── search/SKILL.md   ← sub-agent: retrieves vault docs before tasks
│   ├── obsidian-vault/SKILL.md  ← vault writing rules (invoked by digest sub-agents)
│   └── install/SKILL.md         ← /claude-project-memory:install slash command
│
├── docs/vault/                  ← template vault copied to target project by install.py
│   ├── Home.md
│   ├── Claude/Memory.md
│   ├── Architecture/Database.md
│   ├── Architecture/Project Structure.md
│   ├── Decisions/Index.md
│   ├── Development/Obsidian Vault.md
│   ├── Development/Expected Behaviors.md
│   └── Project/                 ← empty placeholder; customized per project
│
├── .claude/
│   └── settings.json
│
├── memory/daily/.gitkeep        ← template for session log directory
├── install.py                   ← bootstrap script
├── CLAUDE.md
└── README.md
```

---

## What `install.py` creates in the target project

| Path | How | Notes |
|------|-----|-------|
| `memory/daily/` | `mkdir` | Session log directory |
| `specs/` | `mkdir` | Implementation specs (immutable) |
| `docs/vault/{Claude,Decisions,Architecture,Development,Project}/` | `mkdir` | Vault subdirectories |
| `.claude/commands/` | `mkdir` | Claude commands directory |
| `docs/vault/**/*.md` (7 templates) | `copy_if_missing` | Skips existing files |

**Not created by `install.py`:**
- `.claude/rules/` — created on demand by Step 7 of digest sub-agents
- `.claude/hooks/` — hooks run from `${CLAUDE_PLUGIN_ROOT}/hooks/`, not copied to the target

---

## Runtime requirements

- Python ≥ 3.11
- `uv` (for hook execution)
