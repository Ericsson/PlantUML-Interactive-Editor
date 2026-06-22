# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2024 Ericsson
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
from plantuml_gui.sequence.participant import _next_participant_number
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq


def extract_g_element(svg_string):
    match = re.search(r"<g>(.*?)</g>", svg_string, re.DOTALL)
    if match:
        return f"<g>{match.group(1)}</g>"
    return None


def extract_participant_rect(svg_string, index=0):
    """Extract the outerHTML of the nth unique participant rect from SVG."""
    d = Pq(svg_string)
    seen_cx = set()
    count = 0
    for rect in d("rect").items():
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

    def test_checkifinsideparticipant(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
@enduml""",
            "coordinates": [28, 40],
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        with client:
            response = client.post(
                "/checkIfInsideParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = response.get_json()
            assert response_json["isValid"]

    def test_checkifinsideparticipantfalse(self, client):
        test_data = {
            "plantuml": """@startuml
participant Alice
@enduml""",
            "coordinates": [100, 40],
        }
        test_data["svg"] = extract_g_element(
            _create_svg_from_uml(test_data["plantuml"])
        )
        with client:
            response = client.post(
                "/checkIfInsideParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = response.get_json()
            assert not response_json["isValid"]

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
