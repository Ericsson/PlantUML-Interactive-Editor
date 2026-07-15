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

"""Tests for the box SVG classifier (:func:`is_box_rect`).

These render real PlantUML SVG (like the group tests) so the classifier is
validated against the actual renderer output rather than hand-written rects.
"""

import re

import pytest
from flask import json
from plantuml_gui.sequence.box import (
    TEOZ_PRAGMA,
    _participant_header_bounds,
    add_box,
    delete_box,
    edit_box,
    get_box_label,
    index_of_clicked_box,
    is_box_rect,
)
from plantuml_gui.sequence.classes import is_participant_rect
from plantuml_gui.sequence.positions import get_sequence_positions
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq


def _g_inner(puml):
    """Render puml and return the <g> inner HTML string.

    The full SVG carries an XML encoding declaration that lxml refuses; the
    <g> inner content holds every rect/text we classify.
    """
    match = re.search(r"<g>(.*?)</g>", _create_svg_from_uml(puml), re.DOTALL)
    assert match, "expected a <g> element in the rendered SVG"
    return match.group(1)


def _svg_of(puml):
    """Render puml and return the <g> inner HTML wrapped in a pyquery object."""
    return Pq(_g_inner(puml))


def _nth_box_rect_html(svg, n):
    """Return the outerHTML of the nth (0-based) box rect in document order."""
    bounds = _participant_header_bounds(svg)
    boxes = [rect for rect in svg("rect").items() if is_box_rect(rect, bounds)]
    return str(boxes[n])


def _box_rects(svg):
    """Return every rect the classifier flags as a box, in document order."""
    bounds = _participant_header_bounds(svg)
    return [rect for rect in svg("rect").items() if is_box_rect(rect, bounds)]


COLORED_BOX_PUML = """@startuml
box "Internal Service" #LightBlue
participant Bob
participant Alice
end box
participant Other
Bob -> Alice : hello
Alice -> Other : hi
@enduml"""

PLAIN_BOX_PUML = """@startuml
box "Plain Box"
participant Bob
participant Alice
end box
participant Other
Bob -> Alice : hello
@enduml"""

NESTED_TEOZ_PUML = """@startuml
!pragma teoz true
box "Internal Service" #LightBlue
participant Bob
box "Subteam"
participant Alice
participant John
end box
end box
participant Other
Bob -> Alice : hello
Alice -> John : hello
John -> Other: Hello
@enduml"""

# A diagram with every rect-producing element that shares or resembles the box
# style: a box, an activation bar, an rnote, and a group block.
MIXED_PUML = """@startuml
box "MyBox" #LightBlue
participant Bob
end box
participant Alice
activate Alice
rnote over Bob: rnote text
group MyGroup
Bob -> Alice : hello
end
deactivate Alice
@enduml"""


class TestBoxRectDetection:
    def test_detects_colored_box(self):
        assert len(_box_rects(_svg_of(COLORED_BOX_PUML))) == 1

    def test_detects_plain_default_box(self):
        # A box with no explicit color renders with the default #DDDDDD fill and
        # must still be recognized.
        assert len(_box_rects(_svg_of(PLAIN_BOX_PUML))) == 1

    def test_detects_both_nested_teoz_boxes(self):
        assert len(_box_rects(_svg_of(NESTED_TEOZ_PUML))) == 2

    def test_single_box_in_mixed_diagram(self):
        # Exactly one box, despite the activation bar, rnote, and group block
        # also present.
        assert len(_box_rects(_svg_of(MIXED_PUML))) == 1


class TestBoxRectRejections:
    def test_rejects_participant_rects(self):
        svg = _svg_of(COLORED_BOX_PUML)
        bounds = _participant_header_bounds(svg)
        participant_rects = [r for r in svg("rect").items() if is_participant_rect(r)]
        assert participant_rects  # sanity: fixture has participants
        for rect in participant_rects:
            assert not is_box_rect(rect, bounds)

    def test_rejects_activation_group_and_rnote_rects(self):
        # In the mixed diagram, every rect that is NOT the single box must be
        # rejected: participant headers, the activation bar, the rnote, and the
        # group box (both its visible fill:none rect and the layout rect).
        svg = _svg_of(MIXED_PUML)
        bounds = _participant_header_bounds(svg)
        boxes = [rect for rect in svg("rect").items() if is_box_rect(rect, bounds)]
        non_boxes = [
            rect for rect in svg("rect").items() if not is_box_rect(rect, bounds)
        ]
        assert len(boxes) == 1
        # The rnote shares the box's exact style/fill signature; confirm the
        # enclosure test still rejects it.
        rnote_rects = [r for r in non_boxes if (r.attr("fill") or "") == "#FEFFDD"]
        assert rnote_rects, "expected an rnote rect in the fixture"
        for rect in rnote_rects:
            assert not is_box_rect(rect, bounds)

    def test_rejects_when_no_participants_enclosed(self):
        # Without any participant to enclose, no rect should classify as a box.
        svg = _svg_of(MIXED_PUML)
        assert not any(is_box_rect(rect, []) for rect in svg("rect").items())


THREE_PARTICIPANT_PUML = """@startuml
participant alice
participant bob
participant carol
alice -> bob: m1
@enduml"""

# Line indexes in THREE_PARTICIPANT_PUML:
#   0: @startuml
#   1: participant alice
#   2: participant bob
#   3: participant carol
#   4: alice -> bob: m1
#   5: @enduml
ALICE_INDEX = 1
BOB_INDEX = 2
CAROL_INDEX = 3


class TestAddBox:
    def test_wraps_single_participant(self):
        result = add_box(THREE_PARTICIPANT_PUML, "My Box", "none", BOB_INDEX, BOB_INDEX)
        lines = result.splitlines()
        header = lines.index('box "My Box"')
        end = lines.index("end box")
        assert lines[header + 1] == "participant bob"
        assert lines[end - 1] == "participant bob"

    def test_wraps_multiple_participants(self):
        result = add_box(
            THREE_PARTICIPANT_PUML, "Group", "none", ALICE_INDEX, CAROL_INDEX
        )
        lines = result.splitlines()
        header = lines.index('box "Group"')
        end = lines.index("end box")
        assert header < lines.index("participant alice")
        assert lines.index("participant carol") < end
        # All three participant declarations sit inside the box.
        inside = lines[header + 1 : end]
        assert inside == [
            "participant alice",
            "participant bob",
            "participant carol",
        ]

    def test_normalizes_bottom_to_top_selection(self):
        # Selecting carol first then alice must produce the same result as
        # alice-then-carol.
        top_down = add_box(
            THREE_PARTICIPANT_PUML, "G", "none", ALICE_INDEX, CAROL_INDEX
        )
        bottom_up = add_box(
            THREE_PARTICIPANT_PUML, "G", "none", CAROL_INDEX, ALICE_INDEX
        )
        assert top_down == bottom_up

    def test_empty_title_produces_bare_box(self):
        result = add_box(THREE_PARTICIPANT_PUML, "", "none", BOB_INDEX, BOB_INDEX)
        lines = result.splitlines()
        assert "box" in lines
        assert "end box" in lines

    def test_color_appended_with_hash(self):
        result = add_box(
            THREE_PARTICIPANT_PUML, "Colored", "LightBlue", BOB_INDEX, BOB_INDEX
        )
        assert 'box "Colored" #LightBlue' in result.splitlines()

    def test_color_already_hashed_not_double_prefixed(self):
        result = add_box(
            THREE_PARTICIPANT_PUML, "Colored", "#ADD8E6", BOB_INDEX, BOB_INDEX
        )
        assert 'box "Colored" #ADD8E6' in result.splitlines()

    def test_none_color_omitted(self):
        result = add_box(THREE_PARTICIPANT_PUML, "Plain", "none", BOB_INDEX, BOB_INDEX)
        assert 'box "Plain"' in result.splitlines()

    def test_title_is_html_escaped(self):
        result = add_box(
            THREE_PARTICIPANT_PUML, "A & B <c>", "none", BOB_INDEX, BOB_INDEX
        )
        # Mirrors participant renaming: special characters are HTML-escaped.
        assert 'box "A &amp; B &lt;c&gt;"' in result.splitlines()

    def test_result_renders_as_a_box(self):
        # End-to-end: the produced puml renders to SVG with exactly one box.
        result = add_box(
            THREE_PARTICIPANT_PUML, "Rendered", "LightGreen", ALICE_INDEX, BOB_INDEX
        )
        assert len(_box_rects(_svg_of(result))) == 1


class TestBoxNestingTeoz:
    DISJOINT_PUML = """@startuml
box "First"
participant alice
end box
participant bob
participant carol
participant dave
alice -> bob: m1
@enduml"""
    # 0:@startuml 1:box First 2:alice 3:end box 4:bob 5:carol 6:dave 7:msg 8:@enduml

    NESTED_PUML = """@startuml
box "Outer"
participant alice
participant bob
participant carol
end box
participant dave
alice -> bob: m1
@enduml"""
    # 0:@startuml 1:box Outer 2:alice 3:bob 4:carol 5:end box 6:dave 7:msg 8:@enduml

    CONTAINING_PUML = """@startuml
participant alice
box "Inner"
participant bob
participant carol
end box
participant dave
alice -> bob: m1
@enduml"""
    # 0:@startuml 1:alice 2:box Inner 3:bob 4:carol 5:end box 6:dave 7:msg 8:@enduml

    def test_disjoint_range_adds_no_pragma(self):
        # New box around carol(5)..dave(6), separate from the box wrapping alice.
        result = add_box(self.DISJOINT_PUML, "Second", "none", 5, 6)
        assert TEOZ_PRAGMA not in result.splitlines()

    def test_nested_inside_existing_adds_pragma(self):
        # New box around bob(3) only, inside the Outer box (span 1..5).
        result = add_box(self.NESTED_PUML, "Bob's box", "none", 3, 3)
        assert TEOZ_PRAGMA in result.splitlines()

    def test_containing_existing_adds_pragma(self):
        # New box around alice(1)..dave(6) fully contains the Inner box (2..5).
        result = add_box(self.CONTAINING_PUML, "Outer", "none", 1, 6)
        assert TEOZ_PRAGMA in result.splitlines()

    def test_crossing_range_raises(self):
        # New box around alice(1)..bob(3) crosses the Inner box (2..5).
        with pytest.raises(ValueError, match="cross"):
            add_box(self.CONTAINING_PUML, "Bad", "none", 1, 3)

    def test_pragma_not_duplicated(self):
        already = self.NESTED_PUML.replace("@startuml", "@startuml\n" + TEOZ_PRAGMA, 1)
        # bob is now on line 4 after the pragma insertion.
        result = add_box(already, "Bob's box", "none", 4, 4)
        assert result.splitlines().count(TEOZ_PRAGMA) == 1

    def test_nested_result_renders_two_boxes(self):
        result = add_box(self.NESTED_PUML, "Bob's box", "LightBlue", 3, 3)
        assert len(_box_rects(_svg_of(result))) == 2


SINGLE_BOX_PUML = """@startuml
box "MyBox"
participant alice
participant bob
end box
participant carol
alice -> bob: m1
@enduml"""

NESTED_RENDER_PUML = """@startuml
!pragma teoz true
box "Outer"
participant alice
box "Inner"
participant bob
participant carol
end box
end box
participant dave
alice -> bob: m1
@enduml"""


class TestIndexOfClickedBox:
    def test_single_box_is_ordinal_one(self):
        svg = _g_inner(SINGLE_BOX_PUML)
        rect = _nth_box_rect_html(Pq(svg), 0)
        assert index_of_clicked_box(svg, rect) == 1

    def test_nested_outer_then_inner_ordinals(self):
        svg = _g_inner(NESTED_RENDER_PUML)
        outer = _nth_box_rect_html(Pq(svg), 0)
        inner = _nth_box_rect_html(Pq(svg), 1)
        assert index_of_clicked_box(svg, outer) == 1
        assert index_of_clicked_box(svg, inner) == 2


class TestDeleteBox:
    def test_delete_single_box_keeps_participants(self):
        svg = _g_inner(SINGLE_BOX_PUML)
        rect = _nth_box_rect_html(Pq(svg), 0)
        result = delete_box(SINGLE_BOX_PUML, svg, rect)
        lines = result.splitlines()
        assert 'box "MyBox"' not in lines
        assert "end box" not in lines
        # Participants survive the unwrap.
        assert "participant alice" in lines
        assert "participant bob" in lines
        assert "participant carol" in lines

    def test_delete_inner_box_keeps_outer(self):
        svg = _g_inner(NESTED_RENDER_PUML)
        inner = _nth_box_rect_html(Pq(svg), 1)
        result = delete_box(NESTED_RENDER_PUML, svg, inner)
        lines = result.splitlines()
        assert 'box "Outer"' in lines
        assert 'box "Inner"' not in lines
        # Exactly one box remains (the outer), still rendering.
        assert len(_box_rects(_svg_of(result))) == 1

    def test_delete_outer_box_keeps_inner(self):
        svg = _g_inner(NESTED_RENDER_PUML)
        outer = _nth_box_rect_html(Pq(svg), 0)
        result = delete_box(NESTED_RENDER_PUML, svg, outer)
        lines = result.splitlines()
        assert 'box "Outer"' not in lines
        assert 'box "Inner"' in lines
        # The outer's matching (last) "end box" is removed, not the inner's.
        assert lines.count("end box") == 1

    def test_delete_outer_removes_correct_end_box(self):
        # Depth-aware: deleting the outer box must remove the outer header and
        # the final end box, leaving the inner box balanced.
        svg = _g_inner(NESTED_RENDER_PUML)
        outer = _nth_box_rect_html(Pq(svg), 0)
        result = delete_box(NESTED_RENDER_PUML, svg, outer)
        # Inner box still parses as a balanced span.
        from plantuml_gui.sequence.box import _find_box_spans

        spans = _find_box_spans(result.splitlines())
        assert len(spans) == 1


class TestBoxRoutes:
    def test_add_box_route_returns_modified_puml(self, client):
        response = client.post(
            "/addBox",
            data=json.dumps(
                {
                    "plantuml": THREE_PARTICIPANT_PUML,
                    "startParticipantIndex": ALICE_INDEX,
                    "endParticipantIndex": BOB_INDEX,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        # No title/color supplied -> bare box.
        assert "box" in data["plantuml"].splitlines()
        assert "end box" in data["plantuml"].splitlines()

    def test_add_box_route_nested_adds_teoz(self, client):
        response = client.post(
            "/addBox",
            data=json.dumps(
                {
                    "plantuml": TestBoxNestingTeoz.NESTED_PUML,
                    "startParticipantIndex": 3,
                    "endParticipantIndex": 3,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert TEOZ_PRAGMA in data["plantuml"].splitlines()

    def test_add_box_route_crossing_returns_400(self, client):
        response = client.post(
            "/addBox",
            data=json.dumps(
                {
                    "plantuml": TestBoxNestingTeoz.CONTAINING_PUML,
                    "startParticipantIndex": 1,
                    "endParticipantIndex": 3,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data

    def test_delete_box_route_unwraps(self, client):
        svg = _g_inner(SINGLE_BOX_PUML)
        rect = _nth_box_rect_html(Pq(svg), 0)
        response = client.post(
            "/deleteSeqBox",
            data=json.dumps(
                {
                    "plantuml": SINGLE_BOX_PUML,
                    "svg": svg,
                    "svgelement": rect,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        lines = data["plantuml"].splitlines()
        assert 'box "MyBox"' not in lines
        assert "participant alice" in lines


class TestBoxNotConfusedWithNote:
    # A box rect and an rnote share the exact same SVG signature; only the
    # box encloses a participant. Detection must not conflate the two.
    BOX_AND_RNOTE_PUML = """@startuml
box "MyBox"
participant alice
participant bob
end box
rnote over alice: a real rnote
alice -> bob: m1
@enduml"""

    def test_note_detection_ignores_box(self):
        from plantuml_gui.sequence.note import get_note_positions

        svg = _g_inner(self.BOX_AND_RNOTE_PUML)
        notes = get_note_positions(self.BOX_AND_RNOTE_PUML, svg)
        # Exactly one note (the rnote); the box must not be counted.
        assert len(notes) == 1

    def test_box_still_detected_alongside_rnote(self):
        svg = _svg_of(self.BOX_AND_RNOTE_PUML)
        assert len(_box_rects(svg)) == 1


class TestBoxPositions:
    def test_get_sequence_positions_includes_boxes(self):
        svg = _g_inner(SINGLE_BOX_PUML)
        positions = get_sequence_positions(SINGLE_BOX_PUML, svg)
        assert "boxes" in positions
        boxes = positions["boxes"]
        assert len(boxes) == 1
        assert set(boxes[0].keys()) == {"headerIndex", "endIndex"}
        # header is the box line, end is its matching end box (after it).
        assert boxes[0]["headerIndex"] < boxes[0]["endIndex"]

    def test_box_positions_ordered_outer_then_inner(self):
        svg = _g_inner(NESTED_RENDER_PUML)
        boxes = get_sequence_positions(NESTED_RENDER_PUML, svg)["boxes"]
        assert len(boxes) == 2
        # Outer box header precedes inner box header (document/source order).
        assert boxes[0]["headerIndex"] < boxes[1]["headerIndex"]
        # Outer box fully contains the inner box.
        assert boxes[0]["headerIndex"] < boxes[1]["headerIndex"]
        assert boxes[1]["endIndex"] < boxes[0]["endIndex"]


class TestEditBox:
    COLORED_TITLED_PUML = """@startuml
box "Old Title" #LightBlue
participant alice
participant bob
end box
alice -> bob: m1
@enduml"""

    BARE_BOX_PUML = """@startuml
box
participant alice
participant bob
end box
alice -> bob: m1
@enduml"""

    def test_get_label_reads_title_and_color(self):
        svg = _g_inner(self.COLORED_TITLED_PUML)
        rect = _nth_box_rect_html(Pq(svg), 0)
        label = get_box_label(self.COLORED_TITLED_PUML, svg, rect)
        assert label == {"title": "Old Title", "color": "LightBlue"}

    def test_get_label_empty_for_bare_box(self):
        svg = _g_inner(self.BARE_BOX_PUML)
        rect = _nth_box_rect_html(Pq(svg), 0)
        label = get_box_label(self.BARE_BOX_PUML, svg, rect)
        assert label == {"title": "", "color": ""}

    def test_edit_sets_title_and_color_on_bare_box(self):
        svg = _g_inner(self.BARE_BOX_PUML)
        rect = _nth_box_rect_html(Pq(svg), 0)
        result = edit_box(self.BARE_BOX_PUML, svg, rect, "New", "LightGreen")
        lines = result.splitlines()
        assert 'box "New" #LightGreen' in lines
        # Participants preserved.
        assert "participant alice" in lines

    def test_edit_changes_existing_title_and_color(self):
        svg = _g_inner(self.COLORED_TITLED_PUML)
        rect = _nth_box_rect_html(Pq(svg), 0)
        result = edit_box(self.COLORED_TITLED_PUML, svg, rect, "Renamed", "Wheat")
        assert 'box "Renamed" #Wheat' in result.splitlines()
        assert "Old Title" not in result

    def test_edit_clears_title_and_color(self):
        svg = _g_inner(self.COLORED_TITLED_PUML)
        rect = _nth_box_rect_html(Pq(svg), 0)
        result = edit_box(self.COLORED_TITLED_PUML, svg, rect, "", "none")
        lines = result.splitlines()
        assert "box" in lines  # bare box header
        assert not any("#LightBlue" in ln for ln in lines)

    def test_edit_title_is_html_escaped(self):
        svg = _g_inner(self.BARE_BOX_PUML)
        rect = _nth_box_rect_html(Pq(svg), 0)
        result = edit_box(self.BARE_BOX_PUML, svg, rect, "A & B", "none")
        assert 'box "A &amp; B"' in result.splitlines()

    def test_get_label_roundtrips_escaped_title(self):
        # Editing with special chars then reading back gives the original text.
        svg = _g_inner(self.BARE_BOX_PUML)
        rect = _nth_box_rect_html(Pq(svg), 0)
        edited = edit_box(self.BARE_BOX_PUML, svg, rect, "A & B", "none")
        svg2 = _g_inner(edited)
        rect2 = _nth_box_rect_html(Pq(svg2), 0)
        label = get_box_label(edited, svg2, rect2)
        assert label["title"] == "A & B"


class TestEditBoxRoutes:
    TITLED_PUML = """@startuml
box "T" #LightBlue
participant alice
participant bob
end box
alice -> bob: m1
@enduml"""

    def test_get_box_label_route(self, client):
        svg = _g_inner(self.TITLED_PUML)
        rect = _nth_box_rect_html(Pq(svg), 0)
        response = client.post(
            "/getSeqBoxLabel",
            data=json.dumps(
                {"plantuml": self.TITLED_PUML, "svg": svg, "svgelement": rect}
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert data == {"title": "T", "color": "LightBlue"}

    def test_edit_box_route(self, client):
        svg = _g_inner(self.TITLED_PUML)
        rect = _nth_box_rect_html(Pq(svg), 0)
        response = client.post(
            "/editSeqBox",
            data=json.dumps(
                {
                    "plantuml": self.TITLED_PUML,
                    "svg": svg,
                    "svgelement": rect,
                    "title": "Updated",
                    "color": "Khaki",
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert 'box "Updated" #Khaki' in data["plantuml"].splitlines()
