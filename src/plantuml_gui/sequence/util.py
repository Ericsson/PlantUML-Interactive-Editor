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

from .classes import Message


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
