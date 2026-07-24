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
from dataclasses import dataclass, field
from typing import Dict, List

from pyquery import PyQuery as Pq  # pragma: no cover

# Style PlantUML gives participant header rects. Used to distinguish them from
# other rects in the SVG (e.g. activation bars, which use stroke-width:1.0).
# Matches the identification used by the frontend's checkIfParticipant.
PARTICIPANT_RECT_STYLE = "stroke:#181818;stroke-width:0.5;"

# A message arrow, matched so its optional embedded color bracket can be read or
# rewritten. The arrow either starts with ``<`` (a reverse/bidirectional head)
# or ends with a head (``>``, ``x`` or ``o``); either way it contains at least
# one dash. Requiring a head keeps a lone ``-`` inside a participant name (e.g.
# ``Web-Server``) from being mistaken for the arrow. An existing ``[#color]``
# token may sit anywhere among the dashes.
#
# Lives here, in the base module, so both message parsing (index assignment,
# below) and message.py's color read/rewrite share one arrow definition and
# cannot drift apart. classes.py imports nothing from the package, so message.py
# importing this back is cycle-free.
ARROW_RE = re.compile(
    r"<{1,2}[-\\/]*(?:\[#[^\]]*\])?[-\\/]*(?:>{1,2}|[xo])?"  # starts with '<'
    r"|[-\\/]+(?:\[#[^\]]*\])?[-\\/]*(?:>{1,2}|[xo])"  # ends with a head
)


def is_message_line(line: str) -> bool:
    """Return True if a puml line is a message (``sender <arrow> receiver: text``).

    The arrow always precedes the ``": "`` text separator, so only the part
    before the first colon is inspected. Reverse (``<-``), bidirectional
    (``<->``), dotted, self, and colored (``-[#red]>``) arrows are all matched
    via :data:`ARROW_RE`.

    Requiring a real dash in the matched arrow rejects two look-alikes:
    non-message lines whose free text happens to contain a ``<`` before a colon
    (e.g. a group label ``alt <size:12>...``), which :data:`ARROW_RE` would
    otherwise match as a bare ``<``; and notes/labels that carry their arrow
    only after the colon.
    """
    colon_pos = line.find(":")
    if colon_pos == -1:
        return False
    match = ARROW_RE.search(line[:colon_pos])
    return match is not None and "-" in match.group(0)


def is_participant_rect(rect: Pq) -> bool:
    """Return True if an SVG rect is a participant header (not an activation
    bar or an rnote, which shares the same stroke-width:0.5 style but never
    has rounded corners).
    """
    if (rect.attr("style") or "") != PARTICIPANT_RECT_STYLE:
        return False
    return rect.attr("rx") is not None and rect.attr("ry") is not None


def participant_header_bounds(svg: Pq) -> List[Dict[str, float]]:
    """Return the bounding box of every participant header rect in the SVG.

    Shared participant geometry: used by box detection (a box rect is the one
    that encloses a participant header) and by note detection (to exclude box
    rects, which share the rnote signature).
    """
    bounds: List[Dict[str, float]] = []
    for rect in svg("rect").items():
        if not is_participant_rect(rect):
            continue
        bounds.append(
            {
                "x": float(rect.attr("x")),
                "y": float(rect.attr("y")),
                "width": float(rect.attr("width")),
                "height": float(rect.attr("height")),
            }
        )
    return bounds


def rect_encloses(rect: Pq, bound: Dict[str, float]) -> bool:
    """Return True if ``rect`` fully contains the participant ``bound``."""
    x = float(rect.attr("x"))
    y = float(rect.attr("y"))
    width = float(rect.attr("width"))
    height = float(rect.attr("height"))
    return (
        x <= bound["x"]
        and bound["x"] + bound["width"] <= x + width
        and y <= bound["y"]
        and bound["y"] + bound["height"] <= y + height
    )


def _participant_at(participants: List["Participant"], x: float) -> "Participant":
    """Return the participant whose header spans ``x``, else the closest by cx.

    Falling back to the nearest participant keeps message parsing robust when an
    arrow endpoint lands slightly outside a header box (for example when an
    activation bar shifts where the arrow meets the lifeline), instead of
    raising and turning the whole request into a 500. Callers only parse
    messages after participants are parsed, so the list is non-empty here.
    """
    for participant in participants:
        if participant.contains_x(x):
            return participant
    return min(participants, key=lambda p: abs(p.cx - x))


@dataclass
class Participant:
    name: str
    cx: float
    cy: float
    x_origin: float = 0.0
    width: float = 0.0
    index: int = -1  # default

    def contains_x(self, x_val: float) -> bool:
        return self.x_origin <= x_val <= self.x_origin + self.width

    def __eq__(self, other):
        return isinstance(other, Participant) and self.cx == other.cx

    @classmethod
    def from_svg(cls, rect: Pq, text: Pq):
        x = float(rect.attr("x"))
        y = float(rect.attr("y"))
        width = float(rect.attr("width"))
        height = float(rect.attr("height"))

        cx = x + width / 2
        cy = y + height / 2

        name = text.text()

        return cls(name, cx, cy, x, width)


@dataclass
class Message:
    from_participant: Participant
    to_participant: Participant
    message: str
    cy: float
    index: int = -1

    @classmethod
    def from_normal_svg(
        cls, polygon: Pq, line: Pq, text: Pq, participants: List[Participant]
    ):
        """for normal messages <-, <--, -->, ->"""

        # arrow_x is the average x-value of the message arrow/polygon (used to find 'to')
        points = polygon.attr("points")
        coords = [tuple(map(float, p.split(","))) for p in points.strip().split()]
        arrow_x = sum(p[0] for p in coords) / len(coords)

        # x1 and x2 are the two points of the line, the one furthest away from the arrow point is the start of it.
        x1 = float(line.attr("x1"))
        x2 = float(line.attr("x2"))

        # Determine which x is furthest from arrow_x
        start_x = x1 if abs(x1 - arrow_x) > abs(x2 - arrow_x) else x2
        cy = float(line.attr("y1"))

        message = text.text()

        from_participant = _participant_at(participants, start_x)
        to_participant = _participant_at(participants, arrow_x)

        return cls(from_participant, to_participant, message, cy)

    @classmethod
    def from_bidirectional_svg(
        cls, poly1: Pq, poly2: Pq, line: Pq, text: Pq, participants: List["Participant"]
    ):
        """for bidirectional messages <-> or <-->"""

        x1 = float(line.attr("x1"))
        x2 = float(line.attr("x2"))
        cy = float(line.attr("y1"))

        message = text.text()
        start_x = x1
        to_x = x2

        from_participant = _participant_at(participants, start_x)
        to_participant = _participant_at(participants, to_x)

        return cls(
            from_participant=from_participant,
            to_participant=to_participant,
            message=message,
            cy=cy,
        )

    @classmethod
    def from_self_svg(
        cls,
        line1: Pq,
        line2: Pq,
        line3: Pq,
        polygon: Pq,
        text: Pq,
        participants: List["Participant"],
    ):
        """for self messages"""

        # First line is the horizontal start of the loop
        start_x = float(line1.attr("x1"))
        cy = float(line1.attr("y1"))

        message = text.text()

        from_participant = _participant_at(participants, start_x)

        return cls(
            from_participant=from_participant,
            to_participant=from_participant,
            message=message,
            cy=cy,
        )


@dataclass
class Diagram:
    participants: List[Participant] = field(default_factory=list)
    messages: List[Message] = field(default_factory=list)

    @classmethod
    def from_svg(cls, svgtext: str, puml: str):
        svg = Pq(svgtext)
        diagram = cls()

        diagram._parse_participants(svg, puml)
        diagram._parse_messages(svg, puml)

        return diagram

    def _parse_participants(self, svg, puml):
        """Extract unique participants based on `cx` value."""
        unique_participants: Dict[int, Participant] = {}

        for rect in svg("rect").items():
            if not is_participant_rect(rect):
                continue  # skip activation bars and other non-participant rects
            text = rect.next()
            participant = Participant.from_svg(rect, text)

            if participant.cx not in unique_participants:
                unique_participants[participant.cx] = participant

        self.participants.extend(unique_participants.values())
        self._assign_participant_indexes(puml)

    def _assign_participant_indexes(self, puml: str):
        """Assign indexes in the puml code to corresponding participant"""
        lines = puml.splitlines()

        participant_lines = [
            i for i, line in enumerate(lines) if line.startswith("participant")
        ]

        for i, line_index in enumerate(participant_lines):
            if i < len(self.participants):
                self.participants[i].index = line_index

    def _parse_messages(self, svg, puml):
        """Parse messages from svg"""
        elements = list(svg("*").items())
        i = 0
        parsed_messages = []

        while i < len(elements):
            group = elements[i : i + 5]
            tags = [el[0].tag for el in group]

            if tags[:4] == ["polygon", "polygon", "line", "text"]:
                polygon1, polygon2, line, text = group[:4]
                parsed_messages.append(
                    Message.from_bidirectional_svg(
                        polygon1, polygon2, line, text, self.participants
                    )
                )
                i += 4
            elif tags[:5] == ["line", "line", "line", "polygon", "text"]:
                line1, line2, line3, polygon, text = group[:5]
                parsed_messages.append(
                    Message.from_self_svg(
                        line1, line2, line3, polygon, text, self.participants
                    )
                )
                i += 5
            elif tags[:3] == ["polygon", "line", "text"]:
                polygon, line, text = group[:3]
                parsed_messages.append(
                    Message.from_normal_svg(polygon, line, text, self.participants)
                )
                i += 3
            else:
                i += 1

        self.messages.extend(parsed_messages)
        self._assign_message_indexes(puml)

    def _assign_message_indexes(self, puml: str):
        """Assign indexes in the puml code to corresponding message"""
        lines = puml.splitlines()

        # Find all lines that represent messages, in source order. This must
        # count the same arrows the SVG parser does (both directions), or the
        # message list and the source lines fall out of alignment.
        message_lines = [i for i, line in enumerate(lines) if is_message_line(line)]

        # Messages are already in occuring order
        for i, line_index in enumerate(message_lines):
            if i < len(self.messages):
                self.messages[i].index = line_index
