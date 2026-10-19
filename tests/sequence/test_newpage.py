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

"""Multi-page (``newpage``) sequence diagrams: page model, masking, routes."""

import re

import pytest
from flask import json
from plantuml_gui.sequence.classes import is_message_line
from plantuml_gui.sequence.pages import (
    clamp_page,
    mask_other_pages,
    page_boundaries,
    page_count,
    unmask,
)
from plantuml_gui.sequence.util import iter_note_shapes, note_regions
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq

# Line indexes are referenced by the tests below; keep them in sync.
THREE_PAGES = """@startuml
participant Alice
participant Bob
Alice -> Bob: p1m1
note right of Bob: p1n
group g1
Bob -> Alice: p1m2
end
newpage Second
Alice -> Bob: p2m1
note left of Alice: p2n
group g2
Bob -> Alice: p2m2
end
newpage
Alice -> Bob: p3m1
@enduml"""
LINES = THREE_PAGES.splitlines()


def _g_inner(svg: str) -> str:
    match = re.search(r"<g>(.*)</g>", svg, re.DOTALL)
    assert match, svg
    return match.group(1)


def _page_svg(puml: str, page: int) -> str:
    return _g_inner(_create_svg_from_uml(puml, page))


def _text_element(svg: str, text: str) -> str:
    for el in Pq(svg)("text").items():
        if el.text() == text:
            return str(el)
    raise AssertionError(f"no <text>{text}</text> in svg")


def _group_box(svg: str) -> str:
    """The first group box (rect fill=none directly after its tab path)."""
    previous = None
    for el in Pq(svg).children().items():
        if (
            el[0].tag == "rect"
            and el.attr("fill") == "none"
            and previous is not None
            and previous[0].tag == "path"
            and previous.attr("fill") == "#EEEEEE"
        ):
            return str(el)
        previous = el
    raise AssertionError("no group box in svg")


def _post(client, route: str, **data):
    response = client.post(
        route, data=json.dumps(data), content_type="application/json"
    )
    assert response.status_code == 200, response.data
    return response


class TestPageModel:
    def test_single_page(self):
        puml = "@startuml\nA -> B: hi\n@enduml"
        assert page_boundaries(puml) == []
        assert page_count(puml) == 1

    def test_boundaries_and_count(self):
        assert page_boundaries(THREE_PAGES) == [8, 14]
        assert page_count(THREE_PAGES) == 3

    @pytest.mark.parametrize("line", ["NEWPAGE", "  newpage  ", "newpage Title X"])
    def test_spellings_plantuml_accepts(self, line):
        assert page_count(f"@startuml\nA -> B: a\n{line}\nA -> B: b\n@enduml") == 2

    @pytest.mark.parametrize("line", ["' newpage", "newpages", "A -> B: newpage"])
    def test_lookalikes_are_not_breaks(self, line):
        assert page_count(f"@startuml\nA -> B: a\n{line}\n@enduml") == 1

    def test_newpage_inside_note_body_is_text(self):
        puml = "@startuml\nA -> B: a\nnote right of A\nnewpage\nend note\n@enduml"
        assert page_count(puml) == 1

    @pytest.mark.parametrize("requested, expected", [(0, 0), (1, 1), (2, 2), (9, 2)])
    def test_clamp_page(self, requested, expected):
        assert clamp_page(THREE_PAGES, requested) == expected


class TestMasking:
    def test_single_page_is_untouched(self):
        puml = "@startuml\nA -> B: hi\n@enduml"
        assert mask_other_pages(puml, 0) == (puml, {})

    def test_only_current_page_messages_and_notes_remain(self):
        masked, _ = mask_other_pages(THREE_PAGES, 1)
        lines = masked.splitlines()
        assert [i for i, line in enumerate(lines) if is_message_line(line)] == [9, 12]
        assert note_regions(masked) == [(10, 10)]

    def test_line_count_and_global_lines_are_kept(self):
        masked, _ = mask_other_pages(THREE_PAGES, 2)
        lines = masked.splitlines()
        assert len(lines) == len(LINES)
        for i in (0, 1, 2, 15, 16):
            assert lines[i] == LINES[i]

    def test_terminating_newpage_is_kept(self):
        masked, _ = mask_other_pages(THREE_PAGES, 1)
        lines = masked.splitlines()
        assert lines[14] == "newpage"
        assert lines[8] != LINES[8]  # the newpage that starts page 2 is hidden

    def test_group_spanning_pages_stays_visible(self):
        puml = (
            "@startuml\nA -> B: a\ngroup g\nA -> B: b\nnewpage\nA -> B: c\nend\n@enduml"
        )
        masked, _ = mask_other_pages(puml, 1)
        lines = masked.splitlines()
        assert lines[2] == "group g"
        assert lines[3] != "A -> B: b"

    def test_boxes_stay_visible(self):
        puml = (
            '@startuml\nbox "B"\nparticipant A\nend box\nA -> A: a\n'
            "newpage\nA -> A: b\n@enduml"
        )
        masked, _ = mask_other_pages(puml, 1)
        assert masked.splitlines()[1:4] == ['box "B"', "participant A", "end box"]

    def test_round_trip(self):
        for page in range(3):
            masked, originals = mask_other_pages(THREE_PAGES, page)
            assert unmask(masked, originals) == THREE_PAGES

    def test_unmask_survives_edits_on_the_current_page(self):
        masked, originals = mask_other_pages(THREE_PAGES, 1)
        lines = masked.splitlines()
        lines.insert(10, "Bob -> Alice: new")
        del lines[9]
        restored = unmask("\n".join(lines), originals).splitlines()
        assert restored[:9] == LINES[:9]
        assert restored[9] == "Bob -> Alice: new"
        assert restored[10:] == LINES[10:]


class TestRenderRoutes:
    def test_render_reports_page_count(self, client):
        response = _post(client, "/render", plantuml=THREE_PAGES)
        assert response.headers["X-PlantUML-Page-Count"] == "3"
        body = response.data.decode()
        assert ">p1m1<" in body and ">p2m1<" not in body

    def test_render_selected_page(self, client):
        body = _post(client, "/render", plantuml=THREE_PAGES, page=1).data.decode()
        assert ">p2m1<" in body and ">p1m1<" not in body
        assert ">Second<" in body

    def test_render_clamps_out_of_range_page(self, client):
        body = _post(client, "/render", plantuml=THREE_PAGES, page=7).data.decode()
        assert ">p3m1<" in body

    def test_single_page_count(self, client):
        response = _post(client, "/render", plantuml="@startuml\nA -> B: x\n@enduml")
        assert response.headers["X-PlantUML-Page-Count"] == "1"

    def test_png_pages_differ(self, client):
        first = _post(client, "/renderPNG", plantuml=THREE_PAGES).data
        third = _post(client, "/renderPNG", plantuml=THREE_PAGES, page=2).data
        assert first[:4] == third[:4] == b"\x89PNG"
        assert first != third


@pytest.fixture(scope="module")
def page2_svg():
    return _page_svg(THREE_PAGES, 1)


class TestSequenceRoutesOnLaterPages:
    def _edit(self, client, route, page2_svg, **extra):
        data = _post(
            client, route, plantuml=THREE_PAGES, svg=page2_svg, page=1, **extra
        ).get_json()
        return data["plantuml"].splitlines()

    def test_get_message_text(self, client, page2_svg):
        data = _post(
            client,
            "/getMessageText",
            plantuml=THREE_PAGES,
            svg=page2_svg,
            svgelement=_text_element(page2_svg, "p2m2"),
            page=1,
        ).get_json()
        assert data["text"] == "p2m2"

    def test_edit_message(self, client, page2_svg):
        lines = self._edit(
            client,
            "/editMessageText",
            page2_svg,
            svgelement=_text_element(page2_svg, "p2m1"),
            text="edited",
        )
        assert lines[9] == "Alice -> Bob: edited"
        assert lines[:9] == LINES[:9] and lines[10:] == LINES[10:]

    def test_delete_message(self, client, page2_svg):
        lines = self._edit(
            client,
            "/deleteMessage",
            page2_svg,
            svgelement=_text_element(page2_svg, "p2m1"),
        )
        assert lines == LINES[:9] + LINES[10:]

    def test_edit_note(self, client, page2_svg):
        shape = str(iter_note_shapes(page2_svg)[0][0])
        lines = self._edit(
            client, "/editSeqNote", page2_svg, svgelement=shape, text="changed"
        )
        assert lines[10] == "note left of Alice : changed"
        assert lines[4] == LINES[4]

    def test_rename_group(self, client, page2_svg):
        lines = self._edit(
            client,
            "/renameSeqGroup",
            page2_svg,
            svgelement=_group_box(page2_svg),
            label="renamed",
        )
        assert lines[11] == "group renamed"
        assert lines[5] == "group g1"

    def test_positions_use_global_line_indexes(self, client, page2_svg):
        data = _post(
            client,
            "/getSequencePositions",
            plantuml=THREE_PAGES,
            svg=page2_svg,
            page=1,
        ).get_json()
        assert [m["index"] for m in data["messages"]] == [9, 12]
        assert [g["headerIndex"] for g in data["groups"]] == [11]
        assert data["pageBoundaries"] == [8, 14]

    def test_add_message_below_last_element_stays_on_page(self, client):
        page1 = _page_svg(THREE_PAGES, 0)
        lines = (
            _post(
                client,
                "/addMessage",
                plantuml=THREE_PAGES,
                svg=page1,
                message="added",
                firstcoordinates=[0, 100000],
                secondcoordinates=[1000, 100000],
                page=0,
            )
            .get_json()["plantuml"]
            .splitlines()
        )
        assert lines.index("newpage Second") == 9
        assert lines[8].endswith(": added")

    def test_delete_participant_cascades_across_pages(self, client, page2_svg):
        bob = next(
            str(rect)
            for rect in Pq(page2_svg)("rect").items()
            if "Bob" in (rect.next().text() or "")
        )
        lines = self._edit(client, "/deleteParticipant", page2_svg, svgelement=bob)
        assert not any("Bob" in line for line in lines if is_message_line(line))
        assert "participant Bob" not in lines
        assert "newpage Second" in lines

    def test_without_page_field_behaves_as_before(self, client):
        page1 = _page_svg(THREE_PAGES, 0)
        lines = (
            _post(
                client,
                "/deleteMessage",
                plantuml=THREE_PAGES,
                svg=page1,
                svgelement=_text_element(page1, "p1m1"),
            )
            .get_json()["plantuml"]
            .splitlines()
        )
        assert lines == LINES[:3] + LINES[4:]
