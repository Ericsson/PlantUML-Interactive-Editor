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

"""Multi-page (``newpage``) sequence diagrams.

PlantUML splits a diagram into pages at every ``newpage`` line and renders one
page per image (``-pipeimageindex N``). Every interactive sequence operation
matches "the Nth message/note/group in the SVG" to "the Nth one in the puml",
so on page 2+ the SVG's first message is not the puml's first message.

Rather than teach every element module about pages, :func:`mask_other_pages`
hides the other pages' body lines behind sentinel comment lines. The module
then sees only the current page's elements, while line numbers stay global
(the line count is unchanged). :func:`unmask` puts the originals back after the
module has edited the masked text.

What PlantUML draws on every page is never masked: participant declarations,
``box``/``end box``, and groups whose block spans into the current page (their
box is drawn on each page they cover).
"""

import re
from typing import Dict, List, Set, Tuple

from .classes import parse_participant_declaration
from .group import VALID_GROUP_TYPES
from .util import is_page_break, note_regions

_BOX_RE = re.compile(r"^box(?:\s|$)")

# A puml comment, so it can never be read as a message, note, group, box or
# declaration by any element module.
_SENTINEL_PREFIX = "'@@page-mask:"
_SENTINEL_RE = re.compile(r"^'@@page-mask:(\d+)@@$")


def _note_lines(lines: List[str]) -> Set[int]:
    """Line indexes inside any note (header, body and ``end note``)."""
    inside: Set[int] = set()
    for start, end in note_regions("\n".join(lines)):
        inside.update(range(start, end + 1))
    return inside


def page_boundaries(puml: str) -> List[int]:
    """Line indexes of the ``newpage`` lines that split the diagram.

    A ``newpage`` inside a note body is note text, not a page break.
    """
    lines = puml.splitlines()
    in_note = _note_lines(lines)
    return [
        i
        for i, line in enumerate(lines)
        if i not in in_note and is_page_break(line.strip())
    ]


def page_count(puml: str) -> int:
    """Number of pages PlantUML renders for ``puml`` (at least 1)."""
    return len(page_boundaries(puml)) + 1


def clamp_page(puml: str, page: int) -> int:
    """Clamp a requested 0-based page to the pages ``puml`` has.

    The request carries the page that was on screen, which an edit removing
    ``newpage`` lines can leave past the last page.
    """
    return min(page, page_count(puml) - 1)


def page_span(puml: str, page: int) -> Tuple[int, int]:
    """Half-open line range ``[start, end)`` of a page's body.

    ``end`` is the page's terminating ``newpage`` line (or the line count for
    the last page), so the ``newpage`` itself is not part of the page.
    """
    boundaries = page_boundaries(puml)
    start = boundaries[page - 1] + 1 if page > 0 else 0
    end = boundaries[page] if page < len(boundaries) else len(puml.splitlines())
    return start, end


def _group_spans(lines: List[str], in_note: Set[int]) -> List[Tuple[int, int]]:
    """``(header, end)`` line pairs of every group block, nesting-aware."""
    spans: List[Tuple[int, int]] = []
    stack: List[int] = []
    for i, line in enumerate(lines):
        if i in in_note:
            continue
        stripped = line.strip()
        first_word = stripped.split(" ", 1)[0] if stripped else ""
        if first_word in VALID_GROUP_TYPES:
            stack.append(i)
        elif stripped == "end" and stack:
            spans.append((stack.pop(), i))
    return spans


def _is_global_line(stripped: str) -> bool:
    """Lines that describe what every page draws, so are never masked."""
    if stripped.startswith("@start") or stripped.startswith("@end"):
        return True
    # ``box`` must be its own word: ``boxA -> B: hi`` is a message.
    if _BOX_RE.match(stripped) or stripped == "end box":
        return True
    return parse_participant_declaration(stripped) is not None


def mask_other_pages(puml: str, page: int) -> Tuple[str, Dict[int, str]]:
    """Hide every other page's body behind sentinel lines.

    Returns the masked puml (same line count) and the originals keyed by
    sentinel id, for :func:`unmask`. A single-page diagram is returned as-is.
    """
    boundaries = page_boundaries(puml)
    if not boundaries:
        return puml, {}

    lines = puml.splitlines()
    in_note = _note_lines(lines)
    start, end = page_span(puml, page)

    keep: Set[int] = set(range(start, end))
    if page < len(boundaries):
        # The newpage closing this page bounds insertions (see find_insertion_index).
        keep.add(boundaries[page])
    for header, close in _group_spans(lines, in_note):
        if header < end and close >= start:
            keep.update((header, close))
    for i, line in enumerate(lines):
        if i not in in_note and _is_global_line(line.strip()):
            keep.add(i)

    originals: Dict[int, str] = {}
    masked = []
    for i, line in enumerate(lines):
        if i in keep:
            masked.append(line)
        else:
            originals[i] = line
            masked.append(f"{_SENTINEL_PREFIX}{i}@@")
    return "\n".join(masked), originals


def unmask(puml: str, originals: Dict[int, str]) -> str:
    """Restore the lines :func:`mask_other_pages` replaced.

    Sentinels are matched by content, not position, so this works after the
    element module has inserted or deleted lines on the current page.
    """
    if not originals:
        return puml
    restored = []
    for line in puml.splitlines():
        match = _SENTINEL_RE.match(line.strip())
        restored.append(originals[int(match.group(1))] if match else line)
    return "\n".join(restored)
