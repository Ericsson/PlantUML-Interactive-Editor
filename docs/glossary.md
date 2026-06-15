# Glossary

**Activity diagram** — A type of PlantUML diagram showing control flow with activities (actions), decisions, forks, and loops. The primary diagram type supported by this editor.

**Sequence diagram** — A type of PlantUML diagram showing message exchanges between participants over time. Partially supported (add/edit/delete participants and messages).

**Lifeline** — The vertical dashed line extending below a participant in a sequence diagram, representing the participant's existence over time.

**Participant** — A named entity in a sequence diagram (rendered as a box at the top). In the code, represented by the `Participant` class with position and puml line index.

**puml text** — The raw PlantUML source code that defines a diagram. Starts with `@startuml` and ends with `@enduml`. This is what the user edits in the Ace editor and what the backend manipulates.

**Element module** — A Python module in `src/plantuml_gui/` responsible for one type of diagram element (e.g., `activity.py`, `ellipse.py`, `title.py`). Each follows the shared pattern of parsing SVG, locating the clicked element, and manipulating puml lines.

**SvgChunk** — A data class pairing one SVG shape (rect, polygon, or ellipse) with its associated text labels. Element modules build lists of SvgChunks to map between SVG positions and puml line positions.

**TreeNode** — Abstract base class for representing nested puml structures (if/else, repeat, switch) as a tree. Used by `if_statements.py` to navigate and index nested blocks correctly.

**RectElement** — Data class representing a clicked SVG rectangle. Used for activity boxes and fork bars. Identified by x/y coordinates.

**PolyElement** — Data class representing a clicked SVG polygon. Used for if/else diamonds and switch statements. Identified by its points string.

**Ellipse** — Data class representing a clicked SVG ellipse. Used for start/stop/end markers and connectors. Identified by cx/cy center coordinates.

**Fork** — A PlantUML construct for parallel processing (`fork` / `fork again` / `end fork`). Rendered as horizontal bars in the SVG.

**Merge** — A point where parallel branches rejoin (`end merge`). Rendered as a small diamond polygon in the SVG.

**Connector** — A labeled circle in an activity diagram (written as `(A)` in puml) used to link disconnected parts of the diagram without arrows.

**PlantUML JAR** — The Java executable that converts PlantUML text into SVG or PNG images. Required external dependency, path configured via the `PLANTUML_JAR` environment variable.

**Blueprint** — A Flask concept for grouping related routes. This project uses a single Blueprint named `plantuml_gui` registered on the Flask app, containing all routes.

**PyQuery** — A Python library (jQuery-like API for XML/HTML) used to parse SVG output and extract element attributes. The primary tool for SVG manipulation in element modules.

**Ace Editor** — The JavaScript code editor embedded in the frontend. Configured with a custom PlantUML syntax highlighting mode (`mode-plantuml.js`).

**panzoom** — A JavaScript library used to enable pan and zoom on the rendered SVG diagram in the browser.
