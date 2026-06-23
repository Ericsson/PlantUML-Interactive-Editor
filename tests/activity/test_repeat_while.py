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

"""Tests for repeat-while loop creation, editing, deletion, and backward activity."""

from flask import json


class TestAppRoutesRepeatWhile:
    def test_checkrepeathasbackward2(self, client):
        test_data = {
            "plantuml": """@startuml
repeat
  :Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="54"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="74.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,10,63.5,22,51.5,34,39.5,22,51.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="142.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="123.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="117.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="163.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="184.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="34" y2="54"></line><polygon fill="#181818" points="47.5,44,51.5,54,55.5,44,51.5,48" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="95" y1="119.9688" y2="119.9688"></line><polygon fill="#181818" points="91,80.9844,95,70.9844,99,80.9844,95,76.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="95" y1="22" y2="119.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="63.5" y1="22" y2="22"></line><polygon fill="#181818" points="73.5,18,63.5,22,73.5,26,69.5,22" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="87.9688" y2="107.9688"></line><polygon fill="#181818" points="47.5,97.9688,51.5,107.9688,55.5,97.9688,51.5,101.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="131.9688" y2="163.5234"></line><polygon fill="#181818" points="47.5,153.5234,51.5,163.5234,55.5,153.5234,51.5,157.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/checkIfRepeatHasBackward",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """empty"""
            assert response.data.decode("utf-8") == expected_puml

    def test_checkrepeathasbackward(self, client):
        test_data = {
            "plantuml": """@startuml
repeat
  :Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="54"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="74.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,10,63.5,22,51.5,34,39.5,22,51.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="142.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="123.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="117.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="163.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="184.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="34" y2="54"></line><polygon fill="#181818" points="47.5,44,51.5,54,55.5,44,51.5,48" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="95" y1="119.9688" y2="119.9688"></line><polygon fill="#181818" points="91,80.9844,95,70.9844,99,80.9844,95,76.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="95" y1="22" y2="119.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="63.5" y1="22" y2="22"></line><polygon fill="#181818" points="73.5,18,63.5,22,73.5,26,69.5,22" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="87.9688" y2="107.9688"></line><polygon fill="#181818" points="47.5,97.9688,51.5,107.9688,55.5,97.9688,51.5,101.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="131.9688" y2="163.5234"></line><polygon fill="#181818" points="47.5,153.5234,51.5,163.5234,55.5,153.5234,51.5,157.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/checkIfRepeatHasBackward",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """backward"""
            assert response.data.decode("utf-8") == expected_puml

    def test_checkrepeat(self, client):
        test_data = {
            "plantuml": """@startuml
repeat
  :Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="54"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="74.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,10,63.5,22,51.5,34,39.5,22,51.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="142.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="123.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="117.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="163.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="184.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="34" y2="54"></line><polygon fill="#181818" points="47.5,44,51.5,54,55.5,44,51.5,48" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="95" y1="119.9688" y2="119.9688"></line><polygon fill="#181818" points="91,80.9844,95,70.9844,99,80.9844,95,76.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="95" y1="22" y2="119.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="63.5" y1="22" y2="22"></line><polygon fill="#181818" points="73.5,18,63.5,22,73.5,26,69.5,22" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="87.9688" y2="107.9688"></line><polygon fill="#181818" points="47.5,97.9688,51.5,107.9688,55.5,97.9688,51.5,101.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="131.9688" y2="163.5234"></line><polygon fill="#181818" points="47.5,153.5234,51.5,163.5234,55.5,153.5234,51.5,157.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/checkWhatPoly",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """repeat"""
            assert response.data.decode("utf-8") == expected_puml

    def test_gettext_repeatwhile(self, client):
        test_data = {
            "plantuml": """@startuml
repeat
  :Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="54"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="74.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,10,63.5,22,51.5,34,39.5,22,51.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="142.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="123.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="117.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="163.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="184.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="34" y2="54"></line><polygon fill="#181818" points="47.5,44,51.5,54,55.5,44,51.5,48" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="95" y1="119.9688" y2="119.9688"></line><polygon fill="#181818" points="91,80.9844,95,70.9844,99,80.9844,95,76.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="95" y1="22" y2="119.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="63.5" y1="22" y2="22"></line><polygon fill="#181818" points="73.5,18,63.5,22,73.5,26,69.5,22" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="87.9688" y2="107.9688"></line><polygon fill="#181818" points="47.5,97.9688,51.5,107.9688,55.5,97.9688,51.5,101.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="131.9688" y2="163.5234"></line><polygon fill="#181818" points="47.5,153.5234,51.5,163.5234,55.5,153.5234,51.5,157.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getTextPoly",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            output = ["while ?", "no", "yes"]
            json.loads(response.data.decode("utf-8")) == output

    def test_add_backwards_already_exists(self, client):
        test_data = {
            "plantuml": """@startuml
repeat
  :Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="54"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="74.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,10,63.5,22,51.5,34,39.5,22,51.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="142.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="123.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="117.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="163.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="184.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="34" y2="54"></line><polygon fill="#181818" points="47.5,44,51.5,54,55.5,44,51.5,48" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="95" y1="119.9688" y2="119.9688"></line><polygon fill="#181818" points="91,80.9844,95,70.9844,99,80.9844,95,76.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="95" y1="22" y2="119.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="63.5" y1="22" y2="22"></line><polygon fill="#181818" points="73.5,18,63.5,22,73.5,26,69.5,22" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="87.9688" y2="107.9688"></line><polygon fill="#181818" points="47.5,97.9688,51.5,107.9688,55.5,97.9688,51.5,101.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="131.9688" y2="163.5234"></line><polygon fill="#181818" points="47.5,153.5234,51.5,163.5234,55.5,153.5234,51.5,157.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/addBackwards",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
repeat
  :Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_backwards(self, client):
        test_data = {
            "plantuml": """@startuml
repeat
  :Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="54"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="74.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,10,63.5,22,51.5,34,39.5,22,51.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="142.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="123.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="117.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="163.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="184.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="34" y2="54"></line><polygon fill="#181818" points="47.5,44,51.5,54,55.5,44,51.5,48" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="95" y1="119.9688" y2="119.9688"></line><polygon fill="#181818" points="91,80.9844,95,70.9844,99,80.9844,95,76.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="95" y1="22" y2="119.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="63.5" y1="22" y2="22"></line><polygon fill="#181818" points="73.5,18,63.5,22,73.5,26,69.5,22" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="87.9688" y2="107.9688"></line><polygon fill="#181818" points="47.5,97.9688,51.5,107.9688,55.5,97.9688,51.5,101.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="131.9688" y2="163.5234"></line><polygon fill="#181818" points="47.5,153.5234,51.5,163.5234,55.5,153.5234,51.5,157.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/addBackwards",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
repeat
  :Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_repeat_while(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
  :b;
  :b;
  repeat
  :aa;
  :aa;
repeat while (a) is (a) not (a)
repeat while (b) is (b) not (b)
@enduml""",
            "svg": """<ellipse cx="44" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="30" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="40" y="114.9688" style="pointer-events: none;">b</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="30" y="147.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="40" y="168.9375" style="pointer-events: none;">b</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="36" x="26" y="253.4375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="16" x="36" y="274.4063" style="pointer-events: none;">aa</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="36" x="26" y="314.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="16" x="36" y="335.875" style="pointer-events: none;">aa</text><polygon fill="#F1F1F1" points="44,201.9375,56,213.9375,44,225.9375,32,213.9375,44,201.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,368.875,56,368.875,68,380.875,56,392.875,32,392.875,20,380.875,32,368.875" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="48" y="402.9297" style="pointer-events: none;">a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="40.5" y="384.5273" style="pointer-events: none;">a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="68" y="378.125" style="pointer-events: none;">a</text><polygon fill="#F1F1F1" points="44,50,56,62,44,74,32,62,44,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,424.4297,56,424.4297,68,436.4297,56,448.4297,32,448.4297,20,436.4297,32,424.4297" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="48" y="458.4844" style="pointer-events: none;">b</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="40.5" y="440.082" style="pointer-events: none;">b</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="68" y="433.6797" style="pointer-events: none;">b</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="127.9688" y2="147.9688"></line><polygon fill="#181818" points="40,137.9688,44,147.9688,48,137.9688,44,141.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="287.4063" y2="314.9063"></line><polygon fill="#181818" points="40,304.9063,44,314.9063,48,304.9063,44,308.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="225.9375" y2="253.4375"></line><polygon fill="#181818" points="40,243.4375,44,253.4375,48,243.4375,44,247.4375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="68" x2="80" y1="380.875" y2="380.875"></line><polygon fill="#181818" points="76,307.4063,80,297.4063,84,307.4063,80,303.4063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="80" x2="80" y1="213.9375" y2="380.875"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="80" x2="56" y1="213.9375" y2="213.9375"></line><polygon fill="#181818" points="66,209.9375,56,213.9375,66,217.9375,62,213.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="348.875" y2="368.875"></line><polygon fill="#181818" points="40,358.875,44,368.875,48,358.875,44,362.875" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="181.9375" y2="201.9375"></line><polygon fill="#181818" points="40,191.9375,44,201.9375,48,191.9375,44,195.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="74" y2="94"></line><polygon fill="#181818" points="40,84,44,94,48,84,44,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="68" x2="98" y1="436.4297" y2="436.4297"></line><polygon fill="#181818" points="94,245.9375,98,235.9375,102,245.9375,98,241.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="98" x2="98" y1="62" y2="436.4297"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="98" x2="56" y1="62" y2="62"></line><polygon fill="#181818" points="66,58,56,62,66,66,62,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="392.875" y2="424.4297"></line><polygon fill="#181818" points="40,414.4297,44,424.4297,48,414.4297,44,418.4297" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="30" y2="50"></line><polygon fill="#181818" points="40,40,44,50,48,40,44,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,424.4297,56,424.4297,68,436.4297,56,448.4297,32,448.4297,20,436.4297,32,424.4297" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "where": "right",
            "type": "fork",
        }
        with client:
            response = client.post(
                "/addToIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
  :b;
  :b;
  repeat
  :aa;
  :aa;
repeat while (a) is (a) not (a)
repeat while (b) is (b) not (b)
fork
:action;
fork again
:action;
end fork
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_repeatwhile4(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
:activity;
repeat while (hej) is (yes) not (no)
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="114.9688" style="pointer-events: none;">activity</text><polygon fill="#F1F1F1" points="94,50,106,62,94,74,82,62,94,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="82,147.9688,106,147.9688,118,159.9688,106,171.9688,82,171.9688,70,159.9688,82,147.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="182.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="85.5" y="163.6211" style="pointer-events: none;">hej</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="118" y="157.2188" style="pointer-events: none;">yes</text><polygon fill="#F1F1F1" points="64.5,203.5234,123.5,203.5234,135.5,215.5234,123.5,227.5234,64.5,227.5234,52.5,215.5234,64.5,203.5234" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="219.1758" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="212.7734" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="212.7734" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="237.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="258.4922" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="237.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="258.4922" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,277.4922,106,289.4922,94,301.4922,82,289.4922,94,277.4922" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="94"></line><polygon fill="#181818" points="90,84,94,94,98,84,94,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118" x2="137.5" y1="159.9688" y2="159.9688"></line><polygon fill="#181818" points="133.5,120.9844,137.5,110.9844,141.5,120.9844,137.5,116.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="137.5" x2="137.5" y1="62" y2="159.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="137.5" x2="106" y1="62" y2="62"></line><polygon fill="#181818" points="116,58,106,62,116,66,112,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="127.9688" y2="147.9688"></line><polygon fill="#181818" points="90,137.9688,94,147.9688,98,137.9688,94,141.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="215.5234" y2="215.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="215.5234" y2="237.5234"></line><polygon fill="#181818" points="38.5,227.5234,42.5,237.5234,46.5,227.5234,42.5,231.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="215.5234" y2="215.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="215.5234" y2="237.5234"></line><polygon fill="#181818" points="141.5,227.5234,145.5,237.5234,149.5,227.5234,145.5,231.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="271.4922" y2="289.4922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="289.4922" y2="289.4922"></line><polygon fill="#181818" points="72,285.4922,82,289.4922,72,293.4922,76,289.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="271.4922" y2="289.4922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="289.4922" y2="289.4922"></line><polygon fill="#181818" points="116,285.4922,106,289.4922,116,293.4922,112,289.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="171.9688" y2="203.5234"></line><polygon fill="#181818" points="90,193.5234,94,203.5234,98,193.5234,94,197.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "State",
            "branch1": "bam",
            "branch2": "bom",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,203.5234,123.5,203.5234,135.5,215.5234,123.5,227.5234,64.5,227.5234,52.5,215.5234,64.5,203.5234" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
:activity;
repeat while (hej) is (yes) not (no)
if (State) then (bam)
  :Activity;
else (bom)
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_repeatwhile3(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
:activity;
repeat while (hej) is (yes) not (no)
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="114.9688" style="pointer-events: none;">activity</text><polygon fill="#F1F1F1" points="94,50,106,62,94,74,82,62,94,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="82,147.9688,106,147.9688,118,159.9688,106,171.9688,82,171.9688,70,159.9688,82,147.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="182.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="85.5" y="163.6211" style="pointer-events: none;">hej</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="118" y="157.2188" style="pointer-events: none;">yes</text><polygon fill="#F1F1F1" points="64.5,203.5234,123.5,203.5234,135.5,215.5234,123.5,227.5234,64.5,227.5234,52.5,215.5234,64.5,203.5234" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="219.1758" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="212.7734" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="212.7734" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="237.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="258.4922" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="237.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="258.4922" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,277.4922,106,289.4922,94,301.4922,82,289.4922,94,277.4922" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="94"></line><polygon fill="#181818" points="90,84,94,94,98,84,94,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118" x2="137.5" y1="159.9688" y2="159.9688"></line><polygon fill="#181818" points="133.5,120.9844,137.5,110.9844,141.5,120.9844,137.5,116.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="137.5" x2="137.5" y1="62" y2="159.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="137.5" x2="106" y1="62" y2="62"></line><polygon fill="#181818" points="116,58,106,62,116,66,112,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="127.9688" y2="147.9688"></line><polygon fill="#181818" points="90,137.9688,94,147.9688,98,137.9688,94,141.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="215.5234" y2="215.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="215.5234" y2="237.5234"></line><polygon fill="#181818" points="38.5,227.5234,42.5,237.5234,46.5,227.5234,42.5,231.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="215.5234" y2="215.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="215.5234" y2="237.5234"></line><polygon fill="#181818" points="141.5,227.5234,145.5,237.5234,149.5,227.5234,145.5,231.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="271.4922" y2="289.4922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="289.4922" y2="289.4922"></line><polygon fill="#181818" points="72,285.4922,82,289.4922,72,293.4922,76,289.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="271.4922" y2="289.4922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="289.4922" y2="289.4922"></line><polygon fill="#181818" points="116,285.4922,106,289.4922,116,293.4922,112,289.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="171.9688" y2="203.5234"></line><polygon fill="#181818" points="90,193.5234,94,203.5234,98,193.5234,94,197.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "State",
            "branch1": "bam",
            "branch2": "bom",
            "svgelement": """<polygon fill="#F1F1F1" points="82,147.9688,106,147.9688,118,159.9688,106,171.9688,82,171.9688,70,159.9688,82,147.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
:activity;
repeat while (State) is (bom) not (bam)
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_repeatwhile2(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
  :b;
  :b;
  repeat
  :aa;
  :aa;
repeat while (a) is (a) not (a)
repeat while (b) is (b) not (b)
@enduml""",
            "svg": """<ellipse cx="44" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="30" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="40" y="114.9688" style="pointer-events: none;">b</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="30" y="147.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="40" y="168.9375" style="pointer-events: none;">b</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="36" x="26" y="253.4375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="16" x="36" y="274.4063" style="pointer-events: none;">aa</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="36" x="26" y="314.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="16" x="36" y="335.875" style="pointer-events: none;">aa</text><polygon fill="#F1F1F1" points="44,201.9375,56,213.9375,44,225.9375,32,213.9375,44,201.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,368.875,56,368.875,68,380.875,56,392.875,32,392.875,20,380.875,32,368.875" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="48" y="402.9297" style="pointer-events: none;">a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="40.5" y="384.5273" style="pointer-events: none;">a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="68" y="378.125" style="pointer-events: none;">a</text><polygon fill="#F1F1F1" points="44,50,56,62,44,74,32,62,44,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,424.4297,56,424.4297,68,436.4297,56,448.4297,32,448.4297,20,436.4297,32,424.4297" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="48" y="458.4844" style="pointer-events: none;">b</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="40.5" y="440.082" style="pointer-events: none;">b</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="68" y="433.6797" style="pointer-events: none;">b</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="127.9688" y2="147.9688"></line><polygon fill="#181818" points="40,137.9688,44,147.9688,48,137.9688,44,141.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="287.4063" y2="314.9063"></line><polygon fill="#181818" points="40,304.9063,44,314.9063,48,304.9063,44,308.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="225.9375" y2="253.4375"></line><polygon fill="#181818" points="40,243.4375,44,253.4375,48,243.4375,44,247.4375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="68" x2="80" y1="380.875" y2="380.875"></line><polygon fill="#181818" points="76,307.4063,80,297.4063,84,307.4063,80,303.4063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="80" x2="80" y1="213.9375" y2="380.875"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="80" x2="56" y1="213.9375" y2="213.9375"></line><polygon fill="#181818" points="66,209.9375,56,213.9375,66,217.9375,62,213.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="348.875" y2="368.875"></line><polygon fill="#181818" points="40,358.875,44,368.875,48,358.875,44,362.875" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="181.9375" y2="201.9375"></line><polygon fill="#181818" points="40,191.9375,44,201.9375,48,191.9375,44,195.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="74" y2="94"></line><polygon fill="#181818" points="40,84,44,94,48,84,44,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="68" x2="98" y1="436.4297" y2="436.4297"></line><polygon fill="#181818" points="94,245.9375,98,235.9375,102,245.9375,98,241.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="98" x2="98" y1="62" y2="436.4297"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="98" x2="56" y1="62" y2="62"></line><polygon fill="#181818" points="66,58,56,62,66,66,62,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="392.875" y2="424.4297"></line><polygon fill="#181818" points="40,414.4297,44,424.4297,48,414.4297,44,418.4297" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="30" y2="50"></line><polygon fill="#181818" points="40,40,44,50,48,40,44,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "State",
            "branch1": "bam",
            "branch2": "bom",
            "svgelement": """<polygon fill="#F1F1F1" points="32,424.4297,56,424.4297,68,436.4297,56,448.4297,32,448.4297,20,436.4297,32,424.4297" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
  :b;
  :b;
  repeat
  :aa;
  :aa;
repeat while (a) is (a) not (a)
repeat while (State) is (bom) not (bam)
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_nested_repeatwhile(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
  :b;
  :b;
  repeat
  :aa;
  :aa;
repeat while (a) is (a) not (a)
repeat while (b) is (b) not (b)
@enduml""",
            "svg": """<ellipse cx="44" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="30" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="40" y="114.9688" style="pointer-events: none;">b</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="30" y="147.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="40" y="168.9375" style="pointer-events: none;">b</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="36" x="26" y="253.4375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="16" x="36" y="274.4063" style="pointer-events: none;">aa</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="36" x="26" y="314.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="16" x="36" y="335.875" style="pointer-events: none;">aa</text><polygon fill="#F1F1F1" points="44,201.9375,56,213.9375,44,225.9375,32,213.9375,44,201.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,368.875,56,368.875,68,380.875,56,392.875,32,392.875,20,380.875,32,368.875" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="48" y="402.9297" style="pointer-events: none;">a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="40.5" y="384.5273" style="pointer-events: none;">a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="68" y="378.125" style="pointer-events: none;">a</text><polygon fill="#F1F1F1" points="44,50,56,62,44,74,32,62,44,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,424.4297,56,424.4297,68,436.4297,56,448.4297,32,448.4297,20,436.4297,32,424.4297" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="48" y="458.4844" style="pointer-events: none;">b</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="40.5" y="440.082" style="pointer-events: none;">b</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="68" y="433.6797" style="pointer-events: none;">b</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="127.9688" y2="147.9688"></line><polygon fill="#181818" points="40,137.9688,44,147.9688,48,137.9688,44,141.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="287.4063" y2="314.9063"></line><polygon fill="#181818" points="40,304.9063,44,314.9063,48,304.9063,44,308.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="225.9375" y2="253.4375"></line><polygon fill="#181818" points="40,243.4375,44,253.4375,48,243.4375,44,247.4375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="68" x2="80" y1="380.875" y2="380.875"></line><polygon fill="#181818" points="76,307.4063,80,297.4063,84,307.4063,80,303.4063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="80" x2="80" y1="213.9375" y2="380.875"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="80" x2="56" y1="213.9375" y2="213.9375"></line><polygon fill="#181818" points="66,209.9375,56,213.9375,66,217.9375,62,213.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="348.875" y2="368.875"></line><polygon fill="#181818" points="40,358.875,44,368.875,48,358.875,44,362.875" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="181.9375" y2="201.9375"></line><polygon fill="#181818" points="40,191.9375,44,201.9375,48,191.9375,44,195.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="74" y2="94"></line><polygon fill="#181818" points="40,84,44,94,48,84,44,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="68" x2="98" y1="436.4297" y2="436.4297"></line><polygon fill="#181818" points="94,245.9375,98,235.9375,102,245.9375,98,241.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="98" x2="98" y1="62" y2="436.4297"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="98" x2="56" y1="62" y2="62"></line><polygon fill="#181818" points="66,58,56,62,66,66,62,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="392.875" y2="424.4297"></line><polygon fill="#181818" points="40,414.4297,44,424.4297,48,414.4297,44,418.4297" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="30" y2="50"></line><polygon fill="#181818" points="40,40,44,50,48,40,44,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,368.875,56,368.875,68,380.875,56,392.875,32,392.875,20,380.875,32,368.875" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
  :b;
  :b;
repeat while (b) is (b) not (b)
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifnestedinrepeatwhile(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
  :read data;
  :generate diagrams;
repeat while (more data?) is (yes) not (no)
if (Bom) then (y)
  :Activity;
else (n)
  :Activity;
endif
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="64.5,94,123.5,94,135.5,106,123.5,118,64.5,118,52.5,106,64.5,94" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="109.6523" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="103.25" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="103.25" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="128"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="148.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="128"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="148.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,167.9688,106,179.9688,94,191.9688,82,179.9688,94,167.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="82" x="53" y="216.9844"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="62" x="63" y="237.9531" style="pointer-events: none;">read data</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="140" x="24" y="270.9531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="120" x="34" y="291.9219" style="pointer-events: none;">generate diagrams</text><polygon fill="#F1F1F1" points="94,50,106,62,94,74,82,62,94,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="61.5,324.9219,126.5,324.9219,138.5,336.9219,126.5,348.9219,61.5,348.9219,49.5,336.9219,61.5,324.9219" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="358.9766" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="65" x="61.5" y="340.5742" style="pointer-events: none;">more data?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="138.5" y="334.1719" style="pointer-events: none;">yes</text><polygon fill="#F1F1F1" points="81,380.4766,107,380.4766,119,392.4766,107,404.4766,81,404.4766,69,392.4766,81,380.4766" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="26" x="81" y="396.1289" style="pointer-events: none;">Bom</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="6" x="63" y="389.7266" style="pointer-events: none;">y</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="119" y="389.7266" style="pointer-events: none;">n</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="21" y="414.4766"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="31" y="435.4453" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="104" y="414.4766"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="114" y="435.4453" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,454.4453,106,466.4453,94,478.4453,82,466.4453,94,454.4453" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="106" y2="106"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="106" y2="128"></line><polygon fill="#181818" points="38.5,118,42.5,128,46.5,118,42.5,122" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="106" y2="106"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="106" y2="128"></line><polygon fill="#181818" points="141.5,118,145.5,128,149.5,118,145.5,122" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="161.9688" y2="179.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="179.9688" y2="179.9688"></line><polygon fill="#181818" points="72,175.9688,82,179.9688,72,183.9688,76,179.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="161.9688" y2="179.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="179.9688" y2="179.9688"></line><polygon fill="#181818" points="116,175.9688,106,179.9688,116,183.9688,112,179.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="191.9688" y2="216.9844"></line><polygon fill="#181818" points="90,206.9844,94,216.9844,98,206.9844,94,210.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="250.9531" y2="270.9531"></line><polygon fill="#181818" points="90,260.9531,94,270.9531,98,260.9531,94,264.9531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="94"></line><polygon fill="#181818" points="90,84,94,94,98,84,94,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="191" y1="336.9219" y2="336.9219"></line><polygon fill="#181818" points="187,211.9688,191,201.9688,195,211.9688,191,207.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="191" y1="62" y2="336.9219"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="106" y1="62" y2="62"></line><polygon fill="#181818" points="116,58,106,62,116,66,112,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="304.9219" y2="324.9219"></line><polygon fill="#181818" points="90,314.9219,94,324.9219,98,314.9219,94,318.9219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="69" x2="52.5" y1="392.4766" y2="392.4766"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="52.5" y1="392.4766" y2="414.4766"></line><polygon fill="#181818" points="48.5,404.4766,52.5,414.4766,56.5,404.4766,52.5,408.4766" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="119" x2="135.5" y1="392.4766" y2="392.4766"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="135.5" y1="392.4766" y2="414.4766"></line><polygon fill="#181818" points="131.5,404.4766,135.5,414.4766,139.5,404.4766,135.5,408.4766" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="52.5" y1="448.4453" y2="466.4453"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="82" y1="466.4453" y2="466.4453"></line><polygon fill="#181818" points="72,462.4453,82,466.4453,72,470.4453,76,466.4453" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="135.5" y1="448.4453" y2="466.4453"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="106" y1="466.4453" y2="466.4453"></line><polygon fill="#181818" points="116,462.4453,106,466.4453,116,470.4453,112,466.4453" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="348.9219" y2="380.4766"></line><polygon fill="#181818" points="90,370.4766,94,380.4766,98,370.4766,94,374.4766" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,94,123.5,94,135.5,106,123.5,118,64.5,118,52.5,106,64.5,94" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
  :read data;
  :generate diagrams;
repeat while (more data?) is (yes) not (no)
if (Bom) then (y)
  :Activity;
else (n)
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifwithrepeatwhileabove(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
  :read data;
  :generate diagrams;
repeat while (more data?) is (yes) not (no)
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="82" x="53" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="62" x="63" y="114.9688" style="pointer-events: none;">read data</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="140" x="24" y="155.4688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="120" x="34" y="176.4375" style="pointer-events: none;">generate diagrams</text><polygon fill="#F1F1F1" points="94,50,106,62,94,74,82,62,94,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="61.5,209.4375,126.5,209.4375,138.5,221.4375,126.5,233.4375,61.5,233.4375,49.5,221.4375,61.5,209.4375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="243.4922" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="65" x="61.5" y="225.0898" style="pointer-events: none;">more data?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="138.5" y="218.6875" style="pointer-events: none;">yes</text><polygon fill="#F1F1F1" points="64.5,264.9922,123.5,264.9922,135.5,276.9922,123.5,288.9922,64.5,288.9922,52.5,276.9922,64.5,264.9922" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="280.6445" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="274.2422" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="274.2422" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="298.9922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="319.9609" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="298.9922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="319.9609" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,338.9609,106,350.9609,94,362.9609,82,350.9609,94,338.9609" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="127.9688" y2="155.4688"></line><polygon fill="#181818" points="90,145.4688,94,155.4688,98,145.4688,94,149.4688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="94"></line><polygon fill="#181818" points="90,84,94,94,98,84,94,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="176" y1="221.4375" y2="221.4375"></line><polygon fill="#181818" points="172,147.9688,176,137.9688,180,147.9688,176,143.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="176" x2="176" y1="62" y2="221.4375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="176" x2="106" y1="62" y2="62"></line><polygon fill="#181818" points="116,58,106,62,116,66,112,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="189.4375" y2="209.4375"></line><polygon fill="#181818" points="90,199.4375,94,209.4375,98,199.4375,94,203.4375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="276.9922" y2="276.9922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="276.9922" y2="298.9922"></line><polygon fill="#181818" points="38.5,288.9922,42.5,298.9922,46.5,288.9922,42.5,292.9922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="276.9922" y2="276.9922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="276.9922" y2="298.9922"></line><polygon fill="#181818" points="141.5,288.9922,145.5,298.9922,149.5,288.9922,145.5,292.9922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="332.9609" y2="350.9609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="350.9609" y2="350.9609"></line><polygon fill="#181818" points="72,346.9609,82,350.9609,72,354.9609,76,350.9609" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="332.9609" y2="350.9609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="350.9609" y2="350.9609"></line><polygon fill="#181818" points="116,346.9609,106,350.9609,116,354.9609,112,350.9609" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="233.4375" y2="264.9922"></line><polygon fill="#181818" points="90,254.9922,94,264.9922,98,254.9922,94,258.9922" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,264.9922,123.5,264.9922,135.5,276.9922,123.5,288.9922,64.5,288.9922,52.5,276.9922,64.5,264.9922" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
  :read data;
  :generate diagrams;
repeat while (more data?) is (yes) not (no)
@enduml"""
            assert response.data.decode("utf-8") == expected_puml
