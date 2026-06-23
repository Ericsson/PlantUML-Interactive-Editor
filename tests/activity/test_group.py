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

"""Tests for group and partition creation, editing, and deletion."""

from flask import json


class TestAppRoutesGroup:
    def test_gettextpartition(self, client):
        test_data = {
            "plantuml": """@startuml
partition hej {
:Activity;
}
@enduml""",
            "svg": """<rect fill="none" height="75.2656" style="stroke:#000000;stroke-width:1.5;" width="83" x="11" y="11"></rect><path d="M42,11 L42,20.2969 L32,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="21" x="14" y="24.7969">hej</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="21" y="40.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="31" y="61.2656" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<path d="M42,11 L42,20.2969 L32,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
        }
        with client:
            response = client.post(
                "/getGroupText",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = "hej"
            assert response.data.decode("utf-8") == expected_result

    def test_editpartition(self, client):
        test_data = {
            "plantuml": """@startuml
partition hej {
:Activity;
}
@enduml""",
            "svg": """<rect fill="none" height="75.2656" style="stroke:#000000;stroke-width:1.5;" width="83" x="11" y="11"></rect><path d="M42,11 L42,20.2969 L32,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="21" x="14" y="24.7969">hej</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="21" y="40.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="31" y="61.2656" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<path d="M42,11 L42,20.2969 L32,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
            "text": "bom",
        }
        with client:
            response = client.post(
                "/editGroup",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
partition bom {
:Activity;
}
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_get_group_line(self, client):
        test_data = {
            "plantuml": """@startuml
group group
:Activity 1;
end group
partition bom {
:Activity 8;
}
@enduml""",
            "svg": """<rect fill="none" height="75.2656" style="stroke:#000000;stroke-width:1.5;" width="95" x="11" y="11"></rect><path d="M62,11 L62,20.2969 L52,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="41" x="14" y="24.7969">group</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="21" y="40.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="31" y="61.2656" style="pointer-events: none;">Activity 1</text><rect fill="none" height="82.2656" style="stroke:#000000;stroke-width:1.5;" width="95" x="11" y="96.2656"></rect><path d="M52,96.2656 L52,105.5625 L42,115.5625 L11,115.5625 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="31" x="14" y="110.0625">bom</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="21" y="132.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="31" y="153.5313" style="pointer-events: none;">Activity 8</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="74.2656" y2="132.5625"></line><polygon fill="#181818" points="54.5,122.5625,58.5,132.5625,62.5,122.5625,58.5,126.5625" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M62,11 L62,20.2969 L52,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
        }
        with client:
            response = client.post(
                "/getGroupLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
        response_json = json.loads(response.data.decode("utf-8"))
        result_value = response_json.get("result")

        # Expected value
        expected_puml = [1, 3]

        # Assert the result value is as expected
        assert result_value == expected_puml

    def test_deletegroupwithpartition(self, client):
        test_data = {
            "plantuml": """@startuml
group group
:Activity 1;
end group
partition bom {
:Activity 8;
}
@enduml""",
            "svg": """<rect fill="none" height="75.2656" style="stroke:#000000;stroke-width:1.5;" width="95" x="11" y="11"></rect><path d="M62,11 L62,20.2969 L52,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="41" x="14" y="24.7969">group</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="21" y="40.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="31" y="61.2656" style="pointer-events: none;">Activity 1</text><rect fill="none" height="82.2656" style="stroke:#000000;stroke-width:1.5;" width="95" x="11" y="96.2656"></rect><path d="M52,96.2656 L52,105.5625 L42,115.5625 L11,115.5625 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="31" x="14" y="110.0625">bom</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="21" y="132.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="31" y="153.5313" style="pointer-events: none;">Activity 8</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="74.2656" y2="132.5625"></line><polygon fill="#181818" points="54.5,122.5625,58.5,132.5625,62.5,122.5625,58.5,126.5625" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M62,11 L62,20.2969 L52,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
        }
        with client:
            response = client.post(
                "/deleteGroup",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
:Activity 1;
partition bom {
:Activity 8;
}
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_deletegroup(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
note
end note
group group
if (Statement) then (yes)
  :Activity;
else (no)
group hej
  :Activity;
end group
endif
end group
stop
@enduml""",
            "svg": """<ellipse cx="106" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M157.5,54.418 L157.5,62.9844 L137.5,66.9844 L157.5,70.9844 L157.5,79.5508 A0,0 0 0 0 157.5,79.5508 L207.5,79.5508 A0,0 0 0 0 207.5,79.5508 L207.5,64.418 L197.5,54.418 L157.5,54.418 A0,0 0 0 0 157.5,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M197.5,54.418 L197.5,64.418 L207.5,64.418 L197.5,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="29" x="163.5" y="71.3008" style="pointer-events: none;">note</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="74.5" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="84.5" y="70.9688" style="pointer-events: none;">Activity</text><rect fill="none" height="194.5625" style="stroke:#000000;stroke-width:1.5;" width="208" x="11" y="93.9688"></rect><path d="M62,93.9688 L62,103.2656 L52,113.2656 L11,113.2656 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="41" x="14" y="107.7656">group</text><polygon fill="#F1F1F1" points="76.5,130.2656,135.5,130.2656,147.5,142.2656,135.5,154.2656,76.5,154.2656,64.5,142.2656,76.5,130.2656" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="76.5" y="145.918" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="44.5" y="139.5156" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="147.5" y="139.5156" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="23" y="164.2656"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="33" y="185.2344" style="pointer-events: none;">Activity</text><rect fill="none" height="82.2656" style="stroke:#000000;stroke-width:1.5;" width="83" x="116" y="164.2656"></rect><path d="M147,164.2656 L147,173.5625 L137,183.5625 L116,183.5625 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="21" x="119" y="178.0625">hej</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="126" y="200.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="136" y="221.5313" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="106,252.5313,118,264.5313,106,276.5313,94,264.5313,106,252.5313" style="stroke:#181818;stroke-width:0.5;"></polygon><ellipse cx="106" cy="319.5313" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="106" cy="319.5313" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="30" y2="50"></line><polygon fill="#181818" points="102,40,106,50,110,40,106,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="64.5" x2="54.5" y1="142.2656" y2="142.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="54.5" y1="142.2656" y2="164.2656"></line><polygon fill="#181818" points="50.5,154.2656,54.5,164.2656,58.5,154.2656,54.5,158.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="147.5" x2="157.5" y1="142.2656" y2="142.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="157.5" y1="142.2656" y2="200.5625"></line><polygon fill="#181818" points="153.5,190.5625,157.5,200.5625,161.5,190.5625,157.5,194.5625" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="54.5" y1="198.2344" y2="264.5313"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="94" y1="264.5313" y2="264.5313"></line><polygon fill="#181818" points="84,260.5313,94,264.5313,84,268.5313,88,264.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="157.5" y1="234.5313" y2="264.5313"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="118" y1="264.5313" y2="264.5313"></line><polygon fill="#181818" points="128,260.5313,118,264.5313,128,268.5313,124,264.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="83.9688" y2="130.2656"></line><polygon fill="#181818" points="102,120.2656,106,130.2656,110,120.2656,106,124.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="276.5313" y2="308.5313"></line><polygon fill="#181818" points="102,298.5313,106,308.5313,110,298.5313,106,302.5313" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M62,93.9688 L62,103.2656 L52,113.2656 L11,113.2656 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
        }
        with client:
            response = client.post(
                "/deleteGroup",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
note right
note
end note
if (Statement) then (yes)
  :Activity;
else (no)
group hej
  :Activity;
end group
endif
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_editgroupempty(self, client):
        test_data = {
            "plantuml": """@startuml
start
group group
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
end group
stop
@enduml""",
            "svg": """<ellipse cx="106" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="none" height="146.2656" style="stroke:#000000;stroke-width:1.5;" width="190" x="11" y="40"></rect><path d="M62,40 L62,49.2969 L52,59.2969 L11,59.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="41" x="14" y="53.7969">group</text><polygon fill="#F1F1F1" points="76.5,76.2969,135.5,76.2969,147.5,88.2969,135.5,100.2969,76.5,100.2969,64.5,88.2969,76.5,76.2969" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="76.5" y="91.9492" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="44.5" y="85.5469" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="147.5" y="85.5469" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="23" y="110.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="33" y="131.2656" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="126" y="110.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="136" y="131.2656" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="106,150.2656,118,162.2656,106,174.2656,94,162.2656,106,150.2656" style="stroke:#181818;stroke-width:0.5;"></polygon><ellipse cx="106" cy="217.2656" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="106" cy="217.2656" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="64.5" x2="54.5" y1="88.2969" y2="88.2969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="54.5" y1="88.2969" y2="110.2969"></line><polygon fill="#181818" points="50.5,100.2969,54.5,110.2969,58.5,100.2969,54.5,104.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="147.5" x2="157.5" y1="88.2969" y2="88.2969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="157.5" y1="88.2969" y2="110.2969"></line><polygon fill="#181818" points="153.5,100.2969,157.5,110.2969,161.5,100.2969,157.5,104.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="54.5" y1="144.2656" y2="162.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="94" y1="162.2656" y2="162.2656"></line><polygon fill="#181818" points="84,158.2656,94,162.2656,84,166.2656,88,162.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="157.5" y1="144.2656" y2="162.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="118" y1="162.2656" y2="162.2656"></line><polygon fill="#181818" points="128,158.2656,118,162.2656,128,166.2656,124,162.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="30" y2="76.2969"></line><polygon fill="#181818" points="102,66.2969,106,76.2969,110,66.2969,106,70.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="174.2656" y2="206.2656"></line><polygon fill="#181818" points="102,196.2656,106,206.2656,110,196.2656,106,200.2656" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M62,40 L62,49.2969 L52,59.2969 L11,59.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
            "text": "",
        }
        with client:
            response = client.post(
                "/editGroup",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_editgroup(self, client):
        test_data = {
            "plantuml": """@startuml
start
group group
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
end group
stop
@enduml""",
            "svg": """<ellipse cx="106" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="none" height="146.2656" style="stroke:#000000;stroke-width:1.5;" width="190" x="11" y="40"></rect><path d="M62,40 L62,49.2969 L52,59.2969 L11,59.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="41" x="14" y="53.7969">group</text><polygon fill="#F1F1F1" points="76.5,76.2969,135.5,76.2969,147.5,88.2969,135.5,100.2969,76.5,100.2969,64.5,88.2969,76.5,76.2969" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="76.5" y="91.9492" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="44.5" y="85.5469" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="147.5" y="85.5469" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="23" y="110.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="33" y="131.2656" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="126" y="110.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="136" y="131.2656" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="106,150.2656,118,162.2656,106,174.2656,94,162.2656,106,150.2656" style="stroke:#181818;stroke-width:0.5;"></polygon><ellipse cx="106" cy="217.2656" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="106" cy="217.2656" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="64.5" x2="54.5" y1="88.2969" y2="88.2969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="54.5" y1="88.2969" y2="110.2969"></line><polygon fill="#181818" points="50.5,100.2969,54.5,110.2969,58.5,100.2969,54.5,104.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="147.5" x2="157.5" y1="88.2969" y2="88.2969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="157.5" y1="88.2969" y2="110.2969"></line><polygon fill="#181818" points="153.5,100.2969,157.5,110.2969,161.5,100.2969,157.5,104.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="54.5" y1="144.2656" y2="162.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="94" y1="162.2656" y2="162.2656"></line><polygon fill="#181818" points="84,158.2656,94,162.2656,84,166.2656,88,162.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="157.5" y1="144.2656" y2="162.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="118" y1="162.2656" y2="162.2656"></line><polygon fill="#181818" points="128,158.2656,118,162.2656,128,166.2656,124,162.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="30" y2="76.2969"></line><polygon fill="#181818" points="102,66.2969,106,76.2969,110,66.2969,106,70.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="174.2656" y2="206.2656"></line><polygon fill="#181818" points="102,196.2656,106,206.2656,110,196.2656,106,200.2656" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M62,40 L62,49.2969 L52,59.2969 L11,59.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
            "text": "hej",
        }
        with client:
            response = client.post(
                "/editGroup",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
group hej
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
end group
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_gettextgroup(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
note
end note
group hello
if (Statement) then (yes)
group hej
  :Activity;
end group
else (no)
  :Activity;
endif
end group
fork
  :action;
note left
note
end note
fork again
  :action;
end fork
stop
@enduml""",
            "svg": """<ellipse cx="133" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M184.5,54.418 L184.5,62.9844 L164.5,66.9844 L184.5,70.9844 L184.5,79.5508 A0,0 0 0 0 184.5,79.5508 L234.5,79.5508 A0,0 0 0 0 234.5,79.5508 L234.5,64.418 L224.5,54.418 L184.5,54.418 A0,0 0 0 0 184.5,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M224.5,54.418 L224.5,64.418 L234.5,64.418 L224.5,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="29" x="190.5" y="71.3008" style="pointer-events: none;">note</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="101.5" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="111.5" y="70.9688" style="pointer-events: none;">Activity</text><rect fill="none" height="194.5625" style="stroke:#000000;stroke-width:1.5;" width="216" x="20" y="93.9688"></rect><path d="M63,93.9688 L63,103.2656 L53,113.2656 L20,113.2656 " fill="transparent" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="33" x="23" y="107.7656" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="103.5,130.2656,162.5,130.2656,174.5,142.2656,162.5,154.2656,103.5,154.2656,91.5,142.2656,103.5,130.2656" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="103.5" y="145.918" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="71.5" y="139.5156" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="174.5" y="139.5156" style="pointer-events: none;">no</text><rect fill="none" height="82.2656" style="stroke:#000000;stroke-width:1.5;" width="83" x="40" y="164.2656"></rect><path d="M71,164.2656 L71,173.5625 L61,183.5625 L40,183.5625 " fill="transparent" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="21" x="43" y="178.0625" style="pointer-events: none;">hej</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="50" y="200.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="60" y="221.5313" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="153" y="164.2656"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="163" y="185.2344" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="133,252.5313,145,264.5313,133,276.5313,121,264.5313,133,252.5313" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="242" x="11" y="308.5313"></rect><path d="M25,338.9492 L25,364.082 A0,0 0 0 0 25,364.082 L75,364.082 A0,0 0 0 0 75,364.082 L75,356.9492 L95,351.5156 L75,348.9492 L75,348.9492 L65,338.9492 L25,338.9492 A0,0 0 0 0 25,338.9492 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M65,338.9492 L65,348.9492 L75,348.9492 L65,338.9492 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="29" x="31" y="355.832" style="pointer-events: none;">note</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="95" y="334.5313"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="105" y="355.5" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="182" y="334.5313"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="192" y="355.5" style="pointer-events: none;">action</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="242" x="11" y="388.5"></rect><ellipse cx="133" cy="425.5" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="133" cy="425.5" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133" x2="133" y1="30" y2="50"></line><polygon fill="#181818" points="129,40,133,50,137,40,133,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="91.5" x2="81.5" y1="142.2656" y2="142.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="81.5" x2="81.5" y1="142.2656" y2="200.5625"></line><polygon fill="#181818" points="77.5,190.5625,81.5,200.5625,85.5,190.5625,81.5,194.5625" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="174.5" x2="184.5" y1="142.2656" y2="142.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184.5" x2="184.5" y1="142.2656" y2="164.2656"></line><polygon fill="#181818" points="180.5,154.2656,184.5,164.2656,188.5,154.2656,184.5,158.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="81.5" x2="81.5" y1="234.5313" y2="264.5313"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="81.5" x2="121" y1="264.5313" y2="264.5313"></line><polygon fill="#181818" points="111,260.5313,121,264.5313,111,268.5313,115,264.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184.5" x2="184.5" y1="198.2344" y2="264.5313"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184.5" x2="145" y1="264.5313" y2="264.5313"></line><polygon fill="#181818" points="155,260.5313,145,264.5313,155,268.5313,151,264.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133" x2="133" y1="83.9688" y2="130.2656"></line><polygon fill="#181818" points="129,120.2656,133,130.2656,137,120.2656,133,124.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="124.5" x2="124.5" y1="314.5313" y2="334.5313"></line><polygon fill="#181818" points="120.5,324.5313,124.5,334.5313,128.5,324.5313,124.5,328.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="211.5" x2="211.5" y1="314.5313" y2="334.5313"></line><polygon fill="#181818" points="207.5,324.5313,211.5,334.5313,215.5,324.5313,211.5,328.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="124.5" x2="124.5" y1="368.5" y2="388.5"></line><polygon fill="#181818" points="120.5,378.5,124.5,388.5,128.5,378.5,124.5,382.5" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="211.5" x2="211.5" y1="368.5" y2="388.5"></line><polygon fill="#181818" points="207.5,378.5,211.5,388.5,215.5,378.5,211.5,382.5" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133" x2="133" y1="276.5313" y2="308.5313"></line><polygon fill="#181818" points="129,298.5313,133,308.5313,137,298.5313,133,302.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133" x2="133" y1="394.5" y2="414.5"></line><polygon fill="#181818" points="129,404.5,133,414.5,137,404.5,133,408.5" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M71,164.2656 L71,173.5625 L61,183.5625 L40,183.5625 " fill="transparent" style="stroke:#000000;stroke-width:1.5;"></path>""",
        }
        with client:
            response = client.post(
                "/getGroupText",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = "hej"
            assert response.data.decode("utf-8") == expected_result
