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

THREE_MESSAGE_PUML = """@startuml
participant alice
participant bob
alice -> bob: m1
bob -> alice: m2
alice -> bob: m3
@enduml"""

# Line indexes in THREE_MESSAGE_PUML:
#   line 0: @startuml
#   line 1: participant alice
#   line 2: participant bob
#   line 3: alice -> bob: m1
#   line 4: bob -> alice: m2
#   line 5: alice -> bob: m3
#   line 6: @enduml
M1_INDEX = 3
M2_INDEX = 4
M3_INDEX = 5


class TestAddActivation:
    def test_activate_inserted_after_start_message(self):
        # Bar from m1 (start) to m2 (end): activate sits just below the start
        # message (m1), so m1 is above the bar and m2 is inside it.
        result = add_activation(
            THREE_MESSAGE_PUML, "bob", M1_INDEX, M2_INDEX, "deactivate"
        )
        lines = result.splitlines()
        activate_at = lines.index("activate bob")
        deactivate_at = lines.index("deactivate bob")
        assert activate_at < deactivate_at
        assert lines[activate_at - 1] == "alice -> bob: m1"  # activate is below m1
        assert lines[activate_at + 1] == "bob -> alice: m2"  # m2 is inside the bar
        assert lines[deactivate_at - 1] == "bob -> alice: m2"  # close is below m2

    def test_destroy_produces_destroy_line(self):
        result = add_activation(
            THREE_MESSAGE_PUML, "bob", M2_INDEX, M2_INDEX, "destroy"
        )
        assert "activate bob" in result
        assert "destroy bob" in result
        assert "deactivate bob" not in result

    def test_balanced_pair_is_added(self):
        result = add_activation(
            THREE_MESSAGE_PUML, "alice", M1_INDEX, M3_INDEX, "deactivate"
        )
        lines = result.splitlines()
        assert lines.count("activate alice") == 1
        assert lines.count("deactivate alice") == 1

    def test_activate_before_deactivate(self):
        result = add_activation(
            THREE_MESSAGE_PUML, "alice", M1_INDEX, M3_INDEX, "deactivate"
        )
        lines = result.splitlines()
        activate_at = lines.index("activate alice")
        deactivate_at = lines.index("deactivate alice")
        assert activate_at < deactivate_at

    def test_bar_covers_messages_after_start_through_end(self):
        # start=m1, end=m3: activate is below m1, close is below m3, so the bar
        # excludes the start message (m1) and includes m2 and m3.
        result = add_activation(
            THREE_MESSAGE_PUML, "alice", M1_INDEX, M3_INDEX, "deactivate"
        )
        lines = result.splitlines()
        activate_at = lines.index("activate alice")
        deactivate_at = lines.index("deactivate alice")
        # m1 is above the bar.
        assert lines.index("alice -> bob: m1") < activate_at
        # m2 and m3 are inside the bar.
        assert activate_at < lines.index("bob -> alice: m2") < deactivate_at
        assert activate_at < lines.index("alice -> bob: m3") < deactivate_at

    def test_nested_activation_stays_balanced_and_ordered(self):
        # Outer bar wraps all three messages.
        outer = add_activation(
            THREE_MESSAGE_PUML, "bob", M1_INDEX, M3_INDEX, "deactivate"
        )
        # Inner bar wraps only m2.  The outer insert shifted line numbers, so
        # find the current index of m2 in the modified puml.
        outer_lines = outer.splitlines()
        m2_idx = next(i for i, ln in enumerate(outer_lines) if ln == "bob -> alice: m2")
        nested = add_activation(outer, "bob", m2_idx, m2_idx, "deactivate")
        lines = nested.splitlines()
        activate_positions = [i for i, ln in enumerate(lines) if ln == "activate bob"]
        deactivate_positions = [
            i for i, ln in enumerate(lines) if ln == "deactivate bob"
        ]
        assert len(activate_positions) == 2
        assert len(deactivate_positions) == 2
        # Properly nested: both activates come before both deactivates.
        assert max(activate_positions) < min(deactivate_positions)

    def test_unknown_end_type_defaults_to_deactivate(self):
        result = add_activation(THREE_MESSAGE_PUML, "bob", M2_INDEX, M2_INDEX, "bogus")
        assert "activate bob" in result
        assert "deactivate bob" in result
        assert "destroy bob" not in result


class TestParsingWithExistingActivationBar:
    """Regression: a diagram that already contains an activation bar must still
    parse. The bar's narrow rect shares the lifeline's cx, so it must not be
    mistaken for a participant (which previously corrupted message parsing and
    returned HTTP 500 from getMessagePositions / addMessage / addActivation)."""

    PUML_WITH_BAR = """@startuml
participant alice
participant bob
alice -> bob: m1
activate bob
bob -> alice: m2
deactivate bob
alice -> bob: m3
@enduml"""

    def _svg(self):
        from plantuml_gui.shared.render import _create_svg_from_uml

        full = _create_svg_from_uml(self.PUML_WITH_BAR)
        return re.search(r"<g>(.*?)</g>", full, re.DOTALL).group(1)

    def test_get_message_positions_with_bar(self):
        from plantuml_gui.sequence.message import get_message_positions

        positions = get_message_positions(self.PUML_WITH_BAR, self._svg())
        # Three messages, indexes skip the activate/deactivate lines (4 and 6).
        assert [p["index"] for p in positions] == [3, 5, 7]
        assert [p["text"] for p in positions] == ["m1", "m2", "m3"]

    def test_get_message_positions_route_with_bar(self, client):
        response = client.post(
            "/getMessagePositions",
            data=json.dumps({"plantuml": self.PUML_WITH_BAR, "svg": self._svg()}),
            content_type="application/json",
        )
        assert response.status_code == 200
        assert len(response.get_json()["positions"]) == 3


class TestAddActivationRoute:
    def test_valid_request_returns_pair(self, client):
        payload = {
            "plantuml": THREE_MESSAGE_PUML,
            "participant": "bob",
            "startMessageIndex": M2_INDEX,
            "endMessageIndex": M2_INDEX,
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
        payload = {
            "plantuml": THREE_MESSAGE_PUML,
            "participant": "bob",
            "startMessageIndex": M2_INDEX,
            "endMessageIndex": M2_INDEX,
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
        payload = {
            "plantuml": THREE_MESSAGE_PUML,
            "participant": "bob",
            "startMessageIndex": M2_INDEX,
            "endMessageIndex": M2_INDEX,
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
