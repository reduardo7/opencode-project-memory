# OpenCode Project Memory

A long-term memory system for [OpenCode](https://opencode.ai). Captures session decisions, errors, and discoveries in raw daily logs, then distills them into a curated Obsidian vault via the `/digest` command.

### Why this approach is different

Most memory systems store knowledge **per-user**, in a global location on the developer's machine. This system stores memory **inside the repository** — in `docs/vault/` — which means:

- **Shared across the team**: every developer who clones the repo inherits the accumulated context — past decisions, known pitfalls, architectural rationale.
- **Versioned in git**: the knowledge base evolves alongside the code, and its history is fully auditable.
- **Obsidian-compatible**: the vault uses wikilinks and bidirectional links, making it navigable as a knowledge graph — not just a flat log dump.
- **Gets smarter over time**: each session adds context; the agent's answers improve as the vault grows, for everyone on the team.

This makes the memory a **project asset**, not a personal one.

---

## How it works

```
Session work
  └─→ memory/daily/<timestamp>.md   (raw, ephemeral — the agent writes in real time)

/digest  (orchestrator command)
  ├─→ [each daily log] → memory-digest-daily subagent
  │       └─→ extracts durable knowledge → docs/vault/...
  │       └─→ deletes memory/daily/<ts>.md
  │
  └─→ [each undigested spec] → memory-digest-spec subagent
          └─→ extracts decisions and rationale → docs/vault/...
          └─→ records basename in specs/digested.txt

docs/vault/  (curated, permanent, cross-linked Obsidian vault)
```

**The plugin** (`.opencode/plugin/memory.js`) reinforces the system automatically. Where Claude Code needed seven separate hooks, OpenCode's hook model collapses them into one module:

| OpenCode hook | Effect |
| --- | --- |
| `experimental.chat.system.transform` | Injects the memory operating context, the search reminder, the log reminder, and (once after compaction) a re-read-base-docs reminder — into the system prompt on every inference |
| `experimental.session.compacting` | Reminds the agent to persist the daily log before compaction discards history |
| `tool.execute.before` (`task`) | Prepends a vault-consult reminder to any subagent it launches (memory-system agents skipped) |
| `event` → `session.idle` | TUI toast: update/create the daily log if there was significant work |
| `event` → `session.compacted` | Arms the one-shot re-read-base-docs reminder |

---

## Installation

### Per-project (recommended)

Clone this repo, then run the bootstrap script against your target project:

```bash
git clone https://github.com/reduardo7/opencode-project-memory
node opencode-project-memory/install.mjs /path/to/your-project
```

This copies the plugin tooling (`.opencode/plugin`, `command`, `agent`, `skills`) into your project and scaffolds `memory/daily/`, `specs/`, and `docs/vault/`. Tooling files are overwritten on re-install so updates propagate; existing vault files are never overwritten.

Then **restart OpenCode** in the project so it loads the new plugin, agents, and commands.

> Requires Node 18+ or Bun. No Python / uv.

### Global

Copy this repo's `.opencode/` contents into `~/.config/opencode/` so the plugin, agents, commands, and skills are available in every project. Then run `/install` (or `node install.mjs <dir>`) inside each project to scaffold its `memory/`, `specs/`, and vault.

### Customize for your project

1. Edit `docs/vault/Home.md` — replace `[Project Name]` and tailor the sections.
2. Commit `.opencode/`, `docs/vault/`, `memory/`, and `specs/` so the team shares the memory system.

---

## Usage

### During a session

The agent automatically records significant work in `memory/daily/<timestamp>.md`:

- Technical decisions → `## Decisions`
- User corrections → `## Errors and corrections`
- New discoveries → `## Learnings`
- Files touched → `## References`

You don't need to do anything — the plugin and `AGENTS.md` instructions handle this.

### Running `/digest`

After one or more sessions, run:

```
/digest
```

The orchestrator will:

1. Process each `memory/daily/*.md` log with the `memory-digest-daily` subagent.
2. Process any undigested files in `specs/*.md` with the `memory-digest-spec` subagent.
3. Write durable knowledge to `docs/vault/`.
4. Update relevant skill files in `.opencode/skills/` and any nested `AGENTS.md` path rules.
5. Create a local git commit with all changes.
6. Delete the processed daily logs.

### Searching the vault

Before non-trivial tasks, delegate to the read-only retrieval subagent:

```
@memory-search <task description>
```

The plugin also reminds the agent to do this automatically before non-trivial work.

---

## Customization

### Vault language

The digest subagents maintain the vault's established language (they check existing documents and match what is already in use). To enforce a specific language, edit the language instruction in the `digest-rules` skill (`.opencode/skills/digest-rules/SKILL.md`).

### Subagent model

The subagents default to `anthropic/claude-haiku-4-5` for cost. Change the `model:` frontmatter in `.opencode/agent/*.md` to use a different provider/model.

### Vault root path

The default vault path is `docs/vault/`. To change it, update the references in the `.opencode/skills/`, `.opencode/agent/`, and `.opencode/command/` files.

### Specs pipeline

The specs pipeline (`specs/*.md` → `memory-digest-spec`) is optional. If you don't use spec files, remove steps 3 and 4 from `.opencode/command/digest.md`.

---

## File reference

| File | Purpose |
| ---- | ------- |
| `.opencode/plugin/memory.js` | The plugin — all memory hooks in one module |
| `.opencode/command/digest.md` | `/digest` slash command (orchestrator) |
| `.opencode/command/install.md` | `/install` slash command |
| `.opencode/agent/memory-search.md` | Subagent: retrieves vault docs before tasks |
| `.opencode/agent/memory-digest-daily.md` | Subagent: distills one daily log → vault |
| `.opencode/agent/memory-digest-spec.md` | Subagent: distills one spec → vault |
| `.opencode/skills/memory/` | Operating instructions (SKILL.md + context.md) |
| `.opencode/skills/digest-rules/SKILL.md` | Shared vault-writing rules |
| `.opencode/skills/obsidian-vault/SKILL.md` | Vault naming/wikilink/size conventions |
| `memory/daily/*.md` | Raw session logs — ephemeral, deleted after `/digest` |
| `docs/vault/Home.md` | Vault master index — update as the vault grows |
| `docs/vault/OpenCode/Memory.md` | Memory system documentation in the vault |
| `docs/vault/Decisions/Index.md` | ADR index — updated after every architectural decision |
| `docs/vault/Development/Obsidian Vault.md` | Vault writing conventions (naming, wikilinks) |
| `opencode.json` | Project config — `instructions` glob, schema |
| `install.mjs` | Bootstrap script — copies tooling + scaffolds your project |

---

## Requirements

- [OpenCode](https://opencode.ai) with plugin support.
- Node 18+ or Bun — only to run `install.mjs`.
