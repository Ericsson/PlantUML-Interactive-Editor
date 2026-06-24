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

from .classes import Diagram, Message


def _find_insertion_index(messages: List[Message], y: float, lines: List[str]) -> int:
    """Find the line index to insert a new note based on y-coordinate."""
    for msg in messages:
        if msg.cy > y:
            return msg.index
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
    insert_at = _find_insertion_index(diagram.messages, y_position, lines)
    note_line = _build_note_line(participant, placement, text, second_participant)
    lines.insert(insert_at, note_line)
    return "\n".join(lines)
