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

"""Characterization tests: how ``else`` branches in an ``alt`` render, and that
existing element detection (messages, groups, notes) is unaffected by them.

PlantUML (1.2022.x) renders each ``else`` as a horizontal dashed separator
``<line style="stroke:#000000;stroke-width:1.0;stroke-dasharray:2.0,2.0;">``
spanning the group box's full width, followed - only when the ``else`` has a
label - by a bold font-size-11 ``<text>[label]</text>``. A bare ``else`` emits
only the line.
"""

import re

import pytest
from plantuml_gui.sequence.group import get_group_positions
from plantuml_gui.sequence.message import (
    get_message_positions,
    index_of_clicked_message,
)
from plantuml_gui.sequence.note import get_note_positions
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq

# Line indexes:
#   3 alt success | 4 m1 | 5 else failure | 6 m2 | 7 else | 8 m3 | 9 end
FLAT_ALT_ELSE = """@startuml
participant alice
participant bob
alt success
alice -> bob: m1
else failure
bob --> alice: m2
else
alice -> bob: m3
end
@enduml"""

# Line indexes:
#   3 alt outer | 4 m1 | 5 loop retry | 6 m2 | 7 end | 8 else other | 9 m3 | 10 end
NESTED_ALT_ELSE = """@startuml
participant alice
participant bob
alt outer
alice -> bob: m1
loop retry
bob -> alice: m2
end
else other
alice -> bob: m3
end
@enduml"""

# Self messages and a note directly after else separators (labeled and bare).
# Line indexes:
#   3 alt a | 4 self1 | 5 else b | 6 note | 7 m | 8 else | 9 self2 | 10 end
SELF_AND_NOTE_ALT_ELSE = """@startuml
participant alice
participant bob
alt a
alice -> alice: self1
else b
note over alice: n
bob -> alice: m
else
alice -> alice: self2
end
@enduml"""


def _svg(puml):
    """Render puml and return the inner markup of its <g> (what the frontend sends)."""
    match = re.search(r"<g>(.*)</g>", _create_svg_from_uml(puml), re.DOTALL)
    assert match
    return match.group(1)


def _else_separators(svg):
    """Return the else separator lines: dashed lines drawn in the group stroke."""
    return [
        line
        for line in Pq(svg)("line").items()
        if "stroke:#000000" in (line.attr("style") or "")
        and "stroke-dasharray" in (line.attr("style") or "")
    ]


@pytest.fixture(scope="module")
def flat_svg():
    return _svg(FLAT_ALT_ELSE)


@pytest.fixture(scope="module")
def nested_svg():
    return _svg(NESTED_ALT_ELSE)


@pytest.fixture(scope="module")
def self_note_svg():
    return _svg(SELF_AND_NOTE_ALT_ELSE)


class TestElseSvgMarkup:
    def test_one_separator_per_else(self, flat_svg):
        assert len(_else_separators(flat_svg)) == 2

    def test_separator_spans_group_box_width(self, flat_svg):
        box = next(r for r in Pq(flat_svg)("rect").items() if r.attr("fill") == "none")
        box_x = float(box.attr("x"))
        box_right = box_x + float(box.attr("width"))
        for line in _else_separators(flat_svg):
            assert float(line.attr("x1")) == box_x
            assert float(line.attr("x2")) == box_right
            assert line.attr("y1") == line.attr("y2")

    def test_separator_uses_message_stroke_width(self, flat_svg):
        # Same stroke-width as message arrows - the reason a naive
        # "line with stroke-width:1.0" message check would match it.
        for line in _else_separators(flat_svg):
            assert "stroke-width:1.0" in line.attr("style")

    def test_labeled_else_emits_bold_small_label_after_separator(self, flat_svg):
        first = _else_separators(flat_svg)[0]
        label = first.next()
        assert label[0].tag == "text"
        assert label.text() == "[failure]"
        assert label.attr("font-weight") == "bold"
        assert label.attr("font-size") == "11"

    def test_bare_else_emits_no_label(self, flat_svg):
        second = _else_separators(flat_svg)[1]
        assert second.next()[0].tag != "text"


class TestMessageDetectionWithElse:
    def test_flat_message_positions(self, flat_svg):
        positions = get_message_positions(FLAT_ALT_ELSE, flat_svg)
        assert [(p["index"], p["text"]) for p in positions] == [
            (4, "m1"),
            (6, "m2"),
            (8, "m3"),
        ]

    def test_nested_message_positions(self, nested_svg):
        positions = get_message_positions(NESTED_ALT_ELSE, nested_svg)
        assert [(p["index"], p["text"]) for p in positions] == [
            (4, "m1"),
            (6, "m2"),
            (9, "m3"),
        ]

    def test_self_messages_after_else(self, self_note_svg):
        positions = get_message_positions(SELF_AND_NOTE_ALT_ELSE, self_note_svg)
        assert [(p["index"], p["text"]) for p in positions] == [
            (4, "self1"),
            (7, "m"),
            (9, "self2"),
        ]

    def test_message_cy_is_ordered_around_separators(self, flat_svg):
        positions = get_message_positions(FLAT_ALT_ELSE, flat_svg)
        separators = [float(s.attr("y1")) for s in _else_separators(flat_svg)]
        cys = [p["cy"] for p in positions]
        assert cys[0] < separators[0] < cys[1] < separators[1] < cys[2]

    def test_separator_is_not_a_clicked_message(self, flat_svg):
        for line in _else_separators(flat_svg):
            assert index_of_clicked_message(flat_svg, str(line)) == -1

    def test_else_label_is_not_a_clicked_message(self, flat_svg):
        label = _else_separators(flat_svg)[0].next()
        assert index_of_clicked_message(flat_svg, str(label)) == -1

    def test_message_after_else_resolves_to_its_ordinal(self, flat_svg):
        texts = [
            t for t in Pq(flat_svg)("text").items() if t.text() in ("m1", "m2", "m3")
        ]
        assert [index_of_clicked_message(flat_svg, str(t)) for t in texts] == [1, 2, 3]


class TestGroupDetectionWithElse:
    def test_flat_group_positions(self, flat_svg):
        assert get_group_positions(FLAT_ALT_ELSE, flat_svg) == [
            {"headerIndex": 3, "endIndex": 9}
        ]

    def test_nested_group_positions(self, nested_svg):
        assert get_group_positions(NESTED_ALT_ELSE, nested_svg) == [
            {"headerIndex": 3, "endIndex": 10},
            {"headerIndex": 5, "endIndex": 7},
        ]


class TestNoteDetectionWithElse:
    def test_note_after_else_label(self, self_note_svg):
        notes = get_note_positions(SELF_AND_NOTE_ALT_ELSE, self_note_svg)
        assert [n["index"] for n in notes] == [6]
