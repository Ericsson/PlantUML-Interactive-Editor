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

from typing import List

from pyquery import PyQuery as Pq

from .classes import Diagram, Message


def _extract_note_positions(svg: str, puml: str) -> List[tuple[float, int]]:
    """Extract (cy, line_index) for each note from SVG path data."""
    d = Pq(svg)
    paths = list(d("path").items())
    positions = []
    note_count = 0

    for i, path in enumerate(paths):
        if path.attr("fill") != "#FEFFDD":
            continue
        if i + 1 < len(paths) and paths[i + 1].attr("fill") == "#FEFFDD":
            # Extract Y from path d attribute: "M5,80.4297 L..."
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

    return positions


def _find_insertion_index(
    messages: List[Message], svg: str, puml: str, y: float, lines: List[str]
) -> int:
    """Find the line index to insert a new element based on y-coordinate.

    Considers both messages and existing notes ordered by their SVG Y-position.
    """
    # Collect all elements with (cy, line_index)
    elements: List[tuple[float, int]] = []
    for msg in messages:
        elements.append((msg.cy, msg.index))
    elements.extend(_extract_note_positions(svg, puml))
    elements.sort(key=lambda x: x[0])

    for cy, line_index in elements:
        if cy > y:
            return line_index

    # After all elements: insert before @enduml
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "@enduml":
            return i
    return len(lines)


def _build_note_line(
    participant: str,
    placement: str,
    text: str,
    second_participant: str | None = None,
) -> str:
    """Build the PlantUML note syntax string."""
    if placement == "over":
        return f"note over {participant} : {text}"
    if placement == "left":
        return f"note left of {participant} : {text}"
    if placement == "right":
        return f"note right of {participant} : {text}"
    if placement == "spanning":
        return f"note over {participant}, {second_participant} : {text}"
    return ""


def add_note(
    puml: str,
    svg: str,
    participant: str,
    placement: str,
    text: str,
    y_position: float,
    second_participant: str | None = None,
) -> str:
    """Add a note at the correct Y-position in the sequence diagram."""
    if not text:
        return puml

    diagram = Diagram.from_svg(svg, puml)
    lines = puml.splitlines()
    insert_at = _find_insertion_index(diagram.messages, svg, puml, y_position, lines)
    note_line = _build_note_line(participant, placement, text, second_participant)
    lines.insert(insert_at, note_line)
    return "\n".join(lines)


def _find_note_line_index(puml: str, note_index: int) -> int:
    """Find the puml line index of the nth note (1-based)."""
    lines = puml.splitlines()
    count = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("note "):
            count += 1
            if count == note_index:
                return i
    return -1


def index_of_clicked_note(svg: str, svgelement: str) -> int:
    """Find the 1-based index of the clicked note in the SVG.

    Notes are rendered as path elements with fill #FEFFDD. Each note
    has two paths (body + fold corner). We count the body paths (those
    followed by another #FEFFDD path) and match by the d attribute.
    """
    clicked = Pq(svgelement)
    clicked_d = clicked.attr("d")

    d = Pq(svg)
    paths = list(d("path").items())
    count = 0

    for i, path in enumerate(paths):
        if path.attr("fill") != "#FEFFDD":
            continue
        # A note body path is followed by the fold corner path
        if i + 1 < len(paths) and paths[i + 1].attr("fill") == "#FEFFDD":
            count += 1
            if path.attr("d") == clicked_d:
                return count

    return -1


def get_note_text(puml: str, svg: str, svgelement: str) -> str:
    """Get the text of the clicked note."""
    idx = index_of_clicked_note(svg, svgelement)
    line_index = _find_note_line_index(puml, idx)
    line = puml.splitlines()[line_index]
    colon_pos = line.find(": ")
    return line[colon_pos + 2 :] if colon_pos != -1 else ""


def edit_note(puml: str, svg: str, svgelement: str, text: str) -> str:
    """Edit the text of the clicked note."""
    idx = index_of_clicked_note(svg, svgelement)
    line_index = _find_note_line_index(puml, idx)
    lines = puml.splitlines()
    line = lines[line_index]
    colon_pos = line.find(": ")
    if colon_pos != -1:
        lines[line_index] = line[: colon_pos + 2] + text
    return "\n".join(lines)


def delete_note(puml: str, svg: str, svgelement: str) -> str:
    """Delete the clicked note."""
    idx = index_of_clicked_note(svg, svgelement)
    line_index = _find_note_line_index(puml, idx)
    lines = puml.splitlines()
    del lines[line_index]
    return "\n".join(lines)
