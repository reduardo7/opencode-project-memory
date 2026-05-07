#!/usr/bin/env -S uv run --script
# /// script
# requires-python = ">=3.11"
# dependencies = []
# ///

"""
UserPromptSubmit hook — injects a proactive reminder to create or update
the daily session log before responding to non-trivial tasks.

Fires at prompt submission (before Claude responds), so the reminder
arrives early enough to act on — unlike the Stop hook which arrives
after the work is done.

Reads the incoming prompt from stdin JSON and uses keyword heuristics
to skip trivial interactions (simple questions, clarifications).
"""

import glob
import json
import os
import sys

ACTION_KEYWORDS = {
    "implement", "add", "fix", "create", "change", "modify", "refactor",
    "update", "build", "write", "debug", "migrate", "remove", "delete",
    "move", "rename", "configure", "integrate", "deploy", "test", "review",
    "analyze", "investigate", "design", "convert", "parse", "generate",
    "install", "setup", "set up", "initialize", "init", "enable", "disable",
    "replace", "rewrite", "extract", "introduce", "improve", "optimize",
    "hacer", "agregar", "añadir", "crear", "cambiar", "modificar", "refactorizar",
    "actualizar", "construir", "escribir", "depurar", "migrar", "eliminar",
    "mover", "renombrar", "configurar", "integrar", "desplegar", "probar",
    "revisar", "analizar", "diseñar", "convertir", "generar", "instalar",
    "inicializar", "habilitar", "deshabilitar", "reemplazar", "reescribir",
    "introducir", "mejorar", "optimizar",
}

TRIVIAL_STARTERS = (
    "what is", "what are", "what does", "what do",
    "how does", "how do", "how is", "how are",
    "why does", "why do", "why is", "why are",
    "where is", "where are", "who is", "when is",
    "explain", "describe", "list", "show me", "tell me",
    "can you explain", "could you explain",
    "qué es", "qué son", "cómo funciona", "cómo se", "por qué",
    "dónde está", "dónde están", "explica", "describe", "lista",
    "muéstrame", "qué hace",
)


def is_nontrivial(prompt: str) -> bool:
    lower = prompt.lower().strip()

    if any(lower.startswith(starter) for starter in TRIVIAL_STARTERS):
        return False

    words = set(lower.split())
    if words & ACTION_KEYWORDS:
        return True

    # Multi-word phrases
    for kw in ACTION_KEYWORDS:
        if " " in kw and kw in lower:
            return True

    return False


def main():
    try:
        raw = sys.stdin.read()
        data = json.loads(raw) if raw.strip() else {}
        prompt = data.get("prompt", "")
    except Exception:
        prompt = ""

    if not is_nontrivial(prompt):
        sys.exit(0)

    project_dir = os.environ.get("CLAUDE_PROJECT_DIR", "")
    daily_dir = os.path.join(project_dir, "memory", "daily") if project_dir else ""

    if daily_dir:
        existing = [f for f in glob.glob(os.path.join(daily_dir, "*.md"))
                    if not f.endswith(".gitkeep")]
        has_log = bool(existing)
    else:
        has_log = False

    if has_log:
        reminder = (
            "<memory-log-reminder>"
            "This looks like a non-trivial task. There is an active session log in "
            "memory/daily/ — update it as you work: record decisions in ## Decisions, "
            "errors in ## Errors and corrections, and findings in ## Learnings. "
            "Update immediately after each significant event, not at the end."
            "</memory-log-reminder>"
        )
    else:
        reminder = (
            "<memory-log-reminder>"
            "This looks like a non-trivial task. If you make decisions, hit errors, "
            "or discover non-obvious findings, create a session log in "
            "memory/daily/YYYY-MM-DD_HHMMSS.md (see the claude-project-memory:memory skill for the format)"
            "as you work — not at the end."
            "</memory-log-reminder>"
        )

    print(reminder)
    sys.exit(0)


if __name__ == "__main__":
    main()
