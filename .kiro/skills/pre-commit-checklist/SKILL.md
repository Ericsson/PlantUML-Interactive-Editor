---
name: pre-commit-checklist
description: Before committing any changes, run quality checks, ensure tests pass, and update all relevant documentation to keep the project consistent and accurate.
---

# Pre-Commit Checklist

## Before every commit, complete these steps:

### 1. Update documentation

Review and update any documentation affected by your changes:

- **`docs/`** — Update the relevant doc if you changed architecture, routes, data models, the frontend-backend contract, element patterns, or setup steps.
- **`README.md`** — Update if you changed usage instructions, pre-requisites, or setup steps.
- **`FEATURES.md`** — Update if you added, removed, or changed a user-facing feature.
- **`CHANGELOG.md`** — Add new features and bug fixes to the `## [Unreleased]` section. User-facing changes go under `### External`; technical/internal changes go under `### Internal`.
- **`.kiro/steering/structure.md`** — Update if you added new files, modules, or changed the directory layout.
- **`.kiro/steering/product.md`** — Update if you changed supported diagram elements or key features.
- **`.kiro/steering/tech.md`** — Update if you added dependencies, changed tooling, or modified commands.
- **Docstrings and code comments** — Update any that describe behavior you changed.

Do not skip documentation updates. Outdated docs are worse than no docs.

### 2. Stage changes deliberately

Stage specific files rather than using `git add .`. Review what you're committing:

```bash
git diff --cached
```

Ensure no unrelated changes, secrets, or temporary files are included.

## Summary

No commit should go out with stale documentation. If you changed how something works, update the docs that describe it.
