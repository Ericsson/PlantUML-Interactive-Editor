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

"""Tests for sequence diagram participant routes."""

import re

from flask import json
from plantuml_gui.sequence.classes import is_participant_rect
from plantuml_gui.sequence.participant import _next_participant_number
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq


def extract_g_element(svg_string):
    match = re.search(r"<g>(.*?)</g>", svg_string, re.DOTALL)
    if match:
        return f"<g>{match.group(1)}</g>"
    return None


def extract_participant_rect(svg_string, index=0):
    """Extract the outerHTML of the nth unique participant rect from SVG.

    Filters with `is_participant_rect`, the same way the backend counts clicked
    participants. Without it, an activation bar (a <rect> with no rounded
    corners) can come first in document order and the extracted "participant"
    resolves to whichever lifeline the bar sits on.
    """
    d = Pq(svg_string)
    seen_cx = set()
    count = 0
    for rect in d("rect").items():
        if not is_participant_rect(rect):
            continue
        cx = float(rect.attr("x")) + float(rect.attr("width")) / 2
        if cx not in seen_cx:
            seen_cx.add(cx)
            if count == index:
                return str(rect)
            count += 1
    return None


class TestNextParticipantNumber:
    def test_basic(self):
        puml = "@startuml\nparticipant participant1\n@enduml"
        assert _next_participant_number(puml) == 2

    def test_ignores_participant_name_in_message(self):
        puml = "@startuml\nparticipant participant1\nparticipant1 -> bob: tell participant participant99\n@enduml"
        assert _next_participant_number(puml) == 2

    def test_ignores_participant_name_in_inline_comment(self):
        puml = "@startuml\nparticipant participant1\n/' participant participant99 '/\n@enduml"
        assert _next_participant_number(puml) == 2

    def test_ignores_participant_name_in_note(self):
        puml = "@startuml\nparticipant participant1\nnote over participant1: participant participant99 is fast\n@enduml"
        assert _next_participant_number(puml) == 2


class TestParticipantParsingIgnoresRnote:
    """Regression: an rnote's <rect> shares the exact same
    stroke-width:0.5 style as a participant header rect, but participant
    headers always have rounded corners (rx/ry) and rnote never does.
    Without excluding rnote, Diagram.from_svg would misparse it (and its
    text) as an extra phantom participant.

    Uses short note text deliberately: PlantUML's layout can otherwise
    make the phantom rnote "participant" coincidentally land at the same
    cx as a real participant, silently hiding the bug in the results
    (both collapse into the same dict slot) without actually fixing it.
    """

    def test_rnote_is_not_parsed_as_a_participant(self):
        from plantuml_gui.sequence.classes import Diagram

        puml = "@startuml\nparticipant Alice\nparticipant Bob\nrnote over Alice : x\n@enduml"
        svg = extract_g_element(_create_svg_from_uml(puml))
        diagram = Diagram.from_svg(svg, puml)
        assert [p.name for p in diagram.participants] == ["Alice", "Bob"]

    def test_multiple_rnotes_do_not_add_phantom_participants(self):
        from plantuml_gui.sequence.classes import Diagram

        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\n"
            "rnote over Alice : x\n"
            "rnote over Bob : y\n"
            "@enduml"
        )
        svg = extract_g_element(_create_svg_from_uml(puml))
        diagram = Diagram.from_svg(svg, puml)
        assert [p.name for p in diagram.participants] == ["Alice", "Bob"]


class TestAppRoutesParticipant:
    def test_add_participant_right(self, client):
        test_data = {
            "plantuml": """@startuml
participant bob
@enduml""",
            "direction": "right",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/addParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant bob
participant participant1
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_add_participant_left(self, client):
        test_data = {
            "plantuml": """@startuml
participant bob
@enduml""",
            "direction": "left",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/addParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant participant1
participant bob
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_add_participant_right_with_messages(self, client):
        test_data = {
            "plantuml": """@startuml
participant bob
participant fred

bob -> fred: Hello
fred -> bob: Bye

@enduml""",
            "direction": "right",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/addParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant bob
participant participant1
participant fred

bob -> fred: Hello
fred -> bob: Bye

@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_add_participant_number_after_deletion(self, client):
        """Adding a participant after deleting one should increment past the highest existing number."""
        test_data = {
            "plantuml": """@startuml
participant participant1
participant participant3
@enduml""",
            "direction": "right",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/addParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant participant1
participant participant4
participant participant3
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_add_message(self, client):
        test_data = {
            "plantuml": """@startuml
participant bob
participant fred
@enduml""",
            "svg": """<g><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="25" x2="25" y1="36.2969" y2="56.2969"></line><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="76" x2="76" y1="36.2969" y2="56.2969"></line><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="24.9951">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="55.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="75.292">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="56" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="63" y="24.9951">fred</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="56" y="55.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="63" y="75.292">fred</text></g>""",
            "message": "hello fred",
            "firstcoordinates": [34, 43],
            "secondcoordinates": [71, 39],
        }
        with client:
            response = client.post(
                "/addMessage",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant bob
participant fred
bob -> fred: hello fred
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_add_message_multiline_text_is_escaped(self, client):
        test_data = {
            "plantuml": """@startuml
participant bob
participant fred
@enduml""",
            "svg": """<g><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="25" x2="25" y1="36.2969" y2="56.2969"></line><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="76" x2="76" y1="36.2969" y2="56.2969"></line><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="24.9951">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="55.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="75.292">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="56" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="63" y="24.9951">fred</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="56" y="55.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="63" y="75.292">fred</text></g>""",
            "message": "Line1\nLine2",
            "firstcoordinates": [34, 43],
            "secondcoordinates": [71, 39],
        }
        with client:
            response = client.post(
                "/addMessage",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant bob
participant fred
bob -> fred: Line1\\nLine2
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_edit_participant_name(self, client):
        test_data = {
            "plantuml": """@startuml
participant bob
participant fred
bob -> fred: test
fred -> bob: test2
@enduml""",
            "svg": """<g><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="25" x2="25" y1="36.2969" y2="114.5625"></line><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="82" x2="82" y1="36.2969" y2="114.5625"></line><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="24.9951" style="pointer-events: none;">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="113.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="133.5576" style="pointer-events: none;">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="62" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="69" y="24.9951" style="pointer-events: none;">fred</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="62" y="113.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="69" y="133.5576" style="pointer-events: none;">fred</text><polygon fill="#181818" points="70.5,63.4297,80.5,67.4297,70.5,71.4297,74.5,67.4297" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="25.5" x2="76.5" y1="67.4297" y2="67.4297"></line><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="25" x="32.5" y="62.3638" style="pointer-events: none;">test</text><polygon fill="#181818" points="36.5,92.5625,26.5,96.5625,36.5,100.5625,32.5,96.5625" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="30.5" x2="81.5" y1="96.5625" y2="96.5625"></line><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="33" x="42.5" y="91.4966" style="pointer-events: none;">test2</text></g>""",
            "name": "bobby",
            "svgelement": """<rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="5"></rect>""",
        }
        with client:
            response = client.post(
                "/editParticipantName",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant bobby
participant fred
bobby -> fred: test
fred -> bobby: test2
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_edit_participant_name_selfmessage(self, client):
        test_data = {
            "plantuml": """@startuml
participant bobby
participant fred
bobby -> bobby: hello
@enduml""",
            "name": "bob",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/editParticipantName",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant bob
participant fred
bob -> bob: hello
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_getparticipantnameandrenderbidirectional(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
participant Bob
Bob <--> Alice: Hello
@enduml""",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/getParticipantName",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            assert response.get_json()["name"] == "Alice"

    def test_delete_participant_no_messages(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
participant Bob
@enduml""",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/deleteParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant Bob
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_delete_participant_with_messages(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
participant Bob
Alice -> Bob: Hello
Bob -> Alice: Hi
@enduml""",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/deleteParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant Bob
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_delete_participant_self_message(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
participant Bob
Alice -> Alice: Think
Alice -> Bob: Done
@enduml""",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/deleteParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant Bob
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_delete_participant_cascades_hnote(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
participant Bob
hnote over Alice : hex note
@enduml""",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/deleteParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant Bob
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_delete_participant_cascades_rnote(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
participant Bob
rnote over Alice : rect note
@enduml""",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/deleteParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant Bob
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_delete_participant_keeps_hnote_of_other_participant(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
participant Bob
hnote over Bob : keep me
@enduml""",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/deleteParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant Bob
hnote over Bob : keep me
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_delete_last_participant(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
@enduml""",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/deleteParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_delete_participant_with_note_over(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
participant Bob
Alice -> Bob: Hello
note over Alice : think
@enduml""",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/deleteParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant Bob
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_delete_participant_with_note_left(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
participant Bob
Alice -> Bob: Hello
note left of Alice : think
@enduml""",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/deleteParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant Bob
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml

    def test_delete_participant_keeps_unrelated_note(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
participant Bob
Alice -> Bob: Hello
note over Bob : think
@enduml""",
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        test_data["svgelement"] = extract_participant_rect(test_data["svg"], 0)
        with client:
            response = client.post(
                "/deleteParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant Bob
note over Bob : think
@enduml"""
            assert response.get_json()["plantuml"] == expected_puml


class TestAddMessageYBasedInsertion:
    """Tests for y-based message insertion positioning."""

    def test_insert_between_messages(self, client):
        """New message inserted between two existing messages based on y."""
        puml = """@startuml
participant Alice
participant Bob
Alice -> Bob: Hello
Bob -> Alice: Bye
@enduml"""
        test_data = {
            "plantuml": puml,
            "message": "Middle",
            # y=80 is between Hello (cy=67.4) and Bye (cy=96.5)
            "firstcoordinates": [28, 80],
            "secondcoordinates": [84, 80],
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        with client:
            response = client.post(
                "/addMessage",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected = """@startuml
participant Alice
participant Bob
Alice -> Bob: Hello
Alice -> Bob: Middle
Bob -> Alice: Bye
@enduml"""
            assert response.get_json()["plantuml"] == expected

    def test_insert_before_all_messages(self, client):
        """New message inserted before all existing messages when y is above them."""
        puml = """@startuml
participant Alice
participant Bob
Alice -> Bob: Hello
Bob -> Alice: Bye
@enduml"""
        test_data = {
            "plantuml": puml,
            "message": "First",
            # y=50 is above Hello (cy=67.4)
            "firstcoordinates": [28, 50],
            "secondcoordinates": [84, 50],
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        with client:
            response = client.post(
                "/addMessage",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected = """@startuml
participant Alice
participant Bob
Alice -> Bob: First
Alice -> Bob: Hello
Bob -> Alice: Bye
@enduml"""
            assert response.get_json()["plantuml"] == expected

    def test_insert_after_all_messages(self, client):
        """New message inserted after all existing messages when y is below them."""
        puml = """@startuml
participant Alice
participant Bob
Alice -> Bob: Hello
Bob -> Alice: Bye
@enduml"""
        test_data = {
            "plantuml": puml,
            "message": "Last",
            # y=110 is below Bye (cy=96.5)
            "firstcoordinates": [28, 110],
            "secondcoordinates": [84, 110],
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        with client:
            response = client.post(
                "/addMessage",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected = """@startuml
participant Alice
participant Bob
Alice -> Bob: Hello
Bob -> Alice: Bye
Alice -> Bob: Last
@enduml"""
            assert response.get_json()["plantuml"] == expected

    def test_insert_no_existing_messages(self, client):
        """New message inserted before @enduml when no messages exist."""
        puml = """@startuml
participant Alice
participant Bob
@enduml"""
        test_data = {
            "plantuml": puml,
            "message": "Hi",
            "firstcoordinates": [28, 50],
            "secondcoordinates": [84, 50],
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        with client:
            response = client.post(
                "/addMessage",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected = """@startuml
participant Alice
participant Bob
Alice -> Bob: Hi
@enduml"""
            assert response.get_json()["plantuml"] == expected

    def test_insert_self_message(self, client):
        """New self-message (same sender and receiver) inserted correctly."""
        puml = """@startuml
participant Alice
participant Bob
@enduml"""
        test_data = {
            "plantuml": puml,
            "message": "think",
            "firstcoordinates": [28, 50],
            "secondcoordinates": [28, 50],
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        with client:
            response = client.post(
                "/addMessage",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected = """@startuml
participant Alice
participant Bob
Alice -> Alice: think
@enduml"""
            assert response.get_json()["plantuml"] == expected


class TestGetParticipantPositions:
    PUML = """@startuml
participant Alice
participant Bob
Alice -> Bob: Hello
@enduml"""

    def test_positions_include_line_index(self):
        from plantuml_gui.sequence.participant import get_participant_positions

        svg = extract_g_element(_create_svg_from_uml(self.PUML))
        positions = get_participant_positions(self.PUML, svg)
        assert [p["name"] for p in positions] == ["Alice", "Bob"]
        assert [p["index"] for p in positions] == [1, 2]

    def test_implicit_participant_has_negative_index(self):
        from plantuml_gui.sequence.participant import get_participant_positions

        puml = """@startuml
Alice -> Bob: Hello
@enduml"""
        svg = extract_g_element(_create_svg_from_uml(puml))
        positions = get_participant_positions(puml, svg)
        assert len(positions) == 2
        assert all(p["index"] == -1 for p in positions)

    def test_route_returns_index(self, client):
        svg = extract_g_element(_create_svg_from_uml(self.PUML))
        with client:
            response = client.post(
                "/getSequencePositions",
                data=json.dumps({"plantuml": self.PUML, "svg": svg}),
                content_type="application/json",
            )
            assert response.status_code == 200
            positions = response.get_json()["participants"]
            assert [p["index"] for p in positions] == [1, 2]


class TestRenameParticipant:
    """The three renaming cases of /editParticipantName.

    Which lines a rename touches depends on whether the declaration carries an
    alias, because the alias -- not the displayed name -- is what the diagram
    body refers to. A displayed name with spaces is only legal behind an alias,
    so the editor generates one when it has to.
    """

    @staticmethod
    def rename(client, puml, new_name, participant_index=0):
        """Rename the participant whose header rect is at `participant_index`."""
        svg = extract_g_element(_create_svg_from_uml(puml))
        response = client.post(
            "/editParticipantName",
            data=json.dumps(
                {
                    "plantuml": puml,
                    "svg": svg,
                    "name": new_name,
                    "svgelement": extract_participant_rect(svg, participant_index),
                }
            ),
            content_type="application/json",
        )
        return response.get_json()["plantuml"]

    @staticmethod
    def assert_renders(puml, expected_label):
        """PlantUML accepts the result and draws the new label.

        Guards the whole point of the feature: an unquoted name with spaces
        renders PlantUML's error image instead of a diagram.
        """
        svg = _create_svg_from_uml(puml)
        assert "error" not in svg.lower()
        assert expected_label in svg

    # --- Case 1: the participant already has an alias ---

    def test_aliased_participant_changes_only_the_label(self, client):
        puml = """@startuml
participant "Old Name" as ON
participant Bob
ON -> Bob: hi
activate Bob
note over ON: about ON
@enduml"""

        result = self.rename(client, puml, "New Name")

        assert (
            result
            == """@startuml
participant "New Name" as ON
participant Bob
ON -> Bob: hi
activate Bob
note over ON: about ON
@enduml"""
        )
        self.assert_renders(result, "New Name")

    def test_aliased_participant_keeps_quotes_for_a_single_word(self, client):
        puml = """@startuml
participant "Old Name" as ON
participant Bob
ON -> Bob: hi
@enduml"""

        result = self.rename(client, puml, "Bob2")

        assert 'participant "Bob2" as ON' in result

    def test_aliased_participant_keeps_modifiers(self, client):
        puml = """@startuml
participant "Old Name" as ON order 10 #red
participant Bob
ON -> Bob: hi
@enduml"""

        # `order 10` places this participant to the right of Bob, so its header
        # rect is the second one in the rendered diagram.
        result = self.rename(client, puml, "New Name", participant_index=1)

        assert 'participant "New Name" as ON order 10 #red' in result

    # --- Case 2: no alias, new name without spaces ---

    def test_declaration_and_references_move_together(self, client):
        puml = """@startuml
participant Alice
participant Bob
Alice -> Bob: hi
activate Alice
note over Alice: text
deactivate Alice
@enduml"""

        result = self.rename(client, puml, "Carol")

        assert (
            result
            == """@startuml
participant Carol
participant Bob
Carol -> Bob: hi
activate Carol
note over Carol: text
deactivate Carol
@enduml"""
        )
        self.assert_renders(result, "Carol")

    def test_message_text_mentioning_the_old_name_is_preserved(self, client):
        """The old blanket replace rewrote prose as well as references."""
        puml = """@startuml
participant Alice
participant Bob
Alice -> Bob: ask Alice first
@enduml"""

        result = self.rename(client, puml, "Carol")

        assert "Carol -> Bob: ask Alice first" in result

    # --- Case 3: no alias, new name with spaces ---

    def test_name_with_spaces_gains_a_generated_alias(self, client):
        puml = """@startuml
participant Alice
participant Bob
Alice -> Bob: hi
Bob -> Alice: reply
@enduml"""

        result = self.rename(client, puml, "Space Room")

        assert (
            result
            == """@startuml
participant "Space Room" as SpaceRoom
participant Bob
SpaceRoom -> Bob: hi
Bob -> SpaceRoom: reply
@enduml"""
        )
        self.assert_renders(result, "Space Room")

    def test_generated_alias_avoids_an_existing_identifier(self, client):
        puml = """@startuml
participant Alice
participant SpaceRoom
Alice -> SpaceRoom: hi
@enduml"""

        result = self.rename(client, puml, "Space Room")

        assert 'participant "Space Room" as SpaceRoom2' in result
        assert "SpaceRoom2 -> SpaceRoom: hi" in result
        self.assert_renders(result, "Space Room")

    def test_name_with_spaces_keeps_modifiers(self, client):
        puml = """@startuml
participant Alice order 10
participant Bob
Alice -> Bob: hi
@enduml"""

        # `order 10` puts Alice to the right of Bob, hence the second rect.
        result = self.rename(client, puml, "Space Room", participant_index=1)

        assert 'participant "Space Room" as SpaceRoom order 10' in result
        assert "SpaceRoom -> Bob: hi" in result

    def test_quoted_name_without_alias_is_upgraded(self, client):
        """A quoted declaration with no alias is referred to in quotes, so both
        the declaration and the quoted references have to change."""
        puml = """@startuml
participant "Old Name"
participant Bob
"Old Name" -> Bob: hi
note over "Old Name": text
@enduml"""

        result = self.rename(client, puml, "New Name")

        assert (
            result
            == """@startuml
participant "New Name" as NewName
participant Bob
NewName -> Bob: hi
note over NewName: text
@enduml"""
        )
        self.assert_renders(result, "New Name")

    def test_a_shared_display_name_does_not_rename_the_actor(self, client):
        """Two lifelines may share a displayed name when their identifiers
        differ. The clickable one is the `participant`; renaming it must not
        rewrite the `actor` line that happens to carry the same label."""
        puml = """@startuml
actor "Alice" as A
participant Alice
A -> Alice: hi
@enduml"""

        result = self.rename(client, puml, "Space Room")

        assert (
            result
            == """@startuml
actor "Alice" as A
participant "Space Room" as SpaceRoom
A -> SpaceRoom: hi
@enduml"""
        )
        self.assert_renders(result, "Space Room")

    # --- Case 3 with no declaration to rewrite ---

    def test_implicit_participant_gets_a_declaration(self, client):
        """A participant introduced by a message has no declaration line, but a
        displayed name with spaces has nowhere else to live."""
        puml = """@startuml
Alice -> Bob: hi
Bob -> Alice: reply
@enduml"""

        result = self.rename(client, puml, "Space Room")

        assert (
            result
            == """@startuml
participant "Space Room" as SpaceRoom
SpaceRoom -> Bob: hi
Bob -> SpaceRoom: reply
@enduml"""
        )
        self.assert_renders(result, "Space Room")

    def test_implicit_participant_without_spaces_needs_no_declaration(self, client):
        puml = """@startuml
Alice -> Bob: hi
@enduml"""

        result = self.rename(client, puml, "Carol")

        assert (
            result
            == """@startuml
Carol -> Bob: hi
@enduml"""
        )

    def test_declaration_is_inserted_at_first_use_preserving_order(self, client):
        """Inserting at the first reference keeps PlantUML's lifeline order."""
        puml = """@startuml
participant Bob
Bob -> Alice: hi
@enduml"""

        result = self.rename(client, puml, "Space Room", participant_index=1)

        assert (
            result
            == """@startuml
participant Bob
participant "Space Room" as SpaceRoom
Bob -> SpaceRoom: hi
@enduml"""
        )
        self.assert_renders(result, "Space Room")

    # --- Input handling ---

    def test_name_is_escaped(self, client):
        """The name comes straight from a request and ends up as SVG text."""
        puml = """@startuml
participant Alice
participant Bob
Alice -> Bob: hi
@enduml"""

        result = self.rename(client, puml, "<script>")

        assert "<script>" not in result
        assert "&lt;script&gt;" in result

    def test_newline_in_the_name_becomes_a_line_break_escape(self, client):
        """A declaration is one line, so a real newline in the incoming name is
        folded into the literal \\n escape PlantUML draws as a line break. The
        name then needs a quoted declaration and an alias like any other."""
        puml = """@startuml
participant Alice
participant Bob
Alice -> Bob: hi
@enduml"""

        result = self.rename(client, puml, "New\nName")

        assert (
            result
            == """@startuml
participant "New\\nName" as NewnName
participant Bob
NewnName -> Bob: hi
@enduml"""
        )
        # PlantUML draws each line of the name as its own <text>, so check the
        # two lines separately rather than the joined form.
        self.assert_renders(result, "New")
        self.assert_renders(result, "Name")

    def test_surrounding_whitespace_is_trimmed(self, client):
        puml = """@startuml
participant Alice
participant Bob
Alice -> Bob: hi
@enduml"""

        result = self.rename(client, puml, "  Carol  ")

        assert "participant Carol" in result
        assert "Carol -> Bob: hi" in result

    def test_blank_name_leaves_the_diagram_untouched(self, client):
        """Renaming to nothing would otherwise label the participant "" ."""
        puml = """@startuml
participant Alice
participant Bob
Alice -> Bob: hi
@enduml"""

        assert self.rename(client, puml, "   \n  ") == puml
