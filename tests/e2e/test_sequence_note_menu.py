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

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError


def _right_click_until_menu(page, locate_xy, menu_selector, attempts=5):
    """Right-click at freshly computed coordinates, retrying until the menu
    appears (or the attempts run out, re-raising the timeout).

    The sequence demo re-renders the diagram a few times right after it loads,
    which can move the lifelines/notes between when a coordinate is computed
    and when the click lands - so a single click occasionally misses the
    target and the context menu never opens. Recomputing the coordinate and
    retrying makes the gesture robust against that render race without hiding
    a genuine failure (the final attempt still raises)."""
    for attempt in range(attempts):
        x, y = locate_xy()
        page.mouse.click(x, y, button="right")
        try:
            page.wait_for_selector(menu_selector, state="visible", timeout=3000)
            return
        except PlaywrightTimeoutError:
            if attempt == attempts - 1:
                raise


def _open_sequence_demo(page):
    """Switch the app to sequence mode via the real "Sequence Demo" menu
    item, matching how an end user would do it (not editor.setValue)."""
    page.click(".toolbar-btn.dropdown-toggle")
    page.wait_for_selector("#sequence", state="visible", timeout=15000)
    page.click("#sequence")
    page.wait_for_function(
        "() => participantLifelines && participantLifelines.length === 3",
        timeout=15000,
    )


def _right_click_lifeline(page, lifeline_index=0, y_offset=60):
    """Real right-click near a lifeline, converting SVG user-space
    coordinates to screen coordinates the same way a real click would land,
    so this exercises the actual DOM event/bubbling pipeline (unlike
    dispatchEvent, which does not interact with Bootstrap's document-level
    click handlers)."""

    def locate():
        return page.evaluate(
            """(args) => {
                const svg = document.querySelector('#colb svg');
                const lifeline = participantLifelines[args.index];
                const pt = svg.createSVGPoint();
                pt.x = lifeline.cx;
                pt.y = args.yOffset;
                const screenPt = pt.matrixTransform(svg.getScreenCTM());
                return [screenPt.x, screenPt.y];
            }""",
            {"index": lifeline_index, "yOffset": y_offset},
        )

    _right_click_until_menu(page, locate, "#sequence-menu")


def _create_note_via_real_clicks(page, note_type, text, lifeline_index=0):
    """Create a note through the real menu flow (type -> placement -> text
    -> submit) and wait for it to land in the editor and in notePositions."""
    _right_click_lifeline(page, lifeline_index=lifeline_index)
    page.click("#seq-addNote")
    page.click(f'#seq-note-type-menu [data-note-type="{note_type}"]')
    page.click('#seq-note-placement-menu [data-placement="over"]')
    page.fill("#seq-note-text", text)
    page.click("#seq-submit-note")
    page.wait_for_function(
        f"() => editor.session.getValue().includes({text!r})",
        timeout=15000,
    )
    page.wait_for_function(
        "() => notePositions && notePositions.length > 0", timeout=15000
    )


def _right_click_note(page, note_ordinal=0, lifeline_index=0):
    """Real right-click on a note already present in the diagram.

    Locates the actual rendered note shape (path/polygon/rect) via the
    same shape classification the frontend uses, then clicks the center
    of its bounding box - robust regardless of whether the shape's cy
    convention is its top edge (plain "note") or true center (hnote/
    rnote), unlike a fixed y-offset from notePositions[].cy."""

    def locate():
        return page.evaluate(
            """(args) => {
                const svg = document.querySelector('#colb svg');
                const shapes = Array.from(svg.querySelectorAll('path, polygon, rect'))
                    .filter(el => isNoteCandidate(el) && classifyNoteShape(el) !== null);
                const shape = shapes[args.noteOrdinal];
                const box = shape.getBoundingClientRect();
                return [box.x + box.width / 2, box.y + box.height / 2];
            }""",
            {"noteOrdinal": note_ordinal},
        )

    _right_click_until_menu(page, locate, "#seq-note-menu")


class TestSequenceNoteTypeMenuRealClicks:
    """Regression coverage using genuine mouse clicks (not dispatchEvent),
    since Bootstrap 4's dropdown module attaches a document-level click
    listener that closes any .dropdown-menu on click - including one this
    code just opened, if the triggering click's event isn't stopped from
    bubbling to document. dispatchEvent-based tests do not bubble the same
    way and previously missed this regression."""

    def test_real_click_through_type_and_placement_menus(self, app_url, page):
        _open_sequence_demo(page)
        _right_click_lifeline(page)

        page.click("#seq-addNote")
        assert (
            page.evaluate(
                "() => document.getElementById('seq-note-type-menu').style.display"
            )
            == "block"
        )

        page.click('#seq-note-type-menu [data-note-type="hnote"]')

        # The real bug: this used to be reset back to "none" immediately
        # after being shown, because the click bubbled to Bootstrap's
        # document-level dropdown auto-close listener.
        assert (
            page.evaluate(
                "() => document.getElementById('seq-note-type-menu').style.display"
            )
            == "none"
        )
        assert (
            page.evaluate(
                "() => document.getElementById('seq-note-placement-menu').style.display"
            )
            == "block"
        )
        assert page.evaluate("() => selectedNoteType") == "hnote"

    def test_real_click_creates_hnote_end_to_end(self, app_url, page):
        _open_sequence_demo(page)
        _right_click_lifeline(page)

        page.click("#seq-addNote")
        page.click('#seq-note-type-menu [data-note-type="hnote"]')
        page.click('#seq-note-placement-menu [data-placement="over"]')

        page.fill("#seq-note-text", "Real click hex note")
        page.click("#seq-submit-note")
        page.wait_for_function(
            "() => editor.session.getValue().includes('Real click hex note')",
            timeout=15000,
        )

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert "hnote over bob : Real click hex note" in lines


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


class TestSequenceNoteModalTypeSelector:
    """Covers the note modal's type radio selector: hidden during Add
    (the type was already chosen via the type submenu before the modal
    ever opens) and visible during Edit, preselected to the note's
    detected type. The checked radio (internal state, even while hidden)
    is still the source of truth submitNote() reads from. All driven by
    real clicks, per the stopPropagation lesson."""

    def test_add_mode_hides_type_selector_but_preselects_submenu_choice(
        self, app_url, page
    ):
        _open_sequence_demo(page)
        _right_click_lifeline(page)

        page.click("#seq-addNote")
        page.click('#seq-note-type-menu [data-note-type="rnote"]')
        page.click('#seq-note-placement-menu [data-placement="over"]')

        assert (
            page.evaluate(
                "() => document.getElementById('seq-note-type-group').style.display"
            )
            == "none"
        )
        assert page.is_checked("#seq-note-type-rnote")
        assert not page.is_checked("#seq-note-type-note")
        assert not page.is_checked("#seq-note-type-hnote")

    def test_add_mode_defaults_to_note_when_type_menu_skipped(self, app_url, page):
        """Defensive: even if the modal were opened without going through
        the type submenu (selectedNoteType still at its default), the
        radio should reflect the default "note" type."""
        _open_sequence_demo(page)
        page.evaluate("() => { cancelNoteAddMode(); }")
        _right_click_lifeline(page)

        page.click("#seq-addNote")
        page.click('#seq-note-type-menu [data-note-type="note"]')
        page.click('#seq-note-placement-menu [data-placement="over"]')

        assert page.is_checked("#seq-note-type-note")

    def test_edit_mode_shows_type_selector_preselected_to_detected_type(
        self, app_url, page
    ):
        _open_sequence_demo(page)
        _create_note_via_real_clicks(page, "hnote", "Edit-preselect hex note")

        _right_click_note(page)
        page.click("#seq-editNote")
        page.wait_for_selector(
            "#seq-note-modalForm.show", state="visible", timeout=15000
        )

        assert (
            page.evaluate(
                "() => document.getElementById('seq-note-type-group').style.display"
            )
            == "block"
        )
        assert page.is_checked("#seq-note-type-hnote")
        assert not page.is_checked("#seq-note-type-note")
        assert not page.is_checked("#seq-note-type-rnote")
        assert page.input_value("#seq-note-text") == "Edit-preselect hex note"

    def test_edit_flow_changes_note_type_end_to_end(self, app_url, page):
        _open_sequence_demo(page)
        _create_note_via_real_clicks(page, "note", "Original note text")

        _right_click_note(page)
        page.click("#seq-editNote")
        page.wait_for_selector(
            "#seq-note-modalForm.show", state="visible", timeout=15000
        )

        # Confirm it preselected "note", then switch to "rnote" and submit.
        assert page.is_checked("#seq-note-type-note")
        page.check("#seq-note-type-rnote")
        page.click("#seq-submit-note")
        page.wait_for_function(
            "() => editor.session.getValue().includes('rnote over')",
            timeout=15000,
        )

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert any(
            line.startswith("rnote over") and "Original note text" in line
            for line in lines
        )
        assert not any(line.startswith("note over") for line in lines)

    def test_edit_flow_keeps_type_when_radio_unchanged(self, app_url, page):
        _open_sequence_demo(page)
        _create_note_via_real_clicks(page, "hnote", "Unchanged type note")

        _right_click_note(page)
        page.click("#seq-editNote")
        page.wait_for_selector(
            "#seq-note-modalForm.show", state="visible", timeout=15000
        )

        page.fill("#seq-note-text", "Unchanged type note edited")
        page.click("#seq-submit-note")
        page.wait_for_function(
            "() => editor.session.getValue().includes('Unchanged type note edited')",
            timeout=15000,
        )

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert "hnote over bob : Unchanged type note edited" in lines


class TestMultiLineNoteRightClick:
    """Regression: right-clicking any line of a multi-line note must open
    the note context menu, not the message menu.

    PlantUML renders each note line as its own <text> element in sequence
    after the note shape. Only the first line's previousElementSibling is
    the note shape; lines 2+ follow the preceding line's text. The old
    single-sibling exclusion therefore missed lines 2+, leaving them
    hoverable and wired to the message menu. isNoteText() walks back over
    the earlier lines to the anchoring shape, so every line is excluded
    from message handling and given pointer-events:none (clicks fall
    through to the note shape, which opens the note menu)."""

    _PUML = (
        "@startuml\\nparticipant Alice\\nparticipant Bob\\n"
        "note over Alice\\nline one\\nline two\\nline three\\nend note\\n"
        "Alice -> Bob : hello\\n@enduml"
    )

    def _load(self, page, retries=12, wait_ms=2500):
        for _ in range(retries):
            page.evaluate(f"() => editor.session.setValue('{self._PUML}')")
            page.wait_for_timeout(wait_ms)
            count = page.evaluate("() => participantLifelines.length")
            if count == 2:
                return
        raise AssertionError("participantLifelines never loaded")

    def _note_line_count(self, page):
        return page.evaluate(
            """() => {
                const svg = document.querySelector('#colb svg');
                return Array.from(svg.querySelectorAll('text'))
                    .filter(el => isNoteText(el)).length;
            }"""
        )

    def _right_click_note_line(self, page, line_index):
        """Right-click the center of the Nth note-body text line."""
        x, y = page.evaluate(
            """(idx) => {
                const svg = document.querySelector('#colb svg');
                const texts = Array.from(svg.querySelectorAll('text'))
                    .filter(el => isNoteText(el));
                const box = texts[idx].getBoundingClientRect();
                return [box.x + box.width / 2, box.y + box.height / 2];
            }""",
            line_index,
        )
        page.mouse.click(x, y, button="right")

    def test_all_note_lines_detected_as_note_text(self, app_url, page):
        _open_sequence_demo(page)
        self._load(page)
        # All three lines must be recognized as note text (the bug missed
        # lines 2 and 3).
        assert self._note_line_count(page) == 3

    def test_right_click_second_line_opens_note_menu(self, app_url, page):
        _open_sequence_demo(page)
        self._load(page)

        self._right_click_note_line(page, 1)  # "line two"
        page.wait_for_selector("#seq-note-menu", state="visible", timeout=15000)
        assert (
            page.evaluate("() => document.getElementById('message-menu').style.display")
            != "block"
        )

    def test_right_click_last_line_opens_note_menu(self, app_url, page):
        _open_sequence_demo(page)
        self._load(page)

        self._right_click_note_line(page, 2)  # "line three"
        page.wait_for_selector("#seq-note-menu", state="visible", timeout=15000)
        assert (
            page.evaluate("() => document.getElementById('message-menu').style.display")
            != "block"
        )
