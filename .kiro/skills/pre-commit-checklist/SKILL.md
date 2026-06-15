---
name: pre-commit-checklist
description: Before committing any changes, run quality checks, ensure tests pass, and update all relevant documentation to keep the project consistent and accurate.
---

# Pre-Commit Checklist

## Before every commit, complete these steps in order:

### 1. Run linting and formatting

```bash
uv run ruff check --fix .
uv run ruff format .
```

Fix any remaining issues that `--fix` cannot resolve automatically.

### 2. Run type checking

```bash
uv run mypy .
```

Resolve all type errors before proceeding.

### 3. Run tests

```bash
uv run pytest
```

All tests must pass. If your change breaks existing tests, fix them. If your change adds new behavior, add tests for it.

### 4. Update documentation

Review and update any documentation affected by your changes:

- **`docs/`** — Update the relevant doc if you changed architecture, routes, data models, the frontend-backend contract, element patterns, or setup steps.
- **`README.md`** — Update if you changed usage instructions, pre-requisites, or setup steps.
- **`FEATURES.md`** — Update if you added, removed, or changed a user-facing feature.
- **`.kiro/steering/structure.md`** — Update if you added new files, modules, or changed the directory layout.
- **`.kiro/steering/product.md`** — Update if you changed supported diagram elements or key features.
- **`.kiro/steering/tech.md`** — Update if you added dependencies, changed tooling, or modified commands.
- **Docstrings and code comments** — Update any that describe behavior you changed.

Do not skip documentation updates. Outdated docs are worse than no docs.

### 5. Stage changes deliberately

Stage specific files rather than using `git add .`. Review what you're committing:

```bash
git diff --cached
```

Ensure no unrelated changes, secrets, or temporary files are included.

## Summary

No commit should go out with failing checks or stale documentation. If you changed how something works, update the docs that describe it.
