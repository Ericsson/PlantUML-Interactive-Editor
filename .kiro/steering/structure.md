# Project Structure

## Directory Layout

```
├── src/plantuml_gui/       # Main application package
│   ├── __main__.py         # Entry point (python -m plantuml_gui)
│   ├── __about__.py        # Version info
│   ├── app.py              # Flask app, routes, main orchestration
│   ├── shared/             # Shared infrastructure (used by all diagram types)
│   │   ├── routes.py       # Shared routes (/, /render, /renderPNG, /encode, /decode)
│   │   ├── render.py       # PlantUML JAR invocation for PNG/SVG
│   │   └── puml_encoder.py # URL encoding/decoding for diagram sharing
│   ├── templates/          # Jinja2 templates
│   │   └── index.html      # Single-page app template
│   └── static/             # Frontend assets
│       ├── script.js       # Main activity diagram JS
│       ├── activity.js     # Activity-specific interactions
│       ├── sequence.js     # Sequence diagram support (WIP)
│       ├── mode-plantuml.js # Ace editor PlantUML mode
│       └── styles.css      # Stylesheet
├── tests/
│   ├── test_app.py         # Main Python test suite
│   ├── conftest.py         # pytest fixtures
│   └── js/                 # Jasmine JavaScript tests
│       ├── SpecRunner.html
│       └── ScriptTests.js
└── .kiro/steering/         # Kiro steering files
```

## Module Organization

Each diagram element type has its own Python module:
- `activity.py` - Activity boxes
- `if_statements.py` - Conditionals (if/else, switch)
- `fork.py` - Parallel processing (fork/join)
- `whilepoly.py` - While loops
- `note.py` - Note annotations
- `title.py` - Diagram titles
- `group.py` - Groups and partitions
- `arrow.py` - Arrow/connection handling
- `connector.py` - Connector elements
- `ellipse.py` - Start/stop/end markers
- `merge.py` - Merge points
- `add.py` - Element creation logic
- `classes.py` - Shared data classes (Ellipse, PolyElement, RectElement)
- `util.py` - Utility functions

## Naming Conventions

- **Python files**: lowercase with underscores (snake_case)
- **Python functions**: snake_case
- **Python classes**: PascalCase
- **JavaScript files**: lowercase, hyphen-separated for multi-word
- **JavaScript functions**: camelCase

## Architectural Patterns

- **Flask Blueprints**: Routes split across `shared/routes.py` (shared_bp) and the main `plantuml` Blueprint in `app.py`
- **SVG manipulation**: Backend parses PlantUML-generated SVG to extract clickable regions
- **Stateless server**: Diagram state encoded in URL, no server-side storage
- **Bidirectional sync**: Frontend maintains mapping between SVG elements and PlantUML line numbers

## Adding New Features

1. Create a new module in `src/plantuml_gui/` for the element type
2. Add SVG parsing logic to extract element bounds
3. Add route handlers in `app.py`
4. Add frontend interaction handlers in `activity.js` or `script.js`
5. Write tests in `tests/test_app.py` and `tests/js/ScriptTests.js`
