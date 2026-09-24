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

"""Participants whose displayed name contains a line break.

PlantUML draws `participant "a\\nb" as ab` as one <text> element per line, so
reading only the header rect's immediate next sibling saw just `a`. That name
matched no declaration, leaving the participant with line index -1: rename and
delete became silent no-ops, "add participant" inserted at the end of the file,
and editor hover highlighting pointed at nothing.

Only a quoted declaration can hold a line break -- PlantUML rejects `participant
a\\nb` outright -- so these cases all involve an aliased or quoted name.
"""

import re

from flask import json
from plantuml_gui.sequence.classes import (
    Diagram,
    display_names_match,
    is_participant_rect,
    normalized_display_name,
    reference_name_for,
)
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq

# The reported diagram: a two-line displayed name, an alias, and a message.
MULTILINE_PUML = """@startuml
participant "a\\nb" as ab
participant ac
ab -> ac: m
@enduml"""


def extract_g_element(svg_string):
    match = re.search(r"<g>(.*?)</g>", svg_string, re.DOTALL)
    return f"<g>{match.group(1)}</g>" if match else None


def render(puml):
    return extract_g_element(_create_svg_from_uml(puml))


def participant_rect(svg, index):
    """The nth unique participant header rect, as the frontend would send it."""
    seen = []
    for rect in Pq(svg)("rect").items():
        if not is_participant_rect(rect):
            continue
        cx = float(rect.attr("x")) + float(rect.attr("width")) / 2
        if cx not in seen:
            seen.append(cx)
            if len(seen) - 1 == index:
                return str(rect)
    return None


def assert_renders(puml):
    """PlantUML accepts the result rather than drawing its error image."""
    assert "error" not in _create_svg_from_uml(puml).lower()


def post(client, route, payload):
    response = client.post(
        route, data=json.dumps(payload), content_type="application/json"
    )
    return response.get_json()


def edit_payload(puml, extra=None):
    svg = render(puml)
    payload = {
        "plantuml": puml,
        "svg": svg,
        "svgelement": participant_rect(svg, 0),
    }
    payload.update(extra or {})
    return payload


class TestParsing:
    def test_both_lines_form_the_name(self):
        diagram = Diagram.from_svg(render(MULTILINE_PUML), MULTILINE_PUML)

        assert [p.name for p in diagram.participants] == ["a\\nb", "ac"]

    def test_declaration_line_is_found(self):
        """The regression: the name matched no declaration, so index stayed -1."""
        diagram = Diagram.from_svg(render(MULTILINE_PUML), MULTILINE_PUML)

        assert diagram.participants[0].index == 1
        assert diagram.participants[1].index == 2

    def test_alias_is_attached(self):
        diagram = Diagram.from_svg(render(MULTILINE_PUML), MULTILINE_PUML)

        assert diagram.participants[0].alias == "ab"
        assert diagram.participants[0].reference_name == "ab"

    def test_message_endpoints_resolve(self):
        diagram = Diagram.from_svg(render(MULTILINE_PUML), MULTILINE_PUML)

        (message,) = diagram.messages
        assert message.from_participant.name == "a\\nb"
        assert message.to_participant.name == "ac"

    def test_reference_name_for_resolves_the_alias(self):
        assert reference_name_for(MULTILINE_PUML, "a\\nb") == "ab"

    def test_backslash_l_declaration_is_matched(self):
        r"""\l breaks the label exactly like \n, differing only in alignment, and
        the SVG records only that the break happened."""
        puml = (
            '@startuml\nparticipant "a\\lb" as ab\nparticipant ac\nab -> ac: m\n@enduml'
        )

        diagram = Diagram.from_svg(render(puml), puml)

        assert diagram.participants[0].index == 1
        assert diagram.participants[0].alias == "ab"

    def test_empty_line_in_the_name_is_matched(self):
        """PlantUML draws a source-empty line as a single space, so the name read
        back from the SVG is not character-identical to the declaration."""
        puml = '@startuml\nparticipant "a\\n\\nb" as ab\nparticipant ac\nab -> ac: m\n@enduml'

        diagram = Diagram.from_svg(render(puml), puml)

        assert diagram.participants[0].index == 1
        assert diagram.participants[0].alias == "ab"


class TestNormalization:
    def test_line_break_escapes_are_interchangeable(self):
        assert display_names_match("a\\nb", "a\\lb")
        assert display_names_match("a\\rb", "a\\nb")

    def test_surrounding_whitespace_per_line_is_ignored(self):
        assert display_names_match("a\\n \\nb", "a\\n\\nb")

    def test_distinct_names_still_differ(self):
        assert not display_names_match("a\\nb", "a\\nc")
        assert not display_names_match("ab", "a\\nb")

    def test_single_line_name_is_unchanged(self):
        assert normalized_display_name("Alice") == "Alice"


class TestRoutes:
    def test_get_name_returns_both_lines(self, client):
        data = post(client, "/getParticipantName", edit_payload(MULTILINE_PUML))

        assert data["name"] == "a\\nb"

    def test_rename_keeps_the_alias_and_rewrites_nothing_else(self, client):
        data = post(
            client,
            "/editParticipantName",
            edit_payload(MULTILINE_PUML, {"name": "zz"}),
        )

        assert data["plantuml"] == (
            '@startuml\nparticipant "zz" as ab\nparticipant ac\nab -> ac: m\n@enduml'
        )
        assert_renders(data["plantuml"])

    def test_delete_removes_the_declaration_and_cascades(self, client):
        puml = (
            "@startuml\n"
            'participant "a\\nb" as ab\n'
            "participant ac\n"
            "ab -> ac: m\n"
            "note over ab: hi\n"
            "@enduml"
        )

        data = post(client, "/deleteParticipant", edit_payload(puml))

        assert data["plantuml"] == "@startuml\nparticipant ac\n@enduml"
        assert_renders(data["plantuml"])

    def test_add_left_inserts_before_the_declaration(self, client):
        data = post(
            client,
            "/addParticipant",
            edit_payload(MULTILINE_PUML, {"direction": "left"}),
        )

        assert data["plantuml"].splitlines()[1] == "participant participant1"
        assert_renders(data["plantuml"])

    def test_add_right_inserts_after_the_declaration(self, client):
        data = post(
            client,
            "/addParticipant",
            edit_payload(MULTILINE_PUML, {"direction": "right"}),
        )

        assert data["plantuml"].splitlines()[2] == "participant participant1"
        assert_renders(data["plantuml"])

    def test_lifeline_position_reports_the_declaration_line(self, client):
        puml = MULTILINE_PUML
        data = post(
            client,
            "/getSequencePositions",
            {"plantuml": puml, "svg": render(puml)},
        )

        multiline = data["participants"][0]
        assert multiline["name"] == "a\\nb"
        assert multiline["index"] == 1


class TestRenameToAMultilineName:
    """The mirror case: a line break cannot live in a bare reference token, so
    the new name has to be quoted and the body pointed at a generated alias."""

    def test_plain_participant_gains_an_alias(self, client):
        puml = "@startuml\nparticipant ac\nparticipant zz\nac -> zz: m\n@enduml"

        data = post(
            client,
            "/editParticipantName",
            edit_payload(puml, {"name": "x\\ny"}),
        )

        assert data["plantuml"] == (
            '@startuml\nparticipant "x\\ny" as Xny\nparticipant zz\nXny -> zz: m\n@enduml'
        )
        assert_renders(data["plantuml"])
