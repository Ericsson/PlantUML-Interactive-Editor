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
``<keyword> <label> ... end`` block. Any group can be split into branches
with ``else <label>`` lines.
"""

from typing import Dict, Iterator, List, Tuple

from pyquery import PyQuery as Pq

from .classes import is_message_line
from .errors import EditError
from .util import escape_multiline_text

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

    Raises ``EditError`` (a ``ValueError``) if ``group_type`` is not one of the
    valid keywords.
    """
    if group_type not in VALID_GROUP_TYPES:
        raise EditError("invalid_group_type")

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


def _first_word(line: str) -> str:
    """Return the first space-separated word of a puml line ("" if blank)."""
    stripped = line.strip()
    return stripped.split(" ", 1)[0] if stripped else ""


def _find_group_line_index(puml: str, group_index: int) -> int:
    """Find the puml line index of the nth group header (1-based)."""
    lines = puml.splitlines()
    count = 0
    for i, line in enumerate(lines):
        if _first_word(line) in VALID_GROUP_TYPES:
            count += 1
            if count == group_index:
                return i
    return -1


def _block_lines(lines: List[str], header_index: int) -> Iterator[Tuple[int, int]]:
    """Yield ``(line_index, depth)`` for each line after a group header.

    ``depth`` counts the groups enclosing the line, starting from this one:
    1 for lines directly in the group (including a nested group's header and
    'end'), 2 for lines inside that nested group, and so on. The walk ends
    with the group's own closing 'end', yielded at depth 0; if the block is
    never closed it runs to the last line.
    """
    depth = 1
    for i in range(header_index + 1, len(lines)):
        if lines[i].strip() == "end":
            depth -= 1
            yield i, depth
            if depth == 0:
                return
        else:
            yield i, depth
            if _first_word(lines[i]) in VALID_GROUP_TYPES:
                depth += 1


def _find_group_end_index(lines: List[str], header_index: int) -> int:
    """Find the line index of the 'end' closing the group opened at header_index.

    Returns -1 if no matching 'end' exists.
    """
    return next((i for i, depth in _block_lines(lines, header_index) if depth == 0), -1)


def _find_own_else_indexes(lines: List[str], header_index: int) -> List[int]:
    """Find the 'else' lines belonging to the group opened at header_index.

    A nested group's 'else' lines are deeper, so they are not included.
    """
    return [
        i
        for i, depth in _block_lines(lines, header_index)
        if depth == 1 and _first_word(lines[i]) == "else"
    ]


def _compute_else_slots(lines: List[str], header_index: int) -> List[int]:
    """Return the message line indexes an 'else' may be inserted before.

    A slot is a message directly in the group (not inside a nested group)
    whose branch - the lines since the header or the group's latest 'else' -
    already has content, so the new 'else' never creates an empty branch.
    Blank lines and ``'`` comments are not content.
    """
    slots = []
    branch_has_content = False
    for i, depth in _block_lines(lines, header_index):
        if depth == 0:
            break
        if depth > 1:
            continue  # inside a nested group; its header/end were seen at depth 1
        stripped = lines[i].strip()
        if not stripped or stripped.startswith("'"):
            continue
        if _first_word(stripped) == "else":
            branch_has_content = False
            continue
        if is_message_line(stripped) and branch_has_content:
            slots.append(i)
        branch_has_content = True
    return slots


def _count_group_boxes(svg: str) -> int:
    """Count real group boxes, skipping PlantUML's invisible duplicate rect.

    Alongside the visible bordered box (rect fill="none") that follows each
    group's keyword tab (path fill="#EEEEEE"), PlantUML also emits an
    invisible bounding rect earlier in the document for layout purposes.
    That rect is only reliably distinguished from the real box by document
    order - depending on the rendering environment, it can end up with the
    same literal fill="none" attribute, so a plain count of such rects can
    double-count groups. Pairing on "immediately follows its tab path" (the
    same rule the frontend uses in setupGroupHandlers) avoids that.
    """
    d = Pq(svg)
    count = 0
    pending_tab = False
    for el in d.children().items():
        tag = el[0].tag
        if not isinstance(tag, str):
            pending_tab = False
            continue
        if tag == "path" and el.attr("fill") == "#EEEEEE":
            pending_tab = True
            continue
        if tag == "rect" and el.attr("fill") == "none":
            if pending_tab:
                count += 1
            pending_tab = False
            continue
        pending_tab = False
    return count


def get_group_positions(puml: str, svg: str) -> List[Dict[str, object]]:
    """Return header/end line indexes and else slots for each group.

    Groups are in SVG document order, matching puml source order (see
    index_of_clicked_group), so the frontend matches groups by ordinal.
    ``elseSlots`` lists the message line indexes an else may be inserted
    before (see _compute_else_slots); the frontend snaps the add-else ghost
    line to them, so it never offers a position add_else would reject.
    """
    lines = puml.splitlines()
    group_count = _count_group_boxes(svg)

    positions: List[Dict[str, object]] = []
    for n in range(1, group_count + 1):
        header_index = _find_group_line_index(puml, n)
        if header_index == -1:
            positions.append({"headerIndex": -1, "endIndex": -1, "elseSlots": []})
            continue
        positions.append(
            {
                "headerIndex": header_index,
                "endIndex": _find_group_end_index(lines, header_index),
                "elseSlots": _compute_else_slots(lines, header_index),
            }
        )
    return positions


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
    """Unwrap the clicked group: remove its header, 'else' and matching 'end' lines.

    The block's contents (messages, notes, nested groups) are left in place.
    Nesting depth is tracked so only this group's own 'else' and 'end' lines
    are removed, never a nested group's; leaving an 'else' behind would no
    longer be inside any group and break the render.
    """
    idx = index_of_clicked_group(svg, svgelement)
    line_index = _find_group_line_index(puml, idx)
    lines = puml.splitlines()

    end_line = _find_group_end_index(lines, line_index)
    if end_line == -1:
        return puml

    own_lines = [line_index, *_find_own_else_indexes(lines, line_index)]
    # Delete bottom-up so earlier indexes stay valid.
    for i in sorted([*own_lines, end_line], reverse=True):
        del lines[i]
    return "\n".join(lines)


def add_else(
    puml: str, svg: str, svgelement: str, before_message_index: int, label: str
) -> str:
    """Split the clicked ``alt`` with an ``else`` line before a message.

    ``before_message_index`` must be one of the group's else slots (see
    _compute_else_slots). The line is indented like the group's header, as
    'else' is a sibling of the header and 'end'. An empty label writes a bare
    ``else``; newlines in the label are kept as literal ``\\n``.

    Raises ``EditError`` if the position is not a valid slot of the clicked
    group (or no group matches the click).
    """
    lines = puml.splitlines()
    header_index = _find_group_line_index(puml, index_of_clicked_group(svg, svgelement))
    if header_index == -1 or before_message_index not in _compute_else_slots(
        lines, header_index
    ):
        raise EditError("invalid_else_position")

    header = lines[header_index]
    indent = header[: len(header) - len(header.lstrip())]
    text = escape_multiline_text(label.strip())
    lines.insert(before_message_index, f"{indent}else {text}".rstrip())
    return "\n".join(lines)
