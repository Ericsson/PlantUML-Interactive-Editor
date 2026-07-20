# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2026 Ericsson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

from typing import List, Optional

from pyquery import PyQuery as Pq

from .box import is_box_rect
from .classes import Message, participant_header_bounds

# PlantUML renders each note type as a visually distinct shape, independent
# of fill color:
# - "note":  two <path> elements - a folded-corner rectangle body (6 points)
#   immediately followed by the small triangular fold corner (4 points).
# - "hnote": a single <polygon> with exactly 7 points forming a hexagon.
# - "rnote": a single <rect> element (plain rectangle, no fold).
_HEXAGON_POINT_COUNT = 7

# The three PlantUML keywords that render as a "note" element. Order matters
# for matching: check longer keywords first isn't required here since they
# all differ by more than a shared prefix, but kept as a tuple for clarity
# and to avoid repeating the literal list at each call site.
NOTE_KEYWORDS = ("note", "hnote", "rnote")


def classify_note_shape(path: Pq) -> Optional[str]:
    """Classify a single SVG shape element as a note type, or None.

    Identifies "note", "hnote", or "rnote" by tag name and path/point
    structure only - never by fill color - so detection keeps working
    once note colors become user-customizable.

    For "note", `path` must be the first of the two-path pair (the folded
    rectangle body); the caller is responsible for skipping the second
    (fold corner) path.
    """
    tag = path[0].tag if path else None

    if tag == "rect":
        return "rnote"

    if tag == "polygon":
        points = (path.attr("points") or "").strip()
        if not points:
            return None
        point_count = len([p for p in points.split(",") if p.strip()]) // 2
        if point_count == _HEXAGON_POINT_COUNT:
            return "hnote"
        return None

    if tag == "path":
        d_attr = path.attr("d") or ""
        # A note body path has 6 coordinate points (folded-corner rectangle).
        point_count = d_attr.count("L") + 1
        if point_count == 6:
            return "note"
        return None

    return None


def _is_note_stroke(shape: Pq) -> bool:
    """Return True if a shape uses the stroke PlantUML gives notes.

    Notes (of all three types) are always drawn with stroke-width:0.5 and
    stroke:#181818, regardless of fill color. Other same-tag elements that
    could otherwise collide with a note's shape signature use a different
    stroke-width: activation bars and group borders/tabs use 1.0 or 1.5.
    This check is independent of fill/color for the same forward-compat
    reason as classify_note_shape.
    """
    style = shape.attr("style") or ""
    return "stroke-width:0.5" in style


def _is_note_candidate(shape: Pq) -> bool:
    """Return True if a shape could plausibly be a note (any type).

    Excludes look-alikes that would otherwise collide with a note's shape
    signature:
    - Participant header rects: also plain <rect> with stroke-width:0.5,
      but always have rounded corners (rx/ry), which notes never have.
    - Activation bars and group borders/tabs: different stroke-width.
    - Message arrowheads: 4-point <polygon>, already excluded by
      classify_note_shape's point-count check, kept here as a fast path.
    """
    if not _is_note_stroke(shape):
        return False
    if shape.attr("rx") is not None or shape.attr("ry") is not None:
        return False  # participant header rect
    return True


def iter_note_shapes(svg: str) -> List[tuple[Pq, str]]:
    """Return (shape, note_type) for each note in SVG document order.

    Notes are identified by shape structure and stroke, never by fill
    color, so this keeps working once note colors are user-customizable.
    Iterates <path>, <polygon>, and <rect> together in document order
    since PlantUML interleaves note types with other diagram elements in
    source/render order.
    """
    d = Pq(svg)
    shapes = list(d("path, polygon, rect").items())
    # Box rects share the exact rnote signature (rect, stroke-width:0.5, no
    # rx/ry); they are told apart only by enclosing a participant header. Skip
    # them so a box is never counted/handled as an rnote.
    participant_bounds = participant_header_bounds(d)
    results: List[tuple[Pq, str]] = []
    i = 0

    while i < len(shapes):
        shape = shapes[i]
        if not _is_note_candidate(shape):
            i += 1
            continue

        if shape[0].tag == "rect" and is_box_rect(shape, participant_bounds):
            i += 1
            continue

        note_type = classify_note_shape(shape)
        if note_type is None:
            i += 1
            continue

        results.append((shape, note_type))
        if note_type == "note":
            i += 2  # skip the accompanying fold-corner path
        else:
            i += 1

    return results


def note_line_keyword(stripped_line: str) -> Optional[str]:
    """Return the note keyword ("note"/"hnote"/"rnote") a puml line starts
    with, or None if the line is not a note line.

    A note line starts with one of the note keywords, followed by either
    a space (e.g. "note over X : text") or an optional "#color" token
    before the rest of the syntax (e.g. "note #FFAAAA over X : text").
    Matching is prefix-based and independent of placement/color so it
    stays correct as new placement forms or the future color-editing
    feature are added.
    """
    for keyword in NOTE_KEYWORDS:
        if not stripped_line.startswith(keyword):
            continue
        rest = stripped_line[len(keyword) :]
        if rest.startswith(" ") or rest.startswith("#"):
            return keyword
    return None


def is_note_line(stripped_line: str) -> bool:
    """Return True if a puml line is a note/hnote/rnote line."""
    return note_line_keyword(stripped_line) is not None


def _find_note_line_index(puml: str, note_index: int) -> int:
    """Find the puml line index of the nth note (1-based).

    Matches "note", "hnote", and "rnote" lines uniformly.
    """
    lines = puml.splitlines()
    count = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if is_note_line(stripped):
            count += 1
            if count == note_index:
                return i
    return -1


def _shape_cy(shape: Pq) -> float:
    """Return the vertical center of a note shape, regardless of its tag.

    - <path> (note): first two numbers in `d` are the top-left corner's
      x,y; the fold-corner path's height is small enough that using the
      body path's top y (bounds start) matches the existing note ordering
      behavior used for insertion/hover-highlight.
    - <rect> (rnote): y + height / 2.
    - <polygon> (hnote): midpoint between the min and max y among points.
    """
    tag = shape[0].tag if shape else None

    if tag == "rect":
        y = float(shape.attr("y") or 0.0)
        height = float(shape.attr("height") or 0.0)
        return y + height / 2

    if tag == "polygon":
        points = (shape.attr("points") or "").strip()
        coords = [p for p in points.split(",") if p.strip()]
        ys = [float(coords[i]) for i in range(1, len(coords), 2)]
        if not ys:
            return 0.0
        return (min(ys) + max(ys)) / 2

    if tag == "path":
        d_attr = shape.attr("d") or ""
        parts = d_attr.split(",")
        if len(parts) >= 2:
            y_str = parts[1].split(" ")[0]
            try:
                return float(y_str)
            except ValueError:
                return 0.0
        return 0.0

    return 0.0


def extract_note_positions(svg: str, puml: str) -> List[tuple[float, int]]:
    """Extract (cy, line_index) for each note from SVG shape data.

    Identifies notes by shape (see iter_note_shapes), not fill color, so
    this keeps working once note colors become user-customizable.
    """
    positions = []
    for note_count, (shape, _note_type) in enumerate(iter_note_shapes(svg), start=1):
        cy = _shape_cy(shape)
        line_index = _find_note_line_index(puml, note_count)
        positions.append((cy, line_index))
    return positions


def resolve_color(new_color: Optional[str], existing_color: str) -> str:
    """Resolve an edit-request color value against the element's existing color.

    Centralizes the color-edit semantics shared by messages and notes:
    ``None`` leaves the existing color unchanged; an empty value or ``"none"``
    (the palette's default option) clears it; any other value replaces it. The
    returned token has no leading ``#`` (callers add it), matching the frontend
    palette option values.
    """
    if new_color is None:
        return existing_color
    token = new_color.strip()
    if token.lower() in ("", "none"):
        return ""
    return token.lstrip("#")


def escape_multiline_text(text: str) -> str:
    """Convert real newlines to a literal \\n so the text stays one PlantUML line."""
    return text.replace("\r\n", "\n").replace("\r", "\n").replace("\n", "\\n")


def unescape_multiline_text(text: str) -> str:
    """Convert literal \\n back to real newlines for display when editing."""
    return text.replace("\\n", "\n")


def find_insertion_index(
    messages: List[Message], svg: str, puml: str, y: float, lines: List[str]
) -> int:
    """Find the line index to insert a new element based on y-coordinate.

    Considers both messages and existing notes ordered by their SVG Y-position.
    """
    elements: List[tuple[float, int]] = []
    for msg in messages:
        elements.append((msg.cy, msg.index))
    elements.extend(extract_note_positions(svg, puml))
    elements.sort(key=lambda x: x[0])

    for cy, line_index in elements:
        if cy > y:
            return line_index

    # After all elements: insert before @enduml
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "@enduml":
            return i
    return len(lines)
