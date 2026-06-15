# Setup

Developer setup notes for the PlantUML Interactive Editor.

## Prerequisites

- Python 3.10 or newer
- Java runtime (required to run the PlantUML JAR)
- PlantUML JAR file (download from https://plantuml.com/starting)
- uv (for dev dependency management)

## Loading Python

On systems using the module system:

```
module add python/3.11.15
```

## Activating the Virtual Environment

```
source .venv/bin/activate
```

If the venv does not exist yet, create it with:

```
uv venv
```

## Installing Dependencies

For production:

```
pip install .
```

For development (includes pytest, ruff, mypy, pre-commit, coverage):

```
uv sync
```

## Environment Configuration

Create a `.env` file in the project root (see `.env.example`):

```
PLANTUML_JAR="/path/to/plantuml.jar"
```

The `PLANTUML_JAR` variable must point to your local PlantUML JAR file. This is loaded by `python-dotenv` at import time in `render.py`.

## Running the App

```
python -m plantuml_gui
```

This starts Flask in debug mode on the default port (5000). Open `http://localhost:5000` in a browser.

## How render.py Invokes the PlantUML JAR

`render.py` runs the JAR via subprocess:

```
java -DPLANTUML_LIMIT_SIZE=16384 -jar $PLANTUML_JAR -pipe -tsvg
```

- `-pipe` — Read puml from stdin, write output to stdout
- `-tsvg` or `-tpng` — Output format
- `-DPLANTUML_LIMIT_SIZE=16384` — Increases max diagram size

The puml text is passed as stdin bytes. The SVG/PNG output is read from stdout.

## Pre-commit Hooks

```
uv run pre-commit install -t pre-commit -t pre-push
```

Hooks run ruff (linting/formatting) and mypy (type checking).

## Running Tests

Python tests (without coverage):

```
uv run pytest
```

Python tests (with coverage):

```
uv run python -m pytest --cov --cov-report=html
```

JavaScript tests (Jasmine):

1. Run `uv run python -m http.server` from the project root
2. Open `tests/js/SpecRunner.html` in a browser

## Git Branch Convention

Use the `fix/...` prefix for branches:

```
git checkout -b fix/description-of-change
```
