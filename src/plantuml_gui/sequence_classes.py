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
    index: int = -1  # default

    def __eq__(self, other):
        return isinstance(other, Participant) and self.x == other.x

    @classmethod
    def from_svg(cls, rect: Pq, text: Pq):
        x = float(rect.attr("x"))
        y = float(rect.attr("y"))
        width = float(rect.attr("width"))
        height = float(rect.attr("height"))

        cx = x + width / 2
        cy = y + height / 2

        name = text.text()

        return cls(name, cx, cy)


@dataclass
class Diagram:
    participants: List[Participant] = field(default_factory=list)

    @classmethod
    def from_svg(cls, svgtext: str, puml: str):
        svg = Pq(svgtext)
        diagram = cls()

        diagram._parse_participants(svg, puml)

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
