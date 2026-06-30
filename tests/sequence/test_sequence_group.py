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

"""Tests for sequence diagram group blocks (group, alt, opt, loop)."""

import pytest
from flask import json
from plantuml_gui.sequence.group import VALID_GROUP_TYPES, add_group

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


class TestAddGroupBasic:
    def test_wraps_single_message(self):
        result = add_group(THREE_MESSAGE_PUML, "group", "My Group", M2_INDEX, M2_INDEX)
        lines = result.splitlines()
        group_start = lines.index("group My Group")
        end_at = lines.index("end")
        # The group keyword is inserted before the message
        assert lines[group_start + 1] == "bob -> alice: m2"
        # The end is inserted after the message
        assert lines[end_at - 1] == "bob -> alice: m2"

    def test_wraps_multiple_messages(self):
        result = add_group(THREE_MESSAGE_PUML, "group", "All", M1_INDEX, M3_INDEX)
        lines = result.splitlines()
        group_start = lines.index("group All")
        end_at = lines.index("end")
        # All three messages are inside the group
        assert group_start < lines.index("alice -> bob: m1")
        assert lines.index("alice -> bob: m3") < end_at

    def test_wraps_two_consecutive_messages(self):
        result = add_group(THREE_MESSAGE_PUML, "alt", "Case A", M1_INDEX, M2_INDEX)
        lines = result.splitlines()
        alt_start = lines.index("alt Case A")
        end_at = lines.index("end")
        assert lines[alt_start + 1] == "alice -> bob: m1"
        assert lines[end_at - 1] == "bob -> alice: m2"


class TestAddGroupTypes:
    @pytest.mark.parametrize("group_type", VALID_GROUP_TYPES)
    def test_each_type_produces_correct_keyword(self, group_type):
        result = add_group(THREE_MESSAGE_PUML, group_type, "Label", M2_INDEX, M2_INDEX)
        lines = result.splitlines()
        assert f"{group_type} Label" in lines

    def test_invalid_type_raises_value_error(self):
        with pytest.raises(ValueError, match="Invalid group type"):
            add_group(THREE_MESSAGE_PUML, "invalid", "Label", M2_INDEX, M2_INDEX)


class TestAddGroupReversedRange:
    def test_reversed_range_normalizes_to_same_result(self):
        forward = add_group(THREE_MESSAGE_PUML, "loop", "Retry", M1_INDEX, M3_INDEX)
        backward = add_group(THREE_MESSAGE_PUML, "loop", "Retry", M3_INDEX, M1_INDEX)
        assert forward == backward

    def test_reversed_range_wraps_correctly(self):
        result = add_group(THREE_MESSAGE_PUML, "opt", "Maybe", M3_INDEX, M1_INDEX)
        lines = result.splitlines()
        opt_start = lines.index("opt Maybe")
        end_at = lines.index("end")
        # All messages should be inside
        assert opt_start < lines.index("alice -> bob: m1")
        assert lines.index("alice -> bob: m3") < end_at


class TestAddGroupWithActivation:
    """Groups should work correctly when activation lines exist between messages."""

    PUML_WITH_ACTIVATION = """@startuml
participant alice
participant bob
alice -> bob: m1
activate bob
bob -> alice: m2
deactivate bob
alice -> bob: m3
@enduml"""

    # Line indexes:
    #   0: @startuml
    #   1: participant alice
    #   2: participant bob
    #   3: alice -> bob: m1
    #   4: activate bob
    #   5: bob -> alice: m2
    #   6: deactivate bob
    #   7: alice -> bob: m3
    #   8: @enduml

    def test_group_around_activated_messages(self):
        result = add_group(self.PUML_WITH_ACTIVATION, "group", "Active", 3, 5)
        lines = result.splitlines()
        group_start = lines.index("group Active")
        end_at = lines.index("end")
        # Group starts before m1 and ends after m2
        assert lines[group_start + 1] == "alice -> bob: m1"
        assert lines[end_at - 1] == "bob -> alice: m2"
        # Activation lines are inside the group
        assert group_start < lines.index("activate bob") < end_at

    def test_group_wrapping_all_including_deactivate(self):
        result = add_group(self.PUML_WITH_ACTIVATION, "alt", "Full", 3, 7)
        lines = result.splitlines()
        alt_start = lines.index("alt Full")
        end_at = lines.index("end")
        assert alt_start < lines.index("alice -> bob: m1")
        assert lines.index("alice -> bob: m3") < end_at
        assert alt_start < lines.index("activate bob") < end_at
        assert alt_start < lines.index("deactivate bob") < end_at


class TestAddGroupPreservesStructure:
    def test_startuml_and_enduml_preserved(self):
        result = add_group(THREE_MESSAGE_PUML, "group", "Test", M1_INDEX, M3_INDEX)
        lines = result.splitlines()
        assert lines[0] == "@startuml"
        assert lines[-1] == "@enduml"

    def test_participants_not_inside_group(self):
        result = add_group(THREE_MESSAGE_PUML, "group", "Test", M1_INDEX, M3_INDEX)
        lines = result.splitlines()
        group_start = lines.index("group Test")
        assert lines.index("participant alice") < group_start
        assert lines.index("participant bob") < group_start

    def test_empty_label_allowed(self):
        result = add_group(THREE_MESSAGE_PUML, "loop", "", M2_INDEX, M2_INDEX)
        lines = result.splitlines()
        assert "loop " in lines


class TestAddGroupRoute:
    def test_add_group_route_returns_modified_puml(self, client):
        response = client.post(
            "/addGroup",
            data=json.dumps(
                {
                    "plantuml": THREE_MESSAGE_PUML,
                    "groupType": "group",
                    "label": "My Group",
                    "startMessageIndex": M2_INDEX,
                    "endMessageIndex": M2_INDEX,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "plantuml" in data
        assert "group My Group" in data["plantuml"]
        assert "end" in data["plantuml"]

    def test_add_group_route_alt_type(self, client):
        response = client.post(
            "/addGroup",
            data=json.dumps(
                {
                    "plantuml": THREE_MESSAGE_PUML,
                    "groupType": "alt",
                    "label": "Success",
                    "startMessageIndex": M1_INDEX,
                    "endMessageIndex": M3_INDEX,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 200
        data = json.loads(response.data)
        assert "alt Success" in data["plantuml"]

    def test_add_group_route_invalid_type_returns_error(self, client):
        response = client.post(
            "/addGroup",
            data=json.dumps(
                {
                    "plantuml": THREE_MESSAGE_PUML,
                    "groupType": "invalid",
                    "label": "Bad",
                    "startMessageIndex": M1_INDEX,
                    "endMessageIndex": M3_INDEX,
                }
            ),
            content_type="application/json",
        )
        assert response.status_code == 400
        data = json.loads(response.data)
        assert "error" in data
