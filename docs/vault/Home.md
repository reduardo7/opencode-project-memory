---
tags: [moc, home]
---

# [Project Name] — Vault

Master content map. Open this vault from `docs/vault/` in Obsidian.

---

## Project

| Note | Description |
|------|-------------|
| [[Project/PRD]] | Product Requirements Document — objectives, business rules, flows |

---

## Architecture

| Note | Description |
|------|-------------|
| [[Architecture/Database]] | Database schema. |
| [[Architecture/Project Structure]] | Plugin directory layout, what `install.mjs` creates, and runtime requirements |

---

## Decisions (ADRs)

> Navigable index of Architecture Decision Records. Rule: every decision with architectural, API contract, data model, or business behavior impact must be recorded here.

| Note | Scope |
|------|-------|
| [[Decisions/Index]] | Master table of all ADRs with number, section, and link |

> Next ADR: **ADR-001**

---

## Development

| Note | Description |
|------|-------------|
| [[Development/Obsidian Vault]] | Vault writing rules and naming conventions |
| [[Development/Expected Behaviors]] | Intentional design decisions that are NOT bugs |

---

## OpenCode

| Note | Description |
|------|-------------|
| [[OpenCode/Memory]] | Long-term memory system — daily log, `/digest`, distillation flow to vault |

---

## Relationship between documentation sources

| Source | Role |
|--------|------|
| **AGENTS.md** | Absolute rules and source of truth — the *what* and the *why* |
| **`docs/vault/Decisions/Index.md`** | ADR index. Consult before implementing; update when completing features |
| **`docs/vault/Home.md`** | This file — master map of all vault content |

---

## What is NOT in the vault

These resources live outside `docs/vault/` and should not be moved:
- `specs/` — implementation specs (immutable historical record)
