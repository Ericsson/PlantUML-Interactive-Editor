---
name: good-code-design
description: Apply established software design principles whenever writing new code, refactoring existing code, or reviewing code. Prefer clarity and maintainability over cleverness.
---

# Good Code Design

## Core principles to follow

**High cohesion** — Each module, class, or function should do one well-defined thing. Group code that changes together. If a file mixes unrelated responsibilities (e.g. parsing + rendering + HTTP handling), suggest splitting it.

**Low coupling** — Modules should depend on as few other modules as possible, and only through clear interfaces. Avoid reaching into another module's internals. Prefer passing data over sharing global state.

**Single Responsibility Principle (SRP)** — A function or class should have one reason to change. If you can describe it with the word "and," it probably does too much.

**Separation of concerns** — Keep distinct concerns in distinct places: data parsing, business logic, I/O, presentation, and configuration should not be tangled together.

**Don't Repeat Yourself (DRY)** — Extract shared logic into helpers, but only when the duplication is genuine (same reason to change), not just coincidental similarity.

**You Aren't Gonna Need It (YAGNI)** — Don't build abstractions or configuration options for hypothetical future needs. Solve the problem in front of you.

**Keep It Simple (KISS)** — Prefer the simplest design that works. Complexity must justify itself.

**Composition over inheritance** — Reuse behavior by combining small pieces rather than building deep class hierarchies.

**Stable interfaces, flexible internals** — Public function signatures and module APIs should be small and stable; internal implementation can change freely.

**Pure functions where possible** — Functions that don't mutate state or rely on hidden inputs are easier to test and reason about.

## Naming and readability

- Use descriptive names. A good name removes the need for a comment.
- Functions should be short — if a function doesn't fit on one screen, look for something to extract.
- Consistent naming across the codebase (e.g. don't mix get_user and fetch_user for the same concept).

## Error handling

- Fail fast and fail loudly during development.
- Catch exceptions only where you can meaningfully handle them.
- Don't swallow errors silently.

## Testing-friendliness

- Write code that can be tested without spinning up the whole system.
- Inject dependencies (database connections, file paths, HTTP clients) rather than hard-coding them inside functions.

## When reviewing or refactoring

- Point out coupling problems explicitly: "Module A imports from B's internals — consider exposing a function in B instead."
- Point out cohesion problems explicitly: "This file handles routing, parsing, and rendering — consider splitting into three modules."
- Suggest concrete refactors, not vague advice. Show before/after snippets when helpful.
- Don't refactor aggressively without being asked — flag the issue and propose the change.

## When writing new code

- Before writing, briefly state the responsibility of the module/function you're about to create.
- Prefer small, composable functions over one large function with flags and branches.
- Avoid premature abstraction — wait until you have at least two or three concrete cases before generalizing.

## Language-specific notes (Python)

- Prefer plain functions and dataclasses over classes when state isn't needed.
- Use type hints on public functions.
- Keep imports at the top; avoid circular imports by restructuring rather than using local imports as a workaround.
- Respect module boundaries — if module_a and module_b keep importing from each other, that's a design smell.

## Tone

- Be direct and constructive. Explain why a design choice matters, not just what to change.
- Use short, plain language. No jargon without a quick definition.
