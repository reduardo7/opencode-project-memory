---
description: Install opencode-project-memory (scaffolding + vault) into the current project.
agent: build
---

Install **opencode-project-memory** into the current project by running `install.mjs` with the project directory as the target.

---

## Procedure

### Step 1 — Resolve paths

Run the following in a single shell call to collect the required values:

```bash
echo "PROJECT_DIR=$(pwd)"
echo "NODE=$(command -v node >/dev/null 2>&1 && echo yes || echo no)"
echo "BUN=$(command -v bun >/dev/null 2>&1 && echo yes || echo no)"
```

Capture `PROJECT_DIR` (the current working directory — this is the install target).

To locate the `install.mjs` script, try the following in order until one succeeds:

1. `.opencode/install.mjs` and `install.mjs` in the current project (if the plugin source was cloned here).
2. The global OpenCode config: `~/.config/opencode/install.mjs`.
3. Search: `find ~ -maxdepth 6 -name "install.mjs" -path "*opencode-project-memory*" 2>/dev/null | head -1`.

Store the resolved path as `INSTALL_SCRIPT`.

If `INSTALL_SCRIPT` cannot be found, abort and tell the user to clone the plugin repo and run `node install.mjs <project-dir>` manually, or to copy the repo's `.opencode/` directory into the project.

### Step 2 — Run the installer

Prefer `node`; fall back to `bun` if Node is unavailable:

```bash
node "$INSTALL_SCRIPT" "$PROJECT_DIR"   # or: bun "$INSTALL_SCRIPT" "$PROJECT_DIR"
```

Capture and display all output verbatim so the user sees exactly what was created or skipped.

### Step 3 — Report

After the script completes, show the user:

- The full output from `install.mjs` (files created / copied / skipped).
- The next steps printed by the script (customize `docs/vault/Home.md`; commit `.opencode/`, `docs/vault/`, `memory/`, `specs/`; restart OpenCode so it loads the new plugin, agents, and commands).

If the script exits with a non-zero code, report the error output and ask the user to check their environment (Node 18+ or Bun required).
