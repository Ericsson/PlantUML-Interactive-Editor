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

"""Tests for connector element creation, editing, deletion, and detach toggling."""

from flask import json


class TestAppRoutesConnector:
    def test_get_char_connector(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
note left
note
end note
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/getCharConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected = "A"
            assert response.data.decode("utf-8") == expected

    def test_edit_colored_connector_with_colored_activity(self, client):
        test_data = {
            "plantuml": """@startuml
#yellow:Activity;
#green:(A)
note left
note
end note
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
            "text": "C",
        }
        with client:
            response = client.post(
                "/editCharConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
#yellow:Activity;
#green:(C)
note left
note
end note
detach
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_colored_connector(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
#green:(A)
note left
note
end note
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
            "text": "C",
        }
        with client:
            response = client.post(
                "/editCharConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
#green:(C)
note left
note
end note
detach
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_connector(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
note left
note
end note
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
            "text": "C",
        }
        with client:
            response = client.post(
                "/editCharConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
(C)
note left
note
end note
detach
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_while_connector(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
note left
note
end note
detach
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
            "where": "below",
            "type": "while",
        }
        with client:
            response = client.post(
                "/addToConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
(A)
note left
note
end note
detach
while (Statement) is (yes)
:Activity;
endwhile (no)
:Activity;
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_activity_connector2(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
note left
note
end note
detach
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
            "where": "below",
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
(A)
note left
note
end note
detach
:Activity 1;
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_notetoconnector(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
            "where": "below",
            "type": "note",
        }
        with client:
            response = client.post(
                "/addToConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
(A)
note right
note
end note
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_toggle_detach2(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
note right
note
end note
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/detachConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
(A)
note right
note
end note
detach
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_toggle_detach(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
detach
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/detachConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
(A)
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteconnectorwithnote(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
note left
note
end note
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/connectorDelete",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteconnector(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
detach
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/connectorDelete",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_get_connector_line(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
detach
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/getConnectorLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = 3

            # Assert the result value is as expected
            assert result_value == expected_puml
