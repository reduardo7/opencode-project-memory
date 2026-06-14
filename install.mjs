#!/usr/bin/env node
/**
 * Bootstrap script — installs opencode-project-memory into a target project.
 *
 * Usage:
 *   node install.mjs /path/to/target-project
 *
 * What it does:
 *   - Copies the plugin tooling (`.opencode/plugin`, `command`, `agent`, `skills`)
 *     into the target so the project is self-contained and committable for the team.
 *     Tooling files are plugin-managed and are overwritten on re-install so updates
 *     propagate — customize the vault and AGENTS.md, not `.opencode/`.
 *   - Scaffolds the data directories (`memory/daily`, `specs`) and the vault
 *     (`docs/vault/`), copying vault templates only when missing so project
 *     customizations are preserved across re-runs.
 *
 * Zero dependencies — runs on Node 18+ (and Bun), no Python / uv required.
 */

import { cp, mkdir, stat, writeFile, readFile, readdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const SRC = path.dirname(fileURLToPath(import.meta.url));

// Tooling copied verbatim (overwritten on re-install).
const TOOLING = [
  ".opencode/plugin",
  ".opencode/command",
  ".opencode/agent",
  ".opencode/skills",
];

// Directories scaffolded in the target project.
const DIRS = [
  "memory/daily",
  "specs",
  "docs/vault/OpenCode",
  "docs/vault/Decisions",
  "docs/vault/Architecture",
  "docs/vault/Development",
  "docs/vault/Project",
];

// Vault templates copied only when missing.
const VAULT_TEMPLATES = [
  "docs/vault/Home.md",
  "docs/vault/OpenCode/Memory.md",
  "docs/vault/Architecture/Database.md",
  "docs/vault/Architecture/Project Structure.md",
  "docs/vault/Decisions/Index.md",
  "docs/vault/Development/Obsidian Vault.md",
  "docs/vault/Development/Expected Behaviors.md",
];

async function exists(p) {
  try {
    await stat(p);
    return true;
  } catch {
    return false;
  }
}

async function copyMissing(src, dst) {
  if (await exists(dst)) {
    console.log(`  SKIP (exists): ${dst}`);
    return;
  }
  await mkdir(path.dirname(dst), { recursive: true });
  await cp(src, dst);
  console.log(`  CREATED: ${dst}`);
}

async function touchKeep(dir) {
  const keep = path.join(dir, ".gitkeep");
  if (!(await exists(keep))) await writeFile(keep, "");
}

async function mergeOpencodeJson(target) {
  const cfgPath = path.join(target, "opencode.json");
  const instructionsGlob = ".opencode/skills/*/SKILL.md";
  if (!(await exists(cfgPath))) {
    const cfg = {
      $schema: "https://opencode.ai/config.json",
      instructions: ["docs/vault/Home.md"],
    };
    await writeFile(cfgPath, JSON.stringify(cfg, null, 2) + "\n");
    console.log(`  CREATED: ${cfgPath}`);
    return;
  }
  console.log(
    `  SKIP (exists): ${cfgPath} — ensure "instructions" includes "docs/vault/Home.md" if you want the vault index auto-loaded.`
  );
}

async function main() {
  const targetArg = process.argv[2];
  if (!targetArg) {
    console.error("Usage: node install.mjs /path/to/target-project");
    process.exit(1);
  }

  const target = path.resolve(targetArg);
  if (!(await exists(target))) {
    console.error(`Error: target directory '${target}' does not exist`);
    process.exit(1);
  }

  if (path.resolve(SRC) === target) {
    console.error("Error: target is the plugin source itself — choose a different project directory.");
    process.exit(1);
  }

  console.log(`Installing opencode-project-memory into: ${target}\n`);

  console.log("→ Copying plugin tooling (.opencode/)");
  for (const rel of TOOLING) {
    const src = path.join(SRC, rel);
    if (!(await exists(src))) continue;
    const dst = path.join(target, rel);
    await mkdir(path.dirname(dst), { recursive: true });
    await cp(src, dst, { recursive: true, force: true });
    console.log(`  COPIED: ${rel}`);
  }

  console.log("→ Creating data and vault directories");
  for (const sub of DIRS) {
    await mkdir(path.join(target, sub), { recursive: true });
  }
  await touchKeep(path.join(target, "memory/daily"));
  await touchKeep(path.join(target, "specs"));

  console.log("→ Copying docs/vault/ (skipping existing files)");
  for (const f of VAULT_TEMPLATES) {
    await copyMissing(path.join(SRC, f), path.join(target, f));
  }

  console.log("→ Ensuring opencode.json");
  await mergeOpencodeJson(target);

  console.log("\nInstallation complete.\n");
  console.log("Next steps:");
  console.log("  1. Customize docs/vault/Home.md for your project.");
  console.log("  2. Commit .opencode/, docs/vault/, memory/, and specs/ so the team shares the memory system.");
  console.log("  3. Restart OpenCode in the project so it loads the new plugin, agents, and commands.\n");
  console.log("See README.md for full details.");
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
