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

"""Group block logic for sequence diagrams.

Supports the keywords ``group``, ``alt``, ``opt``, and ``loop``.  A group
wraps a range of messages (identified by their puml line indexes) in a
``<keyword> <label> ... end`` block.
"""

from typing import Dict

from pyquery import PyQuery as Pq

VALID_GROUP_TYPES = ("group", "alt", "opt", "loop")


def add_group(
    puml: str,
    group_type: str,
    label: str,
    start_message_index: int,
    end_message_index: int,
) -> str:
    """Insert a group block wrapping messages between two line indexes.

    ``start_message_index`` and ``end_message_index`` are puml line numbers of
    the bounding messages.  The range is normalized so the opening line is
    inserted before the earlier message and the closing ``end`` line is inserted
    after the later message.

    Raises ``ValueError`` if ``group_type`` is not one of the valid keywords.
    """
    if group_type not in VALID_GROUP_TYPES:
        raise ValueError(
            f"Invalid group type '{group_type}'. "
            f"Must be one of: {', '.join(VALID_GROUP_TYPES)}"
        )

    # Normalize so start <= end (user may have selected bottom-to-top)
    start = min(start_message_index, end_message_index)
    end = max(start_message_index, end_message_index)

    lines = puml.splitlines()

    # Insert end line after the end message, then the opening line before the
    # start message.  Inserting the later line first keeps the start index valid.
    lines.insert(end + 1, "end")
    lines.insert(start, f"{group_type} {label}")

    return "\n".join(lines)


def index_of_clicked_group(svg: str, svgelement: str) -> int:
    """Find the 1-based index of the clicked group's box in the SVG.

    Group blocks render a bordered box as a rect with fill "none",
    which is unique to group boxes (participant rects use #E2E2F0,
    activation bars use #FFFFFF). Boxes are counted in document order,
    which matches puml source order, and matched by their x/y position.
    """
    clicked = Pq(svgelement)
    clicked_x = clicked.attr("x")
    clicked_y = clicked.attr("y")

    d = Pq(svg)
    count = 0
    for rect in d("rect").items():
        if rect.attr("fill") != "none":
            continue
        count += 1
        if rect.attr("x") == clicked_x and rect.attr("y") == clicked_y:
            return count
    return -1


def _find_group_line_index(puml: str, group_index: int) -> int:
    """Find the puml line index of the nth group header (1-based)."""
    lines = puml.splitlines()
    count = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        first_word = stripped.split(" ", 1)[0] if stripped else ""
        if first_word in VALID_GROUP_TYPES:
            count += 1
            if count == group_index:
                return i
    return -1


def get_group_label(puml: str, svg: str, svgelement: str) -> Dict[str, str]:
    """Get the keyword and label text of the clicked group."""
    idx = index_of_clicked_group(svg, svgelement)
    line_index = _find_group_line_index(puml, idx)
    line = puml.splitlines()[line_index].strip()
    parts = line.split(" ", 1)
    group_type = parts[0]
    label = parts[1] if len(parts) > 1 else ""
    return {"type": group_type, "label": label}


def rename_group(puml: str, svg: str, svgelement: str, label: str) -> str:
    """Rename the clicked group's title, keeping its keyword unchanged."""
    idx = index_of_clicked_group(svg, svgelement)
    line_index = _find_group_line_index(puml, idx)
    lines = puml.splitlines()
    group_type = lines[line_index].strip().split(" ", 1)[0]
    lines[line_index] = f"{group_type} {label}" if label else group_type
    return "\n".join(lines)


def delete_group(puml: str, svg: str, svgelement: str) -> str:
    """Unwrap the clicked group: remove its header and matching 'end' line.

    The block's contents (messages, notes, nested groups) are left in place.
    Nesting depth is tracked to find this group's own closing 'end' rather
    than a nested group's.
    """
    idx = index_of_clicked_group(svg, svgelement)
    line_index = _find_group_line_index(puml, idx)
    lines = puml.splitlines()

    depth = 1
    end_line = -1
    for i in range(line_index + 1, len(lines)):
        stripped = lines[i].strip()
        first_word = stripped.split(" ", 1)[0] if stripped else ""
        if first_word in VALID_GROUP_TYPES:
            depth += 1
        elif stripped == "end":
            depth -= 1
            if depth == 0:
                end_line = i
                break

    if end_line == -1:
        return puml

    del lines[end_line]
    del lines[line_index]
    return "\n".join(lines)
