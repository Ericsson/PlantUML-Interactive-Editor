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

"""Tests for switch/case statement creation, editing, and adding cases."""

from flask import json


class TestAppRoutesSwitch:
    def test_gettext_switch(self, client):
        test_data = {
            "plantuml": """@startuml
switch (asdfasdfasdf)
case ( condition A )
:Text 1;
switch (hej)
case ( condition A )
:Text 1;
case ( condition B )
:Text 2;
case ( condition C )
:Text 3;
endswitch
case ( condition B )
:Text 2;
case ( condition C )
:Text 3;
endswitch
@enduml""",
            "svg": """<polygon fill="#F1F1F1" points="253,10,328,10,340,22,328,34,253,34,241,22,253,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="75" x="253" y="25.8081" style="pointer-events: none;">asdfasdfasdf</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="141.5" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="151.5" y="90.748" style="pointer-events: none;">Text 1</text><polygon fill="#F1F1F1" points="158.5,123.5781,182.5,123.5781,194.5,135.5781,182.5,147.5781,158.5,147.5781,146.5,135.5781,158.5,123.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="162" y="139.3862" style="pointer-events: none;">hej</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="11" y="183.1875"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="21" y="204.3262" style="pointer-events: none;">Text 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="120" y="183.1875"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="130" y="204.3262" style="pointer-events: none;">Text 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="240" y="183.1875"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="250" y="204.3262" style="pointer-events: none;">Text 3</text><polygon fill="#F1F1F1" points="170.5,237.1563,170.5,237.1563,182.5,249.1563,170.5,261.1563,170.5,261.1563,158.5,249.1563,170.5,237.1563" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="350" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="360" y="90.748" style="pointer-events: none;">Text 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="460" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="470" y="90.748" style="pointer-events: none;">Text 3</text><polygon fill="#F1F1F1" points="290.5,271.1563,290.5,271.1563,302.5,283.1563,290.5,295.1563,290.5,295.1563,278.5,283.1563,290.5,271.1563" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="146.5" x2="40" y1="135.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="40" y1="135.5781" y2="183.1875"></line><polygon fill="#181818" points="36,173.1875,40,183.1875,44,173.1875,40,177.1875" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="44" y="163.1909">condition A</text><line style="stroke:#181818;stroke-width:1.0;" x1="194.5" x2="269" y1="135.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="135.5781" y2="183.1875"></line><polygon fill="#181818" points="265,173.1875,269,183.1875,273,173.1875,269,177.1875" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="273" y="163.1909">condition C</text><line style="stroke:#181818;stroke-width:1.0;" x1="170.5" x2="170.5" y1="147.5781" y2="159.4479"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="149" y1="159.4479" y2="159.4479"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="159.4479" y2="183.1875"></line><polygon fill="#181818" points="145,173.1875,149,183.1875,153,173.1875,149,177.1875" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="153" y="164.1909">condition B</text><line style="stroke:#181818;stroke-width:1.0;" x1="40" x2="40" y1="217.1563" y2="249.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="158.5" y1="249.1563" y2="249.1563"></line><polygon fill="#181818" points="148.5,245.1563,158.5,249.1563,148.5,253.1563,152.5,249.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="217.1563" y2="249.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="182.5" y1="249.1563" y2="249.1563"></line><polygon fill="#181818" points="192.5,245.1563,182.5,249.1563,192.5,253.1563,188.5,249.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="217.1563" y2="222.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="170.5" y1="222.1563" y2="222.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="170.5" y1="222.1563" y2="237.1563"></line><polygon fill="#181818" points="166.5,227.1563,170.5,237.1563,174.5,227.1563,170.5,231.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="170.5" y1="103.5781" y2="123.5781"></line><polygon fill="#181818" points="166.5,113.5781,170.5,123.5781,174.5,113.5781,170.5,117.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="241" x2="170.5" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="170.5" y1="22" y2="69.6094"></line><polygon fill="#181818" points="166.5,59.6094,170.5,69.6094,174.5,59.6094,170.5,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="174.5" y="49.6128">condition A</text><line style="stroke:#181818;stroke-width:1.0;" x1="340" x2="489" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="489" x2="489" y1="22" y2="69.6094"></line><polygon fill="#181818" points="485,59.6094,489,69.6094,493,59.6094,489,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="493" y="49.6128">condition C</text><line style="stroke:#181818;stroke-width:1.0;" x1="379" x2="379" y1="22" y2="69.6094"></line><polygon fill="#181818" points="375,59.6094,379,69.6094,383,59.6094,379,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="383" y="44.6128">condition B</text><line style="stroke:#181818;stroke-width:1.0;" x1="170.5" x2="170.5" y1="261.1563" y2="283.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="278.5" y1="283.1563" y2="283.1563"></line><polygon fill="#181818" points="268.5,279.1563,278.5,283.1563,268.5,287.1563,272.5,283.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="489" x2="489" y1="103.5781" y2="283.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="489" x2="302.5" y1="283.1563" y2="283.1563"></line><polygon fill="#181818" points="312.5,279.1563,302.5,283.1563,312.5,287.1563,308.5,283.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="379" x2="379" y1="103.5781" y2="283.1563"></line><polygon fill="#181818" points="375,273.1563,379,283.1563,383,273.1563,379,277.1563" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="253,10,328,10,340,22,328,34,253,34,241,22,253,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getTextPoly",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            output = ["asdfasdfasdf", "", ""]
            json.loads(response.data.decode("utf-8")) == output

    def test_switch_again2(self, client):
        test_data = {
            "plantuml": """@startuml
switch (test?)
case ( condition A)
:Text 1;
case ( condition B)
:Text 2;
case ( condition 2)
:Text 3;
endswitch
@enduml""",
            "svg": """<polygon fill="#F1F1F1" points="156.5,10,184.5,10,196.5,22,184.5,34,156.5,34,144.5,22,156.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="156.5" y="25.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="11" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="21" y="90.748" style="pointer-events: none;">Text 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="120" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="130" y="90.748" style="pointer-events: none;">Text 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="230" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="240" y="90.748" style="pointer-events: none;">Text 3</text><polygon fill="#F1F1F1" points="170.5,123.5781,170.5,123.5781,182.5,135.5781,170.5,147.5781,170.5,147.5781,158.5,135.5781,170.5,123.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="144.5" x2="40" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="40" y1="22" y2="69.6094"></line><polygon fill="#181818" points="36,59.6094,40,69.6094,44,59.6094,40,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="44" y="49.6128">condition A</text><line style="stroke:#181818;stroke-width:1.0;" x1="196.5" x2="259" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="259" y1="22" y2="69.6094"></line><polygon fill="#181818" points="255,59.6094,259,69.6094,263,59.6094,259,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="263" y="49.6128">condition C</text><line style="stroke:#181818;stroke-width:1.0;" x1="170.5" x2="170.5" y1="34" y2="45.8698"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="149" y1="45.8698" y2="45.8698"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="45.8698" y2="69.6094"></line><polygon fill="#181818" points="145,59.6094,149,69.6094,153,59.6094,149,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="153" y="50.6128">condition B</text><line style="stroke:#181818;stroke-width:1.0;" x1="40" x2="40" y1="103.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="158.5" y1="135.5781" y2="135.5781"></line><polygon fill="#181818" points="148.5,131.5781,158.5,135.5781,148.5,139.5781,152.5,135.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="259" y1="103.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="182.5" y1="135.5781" y2="135.5781"></line><polygon fill="#181818" points="192.5,131.5781,182.5,135.5781,192.5,139.5781,188.5,135.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="103.5781" y2="108.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="170.5" y1="108.5781" y2="108.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="170.5" y1="108.5781" y2="123.5781"></line><polygon fill="#181818" points="166.5,113.5781,170.5,123.5781,174.5,113.5781,170.5,117.5781" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="156.5,10,184.5,10,196.5,22,184.5,34,156.5,34,144.5,22,156.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/switchAgain",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
switch (test?)
case ( condition A)
:Text 1;
case ( condition B)
:Text 2;
case ( condition 2)
:Text 3;
case ( condition 3)
:Activity;
endswitch
@enduml"""

            assert response.data.decode("utf-8") == expected_puml

    def test_switch_again(self, client):
        test_data = {
            "plantuml": """@startuml
switch (test?)
case ( condition A )
:Text 1;
case ( condition B )
:Text 2;
case ( condition C )
:Text 3;
endswitch
@enduml""",
            "svg": """<polygon fill="#F1F1F1" points="156.5,10,184.5,10,196.5,22,184.5,34,156.5,34,144.5,22,156.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="156.5" y="25.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="11" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="21" y="90.748" style="pointer-events: none;">Text 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="120" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="130" y="90.748" style="pointer-events: none;">Text 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="230" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="240" y="90.748" style="pointer-events: none;">Text 3</text><polygon fill="#F1F1F1" points="170.5,123.5781,170.5,123.5781,182.5,135.5781,170.5,147.5781,170.5,147.5781,158.5,135.5781,170.5,123.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="144.5" x2="40" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="40" y1="22" y2="69.6094"></line><polygon fill="#181818" points="36,59.6094,40,69.6094,44,59.6094,40,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="44" y="49.6128">condition A</text><line style="stroke:#181818;stroke-width:1.0;" x1="196.5" x2="259" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="259" y1="22" y2="69.6094"></line><polygon fill="#181818" points="255,59.6094,259,69.6094,263,59.6094,259,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="263" y="49.6128">condition C</text><line style="stroke:#181818;stroke-width:1.0;" x1="170.5" x2="170.5" y1="34" y2="45.8698"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="149" y1="45.8698" y2="45.8698"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="45.8698" y2="69.6094"></line><polygon fill="#181818" points="145,59.6094,149,69.6094,153,59.6094,149,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="153" y="50.6128">condition B</text><line style="stroke:#181818;stroke-width:1.0;" x1="40" x2="40" y1="103.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="158.5" y1="135.5781" y2="135.5781"></line><polygon fill="#181818" points="148.5,131.5781,158.5,135.5781,148.5,139.5781,152.5,135.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="259" y1="103.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="182.5" y1="135.5781" y2="135.5781"></line><polygon fill="#181818" points="192.5,131.5781,182.5,135.5781,192.5,139.5781,188.5,135.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="103.5781" y2="108.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="170.5" y1="108.5781" y2="108.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="170.5" y1="108.5781" y2="123.5781"></line><polygon fill="#181818" points="166.5,113.5781,170.5,123.5781,174.5,113.5781,170.5,117.5781" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="156.5,10,184.5,10,196.5,22,184.5,34,156.5,34,144.5,22,156.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/switchAgain",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
switch (test?)
case ( condition A )
:Text 1;
case ( condition B )
:Text 2;
case ( condition C )
:Text 3;
case ( condition 1)
:Activity;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_switch1(self, client):
        test_data = {
            "plantuml": """@startuml
switch (test?)
case ( condition A )
:Text 1;
case ( condition B )
:Text 2;
case ( condition C )
:Text 3;
endswitch
@enduml""",
            "svg": """<polygon fill="#F1F1F1" points="156.5,10,184.5,10,196.5,22,184.5,34,156.5,34,144.5,22,156.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="156.5" y="25.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="11" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="21" y="90.748" style="pointer-events: none;">Text 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="120" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="130" y="90.748" style="pointer-events: none;">Text 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="230" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="240" y="90.748" style="pointer-events: none;">Text 3</text><polygon fill="#F1F1F1" points="170.5,123.5781,170.5,123.5781,182.5,135.5781,170.5,147.5781,170.5,147.5781,158.5,135.5781,170.5,123.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="144.5" x2="40" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="40" y1="22" y2="69.6094"></line><polygon fill="#181818" points="36,59.6094,40,69.6094,44,59.6094,40,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="44" y="49.6128">condition A</text><line style="stroke:#181818;stroke-width:1.0;" x1="196.5" x2="259" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="259" y1="22" y2="69.6094"></line><polygon fill="#181818" points="255,59.6094,259,69.6094,263,59.6094,259,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="263" y="49.6128">condition C</text><line style="stroke:#181818;stroke-width:1.0;" x1="170.5" x2="170.5" y1="34" y2="45.8698"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="149" y1="45.8698" y2="45.8698"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="45.8698" y2="69.6094"></line><polygon fill="#181818" points="145,59.6094,149,69.6094,153,59.6094,149,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="153" y="50.6128">condition B</text><line style="stroke:#181818;stroke-width:1.0;" x1="40" x2="40" y1="103.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="158.5" y1="135.5781" y2="135.5781"></line><polygon fill="#181818" points="148.5,131.5781,158.5,135.5781,148.5,139.5781,152.5,135.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="259" y1="103.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="182.5" y1="135.5781" y2="135.5781"></line><polygon fill="#181818" points="192.5,131.5781,182.5,135.5781,192.5,139.5781,188.5,135.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="103.5781" y2="108.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="170.5" y1="108.5781" y2="108.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="170.5" y1="108.5781" y2="123.5781"></line><polygon fill="#181818" points="166.5,113.5781,170.5,123.5781,174.5,113.5781,170.5,117.5781" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "State",
            "branch1": "bam",
            "branch2": "bom",
            "svgelement": """<polygon fill="#F1F1F1" points="156.5,10,184.5,10,196.5,22,184.5,34,156.5,34,144.5,22,156.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
switch (State)
case ( condition A )
:Text 1;
case ( condition B )
:Text 2;
case ( condition C )
:Text 3;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_puml
