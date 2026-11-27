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

"""Y-based insertion of new sequence elements (messages, notes).

Kept apart from ``util`` because it combines element positions from several
modules (messages, notes, group boundaries, the current page), and ``group``
and ``pages`` themselves import ``util``.
"""

from typing import List, Tuple

from .classes import Message
from .group import group_boundary_positions
from .pages import current_page_end
from .util import extract_note_positions


def find_insertion_index(messages: List[Message], svg: str, puml: str, y: float) -> int:
    """Find the line index to insert a new element at SVG y-coordinate ``y``.

    Messages, notes and group boundaries (header, else and 'end' lines; see
    ``group_boundary_positions``) are ordered by their SVG y; the element goes
    before the first one below ``y``. Group boundaries make a click inside a
    group's box, below its last message, land inside the group, and a click
    above a box land outside it. The 'end' of a group continuing onto a later
    page is ignored, so the element stays on the current page.

    Past every element it goes at the end of the page: before the ``newpage``
    closing it (see pages.py) or before ``@enduml``.
    """
    end = current_page_end(puml)
    elements: List[Tuple[float, int]] = [(msg.cy, msg.index) for msg in messages]
    elements.extend(extract_note_positions(svg, puml))
    elements.extend(
        (cy, index) for cy, index in group_boundary_positions(puml, svg) if index <= end
    )
    elements.sort(key=lambda x: x[0])

    for cy, line_index in elements:
        if cy > y:
            return line_index
    return end
