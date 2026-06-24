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

"""Tests for arrow label editing, deletion, and switch case arrow operations."""

from flask import json


class TestAppRouteArrow:
    def test_case_duplicate_check(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
case ( condition 2)
    :Activity;
endswitch
@enduml""",
            "svg": """<ellipse cx="118.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="104.5,50,132.5,50,144.5,62,132.5,74,104.5,74,92.5,62,104.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="104.5" y="65.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="130.748" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="128.5" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="138.5" y="130.748" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="118.5,153.5781,118.5,153.5781,130.5,165.5781,118.5,177.5781,118.5,177.5781,106.5,165.5781,118.5,153.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="92.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="109.6094"></line><polygon fill="#181818" points="38.5,99.6094,42.5,109.6094,46.5,99.6094,42.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="46.5" y="89.6128">condition 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="144.5" x2="160" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="62" y2="109.6094"></line><polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="164" y="89.6128">condition 2</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="106.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="96.5,161.5781,106.5,165.5781,96.5,169.5781,100.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="130.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="140.5,161.5781,130.5,165.5781,140.5,169.5781,136.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="118.5" y1="30" y2="50"></line><polygon fill="#181818" points="114.5,40,118.5,50,122.5,40,118.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/checkDuplicateArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            assert not result_value

    def test_check_arrow_duplicate(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="84.3594"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="105.3281" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="91" x="126.5" y="159.8828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="67" x="140.5" y="180.8516" style="pointer-events: none;">2. activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="84.3594"></line><polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="259" x="176" y="51.3047">Nsmf_PDUSession_CreateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="105" x="176" y="64.1094">received from AMF</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="118.3281" y2="159.8828"></line><polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="82" x="176" y="139.6328">label on arrow</text>""",
            "svgelement": """<polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/checkDuplicateArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            assert not result_value

    def test_get_arrow_line(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="84.3594"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="105.3281" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="91" x="126.5" y="159.8828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="67" x="140.5" y="180.8516" style="pointer-events: none;">2. activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="84.3594"></line><polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="259" x="176" y="51.3047">Nsmf_PDUSession_CreateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="105" x="176" y="64.1094">received from AMF</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="118.3281" y2="159.8828"></line><polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="82" x="176" y="139.6328">label on arrow</text>""",
            "svgelement": """<polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getArrowLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = [5, 5]

            # Assert the result value is as expected
            assert result_value == expected_puml

    def test_edit_switch_case_multiline(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
switch (test?)
case (condition\nnewline)
    :Activity;
case (hello)
    :Activity;
endswitch
@enduml""",
            "svg": """<ellipse cx="93.75" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="79.75,50,107.75,50,119.75,62,107.75,74,79.75,74,67.75,62,79.75,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="79.75" y="65.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="134.5083"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="155.647" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="113.5" y="121.7036"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="123.5" y="142.8423" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="93.75,178.4771,93.75,178.4771,105.75,190.4771,93.75,202.4771,93.75,202.4771,81.75,190.4771,93.75,178.4771" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="67.75" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="134.5083"></line><polygon fill="#181818" points="38.5,124.5083,42.5,134.5083,46.5,124.5083,42.5,128.5083" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="51" x="42.5" y="95.3047">condition</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="43" x="42.5" y="108.1094">newline</text><line style="stroke:#181818;stroke-width:1.0;" x1="119.75" x2="145" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145" x2="145" y1="62" y2="121.7036"></line><polygon fill="#181818" points="141,111.7036,145,121.7036,149,111.7036,145,115.7036" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="27" x="145" y="95.3047">hello</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="168.4771" y2="190.4771"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="81.75" y1="190.4771" y2="190.4771"></line><polygon fill="#181818" points="71.75,186.4771,81.75,190.4771,71.75,194.4771,75.75,190.4771" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145" x2="145" y1="155.6724" y2="190.4771"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145" x2="105.75" y1="190.4771" y2="190.4771"></line><polygon fill="#181818" points="115.75,186.4771,105.75,190.4771,115.75,194.4771,111.75,190.4771" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="93.75" x2="93.75" y1="30" y2="50"></line><polygon fill="#181818" points="89.75,40,93.75,50,97.75,40,93.75,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#181818" points="38.5,124.5083,42.5,134.5083,46.5,124.5083,42.5,128.5083" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "text": "hello",
        }
        with client:
            response = client.post(
                "/editArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
switch (test?)
case (hello)
    :Activity;
case (hello)
    :Activity;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_delete_switch_case_nestedswitch(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
    switch (test?)
    case ( condition 1)
        :Activity;
    case ( condition 2)
        :Activity;
    endswitch
case ( condition 2)
    :Activity;
endswitch
@enduml""",
            "svg": """<ellipse cx="177.25" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="163.25,50,191.25,50,203.25,62,191.25,74,163.25,74,151.25,62,163.25,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="163.25" y="65.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="87" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="97" y="130.748" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="104.5,163.5781,132.5,163.5781,144.5,175.5781,132.5,187.5781,104.5,187.5781,92.5,175.5781,104.5,163.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="104.5" y="179.3862" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="223.1875"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="244.3262" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="128.5" y="223.1875"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="138.5" y="244.3262" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="118.5,267.1563,118.5,267.1563,130.5,279.1563,118.5,291.1563,118.5,291.1563,106.5,279.1563,118.5,267.1563" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="236" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="246" y="130.748" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="177.25,301.1563,177.25,301.1563,189.25,313.1563,177.25,325.1563,177.25,325.1563,165.25,313.1563,177.25,301.1563" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="92.5" x2="42.5" y1="175.5781" y2="175.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="175.5781" y2="223.1875"></line><polygon fill="#181818" points="38.5,213.1875,42.5,223.1875,46.5,213.1875,42.5,217.1875" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="46.5" y="203.1909">condition 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="144.5" x2="160" y1="175.5781" y2="175.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="175.5781" y2="223.1875"></line><polygon fill="#181818" points="156,213.1875,160,223.1875,164,213.1875,160,217.1875" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="164" y="203.1909">condition 2</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="257.1563" y2="279.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="106.5" y1="279.1563" y2="279.1563"></line><polygon fill="#181818" points="96.5,275.1563,106.5,279.1563,96.5,283.1563,100.5,279.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="257.1563" y2="279.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="130.5" y1="279.1563" y2="279.1563"></line><polygon fill="#181818" points="140.5,275.1563,130.5,279.1563,140.5,283.1563,136.5,279.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="118.5" y1="143.5781" y2="163.5781"></line><polygon fill="#181818" points="114.5,153.5781,118.5,163.5781,122.5,153.5781,118.5,157.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="151.25" x2="118.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="118.5" y1="62" y2="109.6094"></line><polygon fill="#181818" points="114.5,99.6094,118.5,109.6094,122.5,99.6094,118.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="122.5" y="89.6128">condition 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="203.25" x2="267.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="267.5" x2="267.5" y1="62" y2="109.6094"></line><polygon fill="#181818" points="263.5,99.6094,267.5,109.6094,271.5,99.6094,267.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="271.5" y="89.6128">condition 2</text><line style="stroke:#181818;stroke-width:1.0;" x1="118.5" x2="118.5" y1="291.1563" y2="313.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="165.25" y1="313.1563" y2="313.1563"></line><polygon fill="#181818" points="155.25,309.1563,165.25,313.1563,155.25,317.1563,159.25,313.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="267.5" x2="267.5" y1="143.5781" y2="313.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="267.5" x2="189.25" y1="313.1563" y2="313.1563"></line><polygon fill="#181818" points="199.25,309.1563,189.25,313.1563,199.25,317.1563,195.25,313.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="177.25" x2="177.25" y1="30" y2="50"></line><polygon fill="#181818" points="173.25,40,177.25,50,181.25,40,177.25,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#181818" points="114.5,99.6094,118.5,109.6094,122.5,99.6094,118.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
switch (test?)
case ( condition 2)
    :Activity;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_delete_switch_case(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
case ( condition 2)
    :Activity;
endswitch
@enduml""",
            "svg": """<ellipse cx="118.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="104.5,50,132.5,50,144.5,62,132.5,74,104.5,74,92.5,62,104.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="104.5" y="65.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="130.748" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="128.5" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="138.5" y="130.748" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="118.5,153.5781,118.5,153.5781,130.5,165.5781,118.5,177.5781,118.5,177.5781,106.5,165.5781,118.5,153.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="92.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="109.6094"></line><polygon fill="#181818" points="38.5,99.6094,42.5,109.6094,46.5,99.6094,42.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="46.5" y="89.6128">condition 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="144.5" x2="160" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="62" y2="109.6094"></line><polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="164" y="89.6128">condition 2</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="106.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="96.5,161.5781,106.5,165.5781,96.5,169.5781,100.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="130.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="140.5,161.5781,130.5,165.5781,140.5,169.5781,136.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="118.5" y1="30" y2="50"></line><polygon fill="#181818" points="114.5,40,118.5,50,122.5,40,118.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_edit_switch_case(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
case ( condition 2)
    :Activity;
endswitch
@enduml""",
            "svg": """<ellipse cx="118.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="104.5,50,132.5,50,144.5,62,132.5,74,104.5,74,92.5,62,104.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="104.5" y="65.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="130.748" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="128.5" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="138.5" y="130.748" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="118.5,153.5781,118.5,153.5781,130.5,165.5781,118.5,177.5781,118.5,177.5781,106.5,165.5781,118.5,153.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="92.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="109.6094"></line><polygon fill="#181818" points="38.5,99.6094,42.5,109.6094,46.5,99.6094,42.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="46.5" y="89.6128">condition 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="144.5" x2="160" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="62" y2="109.6094"></line><polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="164" y="89.6128">condition 2</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="106.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="96.5,161.5781,106.5,165.5781,96.5,169.5781,100.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="130.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="140.5,161.5781,130.5,165.5781,140.5,169.5781,136.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="118.5" y1="30" y2="50"></line><polygon fill="#181818" points="114.5,40,118.5,50,122.5,40,118.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "text": "hello",
        }
        with client:
            response = client.post(
                "/editArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
case (hello)
    :Activity;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_edit_arrow(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="84.3594"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="105.3281" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="91" x="126.5" y="159.8828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="67" x="140.5" y="180.8516" style="pointer-events: none;">2. activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="84.3594"></line><polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="259" x="176" y="51.3047">Nsmf_PDUSession_CreateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="105" x="176" y="64.1094">received from AMF</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="118.3281" y2="159.8828"></line><polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="82" x="176" y="139.6328">label on arrow</text>""",
            "svgelement": """<polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "text": "hello",
        }
        with client:
            response = client.post(
                "/editArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
->hello;
: 2. activity2;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_getarrowtext(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="84.3594"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="105.3281" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="91" x="126.5" y="159.8828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="67" x="140.5" y="180.8516" style="pointer-events: none;">2. activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="84.3594"></line><polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="259" x="176" y="51.3047">Nsmf_PDUSession_CreateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="105" x="176" y="64.1094">received from AMF</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="118.3281" y2="159.8828"></line><polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="82" x="176" y="139.6328">label on arrow</text>""",
            "svgelement": """<polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getArrowText",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = "label on arrow"
            assert response.data.decode("utf-8") == expected_result

    def test_deletearrow3(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="84.3594"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="105.3281" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="91" x="126.5" y="159.8828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="67" x="140.5" y="180.8516" style="pointer-events: none;">2. activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="84.3594"></line><polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="259" x="176" y="51.3047">Nsmf_PDUSession_CreateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="105" x="176" y="64.1094">received from AMF</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="118.3281" y2="159.8828"></line><polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="82" x="176" y="139.6328">label on arrow</text>""",
            "svgelement": """<polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
: 2. activity2;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_deletearrow2(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request\nreceived from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="84.3594"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="105.3281" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="91" x="126.5" y="159.8828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="67" x="140.5" y="180.8516" style="pointer-events: none;">2. activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="84.3594"></line><polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="259" x="176" y="51.3047">Nsmf_PDUSession_CreateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="105" x="176" y="64.1094">received from AMF</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="118.3281" y2="159.8828"></line><polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="82" x="176" y="139.6328">label on arrow</text>""",
            "svgelement": """<polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_deletearrow(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
  ->Hej;
  :Activity;
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="71.5547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="92.5234" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="71.5547"></line><polygon fill="#181818" points="38.5,61.5547,42.5,71.5547,46.5,61.5547,42.5,65.5547" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="18" x="46.5" y="51.3047">Hej</text>""",
            "svgelement": """<polygon fill="#181818" points="38.5,61.5547,42.5,71.5547,46.5,61.5547,42.5,65.5547" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
  :Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result
