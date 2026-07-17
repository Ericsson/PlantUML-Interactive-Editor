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

"""Tests for sequence diagram note operations."""

import re

from plantuml_gui.sequence.note import (
    _note_color_from_line,
    _split_prefix_color,
    add_note,
    delete_note,
    edit_note,
    get_note_text,
    get_note_text_and_type,
    index_of_clicked_note,
)
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq


def extract_g_inner(svg_string):
    """Extract the innerHTML of the <g> element from full SVG."""
    match = re.search(r"<g>(.*?)</g>", svg_string, re.DOTALL)
    if match:
        return match.group(1)
    return None


def extract_note_path(svg_string, note_index=0):
    """Extract the outerHTML of the nth note body path from SVG."""
    d = Pq(svg_string)
    paths = list(d("path").items())
    count = 0
    i = 0
    while i < len(paths):
        path = paths[i]
        if path.attr("fill") != "#FEFFDD":
            i += 1
            continue
        if i + 1 < len(paths) and paths[i + 1].attr("fill") == "#FEFFDD":
            if count == note_index:
                return str(path)
            count += 1
            i += 2  # skip the fold-corner path, it's not a separate note
        else:
            i += 1
    return None


class TestNoteLineKeyword:
    def test_plain_note(self):
        from plantuml_gui.sequence.util import note_line_keyword

        assert note_line_keyword("note over Alice : text") == "note"

    def test_hnote(self):
        from plantuml_gui.sequence.util import note_line_keyword

        assert note_line_keyword("hnote left of Alice : text") == "hnote"

    def test_rnote(self):
        from plantuml_gui.sequence.util import note_line_keyword

        assert note_line_keyword("rnote right of Bob : text") == "rnote"

    def test_note_with_color_token(self):
        from plantuml_gui.sequence.util import note_line_keyword

        assert note_line_keyword("note #FFAAAA over Alice : text") == "note"

    def test_hnote_with_named_color_token(self):
        from plantuml_gui.sequence.util import note_line_keyword

        assert note_line_keyword("hnote #palegreen over Alice : text") == "hnote"

    def test_message_attached_shortcut(self):
        from plantuml_gui.sequence.util import note_line_keyword

        assert note_line_keyword("note left : text") == "note"
        assert note_line_keyword("hnote right : text") == "hnote"

    def test_non_note_line_returns_none(self):
        from plantuml_gui.sequence.util import note_line_keyword

        assert note_line_keyword("Alice -> Bob: Hello") is None
        assert note_line_keyword("participant Alice") is None

    def test_prefix_collision_not_matched(self):
        """A participant literally named 'notebook' must not be
        mistaken for a note line."""
        from plantuml_gui.sequence.util import note_line_keyword

        assert note_line_keyword("notebook -> Bob: Hello") is None


class TestFindNoteLineIndexMixedTypes:
    def test_ordinal_resolution_across_mixed_types(self):
        from plantuml_gui.sequence.util import _find_note_line_index

        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\n"
            "note over Alice : first\n"
            "hnote over Bob : second\n"
            "rnote over Alice : third\n"
            "@enduml"
        )
        assert _find_note_line_index(puml, 1) == 3
        assert _find_note_line_index(puml, 2) == 4
        assert _find_note_line_index(puml, 3) == 5

    def test_ordinal_resolution_with_colors(self):
        from plantuml_gui.sequence.util import _find_note_line_index

        puml = (
            "@startuml\nparticipant Alice\n"
            "note #FFAAAA over Alice : first\n"
            "hnote #palegreen over Alice : second\n"
            "@enduml"
        )
        assert _find_note_line_index(puml, 1) == 2
        assert _find_note_line_index(puml, 2) == 3


class TestAddNote:
    def test_add_note_over(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "over", "My note", 0.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : My note\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_note_left(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "left", "Left note", 0.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote left of Alice : Left note\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_note_right(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Bob", "right", "Right note", 0.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote right of Bob : Right note\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_note_spanning(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "spanning", "Span note", 0.0, "Bob")
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice, Bob : Span note\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_note_after_all_messages(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        # Use a very large y so it goes after all messages
        result = add_note(puml, svg, "Alice", "over", "End note", 99999.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nnote over Alice : End note\n@enduml"
        assert result == expected

    def test_add_note_between_messages(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: First\nBob -> Alice: Second\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        # Parse messages to get cy values and pick a y between them
        from plantuml_gui.sequence.classes import Diagram

        diagram = Diagram.from_svg(svg, puml)
        y_between = (diagram.messages[0].cy + diagram.messages[1].cy) / 2
        result = add_note(puml, svg, "Alice", "over", "Middle note", y_between)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: First\nnote over Alice : Middle note\nBob -> Alice: Second\n@enduml"
        assert result == expected

    def test_add_note_empty_text_returns_unchanged(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "over", "", 0.0)
        assert result == puml

    def test_add_note_multiline_text_is_escaped(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "over", "Line1\nLine2", 0.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Line1\\nLine2\nAlice -> Bob: Hello\n@enduml"
        assert result == expected
        # Still exactly 6 lines: the escaped \n must not split the note onto a new source line
        assert len(result.splitlines()) == 6

    def test_add_note_above_existing_note(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nnote over Alice : Existing\nBob -> Alice: Reply\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        # Use y=0 to place above everything
        result = add_note(puml, svg, "Alice", "over", "Above", 0.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Above\nAlice -> Bob: Hello\nnote over Alice : Existing\nBob -> Alice: Reply\n@enduml"
        assert result == expected

    def test_add_note_below_existing_note(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nnote over Alice : Existing\nBob -> Alice: Reply\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        # Use a y between the existing note and the second message
        from plantuml_gui.sequence.util import extract_note_positions

        note_positions = extract_note_positions(svg, puml)
        from plantuml_gui.sequence.classes import Diagram

        diagram = Diagram.from_svg(svg, puml)
        # y between existing note and Reply message
        y_between = (note_positions[0][0] + diagram.messages[1].cy) / 2
        result = add_note(puml, svg, "Bob", "over", "Between", y_between)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nnote over Alice : Existing\nnote over Bob : Between\nBob -> Alice: Reply\n@enduml"
        assert result == expected

    def test_add_note_no_messages(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "over", "Solo note", 50.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Solo note\n@enduml"
        assert result == expected

    def test_add_note_left_attached_to_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nBob -> Alice: Reply\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        from plantuml_gui.sequence.classes import Diagram

        diagram = Diagram.from_svg(svg, puml)
        # Use the exact cy of the first message
        result = add_note(
            puml, svg, "Alice", "left", "Attached", diagram.messages[0].cy
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nnote left : Attached\nBob -> Alice: Reply\n@enduml"
        assert result == expected

    def test_add_note_right_attached_to_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        from plantuml_gui.sequence.classes import Diagram

        diagram = Diagram.from_svg(svg, puml)
        result = add_note(
            puml, svg, "Bob", "right", "Side note", diagram.messages[0].cy
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nnote right : Side note\n@enduml"
        assert result == expected

    def test_add_note_left_far_from_message_uses_participant(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        # y=0 is far from any message
        result = add_note(puml, svg, "Alice", "left", "Far note", 0.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote left of Alice : Far note\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_note_right_outside_message_span_uses_participant(self):
        """Note right of Bob at same Y as Alice->Bob message but x outside message span
        should use participant syntax, not message-attached syntax."""
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nparticipant Carol\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        from plantuml_gui.sequence.classes import Diagram

        diagram = Diagram.from_svg(svg, puml)
        msg_cy = diagram.messages[0].cy
        # Carol's cx is to the right of the Alice->Bob message span
        carol_cx = diagram.participants[2].cx
        result = add_note(
            puml, svg, "Carol", "right", "Carol note", msg_cy, x_position=carol_cx
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nparticipant Carol\nAlice -> Bob: Hello\nnote right of Carol : Carol note\n@enduml"
        assert result == expected

    def test_add_note_near_self_message_uses_participant(self):
        """Note left/right near a self-message should use participant syntax, not message-attached."""
        puml = "@startuml\nparticipant Alice\nAlice -> Alice: self\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        from plantuml_gui.sequence.classes import Diagram

        diagram = Diagram.from_svg(svg, puml)
        msg_cy = diagram.messages[0].cy
        alice_cx = diagram.participants[0].cx
        result = add_note(
            puml, svg, "Alice", "right", "My note", msg_cy - 5, x_position=alice_cx
        )
        expected = "@startuml\nparticipant Alice\nnote right of Alice : My note\nAlice -> Alice: self\n@enduml"
        assert result == expected


class TestAddNoteWithType:
    """Covers note_type parameterization of add_note across all placements
    and the message-attached shortcut, mirroring TestAddNote's plain-note
    coverage but for hnote/rnote."""

    def test_add_hnote_over(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(
            puml, svg, "Alice", "over", "Hex note", 0.0, note_type="hnote"
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nhnote over Alice : Hex note\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_rnote_over(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(
            puml, svg, "Alice", "over", "Rect note", 0.0, note_type="rnote"
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nrnote over Alice : Rect note\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_hnote_left_far_from_message_uses_participant(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "left", "Far hex", 0.0, note_type="hnote")
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nhnote left of Alice : Far hex\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_rnote_right(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Bob", "right", "Far rect", 0.0, note_type="rnote")
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nrnote right of Bob : Far rect\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_hnote_spanning(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(
            puml,
            svg,
            "Alice",
            "spanning",
            "Span hex",
            0.0,
            "Bob",
            note_type="hnote",
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nhnote over Alice, Bob : Span hex\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_rnote_spanning(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(
            puml,
            svg,
            "Alice",
            "spanning",
            "Span rect",
            0.0,
            "Bob",
            note_type="rnote",
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nrnote over Alice, Bob : Span rect\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_hnote_left_attached_to_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nBob -> Alice: Reply\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        from plantuml_gui.sequence.classes import Diagram

        diagram = Diagram.from_svg(svg, puml)
        result = add_note(
            puml,
            svg,
            "Alice",
            "left",
            "Attached hex",
            diagram.messages[0].cy,
            note_type="hnote",
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nhnote left : Attached hex\nBob -> Alice: Reply\n@enduml"
        assert result == expected

    def test_add_rnote_right_attached_to_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        from plantuml_gui.sequence.classes import Diagram

        diagram = Diagram.from_svg(svg, puml)
        result = add_note(
            puml,
            svg,
            "Bob",
            "right",
            "Attached rect",
            diagram.messages[0].cy,
            note_type="rnote",
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nrnote right : Attached rect\n@enduml"
        assert result == expected

    def test_missing_note_type_defaults_to_note(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "over", "Default note", 0.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Default note\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_invalid_note_type_defaults_to_note(self):
        """An unrecognized note_type value (e.g. tampered request) must not
        produce invalid PlantUML syntax; falls back to plain note."""
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(
            puml, svg, "Alice", "over", "Fallback", 0.0, note_type="not-a-real-type"
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Fallback\nAlice -> Bob: Hello\n@enduml"
        assert result == expected


def extract_hnote_polygon(svg_string, index=0):
    d = Pq(svg_string)
    polygons = [
        p
        for p in d("polygon").items()
        if len((p.attr("points") or "").split(",")) // 2 == 7
    ]
    return str(polygons[index])


def extract_rnote_rect(svg_string, index=0):
    d = Pq(svg_string)
    rects = [r for r in d("rect").items() if r.attr("rx") is None]
    return str(rects[index])


class TestShapeBasedNoteDetection:
    """Covers index_of_clicked_note / extract_note_positions detecting
    hnote and rnote, custom colors, and excluding shape look-alikes
    (participant boxes, activation bars, group borders/tabs)."""

    def extract_hnote_polygon(self, svg_string, index=0):
        return extract_hnote_polygon(svg_string, index)

    def extract_rnote_rect(self, svg_string, index=0):
        return extract_rnote_rect(svg_string, index)

    def test_click_hnote(self):
        puml = "@startuml\nparticipant Alice\nhnote over Alice : hex note\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = self.extract_hnote_polygon(svg)
        assert index_of_clicked_note(svg, svgelement) == 1

    def test_click_rnote(self):
        puml = "@startuml\nparticipant Alice\nrnote over Alice : rect note\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = self.extract_rnote_rect(svg)
        assert index_of_clicked_note(svg, svgelement) == 1

    def test_click_second_of_mixed_types(self):
        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\n"
            "note over Alice : first\n"
            "hnote over Bob : second\n"
            "@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = self.extract_hnote_polygon(svg)
        assert index_of_clicked_note(svg, svgelement) == 2

    def test_click_third_of_mixed_types(self):
        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\n"
            "note over Alice : first\n"
            "hnote over Bob : second\n"
            "rnote over Alice : third\n"
            "@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = self.extract_rnote_rect(svg)
        assert index_of_clicked_note(svg, svgelement) == 3

    def test_detection_independent_of_custom_color(self):
        """A note colored to match a common non-note fill (white) must
        still be detected correctly by shape, not by fill value."""
        puml = "@startuml\nparticipant Alice\nrnote over Alice #FFFFFF : white rnote\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = self.extract_rnote_rect(svg)
        assert index_of_clicked_note(svg, svgelement) == 1

    def test_participant_box_not_detected_as_rnote(self):
        """Participant header rects must never be picked up as notes,
        even though both are plain <rect> with the same stroke-width."""
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nrnote over Alice : only note\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        from plantuml_gui.sequence.note import get_note_positions

        positions = get_note_positions(puml, svg)
        assert len(positions) == 1

    def test_activation_bar_not_detected_as_rnote(self):
        """Activation bars are plain <rect> too but use a different
        stroke-width than notes, so they must be excluded."""
        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\n"
            "activate Alice\n"
            "rnote over Alice #FFFFFF : white rnote\n"
            "deactivate Alice\n"
            "@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        from plantuml_gui.sequence.note import get_note_positions

        positions = get_note_positions(puml, svg)
        assert len(positions) == 1

    def test_group_border_and_tab_not_detected_as_note(self):
        """Group blocks render a <path> tab (6 points, like a note body)
        and a <rect> border - neither must be mistaken for a note."""
        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\n"
            "group g1\n"
            "Alice -> Bob : hi\n"
            "end\n"
            "note over Alice #FFFFFF : white note\n"
            "@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        from plantuml_gui.sequence.note import get_note_positions

        positions = get_note_positions(puml, svg)
        assert len(positions) == 1

    def test_message_arrowhead_not_detected_as_hnote(self):
        """Message arrowheads are 4-point <polygon>, hnote is 7-point;
        must not collide."""
        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\n"
            "Alice -> Bob : hello\n"
            "hnote over Alice : hex note\n"
            "@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        from plantuml_gui.sequence.note import get_note_positions

        positions = get_note_positions(puml, svg)
        assert len(positions) == 1

    def test_get_note_positions_mixed_types_ordered(self):
        from plantuml_gui.sequence.note import get_note_positions

        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\n"
            "note over Alice : first\n"
            "hnote over Bob : second\n"
            "rnote over Alice : third\n"
            "@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        positions = get_note_positions(puml, svg)
        assert [p["index"] for p in positions] == [3, 4, 5]
        # top-to-bottom document order
        assert positions[0]["cy"] < positions[1]["cy"] < positions[2]["cy"]


class TestIndexOfClickedNote:
    def test_click_first_note(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nnote over Alice : My note\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        assert svgelement is not None
        assert index_of_clicked_note(svg, svgelement) == 1

    def test_click_second_note(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nnote over Alice : First\nnote over Bob : Second\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 1)
        assert svgelement is not None
        assert index_of_clicked_note(svg, svgelement) == 2


class TestGetNoteText:
    def test_get_note_text(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : My note\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        assert get_note_text(puml, svg, svgelement) == "My note"

    def test_get_second_note_text(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : First\nnote over Bob : Second\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 1)
        assert get_note_text(puml, svg, svgelement) == "Second"

    def test_get_note_text_unescapes_newlines(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Line1\\nLine2\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        assert get_note_text(puml, svg, svgelement) == "Line1\nLine2"


class TestGetNoteType:
    def test_plain_note_type(self):
        from plantuml_gui.sequence.note import get_note_type

        puml = "@startuml\nparticipant Alice\nnote over Alice : text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        assert get_note_type(puml, svg, svgelement) == "note"

    def test_hnote_type(self):
        from plantuml_gui.sequence.note import get_note_type

        puml = "@startuml\nparticipant Alice\nhnote over Alice : text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_hnote_polygon(svg)
        assert get_note_type(puml, svg, svgelement) == "hnote"

    def test_rnote_type(self):
        from plantuml_gui.sequence.note import get_note_type

        puml = "@startuml\nparticipant Alice\nrnote over Alice : text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_rnote_rect(svg)
        assert get_note_type(puml, svg, svgelement) == "rnote"

    def test_type_of_second_note_in_mixed_diagram(self):
        from plantuml_gui.sequence.note import get_note_type

        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\n"
            "note over Alice : first\n"
            "rnote over Bob : second\n"
            "@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_rnote_rect(svg)
        assert get_note_type(puml, svg, svgelement) == "rnote"

    def test_type_with_custom_color(self):
        from plantuml_gui.sequence.note import get_note_type

        puml = (
            "@startuml\nparticipant Alice\nhnote over Alice #palegreen : text\n@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_hnote_polygon(svg)
        assert get_note_type(puml, svg, svgelement) == "hnote"


class TestEditNote:
    def test_edit_note(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Old text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        result = edit_note(puml, svg, svgelement, "New text")
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : New text\n@enduml"
        assert result == expected

    def test_edit_second_note(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : First\nnote over Bob : Second\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 1)
        result = edit_note(puml, svg, svgelement, "Updated")
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : First\nnote over Bob : Updated\n@enduml"
        assert result == expected

    def test_edit_note_multiline_text_is_escaped(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Old text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        result = edit_note(puml, svg, svgelement, "Line1\nLine2")
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Line1\\nLine2\n@enduml"
        assert result == expected

    def test_edit_note_same_type_is_text_only_change(self):
        puml = "@startuml\nparticipant Alice\nnote over Alice : Old text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        result = edit_note(puml, svg, svgelement, "New text", note_type="note")
        expected = "@startuml\nparticipant Alice\nnote over Alice : New text\n@enduml"
        assert result == expected

    def test_edit_note_changes_type_to_hnote(self):
        puml = "@startuml\nparticipant Alice\nnote over Alice : Old text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        result = edit_note(puml, svg, svgelement, "New text", note_type="hnote")
        expected = "@startuml\nparticipant Alice\nhnote over Alice : New text\n@enduml"
        assert result == expected

    def test_edit_hnote_changes_type_to_rnote(self):
        puml = "@startuml\nparticipant Alice\nhnote over Alice : Old text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_hnote_polygon(svg)
        result = edit_note(puml, svg, svgelement, "New text", note_type="rnote")
        expected = "@startuml\nparticipant Alice\nrnote over Alice : New text\n@enduml"
        assert result == expected

    def test_edit_rnote_changes_type_to_note(self):
        puml = "@startuml\nparticipant Alice\nrnote over Alice : Old text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_rnote_rect(svg)
        result = edit_note(puml, svg, svgelement, "New text", note_type="note")
        expected = "@startuml\nparticipant Alice\nnote over Alice : New text\n@enduml"
        assert result == expected

    def test_edit_note_preserves_placement_when_changing_type(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote left of Alice : Old text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        result = edit_note(puml, svg, svgelement, "New text", note_type="rnote")
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nrnote left of Alice : New text\n@enduml"
        assert result == expected

    def test_edit_note_preserves_color_token_when_changing_type(self):
        from plantuml_gui.sequence.util import iter_note_shapes

        puml = (
            "@startuml\nparticipant Alice\nnote over Alice #FFAAAA : Old text\n@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        shape, _note_type = iter_note_shapes(svg)[0]
        svgelement = str(shape)
        result = edit_note(puml, svg, svgelement, "New text", note_type="hnote")
        expected = (
            "@startuml\nparticipant Alice\nhnote over Alice #FFAAAA : New text\n@enduml"
        )
        assert result == expected

    def test_edit_note_invalid_type_leaves_keyword_unchanged(self):
        puml = "@startuml\nparticipant Alice\nnote over Alice : Old text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        result = edit_note(puml, svg, svgelement, "New text", note_type="not-a-type")
        expected = "@startuml\nparticipant Alice\nnote over Alice : New text\n@enduml"
        assert result == expected

    def test_edit_note_missing_type_leaves_keyword_unchanged(self):
        puml = "@startuml\nparticipant Alice\nrnote over Alice : Old text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_rnote_rect(svg)
        result = edit_note(puml, svg, svgelement, "New text")
        expected = "@startuml\nparticipant Alice\nrnote over Alice : New text\n@enduml"
        assert result == expected


class TestDeleteNote:
    def test_delete_note(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : My note\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        result = delete_note(puml, svg, svgelement)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\n@enduml"
        assert result == expected

    def test_delete_second_note(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : First\nnote over Bob : Second\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 1)
        result = delete_note(puml, svg, svgelement)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : First\n@enduml"
        assert result == expected


class TestAddNoteRoute:
    def test_add_note_over_route(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        test_data = {
            "plantuml": puml,
            "svg": svg,
            "participant": "Alice",
            "placement": "over",
            "text": "My note",
            "yPosition": 0.0,
        }
        with client:
            response = client.post(
                "/addNote",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : My note\nAlice -> Bob: Hello\n@enduml"
            assert response.get_json()["plantuml"] == expected

    def test_add_note_spanning_route(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        test_data = {
            "plantuml": puml,
            "svg": svg,
            "participant": "Alice",
            "placement": "spanning",
            "text": "Span note",
            "yPosition": 0.0,
            "secondParticipant": "Bob",
        }
        with client:
            response = client.post(
                "/addNote",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice, Bob : Span note\nAlice -> Bob: Hello\n@enduml"
            assert response.get_json()["plantuml"] == expected

    def test_add_note_with_note_type_route(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        test_data = {
            "plantuml": puml,
            "svg": svg,
            "participant": "Alice",
            "placement": "over",
            "text": "Hex note",
            "yPosition": 0.0,
            "noteType": "hnote",
        }
        with client:
            response = client.post(
                "/addNote",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            expected = "@startuml\nparticipant Alice\nparticipant Bob\nhnote over Alice : Hex note\nAlice -> Bob: Hello\n@enduml"
            assert response.get_json()["plantuml"] == expected

    def test_add_note_without_note_type_route_defaults_to_note(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        test_data = {
            "plantuml": puml,
            "svg": svg,
            "participant": "Alice",
            "placement": "over",
            "text": "Plain note",
            "yPosition": 0.0,
        }
        with client:
            response = client.post(
                "/addNote",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Plain note\nAlice -> Bob: Hello\n@enduml"
            assert response.get_json()["plantuml"] == expected

    def test_add_note_multiline_text_route(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        test_data = {
            "plantuml": puml,
            "svg": svg,
            "participant": "Alice",
            "placement": "over",
            "text": "Line1\nLine2",
            "yPosition": 0.0,
        }
        with client:
            response = client.post(
                "/addNote",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Line1\\nLine2\nAlice -> Bob: Hello\n@enduml"
            assert response.get_json()["plantuml"] == expected

    def test_add_note_empty_text_route(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        test_data = {
            "plantuml": puml,
            "svg": svg,
            "participant": "Alice",
            "placement": "over",
            "text": "",
            "yPosition": 0.0,
        }
        with client:
            response = client.post(
                "/addNote",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            assert response.get_json()["plantuml"] == puml


class TestNoteRoutes:
    def test_get_note_text_route(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : My note\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        test_data = {"plantuml": puml, "svg": svg, "svgelement": svgelement}
        with client:
            response = client.post(
                "/getSeqNoteText",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            assert response.get_json()["text"] == "My note"

    def test_get_note_text_route_returns_note_type(self, client):
        puml = "@startuml\nparticipant Alice\nhnote over Alice : My hex note\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_hnote_polygon(svg)
        test_data = {"plantuml": puml, "svg": svg, "svgelement": svgelement}
        with client:
            response = client.post(
                "/getSeqNoteText",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            data = response.get_json()
            assert data["text"] == "My hex note"
            assert data["noteType"] == "hnote"

    def test_edit_note_route(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Old text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        test_data = {
            "plantuml": puml,
            "svg": svg,
            "svgelement": svgelement,
            "text": "New text",
        }
        with client:
            response = client.post(
                "/editSeqNote",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : New text\n@enduml"
            assert response.get_json()["plantuml"] == expected

    def test_edit_note_route_with_note_type_change(self, client):
        puml = "@startuml\nparticipant Alice\nnote over Alice : Old text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        test_data = {
            "plantuml": puml,
            "svg": svg,
            "svgelement": svgelement,
            "text": "New text",
            "noteType": "rnote",
        }
        with client:
            response = client.post(
                "/editSeqNote",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            expected = (
                "@startuml\nparticipant Alice\nrnote over Alice : New text\n@enduml"
            )
            assert response.get_json()["plantuml"] == expected

    def test_edit_note_multiline_text_route(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Old text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        test_data = {
            "plantuml": puml,
            "svg": svg,
            "svgelement": svgelement,
            "text": "Line1\nLine2",
        }
        with client:
            response = client.post(
                "/editSeqNote",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Line1\\nLine2\n@enduml"
            assert response.get_json()["plantuml"] == expected

    def test_delete_note_route(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : My note\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        test_data = {"plantuml": puml, "svg": svg, "svgelement": svgelement}
        with client:
            response = client.post(
                "/deleteSeqNote",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            expected = "@startuml\nparticipant Alice\nparticipant Bob\n@enduml"
            assert response.get_json()["plantuml"] == expected


class TestGetNotePositions:
    PUML = """@startuml
participant Alice
participant Bob
note over Alice : first
Alice -> Bob: Hello
note over Bob : second
@enduml"""

    def test_positions_in_document_order(self):
        from plantuml_gui.sequence.note import get_note_positions

        svg = extract_g_inner(_create_svg_from_uml(self.PUML))
        positions = get_note_positions(self.PUML, svg)
        assert [p["index"] for p in positions] == [3, 5]
        # Notes are ordered top to bottom
        assert positions[0]["cy"] < positions[1]["cy"]

    def test_no_notes_returns_empty(self):
        from plantuml_gui.sequence.note import get_note_positions

        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        assert get_note_positions(puml, svg) == []

    def test_route_returns_positions(self, client):
        svg = extract_g_inner(_create_svg_from_uml(self.PUML))
        test_data = {"plantuml": self.PUML, "svg": svg}
        with client:
            response = client.post(
                "/getSequencePositions",
                data=__import__("json").dumps(test_data),
                content_type="application/json",
            )
            assert response.status_code == 200
            positions = response.get_json()["notes"]
            assert [p["index"] for p in positions] == [3, 5]


class TestNoteColorHelpers:
    """Pure-string tests for note color parsing."""

    def test_split_no_color(self):
        assert _split_prefix_color("note over Alice ") == ("note over Alice", "")

    def test_split_named_color(self):
        assert _split_prefix_color("note over Alice #LightBlue") == (
            "note over Alice",
            "LightBlue",
        )

    def test_split_hex_color(self):
        assert _split_prefix_color("note over Alice #FFAAAA") == (
            "note over Alice",
            "FFAAAA",
        )

    def test_split_spanning_color(self):
        assert _split_prefix_color("note over Alice, Bob #Orange") == (
            "note over Alice, Bob",
            "Orange",
        )

    def test_color_from_line(self):
        assert (
            _note_color_from_line("note over Alice #LightGreen : hello") == "LightGreen"
        )

    def test_color_from_line_absent(self):
        assert _note_color_from_line("note over Alice : hello") == ""


class TestEditNoteColor:
    def test_edit_note_adds_color(self):
        puml = "@startuml\nparticipant Alice\nnote over Alice : Text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        result = edit_note(puml, svg, svgelement, "Text", color="LightBlue")
        expected = (
            "@startuml\nparticipant Alice\nnote over Alice #LightBlue : Text\n@enduml"
        )
        assert result == expected

    def test_edit_note_none_color_param_keeps_existing(self):
        puml = (
            "@startuml\nparticipant Alice\nnote over Alice #LightBlue : Text\n@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        # A colored note renders with a non-default fill; find its body path by
        # shape (6-point path) rather than the default-fill helper.
        d = Pq(svg)
        svgelement = next(
            str(p) for p in d("path").items() if (p.attr("d") or "").count("L") + 1 == 6
        )
        result = edit_note(puml, svg, svgelement, "New")
        expected = (
            "@startuml\nparticipant Alice\nnote over Alice #LightBlue : New\n@enduml"
        )
        assert result == expected

    def test_edit_note_hnote_with_color(self):
        puml = "@startuml\nparticipant Alice\nhnote over Alice : Text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        d = Pq(svg)
        svgelement = next(str(p) for p in d("polygon").items())
        result = edit_note(puml, svg, svgelement, "Text", color="Khaki")
        expected = (
            "@startuml\nparticipant Alice\nhnote over Alice #Khaki : Text\n@enduml"
        )
        assert result == expected

    def test_get_note_text_and_type_returns_color(self):
        puml = "@startuml\nparticipant Alice\nnote over Alice : Text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_note_path(svg, 0)
        text, note_type, color = get_note_text_and_type(puml, svg, svgelement)
        assert (text, note_type, color) == ("Text", "note", "")
