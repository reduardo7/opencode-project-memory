# Installation Guide

## For Humans (agent-assisted)

Paste this into your LLM agent session (Claude Code, AmpCode, Cursor, OpenCode, etc.):

```
Install and configure opencode-project-memory by following the instructions here:
https://raw.githubusercontent.com/reduardo7/opencode-project-memory/refs/heads/main/docs/guide/installation.md
```

Your agent will read this document and handle the setup for you.

---

## Manual installation

### Prerequisites

- [OpenCode](https://opencode.ai) with plugin support (v1.0.132+)
- Node 18+ or Bun — only needed to run `install.mjs`

### Step 0: Verify OpenCode is installed

```bash
if command -v opencode &> /dev/null; then
    echo "OpenCode $(opencode --version) is installed"
else
    echo "OpenCode is not installed. Please install it first: https://opencode.ai/docs"
fi
```

### Step 1: Clone this repo

```bash
git clone https://github.com/reduardo7/opencode-project-memory
```

### Step 2: Run the bootstrap script

Point it at your target project directory:

```bash
node opencode-project-memory/install.mjs /path/to/your-project
```

This copies the plugin tooling (`.opencode/plugin`, `command`, `agent`, `skills`) into your project and scaffolds `memory/daily/`, `specs/`, and `docs/vault/`. Tooling files are overwritten on re-install so updates propagate; existing vault files are never overwritten.

### Step 3: Customize for your project

1. Edit `docs/vault/Home.md` in your target project — replace `[Project Name]` and tailor the sections.
2. Commit `.opencode/`, `docs/vault/`, `memory/`, and `specs/` so the team shares the memory system.

```bash
cd /path/to/your-project
git add .opencode/ docs/vault/ memory/ specs/
git commit -m "Add opencode-project-memory system"
```

### Step 4: Restart OpenCode

```bash
opencode
```

OpenCode must restart to load the new plugin, agents, and commands.

### Step 5: Verify the setup

```bash
# Check the plugin is loaded
ls .opencode/plugin/memory.js
# Check the vault was scaffolded
ls docs/vault/Home.md
# Check the memory directory
ls memory/daily/.gitkeep
```

---

## Global installation

Copy this repo's `.opencode/` contents into `~/.config/opencode/` so the plugin, agents, commands, and skills are available in every project:

```bash
cp -r opencode-project-memory/.opencode/* ~/.config/opencode/
```

Then run `/install` (or `node install.mjs <dir>`) inside each project to scaffold its `memory/`, `specs/`, and vault.

---

## Post-install

Once installed, the memory system works automatically:

- **During sessions**: the agent records decisions, corrections, and discoveries in `memory/daily/`.
- **After sessions**: run `/digest` to distill raw logs into the curated vault.
- **Before non-trivial tasks**: the agent automatically consults the vault via `@memory-search`.

See the [README](../../README.md) for full usage details.
