# Technology Stack

## Backend

- **Python**: 3.10+ required
- **Flask**: 3.x web framework with Jinja2 templates
- **python-dotenv**: Environment variable management
- **loguru**: Logging
- **pyquery**: HTML/XML parsing for SVG manipulation

## Frontend

- **Vanilla JavaScript**: No framework dependencies
- **Ace Editor**: Code editor with PlantUML syntax highlighting (custom mode in `mode-plantuml.js`)
- **CSS**: Plain CSS, no preprocessors

## External Dependencies

- **PlantUML JAR**: Required for diagram rendering. Path configured via `PLANTUML_JAR` environment variable in `.env` file

## Build & Packaging

- **Hatchling**: Build backend
- **uv**: Package manager and virtual environment tool

## Development Tools

- **ruff**: Linting and formatting (rules: E, F, I, N; E501 ignored)
- **mypy**: Static type checking
- **pre-commit**: Git hooks for code quality
- **js-beautify**: JavaScript formatting (for script.js)

## Testing

- **pytest**: Python unit tests with pytest-cov for coverage
- **Jasmine**: JavaScript tests (run via browser at `tests/js/SpecRunner.html`)

## Commands

```bash
# Install dependencies
pip install .

# Run server
python -m plantuml_gui

# Run Python tests
uv run pytest

# Run tests with coverage
uv run python -m pytest --cov --cov-report=html

# Setup pre-commit hooks
uv run pre-commit install -t pre-commit -t pre-push
```

## Constraints

- All Python code must pass ruff and mypy checks
- MIT license headers required in source files
- PlantUML JAR must be available locally (not bundled)
