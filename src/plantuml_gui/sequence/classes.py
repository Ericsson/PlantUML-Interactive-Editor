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

# A participant declaration, split into the parts a rename must treat
# differently:
#   name  -- the displayed name, which is what the SVG gives us to match on:
#            the quoted text when present (``participant "Long name" as A``),
#            otherwise the bare token (``participant Alice``)
#   alias -- the ``as X`` token when present; this, not the displayed name, is
#            what the diagram body refers to
#   rest  -- everything after the name and alias (``order 10``, ``#lightblue``,
#            ``<<stereotype>>``), captured verbatim so a rewrite never drops a
#            modifier it does not understand
#
# ``rest`` is deliberately left unanchored: a trailing ``$`` would be redundant
# on the single lines this is fed (greedy ``.*`` already runs to the end), but it
# would give the pattern a tail that can fail. On a name holding a newline the
# engine would then retry ``.*`` at every position it can backtrack ``[^\s#]+``
# to, which is quadratic in the name's length. Without the anchor the tail always
# succeeds on first try, so no backtracking is possible.

PARTICIPANT_DECLARATION_RE = re.compile(
    r'^participant\s+(?:"(?P<quoted>[^"]*)"|(?P<bare>[^\s#]+))'
    r'(?:\s+as\s+(?:"(?P<quoted_alias>[^"]*)"|(?P<bare_alias>[^\s#]+)))?'
    r"(?P<rest>.*)"
)


@dataclass(frozen=True)
class ParticipantDeclaration:
    """The structural parts of a single participant declaration line."""

    name: str
    alias: str | None
    rest: str
    quoted: bool

    @property
    def reference_name(self) -> str:
        """The token the diagram body uses to refer to this participant.

        The alias when the declaration has one, otherwise the displayed name.
        """
        return self.alias or self.name


def parse_participant_declaration(line: str) -> ParticipantDeclaration | None:
    """Split a puml line into declaration parts, or None if it is not one."""
    match = PARTICIPANT_DECLARATION_RE.match(line.strip())
    if match is None:
        return None
    quoted = match.group("quoted")
    alias = match.group("quoted_alias")
    if alias is None:
        alias = match.group("bare_alias")
    return ParticipantDeclaration(
        name=quoted if quoted is not None else match.group("bare"),
        alias=alias,
        rest=match.group("rest"),
        quoted=quoted is not None,
    )


def participant_declarations(puml: str) -> List[tuple[int, ParticipantDeclaration]]:
    """Every participant declaration in source order, with its line index."""
    return [
        (line_index, declaration)
        for line_index, line in enumerate(puml.splitlines())
        if (declaration := parse_participant_declaration(line)) is not None
    ]


# Escapes PlantUML breaks a label on. They differ only in line alignment.
_LINE_BREAK_ESCAPE_RE = re.compile(r"\\[nrl]")


def normalized_display_name(name: str) -> str:
    """A displayed name reduced to the form two spellings of it share.

    A name reaches us two ways that render alike but are written differently: the
    puml declaration spells a break as ``\\n``, ``\\r`` or ``\\l``, while the SVG
    records only that a break happened (so it comes back ``\\n``-joined, and a
    source-empty line comes back as a single space). Unifying the escapes and
    trimming each line makes the two comparable. For comparison only -- writers
    keep the original spelling, since that goes back into the puml.
    """
    lines = _LINE_BREAK_ESCAPE_RE.split(name)
    return "\\n".join(line.strip() for line in lines)


def display_names_match(left: str, right: str) -> bool:
    """Whether two spellings of a displayed name denote the same label."""
    return normalized_display_name(left) == normalized_display_name(right)


def contains_line_break(name: str) -> bool:
    """Whether a displayed name carries a PlantUML line-break escape."""
    return _LINE_BREAK_ESCAPE_RE.search(name) is not None


def reference_name_for(puml: str, display_name: str) -> str:
    """The token the diagram body uses for the participant shown as ``display_name``.

    The frontend only knows a participant's *displayed* name, but the body must
    refer to the alias when the declaration has one. Resolving here from the puml
    alone keeps that translation in one place, usable without an SVG. Falls back
    to the displayed name when there is no declaration or alias -- which is then
    the correct token anyway.
    """
    for _line_index, declaration in participant_declarations(puml):
        if display_names_match(declaration.name, display_name):
            return declaration.reference_name
    return display_name


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


# Participant labels are drawn at font-size 14. Message and box-title text use
# 13, and the one other thing drawn at 14 -- the diagram title -- is bold.
_PARTICIPANT_LABEL_FONT_SIZE = "14"


def _is_participant_label_text(element: Pq) -> bool:
    """Whether an SVG element is one line of a participant header's label."""
    if not element or element[0].tag != "text":
        return False
    return (
        element.attr("font-size") == _PARTICIPANT_LABEL_FONT_SIZE
        and element.attr("font-weight") != "bold"
    )


def participant_label(rect: Pq) -> str:
    """The displayed name drawn inside a participant header rect.

    PlantUML renders a name containing a line break (``participant "a\\nb" as
    ab``) as one ``<text>`` sibling per line, so reading only the rect's
    immediate next sibling would see just the first line -- leaving the
    participant unmatchable against its declaration, and every operation on it
    (rename, delete, add beside, hover) pointed at the wrong line or none.

    The lines are rejoined with a literal ``\\n`` so the result is the same
    escaped, single-line form the puml declaration uses. Which of PlantUML's
    break escapes produced the break is not recoverable from the SVG; see
    :func:`normalized_display_name` for how that is reconciled when matching.
    """
    lines: List[str] = []
    sibling = rect.next()
    while _is_participant_label_text(sibling):
        lines.append(sibling.text() or "")
        sibling = sibling.next()
    return "\\n".join(lines)


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
    # The ``as X`` token of this participant's declaration, when it has one.
    # Only ``name`` is readable from the SVG; the alias is filled in from the
    # puml while attaching declaration lines (see _assign_participant_indexes).
    alias: str | None = None

    @property
    def reference_name(self) -> str:
        """The token the diagram body uses to refer to this participant.

        Lines that mention a participant (messages, ``activate``, note
        placement) must use the alias when the declaration has one, and the
        displayed name otherwise. Writers should always build lines from this,
        never from ``name``, or an aliased participant whose displayed name
        contains spaces yields invalid puml.
        """
        return self.alias or self.name

    def contains_x(self, x_val: float) -> bool:
        return self.x_origin <= x_val <= self.x_origin + self.width

    def __eq__(self, other):
        return isinstance(other, Participant) and self.cx == other.cx

    @classmethod
    def from_svg(cls, rect: Pq):
        x = float(rect.attr("x"))
        y = float(rect.attr("y"))
        width = float(rect.attr("width"))
        height = float(rect.attr("height"))

        cx = x + width / 2
        cy = y + height / 2

        name = participant_label(rect)

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
            participant = Participant.from_svg(rect)

            if participant.cx not in unique_participants:
                unique_participants[participant.cx] = participant

        self.participants.extend(unique_participants.values())
        self._assign_participant_indexes(puml)

    def _assign_participant_indexes(self, puml: str):
        """Attach each participant to the puml line that declares it.

        Also copies the declaration's alias onto the participant, so writers can
        refer to it by ``reference_name``. The alias is not recoverable from the
        SVG -- it renders the displayed name only -- so this is the one place the
        two halves are joined.

        Matched by name, not by position. A participant can be introduced
        implicitly by a message (``Alice -> Bob: hi``) and then has no
        declaration line at all, so zipping the declaration lines against the
        diagram-ordered participants shifts every later participant onto some
        other participant's line and leaves the trailing ones at -1. Callers
        treat -1 as "not found", and add_box used to insert at it directly --
        Python's negative indexing then wrote ``end box`` to the top of the
        file and ``box`` before the last line.

        Participants with no declaration keep index -1, which is accurate:
        there is no line to point at. Callers that need a real line must say so
        (see add_box).
        """
        declarations = participant_declarations(puml)

        # Consume each declaration at most once, so repeated display names map
        # to distinct lines in diagram order rather than all to the first.
        claimed: set[int] = set()
        for participant in self.participants:
            for position, (line_index, declaration) in enumerate(declarations):
                if position in claimed:
                    continue
                if display_names_match(declaration.name, participant.name):
                    participant.index = line_index
                    participant.alias = declaration.alias
                    claimed.add(position)
                    break

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
