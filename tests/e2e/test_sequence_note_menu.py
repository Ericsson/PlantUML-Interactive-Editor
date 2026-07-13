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

"""E2E tests for the sequence "Add Note" type submenu (menu-replaces-itself
UX): clicking "Add Note" swaps the context menu in place for a Note/H Note/
R Note choice, which itself swaps in place for the existing placement menu.
"""


class TestSequenceNoteTypeMenu:
    def test_add_note_click_shows_type_menu_in_place_of_sequence_menu(
        self, app_url, page
    ):
        result = page.evaluate("""() => {
            noteOperationEventListeners();
            var seqMenu = document.getElementById('sequence-menu');
            seqMenu.style.display = 'block';
            seqMenu.style.left = '123px';
            seqMenu.style.top = '456px';

            document.getElementById('seq-addNote')
                .dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));

            var typeMenu = document.getElementById('seq-note-type-menu');
            return {
                seqMenuDisplay: seqMenu.style.display,
                typeMenuDisplay: typeMenu.style.display,
                typeMenuLeft: typeMenu.style.left,
                typeMenuTop: typeMenu.style.top
            };
        }""")

        assert result["seqMenuDisplay"] == "none"
        assert result["typeMenuDisplay"] == "block"
        assert result["typeMenuLeft"] == "123px"
        assert result["typeMenuTop"] == "456px"

    def test_type_selection_shows_placement_menu_in_place_and_stores_type(
        self, app_url, page
    ):
        result = page.evaluate("""() => {
            noteOperationEventListeners();
            cancelNoteAddMode();

            var typeMenu = document.getElementById('seq-note-type-menu');
            typeMenu.style.display = 'block';
            typeMenu.style.left = '200px';
            typeMenu.style.top = '300px';

            document.querySelector('#seq-note-type-menu [data-note-type="hnote"]')
                .dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));

            var placementMenu = document.getElementById('seq-note-placement-menu');
            return {
                typeMenuDisplay: typeMenu.style.display,
                placementMenuDisplay: placementMenu.style.display,
                placementMenuLeft: placementMenu.style.left,
                placementMenuTop: placementMenu.style.top,
                selectedType: selectedNoteType,
                active: isAddNoteActive
            };
        }""")

        assert result["typeMenuDisplay"] == "none"
        assert result["placementMenuDisplay"] == "block"
        assert result["placementMenuLeft"] == "200px"
        assert result["placementMenuTop"] == "300px"
        assert result["selectedType"] == "hnote"
        assert result["active"] is True

    def test_each_note_type_choice_stores_correct_type(self, app_url, page):
        result = page.evaluate("""() => {
            noteOperationEventListeners();
            var results = {};
            ['note', 'hnote', 'rnote'].forEach(function(type) {
                cancelNoteAddMode();
                document.querySelector('#seq-note-type-menu [data-note-type="' + type + '"]')
                    .dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
                results[type] = selectedNoteType;
            });
            return results;
        }""")

        assert result == {"note": "note", "hnote": "hnote", "rnote": "rnote"}

    def test_cancel_note_add_mode_resets_selected_type(self, app_url, page):
        result = page.evaluate("""() => {
            noteOperationEventListeners();
            document.querySelector('#seq-note-type-menu [data-note-type="rnote"]')
                .dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
            var beforeCancel = selectedNoteType;

            cancelNoteAddMode();

            return {
                beforeCancel: beforeCancel,
                afterCancel: selectedNoteType,
                active: isAddNoteActive
            };
        }""")

        assert result["beforeCancel"] == "rnote"
        assert result["afterCancel"] == "note"
        assert result["active"] is False

    def test_clicking_outside_note_type_items_does_nothing(self, app_url, page):
        result = page.evaluate("""() => {
            noteOperationEventListeners();
            cancelNoteAddMode();
            var typeMenu = document.getElementById('seq-note-type-menu');
            typeMenu.style.display = 'block';

            typeMenu.dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));

            return {
                typeMenuDisplay: typeMenu.style.display,
                selectedType: selectedNoteType,
                active: isAddNoteActive
            };
        }""")

        assert result["typeMenuDisplay"] == "block"
        assert result["selectedType"] == "note"
        assert result["active"] is False


class TestSequenceNoteCreateFlowWithType:
    """Full integration: type menu -> placement menu -> modal -> submit,
    verifying noteType reaches the backend and produces the right keyword."""

    _PUML = "@startuml\\nparticipant Alice\\nparticipant Bob\\nAlice -> Bob: hello\\n@enduml"

    def _load_sequence(self, page, retries=12, wait_ms=2500):
        for _ in range(retries):
            page.evaluate(f"() => editor.session.setValue('{self._PUML}')")
            page.wait_for_timeout(wait_ms)
            count = page.evaluate("() => participantLifelines.length")
            if count == 2:
                return
        raise AssertionError("participantLifelines never loaded")

    def _create_note_via_menus(self, page, note_type, text):
        page.evaluate("""() => { noteOperationEventListeners(); }""")
        page.evaluate("""() => {
            const alice = participantLifelines[0];
            messageOrigin = {cx: alice.cx, y: 40, name: alice.name};
            firstClickCoordinates = [alice.cx, 40];
        }""")
        page.evaluate(
            """(noteType) => {
                document.querySelector(
                    '#seq-note-type-menu [data-note-type="' + noteType + '"]'
                ).dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
                document.querySelector('#seq-note-placement-menu [data-placement="over"]')
                    .dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));
            }""",
            note_type,
        )
        page.evaluate(
            """(text) => { document.getElementById('seq-note-text').value = text; }""",
            text,
        )
        page.evaluate("""() => { submitNote(); }""")
        page.wait_for_timeout(3000)

    def test_creates_hnote_end_to_end(self, app_url, page):
        self._load_sequence(page)
        self._create_note_via_menus(page, "hnote", "Hex note text")

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert "hnote over Alice : Hex note text" in lines

    def test_creates_rnote_end_to_end(self, app_url, page):
        self._load_sequence(page)
        self._create_note_via_menus(page, "rnote", "Rect note text")

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert "rnote over Alice : Rect note text" in lines

    def test_creates_plain_note_when_note_type_selected(self, app_url, page):
        self._load_sequence(page)
        self._create_note_via_menus(page, "note", "Plain note text")

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert "note over Alice : Plain note text" in lines

    def test_note_type_resets_to_note_after_create(self, app_url, page):
        self._load_sequence(page)
        self._create_note_via_menus(page, "hnote", "First note")

        reset_type = page.evaluate("() => selectedNoteType")
        assert reset_type == "note"
