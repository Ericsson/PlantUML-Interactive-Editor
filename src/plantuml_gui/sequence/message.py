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

from typing import List

from .classes import Diagram, Message, Participant


def _find_insertion_index(messages: List[Message], y: float, lines: List[str]) -> int:
    """Find the line index to insert a new message based on y-coordinate.

    Returns the line index where the new message should be inserted:
    - Before the first message whose cy > y
    - If y is below all messages, returns the line before @enduml
    """
    for msg in messages:
        if msg.cy > y:
            return msg.index
    # After all messages: insert before @enduml
    for i in range(len(lines) - 1, -1, -1):
        if lines[i].strip() == "@enduml":
            return i
    return len(lines)


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
):
    """Add a message between two participants at the correct y-position."""
    first_x, first_y = firstcoordinates
    second_x, _second_y = secondcoordinates

    diagram = Diagram.from_svg(svg, puml)
    sender = _find_closest_participant(diagram.participants, first_x)
    reciever = _find_closest_participant(diagram.participants, second_x)

    lines = puml.splitlines()
    insert_at = _find_insertion_index(diagram.messages, first_y, lines)
    lines.insert(insert_at, f"{sender.name} -> {reciever.name}: {message}")
    return "\n".join(lines)
