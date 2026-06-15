# `classes.py` — Activity Diagram Data Model

This file defines the data classes and helper functions used across all activity diagram modules. It serves as the bridge between the visual SVG representation and the PlantUML source code.

## Overview

When PlantUML renders an activity diagram, it produces an SVG containing three types of shapes:

- **Rectangles** (`<rect>`) — activity boxes
- **Polygons** (`<polygon>`) — diamond shapes for if/switch statements
- **Ellipses** (`<ellipse>`) — start/stop/end markers

`classes.py` provides Python representations of each, plus a tree structure for tracking nested control flow.

## SVG Element Classes

### `Ellipse`

Represents a start, stop, or end marker (rendered as a circle in the SVG).

```python
@dataclass
class Ellipse:
    cx: float  # center x-coordinate in the SVG
    cy: float  # center y-coordinate in the SVG
```

- **Identified by:** its center coordinates (`cx`, `cy`)
- **`from_svg(svgtext)`**: Parses an SVG snippet containing an `<ellipse>` tag and extracts the center position.

### `RectElement`

Represents an activity box (a rounded rectangle in the SVG).

```python
@dataclass
class RectElement:
    x: float  # top-left x-coordinate
    y: float  # top-left y-coordinate
```

- **Identified by:** its top-left corner position (`x`, `y`)
- **`from_svg(svgtext)`**: Parses an SVG snippet containing a `<rect>` tag.

### `PolyElement`

Represents a diamond-shaped polygon used for if/else conditions and switch statements.

```python
@dataclass
class PolyElement:
    points: str  # comma-separated coordinate string from the SVG "points" attribute
```

- **Identified by:** its `points` string (the exact shape coordinates)
- **`from_svg(svgtext)`**: Parses an SVG snippet containing a `<polygon>` tag.
- **`get_points()`**: Parses the points string into a list of unique `(x, y)` coordinate pairs.
- **`is_merge()`**: Returns `True` if this polygon is a merge point (has not exactly 6 unique vertices). A real if/switch diamond has exactly 6 unique points; a merge polygon has fewer because some points overlap.

### `TextElement`

Represents a text label associated with a shape.

```python
@dataclass
class TextElement:
    label: str         # the text content
    x: float | None    # x-coordinate (optional)
    y: float | None    # y-coordinate (optional)
```

- **`from_svg(svgtext)`**: Parses an SVG snippet containing a `<text>` tag.

### `SvgChunk`

Groups a shape with its associated text labels. This is how the app pairs "this rectangle" with "its label text."

```python
@dataclass
class SvgChunk:
    object: RectElement | PolyElement | Ellipse  # the shape
    text_elements: list[TextElement]              # its associated labels
```

## PlantUML Source Classes

### `Activity`

A simple wrapper for a parsed activity's label text.

```python
@dataclass
class Activity:
    label: str  # e.g. "Process order"
```

### `If`

A parsed if-statement with its condition and branch labels.

```python
@dataclass
class If:
    statement: str  # the condition, e.g. "is valid?"
    branch1: str    # label for the "yes" branch
    branch2: str    # label for the "no" branch
```

### `PumlChunk`

Associates a raw PlantUML text line with its parsed object.

```python
@dataclass
class PumlChunk:
    text: str                    # the raw puml line
    object: Activity | If | None # parsed representation (None if not an activity/if)
```

## Tree Node Classes (Control Flow Tracking)

Activity diagrams have nested control flow (if inside while inside fork, etc.). The tree structure maps the **order in which elements appear in the SVG** to the correct **line numbers in the puml source**, accounting for nesting.

### `TreeNode` (base class)

```python
@dataclass(kw_only=True)
class TreeNode:
    index: int  # line number in the puml source
```

- **`add_node(node)`**: Add a child node (overridden by subclasses).
- **`add_indices(indices, lines)`**: Recursively collect line indices in the order they appear visually in the SVG.

### `IfElseNode(TreeNode)`

Represents an if/else block. Has two branches that each contain their own child nodes.

```python
@dataclass(kw_only=True)
class IfElseNode(TreeNode):
    ifbranch: list[TreeNode]       # nodes inside the "if" branch
    elsebranch: list[TreeNode]     # nodes inside the "else" branch
    inside_ifbranch: bool = True   # tracks which branch we're currently adding to
```

- **`add_node(node)`**: Appends to `ifbranch` or `elsebranch` depending on `inside_ifbranch`.
- **`add_indices(indices, lines)`**: Determines whether the if-statement's own index comes before or after its children (depends on whether it has non-empty branches — see `check_branch`).

### `RepeatSwitchNode(TreeNode)`

Represents a repeat-while loop or a switch statement. Has a single branch containing its body.

```python
@dataclass(kw_only=True)
class RepeatSwitchNode(TreeNode):
    branch: list[TreeNode]  # nodes inside the loop/switch body
```

- **`add_indices(indices, lines)`**: For `repeat` loops, the index comes *after* the body (because the loop diamond appears at the bottom in the SVG). For switch statements, the index comes *before* the body.

## Helper Functions

### `check_branch(lines, index)`

Determines whether an if-statement at the given line index should have its own index added *before* or *after* its children in the SVG order.

Returns `True` (index goes after children) when:
- There is no else branch
- The else branch is empty
- The if branch is empty
- Either branch contains only a connector `(...)` or `stop`

### `findelsebounds(lines, if_start)`

Given the line index of an `if` statement, finds the start and end line indices of the corresponding `else` block. Handles nesting by tracking depth levels.

Returns `(start_else, end_else)` — both are `-1` if no else branch exists.

### `find_end(lines, start_if)`

Given the line index of a control-flow statement (`if`, `repeat`, or `switch`), finds its closing line (`endif`, `repeat while`, or `endswitch`). Handles nesting by tracking depth levels.

## How These Classes Work Together

```
SVG (visual)                          puml source (text)
─────────────                         ──────────────────
<ellipse cx=100 cy=20>    ←──────→    @startuml         (line 0)
<rect x=50 y=60>          ←──────→    :Do something;    (line 1)
<polygon points="...">    ←──────→    if (cond?) then   (line 2)
<rect x=30 y=140>         ←──────→      :Yes action;    (line 3)
<rect x=170 y=140>        ←──────→      :No action;     (line 5)
<ellipse cx=100 cy=220>   ←──────→    stop              (line 7)
```

1. The SVG is parsed into `SvgChunk` objects (shape + text labels)
2. The puml source is parsed into `PumlChunk` objects (line text + parsed type)
3. The `TreeNode` hierarchy maps SVG visual order → puml line numbers, handling nesting correctly
4. When a user clicks on an SVG element, its position identifies the `SvgChunk`, which maps to a puml line, enabling source manipulation
