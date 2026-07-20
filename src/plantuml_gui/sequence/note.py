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

import re
from typing import Dict, List

from pyquery import PyQuery as Pq

from .classes import Diagram, Message
from .util import (
    NOTE_KEYWORDS,
    escape_multiline_text,
    extract_note_positions,
    find_insertion_index,
    find_note_region,
    iter_note_shapes,
    note_line_keyword,
    resolve_color,
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


def _resolve_note_region(
    puml: str, svg: str, svgelement: str
) -> tuple[List[str], int, int] | None:
    """Resolve the clicked note to ``(lines, start, end)`` or ``None``.

    ``start``/``end`` are the note's line range (see
    :func:`find_note_region`): equal for a single-line note, or the opening
    ``note`` line and its ``end note`` line for a block note. Shared by the
    getters and editors so the SVG is parsed and the note located once per
    lookup, and the not-found case is handled in a single place.
    """
    idx = index_of_clicked_note(svg, svgelement)
    start, end = find_note_region(puml, idx)
    if start == -1:
        return None
    return puml.splitlines(), start, end


def _leading_ws(line: str) -> str:
    """Return the leading whitespace of a line."""
    return line[: len(line) - len(line.lstrip())]


def _note_text_from_line(line: str) -> str:
    """Extract a single-line note's display text from its puml line (pure)."""
    colon_pos = line.find(": ")
    text = line[colon_pos + 2 :] if colon_pos != -1 else ""
    return unescape_multiline_text(text)


def _note_text_from_region(lines: List[str], start: int, end: int) -> str:
    """Extract a note's display text from its resolved line range.

    Single-line notes (``start == end``) keep their inline ``\\n``-escaped
    text; block notes return the body lines (between the opening line and the
    ``end note`` line) joined with real newlines.
    """
    if start == end:
        return _note_text_from_line(lines[start])
    return "\n".join(lines[start + 1 : end])


def _note_type_from_line(line: str) -> str:
    """Extract a note's keyword ("note"/"hnote"/"rnote") from its puml line.

    Falls back to "note" for an unrecognized line, matching
    _normalize_note_type's default so callers always get a valid type.
    """
    keyword = note_line_keyword(line.strip())
    return keyword if keyword is not None else "note"


def _swap_note_keyword(prefix: str, note_type: str) -> str:
    """Return ``prefix`` with its leading note keyword replaced by ``note_type``.

    Preserves any leading whitespace and the placement clause exactly. Returns
    the prefix unchanged when it has no recognizable note keyword or already
    uses ``note_type``.
    """
    current = note_line_keyword(prefix.strip())
    if current is None or current == note_type:
        return prefix
    return _leading_ws(prefix) + note_type + prefix.strip()[len(current) :]


# A note's optional background color is a whitespace-separated ``#token`` sitting
# at the end of the placement clause, right before the ``": "`` text separator
# (e.g. ``note over A #LightBlue : text``). Requiring a leading space keeps a
# ``#`` inside a participant name (``note over C#``) from being read as a color.
_NOTE_COLOR_RE = re.compile(r"\s#([0-9A-Za-z]+)\s*$")


def _split_prefix_color(prefix: str) -> tuple[str, str]:
    """Split a note line's pre-``": "`` prefix into ``(prefix_without_color, color)``.

    ``color`` has its leading ``#`` stripped (so it matches the frontend's
    palette option values) and is ``""`` when the prefix carries no color. The
    returned prefix keeps its leading whitespace but has the trailing color
    token (and its surrounding whitespace) removed.
    """
    match = _NOTE_COLOR_RE.search(prefix)
    if match:
        return prefix[: match.start()], match.group(1)
    return prefix.rstrip(), ""


def _note_color_from_line(line: str) -> str:
    """Extract a note's background color from its puml line (``""`` if none)."""
    colon_pos = line.find(": ")
    prefix = line[:colon_pos] if colon_pos != -1 else line
    _, color = _split_prefix_color(prefix)
    return color


def get_note_text(puml: str, svg: str, svgelement: str) -> str:
    """Get the text of the clicked note (single-line or block form)."""
    region = _resolve_note_region(puml, svg, svgelement)
    if region is None:
        return ""
    return _note_text_from_region(*region)


def get_note_type(puml: str, svg: str, svgelement: str) -> str:
    """Get the PlantUML keyword ("note"/"hnote"/"rnote") of the clicked note.

    Falls back to "note" if the note can't be found, matching
    _normalize_note_type's default so callers always get a valid type.
    """
    region = _resolve_note_region(puml, svg, svgelement)
    if region is None:
        return "note"
    lines, start, _ = region
    return _note_type_from_line(lines[start])


def get_note_text_and_type(
    puml: str, svg: str, svgelement: str
) -> tuple[str, str, str]:
    """Return (text, note_type, color) for the clicked note in one lookup.

    Resolves the note's puml line range once (parsing the SVG a single
    time) and derives all three fields, so callers needing them - like the
    /getSeqNoteText route - avoid a redundant parse. The type and color come
    from the opening ``note`` line for both single-line and block forms.
    Mirrors the individual functions' not-found defaults ("" text, "note"
    type, "" color).
    """
    region = _resolve_note_region(puml, svg, svgelement)
    if region is None:
        return "", "note", ""
    lines, start, end = region
    opening = lines[start]
    return (
        _note_text_from_region(lines, start, end),
        _note_type_from_line(opening),
        _note_color_from_line(opening),
    )


def edit_note(
    puml: str,
    svg: str,
    svgelement: str,
    text: str,
    note_type: str | None = None,
    color: str | None = None,
) -> str:
    """Edit the text of the clicked note, optionally changing its type/color.

    Handles both note forms: single-line (``note over A : text``) and block
    (``note over A`` ... ``end note``). For a block note the opening line
    carries the type/color and the body lines carry the text, so the incoming
    (possibly multi-line) text replaces the body while the opening and
    ``end note`` lines are preserved.

    note_type selects the PlantUML keyword ("note"/"hnote"/"rnote"). If
    omitted or unrecognized, the existing keyword is left unchanged (a
    text-only edit, matching the original behavior).

    color sets the note's background color (a ``#``-prefixed token placed at
    the end of the placement clause). ``None`` leaves any existing color
    untouched; an empty value or ``"none"`` removes it; any other value
    replaces it. Named colors and hex both work (a leading ``#`` is optional).
    """
    idx = index_of_clicked_note(svg, svgelement)
    start, end = find_note_region(puml, idx)
    if start == -1:
        return puml
    lines = puml.splitlines()
    opening = lines[start]
    is_block = end > start

    if is_block:
        # The whole opening line is the placement prefix (no inline text).
        prefix_raw = opening
    else:
        colon_pos = opening.find(": ")
        if colon_pos == -1:
            return puml
        prefix_raw = opening[:colon_pos]

    prefix, existing_color = _split_prefix_color(prefix_raw)

    if note_type is not None and note_type in NOTE_KEYWORDS:
        prefix = _swap_note_keyword(prefix, note_type)

    new_color = resolve_color(color, existing_color)
    new_prefix = prefix.rstrip()
    if new_color:
        new_prefix += f" #{new_color}"

    if is_block:
        # Real newlines in the incoming text become separate body lines; the
        # opening line (index ``start``) and the ``end note`` line (index
        # ``end``) are preserved. Body lines are written verbatim - the editor
        # flattens per-line indentation before every request, and PlantUML
        # ignores leading whitespace in a note body anyway.
        new_body = text.split("\n")
        lines[start:end] = [new_prefix, *new_body]
    else:
        lines[start] = new_prefix + " : " + escape_multiline_text(text)
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
    """Delete the clicked note (the whole ``note`` ... ``end note`` block for
    block-form notes, or the single line for inline notes)."""
    idx = index_of_clicked_note(svg, svgelement)
    start, end = find_note_region(puml, idx)
    if start == -1:
        return puml
    lines = puml.splitlines()
    del lines[start : end + 1]
    return "\n".join(lines)
