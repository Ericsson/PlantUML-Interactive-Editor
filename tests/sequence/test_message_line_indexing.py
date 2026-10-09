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

"""Regression tests for message-line <-> source-line index mapping.

Reverse arrows (``A <- B``, ``A <[#c]- B``) must be recognized as messages just
like forward ones, so the SVG-parsed message list stays aligned with the puml
source lines. A misalignment here silently breaks delete, editor<->diagram hover
highlighting, and note insertion for any diagram containing a reverse arrow.

These use the real PlantUML render (including ``!pragma teoz true``) so the
alignment is validated against the exact SVG the app parses at runtime.
"""

import re

import pytest
from plantuml_gui.sequence.classes import Diagram, is_message_line
from plantuml_gui.sequence.message import (
    delete_message,
    get_message_positions,
)
from plantuml_gui.sequence.note import add_note
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq

# A diagram exercising every arrow direction the SVG parser counts: reverse
# (``<-``), forward (``->``), colored reverse/forward (``<[#red]-`` /
# ``-[#red]>``), a self message, and a dotted forward (``-->``). It also puts an
# ``alt``/``else`` block around some messages, whose ``<size:12>`` labels contain
# a ``<`` and a ``:`` and must NOT be miscounted as messages.
PUML = """@startuml
!pragma teoz true
participant Access
participant SMF
participant PCF
autonumber
SMF<-PCF:R1
SMF->PCF:R2
SMF->Access:R3
SMF<[#red]-PCF: R4
SMF-[#red]>PCF: R5
SMF<-Access:R6
SMF -> SMF: 123
SMF->PCF:R8
SMF<-PCF:R9
alt <size:12>a) Rule Update</size>
SMF-[#red]>Access:R10
SMF<[#red]-Access:R11
else <size:12>b) Rule Remove</size>
SMF --> Access: R12
SMF-[#red]>Access:R13
SMF<[#red]-Access:R14
end
@enduml"""

# 0-based source-line index of every message line above, in source order.
EXPECTED_MESSAGE_LINES = [6, 7, 8, 9, 10, 11, 12, 13, 14, 16, 17, 19, 20, 21]


def _svg_inner(puml):
    """Render puml and return the inner content of the top-level <g> element.

    Mirrors what the frontend posts back to the sequence routes (the SVG's
    ``<g>`` innerHTML), so parsing matches runtime behavior.
    """
    svg = _create_svg_from_uml(puml)
    return re.search(r"<g>(.*)</g>", svg, re.DOTALL).group(1)


def _nth_message_element(svg_inner, message_index):
    """Return the outerHTML of the <text> element of the nth message (0-based).

    Uses the same element grouping as Diagram._parse_messages so the returned
    element resolves back to that message via index_of_clicked_message.
    """
    d = Pq(svg_inner)
    elements = list(d("*").items())
    i = 0
    count = 0
    while i < len(elements):
        group = elements[i : i + 5]
        tags = [el[0].tag for el in group]
        if tags[:4] == ["polygon", "polygon", "line", "text"]:
            step, text = 4, group[3]
        elif tags[:5] == ["line", "line", "line", "polygon", "text"]:
            step, text = 5, group[4]
        elif tags[:3] == ["polygon", "line", "text"]:
            step, text = 3, group[2]
        else:
            i += 1
            continue
        if count == message_index:
            return str(text)
        count += 1
        i += step
    return None


def test_reverse_and_colored_arrows_map_to_correct_source_lines():
    """Every message (any direction) maps to its own puml source line."""
    inner = _svg_inner(PUML)
    diagram = Diagram.from_svg(inner, PUML)

    assert len(diagram.messages) == len(EXPECTED_MESSAGE_LINES)
    assert [m.index for m in diagram.messages] == EXPECTED_MESSAGE_LINES


def test_delete_reverse_arrow_message_removes_that_line():
    """Deleting a reverse-arrow message removes its own line, not another."""
    inner = _svg_inner(PUML)
    # 6th message (0-based index 5) is "SMF<-Access:R6", a reverse arrow.
    element = _nth_message_element(inner, 5)
    result = delete_message(PUML, inner, element)

    assert "SMF<-Access:R6" not in result
    # Neighbors must be untouched.
    assert "SMF-[#red]>PCF: R5" in result
    assert "SMF -> SMF: 123" in result


def test_note_insertion_between_reverse_arrows_lands_at_correct_line():
    """A note dropped between two messages is inserted between their lines."""
    inner = _svg_inner(PUML)
    positions = get_message_positions(PUML, inner)
    # positions are in source order; [0] == R1 (reverse), [1] == R2.
    y = (positions[0]["cy"] + positions[1]["cy"]) / 2

    result = add_note(PUML, inner, "SMF", "over", "MYNOTE", y)
    lines = result.splitlines()
    note_line = next(i for i, ln in enumerate(lines) if "MYNOTE" in ln)
    r1_line = next(i for i, ln in enumerate(lines) if "SMF<-PCF:R1" in ln)
    r2_line = next(i for i, ln in enumerate(lines) if "SMF->PCF:R2" in ln)

    assert r1_line < note_line < r2_line


@pytest.mark.parametrize(
    "line",
    [
        "A -> B: hi",  # forward
        "A --> B: hi",  # dotted forward
        "A ->> B: hi",  # thin forward
        "A -x B: hi",  # lost-message head
        "A <- B: hi",  # reverse
        "A <-- B: hi",  # dotted reverse
        "A <-> B: hi",  # bidirectional
        "A -[#red]> B: hi",  # colored forward
        "A <[#red]- B: hi",  # colored reverse
        "A -> A: self",  # self message
        "Web-Server -> Client: hi",  # dash in participant name
    ],
)
def test_is_message_line_accepts_every_arrow_direction(line):
    assert is_message_line(line) is True


@pytest.mark.parametrize(
    "line",
    [
        "alt <size:12>a) Rule Update</size>",  # group label: '<' before ':'
        "else <size:12>b) Rule Remove</size>",
        "note over A : some text",  # note, arrow only in free text
        "note left of A : x -> y",  # arrow after the colon
        "participant Access",
        "autonumber",
        "@startuml",
        "end",
        "group My Group",
    ],
)
def test_is_message_line_rejects_non_messages(line):
    assert is_message_line(line) is False
