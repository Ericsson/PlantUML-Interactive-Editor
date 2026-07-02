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

import re

import pytest
from flask import json
from plantuml_gui.sequence.group import (
    VALID_GROUP_TYPES,
    add_group,
    delete_group,
    get_group_label,
    index_of_clicked_group,
    rename_group,
)
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq


def extract_g_inner(svg_string):
    """Extract the innerHTML of the <g> element from full SVG."""
    match = re.search(r"<g>(.*?)</g>", svg_string, re.DOTALL)
    if match:
        return match.group(1)
    return None


def extract_group_rect(svg_string, group_index=0):
    """Extract the outerHTML of the nth group box rect (fill:none) from SVG."""
    d = Pq(svg_string)
    count = 0
    for rect in d("rect").items():
        if rect.attr("fill") != "none":
            continue
        if count == group_index:
            return str(rect)
        count += 1
    return None


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


NESTED_GROUP_PUML = """@startuml
participant alice
participant bob
opt Opt Label
alice -> bob: m1
loop Loop Label
bob -> alice: m2
end
end
group
alice -> bob: m3
end
@enduml"""


class TestIndexOfClickedGroup:
    def test_click_first_group(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 0)
        assert svgelement is not None
        assert index_of_clicked_group(svg, svgelement) == 1

    def test_click_nested_group(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 1)
        assert svgelement is not None
        assert index_of_clicked_group(svg, svgelement) == 2

    def test_click_third_group(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 2)
        assert svgelement is not None
        assert index_of_clicked_group(svg, svgelement) == 3


class TestGetGroupLabel:
    def test_get_outer_label(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 0)
        assert get_group_label(NESTED_GROUP_PUML, svg, svgelement) == {
            "type": "opt",
            "label": "Opt Label",
        }

    def test_get_nested_label(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 1)
        assert get_group_label(NESTED_GROUP_PUML, svg, svgelement) == {
            "type": "loop",
            "label": "Loop Label",
        }

    def test_get_bare_group_label(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 2)
        assert get_group_label(NESTED_GROUP_PUML, svg, svgelement) == {
            "type": "group",
            "label": "",
        }


class TestRenameGroup:
    def test_rename_keeps_keyword(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 0)
        result = rename_group(NESTED_GROUP_PUML, svg, svgelement, "New Label")
        lines = result.splitlines()
        assert "opt New Label" in lines
        assert "loop Loop Label" in lines
        assert "group" in lines

    def test_rename_nested_group(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 1)
        result = rename_group(NESTED_GROUP_PUML, svg, svgelement, "New Loop")
        lines = result.splitlines()
        assert "loop New Loop" in lines
        assert "opt Opt Label" in lines

    def test_rename_bare_group_adds_label(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 2)
        result = rename_group(NESTED_GROUP_PUML, svg, svgelement, "Now Labeled")
        assert "group Now Labeled" in result.splitlines()

    def test_rename_to_empty_label(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 0)
        result = rename_group(NESTED_GROUP_PUML, svg, svgelement, "")
        assert "opt" in result.splitlines()


class TestDeleteGroup:
    def test_unwrap_outer_group_keeps_nested_contents(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 0)
        result = delete_group(NESTED_GROUP_PUML, svg, svgelement)
        lines = result.splitlines()
        assert "opt Opt Label" not in lines
        # Only the outer opt's own "end" is removed; the loop's "end" remains
        assert lines.count("end") == 2
        assert "loop Loop Label" in lines
        assert "alice -> bob: m1" in lines
        assert "bob -> alice: m2" in lines

    def test_unwrap_nested_group_keeps_outer_intact(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 1)
        result = delete_group(NESTED_GROUP_PUML, svg, svgelement)
        lines = result.splitlines()
        assert "loop Loop Label" not in lines
        assert "opt Opt Label" in lines
        assert lines.count("end") == 2
        assert "bob -> alice: m2" in lines

    def test_unwrap_bare_group(self):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 2)
        result = delete_group(NESTED_GROUP_PUML, svg, svgelement)
        lines = result.splitlines()
        assert "group" not in lines
        assert "alice -> bob: m3" in lines


class TestGroupRoutes:
    def test_get_group_label_route(self, client):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 0)
        test_data = {
            "plantuml": NESTED_GROUP_PUML,
            "svg": svg,
            "svgelement": svgelement,
        }
        response = client.post(
            "/getSeqGroupLabel",
            data=json.dumps(test_data),
            content_type="application/json",
        )
        assert response.get_json() == {"type": "opt", "label": "Opt Label"}

    def test_rename_group_route(self, client):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 0)
        test_data = {
            "plantuml": NESTED_GROUP_PUML,
            "svg": svg,
            "svgelement": svgelement,
            "label": "Renamed",
        }
        response = client.post(
            "/renameSeqGroup",
            data=json.dumps(test_data),
            content_type="application/json",
        )
        assert "opt Renamed" in response.get_json()["plantuml"].splitlines()

    def test_delete_group_route(self, client):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        svgelement = extract_group_rect(svg, 2)
        test_data = {
            "plantuml": NESTED_GROUP_PUML,
            "svg": svg,
            "svgelement": svgelement,
        }
        response = client.post(
            "/deleteSeqGroup",
            data=json.dumps(test_data),
            content_type="application/json",
        )
        lines = response.get_json()["plantuml"].splitlines()
        assert "group" not in lines
        assert "alice -> bob: m3" in lines


class TestGetGroupPositions:
    # NESTED_GROUP_PUML line indexes:
    #   3: opt Opt Label ... 8: end (closes opt)
    #   5: loop Loop Label ... 7: end (closes loop)
    #   9: group ... 11: end
    def test_nested_groups_get_correct_bounds(self):
        from plantuml_gui.sequence.group import get_group_positions

        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        positions = get_group_positions(NESTED_GROUP_PUML, svg)
        assert positions == [
            {"headerIndex": 3, "endIndex": 8},
            {"headerIndex": 5, "endIndex": 7},
            {"headerIndex": 9, "endIndex": 11},
        ]

    def test_no_groups_returns_empty(self):
        from plantuml_gui.sequence.group import get_group_positions

        svg = extract_g_inner(_create_svg_from_uml(THREE_MESSAGE_PUML))
        assert get_group_positions(THREE_MESSAGE_PUML, svg) == []

    def test_route_returns_positions(self, client):
        svg = extract_g_inner(_create_svg_from_uml(NESTED_GROUP_PUML))
        with client:
            response = client.post(
                "/getSeqGroupPositions",
                data=json.dumps({"plantuml": NESTED_GROUP_PUML, "svg": svg}),
                content_type="application/json",
            )
            assert response.status_code == 200
            positions = response.get_json()["positions"]
            assert len(positions) == 3
            assert positions[0] == {"headerIndex": 3, "endIndex": 8}
