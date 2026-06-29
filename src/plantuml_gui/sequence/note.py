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
from .util import _find_note_line_index, find_insertion_index

MESSAGE_NOTE_TOLERANCE = 10.0


def _find_nearest_message(
    messages: List[Message], y: float, x: float | None
) -> Message | None:
    """Find the message closest to y if within tolerance and x is within the message span."""
    closest = None
    min_dist = MESSAGE_NOTE_TOLERANCE
    for msg in messages:
        if msg.from_participant == msg.to_participant:
            continue  # self-messages have no horizontal span
        dist = abs(msg.cy - y)
        if dist >= min_dist:
            continue
        if x is not None:
            left_cx = min(msg.from_participant.cx, msg.to_participant.cx)
            right_cx = max(msg.from_participant.cx, msg.to_participant.cx)
            if not (left_cx <= x <= right_cx):
                continue
        min_dist = dist
        closest = msg
    return closest


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
    x_position: float | None = None,
) -> str:
    """Add a note at the correct Y-position in the sequence diagram.

    If placement is 'left' or 'right' and the y_position is close to an
    existing message, and x_position falls within the message's horizontal
    span, uses message-attached syntax (note left/right : text) and inserts
    immediately after that message.
    """
    if not text:
        return puml

    diagram = Diagram.from_svg(svg, puml)
    lines = puml.splitlines()

    # Check if we should attach to a nearby message
    if placement in ("left", "right"):
        nearest = _find_nearest_message(diagram.messages, y_position, x_position)
        if nearest:
            note_line = f"note {placement} : {text}"
            lines.insert(nearest.index + 1, note_line)
            return "\n".join(lines)

    insert_at = find_insertion_index(diagram.messages, svg, puml, y_position, lines)
    note_line = _build_note_line(participant, placement, text, second_participant)
    lines.insert(insert_at, note_line)
    return "\n".join(lines)


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
