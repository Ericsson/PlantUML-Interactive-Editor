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

from .sequence_classes import Diagram, Participant


def add_participant(puml: str, svg: str, cx: int) -> str:
    """Add a participant at the correct position in the puml code."""
    diagram = Diagram.from_svg(svg, puml)
    closest_participant = find_closest_participant(diagram.participants, cx)

    lines = puml.splitlines()

    if not closest_participant:
        lines.insert(1, "participant participant1")
        return "\n".join(lines)

    index = (
        closest_participant.index
        if cx < closest_participant.cx
        else closest_participant.index + 1
    )
    lines.insert(index, f"participant participant{len(diagram.participants) + 1}")
    return "\n".join(lines)


def find_closest_participant(
    participants: List[Participant], target_cx: int
) -> Participant:
    """Find the index of the participant with the closest cx value to the target_cx, and return their cx."""
    min_distance = float("inf")
    closest_participant = None

    for index, participant in enumerate(participants):
        distance = abs(participant.cx - target_cx)
        if distance < min_distance:
            min_distance = distance
            closest_participant = participant

    return closest_participant


def add_message(
    puml: str, svg: str, firstcoordinates: List[int], secondcoordinates: List[int]
):
    """Add a message between two participants at the correct index"""
    first_x, first_y = firstcoordinates
    second_x, second_y = secondcoordinates

    diagram = Diagram.from_svg(svg)
    sender = find_closest_participant(diagram.participants, first_x)
    reciever = find_closest_participant(diagram.participants, second_x)

    return sender, reciever
