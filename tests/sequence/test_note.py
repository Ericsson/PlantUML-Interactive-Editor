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

"""Tests for sequence diagram note operations."""

import re

from plantuml_gui.sequence.note import add_note
from plantuml_gui.shared.render import _create_svg_from_uml


def extract_g_inner(svg_string):
    """Extract the innerHTML of the <g> element from full SVG."""
    match = re.search(r"<g>(.*?)</g>", svg_string, re.DOTALL)
    if match:
        return match.group(1)
    return None


class TestAddNote:
    def test_add_note_over(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "over", "My note", 0.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : My note\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_note_left(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "left", "Left note", 0.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote left of Alice : Left note\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_note_right(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Bob", "right", "Right note", 0.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote right of Bob : Right note\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_note_spanning(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "spanning", "Span note", 0.0, "Bob")
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice, Bob : Span note\nAlice -> Bob: Hello\n@enduml"
        assert result == expected

    def test_add_note_after_all_messages(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        # Use a very large y so it goes after all messages
        result = add_note(puml, svg, "Alice", "over", "End note", 99999.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\nnote over Alice : End note\n@enduml"
        assert result == expected

    def test_add_note_between_messages(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: First\nBob -> Alice: Second\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        # Parse messages to get cy values and pick a y between them
        from plantuml_gui.sequence.classes import Diagram

        diagram = Diagram.from_svg(svg, puml)
        y_between = (diagram.messages[0].cy + diagram.messages[1].cy) / 2
        result = add_note(puml, svg, "Alice", "over", "Middle note", y_between)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: First\nnote over Alice : Middle note\nBob -> Alice: Second\n@enduml"
        assert result == expected

    def test_add_note_empty_text_returns_unchanged(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\nAlice -> Bob: Hello\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "over", "", 0.0)
        assert result == puml

    def test_add_note_no_messages(self):
        puml = "@startuml\nparticipant Alice\nparticipant Bob\n@enduml"
        svg = extract_g_inner(_create_svg_from_uml(puml))
        result = add_note(puml, svg, "Alice", "over", "Solo note", 50.0)
        expected = "@startuml\nparticipant Alice\nparticipant Bob\nnote over Alice : Solo note\n@enduml"
        assert result == expected
