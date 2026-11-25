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

"""Else branches in sequence groups: slots, add_else, delete, /addSeqElse.

PlantUML renders an ``else`` as a dashed line across the group box, followed
by a bold ``[label]`` text if it has a label.
"""

import json
import re
from functools import lru_cache

import pytest
from plantuml_gui.sequence.errors import USER_MESSAGES, EditError
from plantuml_gui.sequence.group import (
    _compute_else_slots,
    _find_group_end_index,
    _find_group_line_index,
    _find_own_else_indexes,
    add_else,
    delete_group,
    get_group_positions,
)
from plantuml_gui.sequence.message import (
    get_message_positions,
    index_of_clicked_message,
)
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


@lru_cache(maxsize=None)
def _svg(puml, page=0):
    """Inner markup of the rendered <g>. Cached: each render runs the JAR."""
    match = re.search(r"<g>(.*)</g>", _create_svg_from_uml(puml, page), re.DOTALL)
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


class TestElseSvgMarkup:
    def test_separator_spans_the_box_with_the_message_stroke_width(self):
        # isElseSeparator's premise: styled like a message, told apart by width.
        svg = _svg(FLAT_ALT_ELSE)
        box = next(r for r in Pq(svg)("rect").items() if r.attr("fill") == "none")
        box_x = float(box.attr("x"))
        box_right = box_x + float(box.attr("width"))
        separators = _else_separators(svg)
        assert len(separators) == 2
        for line in separators:
            assert float(line.attr("x1")) == box_x
            assert float(line.attr("x2")) == box_right
            assert line.attr("y1") == line.attr("y2")
            assert "stroke-width:1.0" in line.attr("style")


class TestMessageDetectionWithElse:
    def test_message_positions_skip_else_lines(self):
        positions = get_message_positions(FLAT_ALT_ELSE, _svg(FLAT_ALT_ELSE))
        assert [(p["index"], p["text"]) for p in positions] == [
            (4, "m1"),
            (6, "m2"),
            (8, "m3"),
        ]

    def test_separator_and_label_are_not_clicked_messages(self):
        svg = _svg(FLAT_ALT_ELSE)
        separators = _else_separators(svg)
        label = separators[0].next()
        for el in [*separators, label]:
            assert index_of_clicked_message(svg, str(el)) == -1


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
    """Rendered message texts; empty on a syntax error."""
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
    def test_every_own_message_and_the_end(self):
        # lines 4-6 are m1..m3, line 7 the end
        assert _slots(THREE_MESSAGE_ALT, 3) == [4, 5, 6, 7]

    def test_single_message_group_has_slots(self):
        # The reported case.
        assert _slots(_block("alice -> bob: m1"), 3) == [4, 5]

    def test_empty_group_has_only_the_end_slot(self):
        assert _slots(_block(), 3) == [4]

    def test_existing_else_lines_are_not_slots(self):
        # 4 m1 | 5 else | 6 m2 | 7 else | 8 m3 | 9 end
        assert _slots(FLAT_ALT_ELSE, 3) == [4, 6, 8, 9]

    def test_nested_group_messages_are_not_slots(self):
        # 4 m1 | 5 loop | 6 m2 (in loop) | 7 end (loop's) | 8 m3 | 9 end
        puml = _block(
            "alice -> bob: m1", "loop l", "bob -> alice: m2", "end", "alice -> bob: m3"
        )
        assert _slots(puml, 3) == [4, 8, 9]

    def test_notes_and_comments_are_not_slots(self):
        # 4 note | 5 comment | 6 m1 | 7 end
        puml = _block("note over alice: n", "' a comment", "alice -> bob: m1")
        assert _slots(puml, 3) == [6, 7]

    def test_nested_group_has_its_own_slots(self):
        # 4 m1 | 5 alt inner | 6 m2 | 7 m3 | 8 end (inner) | 9 end (outer)
        puml = _block(
            "alice -> bob: m1",
            "alt inner",
            "bob -> alice: m2",
            "alice -> bob: m3",
            "end",
        )
        assert _slots(puml, 5) == [6, 7, 8]
        assert _slots(puml, 3) == [4, 9]

    def test_unclosed_block_has_no_end_slot(self):
        lines = ["alt a", "alice -> bob: m1", "bob -> alice: m2"]
        assert _compute_else_slots(lines, 0) == [1, 2]


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

    @pytest.mark.parametrize("label", ["", "   "])
    def test_empty_label_writes_bare_else(self, label):
        lines = _add_else(THREE_MESSAGE_ALT, 6, label).splitlines()
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
        # 4 m1 | 5 else | 6 m2 | 7 m3 | 8 end
        assert get_group_positions(result, svg) == [
            {"headerIndex": 3, "endIndex": 8, "elseSlots": [4, 6, 7, 8]}
        ]

    def test_else_before_end_of_single_message_group(self):
        # The reported case.
        puml = _block("alice -> bob: granted")
        lines = _add_else(puml, 5, "failure").splitlines()
        assert lines[3:7] == ["alt a", "alice -> bob: granted", "else failure", "end"]

    def test_else_in_empty_group(self):
        lines = _add_else(_block(), 4, "").splitlines()
        assert lines[3:6] == ["alt a", "else", "end"]

    def test_else_before_first_message(self):
        result = _add_else(THREE_MESSAGE_ALT, 4, "other")
        assert result.splitlines()[3:6] == [
            "alt success",
            "else other",
            "alice -> bob: m1",
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

    @pytest.mark.parametrize(
        "before",
        [
            3,  # the group header itself
            8,  # @enduml, after the group
            99,  # out of range
            -1,
        ],
    )
    def test_rejects_invalid_position(self, before):
        with pytest.raises(EditError) as error:
            _add_else(THREE_MESSAGE_ALT, before, "x")
        assert error.value.code == "invalid_else_position"

    def test_rejects_message_inside_nested_group(self):
        # 4 m1 | 5 loop | 6 m2 | 7 m3 | 8 end (loop) | 9 end
        puml = _block(
            "alice -> bob: m1", "loop l", "bob -> alice: m2", "alice -> bob: m3", "end"
        )
        with pytest.raises(EditError) as error:
            _add_else(puml, 7, "x")
        assert error.value.code == "invalid_else_position"

    def test_rejects_nested_groups_end(self):
        puml = _block("alice -> bob: m1", "loop l", "bob -> alice: m2", "end")
        with pytest.raises(EditError) as error:
            _add_else(puml, 7, "x")  # the loop's end, not the alt's
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


class TestAddElseRoute:
    def test_adds_else(self, client):
        svg = _svg(THREE_MESSAGE_ALT)
        response = _post(
            client,
            "/addSeqElse",
            plantuml=THREE_MESSAGE_ALT,
            svg=svg,
            svgelement=_group_box(svg, 0),
            beforeLineIndex=5,
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
            beforeLineIndex=5,
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
            beforeLineIndex=3,
            label="<script>",
        )
        assert response.status_code == 400
        assert response.get_json() == {"error": USER_MESSAGES["invalid_else_position"]}

    def test_adds_else_on_the_requested_page(self, client):
        page2 = _svg(TWO_PAGES, 1)
        response = _post(
            client,
            "/addSeqElse",
            plantuml=TWO_PAGES,
            svg=page2,
            svgelement=_group_box(page2, 0),
            beforeLineIndex=10,
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
    def test_else_slots_use_global_line_indexes_on_later_pages(self, client):
        groups = _post(
            client,
            "/getSequencePositions",
            plantuml=TWO_PAGES,
            svg=_svg(TWO_PAGES, 1),
            page=1,
        ).get_json()["groups"]
        assert groups == [{"headerIndex": 8, "endIndex": 11, "elseSlots": [9, 10, 11]}]


# Note bodies that look like statements must be ignored.

# Body 'end' and 'else'.
# Line indexes:
#   3 alt a | 4 m1 | 5 note over alice | 6 else maybe | 7 end | 8 end note
#   9 m2 | 10 end
NOTE_BODY_END = """@startuml
participant alice
participant bob
alt a
alice -> bob: m1
note over alice
else maybe
end
end note
bob -> alice: m2
end
@enduml"""

# Body line starting with a group keyword.
# Line indexes:
#   3 alt a | 4 m1 | 5 note over alice | 6 loop until done | 7 end note
#   8 m2 | 9 end
NOTE_BODY_HEADER = """@startuml
participant alice
participant bob
alt a
alice -> bob: m1
note over alice
loop until done
end note
bob -> alice: m2
end
@enduml"""


class TestNoteBodiesAreNotStatements:
    def test_body_end_does_not_close_the_group(self):
        assert _find_group_end_index(NOTE_BODY_END.splitlines(), 3) == 10

    def test_body_header_does_not_open_a_group(self):
        assert _find_group_end_index(NOTE_BODY_HEADER.splitlines(), 3) == 9

    def test_body_header_is_not_counted_as_a_group(self):
        assert _find_group_line_index(NOTE_BODY_HEADER, 1) == 3
        assert _find_group_line_index(NOTE_BODY_HEADER, 2) == -1

    def test_body_else_is_not_an_own_else(self):
        assert _find_own_else_indexes(NOTE_BODY_END.splitlines(), 3) == []

    def test_else_slots_skip_note_bodies(self):
        assert _slots(NOTE_BODY_END, 3) == [4, 9, 10]
        assert _slots(NOTE_BODY_HEADER, 3) == [4, 8, 9]

    def test_arrow_in_note_body_is_not_a_slot(self):
        lines = [
            "alt a",
            "alice -> bob: m1",
            "note over alice",
            "alice -> bob: in note",
            "end note",
            "bob -> alice: m2",
            "end",
        ]
        assert _compute_else_slots(lines, 0) == [1, 5, 6]

    @pytest.mark.parametrize(
        ("puml", "expected"),
        [
            (
                NOTE_BODY_END,
                {"headerIndex": 3, "endIndex": 10, "elseSlots": [4, 9, 10]},
            ),
            (
                NOTE_BODY_HEADER,
                {"headerIndex": 3, "endIndex": 9, "elseSlots": [4, 8, 9]},
            ),
        ],
    )
    def test_renders_and_positions_match(self, puml, expected):
        assert _renders_messages(puml) == ["m1", "m2"]
        assert get_group_positions(puml, _svg(puml)) == [expected]

    def test_delete_keeps_the_note_intact(self):
        lines = _delete(NOTE_BODY_END, 0).splitlines()
        original = NOTE_BODY_END.splitlines()
        assert lines == original[:3] + original[4:10] + original[11:]

    def test_add_else_after_the_note(self):
        lines = _add_else(NOTE_BODY_END, 9, "b").splitlines()
        assert lines[8:11] == ["end note", "else b", "bob -> alice: m2"]
