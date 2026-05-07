---
name: obsidian-vault
description: Vault writing rules for docs/vault/ files.
---

# Obsidian Vault — Writing Rules

Conventions for maintaining the integrity of the Obsidian vault (`docs/vault/`).

---

## YAML Frontmatter (title + summary)

Every vault document **must** have a YAML frontmatter block at the top with at least `title` and `summary`:

```yaml
---
title: Page Title
summary: One or two sentences, ≤200 chars, so a reader can preview this page without opening it.
tags: [optional, tags]
---
```

Rules:

- `title` — derived from the first H1 heading; omit leading `#`.
- `summary` — 1–2 sentences, ≤ 200 characters, written in Spanish (consistent with the project language for user-facing text). Must be useful as a standalone preview without opening the document.
- All other frontmatter fields (e.g. `tags`, `source`) must be preserved when updating an existing file.
- When creating a new vault document, add the frontmatter block before writing any content.
- When editing an existing document that lacks `title` or `summary`, add them as part of the same commit.

---

## Wikilinks

**Rule: full path required**

Every wikilink **must** include the path relative to the vault root, regardless of whether the filename is unique. This makes links explicit, independent of Obsidian's resolver, and easy to search in the repo.

```markdown
<!-- Wrong — no path -->
[[PRD]]
[[Database]]

<!-- Correct — explicit path -->
[[Project/PRD]]
[[Architecture/Database]]
[[Decisions/ADR - Security and Authentication]]
[[ADWS/Scripts/adw_plan]]
```

> **Exception:** wikilinks with aliases (`[[path/file|visible text]]`) already include a path by nature.

---

## File naming

| Document type | Convention | Example |
|---------------|------------|---------|
| Section index | `Index.md` inside the folder | `ADWS/Index.md` |
| Dev script | `script-name.md` (kebab-case) | `quick-start.md` |
| ADW script | `script_name.md` (snake_case, matches the `.py` file) | `adw_build.md` |
| ADW utility script | `script-script_name.md` (`script-` prefix) | `script-backfill_run_manifests.md` |
| Section ADR | `ADR - Section Name.md` | `ADR - Security and Authentication.md` |
| General document | Descriptive name in English | `Database.md` |

---

## Registration in Home.md

Every new file in the vault **must** have a wikilink in `Home.md` under the corresponding section. If the filename is ambiguous (exists in more than one folder), use the full path relative to the vault.

---

## References when renaming/moving files

When renaming or moving a vault file, find and update **all** references across the entire repo — not just the vault. References may appear in:

- `CLAUDE.md`
- `.claude/commands/`, `.claude/commons/`, `.claude/rules/`, `.claude/skills/`
- `specs/`
- `docker/`
- Other `.md` files outside the vault

---

## Long documents — Splitting into sub-documents

**Rule: 150-line maximum per document**

Any document exceeding **150 lines** **must** be split into thematic sub-documents. The original document becomes an index that links to the sub-documents.

**Structure:**

```
Development/
  Tests/
    Index.md                        ← anti-patterns index
    Conventions - Index.md          ← conventions index
    Backend/
      Controllers.md
      Domain and Mappers.md
      FluentValidation.md
      EF Core and Repositories.md
      Anti-Patterns.md
    Frontend/
      Conventions.md
      Anti-Patterns.md
```

**Splitting rules:**

1. Create a folder with the same name as the original document (without extension).
2. Each sub-document covers **one topic** and has a descriptive name in English.
3. The original document (index) must have:
   - A one-line description per sub-document.
   - Full-path wikilinks to each sub-document (see wikilink rule above).
4. If the folder already exists, add the new sub-document inside it.
5. Add wikilinks to new sub-documents in `Home.md`.

**Motivation:** Reduce context consumption when loading documentation with Claude — only the relevant sub-document is loaded instead of the full document.

---

## Checklist when creating/renaming files

1. Add YAML frontmatter with `title` and `summary` (see section above).
2. Verify the name doesn't already exist in another vault folder.
3. If ambiguous: use full path in all wikilinks.
4. Add wikilink in `Home.md` under the corresponding section.
5. Verify no orphaned references to the old name remain (search the entire repo, not just the vault).
6. If the document exceeds 150 lines: split into sub-documents (see section above) before adding new content.
