## How to contribute to PlantUML Interactive Editor
#### **Did you find a bug?**

* **Ensure the bug was not already reported** by searching on GitHub under [Issues](https://github.com/Ericsson/PlantUML-Interactive-Editor/issues).

* If you're unable to find an open issue addressing the problem, [open a new one](https://github.com/Ericsson/PlantUML-Interactive-Editor/issues/new). Be sure to include a **title and clear description**, as much relevant information as possible, and a **code sample** or an **executable test case** demonstrating the expected behavior that is not occurring.

#### **Did you write a patch that fixes a bug?**

* Open a new GitHub pull request with the patch.

* Ensure the PR description clearly describes the problem and solution. Include the relevant issue number if applicable.

#### **Do you intend to add a new feature or change an existing one?**

* Suggest your change by opening an [issue](https://github.com/Ericsson/PlantUML-Interactive-Editor/issues/new) on GitHub and tagging it with the label **"enhancement"**. Clearly describe your idea and its benefits to gather feedback from the community.

* **Do not submit a pull request** until you have received positive feedback and community approval through the issue.

#### **Do you have questions about the source code?**

* Ask any question by opening an [issue](https://github.com/Ericsson/PlantUML-Interactive-Editor/issues/new) on GitHub and tagging it with the label **"question"**.

## Development setup

### Pre-requisites

- uv

### Setup

```
uv run pre-commit install -t pre-commit -t pre-push
```

## Running tests

```
uv run pytest                                      # Python tests
uv run python -m pytest --cov --cov-report=html    # Python tests with coverage
uv run pytest tests/e2e/                           # JavaScript (Playwright end-to-end) tests
```

## Before opening a pull request

Work through this checklist for every PR.

### 1. Update the documentation your change affects

- **`docs/`**: if you changed the architecture, routes, data models, the frontend-backend contract, element patterns or setup steps.
- **`README.md`**: if you changed usage instructions, pre-requisites or setup steps.
- **`FEATURES.md`**: if you added, removed or changed a user-facing feature.
- **Docstrings and code comments**: if they describe behavior you changed.

### 2. Describe your change in `CHANGELOG.md`

Add a bullet under `## [Unreleased]`:

- **`### External`**: changes users notice (new features, bug fixes, changed behavior). These are shown to users in the app's Version History panel, so write them for users.
- **`### Internal`**: everything else (refactoring, tests, CI, tooling, docs).

Changes to the VS Code extension itself (not to diagram editing) go under `## [Unreleased]` in `plantuml-extension/CHANGELOG.md` instead.

Leave the version number alone and don't add a version heading: both are done when releasing (see below).

### 3. Review what you commit

Stage specific files rather than `git add .`, and check `git diff --cached` for unrelated changes, secrets or temporary files.

## Releasing

Versions follow [semver](https://semver.org) (`X.Y.Z`), and a release is a deliberate decision, not something every PR does.

1. Read the entries under `## [Unreleased]` in `CHANGELOG.md` and pick the step they call for, then run one of:

   ```
   uv run python scripts/bump_version.py patch   # bug fixes only
   uv run python scripts/bump_version.py minor   # new features
   uv run python scripts/bump_version.py major   # incompatible changes
   ```

   This sets the new version in `src/plantuml_gui/__about__.py`, `plantuml-extension/package.json` and `package-lock.json`, and turns `[Unreleased]` into `[X.Y.Z] - <date>` in both changelogs (the extension's only if it has entries). Don't edit version numbers by hand.

2. Get the bump merged to `main`, either in a PR of its own or inside a small fix PR you want released quickly.

3. From a clean checkout of that commit, publish:

   ```
   scripts/build_release.sh <destination>
   ```

   This builds the `.vsix` (backend wheel included), publishes it to `<destination>`, then tags the commit `vX.Y.Z` and pushes the tag. If `vX.Y.Z` already exists on another commit it stops before building: that version has been released, so bump again first.
