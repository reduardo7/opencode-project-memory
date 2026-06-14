---
tags: [development, obsidian, vault, conventions]
---

# Obsidian Vault — Writing Rules

Conventions for maintaining the integrity of the Obsidian vault (`docs/vault/`).

---

## Wikilinks

### Rule: Full path required

Every wikilink **must** include the path relative to the vault root, regardless of whether the filename is unique. This ensures links are explicit, do not depend on Obsidian's resolver, and are easy to search in the repo.

```markdown
<!-- Wrong — no path -->
[[PRD]]
[[Database]]

<!-- Correct — explicit path -->
[[Project/PRD]]
[[Architecture/Database]]
[[Decisions/ADR - Security and Authentication]]
```

> **Exception:** wikilinks with aliases (`[[path/file|visible text]]`) already include the path by nature.

---

## File naming

| Document type | Convention | Example |
|---------------|------------|---------|
| Section index | `Index.md` inside the folder | `Decisions/Index.md` |
| Development script | `script-name.md` (kebab-case) | `quick-start.md` |
| ADR by section | `ADR - Section Name.md` | `ADR - Security and Authentication.md` |
| General document | Descriptive name | `Database.md` |

---

## Registration in Home.md

Every new file in the vault **must** have a wikilink in `Home.md` under the corresponding section. If the filename is ambiguous (exists in more than one folder), use the path relative to the vault.

---

## References when renaming/moving files

When renaming or moving a vault file, search for and update **all** references in the entire repo — not just the vault. References can be in:

- `AGENTS.md` (root and nested)
- `.opencode/command/`, `.opencode/agent/`, `.opencode/skills/`, `.opencode/plugin/`
- `specs/`
- Other `.md` files outside the vault

---

## Checklist when creating/renaming files

1. Verify the name does not exist in another vault folder
2. If ambiguous: use full path in all wikilinks and add to a disambiguation table in this document
3. Add wikilink in `Home.md` in the corresponding section
4. Verify no orphaned references to the previous name remain (search the entire repo, not just the vault)
