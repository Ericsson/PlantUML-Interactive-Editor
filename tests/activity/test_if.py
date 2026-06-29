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

"""Tests for if/else statement creation, editing, deletion, and detach."""

from flask import json
from plantuml_gui.activity.if_statements import build_tree


class TestAppRoutesIf:
    def test_build_tree(self):
        lines = """@startuml
:Activity 1;
if (st0) then (yes)
    if (st1) then (yes)
        :activity 2;
    else (no)
    endif
    if (st2) then (yes)
        if (st3) then (yes)
        else (no)
            :activity 3;
        endif
    else (no)
    endif
    :activity 4;
endif
@enduml""".splitlines()
        output = [3, 8, 7, 2]
        assert build_tree(lines) == output

    def test_addforkrightbranchinsiderepeat(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
repeat while (hej) is (yes) not (no)
:activity;
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="64.5,94,123.5,94,135.5,106,123.5,118,64.5,118,52.5,106,64.5,94" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="109.6523" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="103.25" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="103.25" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="128"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="148.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="128"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="148.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,167.9688,106,179.9688,94,191.9688,82,179.9688,94,167.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="94,50,106,62,94,74,82,62,94,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="82,211.9688,106,211.9688,118,223.9688,106,235.9688,82,235.9688,70,223.9688,82,211.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="246.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="85.5" y="227.6211" style="pointer-events: none;">hej</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="118" y="221.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="267.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="288.4922" style="pointer-events: none;">activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="106" y2="106"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="106" y2="128"></line><polygon fill="#181818" points="38.5,118,42.5,128,46.5,118,42.5,122" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="106" y2="106"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="106" y2="128"></line><polygon fill="#181818" points="141.5,118,145.5,128,149.5,118,145.5,122" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="161.9688" y2="179.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="179.9688" y2="179.9688"></line><polygon fill="#181818" points="72,175.9688,82,179.9688,72,183.9688,76,179.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="161.9688" y2="179.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="179.9688" y2="179.9688"></line><polygon fill="#181818" points="116,175.9688,106,179.9688,116,183.9688,112,179.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="94"></line><polygon fill="#181818" points="90,84,94,94,98,84,94,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118" x2="191" y1="223.9688" y2="223.9688"></line><polygon fill="#181818" points="187,152.9844,191,142.9844,195,152.9844,191,148.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="191" y1="62" y2="223.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="106" y1="62" y2="62"></line><polygon fill="#181818" points="116,58,106,62,116,66,112,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="191.9688" y2="211.9688"></line><polygon fill="#181818" points="90,201.9688,94,211.9688,98,201.9688,94,205.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="235.9688" y2="267.5234"></line><polygon fill="#181818" points="90,257.5234,94,267.5234,98,257.5234,94,261.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,94,123.5,94,135.5,106,123.5,118,64.5,118,52.5,106,64.5,94" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
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
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
fork
:action;
fork again
:action;
end fork
endif
repeat while (hej) is (yes) not (no)
:activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addforkrightbranch(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="56.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="66.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="119.9375">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="94,138.9375,106,150.9375,94,162.9375,82,150.9375,94,138.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="38.5,88.9688,42.5,98.9688,46.5,88.9688,42.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="141.5,88.9688,145.5,98.9688,149.5,88.9688,145.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="72,146.9375,82,150.9375,72,154.9375,76,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="116,146.9375,106,150.9375,116,154.9375,112,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="90,54.9688,94,64.9688,98,54.9688,94,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
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
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
fork
:action;
fork again
:action;
end fork
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addrepeatleftbranch(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="56.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="66.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="119.9375">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="94,138.9375,106,150.9375,94,162.9375,82,150.9375,94,138.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="38.5,88.9688,42.5,98.9688,46.5,88.9688,42.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="141.5,88.9688,145.5,98.9688,149.5,88.9688,145.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="72,146.9375,82,150.9375,72,154.9375,76,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="116,146.9375,106,150.9375,116,154.9375,112,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="90,54.9688,94,64.9688,98,54.9688,94,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "where": "left",
            "type": "repeat",
        }
        with client:
            response = client.post(
                "/addToIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
repeat
:Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
else (no)
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_toggledetach2(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="56.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="66.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="119.9375">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="94,138.9375,106,150.9375,94,162.9375,82,150.9375,94,138.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="38.5,88.9688,42.5,98.9688,46.5,88.9688,42.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="141.5,88.9688,145.5,98.9688,149.5,88.9688,145.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="72,146.9375,82,150.9375,72,154.9375,76,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="116,146.9375,106,150.9375,116,154.9375,112,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="90,54.9688,94,64.9688,98,54.9688,94,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/detachIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_toggledetach(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="56.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="66.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="119.9375">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="94,138.9375,106,150.9375,94,162.9375,82,150.9375,94,138.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="38.5,88.9688,42.5,98.9688,46.5,88.9688,42.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="141.5,88.9688,145.5,98.9688,149.5,88.9688,145.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="72,146.9375,82,150.9375,72,154.9375,76,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="116,146.9375,106,150.9375,116,154.9375,112,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="90,54.9688,94,64.9688,98,54.9688,94,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/detachIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
detach
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_editifwithwhileabove(self, client):
        test_data = {
            "plantuml": """@startuml
start
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
stop
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="69" y="105.5547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="79" y="126.5234" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="56,50,132,50,144,62,132,74,56,74,44,62,56,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="98" y="84.0547" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="56" y="65.6523" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="29" y="59.25" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="49.5" y="181.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="59.5" y="202.4922" style="pointer-events: none;">hello again</text><polygon fill="#F1F1F1" points="64.5,235.4922,123.5,235.4922,135.5,247.4922,123.5,259.4922,64.5,259.4922,52.5,247.4922,64.5,235.4922" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="251.1445" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="244.7422" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="244.7422" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="269.4922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="290.4609" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="269.4922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="290.4609" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,309.4609,106,321.4609,94,333.4609,82,321.4609,94,309.4609" style="stroke:#181818;stroke-width:0.5;"></polygon><ellipse cx="94" cy="364.4609" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="94" cy="364.4609" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="105.5547"></line><polygon fill="#181818" points="90,95.5547,94,105.5547,98,95.5547,94,99.5547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="139.5234" y2="149.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="156" y1="149.5234" y2="149.5234"></line><polygon fill="#181818" points="152,114.1367,156,104.1367,160,114.1367,156,110.1367" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="156" x2="156" y1="62" y2="149.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="156" x2="144" y1="62" y2="62"></line><polygon fill="#181818" points="154,58,144,62,154,66,150,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="32" y1="62" y2="62"></line><polygon fill="#181818" points="28,100.1367,32,110.1367,36,100.1367,32,104.1367" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="32" x2="32" y1="62" y2="161.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="32" x2="94" y1="161.5234" y2="161.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="161.5234" y2="181.5234"></line><polygon fill="#181818" points="90,171.5234,94,181.5234,98,171.5234,94,175.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="247.4922" y2="247.4922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="247.4922" y2="269.4922"></line><polygon fill="#181818" points="38.5,259.4922,42.5,269.4922,46.5,259.4922,42.5,263.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="247.4922" y2="247.4922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="247.4922" y2="269.4922"></line><polygon fill="#181818" points="141.5,259.4922,145.5,269.4922,149.5,259.4922,145.5,263.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="303.4609" y2="321.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="321.4609" y2="321.4609"></line><polygon fill="#181818" points="72,317.4609,82,321.4609,72,325.4609,76,321.4609" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="303.4609" y2="321.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="321.4609" y2="321.4609"></line><polygon fill="#181818" points="116,317.4609,106,321.4609,116,325.4609,112,321.4609" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="215.4922" y2="235.4922"></line><polygon fill="#181818" points="90,225.4922,94,235.4922,98,225.4922,94,229.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="333.4609" y2="353.4609"></line><polygon fill="#181818" points="90,343.4609,94,353.4609,98,343.4609,94,347.4609" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "State",
            "branch1": "bam",
            "branch2": "bom",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,235.4922,123.5,235.4922,135.5,247.4922,123.5,259.4922,64.5,259.4922,52.5,247.4922,64.5,235.4922" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
if (State) then (bam)
  :Activity;
else (bom)
  :Activity;
endif
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_gettextpolynobranch(self, client):
        test_data = {
            "plantuml": """@startuml
if (Statement) then (yes)
  :Activity;
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="58.4023"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="79.3711">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="127.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="148.3398">Activity</text><polygon fill="#F1F1F1" points="32,10,91,10,103,22,91,34,32,34,20,22,32,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="65.5" y="44.0547">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="32" y="25.6523">Statement</text><polygon fill="#F1F1F1" points="61.5,181.3398,73.5,193.3398,61.5,205.3398,49.5,193.3398,61.5,181.3398" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="92.3711" y2="127.3711"></line><polygon fill="#181818" points="57.5,117.3711,61.5,127.3711,65.5,117.3711,61.5,121.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="34" y2="58.4023"></line><polygon fill="#181818" points="57.5,48.4023,61.5,58.4023,65.5,48.4023,61.5,52.4023" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="103" x2="115" y1="22" y2="22"></line><polygon fill="#181818" points="111,99.8711,115,109.8711,119,99.8711,115,103.8711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="115" y1="22" y2="193.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="73.5" y1="193.3398" y2="193.3398"></line><polygon fill="#181818" points="83.5,189.3398,73.5,193.3398,83.5,197.3398,79.5,193.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="161.3398" y2="181.3398"></line><polygon fill="#181818" points="57.5,171.3398,61.5,181.3398,65.5,171.3398,61.5,175.3398" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,10,91,10,103,22,91,34,32,34,20,22,32,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getTextPoly",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = ["Statement", "yes"]
            assert json.loads(response.data.decode("utf-8")) == expected_result

    def test_editnoelsebranchempty(self, client):
        test_data = {
            "plantuml": """@startuml
if (Statement) then (yes)
  :Activity;
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="58.4023"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="79.3711">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="127.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="148.3398">Activity</text><polygon fill="#F1F1F1" points="32,10,91,10,103,22,91,34,32,34,20,22,32,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="65.5" y="44.0547">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="32" y="25.6523">Statement</text><polygon fill="#F1F1F1" points="61.5,181.3398,73.5,193.3398,61.5,205.3398,49.5,193.3398,61.5,181.3398" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="92.3711" y2="127.3711"></line><polygon fill="#181818" points="57.5,117.3711,61.5,127.3711,65.5,117.3711,61.5,121.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="34" y2="58.4023"></line><polygon fill="#181818" points="57.5,48.4023,61.5,58.4023,65.5,48.4023,61.5,52.4023" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="103" x2="115" y1="22" y2="22"></line><polygon fill="#181818" points="111,99.8711,115,109.8711,119,99.8711,115,103.8711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="115" y1="22" y2="193.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="73.5" y1="193.3398" y2="193.3398"></line><polygon fill="#181818" points="83.5,189.3398,73.5,193.3398,83.5,197.3398,79.5,193.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="161.3398" y2="181.3398"></line><polygon fill="#181818" points="57.5,171.3398,61.5,181.3398,65.5,171.3398,61.5,175.3398" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "Statement",
            "branch1": "yes",
            "branch2": "",
            "svgelement": """<polygon fill="#F1F1F1" points="32,10,91,10,103,22,91,34,32,34,20,22,32,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
if (Statement) then (yes)
  :Activity;
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_editnoelsebranch(self, client):
        test_data = {
            "plantuml": """@startuml
if (Statement) then (yes)
  :Activity;
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="58.4023"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="79.3711">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="127.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="148.3398">Activity</text><polygon fill="#F1F1F1" points="32,10,91,10,103,22,91,34,32,34,20,22,32,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="65.5" y="44.0547">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="32" y="25.6523">Statement</text><polygon fill="#F1F1F1" points="61.5,181.3398,73.5,193.3398,61.5,205.3398,49.5,193.3398,61.5,181.3398" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="92.3711" y2="127.3711"></line><polygon fill="#181818" points="57.5,117.3711,61.5,127.3711,65.5,117.3711,61.5,121.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="34" y2="58.4023"></line><polygon fill="#181818" points="57.5,48.4023,61.5,58.4023,65.5,48.4023,61.5,52.4023" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="103" x2="115" y1="22" y2="22"></line><polygon fill="#181818" points="111,99.8711,115,109.8711,119,99.8711,115,103.8711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="115" y1="22" y2="193.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="73.5" y1="193.3398" y2="193.3398"></line><polygon fill="#181818" points="83.5,189.3398,73.5,193.3398,83.5,197.3398,79.5,193.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="161.3398" y2="181.3398"></line><polygon fill="#181818" points="57.5,171.3398,61.5,181.3398,65.5,171.3398,61.5,175.3398" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "Statement",
            "branch1": "yes",
            "branch2": "right",
            "svgelement": """<polygon fill="#F1F1F1" points="32,10,91,10,103,22,91,34,32,34,20,22,32,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
if (Statement) then (yes)
  :Activity;
  :Activity;
else (right)
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addleftifnested(self, client):
        test_data = {
            "plantuml": """@startuml
:activity;
if (Statement) then (yes)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
else (no)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="165.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="175.5" y="31.9688" style="pointer-events: none;">activity</text><polygon fill="#F1F1F1" points="167.5,64.9688,226.5,64.9688,238.5,76.9688,226.5,88.9688,167.5,88.9688,155.5,76.9688,167.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="167.5" y="80.6211" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="135.5" y="74.2188" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="238.5" y="74.2188" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="119.9375" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="64.5,152.9375,123.5,152.9375,135.5,164.9375,123.5,176.9375,64.5,176.9375,52.5,164.9375,64.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="168.5898" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="162.1875" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="162.1875" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="207.9063" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="207.9063" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,226.9063,106,238.9063,94,250.9063,82,238.9063,94,226.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="268.5" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="278.5" y="119.9375" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="270.5,152.9375,329.5,152.9375,341.5,164.9375,329.5,176.9375,270.5,176.9375,258.5,164.9375,270.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="270.5" y="168.5898" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="238.5" y="162.1875" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="341.5" y="162.1875" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="217" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="227" y="207.9063" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="320" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="330" y="207.9063" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="300,226.9063,312,238.9063,300,250.9063,288,238.9063,300,226.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="197,256.9063,209,268.9063,197,280.9063,185,268.9063,197,256.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="38.5,176.9375,42.5,186.9375,46.5,176.9375,42.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="141.5,176.9375,145.5,186.9375,149.5,176.9375,145.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="72,234.9063,82,238.9063,72,242.9063,76,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="116,234.9063,106,238.9063,116,242.9063,112,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="132.9375" y2="152.9375"></line><polygon fill="#181818" points="90,142.9375,94,152.9375,98,142.9375,94,146.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="258.5" x2="248.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="248.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="244.5,176.9375,248.5,186.9375,252.5,176.9375,248.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="341.5" x2="351.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="347.5,176.9375,351.5,186.9375,355.5,176.9375,351.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="248.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="288" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="278,234.9063,288,238.9063,278,242.9063,282,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="312" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="322,234.9063,312,238.9063,322,242.9063,318,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="132.9375" y2="152.9375"></line><polygon fill="#181818" points="296,142.9375,300,152.9375,304,142.9375,300,146.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="155.5" x2="94" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="90,88.9688,94,98.9688,98,88.9688,94,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="238.5" x2="300" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="296,88.9688,300,98.9688,304,88.9688,300,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="250.9063" y2="268.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="185" y1="268.9063" y2="268.9063"></line><polygon fill="#181818" points="175,264.9063,185,268.9063,175,272.9063,179,268.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="250.9063" y2="268.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="209" y1="268.9063" y2="268.9063"></line><polygon fill="#181818" points="219,264.9063,209,268.9063,219,272.9063,215,268.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="197" x2="197" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="193,54.9688,197,64.9688,201,54.9688,197,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="167.5,64.9688,226.5,64.9688,238.5,76.9688,226.5,88.9688,167.5,88.9688,155.5,76.9688,167.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "where": "left",
            "type": "if",
        }
        with client:
            response = client.post(
                "/addToIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:activity;
if (Statement) then (yes)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
if (Statement) then (yes)
:Activity;
else (no)
:Activity;
endif
else (no)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_get_if_line(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
detach
else (no)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="159.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="169.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="167.5,64.9688,226.5,64.9688,238.5,76.9688,226.5,88.9688,167.5,88.9688,155.5,76.9688,167.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="167.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="135.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="238.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="64.5,152.9375,123.5,152.9375,135.5,164.9375,123.5,176.9375,64.5,176.9375,52.5,164.9375,64.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="168.5898">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="162.1875">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="162.1875">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="207.9063">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="207.9063">Activity</text><polygon fill="#F1F1F1" points="94,226.9063,106,238.9063,94,250.9063,82,238.9063,94,226.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="268.5" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="278.5" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="270.5,152.9375,329.5,152.9375,341.5,164.9375,329.5,176.9375,270.5,176.9375,258.5,164.9375,270.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="270.5" y="168.5898">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="238.5" y="162.1875">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="341.5" y="162.1875">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="217" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="227" y="207.9063">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="320" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="330" y="207.9063">Activity</text><polygon fill="#F1F1F1" points="300,226.9063,312,238.9063,300,250.9063,288,238.9063,300,226.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="197,256.9063,209,268.9063,197,280.9063,185,268.9063,197,256.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="38.5,176.9375,42.5,186.9375,46.5,176.9375,42.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="141.5,176.9375,145.5,186.9375,149.5,176.9375,145.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="72,234.9063,82,238.9063,72,242.9063,76,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="116,234.9063,106,238.9063,116,242.9063,112,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="132.9375" y2="152.9375"></line><polygon fill="#181818" points="90,142.9375,94,152.9375,98,142.9375,94,146.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="258.5" x2="248.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="248.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="244.5,176.9375,248.5,186.9375,252.5,176.9375,248.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="341.5" x2="351.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="347.5,176.9375,351.5,186.9375,355.5,176.9375,351.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="248.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="288" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="278,234.9063,288,238.9063,278,242.9063,282,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="312" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="322,234.9063,312,238.9063,322,242.9063,318,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="132.9375" y2="152.9375"></line><polygon fill="#181818" points="296,142.9375,300,152.9375,304,142.9375,300,146.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="155.5" x2="94" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="90,88.9688,94,98.9688,98,88.9688,94,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="238.5" x2="300" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="296,88.9688,300,98.9688,304,88.9688,300,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="250.9063" y2="268.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="185" y1="268.9063" y2="268.9063"></line><polygon fill="#181818" points="175,264.9063,185,268.9063,175,272.9063,179,268.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="250.9063" y2="268.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="209" y1="268.9063" y2="268.9063"></line><polygon fill="#181818" points="219,264.9063,209,268.9063,219,272.9063,215,268.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="197" x2="197" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="193,54.9688,197,64.9688,201,54.9688,197,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,152.9375,123.5,152.9375,135.5,164.9375,123.5,176.9375,64.5,176.9375,52.5,164.9375,64.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getIfLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = [4, 6, 8]

            # Assert the result value is as expected
            assert result_value == expected_puml

    def test_get_if_line2(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
  :Activity;
  backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<ellipse cx="51.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="114.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,50,63.5,62,51.5,74,39.5,62,51.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,157.9688,71,157.9688,83,169.9688,71,181.9688,32,181.9688,20,169.9688,32,157.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="192.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="173.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="167.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="107" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="117" y="114.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="213.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="234.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="74" y2="94"></line><polygon fill="#181818" points="47.5,84,51.5,94,55.5,84,51.5,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="138.5" y1="169.9688" y2="169.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="138.5" y1="127.9688" y2="169.9688"></line><polygon fill="#181818" points="134.5,137.9688,138.5,127.9688,142.5,137.9688,138.5,133.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="138.5" y1="62" y2="94"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="63.5" y1="62" y2="62"></line><polygon fill="#181818" points="73.5,58,63.5,62,73.5,66,69.5,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="127.9688" y2="157.9688"></line><polygon fill="#181818" points="47.5,147.9688,51.5,157.9688,55.5,147.9688,51.5,151.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="30" y2="50"></line><polygon fill="#181818" points="47.5,40,51.5,50,55.5,40,51.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="181.9688" y2="213.5234"></line><polygon fill="#181818" points="47.5,203.5234,51.5,213.5234,55.5,203.5234,51.5,207.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,157.9688,71,157.9688,83,169.9688,71,181.9688,32,181.9688,20,169.9688,32,157.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getIfLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = 5

            # Assert the result value is as expected
            assert result_value == expected_puml

    def test_get_if_line3(self, client):
        test_data = {
            "plantuml": """@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
case ( condition 2)
    :Activity;
endswitch
@enduml""",
            "svg": """<ellipse cx="118.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="104.5,50,132.5,50,144.5,62,132.5,74,104.5,74,92.5,62,104.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="104.5" y="65.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="130.748" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="128.5" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="138.5" y="130.748" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="118.5,153.5781,118.5,153.5781,130.5,165.5781,118.5,177.5781,118.5,177.5781,106.5,165.5781,118.5,153.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="92.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="109.6094"></line><polygon fill="#181818" points="38.5,99.6094,42.5,109.6094,46.5,99.6094,42.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="46.5" y="89.6128">condition 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="144.5" x2="160" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="62" y2="109.6094"></line><polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="164" y="89.6128">condition 2</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="106.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="96.5,161.5781,106.5,165.5781,96.5,169.5781,100.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="130.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="140.5,161.5781,130.5,165.5781,140.5,169.5781,136.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="118.5" y1="30" y2="50"></line><polygon fill="#181818" points="114.5,40,118.5,50,122.5,40,118.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="104.5,50,132.5,50,144.5,62,132.5,74,104.5,74,92.5,62,104.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getIfLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = [2, 7]

            # Assert the result value is as expected
            assert result_value == expected_puml

    def test_deleterepeatweirdnest(self, client):
        test_data = {
            "plantuml": """@startuml

start
if ( 8. IUPF is selected or not in step 4) then (yes)
    :PFCP Session Establishment Request with IUPF;
    repeat
        :Start T1 timer;
        if (Wait) then (PFCP Session Establishment Response)
            break
        endif
        -> T1 Timeout;
        backward:9. Retransmit PFCP Session Establishment Request with IUPF;
    repeat while (Number of retries < N1?) is (Yes) not (No)
    if (PFCP Session Establishment Positive Response?) then (No)
        :5.- Nsmf_PDUSession_CreateSMContext Negative Response
        - Release session without sending N1N2 to AMF;
        stop
    endif
    -> Yes;
endif
:10. Nsmf_PDUSession_CreateSMContext Response with hoState == PREPARING;
: Start Tsrn2 Timer;
repeat
    if (Wait) then (Tsrn2 timeout)
        :11. Start t4to5ho timer;
        if (Wait) then (t4to5ho timeout)
            :12. Release Session;
            stop
        else (Nsmf_PDUSession_UpdateSMContext Request \n hoState == CANCELLED)
            :13. Rollback to EPS;
            stop
        endif
    else (Nsmf_PDUSession_UpdateSMContext Request)
    endif
    backward: 14. Nsmf_PDUSession_UpdateSMContext Negative Response;
repeat while (Message format is valid?) is (No) not (Yes)
:Activity;
@enduml""",
            "svg": """<ellipse cx="269" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="313" x="112.5" y="98.4023"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="293" x="122.5" y="119.3711" style="pointer-events: none;">PFCP Session Establishment Request with IUPF</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="106" x="216" y="196.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="86" x="226" y="217.3398" style="pointer-events: none;">Start T1 timer</text><polygon fill="#F1F1F1" points="257,252.4063,281,252.4063,293,264.4063,281,276.4063,257,276.4063,245,264.4063,257,252.4063" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="223" x="273" y="286.4609" style="pointer-events: none;">PFCP Session Establishment Response</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="23" x="257.5" y="268.0586" style="pointer-events: none;">Wait</text><polygon fill="#F1F1F1" points="269,152.3711,281,164.3711,269,176.3711,257,164.3711,269,152.3711" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="199,361.4609,339,361.4609,351,373.4609,339,385.4609,199,385.4609,187,373.4609,199,361.4609" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="273" y="395.5156" style="pointer-events: none;">No</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="140" x="199" y="377.1133" style="pointer-events: none;">Number of retries &lt; N1?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="351" y="370.7109" style="pointer-events: none;">Yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="401" x="375" y="240.3398"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="381" x="385" y="261.3086" style="pointer-events: none;">9. Retransmit PFCP Session Establishment Request with IUPF</text><polygon fill="#F1F1F1" points="269,417.0156,281,429.0156,269,441.0156,257,429.0156,269,417.0156" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="47.9375" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="391" x="73.5" y="509.418"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="371" x="83.5" y="530.3867" style="pointer-events: none;">5.- Nsmf_PDUSession_CreateSMContext Negative Response</text><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="83.5" y="544.3555" style="pointer-events: none;">- Release session without sending N1N2 to AMF</text><ellipse cx="269" cy="589.8867" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="269" cy="589.8867" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="130.5,461.0156,407.5,461.0156,419.5,473.0156,407.5,485.0156,130.5,485.0156,118.5,473.0156,130.5,461.0156" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="273" y="495.0703" style="pointer-events: none;">No</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="277" x="130.5" y="476.668" style="pointer-events: none;">PFCP Session Establishment Positive Response?</text><polygon fill="#F1F1F1" points="168.5,50,369.5,50,381.5,62,369.5,74,168.5,74,156.5,62,168.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="273" y="84.0547" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="197" x="172.5" y="65.6523" style="pointer-events: none;">8. IUPF is selected or not in step 4</text><polygon fill="#F1F1F1" points="269,646.9414,281,658.9414,269,670.9414,257,658.9414,269,646.9414" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="275" y="644.1914" style="pointer-events: none;">Yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="516" x="11" y="690.9414"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="496" x="21" y="711.9102" style="pointer-events: none;">10. Nsmf_PDUSession_CreateSMContext Response with hoState == PREPARING</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="132" x="203" y="744.9102"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="108" x="217" y="765.8789" style="pointer-events: none;">Start Tsrn2 Timer</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="165" x="186.5" y="891.2813"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="145" x="196.5" y="912.25" style="pointer-events: none;">11. Start t4to5ho timer</text><polygon fill="#F1F1F1" points="257,950.1094,281,950.1094,293,962.1094,281,974.1094,257,974.1094,245,962.1094,257,950.1094" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="23" x="257.5" y="965.7617" style="pointer-events: none;">Wait</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="90" x="155" y="959.3594" style="pointer-events: none;">t4to5ho timeout</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="261" x="293" y="946.5547" style="pointer-events: none;">Nsmf_PDUSession_UpdateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="135" x="297" y="959.3594" style="pointer-events: none;">hoState == CANCELLED</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="147" x="113.5" y="984.1094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="127" x="123.5" y="1005.0781" style="pointer-events: none;">12. Release Session</text><ellipse cx="187" cy="1049.0781" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="187" cy="1049.0781" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="141" x="280.5" y="984.1094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="121" x="290.5" y="1005.0781" style="pointer-events: none;">13. Rollback to EPS</text><ellipse cx="351" cy="1049.0781" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="351" cy="1049.0781" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="257,842.8789,281,842.8789,293,854.8789,281,866.8789,257,866.8789,245,854.8789,257,842.8789" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="80" x="273" y="876.9336" style="pointer-events: none;">Tsrn2 timeout</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="23" x="257.5" y="858.5313" style="pointer-events: none;">Wait</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="261" x="293" y="852.1289" style="pointer-events: none;">Nsmf_PDUSession_UpdateSMContext Request</text><polygon fill="#F1F1F1" points="269,798.8789,281,810.8789,269,822.8789,257,810.8789,269,798.8789" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="197.5,1102.0781,340.5,1102.0781,352.5,1114.0781,340.5,1126.0781,197.5,1126.0781,185.5,1114.0781,197.5,1102.0781" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="273" y="1136.1328" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="143" x="197.5" y="1117.7305" style="pointer-events: none;">Message format is valid?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="352.5" y="1111.3281" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="403" x="604" y="954.3203"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="379" x="618" y="975.2891" style="pointer-events: none;">14. Nsmf_PDUSession_UpdateSMContext Negative Response</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="237.5" y="1157.6328"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="247.5" y="1178.6016" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="276.4063" y2="300.8086"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="177" y1="300.8086" y2="300.8086"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="177" x2="177" y1="300.8086" y2="429.0156"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="177" x2="257" y1="429.0156" y2="429.0156"></line><polygon fill="#181818" points="247,425.0156,257,429.0156,247,433.0156,251,429.0156" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="293" x2="305" y1="264.4063" y2="264.4063"></line><polygon fill="#181818" points="301,287.8086,305,297.8086,309,287.8086,305,291.8086" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="305" x2="305" y1="264.4063" y2="319.8086"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="305" x2="269" y1="319.8086" y2="319.8086"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="230.3398" y2="252.4063"></line><polygon fill="#181818" points="265,242.4063,269,252.4063,273,242.4063,269,246.4063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="176.3711" y2="196.3711"></line><polygon fill="#181818" points="265,186.3711,269,196.3711,273,186.3711,269,190.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351" x2="575.5" y1="373.4609" y2="373.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="575.5" x2="575.5" y1="274.3086" y2="373.4609"></line><polygon fill="#181818" points="571.5,284.3086,575.5,274.3086,579.5,284.3086,575.5,280.3086" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="575.5" x2="575.5" y1="164.3711" y2="240.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="575.5" x2="281" y1="164.3711" y2="164.3711"></line><polygon fill="#181818" points="291,160.3711,281,164.3711,291,168.3711,287,164.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="319.8086" y2="361.4609"></line><polygon fill="#181818" points="265,351.4609,269,361.4609,273,351.4609,269,355.4609" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="64" x="273" y="341.1133">T1 Timeout</text><line style="stroke:#181818;stroke-width:1.0;" x1="269" x2="269" y1="385.4609" y2="417.0156"></line><polygon fill="#181818" points="265,407.0156,269,417.0156,273,407.0156,269,411.0156" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="132.3711" y2="152.3711"></line><polygon fill="#181818" points="265,142.3711,269,152.3711,273,142.3711,269,146.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="557.3555" y2="578.8867"></line><polygon fill="#181818" points="265,568.8867,269,578.8867,273,568.8867,269,572.8867" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="485.0156" y2="509.418"></line><polygon fill="#181818" points="265,499.418,269,509.418,273,499.418,269,503.418" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="419.5" x2="474.5" y1="473.0156" y2="473.0156"></line><polygon fill="#181818" points="470.5,548.8867,474.5,558.8867,478.5,548.8867,474.5,552.8867" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="474.5" x2="474.5" y1="473.0156" y2="622.8867"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="474.5" x2="269" y1="622.8867" y2="622.8867"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="622.8867" y2="646.9414"></line><polygon fill="#181818" points="265,636.9414,269,646.9414,273,636.9414,269,640.9414" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="441.0156" y2="461.0156"></line><polygon fill="#181818" points="265,451.0156,269,461.0156,273,451.0156,269,455.0156" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="74" y2="98.4023"></line><polygon fill="#181818" points="265,88.4023,269,98.4023,273,88.4023,269,92.4023" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="381.5" x2="786" y1="62" y2="62"></line><polygon fill="#181818" points="782,340.3633,786,350.3633,790,340.3633,786,344.3633" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="786" x2="786" y1="62" y2="658.9414"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="786" x2="281" y1="658.9414" y2="658.9414"></line><polygon fill="#181818" points="291,654.9414,281,658.9414,291,662.9414,287,658.9414" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="30" y2="50"></line><polygon fill="#181818" points="265,40,269,50,273,40,269,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="670.9414" y2="690.9414"></line><polygon fill="#181818" points="265,680.9414,269,690.9414,273,680.9414,269,684.9414" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="724.9102" y2="744.9102"></line><polygon fill="#181818" points="265,734.9102,269,744.9102,273,734.9102,269,738.9102" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="187" x2="187" y1="1018.0781" y2="1038.0781"></line><polygon fill="#181818" points="183,1028.0781,187,1038.0781,191,1028.0781,187,1032.0781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351" x2="351" y1="1018.0781" y2="1038.0781"></line><polygon fill="#181818" points="347,1028.0781,351,1038.0781,355,1028.0781,351,1032.0781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="245" x2="187" y1="962.1094" y2="962.1094"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="187" x2="187" y1="962.1094" y2="984.1094"></line><polygon fill="#181818" points="183,974.1094,187,984.1094,191,974.1094,187,978.1094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="293" x2="351" y1="962.1094" y2="962.1094"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351" x2="351" y1="962.1094" y2="984.1094"></line><polygon fill="#181818" points="347,974.1094,351,984.1094,355,974.1094,351,978.1094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="925.25" y2="950.1094"></line><polygon fill="#181818" points="265,940.1094,269,950.1094,273,940.1094,269,944.1094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="866.8789" y2="891.2813"></line><polygon fill="#181818" points="265,881.2813,269,891.2813,273,881.2813,269,885.2813" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="293" x2="568" y1="854.8789" y2="854.8789"></line><polygon fill="#181818" points="564,967.3047,568,977.3047,572,967.3047,568,971.3047" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="568" x2="568" y1="854.8789" y2="1082.0781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="568" x2="269" y1="1082.0781" y2="1082.0781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="1082.0781" y2="1102.0781"></line><polygon fill="#181818" points="265,1092.0781,269,1102.0781,273,1092.0781,269,1096.0781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="822.8789" y2="842.8789"></line><polygon fill="#181818" points="265,832.8789,269,842.8789,273,832.8789,269,836.8789" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="352.5" x2="805.5" y1="1114.0781" y2="1114.0781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="805.5" x2="805.5" y1="988.2891" y2="1114.0781"></line><polygon fill="#181818" points="801.5,998.2891,805.5,988.2891,809.5,998.2891,805.5,994.2891" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="805.5" x2="805.5" y1="810.8789" y2="954.3203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="805.5" x2="281" y1="810.8789" y2="810.8789"></line><polygon fill="#181818" points="291,806.8789,281,810.8789,291,814.8789,287,810.8789" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="778.8789" y2="798.8789"></line><polygon fill="#181818" points="265,788.8789,269,798.8789,273,788.8789,269,792.8789" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="1126.0781" y2="1157.6328"></line><polygon fill="#181818" points="265,1147.6328,269,1157.6328,273,1147.6328,269,1151.6328" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="197.5,1102.0781,340.5,1102.0781,352.5,1114.0781,340.5,1126.0781,197.5,1126.0781,185.5,1114.0781,197.5,1102.0781" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml

start
if ( 8. IUPF is selected or not in step 4) then (yes)
    :PFCP Session Establishment Request with IUPF;
    repeat
        :Start T1 timer;
        if (Wait) then (PFCP Session Establishment Response)
            break
        endif
        -> T1 Timeout;
        backward:9. Retransmit PFCP Session Establishment Request with IUPF;
    repeat while (Number of retries < N1?) is (Yes) not (No)
    if (PFCP Session Establishment Positive Response?) then (No)
        :5.- Nsmf_PDUSession_CreateSMContext Negative Response
        - Release session without sending N1N2 to AMF;
        stop
    endif
    -> Yes;
endif
:10. Nsmf_PDUSession_CreateSMContext Response with hoState == PREPARING;
: Start Tsrn2 Timer;
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifstatementnested2(self, client):
        test_data = {
            "plantuml": """@startuml
if (hoState) then (hoState == PREPARED)
    if (Check N2 IE) then (N2 Handover Request Acknowledge Transfer)
        if (Default QoS flow in QoSFlowSetupResponseList IE?) then (Yes)
        else (No)
            :15.  Nsmf_PDUSession_UpdateSMContext Negative Response;
            :Start t4to5ho timer;
            if (Wait) then (t4to5ho Timeout)
                :16 Release Session;
                stop
            else (Nsmf_PDUSession_UpdateSMContext Request \n hoState == CANCELLED)
                :13. Rollback to EPS;
                stop
            endif
        endif
        :17. Handle optional AMF Change;
        :18. Nsmf_PDUSession_UpdateSMContext Response with hoState == PREPARED;
    else (N2 Handover Resource Allocation Unsuccessful Transfer)
        :19.  Nsmf_PDUSession_UpdateSMContext Negative Response;
        : Start t4to5ho timer;
        if (Wait) then (t4to5ho Timeout)
            :20. Release Session;
            stop
        else (Nsmf_PDUSession_UpdateSMContext Request \n hoState == CANCELLED)
            :13. Rollback to EPS;
            stop
        endif
    endif
else (hoState == CANCELLED)
    : 13. Rollback to EPS;
    stop
endif
end
@enduml""",
            "svg": """<polygon fill="#F1F1F1" points="842.125,12.0547,886.125,12.0547,898.125,24.0547,886.125,36.0547,842.125,36.0547,830.125,24.0547,842.125,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="44" x="842.125" y="27.707" style="pointer-events: none;">hoState</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="127" x="703.125" y="21.3047" style="pointer-events: none;">hoState == PREPARED</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="135" x="898.125" y="21.3047" style="pointer-events: none;">hoState == CANCELLED</text><polygon fill="#F1F1F1" points="501.75,46.0547,568.75,46.0547,580.75,58.0547,568.75,70.0547,501.75,70.0547,489.75,58.0547,501.75,46.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="67" x="501.75" y="61.707" style="pointer-events: none;">Check N2 IE</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="253" x="236.75" y="55.3047" style="pointer-events: none;">N2 Handover Request Acknowledge Transfer</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="321" x="580.75" y="55.3047" style="pointer-events: none;">N2 Handover Resource Allocation Unsuccessful Transfer</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="403" x="67.5" y="128.457"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="383" x="77.5" y="149.4258" style="pointer-events: none;">15.  Nsmf_PDUSession_UpdateSMContext Negative Response</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="141" x="198.5" y="197.4258"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="121" x="208.5" y="218.3945" style="pointer-events: none;">Start t4to5ho timer</text><polygon fill="#F1F1F1" points="257,268.0039,281,268.0039,293,280.0039,281,292.0039,257,292.0039,245,280.0039,257,268.0039" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="23" x="257.5" y="283.6563" style="pointer-events: none;">Wait</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="93" x="152" y="277.2539" style="pointer-events: none;">t4to5ho Timeout</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="261" x="293" y="264.4492" style="pointer-events: none;">Nsmf_PDUSession_UpdateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="135" x="297" y="277.2539" style="pointer-events: none;">hoState == CANCELLED</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="143" x="116.5" y="302.0039"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="123" x="126.5" y="322.9727" style="pointer-events: none;">16 Release Session</text><ellipse cx="188" cy="375.5703" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="188" cy="375.5703" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="141" x="279.5" y="302.0039"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="121" x="289.5" y="322.9727" style="pointer-events: none;">13. Rollback to EPS</text><ellipse cx="350" cy="375.5703" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="350" cy="375.5703" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="123.5,80.0547,414.5,80.0547,426.5,92.0547,414.5,104.0547,123.5,104.0547,111.5,92.0547,123.5,80.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="273" y="114.1094" style="pointer-events: none;">No</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="291" x="123.5" y="95.707" style="pointer-events: none;">Default QoS flow in QoSFlowSetupResponseList IE?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="426.5" y="89.3047" style="pointer-events: none;">Yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="224" x="157" y="428.5703"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="204" x="167" y="449.5391" style="pointer-events: none;">17. Handle optional AMF Change</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="516" x="11" y="482.5391"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="496" x="21" y="503.5078" style="pointer-events: none;">18. Nsmf_PDUSession_UpdateSMContext Response with hoState == PREPARED</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="403" x="600" y="80.0547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="383" x="610" y="101.0234" style="pointer-events: none;">19.  Nsmf_PDUSession_UpdateSMContext Negative Response</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="145" x="729" y="149.0234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="121" x="743" y="169.9922" style="pointer-events: none;">Start t4to5ho timer</text><polygon fill="#F1F1F1" points="789.5,219.6016,813.5,219.6016,825.5,231.6016,813.5,243.6016,789.5,243.6016,777.5,231.6016,789.5,219.6016" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="23" x="790" y="235.2539" style="pointer-events: none;">Wait</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="93" x="684.5" y="228.8516" style="pointer-events: none;">t4to5ho Timeout</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="261" x="825.5" y="216.0469" style="pointer-events: none;">Nsmf_PDUSession_UpdateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="135" x="829.5" y="228.8516" style="pointer-events: none;">hoState == CANCELLED</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="147" x="646" y="253.6016"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="127" x="656" y="274.5703" style="pointer-events: none;">20. Release Session</text><ellipse cx="719.5" cy="333.5703" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="719.5" cy="333.5703" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="141" x="813" y="253.6016"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="121" x="823" y="274.5703" style="pointer-events: none;">13. Rollback to EPS</text><ellipse cx="883.5" cy="333.5703" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="883.5" cy="333.5703" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="145" x="1100.5" y="46.0547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="121" x="1114.5" y="67.0234" style="pointer-events: none;">13. Rollback to EPS</text><ellipse cx="1173" cy="126.0234" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="1173" cy="126.0234" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><ellipse cx="864.125" cy="546.5078" fill="transparent" rx="10" ry="10" style="stroke:#222222;stroke-width:1.5;"></ellipse><line style="stroke: rgb(34, 34, 34); stroke-width: 2.5; pointer-events: none;" x1="857.9378" x2="870.3122" y1="540.3206" y2="552.695"></line><line style="stroke: rgb(34, 34, 34); stroke-width: 2.5; pointer-events: none;" x1="870.3122" x2="857.9378" y1="540.3206" y2="552.695"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="162.4258" y2="197.4258"></line><polygon fill="#181818" points="265,187.4258,269,197.4258,273,187.4258,269,191.4258" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="188" x2="188" y1="335.9727" y2="364.5703"></line><polygon fill="#181818" points="184,354.5703,188,364.5703,192,354.5703,188,358.5703" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="350" x2="350" y1="335.9727" y2="364.5703"></line><polygon fill="#181818" points="346,354.5703,350,364.5703,354,354.5703,350,358.5703" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="245" x2="188" y1="280.0039" y2="280.0039"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="188" x2="188" y1="280.0039" y2="302.0039"></line><polygon fill="#181818" points="184,292.0039,188,302.0039,192,292.0039,188,296.0039" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="293" x2="350" y1="280.0039" y2="280.0039"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="350" x2="350" y1="280.0039" y2="302.0039"></line><polygon fill="#181818" points="346,292.0039,350,302.0039,354,292.0039,350,296.0039" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="231.3945" y2="268.0039"></line><polygon fill="#181818" points="265,258.0039,269,268.0039,273,258.0039,269,262.0039" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="104.0547" y2="128.457"></line><polygon fill="#181818" points="265,118.457,269,128.457,273,118.457,269,122.457" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="426.5" x2="568" y1="92.0547" y2="92.0547"></line><polygon fill="#181818" points="564,250.7148,568,260.7148,572,250.7148,568,254.7148" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="568" x2="568" y1="92.0547" y2="408.5703"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="568" x2="269" y1="408.5703" y2="408.5703"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="408.5703" y2="428.5703"></line><polygon fill="#181818" points="265,418.5703,269,428.5703,273,418.5703,269,422.5703" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="462.5391" y2="482.5391"></line><polygon fill="#181818" points="265,472.5391,269,482.5391,273,472.5391,269,476.5391" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="801.5" x2="801.5" y1="114.0234" y2="149.0234"></line><polygon fill="#181818" points="797.5,139.0234,801.5,149.0234,805.5,139.0234,801.5,143.0234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="719.5" x2="719.5" y1="287.5703" y2="322.5703"></line><polygon fill="#181818" points="715.5,312.5703,719.5,322.5703,723.5,312.5703,719.5,316.5703" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="883.5" x2="883.5" y1="287.5703" y2="322.5703"></line><polygon fill="#181818" points="879.5,312.5703,883.5,322.5703,887.5,312.5703,883.5,316.5703" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="777.5" x2="719.5" y1="231.6016" y2="231.6016"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="719.5" x2="719.5" y1="231.6016" y2="253.6016"></line><polygon fill="#181818" points="715.5,243.6016,719.5,253.6016,723.5,243.6016,719.5,247.6016" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="825.5" x2="883.5" y1="231.6016" y2="231.6016"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="883.5" x2="883.5" y1="231.6016" y2="253.6016"></line><polygon fill="#181818" points="879.5,243.6016,883.5,253.6016,887.5,243.6016,883.5,247.6016" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="801.5" x2="801.5" y1="182.9922" y2="219.6016"></line><polygon fill="#181818" points="797.5,209.6016,801.5,219.6016,805.5,209.6016,801.5,213.6016" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="489.75" x2="269" y1="58.0547" y2="58.0547"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="58.0547" y2="80.0547"></line><polygon fill="#181818" points="265,70.0547,269,80.0547,273,70.0547,269,74.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="580.75" x2="801.5" y1="58.0547" y2="58.0547"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="801.5" x2="801.5" y1="58.0547" y2="80.0547"></line><polygon fill="#181818" points="797.5,70.0547,801.5,80.0547,805.5,70.0547,801.5,74.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="516.5078" y2="521.5078"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="864.125" y1="521.5078" y2="521.5078"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="864.125" x2="864.125" y1="521.5078" y2="536.5078"></line><polygon fill="#181818" points="860.125,526.5078,864.125,536.5078,868.125,526.5078,864.125,530.5078" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="1173" x2="1173" y1="80.0234" y2="115.0234"></line><polygon fill="#181818" points="1169,105.0234,1173,115.0234,1177,105.0234,1173,109.0234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="830.125" x2="535.25" y1="24.0547" y2="24.0547"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="535.25" x2="535.25" y1="24.0547" y2="46.0547"></line><polygon fill="#181818" points="531.25,36.0547,535.25,46.0547,539.25,36.0547,535.25,40.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="898.125" x2="1173" y1="24.0547" y2="24.0547"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="1173" x2="1173" y1="24.0547" y2="46.0547"></line><polygon fill="#181818" points="1169,36.0547,1173,46.0547,1177,36.0547,1173,40.0547" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="257,268.0039,281,268.0039,293,280.0039,281,292.0039,257,292.0039,245,280.0039,257,268.0039" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
if (hoState) then (hoState == PREPARED)
    if (Check N2 IE) then (N2 Handover Request Acknowledge Transfer)
        if (Default QoS flow in QoSFlowSetupResponseList IE?) then (Yes)
        else (No)
            :15.  Nsmf_PDUSession_UpdateSMContext Negative Response;
            :Start t4to5ho timer;
        endif
        :17. Handle optional AMF Change;
        :18. Nsmf_PDUSession_UpdateSMContext Response with hoState == PREPARED;
    else (N2 Handover Resource Allocation Unsuccessful Transfer)
        :19.  Nsmf_PDUSession_UpdateSMContext Negative Response;
        : Start t4to5ho timer;
        if (Wait) then (t4to5ho Timeout)
            :20. Release Session;
            stop
        else (Nsmf_PDUSession_UpdateSMContext Request \n hoState == CANCELLED)
            :13. Rollback to EPS;
            stop
        endif
    endif
else (hoState == CANCELLED)
    : 13. Rollback to EPS;
    stop
endif
end
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifstatementnestedemptyelse(self, client):
        test_data = {
            "plantuml": """@startuml
start
if (Statement) then (yes)
    :Activity;
    if (Statement) then (yes)
        :Activity;
    else (no)
        :Activity;
    endif
    :Activity;
else (no)
endif
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="98.4023"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="119.3711" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="64.5,152.3711,123.5,152.3711,135.5,164.3711,123.5,176.3711,64.5,176.3711,52.5,164.3711,64.5,152.3711" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="168.0234" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="161.6211" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="161.6211" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="186.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="207.3398" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="186.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="207.3398" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,226.3398,106,238.3398,94,250.3398,82,238.3398,94,226.3398" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="270.3398"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="291.3086" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="98" y="84.0547" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="65.6523" style="pointer-events: none;">Statement</text><polygon fill="#F1F1F1" points="94,324.3086,106,336.3086,94,348.3086,82,336.3086,94,324.3086" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="164.3711" y2="164.3711"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="164.3711" y2="186.3711"></line><polygon fill="#181818" points="38.5,176.3711,42.5,186.3711,46.5,176.3711,42.5,180.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="164.3711" y2="164.3711"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="164.3711" y2="186.3711"></line><polygon fill="#181818" points="141.5,176.3711,145.5,186.3711,149.5,176.3711,145.5,180.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="220.3398" y2="238.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="238.3398" y2="238.3398"></line><polygon fill="#181818" points="72,234.3398,82,238.3398,72,242.3398,76,238.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="220.3398" y2="238.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="238.3398" y2="238.3398"></line><polygon fill="#181818" points="116,234.3398,106,238.3398,116,242.3398,112,238.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="132.3711" y2="152.3711"></line><polygon fill="#181818" points="90,142.3711,94,152.3711,98,142.3711,94,146.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="250.3398" y2="270.3398"></line><polygon fill="#181818" points="90,260.3398,94,270.3398,98,260.3398,94,264.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="98.4023"></line><polygon fill="#181818" points="90,88.4023,94,98.4023,98,88.4023,94,92.4023" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="191" y1="62" y2="62"></line><polygon fill="#181818" points="187,191.3555,191,201.3555,195,191.3555,191,195.3555" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="191" y1="62" y2="336.3086"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="106" y1="336.3086" y2="336.3086"></line><polygon fill="#181818" points="116,332.3086,106,336.3086,116,340.3086,112,336.3086" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="304.3086" y2="324.3086"></line><polygon fill="#181818" points="90,314.3086,94,324.3086,98,314.3086,94,318.3086" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifstatementnestednoelse(self, client):
        test_data = {
            "plantuml": """@startuml
start
if (Statement) then (yes)
    :Activity;
    if (Statement) then (yes)
        :Activity;
    else (no)
        :Activity;
    endif
    :Activity;
endif
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="98.4023"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="119.3711" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="64.5,152.3711,123.5,152.3711,135.5,164.3711,123.5,176.3711,64.5,176.3711,52.5,164.3711,64.5,152.3711" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="168.0234" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="161.6211" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="161.6211" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="186.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="207.3398" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="186.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="207.3398" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,226.3398,106,238.3398,94,250.3398,82,238.3398,94,226.3398" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="270.3398"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="291.3086" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="98" y="84.0547" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="65.6523" style="pointer-events: none;">Statement</text><polygon fill="#F1F1F1" points="94,324.3086,106,336.3086,94,348.3086,82,336.3086,94,324.3086" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="164.3711" y2="164.3711"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="164.3711" y2="186.3711"></line><polygon fill="#181818" points="38.5,176.3711,42.5,186.3711,46.5,176.3711,42.5,180.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="164.3711" y2="164.3711"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="164.3711" y2="186.3711"></line><polygon fill="#181818" points="141.5,176.3711,145.5,186.3711,149.5,176.3711,145.5,180.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="220.3398" y2="238.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="238.3398" y2="238.3398"></line><polygon fill="#181818" points="72,234.3398,82,238.3398,72,242.3398,76,238.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="220.3398" y2="238.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="238.3398" y2="238.3398"></line><polygon fill="#181818" points="116,234.3398,106,238.3398,116,242.3398,112,238.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="132.3711" y2="152.3711"></line><polygon fill="#181818" points="90,142.3711,94,152.3711,98,142.3711,94,146.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="250.3398" y2="270.3398"></line><polygon fill="#181818" points="90,260.3398,94,270.3398,98,260.3398,94,264.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="98.4023"></line><polygon fill="#181818" points="90,88.4023,94,98.4023,98,88.4023,94,92.4023" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="191" y1="62" y2="62"></line><polygon fill="#181818" points="187,191.3555,191,201.3555,195,191.3555,191,195.3555" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="191" y1="62" y2="336.3086"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="106" y1="336.3086" y2="336.3086"></line><polygon fill="#181818" points="116,332.3086,106,336.3086,116,340.3086,112,336.3086" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="304.3086" y2="324.3086"></line><polygon fill="#181818" points="90,314.3086,94,324.3086,98,314.3086,94,318.3086" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifstatement_check_branch_cov(self, client):
        test_data = {
            "plantuml": """@startuml
start
if (Statement) then (yes)
    :Activity;
else (no)
    stop
endif
if (Statement) then (yes)
    stop
else (no)
    (A)
endif
end
@enduml""",
            "svg": """<g><ellipse cx="75.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="46,50,105,50,117,62,105,74,46,74,34,62,46,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="46" y="65.8081" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="14" y="59.4058" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="117" y="59.4058" style="pointer-events: none;">no</text><ellipse cx="24" cy="94" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M24.1094,90.1719 L22.5,94.5156 L25.7188,94.5156 L24.1094,90.1719 Z M23.4375,89 L24.7813,89 L28.1094,97.75 L26.875,97.75 L26.0781,95.5 L22.1406,95.5 L21.3438,97.75 L20.0938,97.75 L23.4375,89 Z " fill="#000000" style="pointer-events: none;"></path><ellipse cx="127" cy="95" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;fill:none;"></ellipse><ellipse cx="127" cy="95" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="46,126,105,126,117,138,105,150,46,150,34,138,46,126" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="46" y="141.8081" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="14" y="135.4058" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="117" y="135.4058" style="pointer-events: none;">no</text><ellipse cx="24" cy="171" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;fill:none;"></ellipse><ellipse cx="24" cy="171" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><ellipse cx="127" cy="170" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M127.1094,166.1719 L125.5,170.5156 L128.7188,170.5156 L127.1094,166.1719 Z M126.4375,165 L127.7813,165 L131.1094,173.75 L129.875,173.75 L129.0781,171.5 L125.1406,171.5 L124.3438,173.75 L123.0938,173.75 L126.4375,165 Z " fill="#000000" style="pointer-events: none;"></path><ellipse cx="75.5" cy="212" rx="10" ry="10" style="stroke:#222222;stroke-width:1.5;fill:transparent;" fill="transparent"></ellipse><line style="stroke: rgb(34, 34, 34); stroke-width: 2.5; fill: none; pointer-events: none;" x1="69.3128" x2="81.6872" y1="205.8128" y2="218.1872"></line><line style="stroke: rgb(34, 34, 34); stroke-width: 2.5; fill: none; pointer-events: none;" x1="81.6872" x2="69.3128" y1="205.8128" y2="218.1872"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; fill: none; pointer-events: none;" x1="34" x2="24" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; fill: none; pointer-events: none;" x1="24" x2="24" y1="62" y2="84"></line><polygon fill="#181818" points="20,74,24,84,28,74,24,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="117" x2="127" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="127" x2="127" y1="62" y2="84"></line><polygon fill="#181818" points="123,74,127,84,131,74,127,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="104" y2="111"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="75.5" y1="111" y2="111"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="75.5" x2="75.5" y1="111" y2="126"></line><polygon fill="#181818" points="71.5,116,75.5,126,79.5,116,75.5,120" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="75.5" x2="75.5" y1="30" y2="50"></line><polygon fill="#181818" points="71.5,40,75.5,50,79.5,40,75.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="34" x2="24" y1="138" y2="138"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="138" y2="160"></line><polygon fill="#181818" points="20,150,24,160,28,150,24,154" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="117" x2="127" y1="138" y2="138"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="127" x2="127" y1="138" y2="160"></line><polygon fill="#181818" points="123,150,127,160,131,150,127,154" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="127" x2="127" y1="180" y2="187"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="127" x2="75.5" y1="187" y2="187"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="75.5" x2="75.5" y1="187" y2="202"></line><polygon fill="#181818" points="71.5,192,75.5,202,79.5,192,75.5,196" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="46,126,105,126,117,138,105,150,46,150,34,138,46,126" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
if (Statement) then (yes)
    :Activity;
else (no)
    stop
endif
end
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifstatement(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
detach
else (no)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="159.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="169.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="167.5,64.9688,226.5,64.9688,238.5,76.9688,226.5,88.9688,167.5,88.9688,155.5,76.9688,167.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="167.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="135.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="238.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="64.5,152.9375,123.5,152.9375,135.5,164.9375,123.5,176.9375,64.5,176.9375,52.5,164.9375,64.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="168.5898">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="162.1875">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="162.1875">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="207.9063">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="207.9063">Activity</text><polygon fill="#F1F1F1" points="94,226.9063,106,238.9063,94,250.9063,82,238.9063,94,226.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="268.5" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="278.5" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="270.5,152.9375,329.5,152.9375,341.5,164.9375,329.5,176.9375,270.5,176.9375,258.5,164.9375,270.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="270.5" y="168.5898">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="238.5" y="162.1875">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="341.5" y="162.1875">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="217" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="227" y="207.9063">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="320" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="330" y="207.9063">Activity</text><polygon fill="#F1F1F1" points="300,226.9063,312,238.9063,300,250.9063,288,238.9063,300,226.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="197,256.9063,209,268.9063,197,280.9063,185,268.9063,197,256.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="38.5,176.9375,42.5,186.9375,46.5,176.9375,42.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="141.5,176.9375,145.5,186.9375,149.5,176.9375,145.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="72,234.9063,82,238.9063,72,242.9063,76,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="116,234.9063,106,238.9063,116,242.9063,112,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="132.9375" y2="152.9375"></line><polygon fill="#181818" points="90,142.9375,94,152.9375,98,142.9375,94,146.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="258.5" x2="248.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="248.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="244.5,176.9375,248.5,186.9375,252.5,176.9375,248.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="341.5" x2="351.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="347.5,176.9375,351.5,186.9375,355.5,176.9375,351.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="248.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="288" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="278,234.9063,288,238.9063,278,242.9063,282,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="312" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="322,234.9063,312,238.9063,322,242.9063,318,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="132.9375" y2="152.9375"></line><polygon fill="#181818" points="296,142.9375,300,152.9375,304,142.9375,300,146.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="155.5" x2="94" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="90,88.9688,94,98.9688,98,88.9688,94,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="238.5" x2="300" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="296,88.9688,300,98.9688,304,88.9688,300,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="250.9063" y2="268.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="185" y1="268.9063" y2="268.9063"></line><polygon fill="#181818" points="175,264.9063,185,268.9063,175,272.9063,179,268.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="250.9063" y2="268.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="209" y1="268.9063" y2="268.9063"></line><polygon fill="#181818" points="219,264.9063,209,268.9063,219,272.9063,215,268.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="197" x2="197" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="193,54.9688,197,64.9688,201,54.9688,197,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,152.9375,123.5,152.9375,135.5,164.9375,123.5,176.9375,64.5,176.9375,52.5,164.9375,64.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_get_text_no_branchif(self, client):
        test_data = {
            "plantuml": """@startuml

start
-> 1;
: 1. Nsmf_PDUSession_CreateSMContext Request;
if (statement1a) then (downa)
    :2;
    stop
else (righta)
endif

:3;
:4;
if (statement2) then (down)
    :5;
    stop
else (right)
endif
:Activity;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="71.5547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="92.5234" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="158" y="173.9258"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="168" y="194.8945" style="pointer-events: none;">2</text><ellipse cx="172" cy="247.4102" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="172" cy="247.4102" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="136,125.5234,208,125.5234,220,137.5234,208,149.5234,136,149.5234,124,137.5234,136,125.5234" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="37" x="176" y="159.5781" style="pointer-events: none;">downa</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="72" x="136" y="141.1758" style="pointer-events: none;">statement1a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="33" x="220" y="134.7734" style="pointer-events: none;">righta</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="158" y="300.4102"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="168" y="321.3789" style="pointer-events: none;">3</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="158" y="354.3789"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="168" y="375.3477" style="pointer-events: none;">4</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="158" y="456.75"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="168" y="477.7188" style="pointer-events: none;">5</text><ellipse cx="172" cy="530.2344" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="172" cy="530.2344" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="139.5,408.3477,204.5,408.3477,216.5,420.3477,204.5,432.3477,139.5,432.3477,127.5,420.3477,139.5,408.3477" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="30" x="176" y="442.4023" style="pointer-events: none;">down</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="65" x="139.5" y="424" style="pointer-events: none;">statement2</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="26" x="216.5" y="417.5977" style="pointer-events: none;">right</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="140.5" y="583.2344"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="150.5" y="604.2031" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="71.5547"></line><polygon fill="#181818" points="168,61.5547,172,71.5547,176,61.5547,172,65.5547" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="176" y="51.3047">1</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="207.8945" y2="236.4102"></line><polygon fill="#181818" points="168,226.4102,172,236.4102,176,226.4102,172,230.4102" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="149.5234" y2="173.9258"></line><polygon fill="#181818" points="168,163.9258,172,173.9258,176,163.9258,172,167.9258" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220" x2="232" y1="137.5234" y2="137.5234"></line><polygon fill="#181818" points="228,206.4102,232,216.4102,236,206.4102,232,210.4102" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="232" x2="232" y1="137.5234" y2="280.4102"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="232" x2="172" y1="280.4102" y2="280.4102"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="280.4102" y2="300.4102"></line><polygon fill="#181818" points="168,290.4102,172,300.4102,176,290.4102,172,294.4102" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="105.5234" y2="125.5234"></line><polygon fill="#181818" points="168,115.5234,172,125.5234,176,115.5234,172,119.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="334.3789" y2="354.3789"></line><polygon fill="#181818" points="168,344.3789,172,354.3789,176,344.3789,172,348.3789" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="490.7188" y2="519.2344"></line><polygon fill="#181818" points="168,509.2344,172,519.2344,176,509.2344,172,513.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="432.3477" y2="456.75"></line><polygon fill="#181818" points="168,446.75,172,456.75,176,446.75,172,450.75" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="216.5" x2="228.5" y1="420.3477" y2="420.3477"></line><polygon fill="#181818" points="224.5,489.2344,228.5,499.2344,232.5,489.2344,228.5,493.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="228.5" x2="228.5" y1="420.3477" y2="563.2344"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="228.5" x2="172" y1="563.2344" y2="563.2344"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="563.2344" y2="583.2344"></line><polygon fill="#181818" points="168,573.2344,172,583.2344,176,573.2344,172,577.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="388.3477" y2="408.3477"></line><polygon fill="#181818" points="168,398.3477,172,408.3477,176,398.3477,172,402.3477" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="139.5,408.3477,204.5,408.3477,216.5,420.3477,204.5,432.3477,139.5,432.3477,127.5,420.3477,139.5,408.3477" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getTextPoly",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = ["statement2", "down", "right"]
            assert json.loads(response.data.decode("utf-8")) == expected_result

    def test_gettextpoly(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="56.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="66.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="119.9375">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="94,138.9375,106,150.9375,94,162.9375,82,150.9375,94,138.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="38.5,88.9688,42.5,98.9688,46.5,88.9688,42.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="141.5,88.9688,145.5,98.9688,149.5,88.9688,145.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="72,146.9375,82,150.9375,72,154.9375,76,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="116,146.9375,106,150.9375,116,154.9375,112,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="90,54.9688,94,64.9688,98,54.9688,94,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getTextPoly",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = ["Statement", "yes", "no"]
            assert json.loads(response.data.decode("utf-8")) == expected_result

    def test_editmultilineifstatement(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (hej
hej) then (yes
yes)
  :Activity;
else (no
no)
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="46.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="56.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="72,69.0234,96,69.0234,108,81.8281,96,94.6328,72,94.6328,60,81.8281,72,69.0234" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="75.5" y="79.0781">hej</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="75.5" y="91.8828">hej</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="40" y="66.2734">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="40" y="79.0781">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="108" y="66.2734">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="108" y="79.0781">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="104.6328"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="125.6016">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="94" y="104.6328"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="104" y="125.6016">Activity</text><polygon fill="#F1F1F1" points="84,144.6016,96,156.6016,84,168.6016,72,156.6016,84,144.6016" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="60" x2="42.5" y1="81.8281" y2="81.8281"></line><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="81.8281" y2="104.6328"></line><polygon fill="#181818" points="38.5,94.6328,42.5,104.6328,46.5,94.6328,42.5,98.6328" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="108" x2="125.5" y1="81.8281" y2="81.8281"></line><line style="stroke:#181818;stroke-width:1.0;" x1="125.5" x2="125.5" y1="81.8281" y2="104.6328"></line><polygon fill="#181818" points="121.5,94.6328,125.5,104.6328,129.5,94.6328,125.5,98.6328" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="138.6016" y2="156.6016"></line><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="72" y1="156.6016" y2="156.6016"></line><polygon fill="#181818" points="62,152.6016,72,156.6016,62,160.6016,66,156.6016" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="125.5" x2="125.5" y1="138.6016" y2="156.6016"></line><line style="stroke:#181818;stroke-width:1.0;" x1="125.5" x2="96" y1="156.6016" y2="156.6016"></line><polygon fill="#181818" points="106,152.6016,96,156.6016,106,160.6016,102,156.6016" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="84" x2="84" y1="44.9688" y2="69.0234"></line><polygon fill="#181818" points="80,59.0234,84,69.0234,88,59.0234,84,63.0234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "hej",
            "branch1": "yes",
            "branch2": "no",
            "svgelement": """<polygon fill="#F1F1F1" points="72,69.0234,96,69.0234,108,81.8281,96,94.6328,72,94.6328,60,81.8281,72,69.0234" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
if (hej) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml
