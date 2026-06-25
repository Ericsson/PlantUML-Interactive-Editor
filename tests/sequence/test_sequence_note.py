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
    add_note,
    delete_note,
    edit_note,
    get_note_text,
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
    for i, path in enumerate(paths):
        if path.attr("fill") != "#FEFFDD":
            continue
        if i + 1 < len(paths) and paths[i + 1].attr("fill") == "#FEFFDD":
            if count == note_index:
                return str(path)
            count += 1
    return None


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
