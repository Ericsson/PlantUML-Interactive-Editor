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

"""Characterization tests: how ``else`` branches in an ``alt`` render, and that
existing element detection (messages, groups, notes) is unaffected by them.

PlantUML (1.2022.x) renders each ``else`` as a horizontal dashed separator
``<line style="stroke:#000000;stroke-width:1.0;stroke-dasharray:2.0,2.0;">``
spanning the group box's full width, followed - only when the ``else`` has a
label - by a bold font-size-11 ``<text>[label]</text>``. A bare ``else`` emits
only the line.
"""

import json
import re

import pytest
from plantuml_gui.sequence.errors import USER_MESSAGES, EditError
from plantuml_gui.sequence.group import (
    _compute_else_slots,
    add_else,
    delete_group,
    get_group_positions,
)
from plantuml_gui.sequence.message import (
    get_message_positions,
    index_of_clicked_message,
)
from plantuml_gui.sequence.note import get_note_positions
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq

# Line indexes:
#   3 alt success | 4 m1 | 5 else failure | 6 m2 | 7 else | 8 m3 | 9 end
FLAT_ALT_ELSE = """@startuml
participant alice
participant bob
alt success
alice -> bob: m1
else failure
bob --> alice: m2
else
alice -> bob: m3
end
@enduml"""

# Line indexes:
#   3 alt outer | 4 m1 | 5 loop retry | 6 m2 | 7 end | 8 else other | 9 m3 | 10 end
NESTED_ALT_ELSE = """@startuml
participant alice
participant bob
alt outer
alice -> bob: m1
loop retry
bob -> alice: m2
end
else other
alice -> bob: m3
end
@enduml"""

# Self messages and a note directly after else separators (labeled and bare).
# Line indexes:
#   3 alt a | 4 self1 | 5 else b | 6 note | 7 m | 8 else | 9 self2 | 10 end
SELF_AND_NOTE_ALT_ELSE = """@startuml
participant alice
participant bob
alt a
alice -> alice: self1
else b
note over alice: n
bob -> alice: m
else
alice -> alice: self2
end
@enduml"""


def _svg(puml):
    """Render puml and return the inner markup of its <g> (what the frontend sends)."""
    match = re.search(r"<g>(.*)</g>", _create_svg_from_uml(puml), re.DOTALL)
    assert match
    return match.group(1)


def _else_separators(svg):
    """Return the else separator lines: dashed lines drawn in the group stroke."""
    return [
        line
        for line in Pq(svg)("line").items()
        if "stroke:#000000" in (line.attr("style") or "")
        and "stroke-dasharray" in (line.attr("style") or "")
    ]


@pytest.fixture(scope="module")
def flat_svg():
    return _svg(FLAT_ALT_ELSE)


@pytest.fixture(scope="module")
def nested_svg():
    return _svg(NESTED_ALT_ELSE)


@pytest.fixture(scope="module")
def self_note_svg():
    return _svg(SELF_AND_NOTE_ALT_ELSE)


class TestElseSvgMarkup:
    def test_one_separator_per_else(self, flat_svg):
        assert len(_else_separators(flat_svg)) == 2

    def test_separator_spans_group_box_width(self, flat_svg):
        box = next(r for r in Pq(flat_svg)("rect").items() if r.attr("fill") == "none")
        box_x = float(box.attr("x"))
        box_right = box_x + float(box.attr("width"))
        for line in _else_separators(flat_svg):
            assert float(line.attr("x1")) == box_x
            assert float(line.attr("x2")) == box_right
            assert line.attr("y1") == line.attr("y2")

    def test_separator_uses_message_stroke_width(self, flat_svg):
        # Same stroke-width as message arrows - the reason a naive
        # "line with stroke-width:1.0" message check would match it.
        for line in _else_separators(flat_svg):
            assert "stroke-width:1.0" in line.attr("style")

    def test_labeled_else_emits_bold_small_label_after_separator(self, flat_svg):
        first = _else_separators(flat_svg)[0]
        label = first.next()
        assert label[0].tag == "text"
        assert label.text() == "[failure]"
        assert label.attr("font-weight") == "bold"
        assert label.attr("font-size") == "11"

    def test_bare_else_emits_no_label(self, flat_svg):
        second = _else_separators(flat_svg)[1]
        assert second.next()[0].tag != "text"


class TestMessageDetectionWithElse:
    def test_flat_message_positions(self, flat_svg):
        positions = get_message_positions(FLAT_ALT_ELSE, flat_svg)
        assert [(p["index"], p["text"]) for p in positions] == [
            (4, "m1"),
            (6, "m2"),
            (8, "m3"),
        ]

    def test_nested_message_positions(self, nested_svg):
        positions = get_message_positions(NESTED_ALT_ELSE, nested_svg)
        assert [(p["index"], p["text"]) for p in positions] == [
            (4, "m1"),
            (6, "m2"),
            (9, "m3"),
        ]

    def test_self_messages_after_else(self, self_note_svg):
        positions = get_message_positions(SELF_AND_NOTE_ALT_ELSE, self_note_svg)
        assert [(p["index"], p["text"]) for p in positions] == [
            (4, "self1"),
            (7, "m"),
            (9, "self2"),
        ]

    def test_message_cy_is_ordered_around_separators(self, flat_svg):
        positions = get_message_positions(FLAT_ALT_ELSE, flat_svg)
        separators = [float(s.attr("y1")) for s in _else_separators(flat_svg)]
        cys = [p["cy"] for p in positions]
        assert cys[0] < separators[0] < cys[1] < separators[1] < cys[2]

    def test_separator_is_not_a_clicked_message(self, flat_svg):
        for line in _else_separators(flat_svg):
            assert index_of_clicked_message(flat_svg, str(line)) == -1

    def test_else_label_is_not_a_clicked_message(self, flat_svg):
        label = _else_separators(flat_svg)[0].next()
        assert index_of_clicked_message(flat_svg, str(label)) == -1

    def test_message_after_else_resolves_to_its_ordinal(self, flat_svg):
        texts = [
            t for t in Pq(flat_svg)("text").items() if t.text() in ("m1", "m2", "m3")
        ]
        assert [index_of_clicked_message(flat_svg, str(t)) for t in texts] == [1, 2, 3]


class TestGroupDetectionWithElse:
    def test_flat_group_positions(self, flat_svg):
        assert get_group_positions(FLAT_ALT_ELSE, flat_svg) == [
            {"headerIndex": 3, "endIndex": 9, "elseSlots": []}
        ]

    def test_nested_group_positions(self, nested_svg):
        assert get_group_positions(NESTED_ALT_ELSE, nested_svg) == [
            {"headerIndex": 3, "endIndex": 10, "elseSlots": []},
            {"headerIndex": 5, "endIndex": 7, "elseSlots": []},
        ]


class TestNoteDetectionWithElse:
    def test_note_after_else_label(self, self_note_svg):
        notes = get_note_positions(SELF_AND_NOTE_ALT_ELSE, self_note_svg)
        assert [n["index"] for n in notes] == [6]


# An alt nested in an alt, each with its own else.
# Line indexes:
#   3 alt outer | 4 m1 | 5 alt inner | 6 m2 | 7 else inner-else | 8 m3 | 9 end
#   10 else outer-else | 11 m4 | 12 end
NESTED_ALTS_WITH_ELSE = """@startuml
participant alice
participant bob
alt outer
alice -> bob: m1
alt inner
bob -> alice: m2
else inner-else
alice -> bob: m3
end
else outer-else
bob -> alice: m4
end
@enduml"""

INDENTED_ALT_ELSE = """@startuml
participant alice
participant bob
alt success
    alice -> bob: m1
  else failure
    bob -> alice: m2
end
@enduml"""


def _group_box(svg, ordinal):
    """Return the outerHTML of the nth real group box (the rect after its tab)."""
    boxes = []
    pending_tab = False
    for el in Pq(svg).children().items():
        tag = el[0].tag
        if tag == "path" and el.attr("fill") == "#EEEEEE":
            pending_tab = True
            continue
        if tag == "rect" and el.attr("fill") == "none" and pending_tab:
            boxes.append(str(el))
        pending_tab = False
    return boxes[ordinal]


def _delete(puml, ordinal):
    svg = _svg(puml)
    return delete_group(puml, svg, _group_box(svg, ordinal))


def _renders_messages(puml):
    """Return the message texts PlantUML renders - empty if it hit a syntax error."""
    return [p["text"] for p in get_message_positions(puml, _svg(puml))]


class TestDeleteGroupWithElse:
    def test_removes_header_own_elses_and_end(self):
        result = _delete(FLAT_ALT_ELSE, 0)
        assert result.splitlines() == [
            "@startuml",
            "participant alice",
            "participant bob",
            "alice -> bob: m1",
            "bob --> alice: m2",
            "alice -> bob: m3",
            "@enduml",
        ]

    def test_result_still_renders(self):
        result = _delete(FLAT_ALT_ELSE, 0)
        assert _renders_messages(result) == ["m1", "m2", "m3"]

    def test_else_after_nested_non_alt_group_is_removed(self):
        lines = _delete(NESTED_ALT_ELSE, 0).splitlines()
        assert "alt outer" not in lines
        assert "else other" not in lines
        assert "loop retry" in lines
        assert lines.count("end") == 1  # the loop's

    def test_deleting_outer_alt_keeps_inner_else(self):
        lines = _delete(NESTED_ALTS_WITH_ELSE, 0).splitlines()
        assert "alt outer" not in lines
        assert "else outer-else" not in lines
        assert "alt inner" in lines
        assert "else inner-else" in lines
        assert lines.count("end") == 1

    def test_deleting_inner_alt_keeps_outer_else(self):
        lines = _delete(NESTED_ALTS_WITH_ELSE, 1).splitlines()
        assert "alt inner" not in lines
        assert "else inner-else" not in lines
        assert "alt outer" in lines
        assert "else outer-else" in lines
        assert lines.count("end") == 1

    def test_nested_results_still_render(self):
        for ordinal in (0, 1):
            result = _delete(NESTED_ALTS_WITH_ELSE, ordinal)
            assert _renders_messages(result) == ["m1", "m2", "m3", "m4"]

    def test_indented_else_is_removed(self):
        lines = _delete(INDENTED_ALT_ELSE, 0).splitlines()
        assert lines[3:5] == ["    alice -> bob: m1", "    bob -> alice: m2"]
        assert not any(line.strip().startswith("else") for line in lines)

    def test_message_text_starting_with_else_is_kept(self):
        puml = FLAT_ALT_ELSE.replace("bob --> alice: m2", "bob --> alice: else m2")
        lines = _delete(puml, 0).splitlines()
        assert "bob --> alice: else m2" in lines


# Line indexes: 3 alt | 4 m1 | 5 m2 | 6 m3 | 7 end
THREE_MESSAGE_ALT = """@startuml
participant alice
participant bob
alt success
alice -> bob: m1
bob -> alice: m2
alice -> bob: m3
end
@enduml"""


def _slots(puml, header_index):
    return _compute_else_slots(puml.splitlines(), header_index)


def _block(*body):
    """Wrap body lines in a two-participant alt; the alt header is line 3."""
    return "\n".join(
        ["@startuml", "participant alice", "participant bob", "alt a", *body]
        + ["end", "@enduml"]
    )


class TestElseSlots:
    def test_every_message_after_the_first(self):
        assert _slots(THREE_MESSAGE_ALT, 3) == [5, 6]

    def test_no_slot_directly_after_an_else(self):
        # m2 and m3 each open their branch; splitting would leave it empty.
        assert _slots(FLAT_ALT_ELSE, 3) == []

    def test_slot_after_an_else_branch_has_content(self):
        puml = _block(
            "alice -> bob: m1", "else b", "bob -> alice: m2", "alice -> bob: m3"
        )
        assert _slots(puml, 3) == [7]

    def test_nested_group_messages_are_not_slots(self):
        puml = _block("alice -> bob: m1", "loop l", "bob -> alice: m2", "end")
        assert _slots(puml, 3) == []

    def test_message_after_a_nested_group_is_a_slot(self):
        puml = _block(
            "alice -> bob: m1", "loop l", "bob -> alice: m2", "end", "alice -> bob: m3"
        )
        assert _slots(puml, 3) == [8]

    def test_nested_group_counts_as_branch_content(self):
        puml = _block("loop l", "bob -> alice: m2", "end", "alice -> bob: m3")
        assert _slots(puml, 3) == [7]

    def test_note_counts_as_branch_content(self):
        puml = _block("note over alice: n", "alice -> bob: m1")
        assert _slots(puml, 3) == [5]

    def test_blank_lines_and_comments_are_not_content(self):
        puml = _block("' a comment", "", "alice -> bob: m1", "bob -> alice: m2")
        assert _slots(puml, 3) == [7]

    def test_inner_alt_slots_ignore_the_outer_alt(self):
        assert _slots(NESTED_ALTS_WITH_ELSE, 5) == []
        puml = _block(
            "alice -> bob: m1",
            "alt inner",
            "bob -> alice: m2",
            "alice -> bob: m3",
            "end",
        )
        assert _slots(puml, 5) == [7]  # inner alt: m3 only
        assert _slots(puml, 3) == []  # outer alt: no own-level message after m1

    def test_unclosed_block_does_not_crash(self):
        lines = ["alt a", "alice -> bob: m1", "bob -> alice: m2"]
        assert _compute_else_slots(lines, 0) == [2]


def _add_else(puml, before, label, ordinal=0):
    svg = _svg(puml)
    return add_else(puml, svg, _group_box(svg, ordinal), before, label)


class TestAddElse:
    def test_inserts_labeled_else_before_message(self):
        lines = _add_else(THREE_MESSAGE_ALT, 5, "failure").splitlines()
        assert lines[3:8] == [
            "alt success",
            "alice -> bob: m1",
            "else failure",
            "bob -> alice: m2",
            "alice -> bob: m3",
        ]

    def test_empty_label_writes_bare_else(self):
        lines = _add_else(THREE_MESSAGE_ALT, 6, "").splitlines()
        assert lines[6] == "else"

    def test_whitespace_only_label_writes_bare_else(self):
        lines = _add_else(THREE_MESSAGE_ALT, 6, "   ").splitlines()
        assert lines[6] == "else"

    def test_multiline_label_stays_on_one_line(self):
        lines = _add_else(THREE_MESSAGE_ALT, 5, "a\nb").splitlines()
        assert lines[5] == "else a\\nb"

    def test_else_is_indented_like_the_alt_header(self):
        puml = "\n".join(
            [
                "@startuml",
                "participant alice",
                "participant bob",
                "  alt a",
                "      alice -> bob: m1",
                "      bob -> alice: m2",
                "  end",
                "@enduml",
            ]
        )
        assert _add_else(puml, 5, "b").splitlines()[5] == "  else b"

    def test_result_renders_two_branches(self):
        result = _add_else(THREE_MESSAGE_ALT, 5, "failure")
        svg = _svg(result)
        assert len(_else_separators(svg)) == 1
        assert _renders_messages(result) == ["m1", "m2", "m3"]
        # m3 (line 7) is now the only slot: m2 opens the new branch.
        assert get_group_positions(result, svg) == [
            {"headerIndex": 3, "endIndex": 8, "elseSlots": [7]}
        ]

    def test_targets_the_clicked_alt(self):
        puml = _block(
            "alice -> bob: m1",
            "alt inner",
            "bob -> alice: m2",
            "alice -> bob: m3",
            "end",
        )
        lines = _add_else(puml, 7, "x", ordinal=1).splitlines()
        assert lines[7] == "else x"
        assert lines[5:9] == [
            "alt inner",
            "bob -> alice: m2",
            "else x",
            "alice -> bob: m3",
        ]

    @pytest.mark.parametrize("group_type", ["group", "alt", "opt", "loop"])
    def test_every_group_type_accepts_else(self, group_type):
        puml = THREE_MESSAGE_ALT.replace("alt success", f"{group_type} success")
        result = _add_else(puml, 5, "x")
        assert result.splitlines()[5] == "else x"
        assert len(_else_separators(_svg(result))) == 1
        assert _renders_messages(result) == ["m1", "m2", "m3"]

    @pytest.mark.parametrize(
        "before",
        [
            4,  # first message: would leave the first branch empty
            3,  # the alt header itself
            7,  # the alt's end
            99,  # out of range
            -1,
        ],
    )
    def test_rejects_invalid_position(self, before):
        with pytest.raises(EditError) as error:
            _add_else(THREE_MESSAGE_ALT, before, "x")
        assert error.value.code == "invalid_else_position"

    def test_rejects_message_inside_nested_group(self):
        puml = _block(
            "alice -> bob: m1", "loop l", "bob -> alice: m2", "alice -> bob: m3", "end"
        )
        with pytest.raises(EditError) as error:
            _add_else(puml, 8, "x")
        assert error.value.code == "invalid_else_position"

    def test_rejects_position_directly_after_existing_else(self):
        with pytest.raises(EditError) as error:
            _add_else(FLAT_ALT_ELSE, 6, "x")
        assert error.value.code == "invalid_else_position"


def _post(client, route, **data):
    return client.post(route, data=json.dumps(data), content_type="application/json")


# Line indexes:
#   3 alt first | 4 p1m1 | 5 p1m2 | 6 end | 7 newpage
#   8 alt second | 9 p2m1 | 10 p2m2 | 11 end
TWO_PAGES = """@startuml
participant Alice
participant Bob
alt first
Alice -> Bob: p1m1
Bob -> Alice: p1m2
end
newpage Second
alt second
Alice -> Bob: p2m1
Bob -> Alice: p2m2
end
@enduml"""


def _page_svg(puml, page):
    match = re.search(r"<g>(.*)</g>", _create_svg_from_uml(puml, page), re.DOTALL)
    assert match
    return match.group(1)


class TestAddElseRoute:
    def test_adds_else(self, client):
        svg = _svg(THREE_MESSAGE_ALT)
        response = _post(
            client,
            "/addSeqElse",
            plantuml=THREE_MESSAGE_ALT,
            svg=svg,
            svgelement=_group_box(svg, 0),
            beforeMessageIndex=5,
            label="failure",
        )
        assert response.status_code == 200
        assert response.get_json()["plantuml"].splitlines()[5] == "else failure"

    def test_missing_label_writes_bare_else(self, client):
        svg = _svg(THREE_MESSAGE_ALT)
        response = _post(
            client,
            "/addSeqElse",
            plantuml=THREE_MESSAGE_ALT,
            svg=svg,
            svgelement=_group_box(svg, 0),
            beforeMessageIndex=5,
        )
        assert response.get_json()["plantuml"].splitlines()[5] == "else"

    def test_invalid_position_is_a_400_with_the_fixed_message(self, client):
        svg = _svg(THREE_MESSAGE_ALT)
        response = _post(
            client,
            "/addSeqElse",
            plantuml=THREE_MESSAGE_ALT,
            svg=svg,
            svgelement=_group_box(svg, 0),
            beforeMessageIndex=4,
            label="<script>",
        )
        assert response.status_code == 400
        assert response.get_json() == {"error": USER_MESSAGES["invalid_else_position"]}

    def test_adds_else_on_the_requested_page(self, client):
        page2 = _page_svg(TWO_PAGES, 1)
        response = _post(
            client,
            "/addSeqElse",
            plantuml=TWO_PAGES,
            svg=page2,
            svgelement=_group_box(page2, 0),
            beforeMessageIndex=10,
            label="x",
            page=1,
        )
        assert response.status_code == 200
        lines = response.get_json()["plantuml"].splitlines()
        original = TWO_PAGES.splitlines()
        assert lines[:10] == original[:10]  # page 1 untouched
        assert lines[10] == "else x"
        assert lines[11:] == original[10:]


class TestElseSlotsInSequencePositions:
    def test_positions_route_returns_else_slots(self, client):
        svg = _svg(THREE_MESSAGE_ALT)
        groups = _post(
            client, "/getSequencePositions", plantuml=THREE_MESSAGE_ALT, svg=svg
        ).get_json()["groups"]
        assert groups == [{"headerIndex": 3, "endIndex": 7, "elseSlots": [5, 6]}]

    def test_else_slots_use_global_line_indexes_on_later_pages(self, client):
        groups = _post(
            client,
            "/getSequencePositions",
            plantuml=TWO_PAGES,
            svg=_page_svg(TWO_PAGES, 1),
            page=1,
        ).get_json()["groups"]
        assert groups == [{"headerIndex": 8, "endIndex": 11, "elseSlots": [10]}]
