# Data Model

## classes.py (Activity Diagrams)

**RectElement**

Represents a rectangle in the SVG — corresponds to an activity box. Identified by its `x` and `y` attributes. Created from SVG via `RectElement.from_svg(svgtext)` which extracts the `<rect>` element's x/y. Two RectElements are equal if they share the same coordinates.

**PolyElement**

Represents a polygon in the SVG — corresponds to an if/else diamond or switch statement. Identified by its `points` string (comma-separated coordinate pairs). Has `get_points()` which returns unique coordinate pairs, and `is_merge()` which detects merge polygons (those with not exactly 6 unique points) to distinguish them from statement polygons.

**Ellipse**

Represents an ellipse in the SVG — corresponds to start, stop, or end markers, and also connectors. Identified by `cx` and `cy` (center coordinates). Created from SVG via `Ellipse.from_svg(svgtext)`.

**TextElement**

Represents a `<text>` element in the SVG. Stores `label`, `x`, and `y`. Used as part of `SvgChunk` to associate text labels with their parent shape.

**SvgChunk**

Pairs one shape object (`RectElement`, `PolyElement`, or `Ellipse`) with a list of `TextElement` objects. This is the fundamental unit that element modules iterate over to count and locate clicked elements. Built by each module's `svgtochunklist*` function.

**TreeNode (abstract base)**

Base class for building a tree of nested puml structures. Has `index` (the puml line number) and abstract methods `add_node()` and `add_indices()`. Used internally by `if_statements.py` for navigating nested if/else and repeat blocks.

**IfElseNode (extends TreeNode)**

Represents an if/else block. Contains `ifbranch` and `elsebranch` (both lists of TreeNode). Tracks `inside_ifbranch` state for building. `add_indices()` collects all relevant line indices for the block.

**RepeatSwitchNode (extends TreeNode)**

Represents a repeat or switch block. Contains a single `branch` list. `add_indices()` collects line indices for the entire block.

**Activity**

Simple dataclass holding a `label` string. Used inside `PumlChunk`.

**If**

Simple dataclass holding `statement`, `branch1`, `branch2` strings.

**PumlChunk**

Pairs a `text` string with an optional `object` (Activity or If). Appears to be used for intermediate parsing but is not heavily referenced in current code.

## sequence_classes.py (Sequence Diagrams)

**Participant**

Represents a participant in a sequence diagram. Fields: `name`, `cx`, `cy` (center of the header rect), `x_origin`, `width`, `index` (line number in puml source). Has `contains_x(x_val)` to check if an x-coordinate falls within the participant's header rectangle. Created from SVG via `Participant.from_svg(rect, text)`.

**Message**

Represents a message arrow between two participants. Fields: `from_participant`, `to_participant`, `message` (label text), `cy` (vertical position), `index` (puml line number). Has three factory methods:

- `from_normal_svg()` — For `->`, `-->`, `<-`, `<--` arrows. Determines direction by comparing line endpoints to the arrow polygon position.
- `from_bidirectional_svg()` — For `<->` or `<-->` arrows.
- `from_self_svg()` — For self-referencing messages (three lines + polygon).

**Diagram**

Top-level container that parses an SVG string and puml text to extract all participants and messages. Factory method `Diagram.from_svg(svgtext, puml)` builds the diagram. Internally:

- `_parse_participants()` — Finds unique `<rect>` elements by cx, creates Participant objects, then assigns puml line indexes by matching participant declaration lines.
- `_parse_messages()` — Iterates SVG elements looking for three patterns: polygon+polygon+line+text (bidirectional messages), line+line+line+polygon+text (self-messages), and polygon+line+text (normal messages). Creates Message objects, then assigns indexes from lines containing `->`.
