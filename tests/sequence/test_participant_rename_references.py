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

"""Token-aware rewriting of participant references.

A rename used to be a blanket ``puml.replace``, which also rewrote any prose
that happened to contain the name. These tests fix the boundary: only positions
where PlantUML expects a participant are rewritten, and everything else -- most
importantly message text and note bodies -- is returned byte-for-byte.
"""

import pytest
from plantuml_gui.sequence.rename import rewrite_participant_references


def rewrite(line, old="Alice", new="SpaceRoom"):
    """Rewrite a single line, for compact table-driven cases."""
    return rewrite_participant_references(line, old, new)


class TestMessageEndpoints:
    @pytest.mark.parametrize(
        "line, expected",
        [
            ("Alice -> Bob: hi", "SpaceRoom -> Bob: hi"),
            ("Bob -> Alice: hi", "Bob -> SpaceRoom: hi"),
            ("Alice -> Alice: self", "SpaceRoom -> SpaceRoom: self"),
            ("Bob <- Alice: reverse", "Bob <- SpaceRoom: reverse"),
            ("Bob <--> Alice: both ways", "Bob <--> SpaceRoom: both ways"),
            ("Alice -[#red]> Bob: colored", "SpaceRoom -[#red]> Bob: colored"),
            ("Alice->Bob: no spaces", "SpaceRoom->Bob: no spaces"),
            ("Alice ->x Bob: lost", "SpaceRoom ->x Bob: lost"),
            # A message with no text at all is still a message.
            ("Alice -> Bob", "SpaceRoom -> Bob"),
            # Indentation (inside a group block) is preserved.
            ("    Alice -> Bob: hi", "    SpaceRoom -> Bob: hi"),
        ],
    )
    def test_endpoints_are_rewritten(self, line, expected):
        assert rewrite(line) == expected

    def test_message_text_is_never_rewritten(self):
        """The blanket replace corrupted prose; only endpoints may change."""
        line = "Alice -> Bob: tell Alice that Alice left"
        assert rewrite(line) == "SpaceRoom -> Bob: tell Alice that Alice left"

    def test_activation_shorthand_survives(self):
        assert rewrite("Bob -> Alice++: hi") == "Bob -> SpaceRoom++: hi"

    def test_name_containing_a_dash_is_not_split(self):
        """A lone dash inside a name must not be read as the arrow."""
        line = "Web-Server -> Bob: hi"
        assert (
            rewrite(line, old="Web-Server", new="WebServer") == "WebServer -> Bob: hi"
        )

    def test_other_participants_are_untouched(self):
        assert rewrite("Bob -> Carol: hi") == "Bob -> Carol: hi"

    def test_partial_name_match_is_not_rewritten(self):
        """Substring replacement turned `Alice2` into `SpaceRoom2`."""
        assert rewrite("Alice2 -> Bob: hi") == "Alice2 -> Bob: hi"


class TestActivationLines:
    @pytest.mark.parametrize(
        "line, expected",
        [
            ("activate Alice", "activate SpaceRoom"),
            ("deactivate Alice", "deactivate SpaceRoom"),
            ("destroy Alice", "destroy SpaceRoom"),
            ("create Alice", "create SpaceRoom"),
            ("activate Alice #red", "activate SpaceRoom #red"),
            ("    activate Alice", "    activate SpaceRoom"),
        ],
    )
    def test_subject_is_rewritten(self, line, expected):
        assert rewrite(line) == expected

    def test_other_participant_untouched(self):
        assert rewrite("activate Bob") == "activate Bob"


class TestNotePlacement:
    @pytest.mark.parametrize(
        "line, expected",
        [
            ("note over Alice: text", "note over SpaceRoom: text"),
            ("note over Alice : text", "note over SpaceRoom : text"),
            ("note left of Alice: text", "note left of SpaceRoom: text"),
            ("note right of Alice: text", "note right of SpaceRoom: text"),
            ("rnote over Alice: text", "rnote over SpaceRoom: text"),
            ("hnote over Alice: text", "hnote over SpaceRoom: text"),
            ("note #FFAAAA over Alice: text", "note #FFAAAA over SpaceRoom: text"),
            # Spanning notes name two participants; only the match changes.
            ("note over Alice, Bob: text", "note over SpaceRoom, Bob: text"),
            ("note over Bob, Alice: text", "note over Bob, SpaceRoom: text"),
            # Block note opening line, no inline text.
            ("note over Alice", "note over SpaceRoom"),
        ],
    )
    def test_placement_is_rewritten(self, line, expected):
        assert rewrite(line) == expected

    def test_note_body_is_never_rewritten(self):
        """A block note's body is prose and must survive untouched."""
        puml = "note over Alice\nAlice did something\nend note"
        assert rewrite(puml) == "note over SpaceRoom\nAlice did something\nend note"

    def test_message_attached_note_has_no_participant(self):
        assert rewrite("note left : text") == "note left : text"

    def test_note_text_mentioning_the_name_is_untouched(self):
        line = "note over Bob: Alice waits"
        assert rewrite(line) == "note over Bob: Alice waits"


class TestRefOver:
    def test_ref_targets_are_rewritten(self):
        assert rewrite("ref over Alice, Bob: see other") == (
            "ref over SpaceRoom, Bob: see other"
        )


class TestNonReferenceLines:
    @pytest.mark.parametrize(
        "line",
        [
            "@startuml",
            "@enduml",
            # A declaration is rebuilt by the caller, not rewritten here.
            "participant Alice",
            'participant "Alice" as Alice',
            # Free text that merely mentions the name.
            "title Alice and friends",
            "group Alice waits",
            'box "Alice team"',
            "/' Alice is a comment '/",
            "autonumber",
            "end note",
        ],
    )
    def test_line_is_returned_unchanged(self, line):
        assert rewrite(line) == line


class TestQuotedReferences:
    def test_quoted_reference_is_rewritten(self):
        """A participant declared `participant "Old Name"` with no alias is
        referred to in quotes, so the quoted spelling has to match too."""
        puml = 'note over "Old Name": text\n"Old Name" -> Bob: hi'
        assert rewrite_participant_references(puml, "Old Name", "NewName") == (
            "note over NewName: text\nNewName -> Bob: hi"
        )


class TestWholeDiagram:
    def test_only_reference_sites_change(self):
        puml = (
            "@startuml\n"
            "participant Alice\n"
            "participant Bob\n"
            "Alice -> Bob: ask Alice later\n"
            "activate Bob\n"
            "note over Alice: Alice thinks\n"
            "Bob --> Alice: reply\n"
            "deactivate Bob\n"
            "@enduml"
        )

        assert (
            rewrite_participant_references(puml, "Alice", "SpaceRoom")
            == (
                "@startuml\n"
                "participant Alice\n"  # declaration handled by the caller
                "participant Bob\n"
                "SpaceRoom -> Bob: ask Alice later\n"  # text preserved
                "activate Bob\n"
                "note over SpaceRoom: Alice thinks\n"  # text preserved
                "Bob --> SpaceRoom: reply\n"
                "deactivate Bob\n"
                "@enduml"
            )
        )
