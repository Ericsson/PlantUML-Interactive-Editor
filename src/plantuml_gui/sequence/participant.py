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

from pyquery import PyQuery as Pq

from .classes import Diagram, Participant


def index_of_clicked_participant(svg: str, svgelement: str) -> int:
    """Find the 1-based index of the clicked participant in the SVG.

    Follows the same element-matching pattern as activity diagrams:
    the frontend sends the outerHTML of the clicked SVG element, and the
    backend iterates all elements of that type in the full SVG, counting
    until it finds the exact match. This gives a positional index that maps
    to the corresponding line in the puml source.

    Participants are deduplicated by center-x because PlantUML renders two
    rects per participant (top and bottom header boxes) with the same cx.
    """
    clicked_rect = Pq(svgelement)
    clicked_cx = float(clicked_rect.attr("x")) + float(clicked_rect.attr("width")) / 2

    d = Pq(svg)
    seen_cx: set[float] = set()
    count = 0
    for rect in d("rect").items():
        cx = float(rect.attr("x")) + float(rect.attr("width")) / 2
        if cx not in seen_cx:
            seen_cx.add(cx)
            count += 1
            if cx == clicked_cx:
                return count
    return count


def add_participant(puml: str, svg: str, clicked_x: int) -> str:
    """Add a participant at the correct position in the puml code."""
    diagram = Diagram.from_svg(svg, puml)
    lines = puml.splitlines()

    if not diagram.participants:
        lines.insert(1, "participant participant1")
        return "\n".join(lines)

    closest_participant = find_closest_participant(diagram.participants, clicked_x)
    index = (
        closest_participant.index
        if clicked_x < closest_participant.cx
        else closest_participant.index + 1
    )
    lines.insert(index, f"participant participant{len(diagram.participants) + 1}")
    return "\n".join(lines)


def find_closest_participant(
    participants: List[Participant], target_cx: int
) -> Participant:
    """Find the participant with the closest cx value to the target_cx."""
    min_distance = float("inf")
    closest_participant = participants[0]

    for participant in participants:
        distance = abs(participant.cx - target_cx)
        if distance < min_distance:
            min_distance = distance
            closest_participant = participant

    return closest_participant


def check_if_inside_participant(puml: str, svg: str, coords: List[int]):
    x, y = coords
    diagram = Diagram.from_svg(svg, puml)
    for participant in diagram.participants:
        if participant.contains_x(x):
            return True

    return False


def add_message(
    puml: str,
    svg: str,
    message: str,
    firstcoordinates: List[int],
    secondcoordinates: List[int],
):
    """Add a message between two participants at the correct index"""
    first_x, first_y = firstcoordinates
    second_x, second_y = secondcoordinates

    diagram = Diagram.from_svg(svg, puml)
    sender = find_closest_participant(diagram.participants, first_x)
    reciever = find_closest_participant(diagram.participants, second_x)

    lines = puml.splitlines()
    lines.insert(-1, f"{sender.name} -> {reciever.name}: {message}")
    return "\n".join(lines)


def get_participant_name(puml: str, svg: str, svgelement: str) -> str:
    """Get participant name by matching the clicked SVG element."""
    diagram = Diagram.from_svg(svg, puml)
    count = index_of_clicked_participant(svg, svgelement)
    return diagram.participants[count - 1].name


def edit_participant_name(puml: str, svg: str, newname: str, svgelement: str) -> str:
    """Edit participant name by matching the clicked SVG element."""
    diagram = Diagram.from_svg(svg, puml)
    count = index_of_clicked_participant(svg, svgelement)
    participant = diagram.participants[count - 1]
    return puml.replace(participant.name, newname)
