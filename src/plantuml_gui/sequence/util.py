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

from .classes import Message

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


def extract_note_positions(svg: str, puml: str) -> List[tuple[float, int]]:
    """Extract (cy, line_index) for each note from SVG path data."""
    d = Pq(svg)
    paths = list(d("path").items())
    positions = []
    note_count = 0
    i = 0

    while i < len(paths):
        path = paths[i]
        if path.attr("fill") != "#FEFFDD":
            i += 1
            continue
        if i + 1 < len(paths) and paths[i + 1].attr("fill") == "#FEFFDD":
            d_attr = path.attr("d") or ""
            parts = d_attr.split(",")
            if len(parts) >= 2:
                y_str = parts[1].split(" ")[0]
                try:
                    cy = float(y_str)
                except ValueError:
                    cy = 0.0
            else:
                cy = 0.0
            note_count += 1
            line_index = _find_note_line_index(puml, note_count)
            positions.append((cy, line_index))
            i += 2  # skip the fold corner path
        else:
            i += 1

    return positions


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
