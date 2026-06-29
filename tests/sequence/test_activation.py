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

"""Tests for sequence diagram activation bars (activate/deactivate/destroy)."""

import re

from flask import json
from plantuml_gui.sequence.activation import add_activation
from plantuml_gui.shared.render import _create_svg_from_uml

THREE_MESSAGE_PUML = """@startuml
participant alice
participant bob
alice -> bob: m1
bob -> alice: m2
alice -> bob: m3
@enduml"""

# Message Y-positions for THREE_MESSAGE_PUML (from the rendered SVG):
#   m1 ~ 67.4, m2 ~ 96.6, m3 ~ 125.7
# These constants pick points that fall between messages.
Y_BEFORE_M2 = 80.0
Y_AFTER_M2 = 110.0
Y_BEFORE_M1 = 55.0
Y_AFTER_M3 = 140.0


def extract_g_element(svg_string):
    match = re.search(r"<g>(.*?)</g>", svg_string, re.DOTALL)
    if match:
        return f"<g>{match.group(1)}</g>"
    return None


def svg_for(puml):
    return extract_g_element(_create_svg_from_uml(puml))


class TestAddActivation:
    def test_activate_deactivate_wraps_message(self):
        svg = svg_for(THREE_MESSAGE_PUML)
        result = add_activation(
            THREE_MESSAGE_PUML, svg, "bob", Y_BEFORE_M2, Y_AFTER_M2, "deactivate"
        )
        lines = result.splitlines()
        activate_at = lines.index("activate bob")
        deactivate_at = lines.index("deactivate bob")
        # activate precedes its close, and the bar wraps the m2 message line.
        assert activate_at < deactivate_at
        assert lines[activate_at + 1] == "bob -> alice: m2"
        assert lines[deactivate_at - 1] == "bob -> alice: m2"

    def test_destroy_produces_destroy_line(self):
        svg = svg_for(THREE_MESSAGE_PUML)
        result = add_activation(
            THREE_MESSAGE_PUML, svg, "bob", Y_BEFORE_M2, Y_AFTER_M2, "destroy"
        )
        assert "activate bob" in result
        assert "destroy bob" in result
        assert "deactivate bob" not in result

    def test_balanced_pair_is_added(self):
        svg = svg_for(THREE_MESSAGE_PUML)
        result = add_activation(
            THREE_MESSAGE_PUML, svg, "alice", Y_BEFORE_M1, Y_AFTER_M3, "deactivate"
        )
        lines = result.splitlines()
        assert lines.count("activate alice") == 1
        assert lines.count("deactivate alice") == 1

    def test_nested_activation_stays_balanced_and_ordered(self):
        svg = svg_for(THREE_MESSAGE_PUML)
        # Outer bar wraps all three messages.
        outer = add_activation(
            THREE_MESSAGE_PUML, svg, "bob", Y_BEFORE_M1, Y_AFTER_M3, "deactivate"
        )
        # Inner bar wraps only m2; reuse original svg coordinates (geometry of
        # the original render is what the frontend would have sent).
        nested = add_activation(
            outer, svg, "bob", Y_BEFORE_M2, Y_AFTER_M2, "deactivate"
        )
        lines = nested.splitlines()
        activate_positions = [i for i, ln in enumerate(lines) if ln == "activate bob"]
        deactivate_positions = [
            i for i, ln in enumerate(lines) if ln == "deactivate bob"
        ]
        assert len(activate_positions) == 2
        assert len(deactivate_positions) == 2
        # Properly nested: both activates come before both deactivates.
        assert max(activate_positions) < min(deactivate_positions)


class TestAddActivationRoute:
    def test_valid_request_returns_pair(self, client):
        svg = svg_for(THREE_MESSAGE_PUML)
        payload = {
            "plantuml": THREE_MESSAGE_PUML,
            "svg": svg,
            "participant": "bob",
            "startY": Y_BEFORE_M2,
            "endY": Y_AFTER_M2,
            "endType": "deactivate",
        }
        response = client.post(
            "/addActivation",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200
        result = response.get_json()["plantuml"]
        assert "activate bob" in result
        assert "deactivate bob" in result

    def test_destroy_request_returns_destroy_line(self, client):
        svg = svg_for(THREE_MESSAGE_PUML)
        payload = {
            "plantuml": THREE_MESSAGE_PUML,
            "svg": svg,
            "participant": "bob",
            "startY": Y_BEFORE_M2,
            "endY": Y_AFTER_M2,
            "endType": "destroy",
        }
        response = client.post(
            "/addActivation",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200
        result = response.get_json()["plantuml"]
        assert "activate bob" in result
        assert "destroy bob" in result

    def test_unknown_end_type_defaults_to_deactivate(self, client):
        svg = svg_for(THREE_MESSAGE_PUML)
        payload = {
            "plantuml": THREE_MESSAGE_PUML,
            "svg": svg,
            "participant": "bob",
            "startY": Y_BEFORE_M2,
            "endY": Y_AFTER_M2,
            "endType": "bogus",
        }
        response = client.post(
            "/addActivation",
            data=json.dumps(payload),
            content_type="application/json",
        )
        assert response.status_code == 200
        result = response.get_json()["plantuml"]
        assert "activate bob" in result
        assert "deactivate bob" in result
