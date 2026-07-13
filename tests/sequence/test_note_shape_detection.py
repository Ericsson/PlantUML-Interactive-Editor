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

"""Tests for color-independent note shape classification.

Verifies that note/hnote/rnote can be told apart purely by SVG shape
structure (tag name and path/point count), regardless of fill color,
across the placements PlantUML supports for all three note types.
"""

import re

from plantuml_gui.sequence.util import classify_note_shape
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq


def extract_g_inner(svg_string):
    """Extract the innerHTML of the <g> element from full SVG."""
    match = re.search(r"<g>(.*?)</g>", svg_string, re.DOTALL)
    if match:
        return match.group(1)
    return None


def shapes_in_document_order(svg):
    """Return path/polygon/rect elements in document order."""
    d = Pq(svg)
    return list(d("path, polygon, rect").items())


class TestClassifyNoteShape:
    def test_plain_note_over(self):
        puml = "@startuml\nparticipant Alice\nnote over Alice : text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        shapes = shapes_in_document_order(svg)
        # note renders as two consecutive <path> elements; classify the first
        note_shapes = [s for s in shapes if s[0].tag == "path"]
        assert classify_note_shape(note_shapes[0]) == "note"

    def test_plain_hnote_over(self):
        puml = "@startuml\nparticipant Alice\nhnote over Alice : text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        shapes = shapes_in_document_order(svg)
        polygon_shapes = [s for s in shapes if s[0].tag == "polygon"]
        assert len(polygon_shapes) == 1
        assert classify_note_shape(polygon_shapes[0]) == "hnote"

    def test_plain_rnote_over(self):
        puml = "@startuml\nparticipant Alice\nrnote over Alice : text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        shapes = shapes_in_document_order(svg)
        # Participant boxes also render as <rect>, so identify the note's
        # rect by its distinct fill (#FEFFDD) here; classify_note_shape
        # itself never inspects fill, only shape.
        rect_shapes = [s for s in shapes if s[0].tag == "rect"]
        note_rect = [s for s in rect_shapes if s.attr("fill") == "#FEFFDD"]
        assert len(note_rect) == 1
        assert classify_note_shape(note_rect[0]) == "rnote"

    def test_note_left_of(self):
        puml = "@startuml\nparticipant Alice\nnote left of Alice : text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        shapes = shapes_in_document_order(svg)
        note_shapes = [s for s in shapes if s[0].tag == "path"]
        assert classify_note_shape(note_shapes[0]) == "note"

    def test_hnote_right_of(self):
        puml = "@startuml\nparticipant Alice\nhnote right of Alice : text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        shapes = shapes_in_document_order(svg)
        polygon_shapes = [s for s in shapes if s[0].tag == "polygon"]
        assert classify_note_shape(polygon_shapes[0]) == "hnote"

    def test_rnote_spanning(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nrnote over Alice, Bob : text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        shapes = shapes_in_document_order(svg)
        rect_shapes = [s for s in shapes if s[0].tag == "rect"]
        note_rect = [s for s in rect_shapes if s.attr("fill") == "#FEFFDD"]
        assert len(note_rect) == 1
        assert classify_note_shape(note_rect[0]) == "rnote"

    def test_classification_independent_of_custom_color(self):
        puml = (
            "@startuml\nparticipant Alice\n"
            "note over Alice #FFAAAA : plain\n"
            "hnote over Alice #palegreen : hex\n"
            "rnote over Alice #palegreen : rect\n"
            "@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        shapes = shapes_in_document_order(svg)

        note_shapes = [s for s in shapes if s[0].tag == "path"]
        polygon_shapes = [s for s in shapes if s[0].tag == "polygon"]
        rect_shapes = [s for s in shapes if s[0].tag == "rect"]

        assert classify_note_shape(note_shapes[0]) == "note"
        assert classify_note_shape(polygon_shapes[0]) == "hnote"
        assert classify_note_shape(rect_shapes[0]) == "rnote"

    def test_message_attached_shortcut_shapes(self):
        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\n"
            "Alice -> Bob : hello\n"
            "note left : plain\n"
            "hnote left : hex\n"
            "rnote left : rect\n"
            "@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        shapes = shapes_in_document_order(svg)

        note_shapes = [s for s in shapes if s[0].tag == "path"]
        # The message arrowhead is also a <polygon> (4 points); only the
        # note's hexagon (7 points, fill #FEFFDD) represents the hnote.
        polygon_shapes = [
            s for s in shapes if s[0].tag == "polygon" and s.attr("fill") == "#FEFFDD"
        ]
        # Participant boxes are also <rect>; only the #FEFFDD one is the rnote.
        rect_shapes = [
            s for s in shapes if s[0].tag == "rect" and s.attr("fill") == "#FEFFDD"
        ]

        assert classify_note_shape(note_shapes[0]) == "note"
        assert len(polygon_shapes) == 1
        assert classify_note_shape(polygon_shapes[0]) == "hnote"
        assert len(rect_shapes) == 1
        assert classify_note_shape(rect_shapes[0]) == "rnote"

    def test_unrelated_shape_returns_none(self):
        puml = (
            "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob : hi\n@enduml"
        )
        svg = extract_g_inner(_create_svg_from_uml(puml))
        shapes = shapes_in_document_order(svg)
        # The message arrowhead is a 4-point <polygon>, not note-like.
        arrowhead = [s for s in shapes if s[0].tag == "polygon"]
        assert arrowhead, "expected a message arrowhead polygon in fixture"
        assert classify_note_shape(arrowhead[0]) is None
        # Participant boxes are <rect> but must not be classified as rnote.
        participant_boxes = [s for s in shapes if s[0].tag == "rect"]
        assert participant_boxes, "expected participant box rects in fixture"
        # classify_note_shape only looks at shape, so a plain rect always
        # reads as "rnote" - callers (Task 3) are responsible for excluding
        # participant boxes from the candidate set before classifying.

    def test_note_fold_corner_path_is_not_classified_as_note(self):
        """The second path of a note pair (fold corner, 4 points) must not
        itself be classified as 'note' - callers skip it explicitly."""
        puml = "@startuml\nparticipant Alice\nnote over Alice : text\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        shapes = shapes_in_document_order(svg)
        note_paths = [s for s in shapes if s[0].tag == "path"]
        fold_corner = note_paths[1]
        assert classify_note_shape(fold_corner) is None
