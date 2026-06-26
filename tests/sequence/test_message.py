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

"""Tests for sequence diagram message edit and delete operations."""

import re

from flask import json
from plantuml_gui.sequence.message import (
    delete_message,
    edit_message_text,
    get_message_text,
    index_of_clicked_message,
)
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq


def extract_g_inner(svg_string):
    """Extract the innerHTML of the <g> element from full SVG."""
    match = re.search(r"<g>(.*?)</g>", svg_string, re.DOTALL)
    if match:
        return match.group(1)
    return None


def extract_message_element(svg_string, message_index=0, element_type="polygon"):
    """Extract the outerHTML of an element from the nth message group.

    element_type can be 'polygon', 'line', or 'text'.
    Returns the first matching element in the message group.
    """
    d = Pq(svg_string)
    elements = list(d("*").items())
    i = 0
    msg_count = 0

    while i < len(elements):
        group = elements[i : i + 5]
        tags = [el[0].tag for el in group]

        if tags[:4] == ["polygon", "polygon", "line", "text"]:
            if msg_count == message_index:
                for el in group[:4]:
                    if el[0].tag == element_type:
                        return str(el)
            msg_count += 1
            i += 4
        elif tags[:5] == ["line", "line", "line", "polygon", "text"]:
            if msg_count == message_index:
                for el in group[:5]:
                    if el[0].tag == element_type:
                        return str(el)
            msg_count += 1
            i += 5
        elif tags[:3] == ["polygon", "line", "text"]:
            if msg_count == message_index:
                for el in group[:3]:
                    if el[0].tag == element_type:
                        return str(el)
            msg_count += 1
            i += 3
        else:
            i += 1

    return None


class TestIndexOfClickedMessage:
    def test_click_polygon_normal_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        assert svgelement is not None
        assert index_of_clicked_message(svg, svgelement) == 1

    def test_click_line_normal_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "line")
        assert svgelement is not None
        assert index_of_clicked_message(svg, svgelement) == 1

    def test_click_text_normal_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "text")
        assert svgelement is not None
        assert index_of_clicked_message(svg, svgelement) == 1

    def test_click_second_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nBob -> Alice: Bye\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 1, "polygon")
        assert svgelement is not None
        assert index_of_clicked_message(svg, svgelement) == 2

    def test_click_self_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Alice: Think\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        assert svgelement is not None
        assert index_of_clicked_message(svg, svgelement) == 1

    def test_click_bidirectional_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice <-> Bob: Sync\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "line")
        assert svgelement is not None
        assert index_of_clicked_message(svg, svgelement) == 1


class TestGetMessageText:
    def test_normal_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello World\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        assert get_message_text(puml, svg, svgelement) == "Hello World"

    def test_second_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: First\nBob -> Alice: Second\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 1, "polygon")
        assert get_message_text(puml, svg, svgelement) == "Second"

    def test_self_message(self):
        puml = "@startuml\nparticipant Alice\nAlice -> Alice: Think\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        assert get_message_text(puml, svg, svgelement) == "Think"


class TestEditMessageText:
    def test_edit_normal_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        result = edit_message_text(puml, svg, svgelement, "Goodbye")
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Goodbye\n@enduml"
        assert result == expected

    def test_edit_second_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: First\nBob -> Alice: Second\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 1, "polygon")
        result = edit_message_text(puml, svg, svgelement, "Updated")
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: First\nBob -> Alice: Updated\n@enduml"
        assert result == expected

    def test_edit_self_message(self):
        puml = "@startuml\nparticipant Alice\nAlice -> Alice: Think\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        result = edit_message_text(puml, svg, svgelement, "Ponder")
        expected = "@startuml\nparticipant Alice\nAlice -> Alice: Ponder\n@enduml"
        assert result == expected

    def test_edit_dashed_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice --> Bob: Dashed\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        result = edit_message_text(puml, svg, svgelement, "Still dashed")
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice --> Bob: Still dashed\n@enduml"
        assert result == expected


class TestDeleteMessage:
    def test_delete_single_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        result = delete_message(puml, svg, svgelement)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\n@enduml"
        assert result == expected

    def test_delete_first_of_two_messages(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: First\nBob -> Alice: Second\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        result = delete_message(puml, svg, svgelement)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nBob -> Alice: Second\n@enduml"
        assert result == expected

    def test_delete_second_of_two_messages(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: First\nBob -> Alice: Second\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 1, "polygon")
        result = delete_message(puml, svg, svgelement)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: First\n@enduml"
        assert result == expected

    def test_delete_self_message(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Alice: Think\nAlice -> Bob: Done\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        result = delete_message(puml, svg, svgelement)
        expected = (
            "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Done\n@enduml"
        )
        assert result == expected


class TestMessageRoutes:
    """Integration tests for message routes via Flask test client."""

    def test_get_message_text(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello World\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        response = client.post(
            "/getMessageText",
            data=json.dumps({"plantuml": puml, "svg": svg, "svgelement": svgelement}),
            content_type="application/json",
        )
        assert response.get_json()["text"] == "Hello World"

    def test_edit_message_text(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        response = client.post(
            "/editMessageText",
            data=json.dumps(
                {
                    "plantuml": puml,
                    "svg": svg,
                    "svgelement": svgelement,
                    "text": "Goodbye",
                }
            ),
            content_type="application/json",
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Goodbye\n@enduml"
        assert response.get_json()["plantuml"] == expected

    def test_delete_message(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nBob -> Alice: Bye\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        response = client.post(
            "/deleteMessage",
            data=json.dumps({"plantuml": puml, "svg": svg, "svgelement": svgelement}),
            content_type="application/json",
        )
        expected = (
            "@startuml\nparticipant Alice\nparticipant Bob\nBob -> Alice: Bye\n@enduml"
        )
        assert response.get_json()["plantuml"] == expected

    def test_delete_message_click_line(self, client):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "line")
        response = client.post(
            "/deleteMessage",
            data=json.dumps({"plantuml": puml, "svg": svg, "svgelement": svgelement}),
            content_type="application/json",
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\n@enduml"
        assert response.get_json()["plantuml"] == expected
