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

from .classes import ARROW_RE, Diagram, Participant
from .util import (
    escape_multiline_text,
    find_insertion_index,
    resolve_color,
    unescape_multiline_text,
)


def _find_closest_participant(
    participants: List[Participant], target_cx: int
) -> Participant:
    """Find the participant with the closest cx value to the target_cx."""
    min_distance = float("inf")
    closest = participants[0]

    for participant in participants:
        distance = abs(participant.cx - target_cx)
        if distance < min_distance:
            min_distance = distance
            closest = participant

    return closest


def add_message(
    puml: str,
    svg: str,
    message: str,
    firstcoordinates: List[int],
    secondcoordinates: List[int],
    arrow_type: str = "->",
):
    """Add a message between two participants at the correct y-position."""
    first_x, first_y = firstcoordinates
    second_x, _second_y = secondcoordinates

    diagram = Diagram.from_svg(svg, puml)
    sender = _find_closest_participant(diagram.participants, first_x)
    reciever = _find_closest_participant(diagram.participants, second_x)

    lines = puml.splitlines()
    insert_at = find_insertion_index(diagram.messages, svg, puml, first_y, lines)
    message = escape_multiline_text(message)
    lines.insert(insert_at, f"{sender.name} {arrow_type} {reciever.name}: {message}")
    return "\n".join(lines)


def _svg_element_matches(element: Pq, clicked: Pq) -> bool:
    """Check if two SVG elements match by comparing tag and key attributes."""
    tag = element[0].tag
    clicked_tag = clicked[0].tag
    if tag != clicked_tag:
        return False
    if tag == "polygon":
        return element.attr("points") == clicked.attr("points")
    if tag == "line":
        return (
            element.attr("x1") == clicked.attr("x1")
            and element.attr("x2") == clicked.attr("x2")
            and element.attr("y1") == clicked.attr("y1")
            and element.attr("y2") == clicked.attr("y2")
        )
    if tag == "text":
        return element.attr("x") == clicked.attr("x") and element.attr(
            "y"
        ) == clicked.attr("y")
    return False


def _is_continuation_text(element: Pq) -> bool:
    """Return True if an SVG element is a message text continuation line.

    A multi-line message (``A -> B: a\\nb``) renders its text as several
    <text> siblings following the message's shape group. They are plain
    message text (font-size 13, not bold - bold marks a group keyword/label)
    and, unlike the group's first line, aren't part of any tag pattern, so
    they must be explicitly attributed to their message.
    """
    if element[0].tag != "text":
        return False
    return element.attr("font-size") == "13" and element.attr("font-weight") != "bold"


def index_of_clicked_message(svg: str, svgelement: str) -> int:
    """Find the 1-based index of the message containing the clicked SVG element.

    Iterates SVG elements using the same grouping logic as Diagram._parse_messages,
    checking if the clicked element matches any element in each message group.
    Continuation text lines of a multi-line message (rendered as extra <text>
    siblings after the group) are attributed to that same message, so a click on
    any line of the text resolves to it.
    """
    d = Pq(svg)
    clicked = Pq(svgelement)
    elements = list(d("*").items())
    i = 0
    message_index = 0

    while i < len(elements):
        group = elements[i : i + 5]
        tags = [el[0].tag for el in group]

        if tags[:4] == ["polygon", "polygon", "line", "text"]:
            members = list(group[:4])
            j = i + 4
        elif tags[:5] == ["line", "line", "line", "polygon", "text"]:
            members = list(group[:5])
            j = i + 5
        elif tags[:3] == ["polygon", "line", "text"]:
            members = list(group[:3])
            j = i + 3
        else:
            i += 1
            continue

        message_index += 1
        # Attribute any trailing continuation text lines to this message. The
        # next message always starts with a polygon/line and a note with its
        # shape, so a bare <text> here can only be this message's extra line.
        while j < len(elements) and _is_continuation_text(elements[j]):
            members.append(elements[j])
            j += 1
        for el in members:
            if _svg_element_matches(el, clicked):
                return message_index
        i = j

    return -1


def _arrow_color_from_line(line: str) -> str:
    """Extract a message's arrow color from its puml line (``""`` if none).

    Uses the shared ``ARROW_RE`` (defined in ``classes.py``) so message-line
    detection and color read/rewrite recognize the exact same arrow shapes.
    """
    colon_pos = line.find(": ")
    prefix = line[:colon_pos] if colon_pos != -1 else line
    match = ARROW_RE.search(prefix)
    if not match:
        return ""
    color_match = re.search(r"\[#([^\]]+)\]", match.group(0))
    return color_match.group(1) if color_match else ""


def _apply_arrow_color(arrow: str, color: str) -> str:
    """Return ``arrow`` with its color set to ``color`` (``""`` removes it).

    Any existing ``[#...]`` token is stripped first. A non-empty color is
    re-inserted as ``[#color]`` immediately after the arrow's first dash, which
    is PlantUML's canonical placement (``->`` -> ``-[#red]>``, ``-->`` ->
    ``-[#red]->``, ``<->`` -> ``<-[#red]->``).
    """
    arrow = re.sub(r"\[#[^\]]*\]", "", arrow)
    if not color:
        return arrow
    dash = arrow.find("-")
    if dash == -1:
        return arrow
    return f"{arrow[: dash + 1]}[#{color}]{arrow[dash + 1 :]}"


def _set_arrow_color(prefix: str, color: str) -> str:
    """Rewrite the arrow color in a message line's pre-``": "`` prefix."""
    match = ARROW_RE.search(prefix)
    if not match:
        return prefix
    new_arrow = _apply_arrow_color(match.group(0), color)
    return prefix[: match.start()] + new_arrow + prefix[match.end() :]


def _clicked_message_line(puml: str, svg: str, svgelement: str) -> str | None:
    """Return the puml source line of the clicked message, or ``None``.

    Shared by the label/color getters so the SVG is parsed and the clicked
    message resolved in one place. Returns ``None`` when the clicked element
    doesn't resolve to a message (``index_of_clicked_message`` returned -1), so
    callers never index ``messages[-1 - 1]`` and read an unrelated message.
    """
    diagram = Diagram.from_svg(svg, puml)
    idx = index_of_clicked_message(svg, svgelement)
    if idx == -1:
        return None
    return puml.splitlines()[diagram.messages[idx - 1].index]


def _message_text_from_line(line: str) -> str:
    """Extract a message's display text from its puml line (pure)."""
    colon_pos = line.find(": ")
    text = line[colon_pos + 2 :] if colon_pos != -1 else ""
    return unescape_multiline_text(text)


def get_message_text(puml: str, svg: str, svgelement: str) -> str:
    """Get the label text of the clicked message (``""`` if not a message)."""
    line = _clicked_message_line(puml, svg, svgelement)
    return _message_text_from_line(line) if line is not None else ""


def get_message_color(puml: str, svg: str, svgelement: str) -> str:
    """Get the arrow color of the clicked message (``""`` if uncolored/none)."""
    line = _clicked_message_line(puml, svg, svgelement)
    return _arrow_color_from_line(line) if line is not None else ""


def get_message_label(puml: str, svg: str, svgelement: str) -> tuple[str, str]:
    """Return (text, color) for the clicked message in one lookup.

    Resolves the message's puml line once (parsing the SVG a single time) and
    derives both fields, so the /getMessageText route avoids a redundant parse.
    Returns ``("", "")`` when the clicked element isn't a message.
    """
    line = _clicked_message_line(puml, svg, svgelement)
    if line is None:
        return "", ""
    return _message_text_from_line(line), _arrow_color_from_line(line)


def edit_message_text(
    puml: str, svg: str, svgelement: str, text: str, color: str | None = None
) -> str:
    """Edit the label text of the clicked message, optionally its arrow color.

    color sets the message arrow's color as a ``[#color]`` token. ``None``
    leaves any existing color unchanged; an empty value or ``"none"`` removes
    it; any other value replaces it. Named colors and hex both work.
    """
    diagram = Diagram.from_svg(svg, puml)
    idx = index_of_clicked_message(svg, svgelement)
    if idx == -1:
        return puml  # clicked element isn't a message; leave puml unchanged
    message = diagram.messages[idx - 1]
    lines = puml.splitlines()
    line = lines[message.index]
    # Replace text after ": "
    colon_pos = line.find(": ")
    if colon_pos == -1:
        return puml
    prefix = line[:colon_pos]
    if color is not None:
        existing = _arrow_color_from_line(line)
        prefix = _set_arrow_color(prefix, resolve_color(color, existing))
    lines[message.index] = prefix + ": " + escape_multiline_text(text)
    return "\n".join(lines)


def delete_message(puml: str, svg: str, svgelement: str) -> str:
    """Delete the clicked message (no-op if the element isn't a message)."""
    diagram = Diagram.from_svg(svg, puml)
    idx = index_of_clicked_message(svg, svgelement)
    if idx == -1:
        return puml  # clicked element isn't a message; leave puml unchanged
    message = diagram.messages[idx - 1]
    lines = puml.splitlines()
    del lines[message.index]
    return "\n".join(lines)


def get_message_positions(puml: str, svg: str) -> List[Dict[str, object]]:
    """Return message positions for frontend snapping during activation-bar gestures.

    Each entry contains the SVG Y-coordinate (``cy``), the puml line index
    (``index``), and the message label text (``text``).  The frontend stores
    these as ``messagePositions`` and uses them to snap the start/end of an
    activation bar to the nearest message line.
    """
    diagram = Diagram.from_svg(svg, puml)
    lines = puml.splitlines()
    positions = []
    for msg in diagram.messages:
        colon_pos = lines[msg.index].find(": ")
        text = lines[msg.index][colon_pos + 2 :] if colon_pos != -1 else ""
        positions.append(
            {"cy": msg.cy, "index": msg.index, "text": unescape_multiline_text(text)}
        )
    return positions
