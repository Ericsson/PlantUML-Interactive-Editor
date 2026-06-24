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

"""Tests for fork/join parallel processing element routes."""

from flask import json


class TestAppRoutesFork:
    def test_delfork3(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action;
fork again
  :action;
fork
  :action;
fork again
  :action;
end fork
end fork
  :Activity;
@enduml""",
            "line": 11,
        }
        with client:
            response = client.post(
                "/deleteFork2",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
  :Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_delfork2(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action;
fork again
  :action;
end fork
@enduml""",
            "line": 6,
        }
        with client:
            response = client.post(
                "/deleteFork2",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_togglefork3(self, client):
        test_data = {
            "plantuml": """@startuml
fork
    :action;
end fork
@enduml""",
            "line": 3,
        }
        with client:
            response = client.post(
                "/forkToggle2",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
fork
    :action;
end merge
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_togglefork2(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action;
fork again
  :action;
end fork
@enduml""",
            "line": 6,
        }
        with client:
            response = client.post(
                "/forkToggle2",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
fork
  :action;
fork again
  :action;
end merge
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addtofork(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action;
fork again
  :action;
end fork
@enduml""",
            "line": 6,
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToFork",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
fork
  :action;
fork again
  :action;
end fork
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_forktogglefork(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
end merge
stop
@enduml""",
            "svg": """<ellipse cx="139.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="23" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="33" y="96.9688" style="pointer-events: none;">action 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="104" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="114" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="185" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="195" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="129.9688"></rect><ellipse cx="139.5" cy="166.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="139.5" cy="166.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="56" y2="76"></line><polygon fill="#181818" points="54.5,66,58.5,76,62.5,66,58.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="56" y2="76"></line><polygon fill="#181818" points="135.5,66,139.5,76,143.5,66,139.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="56" y2="76"></line><polygon fill="#181818" points="216.5,66,220.5,76,224.5,66,220.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="54.5,119.9688,58.5,129.9688,62.5,119.9688,58.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="135.5,119.9688,139.5,129.9688,143.5,119.9688,139.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="216.5,119.9688,220.5,129.9688,224.5,119.9688,220.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="30" y2="50"></line><polygon fill="#181818" points="135.5,40,139.5,50,143.5,40,139.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="135.5,145.9688,139.5,155.9688,143.5,145.9688,139.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect>""",
        }
        with client:
            response = client.post(
                "/forkToggle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
end fork
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_forktogglemerge(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
end fork
stop
@enduml""",
            "svg": """<ellipse cx="139.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="23" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="33" y="96.9688" style="pointer-events: none;">action 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="104" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="114" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="185" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="195" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="129.9688"></rect><ellipse cx="139.5" cy="166.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="139.5" cy="166.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="56" y2="76"></line><polygon fill="#181818" points="54.5,66,58.5,76,62.5,66,58.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="56" y2="76"></line><polygon fill="#181818" points="135.5,66,139.5,76,143.5,66,139.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="56" y2="76"></line><polygon fill="#181818" points="216.5,66,220.5,76,224.5,66,220.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="54.5,119.9688,58.5,129.9688,62.5,119.9688,58.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="135.5,119.9688,139.5,129.9688,143.5,119.9688,139.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="216.5,119.9688,220.5,129.9688,224.5,119.9688,220.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="30" y2="50"></line><polygon fill="#181818" points="135.5,40,139.5,50,143.5,40,139.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="135.5,145.9688,139.5,155.9688,143.5,145.9688,139.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect>""",
        }
        with client:
            response = client.post(
                "/forkToggle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
end merge
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_forkagainwithnestedmerge(self, client):
        test_data = {
            "plantuml": """@startuml
fork
  :action;
fork again
  :action;
fork
  :action;
fork again
  :action;
fork again
  :action;
end merge
fork again
  :action;
fork
  :action;
fork again
  :action;
fork
  :action;
fork again
  :acation;
end fork
fork again
  :actioasdn;
fork again
  :action;
fork again
  :action;
end fork
end fork
stop
@enduml""",
            "svg": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="856.5" x="11" y="11"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="23" y="157.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="33" y="178.9375" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="173" y="88.4844"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="183" y="109.4531" style="pointer-events: none;">action</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="221" x="92" y="157.4531"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="104" y="183.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="114" y="204.4219" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="173" y="183.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="183" y="204.4219" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="242" y="183.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="252" y="204.4219" style="pointer-events: none;">action</text><polygon fill="#F1F1F1" points="202.5,237.4219,214.5,249.4219,202.5,261.4219,190.5,249.4219,202.5,237.4219" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="573.5" y="37"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="583.5" y="57.9688" style="pointer-events: none;">action</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="532.5" x="323" y="105.9688"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="335" y="192.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="345" y="213.4219" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="475" y="131.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="485" y="152.9375" style="pointer-events: none;">action</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="182" x="413.5" y="200.9375"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="427.5" y="226.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="437.5" y="247.9063" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="67" x="514.5" y="226.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="47" x="524.5" y="247.9063" style="pointer-events: none;">acation</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="182" x="413.5" y="280.9063"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="82" x="623.5" y="192.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="62" x="633.5" y="213.4219" style="pointer-events: none;">actioasdn</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="715.5" y="192.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="725.5" y="213.4219" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="784.5" y="192.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="794.5" y="213.4219" style="pointer-events: none;">action</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="532.5" x="323" y="306.9063"></rect><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="856.5" x="11" y="332.9063"></rect><ellipse cx="415" cy="369.9063" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="415" cy="369.9063" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133.5" x2="133.5" y1="163.4531" y2="183.4531"></line><polygon fill="#181818" points="129.5,173.4531,133.5,183.4531,137.5,173.4531,133.5,177.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="202.5" x2="202.5" y1="163.4531" y2="183.4531"></line><polygon fill="#181818" points="198.5,173.4531,202.5,183.4531,206.5,173.4531,202.5,177.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="271.5" x2="271.5" y1="163.4531" y2="183.4531"></line><polygon fill="#181818" points="267.5,173.4531,271.5,183.4531,275.5,173.4531,271.5,177.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133.5" x2="133.5" y1="217.4219" y2="249.4219"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133.5" x2="190.5" y1="249.4219" y2="249.4219"></line><polygon fill="#181818" points="180.5,245.4219,190.5,249.4219,180.5,253.4219,184.5,249.4219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="202.5" x2="202.5" y1="217.4219" y2="237.4219"></line><polygon fill="#181818" points="198.5,227.4219,202.5,237.4219,206.5,227.4219,202.5,231.4219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="271.5" x2="271.5" y1="217.4219" y2="249.4219"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="271.5" x2="214.5" y1="249.4219" y2="249.4219"></line><polygon fill="#181818" points="224.5,245.4219,214.5,249.4219,224.5,253.4219,220.5,249.4219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="202.5" x2="202.5" y1="122.4531" y2="157.4531"></line><polygon fill="#181818" points="198.5,147.4531,202.5,157.4531,206.5,147.4531,202.5,151.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="457" x2="457" y1="206.9375" y2="226.9375"></line><polygon fill="#181818" points="453,216.9375,457,226.9375,461,216.9375,457,220.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="548" x2="548" y1="206.9375" y2="226.9375"></line><polygon fill="#181818" points="544,216.9375,548,226.9375,552,216.9375,548,220.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="457" x2="457" y1="260.9063" y2="280.9063"></line><polygon fill="#181818" points="453,270.9063,457,280.9063,461,270.9063,457,274.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="548" x2="548" y1="260.9063" y2="280.9063"></line><polygon fill="#181818" points="544,270.9063,548,280.9063,552,270.9063,548,274.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="504.5" x2="504.5" y1="165.9375" y2="200.9375"></line><polygon fill="#181818" points="500.5,190.9375,504.5,200.9375,508.5,190.9375,504.5,194.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="364.5" x2="364.5" y1="111.9688" y2="192.4531"></line><polygon fill="#181818" points="360.5,182.4531,364.5,192.4531,368.5,182.4531,364.5,186.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="504.5" x2="504.5" y1="111.9688" y2="131.9688"></line><polygon fill="#181818" points="500.5,121.9688,504.5,131.9688,508.5,121.9688,504.5,125.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="664.5" x2="664.5" y1="111.9688" y2="192.4531"></line><polygon fill="#181818" points="660.5,182.4531,664.5,192.4531,668.5,182.4531,664.5,186.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="745" x2="745" y1="111.9688" y2="192.4531"></line><polygon fill="#181818" points="741,182.4531,745,192.4531,749,182.4531,745,186.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="814" x2="814" y1="111.9688" y2="192.4531"></line><polygon fill="#181818" points="810,182.4531,814,192.4531,818,182.4531,814,186.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="364.5" x2="364.5" y1="226.4219" y2="306.9063"></line><polygon fill="#181818" points="360.5,296.9063,364.5,306.9063,368.5,296.9063,364.5,300.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="504.5" x2="504.5" y1="286.9063" y2="306.9063"></line><polygon fill="#181818" points="500.5,296.9063,504.5,306.9063,508.5,296.9063,504.5,300.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="664.5" x2="664.5" y1="226.4219" y2="306.9063"></line><polygon fill="#181818" points="660.5,296.9063,664.5,306.9063,668.5,296.9063,664.5,300.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="745" x2="745" y1="226.4219" y2="306.9063"></line><polygon fill="#181818" points="741,296.9063,745,306.9063,749,296.9063,745,300.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="814" x2="814" y1="226.4219" y2="306.9063"></line><polygon fill="#181818" points="810,296.9063,814,306.9063,818,296.9063,814,300.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="603" x2="603" y1="70.9688" y2="105.9688"></line><polygon fill="#181818" points="599,95.9688,603,105.9688,607,95.9688,603,99.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="52.5" y1="17" y2="157.9688"></line><polygon fill="#181818" points="48.5,147.9688,52.5,157.9688,56.5,147.9688,52.5,151.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="202.5" x2="202.5" y1="17" y2="88.4844"></line><polygon fill="#181818" points="198.5,78.4844,202.5,88.4844,206.5,78.4844,202.5,82.4844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="603" x2="603" y1="17" y2="37"></line><polygon fill="#181818" points="599,27,603,37,607,27,603,31" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="52.5" y1="191.9375" y2="332.9063"></line><polygon fill="#181818" points="48.5,322.9063,52.5,332.9063,56.5,322.9063,52.5,326.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="202.5" x2="202.5" y1="261.4219" y2="332.9063"></line><polygon fill="#181818" points="198.5,322.9063,202.5,332.9063,206.5,322.9063,202.5,326.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="603" x2="603" y1="312.9063" y2="332.9063"></line><polygon fill="#181818" points="599,322.9063,603,332.9063,607,322.9063,603,326.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="415" x2="415" y1="338.9063" y2="358.9063"></line><polygon fill="#181818" points="411,348.9063,415,358.9063,419,348.9063,415,352.9063" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="532.5" x="323" y="105.9688"></rect>""",
        }
        with client:
            response = client.post(
                "/forkAgain",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
fork
  :action;
fork again
  :action;
fork
  :action;
fork again
  :action;
fork again
  :action;
end merge
fork again
  :action;
fork
  :action;
fork again
  :action;
fork
  :action;
fork again
  :acation;
end fork
fork again
  :actioasdn;
fork again
  :action;
fork again
  :action;
fork again
  :action;
end fork
end fork
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_forkagain(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
end fork
stop
@enduml""",
            "svg": """<ellipse cx="139.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="23" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="33" y="96.9688" style="pointer-events: none;">action 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="104" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="114" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="185" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="195" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="129.9688"></rect><ellipse cx="139.5" cy="166.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="139.5" cy="166.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="56" y2="76"></line><polygon fill="#181818" points="54.5,66,58.5,76,62.5,66,58.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="56" y2="76"></line><polygon fill="#181818" points="135.5,66,139.5,76,143.5,66,139.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="56" y2="76"></line><polygon fill="#181818" points="216.5,66,220.5,76,224.5,66,220.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="54.5,119.9688,58.5,129.9688,62.5,119.9688,58.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="135.5,119.9688,139.5,129.9688,143.5,119.9688,139.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="216.5,119.9688,220.5,129.9688,224.5,119.9688,220.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="30" y2="50"></line><polygon fill="#181818" points="135.5,40,139.5,50,143.5,40,139.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="135.5,145.9688,139.5,155.9688,143.5,145.9688,139.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect>""",
        }
        with client:
            response = client.post(
                "/forkAgain",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
fork again
  :action;
end fork
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deletenestedfork(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action 2;
fork
:action 1;
fork again
:action 2;
end fork
fork again
  :action 2;
fork
:action 1;
fork again
:action 2;
end fork
end fork
stop
@enduml""",
            "svg": """<ellipse cx="231" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="440" x="11" y="50"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="84.5" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="94.5" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="194" x="23" y="129.9688"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="35" y="155.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="45" y="176.9375" style="pointer-events: none;">action 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="134" y="155.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="144" y="176.9375" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="194" x="23" y="209.9375"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="306.5" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="316.5" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="194" x="245" y="129.9688"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="257" y="155.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="267" y="176.9375" style="pointer-events: none;">action 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="356" y="155.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="366" y="176.9375" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="194" x="245" y="209.9375"></rect><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="440" x="11" y="235.9375"></rect><ellipse cx="231" cy="272.9375" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="231" cy="272.9375" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="70.5" x2="70.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="66.5,145.9688,70.5,155.9688,74.5,145.9688,70.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="169.5" x2="169.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="165.5,145.9688,169.5,155.9688,173.5,145.9688,169.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="70.5" x2="70.5" y1="189.9375" y2="209.9375"></line><polygon fill="#181818" points="66.5,199.9375,70.5,209.9375,74.5,199.9375,70.5,203.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="169.5" x2="169.5" y1="189.9375" y2="209.9375"></line><polygon fill="#181818" points="165.5,199.9375,169.5,209.9375,173.5,199.9375,169.5,203.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="120" x2="120" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="116,119.9688,120,129.9688,124,119.9688,120,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="292.5" x2="292.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="288.5,145.9688,292.5,155.9688,296.5,145.9688,292.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="391.5" x2="391.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="387.5,145.9688,391.5,155.9688,395.5,145.9688,391.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="292.5" x2="292.5" y1="189.9375" y2="209.9375"></line><polygon fill="#181818" points="288.5,199.9375,292.5,209.9375,296.5,199.9375,292.5,203.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="391.5" x2="391.5" y1="189.9375" y2="209.9375"></line><polygon fill="#181818" points="387.5,199.9375,391.5,209.9375,395.5,199.9375,391.5,203.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="342" x2="342" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="338,119.9688,342,129.9688,346,119.9688,342,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="120" x2="120" y1="56" y2="76"></line><polygon fill="#181818" points="116,66,120,76,124,66,120,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="342" x2="342" y1="56" y2="76"></line><polygon fill="#181818" points="338,66,342,76,346,66,342,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="120" x2="120" y1="215.9375" y2="235.9375"></line><polygon fill="#181818" points="116,225.9375,120,235.9375,124,225.9375,120,229.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="342" x2="342" y1="215.9375" y2="235.9375"></line><polygon fill="#181818" points="338,225.9375,342,235.9375,346,225.9375,342,229.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="231" x2="231" y1="30" y2="50"></line><polygon fill="#181818" points="227,40,231,50,235,40,231,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="231" x2="231" y1="241.9375" y2="261.9375"></line><polygon fill="#181818" points="227,251.9375,231,261.9375,235,251.9375,231,255.9375" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="194" x="245" y="129.9688"></rect>""",
        }
        with client:
            response = client.post(
                "/deleteFork",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
fork
  :action 2;
fork
:action 1;
fork again
:action 2;
end fork
fork again
  :action 2;
end fork
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deletefork(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
end fork
stop
@enduml""",
            "svg": """<ellipse cx="139.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="23" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="33" y="96.9688" style="pointer-events: none;">action 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="104" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="114" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="185" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="195" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="129.9688"></rect><ellipse cx="139.5" cy="166.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="139.5" cy="166.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="56" y2="76"></line><polygon fill="#181818" points="54.5,66,58.5,76,62.5,66,58.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="56" y2="76"></line><polygon fill="#181818" points="135.5,66,139.5,76,143.5,66,139.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="56" y2="76"></line><polygon fill="#181818" points="216.5,66,220.5,76,224.5,66,220.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="54.5,119.9688,58.5,129.9688,62.5,119.9688,58.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="135.5,119.9688,139.5,129.9688,143.5,119.9688,139.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="216.5,119.9688,220.5,129.9688,224.5,119.9688,220.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="30" y2="50"></line><polygon fill="#181818" points="135.5,40,139.5,50,143.5,40,139.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="135.5,145.9688,139.5,155.9688,143.5,145.9688,139.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect>""",
        }
        with client:
            response = client.post(
                "/deleteFork",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml
