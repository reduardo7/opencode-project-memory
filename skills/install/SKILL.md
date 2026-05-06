---
name: install
description: Install claude-project-memory into the current project. Ensures `uv` is available (installing it if needed), then runs `install.py` with the current project directory as the target.
version: 1.0.0
model: sonnet
allowed-tools: ["Bash"]
---

Install **claude-project-memory** into the current project by running `install.py` with the project directory as the target.

---

## Procedure

### Step 1 — Resolve paths

Run the following in a single Bash call to collect all required values:

```bash
echo "OS=$(uname -s 2>/dev/null || echo Windows)"
echo "PROJECT_DIR=$(pwd)"
echo "UV_AVAILABLE=$(command -v uv >/dev/null 2>&1 && echo yes || echo no)"
```

> On Windows (PowerShell), `uname` may not exist — the `|| echo Windows` fallback handles that.
> Capture `PROJECT_DIR` (the current working directory — this is the install target).

To locate the `install.py` script, try the following in order until one succeeds:

1. Check `$CLAUDE_PLUGIN_ROOT/install.py` (set by Claude Code when running plugin skills).
2. Check `~/.claude/plugins/claude-project-memory/install.py` (default plugin install path).
3. Use `find ~ -maxdepth 6 -name "install.py" -path "*/claude-project-memory/*" 2>/dev/null | head -1` to search.

Store the resolved path as `INSTALL_SCRIPT`.

If `INSTALL_SCRIPT` cannot be found, abort and inform the user:

> `install.py` was not found. Make sure the `claude-project-memory` plugin is installed via `/plugin install github.com/reduardo7/claude-project-memory`.

---

### Step 2 — Ensure `uv` is installed

If `UV_AVAILABLE` is `yes`, skip this step.

Otherwise install `uv` based on the detected OS:

**macOS / Linux** (OS is not `Windows`):

```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

Then reload the shell environment so `uv` is on `PATH`:

```bash
export PATH="$HOME/.local/bin:$HOME/.cargo/bin:$PATH"
```

**Windows** (OS is `Windows`):

```powershell
powershell -ExecutionPolicy ByPass -c "irm https://astral.sh/uv/install.ps1 | iex"
```

After installation, verify `uv` is now available:

```bash
uv --version
```

If verification fails, abort and ask the user to install `uv` manually:

> `uv` could not be installed automatically. Install it from [docs.astral.sh/uv](https://docs.astral.sh/uv/getting-started/installation/) and then re-run `/claude-project-memory:install`.

---

### Step 3 — Run `install.py`

Execute:

```bash
uv run "$INSTALL_SCRIPT" "$PROJECT_DIR"
```

Capture and display all output verbatim so the user sees exactly what was created or skipped.

---

### Step 4 — Report

After the script completes, show the user:

- Whether `uv` was already present or was installed.
- The full output from `install.py` (files created / skipped).
- The next steps printed by the script (customize `docs/vault/Home.md`, update the skills table in `skills/memory-digest-daily/SKILL.md`).

If the script exits with a non-zero code, report the error output and ask the user to check their environment.
