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

"""Operations on a participant whose displayed name is not its reference name.

Every writer learns participants by their *displayed* name -- it is what the SVG
renders and what the frontend sends back -- but the diagram body has to name the
alias. Building a line from the displayed name of `participant "Space Room" as
SpaceRoom` yields `Space Room -> Bob`, which PlantUML rejects.

Renaming a participant to a name with spaces now generates exactly that kind of
declaration, so these are the operations a user reaches for immediately after.
"""

import re

from flask import json
from plantuml_gui.sequence.classes import is_participant_rect
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq

# One aliased participant whose displayed name contains a space, plus a plain
# one to interact with.
ALIASED_PUML = """@startuml
participant "Space Room" as SpaceRoom
participant Bob
SpaceRoom -> Bob: hi
@enduml"""


def extract_g_element(svg_string):
    match = re.search(r"<g>(.*?)</g>", svg_string, re.DOTALL)
    return f"<g>{match.group(1)}</g>" if match else None


def render(puml):
    return extract_g_element(_create_svg_from_uml(puml))


def participant_cx(svg, index):
    """Center x of the nth unique participant header rect."""
    seen = []
    for rect in Pq(svg)("rect").items():
        if not is_participant_rect(rect):
            continue
        cx = float(rect.attr("x")) + float(rect.attr("width")) / 2
        if cx not in seen:
            seen.append(cx)
    return seen[index]


def participant_rect(svg, index):
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
    return response.get_json()["plantuml"]


class TestAddMessageToAliasedParticipant:
    def test_message_uses_the_alias(self, client):
        svg = render(ALIASED_PUML)
        first = participant_cx(svg, 0)
        second = participant_cx(svg, 1)

        result = post(
            client,
            "/addMessage",
            {
                "plantuml": ALIASED_PUML,
                "svg": svg,
                "message": "second",
                "firstcoordinates": [first, 200],
                "secondcoordinates": [second, 200],
            },
        )

        assert "SpaceRoom -> Bob: second" in result
        assert "Space Room -> Bob" not in result
        assert_renders(result)


class TestAddActivationToAliasedParticipant:
    def test_activation_uses_the_alias(self, client):
        result = post(
            client,
            "/addActivation",
            {
                "plantuml": ALIASED_PUML,
                # The frontend only ever knows the displayed name.
                "participant": "Space Room",
                "startMessageIndex": 3,
                "endMessageIndex": 3,
                "endType": "deactivate",
            },
        )

        assert "activate SpaceRoom" in result
        assert "deactivate SpaceRoom" in result
        assert "activate Space Room" not in result
        assert_renders(result)

    def test_destroy_uses_the_alias(self, client):
        result = post(
            client,
            "/addActivation",
            {
                "plantuml": ALIASED_PUML,
                "participant": "Space Room",
                "startMessageIndex": 3,
                "endMessageIndex": 3,
                "endType": "destroy",
            },
        )

        assert "destroy SpaceRoom" in result
        assert_renders(result)

    def test_activation_bar_can_be_deleted_again(self, client):
        """delete_activation pairs activate/close lines by participant, so it
        has to look for the alias too."""
        activated = post(
            client,
            "/addActivation",
            {
                "plantuml": ALIASED_PUML,
                "participant": "Space Room",
                "startMessageIndex": 3,
                "endMessageIndex": 3,
                "endType": "deactivate",
            },
        )
        svg = render(activated)
        bar = next(
            str(rect)
            for rect in Pq(svg)("rect").items()
            if not is_participant_rect(rect)
        )

        result = post(
            client,
            "/deleteActivation",
            {"plantuml": activated, "svg": svg, "svgelement": bar},
        )

        assert "activate SpaceRoom" not in result
        assert "deactivate SpaceRoom" not in result
        assert_renders(result)


class TestAddNoteToAliasedParticipant:
    def test_note_placement_uses_the_alias(self, client):
        svg = render(ALIASED_PUML)

        result = post(
            client,
            "/addNote",
            {
                "plantuml": ALIASED_PUML,
                "svg": svg,
                "participant": "Space Room",
                "placement": "over",
                "text": "a note",
                "yPosition": 200,
            },
        )

        assert "note over SpaceRoom : a note" in result
        assert "note over Space Room" not in result
        assert_renders(result)

    def test_spanning_note_uses_both_aliases(self, client):
        svg = render(ALIASED_PUML)

        result = post(
            client,
            "/addNote",
            {
                "plantuml": ALIASED_PUML,
                "svg": svg,
                "participant": "Space Room",
                "placement": "spanning",
                "secondParticipant": "Bob",
                "text": "a note",
                "yPosition": 200,
            },
        )

        assert "note over SpaceRoom, Bob : a note" in result
        assert_renders(result)


class TestDeleteAliasedParticipant:
    def test_note_over_the_participant_is_cascaded(self, client):
        puml = """@startuml
participant "Space Room" as SpaceRoom
participant Bob
SpaceRoom -> Bob: hi
note over SpaceRoom: about it
@enduml"""
        svg = render(puml)

        result = post(
            client,
            "/deleteParticipant",
            {
                "plantuml": puml,
                "svg": svg,
                "svgelement": participant_rect(svg, 0),
            },
        )

        assert "SpaceRoom" not in result
        assert "note over" not in result
        assert_renders(result)

    def test_note_over_another_participant_is_kept(self, client):
        puml = """@startuml
participant "Space Room" as SpaceRoom
participant Bob
SpaceRoom -> Bob: hi
note over Bob: about Bob
@enduml"""
        svg = render(puml)

        result = post(
            client,
            "/deleteParticipant",
            {
                "plantuml": puml,
                "svg": svg,
                "svgelement": participant_rect(svg, 0),
            },
        )

        assert "note over Bob: about Bob" in result
        assert_renders(result)
