# Element Pattern

All element modules in `src/plantuml_gui/` follow the same general pattern for handling user interactions with diagram elements. This document describes that pattern and walks through two concrete examples.

## The Shared Pattern

1. **Parse SVG into a chunk list** — Use PyQuery to find all SVG elements of the relevant type (e.g., `<rect>`, `<polygon>`, `<ellipse>`). For each, create an `SvgChunk` object pairing the shape with its associated `TextElement` objects (the text labels immediately following the shape in the SVG DOM).

2. **Locate the clicked element** — The frontend sends the clicked SVG element's `outerHTML`. The backend deserializes it into a data object (`RectElement`, `PolyElement`, or `Ellipse`) using the class's `from_svg()` method. Then it counts through the chunk list to find the matching element's position (1-based index).

3. **Map to puml line index** — Walk through the puml lines, counting occurrences of the relevant keyword pattern (e.g., lines starting with `:` for activities, `stop`/`start`/`end` for ellipses). When the count matches the SVG position, that's the puml line being interacted with.

4. **Manipulate puml lines** — Depending on the operation (edit, delete, add below, detach, etc.), insert, replace, or remove lines from the puml text.

5. **Return modified puml** — Join the lines back with `"\n"` and return as plain text.

## Walkthrough: `title.py`

Title is the simplest module because there is at most one title block, so no SVG parsing or counting is needed.

```python
def add_title(puml):
    lines = puml.splitlines()
    for index, line in enumerate(lines):
        if line == "@startuml":
            # Insert "title\nPlaceholder Title\nendtitle" after @startuml
            lines.insert(index + 1, "endtitle")
            lines.insert(index + 1, "Placeholder Title")
            lines.insert(index + 1, "title")
            break
    return "\n".join(lines)
```

- `get_title_text(puml)` — Iterates lines between `title` and `endtitle`, concatenates them.
- `edit_title_text(puml, title)` — Finds the title bounds, replaces the content lines. If title is empty string, deletes the whole block.
- `find_title_bounds(lines)` — Returns `(start, end)` line indices.
- `delete_title(puml)` — Calls `find_title_bounds` then deletes `lines[start:end+1]`.

No SVG parsing is needed because the title is identified purely by its puml keywords.

## Walkthrough: `ellipse.py`

Ellipse demonstrates the full SVG-counting pattern for start/stop/end markers.

**Step 1 — Parse SVG:**

```python
def svgtochunklistellipse(svg):
    chunks = []
    d = Pq(svg)
    ellipses = d("ellipse")
    for ellipse in ellipses:
        ellipse_obj = Ellipse.from_svg(ellipse_svg)
        # Skip double-ellipses (the "end" marker has two overlapping)
        # Skip ellipses followed by a filled path (connector markers)
        chunks.append(SvgChunk(object=ellipse_obj, text_elements=[]))
    return chunks
```

**Step 2 — Locate clicked element:**

Uses the shared `index_of_clicked_element()` from `util.py` which iterates chunks comparing `.object == clickedelement` and returns the 1-based count.

**Step 3 — Map to puml line:**

```python
def get_index_ellipse(puml, svgchunklist, clickedelement, where) -> int:
    count = index_of_clicked_element(svgchunklist, clickedelement)
    lines = puml.splitlines()
    for index, line in enumerate(lines):
        clean_line = line.strip()
        if clean_line in ["stop", "start", "end"]:
            count -= 1
        if count == 0:
            break
    return index + 1  # returns line after the element (for "add below")
```

**Step 4 — Delete:**

```python
def delete_ellipse_element(puml, svgchunklist, clickedelement):
    # Same counting logic, then del lines[index]
    return "\n".join(lines)
```

## Other Modules

The same pattern applies to:

- `activity.py` — Counts `<rect>` elements with specific height/style attributes
- `if_statements.py` — Counts `<polygon>` elements, skipping merge polygons (detected via `is_merge()`)
- `connector.py` — Counts small `<ellipse>` elements that have an associated text character
- `fork.py` — Counts `<rect>` elements that represent fork/join bars (height <= 6)
- `whilepoly.py` — Reuses the polygon chunk list, distinguishes while polygons via the `checkifwhile()` utility
- `note.py`, `group.py`, `arrow.py` — Use different SVG element matching but follow the same locate-then-manipulate pattern
- `participant.py` (sequence) — Counts `<rect>` elements deduplicated by center-x (each participant has top and bottom rects with the same cx)
