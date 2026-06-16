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

"""Tests for note annotation creation, editing, deletion, and side toggling."""

from flask import json


class TestAppRoutesNote:
    def test_togglenoteleft(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note left
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
        }
        with client:
            response = client.post(
                "/noteToggle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
note right
Hello
end note
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_togglenote(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
        }
        with client:
            response = client.post(
                "/noteToggle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
note left
Hello
end note
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_deletenote(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
        }
        with client:
            response = client.post(
                "/deleteNote",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_get_note_line(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
        }
        with client:
            response = client.post(
                "/getNoteLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
        response_json = json.loads(response.data.decode("utf-8"))
        result_value = response_json.get("result")

        # Expected value
        expected_puml = [3, 5]

        # Assert the result value is as expected
        assert result_value == expected_puml

    def test_editnote_empty(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
            "text": "",
        }
        with client:
            response = client.post(
                "/editNote",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_editnote(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
            "text": """Bom""",
        }
        with client:
            response = client.post(
                "/editNote",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
note right
Bom
end note
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def testgettextnote(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
        }
        with client:
            response = client.post(
                "/getNoteText",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = "Hello"
            assert response.data.decode("utf-8") == expected_result

    def testgettextnotebug(self, client):
        test_data = {
            "plantuml": """@startuml
title
This is the title of this diagram
endtitle
start
:Link to [[google.com Start]];
note right
start
end note
if (Statement) then (yes)
  :Activity;
while (While ?) is (yes)
  :Activity;
endwhile (no)
#red:Activity;
note left
end
end note
else (no)
  :Activity;
group group
if (Statement) then (yes)
  :Activity;
(C)
detach
else (no)
#lightgreen:Activity;
note right
hej
end note
fork
  :action;
stop
fork again
  :action;
fork again
  :action;
note right
action
end note
end merge
endif
end group
partition partition {
while (While ?) is (yes)
  :Activity;
endwhile (no)
(C)
note right
end
end note
}
endif
detach
@enduml
""",
            "svg": """<text fill="#000000" font-family="sans-serif" font-size="14" font-weight="bold" lengthAdjust="spacing" textLength="238" x="197" y="32.7969">This is the title of this diagram</text><ellipse cx="219.5" cy="57.2969" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M287.5,91.7148 L287.5,100.2813 L267.5,104.2813 L287.5,108.2813 L287.5,116.8477 A0,0 0 0 0 287.5,116.8477 L338.5,116.8477 A0,0 0 0 0 338.5,116.8477 L338.5,101.7148 L328.5,91.7148 L287.5,91.7148 A0,0 0 0 0 287.5,91.7148 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M328.5,91.7148 L328.5,101.7148 L338.5,101.7148 L328.5,91.7148 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="30" x="293.5" y="108.5977" style="pointer-events: none;">start</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="96" x="171.5" y="87.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="41" x="181.5" y="108.2656" style="pointer-events: none;">Link to</text><a href="google.com" target="_top" title="google.com" xlink:actuate="onRequest" xlink:href="google.com" xlink:show="new" xlink:title="google.com" xlink:type="simple"><text fill="#0000FF" font-family="sans-serif" font-size="12" lengthAdjust="spacing" text-decoration="underline" textLength="31" x="226.5" y="108.2656" style="pointer-events: none;">Start</text></a><polygon fill="#F1F1F1" points="190,141.2656,249,141.2656,261,153.2656,249,165.2656,190,165.2656,178,153.2656,190,141.2656" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="190" y="156.918" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="158" y="150.5156" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="261" y="150.5156" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="75" y="175.2656"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="85" y="196.2344" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="75" y="290.0391"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="85" y="311.0078" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="87,229.2344,126,229.2344,138,241.2344,126,253.2344,87,253.2344,75,241.2344,87,229.2344" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="110.5" y="263.2891" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="87" y="244.8867" style="pointer-events: none;">While ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="61" y="238.4844" style="pointer-events: none;">no</text><path d="M10,386.9336 L10,412.0664 A0,0 0 0 0 10,412.0664 L55,412.0664 A0,0 0 0 0 55,412.0664 L55,404.9336 L75,399.5 L55,396.9336 L55,396.9336 L45,386.9336 L10,386.9336 A0,0 0 0 0 10,386.9336 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M45,386.9336 L45,396.9336 L55,396.9336 L45,386.9336 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="24" x="16" y="403.8164" style="pointer-events: none;">end</text><rect fill="#FF0000" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="75" y="382.5156"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="85" y="403.4844" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="301" y="175.2656"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="311" y="196.2344" style="pointer-events: none;">Activity</text><rect fill="none" height="301.7422" style="stroke:#000000;stroke-width:1.5;" width="454" x="170" y="229.2344"></rect><path d="M221,229.2344 L221,238.5313 L211,248.5313 L170,248.5313 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="41" x="173" y="243.0313">group</text><polygon fill="#F1F1F1" points="303,265.5313,362,265.5313,374,277.5313,362,289.5313,303,289.5313,291,277.5313,303,265.5313" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="303" y="281.1836" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="271" y="274.7813" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="374" y="274.7813" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="190" y="299.5313"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="200" y="320.5" style="pointer-events: none;">Activity</text><ellipse cx="221.5" cy="378.0078" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M224.7344,374.4297 L224.7344,375.6797 Q224.125,375.1172 223.4531,374.8516 Q222.7813,374.5703 222.0156,374.5703 Q220.5156,374.5703 219.7188,375.4922 Q218.9219,376.4141 218.9219,378.1484 Q218.9219,379.8672 219.7188,380.7891 Q220.5156,381.7109 222.0156,381.7109 Q222.7813,381.7109 223.4531,381.4297 Q224.125,381.1484 224.7344,380.6016 L224.7344,381.8359 Q224.1094,382.2578 223.4063,382.4766 Q222.7188,382.6797 221.9531,382.6797 Q219.9531,382.6797 218.8125,381.4609 Q217.6719,380.2422 217.6719,378.1484 Q217.6719,376.0391 218.8125,374.8203 Q219.9531,373.6016 221.9531,373.6016 Q222.7344,373.6016 223.4219,373.8203 Q224.125,374.0234 224.7344,374.4297 Z " fill="#000000" style="pointer-events: none;"></path><path d="M495,303.9492 L495,312.5156 L475,316.5156 L495,320.5156 L495,329.082 A0,0 0 0 0 495,329.082 L535,329.082 A0,0 0 0 0 535,329.082 L535,313.9492 L525,303.9492 L495,303.9492 A0,0 0 0 0 495,303.9492 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M525,303.9492 L525,313.9492 L535,313.9492 L525,303.9492 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="19" x="501" y="320.832" style="pointer-events: none;">hej</text><rect fill="#90EE90" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="412" y="299.5313"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="422" y="320.5" style="pointer-events: none;">Activity</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="339" x="273" y="368.0078"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="287" y="394.0078"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="297" y="414.9766" style="pointer-events: none;">action</text><ellipse cx="316.5" cy="473.9766" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="316.5" cy="473.9766" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="374" y="422.5078"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="384" y="443.4766" style="pointer-events: none;">action</text><path d="M540,426.9258 L540,435.4922 L520,439.4922 L540,443.4922 L540,452.0586 A0,0 0 0 0 540,452.0586 L600,452.0586 A0,0 0 0 0 600,452.0586 L600,436.9258 L590,426.9258 L540,426.9258 A0,0 0 0 0 540,426.9258 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M590,426.9258 L590,436.9258 L600,436.9258 L590,426.9258 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="39" x="546" y="443.8086" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="461" y="422.5078"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="471" y="443.4766" style="pointer-events: none;">action</text><polygon fill="#F1F1F1" points="443.5,494.9766,455.5,506.9766,443.5,518.9766,431.5,506.9766,443.5,494.9766" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="none" height="202.3867" style="stroke:#000000;stroke-width:1.5;" width="150.5" x="267" y="540.9766"></rect><path d="M333,540.9766 L333,550.2734 L323,560.2734 L267,560.2734 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="56" x="270" y="554.7734">partition</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="301" y="632.8281"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="311" y="653.7969" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="313,577.2734,352,577.2734,364,589.2734,352,601.2734,313,601.2734,301,589.2734,313,577.2734" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="336.5" y="611.3281" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="313" y="592.9258" style="pointer-events: none;">While ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="287" y="586.5234" style="pointer-events: none;">no</text><path d="M362.5,706.2305 L362.5,714.7969 L342.5,718.7969 L362.5,722.7969 L362.5,731.3633 A0,0 0 0 0 362.5,731.3633 L407.5,731.3633 A0,0 0 0 0 407.5,731.3633 L407.5,716.2305 L397.5,706.2305 L362.5,706.2305 A0,0 0 0 0 362.5,706.2305 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M397.5,706.2305 L397.5,716.2305 L407.5,716.2305 L397.5,706.2305 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="24" x="368.5" y="723.1133" style="pointer-events: none;">end</text><ellipse cx="332.5" cy="718.7969" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M335.7344,715.2188 L335.7344,716.4688 Q335.125,715.9063 334.4531,715.6406 Q333.7813,715.3594 333.0156,715.3594 Q331.5156,715.3594 330.7188,716.2813 Q329.9219,717.2031 329.9219,718.9375 Q329.9219,720.6563 330.7188,721.5781 Q331.5156,722.5 333.0156,722.5 Q333.7813,722.5 334.4531,722.2188 Q335.125,721.9375 335.7344,721.3906 L335.7344,722.625 Q335.1094,723.0469 334.4063,723.2656 Q333.7188,723.4688 332.9531,723.4688 Q330.9531,723.4688 329.8125,722.25 Q328.6719,721.0313 328.6719,718.9375 Q328.6719,716.8281 329.8125,715.6094 Q330.9531,714.3906 332.9531,714.3906 Q333.7344,714.3906 334.4219,714.6094 Q335.125,714.8125 335.7344,715.2188 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="219.5" x2="219.5" y1="67.2969" y2="87.2969"></line><polygon fill="#181818" points="215.5,77.2969,219.5,87.2969,223.5,77.2969,219.5,81.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106.5" x2="106.5" y1="253.2344" y2="290.0391"></line><polygon fill="#181818" points="102.5,280.0391,106.5,290.0391,110.5,280.0391,106.5,284.0391" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106.5" x2="106.5" y1="324.0078" y2="336.0078"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106.5" x2="150" y1="336.0078" y2="336.0078"></line><polygon fill="#181818" points="146,298.6211,150,288.6211,154,298.6211,150,294.6211" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="150" x2="150" y1="241.2344" y2="336.0078"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="150" x2="138" y1="241.2344" y2="241.2344"></line><polygon fill="#181818" points="148,237.2344,138,241.2344,148,245.2344,144,241.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="75" x2="63" y1="241.2344" y2="241.2344"></line><polygon fill="#181818" points="59,284.6211,63,294.6211,67,284.6211,63,288.6211" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="63" x2="63" y1="241.2344" y2="348.0078"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="63" x2="106.5" y1="348.0078" y2="348.0078"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106.5" x2="106.5" y1="348.0078" y2="382.5156"></line><polygon fill="#181818" points="102.5,372.5156,106.5,382.5156,110.5,372.5156,106.5,376.5156" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106.5" x2="106.5" y1="209.2344" y2="229.2344"></line><polygon fill="#181818" points="102.5,219.2344,106.5,229.2344,110.5,219.2344,106.5,223.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="221.5" x2="221.5" y1="333.5" y2="368.0078"></line><polygon fill="#181818" points="217.5,358.0078,221.5,368.0078,225.5,358.0078,221.5,362.0078" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="316.5" x2="316.5" y1="427.9766" y2="462.9766"></line><polygon fill="#181818" points="312.5,452.9766,316.5,462.9766,320.5,452.9766,316.5,456.9766" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="316.5" x2="316.5" y1="374.0078" y2="394.0078"></line><polygon fill="#181818" points="312.5,384.0078,316.5,394.0078,320.5,384.0078,316.5,388.0078" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="403.5" x2="403.5" y1="374.0078" y2="422.5078"></line><polygon fill="#181818" points="399.5,412.5078,403.5,422.5078,407.5,412.5078,403.5,416.5078" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="490.5" x2="490.5" y1="374.0078" y2="422.5078"></line><polygon fill="#181818" points="486.5,412.5078,490.5,422.5078,494.5,412.5078,490.5,416.5078" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="403.5" x2="403.5" y1="456.4766" y2="506.9766"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="403.5" x2="431.5" y1="506.9766" y2="506.9766"></line><polygon fill="#181818" points="421.5,502.9766,431.5,506.9766,421.5,510.9766,425.5,506.9766" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="490.5" x2="490.5" y1="456.4766" y2="506.9766"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="490.5" x2="455.5" y1="506.9766" y2="506.9766"></line><polygon fill="#181818" points="465.5,502.9766,455.5,506.9766,465.5,510.9766,461.5,506.9766" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="443.5" x2="443.5" y1="333.5" y2="368.0078"></line><polygon fill="#181818" points="439.5,358.0078,443.5,368.0078,447.5,358.0078,443.5,362.0078" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="291" x2="221.5" y1="277.5313" y2="277.5313"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="221.5" x2="221.5" y1="277.5313" y2="299.5313"></line><polygon fill="#181818" points="217.5,289.5313,221.5,299.5313,225.5,289.5313,221.5,293.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="374" x2="443.5" y1="277.5313" y2="277.5313"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="443.5" x2="443.5" y1="277.5313" y2="299.5313"></line><polygon fill="#181818" points="439.5,289.5313,443.5,299.5313,447.5,289.5313,443.5,293.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="443.5" x2="443.5" y1="518.9766" y2="523.9766"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="443.5" x2="332.5" y1="523.9766" y2="523.9766"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="332.5" y1="523.9766" y2="577.2734"></line><polygon fill="#181818" points="328.5,567.2734,332.5,577.2734,336.5,567.2734,332.5,571.2734" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="332.5" y1="209.2344" y2="265.5313"></line><polygon fill="#181818" points="328.5,255.5313,332.5,265.5313,336.5,255.5313,332.5,259.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="332.5" y1="601.2734" y2="632.8281"></line><polygon fill="#181818" points="328.5,622.8281,332.5,632.8281,336.5,622.8281,332.5,626.8281" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="332.5" y1="666.7969" y2="676.7969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="376" y1="676.7969" y2="676.7969"></line><polygon fill="#181818" points="372,641.4102,376,631.4102,380,641.4102,376,637.4102" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="376" x2="376" y1="589.2734" y2="676.7969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="376" x2="364" y1="589.2734" y2="589.2734"></line><polygon fill="#181818" points="374,585.2734,364,589.2734,374,593.2734,370,589.2734" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="301" x2="289" y1="589.2734" y2="589.2734"></line><polygon fill="#181818" points="285,627.4102,289,637.4102,293,627.4102,289,631.4102" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="289" x2="289" y1="589.2734" y2="688.7969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="289" x2="332.5" y1="688.7969" y2="688.7969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="332.5" y1="688.7969" y2="708.7969"></line><polygon fill="#181818" points="328.5,698.7969,332.5,708.7969,336.5,698.7969,332.5,702.7969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="178" x2="106.5" y1="153.2656" y2="153.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106.5" x2="106.5" y1="153.2656" y2="175.2656"></line><polygon fill="#181818" points="102.5,165.2656,106.5,175.2656,110.5,165.2656,106.5,169.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="261" x2="332.5" y1="153.2656" y2="153.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="332.5" y1="153.2656" y2="175.2656"></line><polygon fill="#181818" points="328.5,165.2656,332.5,175.2656,336.5,165.2656,332.5,169.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="219.5" x2="219.5" y1="121.2656" y2="141.2656"></line><polygon fill="#181818" points="215.5,131.2656,219.5,141.2656,223.5,131.2656,219.5,135.2656" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M495,303.9492 L495,312.5156 L475,316.5156 L495,320.5156 L495,329.082 A0,0 0 0 0 495,329.082 L535,329.082 A0,0 0 0 0 535,329.082 L535,313.9492 L525,303.9492 L495,303.9492 A0,0 0 0 0 495,303.9492 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
        }
        with client:
            response = client.post(
                "/getNoteText",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = "hej"
            assert response.data.decode("utf-8") == expected_result
