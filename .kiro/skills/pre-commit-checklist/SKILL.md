---
name: pre-commit-checklist
description: Before committing any changes, run quality checks, ensure tests pass, and update all relevant documentation to keep the project consistent and accurate.
---

# Pre-Commit Checklist

The contributor checklist lives in [`CONTRIBUTING.md`](../../../CONTRIBUTING.md), section "Before opening a pull request". Read it and follow it before every commit; it is the single source of truth for documentation updates, `CHANGELOG.md` entries and staging. Don't duplicate its content here.

Don't bump the version or add a changelog version heading unless the user asks for a release; releasing is described in the "Releasing" section of `CONTRIBUTING.md`.

## Additionally, for agents

Keep the Kiro steering files current, alongside the documentation listed in `CONTRIBUTING.md`:

- **`.kiro/steering/structure.md`**: if you added files or modules, or changed the directory layout.
- **`.kiro/steering/product.md`**: if you changed supported diagram elements or key features.
- **`.kiro/steering/tech.md`**: if you added dependencies, changed tooling, or modified commands.

No commit should go out with stale documentation. If you changed how something works, update the docs that describe it.
