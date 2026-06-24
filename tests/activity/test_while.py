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

"""Tests for while loop creation, editing, deletion, and nested loops."""

from flask import json


class TestAppRoutesWhile:
    def test_addforkbreak(self, client):
        test_data = {
            "plantuml": """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
stop
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="67.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="88.5781" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="90" y="46.1094" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="48" y="27.707" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="21" y="21.3047" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="143.5781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="164.5469" style="pointer-events: none;">hello again</text><ellipse cx="86" cy="208.5469" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="86" cy="208.5469" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="36.0547" y2="67.6094"></line><polygon fill="#181818" points="82,57.6094,86,67.6094,90,57.6094,86,61.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="101.5781" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="148" y1="111.5781" y2="111.5781"></line><polygon fill="#181818" points="144,76.1914,148,66.1914,152,76.1914,148,72.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="148" y1="24.0547" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="136" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="146,20.0547,136,24.0547,146,28.0547,142,24.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="36" x2="24" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="20,62.1914,24,72.1914,28,62.1914,24,66.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="24.0547" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="86" y1="123.5781" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="123.5781" y2="143.5781"></line><polygon fill="#181818" points="82,133.5781,86,143.5781,90,133.5781,86,137.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="177.5469" y2="197.5469"></line><polygon fill="#181818" points="82,187.5469,86,197.5469,90,187.5469,86,191.5469" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "type": "fork",
            "where": "break",
        }
        with client:
            response = client.post(
                "/addToWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
fork
:action;
fork again
:action;
end fork
:hello again;
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_addifloop(self, client):
        test_data = {
            "plantuml": """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
stop
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="67.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="88.5781" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="90" y="46.1094" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="48" y="27.707" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="21" y="21.3047" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="143.5781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="164.5469" style="pointer-events: none;">hello again</text><ellipse cx="86" cy="208.5469" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="86" cy="208.5469" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="36.0547" y2="67.6094"></line><polygon fill="#181818" points="82,57.6094,86,67.6094,90,57.6094,86,61.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="101.5781" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="148" y1="111.5781" y2="111.5781"></line><polygon fill="#181818" points="144,76.1914,148,66.1914,152,76.1914,148,72.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="148" y1="24.0547" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="136" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="146,20.0547,136,24.0547,146,28.0547,142,24.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="36" x2="24" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="20,62.1914,24,72.1914,28,62.1914,24,66.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="24.0547" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="86" y1="123.5781" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="123.5781" y2="143.5781"></line><polygon fill="#181818" points="82,133.5781,86,143.5781,90,133.5781,86,137.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="177.5469" y2="197.5469"></line><polygon fill="#181818" points="82,187.5469,86,197.5469,90,187.5469,86,191.5469" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "type": "if",
            "where": "loop",
        }
        with client:
            response = client.post(
                "/addToWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
if (Statement) then (yes)
:Activity;
else (no)
:Activity;
endif
endwhile (No);
:hello again;
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_delwhile(self, client):
        test_data = {
            "plantuml": """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
stop
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="67.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="88.5781" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="90" y="46.1094" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="48" y="27.707" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="21" y="21.3047" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="143.5781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="164.5469" style="pointer-events: none;">hello again</text><ellipse cx="86" cy="208.5469" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="86" cy="208.5469" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="36.0547" y2="67.6094"></line><polygon fill="#181818" points="82,57.6094,86,67.6094,90,57.6094,86,61.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="101.5781" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="148" y1="111.5781" y2="111.5781"></line><polygon fill="#181818" points="144,76.1914,148,66.1914,152,76.1914,148,72.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="148" y1="24.0547" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="136" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="146,20.0547,136,24.0547,146,28.0547,142,24.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="36" x2="24" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="20,62.1914,24,72.1914,28,62.1914,24,66.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="24.0547" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="86" y1="123.5781" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="123.5781" y2="143.5781"></line><polygon fill="#181818" points="82,133.5781,86,143.5781,90,133.5781,86,137.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="177.5469" y2="197.5469"></line><polygon fill="#181818" points="82,187.5469,86,197.5469,90,187.5469,86,191.5469" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
:hello again;
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_get_while_line(self, client):
        test_data = {
            "plantuml": """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
stop
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="67.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="88.5781" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="90" y="46.1094" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="48" y="27.707" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="21" y="21.3047" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="143.5781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="164.5469" style="pointer-events: none;">hello again</text><ellipse cx="86" cy="208.5469" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="86" cy="208.5469" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="36.0547" y2="67.6094"></line><polygon fill="#181818" points="82,57.6094,86,67.6094,90,57.6094,86,61.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="101.5781" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="148" y1="111.5781" y2="111.5781"></line><polygon fill="#181818" points="144,76.1914,148,66.1914,152,76.1914,148,72.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="148" y1="24.0547" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="136" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="146,20.0547,136,24.0547,146,28.0547,142,24.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="36" x2="24" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="20,62.1914,24,72.1914,28,62.1914,24,66.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="24.0547" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="86" y1="123.5781" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="123.5781" y2="143.5781"></line><polygon fill="#181818" points="82,133.5781,86,143.5781,90,133.5781,86,137.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="177.5469" y2="197.5469"></line><polygon fill="#181818" points="82,187.5469,86,197.5469,90,187.5469,86,191.5469" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getWhileLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = [1, 3]

            # Assert the result value is as expected
            assert result_value == expected_puml

    def test_editwhilemultiplenests(self, client):
        test_data = {
            "plantuml": """@startuml
start
while (ST_ONGOING) is (Yes)
    :hello;
    while (ST_ONGOING) is (Yes)
    :hello;
    while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:activity;
endwhile (No);
:activity;
endwhile (No);
:activity;
while (ST_ONGOING) is (Yes)
    :hello;
    while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:activity;
endwhile (No);
:activity;
@enduml""",
            "svg": """<ellipse cx="122" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="97" y="105.5547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="107" y="126.5234" style="pointer-events: none;">hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="97" y="215.0781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="107" y="236.0469" style="pointer-events: none;">hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="97" y="329.8516"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="107" y="350.8203" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="84,269.0469,160,269.0469,172,281.0469,160,293.0469,84,293.0469,72,281.0469,84,269.0469" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="126" y="303.1016" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="84" y="284.6992" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="57" y="278.2969" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="90.5" y="405.8203"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="100.5" y="426.7891" style="pointer-events: none;">activity</text><polygon fill="#F1F1F1" points="84,159.5234,160,159.5234,172,171.5234,160,183.5234,84,183.5234,72,171.5234,84,159.5234" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="126" y="193.5781" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="84" y="175.1758" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="57" y="168.7734" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="90.5" y="481.7891"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="100.5" y="502.7578" style="pointer-events: none;">activity</text><polygon fill="#F1F1F1" points="84,50,160,50,172,62,160,74,84,74,72,62,84,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="126" y="84.0547" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="84" y="65.6523" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="57" y="59.25" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="90.5" y="557.7578"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="100.5" y="578.7266" style="pointer-events: none;">activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="97" y="667.2813"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="107" y="688.25" style="pointer-events: none;">hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="97" y="782.0547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="107" y="803.0234" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="84,721.25,160,721.25,172,733.25,160,745.25,84,745.25,72,733.25,84,721.25" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="126" y="755.3047" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="84" y="736.9023" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="57" y="730.5" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="90.5" y="858.0234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="100.5" y="878.9922" style="pointer-events: none;">activity</text><polygon fill="#F1F1F1" points="84,611.7266,160,611.7266,172,623.7266,160,635.7266,84,635.7266,72,623.7266,84,611.7266" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="126" y="645.7813" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="84" y="627.3789" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="57" y="620.9766" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="90.5" y="933.9922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="100.5" y="954.9609" style="pointer-events: none;">activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="293.0469" y2="329.8516"></line><polygon fill="#181818" points="118,319.8516,122,329.8516,126,319.8516,122,323.8516" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="363.8203" y2="373.8203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="184" y1="373.8203" y2="373.8203"></line><polygon fill="#181818" points="180,338.4336,184,328.4336,188,338.4336,184,334.4336" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184" x2="184" y1="281.0469" y2="373.8203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184" x2="172" y1="281.0469" y2="281.0469"></line><polygon fill="#181818" points="182,277.0469,172,281.0469,182,285.0469,178,281.0469" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="72" x2="60" y1="281.0469" y2="281.0469"></line><polygon fill="#181818" points="56,324.4336,60,334.4336,64,324.4336,60,328.4336" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="60" x2="60" y1="281.0469" y2="385.8203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="60" x2="122" y1="385.8203" y2="385.8203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="385.8203" y2="405.8203"></line><polygon fill="#181818" points="118,395.8203,122,405.8203,126,395.8203,122,399.8203" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="249.0469" y2="269.0469"></line><polygon fill="#181818" points="118,259.0469,122,269.0469,126,259.0469,122,263.0469" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="183.5234" y2="215.0781"></line><polygon fill="#181818" points="118,205.0781,122,215.0781,126,205.0781,122,209.0781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="439.7891" y2="449.7891"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="196" y1="449.7891" y2="449.7891"></line><polygon fill="#181818" points="192,320.0313,196,310.0313,200,320.0313,196,316.0313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="196" x2="196" y1="171.5234" y2="449.7891"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="196" x2="172" y1="171.5234" y2="171.5234"></line><polygon fill="#181818" points="182,167.5234,172,171.5234,182,175.5234,178,171.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="72" x2="42" y1="171.5234" y2="171.5234"></line><polygon fill="#181818" points="38,306.0313,42,316.0313,46,306.0313,42,310.0313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42" x2="42" y1="171.5234" y2="461.7891"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42" x2="122" y1="461.7891" y2="461.7891"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="461.7891" y2="481.7891"></line><polygon fill="#181818" points="118,471.7891,122,481.7891,126,471.7891,122,475.7891" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="139.5234" y2="159.5234"></line><polygon fill="#181818" points="118,149.5234,122,159.5234,126,149.5234,122,153.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="74" y2="105.5547"></line><polygon fill="#181818" points="118,95.5547,122,105.5547,126,95.5547,122,99.5547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="515.7578" y2="525.7578"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="208" y1="525.7578" y2="525.7578"></line><polygon fill="#181818" points="204,301.6289,208,291.6289,212,301.6289,208,297.6289" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="208" x2="208" y1="62" y2="525.7578"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="208" x2="172" y1="62" y2="62"></line><polygon fill="#181818" points="182,58,172,62,182,66,178,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="72" x2="24" y1="62" y2="62"></line><polygon fill="#181818" points="20,287.6289,24,297.6289,28,287.6289,24,291.6289" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="62" y2="537.7578"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="122" y1="537.7578" y2="537.7578"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="537.7578" y2="557.7578"></line><polygon fill="#181818" points="118,547.7578,122,557.7578,126,547.7578,122,551.7578" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="30" y2="50"></line><polygon fill="#181818" points="118,40,122,50,126,40,122,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="745.25" y2="782.0547"></line><polygon fill="#181818" points="118,772.0547,122,782.0547,126,772.0547,122,776.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="816.0234" y2="826.0234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="184" y1="826.0234" y2="826.0234"></line><polygon fill="#181818" points="180,790.6367,184,780.6367,188,790.6367,184,786.6367" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184" x2="184" y1="733.25" y2="826.0234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184" x2="172" y1="733.25" y2="733.25"></line><polygon fill="#181818" points="182,729.25,172,733.25,182,737.25,178,733.25" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="72" x2="60" y1="733.25" y2="733.25"></line><polygon fill="#181818" points="56,776.6367,60,786.6367,64,776.6367,60,780.6367" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="60" x2="60" y1="733.25" y2="838.0234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="60" x2="122" y1="838.0234" y2="838.0234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="838.0234" y2="858.0234"></line><polygon fill="#181818" points="118,848.0234,122,858.0234,126,848.0234,122,852.0234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="701.25" y2="721.25"></line><polygon fill="#181818" points="118,711.25,122,721.25,126,711.25,122,715.25" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="635.7266" y2="667.2813"></line><polygon fill="#181818" points="118,657.2813,122,667.2813,126,657.2813,122,661.2813" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="891.9922" y2="901.9922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="196" y1="901.9922" y2="901.9922"></line><polygon fill="#181818" points="192,772.2344,196,762.2344,200,772.2344,196,768.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="196" x2="196" y1="623.7266" y2="901.9922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="196" x2="172" y1="623.7266" y2="623.7266"></line><polygon fill="#181818" points="182,619.7266,172,623.7266,182,627.7266,178,623.7266" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="72" x2="42" y1="623.7266" y2="623.7266"></line><polygon fill="#181818" points="38,758.2344,42,768.2344,46,758.2344,42,762.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42" x2="42" y1="623.7266" y2="913.9922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42" x2="122" y1="913.9922" y2="913.9922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="913.9922" y2="933.9922"></line><polygon fill="#181818" points="118,923.9922,122,933.9922,126,923.9922,122,927.9922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="591.7266" y2="611.7266"></line><polygon fill="#181818" points="118,601.7266,122,611.7266,126,601.7266,122,605.7266" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "whilestatement": "A",
            "break": "B",
            "loop": "C",
            "svgelement": """<polygon fill="#F1F1F1" points="84,721.25,160,721.25,172,733.25,160,745.25,84,745.25,72,733.25,84,721.25" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
while (ST_ONGOING) is (Yes)
    :hello;
    while (ST_ONGOING) is (Yes)
    :hello;
    while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:activity;
endwhile (No);
:activity;
endwhile (No);
:activity;
while (ST_ONGOING) is (Yes)
    :hello;
    while (A) is (C)
    :hello;
endwhile (B);
:activity;
endwhile (No);
:activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_editwhilenested(self, client):
        test_data = {
            "plantuml": """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
    while (Hej) is (Bom)
    :hello;
endwhile (Bam);
:hello again;
endwhile (No);
:hello again;
stop
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="67.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="88.5781" style="pointer-events: none;">hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="182.3828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="203.3516" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="74,121.5781,98,121.5781,110,133.5781,98,145.5781,74,145.5781,62,133.5781,74,121.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="26" x="90" y="155.6328" style="pointer-events: none;">Bom</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="18" x="77" y="137.2305" style="pointer-events: none;">Hej</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="26" x="36" y="130.8281" style="pointer-events: none;">Bam</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="258.3516"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="279.3203" style="pointer-events: none;">hello again</text><polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="90" y="46.1094" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="48" y="27.707" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="21" y="21.3047" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="334.3203"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="355.2891" style="pointer-events: none;">hello again</text><ellipse cx="86" cy="399.2891" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="86" cy="399.2891" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="145.5781" y2="182.3828"></line><polygon fill="#181818" points="82,172.3828,86,182.3828,90,172.3828,86,176.3828" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="216.3516" y2="226.3516"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="123" y1="226.3516" y2="226.3516"></line><polygon fill="#181818" points="119,190.9648,123,180.9648,127,190.9648,123,186.9648" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="123" x2="123" y1="133.5781" y2="226.3516"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="123" x2="110" y1="133.5781" y2="133.5781"></line><polygon fill="#181818" points="120,129.5781,110,133.5781,120,137.5781,116,133.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="62" x2="49" y1="133.5781" y2="133.5781"></line><polygon fill="#181818" points="45,176.9648,49,186.9648,53,176.9648,49,180.9648" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="49" x2="49" y1="133.5781" y2="238.3516"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="49" x2="86" y1="238.3516" y2="238.3516"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="238.3516" y2="258.3516"></line><polygon fill="#181818" points="82,248.3516,86,258.3516,90,248.3516,86,252.3516" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="101.5781" y2="121.5781"></line><polygon fill="#181818" points="82,111.5781,86,121.5781,90,111.5781,86,115.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="36.0547" y2="67.6094"></line><polygon fill="#181818" points="82,57.6094,86,67.6094,90,57.6094,86,61.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="292.3203" y2="302.3203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="148" y1="302.3203" y2="302.3203"></line><polygon fill="#181818" points="144,172.5625,148,162.5625,152,172.5625,148,168.5625" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="148" y1="24.0547" y2="302.3203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="136" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="146,20.0547,136,24.0547,146,28.0547,142,24.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="36" x2="24" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="20,158.5625,24,168.5625,28,158.5625,24,162.5625" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="24.0547" y2="314.3203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="86" y1="314.3203" y2="314.3203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="314.3203" y2="334.3203"></line><polygon fill="#181818" points="82,324.3203,86,334.3203,90,324.3203,86,328.3203" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="368.2891" y2="388.2891"></line><polygon fill="#181818" points="82,378.2891,86,388.2891,90,378.2891,86,382.2891" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "whilestatement": "A",
            "break": "B",
            "loop": "C",
            "svgelement": """<polygon fill="#F1F1F1" points="74,121.5781,98,121.5781,110,133.5781,98,145.5781,74,145.5781,62,133.5781,74,121.5781" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
    while (A) is (C)
    :hello;
endwhile (B);
:hello again;
endwhile (No);
:hello again;
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_editwhile(self, client):
        test_data = {
            "plantuml": """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
stop
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="67.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="88.5781" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="90" y="46.1094" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="48" y="27.707" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="21" y="21.3047" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="143.5781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="164.5469" style="pointer-events: none;">hello again</text><ellipse cx="86" cy="208.5469" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="86" cy="208.5469" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="36.0547" y2="67.6094"></line><polygon fill="#181818" points="82,57.6094,86,67.6094,90,57.6094,86,61.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="101.5781" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="148" y1="111.5781" y2="111.5781"></line><polygon fill="#181818" points="144,76.1914,148,66.1914,152,76.1914,148,72.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="148" y1="24.0547" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="136" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="146,20.0547,136,24.0547,146,28.0547,142,24.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="36" x2="24" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="20,62.1914,24,72.1914,28,62.1914,24,66.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="24.0547" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="86" y1="123.5781" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="123.5781" y2="143.5781"></line><polygon fill="#181818" points="82,133.5781,86,143.5781,90,133.5781,86,137.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="177.5469" y2="197.5469"></line><polygon fill="#181818" points="82,187.5469,86,197.5469,90,187.5469,86,191.5469" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "whilestatement": "Hej",
            "break": "Bom",
            "loop": "Bam",
            "svgelement": """<polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
while (Hej) is (Bam)
    :hello;
endwhile (Bom);
:hello again;
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_getwhiletext(self, client):
        test_data = {
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="70.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="64.5,103.9688,123.5,103.9688,135.5,115.9688,123.5,127.9688,64.5,127.9688,52.5,115.9688,64.5,103.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="119.6211" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="113.2188" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="113.2188" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="137.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="158.9375" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="137.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="158.9375" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,177.9375,106,189.9375,94,201.9375,82,189.9375,94,177.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="69" y="277.4922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="79" y="298.4609" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="56,221.9375,132,221.9375,144,233.9375,132,245.9375,56,245.9375,44,233.9375,56,221.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="98" y="255.9922" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="56" y="237.5898" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="29" y="231.1875" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="49.5" y="353.4609"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="59.5" y="374.4297" style="pointer-events: none;">hello again</text><ellipse cx="94" cy="418.4297" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="94" cy="418.4297" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="115.9688" y2="115.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="115.9688" y2="137.9688"></line><polygon fill="#181818" points="38.5,127.9688,42.5,137.9688,46.5,127.9688,42.5,131.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="115.9688" y2="115.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="115.9688" y2="137.9688"></line><polygon fill="#181818" points="141.5,127.9688,145.5,137.9688,149.5,127.9688,145.5,131.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="171.9375" y2="189.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="189.9375" y2="189.9375"></line><polygon fill="#181818" points="72,185.9375,82,189.9375,72,193.9375,76,189.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="171.9375" y2="189.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="189.9375" y2="189.9375"></line><polygon fill="#181818" points="116,185.9375,106,189.9375,116,193.9375,112,189.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="83.9688" y2="103.9688"></line><polygon fill="#181818" points="90,93.9688,94,103.9688,98,93.9688,94,97.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="245.9375" y2="277.4922"></line><polygon fill="#181818" points="90,267.4922,94,277.4922,98,267.4922,94,271.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="311.4609" y2="321.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="156" y1="321.4609" y2="321.4609"></line><polygon fill="#181818" points="152,286.0742,156,276.0742,160,286.0742,156,282.0742" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="156" x2="156" y1="233.9375" y2="321.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="156" x2="144" y1="233.9375" y2="233.9375"></line><polygon fill="#181818" points="154,229.9375,144,233.9375,154,237.9375,150,233.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="32" y1="233.9375" y2="233.9375"></line><polygon fill="#181818" points="28,272.0742,32,282.0742,36,272.0742,32,276.0742" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="32" x2="32" y1="233.9375" y2="333.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="32" x2="94" y1="333.4609" y2="333.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="333.4609" y2="353.4609"></line><polygon fill="#181818" points="90,343.4609,94,353.4609,98,343.4609,94,347.4609" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="201.9375" y2="221.9375"></line><polygon fill="#181818" points="90,211.9375,94,221.9375,98,211.9375,94,215.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="387.4297" y2="407.4297"></line><polygon fill="#181818" points="90,397.4297,94,407.4297,98,397.4297,94,401.4297" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="56,221.9375,132,221.9375,144,233.9375,132,245.9375,56,245.9375,44,233.9375,56,221.9375" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getTextWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = ["ST_ONGOING", "No", "Yes"]
            assert json.loads(response.data.decode("utf-8")) == expected_result
