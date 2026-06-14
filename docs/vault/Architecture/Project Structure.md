---
tags: [architecture, structure, plugin]
summary: Estructura de directorios y responsabilidades de cada componente del plugin opencode-project-memory
---

# Project Structure

Plugin structure for `opencode-project-memory`. Installed into target projects via `install.mjs` (or by copying `.opencode/` into `~/.config/opencode/`).

See also: [[OpenCode/Memory]] | [[Development/Obsidian Vault]]

---

## Plugin source layout

```
opencode-project-memory/
├── opencode.json                ← project config (instructions glob, schema)
├── AGENTS.md                    ← project instructions (source of truth for this repo)
│
├── .opencode/
│   ├── plugin/
│   │   └── memory.js            ← the plugin — all memory hooks in one module
│   ├── command/
│   │   ├── digest.md            ← /digest orchestrator
│   │   └── install.md           ← /install slash command
│   ├── agent/
│   │   ├── memory-search.md     ← subagent: retrieves vault docs before tasks
│   │   ├── memory-digest-daily.md ← subagent: processes one memory/daily/ file
│   │   └── memory-digest-spec.md  ← subagent: processes one specs/ file
│   └── skills/
│       ├── memory/SKILL.md      ← operating instructions
│       ├── memory/context.md    ← rules injected by the plugin into the system prompt
│       ├── digest-rules/SKILL.md  ← vault-writing rules (loaded by digest subagents)
│       └── obsidian-vault/SKILL.md ← vault naming/wikilink/size conventions
│
├── docs/vault/                  ← template vault copied to target project by install.mjs
│   ├── Home.md
│   ├── OpenCode/Memory.md
│   ├── Architecture/Database.md
│   ├── Architecture/Project Structure.md
│   ├── Decisions/Index.md
│   ├── Development/Obsidian Vault.md
│   ├── Development/Expected Behaviors.md
│   └── Project/                 ← empty placeholder; customized per project
│
├── memory/daily/.gitkeep        ← template for session log directory
├── install.mjs                  ← bootstrap script (Node/Bun, zero-dependency)
└── README.md
```

---

## What `install.mjs` creates in the target project

| Path | How | Notes |
|------|-----|-------|
| `.opencode/{plugin,command,agent,skills}/` | copy (overwrite) | Plugin-managed tooling — overwritten on re-install so updates propagate |
| `memory/daily/` | `mkdir` + `.gitkeep` | Session log directory |
| `specs/` | `mkdir` + `.gitkeep` | Implementation specs (immutable) |
| `docs/vault/{OpenCode,Decisions,Architecture,Development,Project}/` | `mkdir` | Vault subdirectories |
| `docs/vault/**/*.md` (7 templates) | copy if missing | Skips existing files (preserves customizations) |
| `opencode.json` | create if missing | Minimal config with `instructions: ["docs/vault/Home.md"]` |

**Not created by `install.mjs`:**
- Nested `AGENTS.md` path rules — created on demand by the digest subagents when a vault doc maps to a code path.

---

## Runtime requirements

- OpenCode (loads `.opencode/plugin/`, `agent/`, `command/`, `skills/` automatically).
- Node 18+ or Bun — only for running `install.mjs`. The plugin itself runs inside OpenCode's runtime; no Python / uv.
