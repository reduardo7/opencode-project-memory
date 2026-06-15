/**
 * opencode-project-memory — OpenCode plugin
 *
 * Project-scoped long-term memory system. A single plugin drives all memory
 * behaviors. OpenCode plugins export hook functions that mutate the model's
 * system prompt and the compaction prompt directly (rather than external
 * scripts printing to stdout on lifecycle events).
 *
 * Hooks:
 *   experimental.chat.system.transform -> inject memory context + search/log reminders (every inference)
 *   experimental.session.compacting    -> remind to persist the daily log before history is discarded
 *   tool.execute.before (task)         -> remind subagents to consult the vault first
 *   event: session.idle                -> nudge to update/create the daily log (TUI toast)
 *   event: session.compacted           -> arm the one-shot "re-read base docs" reminder
 *
 * The experimental.* hook surface still moves between OpenCode versions, so
 * every hook body is defensive: optional chaining, array guards, and try/catch
 * so a renamed field degrades gracefully instead of breaking the session.
 */

import { readFile, stat, readdir } from "node:fs/promises";
import path from "node:path";

export const MemoryPlugin = async ({ project, client, directory, worktree, $ }) => {
  const root =
    directory ||
    worktree ||
    project?.worktree ||
    project?.directory ||
    process.cwd();

  // Session IDs that compacted on their previous turn — used to emit the
  // "re-read base docs" reminder exactly once after compaction.
  const justCompacted = new Set();

  // ---- helpers -----------------------------------------------------------

  async function readContext() {
    const candidates = [
      path.join(root, ".opencode", "skills", "memory", "context.md"),
      path.join(root, "skills", "memory", "context.md"),
    ];
    for (const c of candidates) {
      try {
        return (await readFile(c, "utf8")).trim();
      } catch {
        /* try next */
      }
    }
    return null;
  }

  async function hasActiveLog() {
    try {
      const dir = path.join(root, "memory", "daily");
      const files = await readdir(dir);
      return files.some((f) => f.endsWith(".md") && f !== ".gitkeep");
    } catch {
      return false;
    }
  }

  async function hasGitChanges() {
    try {
      const r = await $`git -C ${root} status --porcelain`.quiet().nothrow();
      const out = (r?.stdout ?? "").toString();
      return out.trim().length > 0;
    } catch {
      return false;
    }
  }

  function pushSystem(output, text) {
    // output.system is expected to be an array of strings.
    if (Array.isArray(output?.system)) {
      output.system.push(text);
    } else if (output && typeof output.system === "string") {
      output.system += `\n\n${text}`;
    }
  }

  // ---- static reminder fragments ----------------------------------------

  const SEARCH_REMINDER =
    "<memory-search-reminder>" +
    "Before a non-trivial task (feature work, architectural or schema changes, " +
    "ADR creation/updates, or questions about what already exists in the project), " +
    "retrieve vault context first by delegating to the `memory-search` subagent " +
    "(`@memory-search <task>` or a task() call to it). Skip for trivial questions " +
    "already answered in context." +
    "</memory-search-reminder>";

  const logReminder = (active) =>
    active
      ? "<memory-log-reminder>" +
        "There is an active session log under memory/daily/. As you work, update it " +
        "immediately after each significant event: decisions in ## Decisions, errors " +
        "and user corrections in ## Errors and corrections, discoveries in ## Learnings, " +
        "and touched files/PRs in ## References — never batch for the end." +
        "</memory-log-reminder>"
      : "<memory-log-reminder>" +
        "If this turn involves non-trivial work — decisions, errors and corrections, or " +
        "non-obvious discoveries — create memory/daily/YYYY-MM-DD_HHMMSS.md (see the " +
        "`memory` skill for the format) and record as you go, not at the end." +
        "</memory-log-reminder>";

  const POST_COMPACT_REMINDER =
    "<memory-post-compact-reminder>" +
    "Context was just compacted. Restore the architectural context of the session: " +
    "(1) re-read docs/vault/Home.md and any active memory/daily/ log; " +
    "(2) consult the `memory` skill for the operating rules. " +
    "These hold decisions and conventions that are not in the compacted history." +
    "</memory-post-compact-reminder>";

  // ---- hooks -------------------------------------------------------------

  return {
    /**
     * Runs before every model inference. The memory operating context plus the
     * search and log reminders are injected here, so they are always present and
     * survive compaction for free.
     */
    "experimental.chat.system.transform": async (input, output) => {
      try {
        const ctx = await readContext();
        pushSystem(
          output,
          "<memory-session-instructions>\n" +
            (ctx ??
              "Memory system context not found. Read the `memory` skill " +
                "(.opencode/skills/memory/SKILL.md) and its context.md for the operating rules.") +
            "\n</memory-session-instructions>"
        );

        pushSystem(output, SEARCH_REMINDER);
        pushSystem(output, logReminder(await hasActiveLog()));

        const sid = input?.sessionID ?? input?.sessionId;
        if (sid && justCompacted.has(sid)) {
          justCompacted.delete(sid);
          pushSystem(output, POST_COMPACT_REMINDER);
        }
      } catch {
        /* never break a turn over a reminder */
      }
    },

    /**
     * Fires before context compaction discards conversation history.
     * Mirrors the PreCompact hook: persist the session log before it is lost.
     */
    "experimental.session.compacting": async (_input, output) => {
      try {
        const active = await hasActiveLog();
        const body = active
          ? "update memory/daily/ now with everything relevant from this session — " +
            "Decisions, Errors and corrections, Learnings, References"
          : (await hasGitChanges())
            ? "files were modified but no session log exists — create " +
              "memory/daily/YYYY-MM-DD_HHMMSS.md now with topic, Context, Decisions, " +
              "Errors and corrections, Learnings, References"
            : "if there were decisions, errors, or learnings this session, create " +
              "memory/daily/YYYY-MM-DD_HHMMSS.md now (see the `memory` skill)";
        const text =
          "<memory-pre-compact-reminder>BEFORE COMPACTION: " +
          body +
          ". Compaction will discard the conversation history; anything not in the " +
          "session file is permanently lost.</memory-pre-compact-reminder>";

        if (Array.isArray(output?.context)) {
          output.context.push(text);
        } else if (output && typeof output.prompt === "string") {
          output.prompt = `${text}\n\n${output.prompt}`;
        }
      } catch {
        /* ignore */
      }
    },

    /**
     * Before any subagent launch (the `task` tool), remind it to consult the
     * vault first. Mirrors PreToolUse[Agent]. Memory-system agents already have
     * their own flow, so they are skipped.
     */
    "tool.execute.before": async (input, output) => {
      try {
        if (input?.tool !== "task") return;
        const args = output?.args;
        if (!args) return;

        const blob = JSON.stringify(args);
        if (/memory-(search|digest)/.test(blob)) return; // skip memory agents

        const reminder =
          "<pre-agent-reminder>" +
          "Before you start: if relevant vault documentation has not yet been retrieved " +
          "for this task, consult it (via the `memory-search` subagent) and weave the " +
          "results into your work." +
          "</pre-agent-reminder>\n\n";

        if (typeof args.prompt === "string") {
          args.prompt = reminder + args.prompt;
        } else if (typeof args.description === "string") {
          args.description = reminder + args.description;
        }
      } catch {
        /* ignore */
      }
    },

    /**
     * Event stream. Two events matter:
     *   session.compacted -> arm the one-shot post-compaction reminder.
     *   session.idle      -> Stop-hook equivalent: nudge to persist the log.
     */
    event: async ({ event }) => {
      try {
        const type = event?.type;

        if (type === "session.compacted") {
          const sid =
            event?.properties?.sessionID ??
            event?.properties?.sessionId ??
            event?.properties?.info?.id ??
            event?.sessionID;
          if (sid) justCompacted.add(sid);
          return;
        }

        if (type === "session.idle") {
          const active = await hasActiveLog();
          let message;
          if (active) {
            message =
              "Memory: update memory/daily/ with this session's decisions, errors, and learnings before moving on.";
          } else if (await hasGitChanges()) {
            message =
              "Memory: files changed but no session log exists — create memory/daily/<timestamp>.md.";
          } else {
            message =
              "Memory: record any decisions, errors, or learnings from this session in memory/daily/.";
          }

          // Best-effort TUI toast. The SDK surface varies; try the common shapes.
          try {
            if (client?.tui?.showToast) {
              await client.tui.showToast({ body: { message, variant: "info" } });
            } else if (client?.tui?.toast) {
              await client.tui.toast({ message, variant: "info" });
            }
          } catch {
            /* toast is optional */
          }
        }
      } catch {
        /* ignore */
      }
    },
  };
};
