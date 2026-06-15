# Architecture

PlantUML Interactive Editor is structured in five layers.

## Layer 1: Entry Point and Flask Routes

- `__main__.py` — Imports `app` from `app.py` and calls `app.run(debug=True)`. Run with `python -m plantuml_gui`.
- `app.py` — Creates a Flask app with a single Blueprint (`plantuml_gui`). Contains ~71 POST routes and 1 GET route (`/`). Each route extracts JSON fields from the request, calls the appropriate element module function, and returns the result (usually modified puml text).

The Flask app is stateless. There is no database or session storage. Diagram state lives entirely in the URL (encoded puml text).

## Layer 2: Data Models

- `classes.py` — Shared data classes for activity diagrams: `RectElement`, `PolyElement`, `Ellipse`, `TextElement`, `SvgChunk`, and the `TreeNode` hierarchy (`IfElseNode`, `RepeatSwitchNode`). Also contains helper functions for navigating nested if/else/repeat structures in puml lines.
- `sequence_classes.py` — Data classes for sequence diagrams: `Participant`, `Message`, `Diagram`. The `Diagram` class parses SVG to extract participants and messages, and assigns source line indexes from the puml text.

## Layer 3: Rendering Pipeline

- `render.py` — Invokes the PlantUML JAR via `subprocess.run` to produce SVG or PNG output. The JAR path comes from the `PLANTUML_JAR` environment variable (loaded from `.env` by python-dotenv). Command: `java -DPLANTUML_LIMIT_SIZE=16384 -jar $PLANTUML_JAR -pipe -tsvg`.
- `puml_encoder.py` — Encodes puml text into a URL-safe string (zlib compress → base64 → custom alphabet translation) and decodes it back. Used for sharing diagrams via the browser address bar.

## Layer 4: Element Modules

Each diagram element type has its own Python module. They all follow a shared pattern: parse the SVG with PyQuery to build a list of `SvgChunk` objects, count through the chunks to find the clicked element, locate the corresponding line index in the puml text, manipulate the puml lines (edit, delete, add), and return the modified puml string.

Modules:

- `activity.py` — Activity boxes (rectangles)
- `if_statements.py` — If/else and switch statements (polygons)
- `ellipse.py` — Start/stop/end markers (ellipses)
- `fork.py` — Fork/join parallel processing (rectangle bars)
- `whilepoly.py` — While loops (polygons)
- `note.py` — Note annotations
- `title.py` — Diagram titles
- `group.py` — Groups and partitions
- `arrow.py` — Arrow/connection handling
- `connector.py` — Connector elements (small labeled circles)
- `merge.py` — Merge points
- `add.py` — Element creation logic (inserts new puml lines for a given element type)
- `participant.py` — Sequence diagram participants and messages

## Layer 5: Frontend

- `templates/index.html` — Single-page app template. Loads Bootstrap, jQuery, Popper.js, Ace Editor, panzoom, and jsdiff from CDNs. Includes the app's own JS and CSS. Uses `{% include %}` to pull in diagram-specific partials.
- `templates/partials/activity_menus.html` — All activity diagram context menus and modal dialogs.
- `templates/partials/sequence_menus.html` — Sequence diagram context menus and modal dialogs.
- `static/script.js` — Core logic: editor initialization (Ace with PlantUML syntax mode), rendering (calls `/render` and `/encode`), URL hash management, undo/redo history, diagram type detection, indentation, panning/zooming, and utility functions.
- `static/activity.js` — Event listeners and fetch calls for all activity diagram interactions (edit, delete, add, detach, context menus for activities, if-statements, ellipses, forks, notes, groups, merges, whiles, connectors, arrows).
- `static/sequence.js` — Event listeners for sequence diagram interactions (add/edit/delete participants, add messages with two-click coordinate capture).

## Summary

*The frontend sends the current PlantUML text + rendered SVG + click coordinates to the backend; the backend parses the SVG to find what was clicked, manipulates the corresponding lines in the puml text, and returns the modified text; the frontend re-renders it.*
