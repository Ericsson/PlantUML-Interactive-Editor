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

"""Activation bar logic for sequence diagrams.

A single user gesture creates one balanced activation bar for one participant:
an ``activate <P>`` line before the message at ``start_index`` and a closing
``deactivate <P>`` or ``destroy <P>`` line after the message at ``end_index``.
Because the gesture always starts by activating and inserts a matched pair, a
participant can never be deactivated without first being activated.
"""

from typing import List, Optional, Tuple

from pyquery import PyQuery as Pq

from .classes import Diagram, Message, Participant


def add_activation(
    puml: str,
    participant_name: str,
    start_index: int,
    end_index: int,
    end_type: str,
) -> str:
    """Insert a matched activate + close pair for a participant by line index.

    ``start_index`` and ``end_index`` are the puml line numbers of the messages
    nearest to where the user started and ended the gesture. The ``activate``
    line is inserted just *after* the start message and the closing line just
    *after* the end message, so both anchor below their nearest message. The bar
    therefore covers the messages following the start message up to and
    including the end message. ``end_type`` is ``"destroy"`` to end the lifeline
    with an X, otherwise the bar is closed with ``deactivate``.

    The closing line is inserted first (it sits at a greater-or-equal line
    index), then the ``activate`` line, so the start insertion index stays valid.
    """
    keyword = "destroy" if end_type == "destroy" else "deactivate"

    lines = puml.splitlines()

    # Insert the closing line after the end message, then the opening line after
    # the start message. Inserting the (lower) end line first keeps the start
    # insertion index valid.
    lines.insert(end_index + 1, f"{keyword} {participant_name}")
    lines.insert(start_index + 1, f"activate {participant_name}")
    return "\n".join(lines)


def _activation_pairs(
    lines: List[str], participant_name: str
) -> List[Tuple[int, int, int]]:
    """Pair each ``activate`` with its closing ``deactivate``/``destroy`` line.

    Returns ``(activate_line, close_line, level)`` tuples for the participant,
    resolved with a stack so nested bars pair correctly. ``level`` is the
    nesting depth (0 = outermost), which mirrors how PlantUML offsets nested
    bars horizontally.
    """
    activate_text = f"activate {participant_name}"
    close_texts = (f"deactivate {participant_name}", f"destroy {participant_name}")
    stack: List[int] = []
    pairs: List[Tuple[int, int, int]] = []
    for index, line in enumerate(lines):
        stripped = line.strip()
        if stripped == activate_text:
            stack.append(index)
        elif stripped in close_texts and stack:
            start = stack.pop()
            pairs.append((start, index, len(stack)))
    return pairs


def _message_cy_above(messages: List[Message], line_index: int) -> Optional[float]:
    """Return the cy of the message on the closest line above ``line_index``."""
    above = [m for m in messages if m.index < line_index]
    if not above:
        return None
    return max(above, key=lambda m: m.index).cy


def _nearest_participant(
    participants: List[Participant], cx: float
) -> Optional[Participant]:
    if not participants:
        return None
    return min(participants, key=lambda p: abs(p.cx - cx))


def delete_activation(puml: str, svg: str, svgelement: str) -> str:
    """Remove the activation bar matching the clicked rect and its closing line.

    The clicked rect identifies a bar by its lifeline (x), top (y) and nesting
    offset. Each puml ``activate``/close pair has a predictable geometry — its
    top aligns with the message just above the ``activate`` line and its centre
    is offset right by the nesting level — so the clicked rect is matched to the
    nearest pair, and only that pair's two lines are removed.
    """
    clicked = Pq(svgelement)
    x = float(clicked.attr("x"))
    width = float(clicked.attr("width"))
    clicked_top = float(clicked.attr("y"))
    clicked_cx = x + width / 2
    level_offset = width / 2

    diagram = Diagram.from_svg(svg, puml)
    participant = _nearest_participant(diagram.participants, clicked_cx)
    if participant is None:
        return puml

    lines = puml.splitlines()
    best: Optional[Tuple[int, int]] = None
    best_distance = float("inf")
    for activate_line, close_line, level in _activation_pairs(lines, participant.name):
        expected_top = _message_cy_above(diagram.messages, activate_line)
        if expected_top is None:
            continue
        expected_cx = participant.cx + level * level_offset
        distance = abs(expected_top - clicked_top) + abs(expected_cx - clicked_cx)
        if distance < best_distance:
            best_distance = distance
            best = (activate_line, close_line)

    if best is None:
        return puml

    activate_line, close_line = best
    # Delete the (higher-index) close line first so activate_line stays valid.
    del lines[close_line]
    del lines[activate_line]
    return "\n".join(lines)
