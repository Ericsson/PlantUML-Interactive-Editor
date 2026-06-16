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

"""Tests for start/stop/end ellipse elements and adding elements below them."""

from flask import json


class TestAppRoutesEllipse:
    def test_addconnectorbelowwithconnector(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
(A)
detach
stop
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="113.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,110.1406 L41,114.4844 L44.2188,114.4844 L42.6094,110.1406 Z M41.9375,108.9688 L43.2813,108.9688 L46.6094,117.7188 L45.375,117.7188 L44.5781,115.4688 L40.6406,115.4688 L39.8438,117.7188 L38.5938,117.7188 L41.9375,108.9688 Z " fill="#000000"></path><ellipse cx="42.5" cy="144.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="42.5" cy="144.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="83.9688" y2="103.9688"></line><polygon fill="#181818" points="38.5,93.9688,42.5,103.9688,46.5,93.9688,42.5,97.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="144.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse>""",
            "where": "below",
            "type": "connector",
        }
        with client:
            response = client.post(
                "/addToEllipse",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
:Activity;
(A)
detach
stop
(C)
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addactivitybelowwithconnector(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
(A)
detach
stop
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="113.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,110.1406 L41,114.4844 L44.2188,114.4844 L42.6094,110.1406 Z M41.9375,108.9688 L43.2813,108.9688 L46.6094,117.7188 L45.375,117.7188 L44.5781,115.4688 L40.6406,115.4688 L39.8438,117.7188 L38.5938,117.7188 L41.9375,108.9688 Z " fill="#000000"></path><ellipse cx="42.5" cy="144.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="42.5" cy="144.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="83.9688" y2="103.9688"></line><polygon fill="#181818" points="38.5,93.9688,42.5,103.9688,46.5,93.9688,42.5,97.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="144.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse>""",
            "where": "below",
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToEllipse",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
:Activity;
(A)
detach
stop
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteellipse(self, client):
        test_data = {
            "plantuml": """@startuml
start
stop
@enduml""",
            "svg": """<ellipse cx="24" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="24" cy="61" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="24" cy="61" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="30" y2="50"></line><polygon fill="#181818" points="20,40,24,50,28,40,24,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="24" cy="61" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/deleteEllipse",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_get_ellipse_line(self, client):
        test_data = {
            "plantuml": """@startuml
start
stop
@enduml""",
            "svg": """<ellipse cx="24" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="24" cy="61" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="24" cy="61" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="30" y2="50"></line><polygon fill="#181818" points="20,40,24,50,28,40,24,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="24" cy="61" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/getEllipseLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = 3

            # Assert the result value is as expected
            assert result_value == expected_puml
