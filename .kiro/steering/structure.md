# Project Structure

## Directory Layout

```
├── src/plantuml_gui/       # Main application package
│   ├── __main__.py         # Entry point (python -m plantuml_gui)
│   ├── __about__.py        # Version info
│   ├── app.py              # Flask app factory, blueprint registration only
│   ├── shared/             # Shared infrastructure (used by all diagram types)
│   │   ├── routes.py       # Shared routes (/, /render, /renderPNG, /encode, /decode)
│   │   ├── render.py       # PlantUML JAR invocation for PNG/SVG
│   │   ├── puml_encoder.py # URL encoding/decoding for diagram sharing
│   │   └── parse_changelog.py # CHANGELOG.md parser for version history
│   ├── sequence/           # Sequence diagram package
│   │   ├── routes.py       # Sequence routes (/addParticipant, /addMessage, etc.)
│   │   ├── classes.py      # Diagram, Participant, Message data classes; shared participant-rect helpers (is_participant_rect, participant_header_bounds, rect_encloses)
│   │   ├── participant.py  # Participant logic (add, rename, delete, positions)
│   │   ├── message.py      # Message logic (add message, y-based insertion)
│   │   ├── activation.py   # Activation bar logic (activate + deactivate/destroy pair)
│   │   ├── group.py        # Group block logic (group, alt, opt, loop)
│   │   ├── box.py          # Participant box logic (add, delete, nesting via teoz, is_box_rect)
│   │   ├── note.py         # Note logic (add, edit, delete notes)
│   │   ├── positions.py    # Per-render position aggregator (get_sequence_positions: one fetch for all element types' editor rows)
│   │   └── util.py         # Shared utilities (insertion index, note position extraction, multi-line text escaping)
│   ├── activity/           # Activity diagram package
│   │   ├── routes.py       # All activity routes (~64 endpoints)
│   │   ├── classes.py      # RectElement, PolyElement, Ellipse, SvgChunk, TextElement
│   │   ├── activity.py     # Activity box logic
│   │   ├── if_statements.py # Conditionals (if/else, switch)
│   │   ├── fork.py         # Parallel processing (fork/join)
│   │   ├── whilepoly.py    # While loops
│   │   ├── note.py         # Note annotations
│   │   ├── title.py        # Diagram titles
│   │   ├── group.py        # Groups and partitions
│   │   ├── arrow.py        # Arrow/connection handling
│   │   ├── connector.py    # Connector elements
│   │   ├── ellipse.py      # Start/stop/end markers
│   │   ├── merge.py        # Merge points
│   │   ├── add.py          # Element creation logic
│   │   └── util.py         # Utility functions
│   ├── templates/          # Jinja2 templates
│   │   ├── index.html      # Single-page app template (shared layout)
│   │   └── partials/       # Included template fragments
│   │       ├── activity_menus.html  # Activity context menus and modals
│   │       └── sequence_menus.html  # Sequence context menus and modals
│   └── static/             # Frontend assets
│       ├── script.js       # Main activity diagram JS
│       ├── activity.js     # Activity-specific interactions
│       ├── hover-highlight.js # Shared editor->diagram hover-highlight core (row map, highlight styles, and editor hover/cursor dispatch), used by activity.js and sequence-operations.js
│       ├── sequence-message.js  # Sequence add-message interaction (hover, ghost arrow, modal)
│       ├── sequence-activation.js # Sequence activation-bar interaction (ghost bar, two-click)
│       ├── sequence-group.js    # Sequence group-block interaction (ghost box, two-click, modal)
│       ├── sequence-box.js      # Sequence participant-box interaction (horizontal ghost box, two-click add; edit title/color and delete via the lifeline context menu)
│       ├── sequence-operations.js # Sequence participant operations and orchestration
│       ├── mode-plantuml.js # Ace editor PlantUML mode
│       ├── styles.css      # Main stylesheet (imports css/ modules)
│       └── css/            # Modular CSS files
│           ├── tokens.css  # Design tokens (CSS custom properties)
│           ├── layout.css  # App shell, split panes, divider
│           ├── toolbars.css # Global bar, pane toolbars, button styles
│           ├── panels.css  # Dropdown panels, legacy dropdown compat
│           ├── editor.css  # Ace editor, diagram canvas, loading
│           └── legacy.css  # Error popup, hover overlay
├── tests/
│   ├── conftest.py         # pytest fixtures (client fixture)
│   ├── activity/           # Activity diagram route & logic tests
│   │   ├── test_activity.py
│   │   ├── test_arrow.py
│   │   ├── test_connector.py
│   │   ├── test_ellipse.py
│   │   ├── test_fork.py
│   │   ├── test_group.py
│   │   ├── test_if.py
│   │   ├── test_if_statements.py
│   │   ├── test_merge.py
│   │   ├── test_activity_note.py
│   │   ├── test_repeat_while.py
│   │   ├── test_switch.py
│   │   ├── test_title.py
│   │   └── test_while.py
│   ├── shared/             # Shared route tests (render, encode/decode)
│   │   └── test_render.py
│   ├── sequence/           # Sequence diagram tests
│   │   ├── test_participant.py
│   │   ├── test_message.py
│   │   ├── test_activation.py
│   │   ├── test_sequence_group.py
│   │   ├── test_box.py
│   │   └── test_sequence_note.py
│   └── e2e/                # Playwright end-to-end tests
│       ├── conftest.py     # Live server fixture
│       ├── test_app_loads.py  # App loads correctly
│       ├── test_js_logic.py   # JS function logic tests
│       ├── test_render_race.py # Render-generation race regression (slow render can't clobber a newer diagram)
│       ├── test_ribbon.py     # Toolbar ribbon UI tests
│       ├── test_sequence_activation.py       # Activation bar e2e tests
│       ├── test_sequence_box.py              # Participant box add/delete/hover e2e tests
│       ├── test_sequence_hover_highlight.py  # Editor <-> diagram hover highlighting e2e tests
│       ├── test_sequence_message_interactions.py # Message add/edit/delete e2e tests
│       ├── test_sequence_note_menu.py         # Note type menu, modal type selector & create/edit flow e2e tests
│       └── test_sequence_participant.py      # Participant add/rename/delete e2e tests
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

- **Flask Blueprints**: Routes split across `shared/routes.py` (shared_bp), `activity/routes.py` (activity_bp), and `sequence/routes.py` (sequence_bp). `app.py` only registers blueprints.
- **SVG manipulation**: Backend parses PlantUML-generated SVG to extract clickable regions
- **Stateless server**: Diagram state encoded in URL, no server-side storage
- **Bidirectional sync**: Frontend maintains mapping between SVG elements and PlantUML line numbers

## Adding New Features

1. Create a new module in `src/plantuml_gui/` for the element type
2. Add SVG parsing logic to extract element bounds
3. Add route handlers in `app.py`
4. Add frontend interaction handlers in `activity.js` or `script.js`
5. Write tests in the appropriate `tests/<module>/` directory and `tests/e2e/`
