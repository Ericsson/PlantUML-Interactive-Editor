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
    arrow_type: str = "->",
):
    """Add a message between two participants at the correct y-position."""
    first_x, first_y = firstcoordinates
    second_x, _second_y = secondcoordinates

    diagram = Diagram.from_svg(svg, puml)
    sender = _find_closest_participant(diagram.participants, first_x)
    reciever = _find_closest_participant(diagram.participants, second_x)

    lines = puml.splitlines()
    insert_at = _find_insertion_index(diagram.messages, first_y, lines)
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


def index_of_clicked_message(svg: str, svgelement: str) -> int:
    """Find the 1-based index of the message containing the clicked SVG element.

    Iterates SVG elements using the same grouping logic as Diagram._parse_messages,
    checking if the clicked element matches any element in each message group.
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
            message_index += 1
            for el in group[:4]:
                if _svg_element_matches(el, clicked):
                    return message_index
            i += 4
        elif tags[:5] == ["line", "line", "line", "polygon", "text"]:
            message_index += 1
            for el in group[:5]:
                if _svg_element_matches(el, clicked):
                    return message_index
            i += 5
        elif tags[:3] == ["polygon", "line", "text"]:
            message_index += 1
            for el in group[:3]:
                if _svg_element_matches(el, clicked):
                    return message_index
            i += 3
        else:
            i += 1

    return -1


def get_message_text(puml: str, svg: str, svgelement: str) -> str:
    """Get the label text of the clicked message."""
    diagram = Diagram.from_svg(svg, puml)
    idx = index_of_clicked_message(svg, svgelement)
    message = diagram.messages[idx - 1]
    line = puml.splitlines()[message.index]
    colon_pos = line.find(": ")
    return line[colon_pos + 2 :] if colon_pos != -1 else ""


def edit_message_text(puml: str, svg: str, svgelement: str, text: str) -> str:
    """Edit the label text of the clicked message."""
    diagram = Diagram.from_svg(svg, puml)
    idx = index_of_clicked_message(svg, svgelement)
    message = diagram.messages[idx - 1]
    lines = puml.splitlines()
    line = lines[message.index]
    # Replace text after ": "
    colon_pos = line.find(": ")
    if colon_pos != -1:
        lines[message.index] = line[: colon_pos + 2] + text
    return "\n".join(lines)


def delete_message(puml: str, svg: str, svgelement: str) -> str:
    """Delete the clicked message."""
    diagram = Diagram.from_svg(svg, puml)
    idx = index_of_clicked_message(svg, svgelement)
    message = diagram.messages[idx - 1]
    lines = puml.splitlines()
    del lines[message.index]
    return "\n".join(lines)
