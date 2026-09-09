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

"""Tests for the activity positions map powering editor->diagram hover."""

import re

from flask import json
from plantuml_gui.activity.positions import get_activity_positions
from plantuml_gui.shared.render import _create_svg_from_uml


def extract_g_inner(svg_string):
    """Extract the innerHTML of the <g> element from full SVG."""
    match = re.search(r"<g>(.*?)</g>", svg_string, re.DOTALL)
    if match:
        return match.group(1)
    return None


# Line indexes:
#  0 @startuml             13 :Loop body;          26 end fork
#  1 title                 14 endwhile (done)      27 repeat
#  2 My flow               15 (A)                  28 :Repeat body;
#  3 endtitle              16 note right           29 repeat while (again?)
#  4 start                 17 a note               30 -> labeled arrow;
#  5 :First activity;      18 end note             31 switch (what?)
#  6 if (cond?) then (yes) 19 partition Init {     32 case ( one)
#  7 :Yes branch;          20 :Inside part;        33 :Case one;
#  8 else (no)             21 }                    34 case ( two)
#  9 :No branch            22 fork                 35 :Case two;
# 10 continues;            23 :Par one;            36 endswitch
# 11 endif                 24 fork again           37 stop
# 12 while (more?) is (yes)25 :Par one b;          38 @enduml
COMPREHENSIVE_PUML = """@startuml
title
My flow
endtitle
start
:First activity;
if (cond?) then (yes)
:Yes branch;
else (no)
:No branch
continues;
endif
while (more?) is (yes)
:Loop body;
endwhile (done)
(A)
note right
a note
end note
partition Init {
:Inside part;
}
fork
:Par one;
fork again
:Par one b;
end fork
repeat
:Repeat body;
repeat while (again?)
-> labeled arrow;
switch (what?)
case ( one)
:Case one;
case ( two)
:Case two;
endswitch
stop
@enduml"""

REPEAT_WITH_BACKWARD_PUML = """@startuml
start
repeat
:Body;
backward:Go back;
repeat while (again?)
:After;
stop
@enduml"""


class TestGetActivityPositions:
    def test_comprehensive_diagram(self):
        svg = extract_g_inner(_create_svg_from_uml(COMPREHENSIVE_PUML))
        positions = get_activity_positions(COMPREHENSIVE_PUML, svg)

        assert positions["activities"] == [
            [5],
            [7],
            [9, 10],
            [13],
            [20],
            [23],
            [25],
            [28],
            [33],
            [35],
        ]
        assert positions["polys"] == [[6, 8, 11], [29], [31, 36]]
        assert positions["whiles"] == [[12, 14]]
        assert positions["notes"] == [[16, 17, 18]]
        assert positions["groups"] == [[19, 21]]
        assert positions["ellipses"] == [[4], [37]]
        assert positions["connectors"] == [[15]]
        assert positions["title"] == [1, 2, 3]
        # merges: endif, repeat and endswitch merge markers in document order
        assert sorted(positions["merges"]) == [[11], [27], [36]]
        # arrows: the labeled arrow plus both switch case labels
        assert sorted(positions["arrows"]) == [[30], [32], [34]]

    def test_repeat_without_backward_does_not_shift_later_activities(self):
        # A repeat block only renders a backward box when a backward line
        # exists; the counting must not reserve a slot for a missing one.
        puml = "\n".join(
            line
            for line in REPEAT_WITH_BACKWARD_PUML.splitlines()
            if not line.startswith("backward")
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        positions = get_activity_positions(puml, svg)
        assert positions["activities"] == [[3], [5]]

    def test_repeat_with_backward_maps_backward_box(self):
        svg = extract_g_inner(_create_svg_from_uml(REPEAT_WITH_BACKWARD_PUML))
        positions = get_activity_positions(REPEAT_WITH_BACKWARD_PUML, svg)
        assert positions["activities"] == [[3], [4], [6]]

    def test_empty_types_for_minimal_diagram(self):
        puml = "@startuml\nstart\n:Only;\nstop\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        positions = get_activity_positions(puml, svg)
        assert positions["activities"] == [[2]]
        assert positions["ellipses"] == [[1], [3]]
        assert positions["polys"] == []
        assert positions["whiles"] == []
        assert positions["notes"] == []
        assert positions["groups"] == []
        assert positions["connectors"] == []
        assert positions["merges"] == []
        assert positions["arrows"] == []
        assert positions["title"] == []

    def test_route_returns_positions(self, client):
        svg = extract_g_inner(_create_svg_from_uml(COMPREHENSIVE_PUML))
        with client:
            response = client.post(
                "/getActivityPositions",
                data=json.dumps({"plantuml": COMPREHENSIVE_PUML, "svg": svg}),
                content_type="application/json",
            )
            assert response.status_code == 200
            positions = response.get_json()
            assert positions["activities"][0] == [5]
            assert positions["whiles"] == [[12, 14]]
            assert positions["groups"] == [[19, 21]]


class TestNthEllipseRow:
    """Unit tests for the _nth_ellipse_row helper, including the index-0 edge
    case where Python's negative-index wrap (lines[-1]) would previously cause
    the first line to be skipped when the last line starts with 'note'."""

    def test_start_on_first_line_is_found(self):
        """start at index 0 must be returned as row 0, not silently skipped."""
        from plantuml_gui.activity.positions import _nth_ellipse_row

        lines = ["start", ":do thing;", "stop"]
        assert _nth_ellipse_row(lines, 1) == 0

    def test_start_on_first_line_not_skipped_when_last_line_starts_with_note(self):
        """Regression: lines[-1] wrap made index-0 look note-preceded when the
        last line of the file started with 'note'."""
        from plantuml_gui.activity.positions import _nth_ellipse_row

        lines = ["start", ":do thing;", "stop", "note something"]
        # 'start' is at index 0; last line starts with 'note', which would
        # previously make the guard fire and skip 'start'.
        assert _nth_ellipse_row(lines, 1) == 0

    def test_ellipse_after_note_keyword_is_skipped(self):
        """An ellipse keyword immediately following a 'note' line is skipped,
        matching get_index_ellipse behaviour."""
        from plantuml_gui.activity.positions import _nth_ellipse_row

        lines = ["start", "note right", "end", ":activity;", "stop"]
        # 'end' at index 2 is preceded by 'note right' → should be skipped.
        # Only 'start' (index 0) and 'stop' (index 4) count.
        assert _nth_ellipse_row(lines, 1) == 0
        assert _nth_ellipse_row(lines, 2) == 4

    def test_returns_minus_one_when_not_enough_ellipses(self):
        from plantuml_gui.activity.positions import _nth_ellipse_row

        lines = ["start", ":do thing;", "stop"]
        assert _nth_ellipse_row(lines, 3) == -1
