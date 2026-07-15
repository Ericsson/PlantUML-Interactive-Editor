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

"""Participant box logic for sequence diagrams.

A ``box "title" [#color] ... end box`` block groups one or more contiguous
participants inside a bordered rectangle drawn behind their header cells.
Nested boxes require PlantUML's teoz rendering engine (``!pragma teoz true``).

SVG signature
-------------
PlantUML draws a box as a ``<rect>`` sharing the participant header style
``stroke:#181818;stroke-width:0.5;`` but *without* the rounded corners
(``rx``/``ry``) that participant headers carry, and with a solid ``fill`` color
(``#DDDDDD`` by default, or the chosen color). That signature is otherwise
identical to an ``rnote`` rect, so a box is disambiguated *geometrically*: a box
rect encloses at least one participant header rect, whereas an rnote never does.
Activation bars (``stroke-width:1.0``) and group boxes (``fill="none"``) differ
in style and are excluded outright.
"""

import html
import re
from typing import Dict, List

from pyquery import PyQuery as Pq

from .classes import participant_header_bounds, rect_encloses

# Style PlantUML gives box rects. Shared verbatim with participant headers and
# rnotes; see the module docstring for how the three are told apart.
BOX_RECT_STYLE = "stroke:#181818;stroke-width:0.5;"


def _box_header(title: str, color: str) -> str:
    """Build a ``box`` opening line from a title and an optional color.

    The title is HTML-escaped (mirroring participant renaming) and quoted; an
    empty title yields a bare ``box`` (an unnamed box, which PlantUML allows).
    ``color`` is optional: an empty value or ``"none"`` omits it, otherwise it
    is appended as a ``#``-prefixed token (named colors and hex both use ``#``).
    """
    header = "box"
    if title:
        header += f' "{html.escape(title, quote=True)}"'
    if color and color.strip().lower() != "none":
        token = color.strip()
        if not token.startswith("#"):
            token = f"#{token}"
        header += f" {token}"
    return header


TEOZ_PRAGMA = "!pragma teoz true"


def _find_box_spans(lines: List[str]) -> List[tuple[int, int]]:
    """Return ``(header_index, end_index)`` for every box, depth-aware.

    A box opens on a line whose first word is ``box`` and closes on the next
    ``end box`` at the same nesting depth. A stack pairs each ``end box`` with
    the most recent unclosed ``box`` so nested boxes are captured correctly.
    """
    spans: List[tuple[int, int]] = []
    stack: List[int] = []
    for i, line in enumerate(lines):
        stripped = line.strip()
        first_word = stripped.split(" ", 1)[0] if stripped else ""
        if first_word == "box":
            stack.append(i)
        elif stripped == "end box" and stack:
            spans.append((stack.pop(), i))
    return spans


def _needs_teoz_or_raise(spans: List[tuple[int, int]], start: int, end: int) -> bool:
    """Classify a new box's range against existing boxes.

    Returns True if the new range nests with any existing box (one fully
    contains the other), which requires the teoz engine. Returns False if the
    range is disjoint from every box. Raises ``ValueError`` if it *crosses* a
    box (partial overlap), which PlantUML cannot render.
    """
    needs_teoz = False
    for box_start, box_end in spans:
        if end < box_start or start > box_end:
            continue  # disjoint
        new_contains = start <= box_start and box_end <= end
        existing_contains = box_start <= start and end <= box_end
        if new_contains or existing_contains:
            needs_teoz = True
        else:
            raise ValueError(
                "Box overlaps an existing box. Boxes may nest but not cross."
            )
    return needs_teoz


def _insert_teoz(lines: List[str]) -> None:
    """Insert the teoz pragma right after ``@startuml`` (idempotent)."""
    if any(line.strip().startswith("!pragma teoz") for line in lines):
        return
    for i, line in enumerate(lines):
        if line.strip().startswith("@startuml"):
            lines.insert(i + 1, TEOZ_PRAGMA)
            return
    lines.insert(0, TEOZ_PRAGMA)


def add_box(puml: str, title: str, color: str, start_index: int, end_index: int) -> str:
    """Wrap a contiguous run of participants in a ``box ... end box`` block.

    ``start_index`` and ``end_index`` are the puml line indexes of the two
    boundary participant declarations (as carried by the frontend's
    participant-lifeline table). The range is normalized so the ``box`` opening
    line is inserted before the earlier declaration and the ``end box`` closing
    line after the later one, wrapping every line between them.

    If the range nests with an existing box, ``!pragma teoz true`` is added
    (once) so PlantUML renders nested boxes. A range that crosses an existing
    box (partial overlap) raises ``ValueError``.
    """
    start = min(start_index, end_index)
    end = max(start_index, end_index)

    lines = puml.splitlines()
    needs_teoz = _needs_teoz_or_raise(_find_box_spans(lines), start, end)

    # Insert the closing line first so the opening insertion index stays valid.
    lines.insert(end + 1, "end box")
    lines.insert(start, _box_header(title, color))

    if needs_teoz:
        _insert_teoz(lines)

    return "\n".join(lines)


def is_box_rect(rect: Pq, participant_bounds: List[Dict[str, float]]) -> bool:
    """Return True if an SVG rect is a participant box background.

    ``participant_bounds`` is the output of :func:`participant_header_bounds`
    for the same SVG. A box is a rect with the shared header style, no rounded
    corners, a solid fill, that encloses at least one participant header. That
    enclosure check is what separates a box from an rnote (which shares every
    attribute but never wraps a participant).
    """
    if (rect.attr("style") or "") != BOX_RECT_STYLE:
        return False
    # Participant headers carry rounded corners; boxes and rnotes do not.
    if rect.attr("rx") is not None or rect.attr("ry") is not None:
        return False
    fill = rect.attr("fill")
    if fill is None or fill == "none":
        return False
    return any(rect_encloses(rect, bound) for bound in participant_bounds)


def index_of_clicked_box(svg: str, svgelement: str) -> int:
    """Return the 1-based ordinal of the clicked box among all boxes.

    Box rects render in document order matching puml source order (outer before
    inner for nested boxes), so the ordinal maps directly to the Nth ``box``
    header line. Matched by the clicked rect's x/y, mirroring
    ``index_of_clicked_group``.
    """
    clicked = Pq(svgelement)
    clicked_x = clicked.attr("x")
    clicked_y = clicked.attr("y")

    d = Pq(svg)
    bounds = participant_header_bounds(d)
    count = 0
    for rect in d("rect").items():
        if not is_box_rect(rect, bounds):
            continue
        count += 1
        if rect.attr("x") == clicked_x and rect.attr("y") == clicked_y:
            return count
    return -1


def _resolve_box_line(puml: str, svg: str, svgelement: str) -> int:
    """Return the puml line index of the clicked box's header, or -1.

    Shared by get_box_label/edit_box/delete_box, which all need to turn the
    clicked SVG box rect into its header line before reading or editing it.
    """
    return _find_box_line_index(puml, index_of_clicked_box(svg, svgelement))


def _find_box_line_index(puml: str, box_index: int) -> int:
    """Find the puml line index of the nth ``box`` header (1-based)."""
    lines = puml.splitlines()
    count = 0
    for i, line in enumerate(lines):
        stripped = line.strip()
        first_word = stripped.split(" ", 1)[0] if stripped else ""
        if first_word == "box":
            count += 1
            if count == box_index:
                return i
    return -1


def _find_box_end_index(lines: List[str], header_index: int) -> int:
    """Find the ``end box`` closing the box opened at ``header_index``.

    Nesting depth is tracked so a nested box's ``end box`` is skipped. Returns
    -1 if no matching ``end box`` exists.
    """
    depth = 1
    for i in range(header_index + 1, len(lines)):
        stripped = lines[i].strip()
        first_word = stripped.split(" ", 1)[0] if stripped else ""
        if first_word == "box":
            depth += 1
        elif stripped == "end box":
            depth -= 1
            if depth == 0:
                return i
    return -1


def delete_box(puml: str, svg: str, svgelement: str) -> str:
    """Unwrap the clicked box: remove its header and matching ``end box``.

    The participants (and any nested boxes) inside are left in place. The teoz
    pragma, if present, is left untouched so any remaining nested boxes still
    render.
    """
    line_index = _resolve_box_line(puml, svg, svgelement)
    if line_index == -1:
        return puml

    lines = puml.splitlines()
    end_line = _find_box_end_index(lines, line_index)
    if end_line == -1:
        return puml

    del lines[end_line]
    del lines[line_index]
    return "\n".join(lines)


def get_box_positions(puml: str, svg: str) -> List[Dict[str, int]]:
    """Return header/end line indexes for each box in SVG document order.

    Box rects render in document order matching puml source order (see
    :func:`index_of_clicked_box`), so the frontend matches boxes by ordinal for
    editor<->diagram hover highlighting.
    """
    lines = puml.splitlines()
    d = Pq(svg)
    bounds = participant_header_bounds(d)
    box_count = sum(1 for rect in d("rect").items() if is_box_rect(rect, bounds))

    positions: List[Dict[str, int]] = []
    for n in range(1, box_count + 1):
        header_index = _find_box_line_index(puml, n)
        end_index = (
            _find_box_end_index(lines, header_index) if header_index != -1 else -1
        )
        positions.append({"headerIndex": header_index, "endIndex": end_index})
    return positions


def _parse_box_header(line: str) -> Dict[str, str]:
    """Extract the title and color from a ``box`` header line.

    The title is the quoted string (HTML-unescaped for display) and the color
    is the ``#``-prefixed token, both optional and in either order. Returns
    ``{"title": ..., "color": ...}`` with the color's leading ``#`` stripped
    (so it matches the frontend's palette option values) and ``""`` for a
    missing title/color.
    """
    rest = line.strip()
    if rest.startswith("box"):
        rest = rest[len("box") :]

    title_match = re.search(r'"([^"]*)"', rest)
    title = html.unescape(title_match.group(1)) if title_match else ""

    # Search for the color only outside the quoted title, so a '#' inside the
    # title (e.g. box "C#") is not mistaken for a color token.
    remainder = rest[title_match.end() :] if title_match else rest
    color_match = re.search(r"#(\S+)", remainder)
    color = color_match.group(1) if color_match else ""

    return {"title": title, "color": color}


def get_box_label(puml: str, svg: str, svgelement: str) -> Dict[str, str]:
    """Return the clicked box's current title and color for the edit modal."""
    line_index = _resolve_box_line(puml, svg, svgelement)
    if line_index == -1:
        return {"title": "", "color": ""}
    return _parse_box_header(puml.splitlines()[line_index])


def edit_box(puml: str, svg: str, svgelement: str, title: str, color: str) -> str:
    """Rewrite the clicked box's header line with a new title and color.

    Reuses :func:`_box_header`, so the title is HTML-escaped and quoted (empty
    title -> bare ``box``) and the color is appended as a ``#``-prefixed token
    (``""``/``"none"`` -> omitted). The box's contents and nesting are untouched.
    """
    line_index = _resolve_box_line(puml, svg, svgelement)
    if line_index == -1:
        return puml

    lines = puml.splitlines()
    lines[line_index] = _box_header(title, color)
    return "\n".join(lines)
