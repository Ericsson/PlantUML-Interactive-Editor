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

"""Editor-row positions for every activity diagram element.

Powers editor->diagram hover highlighting: one fetch per render returns,
for each element type, the puml line indexes owned by the nth element of
that type in SVG document order. The frontend registers hover targets in
the same document order (setHandlersForSvg walk), so entries match by
ordinal - the same invariant the existing per-element get*Line endpoints
rely on when counting the clicked element's position.
"""

from typing import Dict, List

from pyquery import PyQuery as Pq

from ..shared.title import find_title_bounds
from .activity import find_text_bounds, svgtochunklist
from .arrow import find_arrow_bounds
from .classes import PolyElement
from .connector import svgtochunklistconnector
from .ellipse import svgtochunklistellipse
from .group import find_group_bounds
from .if_statements import get_if_line, svgtochunklistpolygon
from .merge import find_merge_index
from .note import find_note_bounds
from .util import checkifwhile
from .whilepoly import get_while_line


def _expand(start: int, end: int) -> List[int]:
    """All rows from start to end inclusive; empty if the bounds are invalid."""
    if start < 0 or end < start:
        return []
    return list(range(start, end + 1))


def _activity_rows(puml: str, svg: str) -> List[List[int]]:
    lines = puml.splitlines()
    rows = []
    for n in range(1, len(svgtochunklist(svg)) + 1):
        start, end = find_text_bounds(lines, n)
        rows.append(_expand(start, end))
    return rows


def _poly_and_while_rows(
    puml: str, svg: str
) -> tuple[List[List[int]], List[List[int]]]:
    """Rows for if/switch/repeat polygons and for while polygons.

    get_if_line returns the repeat-while row for repeats, (start, end) for
    switches and (start, else_start, end) for ifs; get_while_line returns
    (while, endwhile). Negative rows (e.g. an if without an else) are dropped.
    """
    chunklist = svgtochunklistpolygon(svg)
    poly_rows = []
    while_rows = []
    for chunk in chunklist:
        if not chunk.text_elements:
            continue
        if checkifwhile(chunk):
            start, end = get_while_line(puml, chunklist, chunk.object)
            while_rows.append([row for row in (start, end) if row >= 0])
        else:
            result = get_if_line(puml, chunklist, chunk.object)
            if isinstance(result, int):
                result = (result,)
            poly_rows.append([row for row in result if row >= 0])
    return poly_rows, while_rows


def _count_notes(svg: str) -> int:
    """Count note body/fold paths the way note_count does, without a target."""
    count = 0
    d = Pq(svg)
    for path in d("path").items():
        if path.attr("style") == "pointer-events: none;":
            continue
        nxt = path.next()
        if nxt and nxt[0].tag == "path":
            count += 1
    return count


def _note_rows(puml: str, svg: str) -> List[List[int]]:
    lines = puml.splitlines()
    rows = []
    for n in range(1, _count_notes(svg) + 1):
        start, end = find_note_bounds(lines, n)
        rows.append(_expand(start, end))
    return rows


def _count_groups(svg: str) -> int:
    """Count group border paths the way group_count does, without a target."""
    d = Pq(svg)
    return sum(
        1
        for path in d("path").items()
        if path.attr("style") == "stroke:#000000;stroke-width:1.5;"
    )


def _group_rows(puml: str, svg: str) -> List[List[int]]:
    lines = puml.splitlines()
    rows = []
    for n in range(1, _count_groups(svg) + 1):
        start, end = find_group_bounds(lines, n)
        rows.append([row for row in (start, end) if row >= 0])
    return rows


def _nth_ellipse_row(lines: List[str], count: int) -> int:
    """Row of the nth start/stop/end line, mirroring get_index_ellipse's
    counting (including its skip of lines preceded by a note keyword) but
    returning the matched row itself rather than the insertion point below it.

    The note-keyword guard uses ``index > 0`` to avoid the Python
    ``lines[-1]`` wrap that would otherwise cause line 0 to be skipped
    whenever the last line of the diagram happens to start with "note".
    """
    for index, line in enumerate(lines):
        clean_line = line.strip()
        preceded_by_note = index > 0 and lines[index - 1].startswith("note")
        if not preceded_by_note:
            if clean_line in ["stop", "start", "end"]:
                count -= 1
                if count == 0:
                    return index
    return -1


def _ellipse_rows(puml: str, svg: str) -> List[List[int]]:
    lines = puml.splitlines()
    rows = []
    for n in range(1, len(svgtochunklistellipse(svg)) + 1):
        row = _nth_ellipse_row(lines, n)
        rows.append([row] if row >= 0 else [])
    return rows


def _nth_connector_row(lines: List[str], count: int) -> int:
    """Row of the nth connector line, mirroring find_index_connector's
    counting but returning the matched row itself.
    """
    for index, line in enumerate(lines):
        clean_line = line.strip()
        if clean_line.startswith("(") or (
            clean_line.startswith("#") and clean_line.endswith(")")
        ):
            count -= 1
            if count == 0:
                return index
    return -1


def _connector_rows(puml: str, svg: str) -> List[List[int]]:
    lines = puml.splitlines()
    rows = []
    for n in range(1, len(svgtochunklistconnector(svg)) + 1):
        row = _nth_connector_row(lines, n)
        rows.append([row] if row >= 0 else [])
    return rows


def _count_merges(svg: str) -> int:
    """Count merge polygons the way index_of_clicked_merge does."""
    count = 0
    d = Pq(svg)
    for poly in d("polygon").items():
        poly_svg = str(poly)[:-2] + "></polygon>"
        poly_obj = PolyElement.from_svg(poly_svg)
        if (
            poly.attr("style") == "stroke:#181818;stroke-width:0.5;"
            and poly_obj.is_merge()
        ):
            count += 1
    return count


def _merge_rows(puml: str, svg: str) -> List[List[int]]:
    lines = puml.splitlines()
    rows = []
    for n in range(1, _count_merges(svg) + 1):
        row = find_merge_index(lines, n)
        rows.append([row] if row >= 0 else [])
    return rows


def _arrow_rows(puml: str, svg: str) -> List[List[int]]:
    """Rows for arrow/case labels, one entry per arrowhead polygon that is
    followed by label text (the same elements checkIfArrowLabel attaches
    hover handlers to). Arrows are resolved by text match via
    find_arrow_bounds, exactly like the existing getArrowLine endpoint.
    """
    rows = []
    d = Pq(svg)
    for poly in d("polygon").items():
        style = poly.attr("style") or ""
        if "stroke-width:1.0" not in style:
            continue
        nxt = poly.next()
        if not nxt or nxt[0].tag != "text":
            continue
        poly_svg = str(poly)[:-2] + "></polygon>"
        start, end = find_arrow_bounds(puml, svg, poly_svg)
        rows.append(_expand(start, end))
    return rows


def _title_rows(puml: str) -> List[int]:
    start, end = find_title_bounds(puml.splitlines())
    return _expand(start, end)


def get_activity_positions(puml: str, svg: str) -> Dict[str, object]:
    """Return editor rows per element type for frontend hover highlighting."""
    poly_rows, while_rows = _poly_and_while_rows(puml, svg)
    return {
        "activities": _activity_rows(puml, svg),
        "polys": poly_rows,
        "whiles": while_rows,
        "notes": _note_rows(puml, svg),
        "groups": _group_rows(puml, svg),
        "ellipses": _ellipse_rows(puml, svg),
        "connectors": _connector_rows(puml, svg),
        "merges": _merge_rows(puml, svg),
        "arrows": _arrow_rows(puml, svg),
        "title": _title_rows(puml),
    }
