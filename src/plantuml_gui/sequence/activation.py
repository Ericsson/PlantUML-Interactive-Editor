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
an ``activate <P>`` line at the start-Y position and a closing ``deactivate <P>``
or ``destroy <P>`` line at the end-Y position. Because the gesture always starts
by activating and inserts a matched pair, a participant can never be deactivated
without first being activated.
"""

from .classes import Diagram
from .util import find_insertion_index


def add_activation(
    puml: str,
    svg: str,
    participant_name: str,
    start_y: float,
    end_y: float,
    end_type: str,
) -> str:
    """Insert a matched activate + close pair for a participant by Y-position.

    ``end_type`` is ``"destroy"`` to end the lifeline with an X, otherwise the
    bar is closed with ``deactivate``. The closing line is inserted first (it
    sits at a greater-or-equal line index), then the ``activate`` line, so
    source order always has ``activate`` before its close and the index of the
    start insertion stays valid.
    """
    keyword = "destroy" if end_type == "destroy" else "deactivate"

    diagram = Diagram.from_svg(svg, puml)
    lines = puml.splitlines()

    start_index = find_insertion_index(diagram.messages, svg, puml, start_y, lines)
    end_index = find_insertion_index(diagram.messages, svg, puml, end_y, lines)

    # Insert the closing line first so start_index remains valid afterwards.
    lines.insert(end_index, f"{keyword} {participant_name}")
    lines.insert(start_index, f"activate {participant_name}")
    return "\n".join(lines)
