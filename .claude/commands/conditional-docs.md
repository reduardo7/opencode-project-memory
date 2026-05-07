# Conditional Documentation Guide

This guide determines which documentation to read based on the task at hand. Review the conditions below and read the relevant documentation before proceeding.

## Instructions

- Review the task you have been asked to perform.
- Check each documentation path in the sections below.
- For each path, evaluate if any listed condition applies.
- **Only read documentation if a condition matches** — do not read everything unconditionally.
- After reading, identify which skills (`.claude/skills/*/SKILL.md`) are relevant to the task.

---

## Memory system

- `skills/memory/SKILL.md`
  - Conditions:
    - When creating or modifying files in `memory/` or `memory/daily/`
    - When running or modifying the `/claude-project-memory:memory-digest` command
    - When updating the memory system flow or classification rules

- `docs/vault/Claude/Memory.md`
  - Conditions:
    - When modifying the memory system architecture, classification, or agent instructions
    - When adding or removing skills from the digest table
    - When creating new Claude agents or rules related to memory

---

## Vault conventions

- `docs/vault/Development/Obsidian Vault.md`
  - Conditions:
    - When creating or renaming vault documents
    - When adding wikilinks between vault documents
    - When unsure about vault naming conventions (kebab-case, ADR naming, etc.)

- `docs/vault/Home.md`
  - Conditions:
    - When creating a new vault document and need to find the right section
    - When looking for an existing document and unsure of its location
    - Always read this first when exploring the vault

---

## Architecture and decisions

- `docs/vault/Decisions/Index.md`
  - Conditions:
    - Before creating a new ADR (to avoid duplicates and get the next number)
    - When implementing a feature that may have existing architectural decisions
    - When making a technology or pattern choice

---

## Project-specific documentation

<!-- Add project-specific conditional reading rules below this line.
     Follow this pattern for each entry:

- `docs/vault/<Section>/<Document>.md`
  - Conditions:
    - When working on <specific area>
    - When modifying <specific files or layers>
-->
