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
    _apply_arrow_color,
    _arrow_color_from_line,
    _message_text_from_line,
    _unwrap_text_color,
    _wrap_text_color,
    add_message,
    delete_message,
    edit_message_text,
    get_message_color,
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

    def test_message_unescapes_newlines(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Line1\\nLine2\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        assert get_message_text(puml, svg, svgelement) == "Line1\nLine2"


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

    def test_edit_message_multiline_text_is_escaped(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        svgelement = extract_message_element(svg, 0, "polygon")
        result = edit_message_text(puml, svg, svgelement, "Line1\nLine2")
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Line1\\nLine2\n@enduml"
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

    def test_edit_message_multiline_text(self, client):
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
                    "text": "Line1\nLine2",
                }
            ),
            content_type="application/json",
        )
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Line1\\nLine2\n@enduml"
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


class TestArrowColorHelpers:
    """Pure-string tests for arrow-color parsing and rewriting."""

    def test_apply_color_solid_arrow(self):
        assert _apply_arrow_color("->", "red") == "-[#red]>"

    def test_apply_color_dashed_arrow(self):
        assert _apply_arrow_color("-->", "LightBlue") == "-[#LightBlue]->"

    def test_apply_color_reverse_arrow(self):
        assert _apply_arrow_color("<-", "red") == "<-[#red]"

    def test_apply_color_bidirectional_arrow(self):
        assert _apply_arrow_color("<->", "red") == "<-[#red]>"

    def test_apply_color_lost_message_arrow(self):
        # ->x keeps its trailing head; color goes after the first dash.
        assert _apply_arrow_color("->x", "red") == "-[#red]>x"

    def test_apply_color_replaces_existing(self):
        assert _apply_arrow_color("-[#blue]>", "red") == "-[#red]>"

    def test_apply_empty_color_removes(self):
        assert _apply_arrow_color("-[#blue]>", "") == "->"

    def test_read_color_present(self):
        assert _arrow_color_from_line("Alice -[#red]> Bob: hi") == "red"

    def test_read_color_absent(self):
        assert _arrow_color_from_line("Alice -> Bob: hi") == ""

    def test_read_color_ignores_hyphen_in_name(self):
        # A dash inside a participant name must not be read as the arrow.
        assert _arrow_color_from_line("Web-Server -[#Orange]> DB: q") == "Orange"


class TestMessageColorRoundTrip:
    """Render-based tests that color survives read/edit through the SVG."""

    def _first_polygon(self, puml):
        svg = extract_g_inner(_create_svg_from_uml(puml))
        return svg, extract_message_element(svg, 0, "polygon")

    def test_get_color_uncolored(self):
        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hi\n@enduml"
        )
        svg, svgelement = self._first_polygon(puml)
        assert get_message_color(puml, svg, svgelement) == ""

    def test_get_color_colored(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -[#LightBlue]> Bob: Hi\n@enduml"
        svg, svgelement = self._first_polygon(puml)
        assert get_message_color(puml, svg, svgelement) == "LightBlue"

    def test_edit_adds_color(self):
        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hi\n@enduml"
        )
        svg, svgelement = self._first_polygon(puml)
        result = edit_message_text(puml, svg, svgelement, "Hi", "LightGreen")
        assert "Alice -[#LightGreen]> Bob: <color:LightGreen>Hi</color>" in result

    def test_edit_removes_color_with_none(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -[#LightBlue]> Bob: Hi\n@enduml"
        svg, svgelement = self._first_polygon(puml)
        result = edit_message_text(puml, svg, svgelement, "Hi", "none")
        assert "Alice -> Bob: Hi" in result

    def test_edit_removes_text_color_with_none(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -[#LightBlue]> Bob: <color:LightBlue>Hi</color>\n@enduml"
        svg, svgelement = self._first_polygon(puml)
        result = edit_message_text(puml, svg, svgelement, "Hi", "none")
        assert "Alice -> Bob: Hi\n" in result

    def test_edit_none_color_param_keeps_existing(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -[#LightBlue]> Bob: Hi\n@enduml"
        svg, svgelement = self._first_polygon(puml)
        result = edit_message_text(puml, svg, svgelement, "Bye")
        assert "Alice -[#LightBlue]> Bob: <color:LightBlue>Bye</color>" in result

    def test_get_text_strips_color_wrapper(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -[#Red]> Bob: <color:Red>a</color>\\n<color:Red>b</color>\n@enduml"
        svg, svgelement = self._first_polygon(puml)
        assert get_message_text(puml, svg, svgelement) == "a\nb"

    def test_colored_text_renders_in_color(self):
        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hi\n@enduml"
        )
        svg, svgelement = self._first_polygon(puml)
        result = edit_message_text(puml, svg, svgelement, "a\nb", "Red")
        texts = Pq(extract_g_inner(_create_svg_from_uml(result)))(
            'text[font-size="13"]'
        )
        assert [t.attrib["fill"] for t in texts] == ["#FF0000", "#FF0000"]


class TestMessageTextColorHelpers:
    """Pure-string tests for wrapping message text in <color> tags."""

    def test_wrap_single_line(self):
        assert _wrap_text_color("hi", "Red") == "<color:Red>hi</color>"

    def test_wrap_each_line_of_multiline(self):
        assert (
            _wrap_text_color("a\\nb", "Red")
            == "<color:Red>a</color>\\n<color:Red>b</color>"
        )

    def test_wrap_no_color_is_noop(self):
        assert _wrap_text_color("hi", "") == "hi"

    def test_unwrap_round_trip(self):
        assert _unwrap_text_color(_wrap_text_color("a\\nb", "Red"), "Red") == "a\\nb"

    def test_unwrap_does_not_span_separate_tags(self):
        text = "<color:Red>a</color> and <color:Red>b</color>"
        assert _unwrap_text_color(text, "Red") == "a and b"

    def test_unwrap_keeps_other_color_markup(self):
        assert _unwrap_text_color("<color:Blue>hi</color>", "Red") == (
            "<color:Blue>hi</color>"
        )

    def test_unwrap_without_arrow_color_keeps_markup(self):
        assert _message_text_from_line("A -> B: <color:Red>hi</color>") == (
            "<color:Red>hi</color>"
        )


class TestAddMessageColor:
    """add_message colors the whole message (arrow and text)."""

    PUML = "@startuml\nparticipant Alice\nparticipant Bob\n@enduml"

    def _add(self, color, arrow="->", text="Hi"):
        svg = extract_g_inner(_create_svg_from_uml(self.PUML))
        xs = [int(float(x)) for x in re.findall(r'<line[^>]*x1="([\d.]+)"', svg)][:2]
        return add_message(self.PUML, svg, text, [xs[0], 40], [xs[1], 40], arrow, color)

    def test_add_with_color(self):
        assert "Alice -[#Red]> Bob: <color:Red>Hi</color>" in self._add("Red")

    def test_add_dashed_with_color(self):
        assert "Alice -[#Red]-> Bob: <color:Red>Hi</color>" in self._add("Red", "-->")

    def test_add_with_none_color(self):
        assert "Alice -> Bob: Hi" in self._add("none")

    def test_add_without_color(self):
        assert "Alice -> Bob: Hi" in self._add(None)

    def test_add_route_passes_color(self, client):
        svg = extract_g_inner(_create_svg_from_uml(self.PUML))
        xs = [int(float(x)) for x in re.findall(r'<line[^>]*x1="([\d.]+)"', svg)][:2]
        response = client.post(
            "/addMessage",
            data=json.dumps(
                {
                    "plantuml": self.PUML,
                    "svg": svg,
                    "message": "Hi",
                    "firstcoordinates": [xs[0], 40],
                    "secondcoordinates": [xs[1], 40],
                    "color": "LightBlue",
                }
            ),
            content_type="application/json",
        )
        assert (
            "Alice -[#LightBlue]> Bob: <color:LightBlue>Hi</color>"
            in response.get_json()["plantuml"]
        )
