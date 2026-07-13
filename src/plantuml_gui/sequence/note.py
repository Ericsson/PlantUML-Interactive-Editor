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

from typing import Dict, List

from pyquery import PyQuery as Pq

from .classes import Diagram, Message
from .util import (
    NOTE_KEYWORDS,
    _find_note_line_index,
    escape_multiline_text,
    extract_note_positions,
    find_insertion_index,
    iter_note_shapes,
    note_line_keyword,
    unescape_multiline_text,
)

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


def _normalize_note_type(note_type: str | None) -> str:
    """Validate and default a note_type value from an untrusted request.

    Falls back to "note" for missing or unrecognized values, since the
    request body comes directly from client JS.
    """
    if note_type in NOTE_KEYWORDS:
        return note_type
    return "note"


def _build_note_line(
    participant: str,
    placement: str,
    text: str,
    second_participant: str | None = None,
    note_type: str = "note",
) -> str:
    """Build the PlantUML note syntax string."""
    if placement == "over":
        return f"{note_type} over {participant} : {text}"
    if placement == "left":
        return f"{note_type} left of {participant} : {text}"
    if placement == "right":
        return f"{note_type} right of {participant} : {text}"
    if placement == "spanning":
        return f"{note_type} over {participant}, {second_participant} : {text}"
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
    note_type: str | None = None,
) -> str:
    """Add a note at the correct Y-position in the sequence diagram.

    note_type selects the PlantUML keyword ("note", "hnote", or "rnote"),
    defaulting to "note" for missing/unrecognized values. All three types
    support the same placement grammar identically.

    If placement is 'left' or 'right' and the y_position is close to an
    existing message, and x_position falls within the message's horizontal
    span, uses message-attached syntax (note left/right : text) and inserts
    immediately after that message.
    """
    if not text:
        return puml

    note_type = _normalize_note_type(note_type)
    text = escape_multiline_text(text)
    diagram = Diagram.from_svg(svg, puml)
    lines = puml.splitlines()

    # Check if we should attach to a nearby message
    if placement in ("left", "right"):
        nearest = _find_nearest_message(diagram.messages, y_position, x_position)
        if nearest:
            note_line = f"{note_type} {placement} : {text}"
            lines.insert(nearest.index + 1, note_line)
            return "\n".join(lines)

    insert_at = find_insertion_index(diagram.messages, svg, puml, y_position, lines)
    note_line = _build_note_line(
        participant, placement, text, second_participant, note_type
    )
    lines.insert(insert_at, note_line)
    return "\n".join(lines)


def _shapes_match(a: Pq, b: Pq) -> bool:
    """Return True if two SVG shapes represent the same note element.

    Compares by tag-appropriate identity attribute (never fill color):
    `d` for <path> (note), `points` for <polygon> (hnote), and x/y/width/
    height for <rect> (rnote).
    """
    tag_a = a[0].tag if a else None
    tag_b = b[0].tag if b else None
    if tag_a != tag_b:
        return False

    if tag_a == "path":
        return a.attr("d") == b.attr("d")
    if tag_a == "polygon":
        return a.attr("points") == b.attr("points")
    if tag_a == "rect":
        return (
            a.attr("x") == b.attr("x")
            and a.attr("y") == b.attr("y")
            and a.attr("width") == b.attr("width")
            and a.attr("height") == b.attr("height")
        )
    return False


def index_of_clicked_note(svg: str, svgelement: str) -> int:
    """Find the 1-based index of the clicked note in the SVG.

    Identifies notes by shape (see iter_note_shapes), not fill color, so
    this keeps working once note colors become user-customizable.
    """
    clicked = Pq(svgelement)

    for count, (shape, _note_type) in enumerate(iter_note_shapes(svg), start=1):
        if _shapes_match(shape, clicked):
            return count

    return -1


def get_note_text(puml: str, svg: str, svgelement: str) -> str:
    """Get the text of the clicked note."""
    idx = index_of_clicked_note(svg, svgelement)
    line_index = _find_note_line_index(puml, idx)
    line = puml.splitlines()[line_index]
    colon_pos = line.find(": ")
    text = line[colon_pos + 2 :] if colon_pos != -1 else ""
    return unescape_multiline_text(text)


def get_note_type(puml: str, svg: str, svgelement: str) -> str:
    """Get the PlantUML keyword ("note"/"hnote"/"rnote") of the clicked note.

    Falls back to "note" if the note can't be found, matching
    _normalize_note_type's default so callers always get a valid type.
    """
    idx = index_of_clicked_note(svg, svgelement)
    line_index = _find_note_line_index(puml, idx)
    if line_index == -1:
        return "note"
    line = puml.splitlines()[line_index]
    keyword = note_line_keyword(line.strip())
    return keyword if keyword is not None else "note"


def edit_note(
    puml: str, svg: str, svgelement: str, text: str, note_type: str | None = None
) -> str:
    """Edit the text of the clicked note, optionally changing its type.

    note_type selects the PlantUML keyword ("note"/"hnote"/"rnote"). If
    omitted or unrecognized, the existing keyword is left unchanged (a
    text-only edit, matching the original behavior).
    """
    idx = index_of_clicked_note(svg, svgelement)
    line_index = _find_note_line_index(puml, idx)
    lines = puml.splitlines()
    line = lines[line_index]
    colon_pos = line.find(": ")
    if colon_pos == -1:
        return puml

    new_line = line[: colon_pos + 2] + escape_multiline_text(text)

    if note_type is not None and note_type in NOTE_KEYWORDS:
        current_keyword = note_line_keyword(line.strip())
        if current_keyword is not None and current_keyword != note_type:
            # Replace only the leading keyword, preserving any leading
            # whitespace, the placement clause, and an optional #color
            # token exactly as they were.
            stripped = new_line.strip()
            leading_ws = new_line[: len(new_line) - len(stripped)]
            new_line = leading_ws + note_type + stripped[len(current_keyword) :]

    lines[line_index] = new_line
    return "\n".join(lines)


def get_note_positions(puml: str, svg: str) -> List[Dict[str, object]]:
    """Return note positions for frontend hover highlighting.

    Notes are ordered by SVG document order, which matches puml source
    order, so the frontend can also match by ordinal.
    """
    return [
        {"cy": cy, "index": line_index}
        for cy, line_index in extract_note_positions(svg, puml)
    ]


def delete_note(puml: str, svg: str, svgelement: str) -> str:
    """Delete the clicked note."""
    idx = index_of_clicked_note(svg, svgelement)
    line_index = _find_note_line_index(puml, idx)
    lines = puml.splitlines()
    del lines[line_index]
    return "\n".join(lines)
