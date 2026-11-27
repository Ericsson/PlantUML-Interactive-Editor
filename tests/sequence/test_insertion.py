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

"""Y-based insertion of messages and notes around group boundaries.

Regression: a message added below a group's last message, but still inside
the group's box, was inserted after the group's 'end' (outside the group).
"""

import re

import pytest
from flask import json
from plantuml_gui.sequence.classes import Diagram
from plantuml_gui.sequence.group import _group_box_rects, group_boundary_positions
from plantuml_gui.sequence.message import add_message
from plantuml_gui.sequence.note import add_note
from plantuml_gui.sequence.pages import current_page_end, mask_other_pages
from plantuml_gui.shared.render import _create_svg_from_uml


def _svg(puml: str, page: int = 0) -> str:
    match = re.search(r"<g>(.*)</g>", _create_svg_from_uml(puml, page), re.DOTALL)
    assert match
    return match.group(1)


def _box(svg: str, n: int = 0) -> tuple[float, float]:
    """(top, bottom) of the nth group box."""
    rect = _group_box_rects(svg)[n]
    top = float(rect.attr("y"))
    return top, top + float(rect.attr("height"))


def _message_cys(svg: str, puml: str) -> list[float]:
    return [m.cy for m in Diagram.from_svg(svg, puml).messages]


def _add(puml: str, svg: str, y: float) -> list[str]:
    return add_message(puml, svg, "new", [42, int(y)], [95, int(y)]).splitlines()


ALT = """@startuml
participant alice
participant bob
alice -> bob: m0
alt cond
alice -> bob: m1
else other
bob -> alice: m2
end
@enduml"""


class TestGroupBoundaries:
    @pytest.fixture
    def svg(self):
        return _svg(ALT)

    def test_below_last_message_inside_box_goes_before_end(self, svg):
        m2 = _message_cys(svg, ALT)[2]
        _top, bottom = _box(svg)
        lines = _add(ALT, svg, (m2 + bottom) / 2)
        assert lines[8:10] == ["alice -> bob: new", "end"]

    def test_below_box_goes_after_end(self, svg):
        _top, bottom = _box(svg)
        lines = _add(ALT, svg, bottom + 5)
        assert lines[8:10] == ["end", "alice -> bob: new"]

    def test_above_box_goes_before_header(self, svg):
        m0 = _message_cys(svg, ALT)[0]
        top, _bottom = _box(svg)
        lines = _add(ALT, svg, (m0 + top) / 2)
        assert lines[4:6] == ["alice -> bob: new", "alt cond"]

    def test_inside_box_above_first_message_goes_after_header(self, svg):
        m1 = _message_cys(svg, ALT)[1]
        top, _bottom = _box(svg)
        lines = _add(ALT, svg, (top + m1) / 2)
        assert lines[4:6] == ["alt cond", "alice -> bob: new"]

    def test_else_separator_splits_branches(self, svg):
        boundaries = dict((i, y) for y, i in group_boundary_positions(ALT, svg))
        else_y = boundaries[6]
        m1, m2 = _message_cys(svg, ALT)[1:3]
        above = _add(ALT, svg, (m1 + else_y) / 2)
        assert above[6:8] == ["alice -> bob: new", "else other"]
        below = _add(ALT, svg, (else_y + m2) / 2)
        assert below[6:8] == ["else other", "alice -> bob: new"]

    def test_boundary_positions(self, svg):
        top, bottom = _box(svg)
        positions = group_boundary_positions(ALT, svg)
        assert [i for _y, i in positions] == [4, 6, 8]
        assert positions[0][0] == top
        assert positions[2][0] == bottom
        assert top < positions[1][0] < bottom

    def test_note_below_last_message_inside_box_goes_before_end(self, svg):
        m2 = _message_cys(svg, ALT)[2]
        _top, bottom = _box(svg)
        result = add_note(
            ALT, svg, "alice", "over", "n", (m2 + bottom) / 2, x_position=42
        )
        assert result.splitlines()[8:10] == ["note over alice : n", "end"]


NESTED = """@startuml
participant alice
participant bob
group outer
alice -> bob: m1
loop inner
bob -> alice: m2
end
end
@enduml"""


class TestNestedGroups:
    def test_between_inner_and_outer_end_stays_in_outer(self):
        svg = _svg(NESTED)
        _itop, inner_bottom = _box(svg, 1)
        _otop, outer_bottom = _box(svg, 0)
        assert inner_bottom < outer_bottom
        lines = _add(NESTED, svg, (inner_bottom + outer_bottom) / 2)
        assert lines[7:10] == ["end", "alice -> bob: new", "end"]

    def test_below_inner_last_message_stays_in_inner(self):
        svg = _svg(NESTED)
        m2 = _message_cys(svg, NESTED)[1]
        _itop, inner_bottom = _box(svg, 1)
        lines = _add(NESTED, svg, (m2 + inner_bottom) / 2)
        assert lines[6:9] == ["bob -> alice: m2", "alice -> bob: new", "end"]


SPANNING = """@startuml
participant alice
participant bob
group g
alice -> bob: m1
newpage
bob -> alice: m2
end
@enduml"""


class TestGroupSpanningPages:
    def test_current_page_end(self):
        assert current_page_end(ALT) == 9
        assert current_page_end(mask_other_pages(SPANNING, 0)[0]) == 5
        assert current_page_end(mask_other_pages(SPANNING, 1)[0]) == 8

    def _post_add(self, client, page: int, y: float) -> list[str]:
        response = client.post(
            "/addMessage",
            data=json.dumps(
                {
                    "plantuml": SPANNING,
                    "svg": _svg(SPANNING, page),
                    "message": "new",
                    "firstcoordinates": [42, y],
                    "secondcoordinates": [95, y],
                    "page": page,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200, response.data
        return response.get_json()["plantuml"].splitlines()

    def test_inside_box_below_last_message_stays_on_first_page(self, client):
        masked = mask_other_pages(SPANNING, 0)[0]
        svg = _svg(SPANNING, 0)
        m1 = _message_cys(svg, masked)[0]
        _top, bottom = _box(svg)
        lines = self._post_add(client, 0, (m1 + bottom) / 2)
        assert lines[5:7] == ["alice -> bob: new", "newpage"]

    def test_above_first_message_stays_on_second_page(self, client):
        # The continued box on page 2 has no keyword tab, so it is not a
        # group box; the opening header (on page 1) must not be used either.
        masked = mask_other_pages(SPANNING, 1)[0]
        m2 = _message_cys(_svg(SPANNING, 1), masked)[0]
        lines = self._post_add(client, 1, m2 - 10)
        assert lines[5:8] == ["newpage", "alice -> bob: new", "bob -> alice: m2"]
