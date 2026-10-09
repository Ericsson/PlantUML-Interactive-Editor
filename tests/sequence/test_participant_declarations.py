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

"""Parsing of participant declaration lines.

The rename logic has to tell apart the displayed name (what the SVG shows, and
therefore what a click resolves to) from the alias (what the diagram body
refers to), and must hand back every modifier it did not touch. These tests pin
that split down for each declaration form PlantUML accepts.
"""

import pytest
from plantuml_gui.sequence.classes import (
    parse_participant_declaration,
    participant_declarations,
    reference_name_for,
)


class TestParseParticipantDeclaration:
    def test_bare_name(self):
        declaration = parse_participant_declaration("participant Alice")
        assert declaration is not None
        assert declaration.name == "Alice"
        assert declaration.alias is None
        assert declaration.rest == ""
        assert declaration.quoted is False
        assert declaration.reference_name == "Alice"

    def test_quoted_name_without_alias(self):
        declaration = parse_participant_declaration('participant "Long Name"')
        assert declaration is not None
        assert declaration.name == "Long Name"
        assert declaration.alias is None
        assert declaration.quoted is True
        # With no alias, the body has to refer to the quoted displayed name.
        assert declaration.reference_name == "Long Name"

    def test_bare_name_with_alias(self):
        declaration = parse_participant_declaration("participant Alice as A")
        assert declaration is not None
        assert declaration.name == "Alice"
        assert declaration.alias == "A"
        assert declaration.quoted is False
        assert declaration.reference_name == "A"

    def test_quoted_name_with_alias(self):
        declaration = parse_participant_declaration('participant "Long Name" as L')
        assert declaration is not None
        assert declaration.name == "Long Name"
        assert declaration.alias == "L"
        assert declaration.quoted is True
        assert declaration.reference_name == "L"

    def test_quoted_alias(self):
        declaration = parse_participant_declaration('participant Alice as "A B"')
        assert declaration is not None
        assert declaration.name == "Alice"
        assert declaration.alias == "A B"

    @pytest.mark.parametrize(
        "line, expected_rest",
        [
            ("participant Alice order 10", " order 10"),
            ("participant Alice #lightblue", " #lightblue"),
            ("participant Alice as A order 10 #red", " order 10 #red"),
            ('participant "Long Name" as L <<stereotype>>', " <<stereotype>>"),
        ],
    )
    def test_modifiers_are_captured_verbatim(self, line, expected_rest):
        """Anything after the name/alias must survive a rewrite untouched.

        The rename rebuilds the declaration from these parts, so a modifier that
        lands in no group is a modifier silently deleted from the user's diagram.
        """
        declaration = parse_participant_declaration(line)
        assert declaration is not None
        assert declaration.rest == expected_rest

    @pytest.mark.parametrize(
        "keyword",
        ["actor", "boundary", "control", "entity", "database", "collections", "queue"],
    )
    def test_other_lifeline_keywords_are_not_declarations(self, keyword):
        """Only `participant` draws the rounded header rect the editor detects,
        so the other lifeline keywords can be neither clicked nor renamed and
        are deliberately not parsed."""
        assert parse_participant_declaration(f'{keyword} "Long Name" as L') is None

    def test_indentation_is_tolerated(self):
        """Declarations inside a box are indented."""
        declaration = parse_participant_declaration("    participant Alice")
        assert declaration is not None
        assert declaration.name == "Alice"

    @pytest.mark.parametrize(
        "line",
        [
            "Alice -> Bob: hi",
            "note over Alice: text",
            "activate Alice",
            "@startuml",
            "",
            # A word merely starting with the keyword is not a declaration.
            "participants Alice",
        ],
    )
    def test_non_declarations_return_none(self, line):
        assert parse_participant_declaration(line) is None


class TestParticipantDeclarations:
    def test_returns_declarations_in_source_order_with_line_indexes(self):
        puml = (
            "@startuml\n"  # 0
            "participant Alice\n"  # 1
            "Alice -> Bob: hi\n"  # 2
            'participant "Long Name" as L\n'  # 3
            "@enduml"  # 4
        )
        assert [
            (index, declaration.name)
            for index, declaration in participant_declarations(puml)
        ] == [(1, "Alice"), (3, "Long Name")]

    def test_implicit_participant_has_no_declaration(self):
        puml = "@startuml\nAlice -> Bob: hi\n@enduml"
        assert participant_declarations(puml) == []

    def test_a_non_participant_cannot_claim_a_participant_line(self):
        """Two lifelines may share a displayed name when their identifiers
        differ. Were `actor` parsed as a declaration, its line would be handed to
        the separate `participant Alice`, which would also inherit the actor's
        alias -- so a rename would rewrite the actor and leave the participant
        alone."""
        puml = (
            "@startuml\n"  # 0
            'actor "Alice" as A\n'  # 1
            "participant Alice\n"  # 2
            "A -> Alice: hi\n"  # 3
            "@enduml"  # 4
        )

        assert [
            (index, declaration.name, declaration.alias)
            for index, declaration in participant_declarations(puml)
        ] == [(2, "Alice", None)]


class TestReferenceNameFor:
    def test_alias_when_declared(self):
        puml = '@startuml\nparticipant "Space Room" as SpaceRoom\n@enduml'
        assert reference_name_for(puml, "Space Room") == "SpaceRoom"

    def test_display_name_when_no_alias(self):
        puml = "@startuml\nparticipant Alice\n@enduml"
        assert reference_name_for(puml, "Alice") == "Alice"

    def test_display_name_when_not_declared(self):
        """An implicit participant is referred to by its displayed name."""
        puml = "@startuml\nAlice -> Bob: hi\n@enduml"
        assert reference_name_for(puml, "Bob") == "Bob"
