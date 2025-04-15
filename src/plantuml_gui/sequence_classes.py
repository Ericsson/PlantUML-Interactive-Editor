# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2025 Ericsson
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

from dataclasses import dataclass, field
from typing import Dict, List

from pyquery import PyQuery as Pq  # pragma: no cover


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
    index: int = -1  # default

    @classmethod
    def from_svg(cls, elements: List[Pq], participants: List[Participant]):
        polygon, line, text = elements

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

        from_participant = next((p for p in participants if p.contains_x(start_x)))
        to_participant = next((p for p in participants if p.contains_x(arrow_x)))

        return cls(from_participant, to_participant, message, cy)


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
        parsed_messages = []

        elements = list(svg("polygon, line, text").items())
        message_groups = [
            [elements[i], elements[i + 1], elements[i + 2]]
            for i in range(len(elements) - 2)
            if elements[i][0].tag == "polygon"
            and elements[i + 1][0].tag == "line"
            and elements[i + 2][0].tag == "text"
        ]

        for message_group in message_groups:
            parsed_messages.append(Message.from_svg(message_group, self.participants))

        self.messages.extend(parsed_messages)
        self._assign_message_indexes(puml)

    def _assign_message_indexes(self, puml: str):
        """Assign indexes in the puml code to corresponding message"""
        lines = puml.splitlines()

        # Find all lines that represent messages (lines with '->')
        message_lines = [i for i, line in enumerate(lines) if "->" in line]

        # Messages are already in occuring order
        for i, line_index in enumerate(message_lines):
            if i < len(self.messages):
                self.messages[i].index = line_index
