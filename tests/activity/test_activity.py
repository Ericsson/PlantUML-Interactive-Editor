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

"""Tests for activity box creation, editing, deletion, and color routes."""

from flask import json
from plantuml_gui.activity.activity import activity_indices


class TestAppRoutesActivity:
    def test_break_colored_activity_with_colored_connector(self, client):
        test_data = {
            "plantuml": """@startuml
start
#green:(A)
#red:Activity;
:Activity;
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="42.5" cy="60" fill="#008000" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,56.1719 L41,60.5156 L44.2188,60.5156 L42.6094,56.1719 Z M41.9375,55 L43.2813,55 L46.6094,63.75 L45.375,63.75 L44.5781,61.5 L40.6406,61.5 L39.8438,63.75 L38.5938,63.75 L41.9375,55 Z " fill="#000000" style="pointer-events: none;"></path><rect fill="#FF0000" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="90"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="111.1387" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="143.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="165.1074" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="70" y2="90"></line><polygon fill="#181818" points="38.5,80,42.5,90,46.5,80,42.5,84" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="123.9688" y2="143.9688"></line><polygon fill="#181818" points="38.5,133.9688,42.5,143.9688,46.5,133.9688,42.5,137.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#FF0000" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="90"></rect>""",
        }
        with client:
            response = client.post(
                "/breakActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
#green:(A)
#red:Activity;
break
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addarrow3(self, client):
        test_data = {
            "plantuml": """@startuml
start
-> Arrow label 1;
:Activity;
:Activity;
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="71.3989"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="92.5376" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="125.3677"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="146.5063" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="71.3989"></line><polygon fill="#181818" points="38.5,61.3989,42.5,71.3989,46.5,61.3989,42.5,65.3989" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="75" x="46.5" y="51.3047">Arrow label 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="105.3677" y2="125.3677"></line><polygon fill="#181818" points="38.5,115.3677,42.5,125.3677,46.5,115.3677,42.5,119.3677" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="125.3677"></rect>""",
            "where": "below",
        }
        with client:
            response = client.post(
                "/addArrowLabel",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
-> Arrow label 1;
:Activity;
:Activity;
-> Arrow label 2;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addarrow2(self, client):
        test_data = {
            "plantuml": """@startuml
start
  :Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect>""",
            "where": "below",
        }
        with client:
            response = client.post(
                "/addArrowLabel",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
  :Activity;
-> Arrow label 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addarrow(self, client):
        test_data = {
            "plantuml": """@startuml
start
  :Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect>""",
            "where": "above",
        }
        with client:
            response = client.post(
                "/addArrowLabel",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
-> Arrow label 1;
  :Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_break3(self, client):
        test_data = {
            "plantuml": """@startuml
  :Activity;
break
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/breakActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
  :Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_detach2(self, client):
        test_data = {
            "plantuml": """@startuml
  :Activity;
break
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/detachActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
  :Activity;
detach
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_break2(self, client):
        test_data = {
            "plantuml": """@startuml
  :Activity;
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/breakActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
  :Activity;
break
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_break(self, client):
        test_data = {
            "plantuml": """@startuml
  :Activity;
note right
note
end note
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/breakActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
  :Activity;
note right
note
end note
break
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_checkbackward(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
repeat
  :Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="31.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="108.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="129.9375" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,64.9688,63.5,76.9688,51.5,88.9688,39.5,76.9688,51.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,172.9375,71,172.9375,83,184.9375,71,196.9375,32,196.9375,20,184.9375,32,172.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="206.9922" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="188.5898" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="182.1875" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="107" y="108.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="117" y="129.9375" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="228.4922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="249.4609" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="88.9688" y2="108.9688"></line><polygon fill="#181818" points="47.5,98.9688,51.5,108.9688,55.5,98.9688,51.5,102.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="138.5" y1="184.9375" y2="184.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="138.5" y1="142.9375" y2="184.9375"></line><polygon fill="#181818" points="134.5,152.9375,138.5,142.9375,142.5,152.9375,138.5,148.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="138.5" y1="76.9688" y2="108.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="63.5" y1="76.9688" y2="76.9688"></line><polygon fill="#181818" points="73.5,72.9688,63.5,76.9688,73.5,80.9688,69.5,76.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="142.9375" y2="172.9375"></line><polygon fill="#181818" points="47.5,162.9375,51.5,172.9375,55.5,162.9375,51.5,166.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="47.5,54.9688,51.5,64.9688,55.5,54.9688,51.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="196.9375" y2="228.4922"></line><polygon fill="#181818" points="47.5,218.4922,51.5,228.4922,55.5,218.4922,51.5,222.4922" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="107" y="108.9688"></rect>""",
        }
        with client:
            response = client.post(
                "/checkBackward",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """backward:Activity;"""
            assert response.data.decode("utf-8") == expected_puml

    def test_activity_indexes(self):
        output = [3, 5, 7, 6, 10, 9, 12]
        lines = """@startuml
start
repeat
:Activity;
repeat
#blue:Activity;
backward:Activity2;
:Activity;
repeat while (while ?) is (yes) not (no)
backward:Activity2;
:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""".splitlines()
        assert activity_indices(lines, 0) == output

    def test_editcoloredactivity(self, client):
        test_data = {
            "plantuml": """@startuml
#lightblue:PPSI = 1, PPEI = 0;
@enduml""",
            "svg": """<rect fill="#ADD8E6" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="134" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="114" x="21" y="31.9688" style="pointer-events: none;">PPSI = 1, PPEI = 0</text>""",
            "newname": "Hej",
            "oldname": "PPSI = 1, PPEI = 0",
            "svgelement": """<rect fill="#ADD8E6" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="134" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/editText",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
#lightblue:Hej;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_toggledetach2(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
note right
note
end note
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/detachActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
note right
note
end note
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addnote2(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/addNoteActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
note right
note
end note
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addswitchtoactivity(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
            "type": "switch",
        }
        with client:
            response = client.post(
                "/addToActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
switch (test?)
case ( condition 1)
:Activity;
case ( condition 2)
:Activity;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addtoactivity(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
            "type": "repeat",
        }
        with client:
            response = client.post(
                "/addToActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
repeat
:Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addactivitytoactivity(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
:Activity 2;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addnote(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
note right
note
end note
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/addNoteActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
note right
note
end note
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_toggledetach(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
note right
note
end note
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/detachActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
note right
note
end note
detach
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_text_empty(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
:Activity 2;
:Activity 3;
:Activity 4;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688">Activity 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="85.9375">Activity 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="139.9063">Activity 3</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="172.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="193.875">Activity 4</text><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="44.5,54.9688,48.5,64.9688,52.5,54.9688,48.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="98.9375" y2="118.9375"></line><polygon fill="#181818" points="44.5,108.9375,48.5,118.9375,52.5,108.9375,48.5,112.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="152.9063" y2="172.9063"></line><polygon fill="#181818" points="44.5,162.9063,48.5,172.9063,52.5,162.9063,48.5,166.9063" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "newname": "",
            "oldname": "Activity 3",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect>""",
        }
        with client:
            response = client.post(
                "/editText", data=json.dumps(test_data), content_type="application/json"
            )
            expected_puml = """@startuml
:Activity 1;
:Activity 2;
:Activity 4;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_text_multiline(self, client):
        test_data = {
            "plantuml": """@startuml
  :Activity
  ASdasdasd
  asdasdasd;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="61.9063" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="90" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="70" x="21" y="45.9375" style="pointer-events: none;">ASdasdasd</text><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="21" y="59.9063" style="pointer-events: none;">asdasdasd</text>""",
            "newname": "Hej",
            "oldname": "Activity 3",
            "svgelement": """<rect fill="#F1F1F1" height="61.9063" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="90" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/editText", data=json.dumps(test_data), content_type="application/json"
            )
            expected_puml = """@startuml
  :Hej;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_text(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
:Activity 2;
:Activity 3;
:Activity 4;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688">Activity 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="85.9375">Activity 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="139.9063">Activity 3</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="172.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="193.875">Activity 4</text><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="44.5,54.9688,48.5,64.9688,52.5,54.9688,48.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="98.9375" y2="118.9375"></line><polygon fill="#181818" points="44.5,108.9375,48.5,118.9375,52.5,108.9375,48.5,112.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="152.9063" y2="172.9063"></line><polygon fill="#181818" points="44.5,162.9063,48.5,172.9063,52.5,162.9063,48.5,166.9063" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "newname": "Hej",
            "oldname": "Activity 3",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect>""",
        }
        with client:
            response = client.post(
                "/editText", data=json.dumps(test_data), content_type="application/json"
            )
            expected_puml = """@startuml
:Activity 1;
:Activity 2;
:Hej;
:Activity 4;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_get_text_link(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Link to [[google.com Google]];
stop
@enduml""",
            "svg": """<ellipse cx="65.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="109" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="41" x="21" y="70.9688" style="pointer-events: none;">Link to</text><a href="google.com" target="_top" title="google.com" xlink:actuate="onRequest" xlink:href="google.com" xlink:show="new" xlink:title="google.com" xlink:type="simple"><text fill="#0000FF" font-family="sans-serif" font-size="12" lengthAdjust="spacing" text-decoration="underline" textLength="44" x="66" y="70.9688" style="pointer-events: none;">Google</text></a><ellipse cx="65.5" cy="114.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="65.5" cy="114.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="65.5" x2="65.5" y1="30" y2="50"></line><polygon fill="#181818" points="61.5,40,65.5,50,69.5,40,65.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="65.5" x2="65.5" y1="83.9688" y2="103.9688"></line><polygon fill="#181818" points="61.5,93.9688,65.5,103.9688,69.5,93.9688,65.5,97.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="109" x="11" y="50"></rect>""",
        }
        with client:
            response = client.post(
                "/getText", data=json.dumps(test_data), content_type="application/json"
            )
            expected_output = """Link to [[google.com Google]]"""
            assert response.data.decode("utf-8") == expected_output

    def test_get_text(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
:Activity 2;
:Activity 3
Hej
Bom;
:Activity 4;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688">Activity 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="85.9375">Activity 2</text><rect fill="#F1F1F1" height="61.9063" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="139.9063">Activity 3</text><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="20" x="21" y="153.875">Hej</text><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="27" x="21" y="167.8438">Bom</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="200.8438"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="221.8125">Activity 4</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="48.5" x2="48.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="44.5,54.9688,48.5,64.9688,52.5,54.9688,48.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="48.5" x2="48.5" y1="98.9375" y2="118.9375"></line><polygon fill="#181818" points="44.5,108.9375,48.5,118.9375,52.5,108.9375,48.5,112.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="48.5" x2="48.5" y1="180.8438" y2="200.8438"></line><polygon fill="#181818" points="44.5,190.8438,48.5,200.8438,52.5,190.8438,48.5,194.8438" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="61.9063" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect>""",
        }
        with client:
            response = client.post(
                "/getText", data=json.dumps(test_data), content_type="application/json"
            )
            expected_output = """Activity 3
Hej
Bom"""
            assert response.data.decode("utf-8") == expected_output

    def test_delete_activitywithnote(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
:Activity 2;
note right
note
end note
detach
:Activity 3;
:Activity 4;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">Activity 1</text><path d="M106,69.3867 L106,77.9531 L86,81.9531 L106,85.9531 L106,94.5195 A0,0 0 0 0 106,94.5195 L156,94.5195 A0,0 0 0 0 156,94.5195 L156,79.3867 L146,69.3867 L106,69.3867 A0,0 0 0 0 106,69.3867 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M146,69.3867 L146,79.3867 L156,79.3867 L146,69.3867 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="29" x="112" y="86.2695" style="pointer-events: none;">note</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="85.9375" style="pointer-events: none;">Activity 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="139.9063" style="pointer-events: none;">Activity 3</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="172.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="193.875" style="pointer-events: none;">Activity 4</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="48.5" x2="48.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="44.5,54.9688,48.5,64.9688,52.5,54.9688,48.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="48.5" x2="48.5" y1="98.9375" y2="118.9375"></line><polygon fill="#181818" points="44.5,108.9375,48.5,118.9375,52.5,108.9375,48.5,112.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="48.5" x2="48.5" y1="152.9063" y2="172.9063"></line><polygon fill="#181818" points="44.5,162.9063,48.5,172.9063,52.5,162.9063,48.5,166.9063" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect>""",
        }
        with client:
            response = client.post(
                "/deleteActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
:Activity 3;
:Activity 4;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_delete_activity2(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
:Activity;
repeat
:Activity;
backward:Activity2;
:Activity;
repeat while (while ?) is (yes) not (no)
backward:Activity2;
:Activity;
repeat while (while ?) is (yes) not (no)
@enduml""",
            "svg": """<ellipse cx="51.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="114.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="191.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="212.9375" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="260.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="281.9063" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,147.9688,63.5,159.9688,51.5,171.9688,39.5,159.9688,51.5,147.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,314.9063,71,314.9063,83,326.9063,71,338.9063,32,338.9063,20,326.9063,32,314.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="348.9609" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="330.5586" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="324.1563" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="107" y="226.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="117" y="247.4219" style="pointer-events: none;">Activity2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="370.4609"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="391.4297" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,50,63.5,62,51.5,74,39.5,62,51.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,424.4297,71,424.4297,83,436.4297,71,448.4297,32,448.4297,20,436.4297,32,424.4297" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="458.4844" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="440.082" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="433.6797" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="188" y="226.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="198" y="247.4219" style="pointer-events: none;">Activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="225.9375" y2="260.9375"></line><polygon fill="#181818" points="47.5,250.9375,51.5,260.9375,55.5,250.9375,51.5,254.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="171.9688" y2="191.9688"></line><polygon fill="#181818" points="47.5,181.9688,51.5,191.9688,55.5,181.9688,51.5,185.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="142.5" y1="326.9063" y2="326.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="142.5" x2="142.5" y1="260.4219" y2="326.9063"></line><polygon fill="#181818" points="138.5,270.4219,142.5,260.4219,146.5,270.4219,142.5,266.4219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="142.5" x2="142.5" y1="159.9688" y2="226.4531"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="142.5" x2="63.5" y1="159.9688" y2="159.9688"></line><polygon fill="#181818" points="73.5,155.9688,63.5,159.9688,73.5,163.9688,69.5,159.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="294.9063" y2="314.9063"></line><polygon fill="#181818" points="47.5,304.9063,51.5,314.9063,55.5,304.9063,51.5,308.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="127.9688" y2="147.9688"></line><polygon fill="#181818" points="47.5,137.9688,51.5,147.9688,55.5,137.9688,51.5,141.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="338.9063" y2="370.4609"></line><polygon fill="#181818" points="47.5,360.4609,51.5,370.4609,55.5,360.4609,51.5,364.4609" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="74" y2="94"></line><polygon fill="#181818" points="47.5,84,51.5,94,55.5,84,51.5,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="223.5" y1="436.4297" y2="436.4297"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="223.5" x2="223.5" y1="260.4219" y2="436.4297"></line><polygon fill="#181818" points="219.5,270.4219,223.5,260.4219,227.5,270.4219,223.5,266.4219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="223.5" x2="223.5" y1="62" y2="226.4531"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="223.5" x2="63.5" y1="62" y2="62"></line><polygon fill="#181818" points="73.5,58,63.5,62,73.5,66,69.5,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="404.4297" y2="424.4297"></line><polygon fill="#181818" points="47.5,414.4297,51.5,424.4297,55.5,414.4297,51.5,418.4297" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="30" y2="50"></line><polygon fill="#181818" points="47.5,40,51.5,50,55.5,40,51.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="107" y="226.4531"></rect>""",
        }
        with client:
            response = client.post(
                "/deleteActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
:Activity;
repeat
:Activity;
:Activity;
repeat while (while ?) is (yes) not (no)
backward:Activity2;
:Activity;
repeat while (while ?) is (yes) not (no)
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_delete_activity(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
:Activity 2;
:Activity 3;
:Activity 4;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688">Activity 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="85.9375">Activity 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="139.9063">Activity 3</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="172.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="193.875">Activity 4</text><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="44.5,54.9688,48.5,64.9688,52.5,54.9688,48.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="98.9375" y2="118.9375"></line><polygon fill="#181818" points="44.5,108.9375,48.5,118.9375,52.5,108.9375,48.5,112.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="152.9063" y2="172.9063"></line><polygon fill="#181818" points="44.5,162.9063,48.5,172.9063,52.5,162.9063,48.5,166.9063" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect>""",
        }
        with client:
            response = client.post(
                "/deleteActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
:Activity 2;
:Activity 4;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_activity_line(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
:Activity 2;
:Activity 3;
:Activity 4;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688">Activity 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="85.9375">Activity 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="139.9063">Activity 3</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="172.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="193.875">Activity 4</text><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="44.5,54.9688,48.5,64.9688,52.5,54.9688,48.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="98.9375" y2="118.9375"></line><polygon fill="#181818" points="44.5,108.9375,48.5,118.9375,52.5,108.9375,48.5,112.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="152.9063" y2="172.9063"></line><polygon fill="#181818" points="44.5,162.9063,48.5,172.9063,52.5,162.9063,48.5,166.9063" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect>""",
        }
        with client:
            response = client.post(
                "/getActivityLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )

            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            expected_output = [3, 3]
            assert result_value == expected_output
