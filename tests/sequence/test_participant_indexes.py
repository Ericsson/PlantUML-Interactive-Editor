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

"""Tests for mapping participants to the puml line that declares them.

Participants can appear in a diagram without a declaration line -- a message
like ``Alice -> Bob: hi`` introduces both. The mapping used to pair declaration
lines with diagram-ordered participants positionally, which silently shifted
every participant after the first implicit one onto some other participant's
line, and left the trailing ones reporting -1 ("not found").

That index feeds box creation and participant hover-highlighting, so a wrong
value edits or highlights the wrong line. Rendering real SVG here rather than
hand-writing rects, so the diagram order is PlantUML's own.
"""

from plantuml_gui.sequence.classes import Diagram
from plantuml_gui.shared.render import _create_svg_from_uml


def _participants(puml):
    """{name: puml line index} as reported for a real render of `puml`."""
    svg = _create_svg_from_uml(puml)
    inner = svg[svg.index(">", svg.index("<g")) + 1 : svg.rindex("</g>")]
    diagram = Diagram.from_svg(inner, puml)
    return {p.name: p.index for p in diagram.participants}


def test_all_participants_declared():
    puml = "@startuml\nparticipant a\nparticipant b\na -> b: m\n@enduml"

    assert _participants(puml) == {"a": 1, "b": 2}


def test_implicit_participant_does_not_shift_later_declarations():
    """The reported bug: `participant1` reported -1 while its own declaration
    sat on line 3, and `Alice` was handed that line instead."""
    puml = (
        "@startuml\n"  # 0
        "participant t\n"  # 1
        "Alice -> Bob: h\n"  # 2
        "participant participant1\n"  # 3
        "@enduml"  # 4
    )

    indexes = _participants(puml)

    assert indexes["t"] == 1
    assert indexes["participant1"] == 3
    # Implicit participants genuinely have no line to point at.
    assert indexes["Alice"] == -1
    assert indexes["Bob"] == -1


def test_fully_implicit_participants_report_not_found():
    puml = "@startuml\nAlice -> Bob: h\n@enduml"

    assert _participants(puml) == {"Alice": -1, "Bob": -1}


def test_declaration_after_implicit_use_is_still_found():
    puml = (
        "@startuml\n"  # 0
        "Alice -> Bob: h\n"  # 1
        "participant Bob\n"  # 2  declared late, but declared
        "@enduml"  # 3
    )

    indexes = _participants(puml)

    assert indexes["Bob"] == 2
    assert indexes["Alice"] == -1


def test_quoted_display_name_is_matched():
    """PlantUML renders the quoted text, which is what the SVG gives us, so the
    alias must not be what we match on."""
    puml = (
        "@startuml\n"  # 0
        'participant "Long Name" as L\n'  # 1
        "participant b\n"  # 2
        "L -> b: m\n"  # 3
        "@enduml"  # 4
    )

    indexes = _participants(puml)

    assert indexes["Long Name"] == 1
    assert indexes["b"] == 2


def test_declaration_with_trailing_color_is_matched():
    puml = "@startuml\nparticipant a #red\nparticipant b\na -> b: m\n@enduml"

    indexes = _participants(puml)

    assert indexes["a"] == 1
    assert indexes["b"] == 2


def test_participant_named_like_a_prefix_of_another():
    """`startswith`-style matching on names would pair `ab` with `a`'s line."""
    puml = "@startuml\nparticipant ab\nparticipant a\nab -> a: m\n@enduml"

    indexes = _participants(puml)

    assert indexes["ab"] == 1
    assert indexes["a"] == 2
