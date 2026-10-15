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

"""Alias generation for participants whose displayed name contains spaces.

A generated alias has to be a legal bare token in the diagram body and must not
collide with an identifier another participant already answers to.
"""

import pytest
from plantuml_gui.sequence.rename import generate_alias, taken_identifiers


class TestGenerateAlias:
    @pytest.mark.parametrize(
        "new_name, expected",
        [
            ("Space Room", "SpaceRoom"),
            ("Order Service #2", "OrderService2"),
            # split() collapses runs of whitespace, including tabs.
            ("my  spaced   name", "MySpacedName"),
            ("\tleading tab", "LeadingTab"),
            # An acronym keeps its casing: only the first letter is forced up.
            ("REST Gateway", "RESTGateway"),
            # Punctuation is dropped, not escaped.
            ("Payment-Service (v2)", "PaymentServiceV2"),
            # A single word still round-trips.
            ("Alice", "Alice"),
        ],
    )
    def test_pascal_cases_and_sanitizes(self, new_name, expected):
        assert generate_alias(new_name, set()) == expected

    def test_leading_digit_is_prefixed(self):
        """A bare token starting with a digit is not a usable alias."""
        assert generate_alias("2 Fast", set()) == "P2Fast"

    def test_name_with_nothing_aliasable_falls_back(self):
        assert generate_alias("___", set()) == "Participant"

    def test_collision_gets_a_numeric_suffix(self):
        assert generate_alias("Space Room", {"SpaceRoom"}) == "SpaceRoom2"

    def test_suffix_skips_past_every_taken_candidate(self):
        taken = {"SpaceRoom", "SpaceRoom2", "SpaceRoom3"}
        assert generate_alias("Space Room", taken) == "SpaceRoom4"

    def test_collision_against_a_display_name_also_counts(self):
        """PlantUML resolves a reference against displayed names too, so reusing
        one as an alias would merge two lifelines."""
        assert generate_alias("Space Room", {"SpaceRoom"}) != "SpaceRoom"


class TestTakenIdentifiers:
    def test_collects_names_and_aliases(self):
        puml = (
            "@startuml\n"  # 0
            "participant Alice\n"  # 1
            'participant "Long Name" as L\n'  # 2
            "Alice -> L: hi\n"  # 3
            "@enduml"  # 4
        )

        assert taken_identifiers(puml, exclude_line=-1) == {"Alice", "Long Name", "L"}

    def test_excludes_the_line_being_rewritten(self):
        """The declaration under rename must not block its own replacement."""
        puml = "@startuml\nparticipant Alice\nparticipant Bob\n@enduml"

        assert taken_identifiers(puml, exclude_line=1) == {"Bob"}

    def test_ignores_non_declaration_lines(self):
        puml = "@startuml\nAlice -> Bob: hi\nnote over Alice: text\n@enduml"

        assert taken_identifiers(puml, exclude_line=-1) == set()

    def test_non_participant_lifelines_are_not_seen(self):
        """The accepted limitation: an alias duplicating an actor's identifier
        slips through, and PlantUML then merges the two lifelines. Preventing it
        would need a second, wider scan of the source for a collision that
        requires the new name's PascalCase to match an aliased non-participant
        exactly."""
        puml = "@startuml\nactor Customer as SpaceRoom\n@enduml"

        assert taken_identifiers(puml, exclude_line=-1) == set()
