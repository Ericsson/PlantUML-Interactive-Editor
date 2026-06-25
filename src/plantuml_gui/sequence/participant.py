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

import html
import re
from typing import Dict, List

from pyquery import PyQuery as Pq

from .classes import Diagram


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


def _next_participant_number(puml: str) -> int:
    """Find the next available participant number by checking existing names."""
    numbers = [
        int(m.group(1))
        for m in re.finditer(r"^participant participant(\d+)", puml, re.MULTILINE)
    ]
    return max(numbers, default=0) + 1


def add_participant(puml: str, svg: str, svgelement: str, direction: str) -> str:
    """Add a participant to the left or right of the clicked participant."""
    diagram = Diagram.from_svg(svg, puml)
    lines = puml.splitlines()

    count = index_of_clicked_participant(svg, svgelement)
    participant = diagram.participants[count - 1]
    index = participant.index if direction == "left" else participant.index + 1
    next_number = _next_participant_number(puml)
    lines.insert(index, f"participant participant{next_number}")
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
    safe_newname = html.escape(newname, quote=True)
    return puml.replace(participant.name, safe_newname)


def delete_participant(puml: str, svg: str, svgelement: str) -> str:
    """Delete a participant and all messages and notes referencing it (cascade)."""
    diagram = Diagram.from_svg(svg, puml)
    count = index_of_clicked_participant(svg, svgelement)
    participant = diagram.participants[count - 1]
    lines = puml.splitlines()

    lines_to_remove = {participant.index}
    for msg in diagram.messages:
        if msg.from_participant == participant or msg.to_participant == participant:
            lines_to_remove.add(msg.index)
    for i, line in enumerate(lines):
        stripped = line.strip()
        if stripped.startswith("note ") and participant.name in stripped:
            lines_to_remove.add(i)

    lines = [line for i, line in enumerate(lines) if i not in lines_to_remove]
    return "\n".join(lines)


def get_participant_positions(puml: str, svg: str) -> List[Dict[str, object]]:
    """Return participant lifeline positions for frontend hover detection."""
    diagram = Diagram.from_svg(svg, puml)
    d = Pq(svg)

    # Extract lifeline vertical bounds from dashed lines
    lifeline_bounds: Dict[float, Dict[str, float]] = {}
    for line in d("line").items():
        style = line.attr("style") or ""
        if "stroke-dasharray:5.0,5.0" in style:
            x = float(line.attr("x1"))
            lifeline_bounds[x] = {
                "yTop": float(line.attr("y1")),
                "yBottom": float(line.attr("y2")),
            }

    positions = []
    for participant in diagram.participants:
        # Find matching lifeline (cx may differ by ~0.5 due to stroke-width)
        bounds = {"yTop": 0.0, "yBottom": 0.0}
        for lx, lb in lifeline_bounds.items():
            if abs(lx - participant.cx) <= 1:
                bounds = lb
                break
        positions.append(
            {
                "name": participant.name,
                "cx": participant.cx,
                "yTop": bounds["yTop"],
                "yBottom": bounds["yBottom"],
            }
        )
    return positions
