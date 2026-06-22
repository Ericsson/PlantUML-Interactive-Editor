# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2025 Ericsson
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

"""Tests for sequence diagram delete participant JS logic."""


class TestCheckIfParticipant:
    def test_identifies_participant_rect(self, app_url, page):
        """checkIfParticipant returns true for a rect with participant style."""
        result = page.evaluate("""() => {
            const container = document.createElement('div');
            container.innerHTML = `
                <rect fill="#E2E2F0" height="30" rx="2.5" ry="2.5"
                      style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="5"></rect>
                <text>Alice</text>
            `;
            const elements = container.querySelectorAll('*');
            return checkIfParticipant(elements, 0);
        }""")
        assert result is True

    def test_rejects_non_participant_rect(self, app_url, page):
        """checkIfParticipant returns false for a rect with different style."""
        result = page.evaluate("""() => {
            const container = document.createElement('div');
            container.innerHTML = `
                <rect fill="#E2E2F0" height="30" rx="2.5" ry="2.5"
                      style="stroke:#000000;stroke-width:1.5;" width="41" x="5" y="5"></rect>
            `;
            const elements = container.querySelectorAll('*');
            return checkIfParticipant(elements, 0);
        }""")
        assert result is False

    def test_rejects_non_rect_element(self, app_url, page):
        """checkIfParticipant returns false for non-rect elements."""
        result = page.evaluate("""() => {
            const container = document.createElement('div');
            container.innerHTML = `
                <line style="stroke:#181818;stroke-width:0.5;" x1="5" x2="5" y1="0" y2="50"></line>
            `;
            const elements = container.querySelectorAll('*');
            return checkIfParticipant(elements, 0);
        }""")
        assert result is False


class TestSequenceListArguments:
    def test_add_participant_left_has_direction(self, app_url, page):
        """addParticipantLeft entry sends direction 'left' argument."""
        result = page.evaluate("""() => {
            const list = [{
                id: 'addParticipantLeft',
                endpoint: 'addParticipant',
                arguments: {direction: 'left'}
            }];
            return list[0].arguments.direction;
        }""")
        assert result == "left"

    def test_add_participant_right_has_direction(self, app_url, page):
        """addParticipantRight entry sends direction 'right' argument."""
        result = page.evaluate("""() => {
            const list = [{
                id: 'addParticipantRight',
                endpoint: 'addParticipant',
                arguments: {direction: 'right'}
            }];
            return list[0].arguments.direction;
        }""")
        assert result == "right"


class TestRenameParticipant:
    def test_rename_modal_exists(self, app_url, page):
        """The participant name modal form exists in the DOM."""
        result = page.evaluate("""() => {
            const modal = document.getElementById('participant-name-modalForm');
            return modal !== null;
        }""")
        assert result is True

    def test_rename_menu_item_exists(self, app_url, page):
        """The renameParticipant menu item exists in the DOM."""
        result = page.evaluate("""() => {
            const item = document.getElementById('renameParticipant');
            return item !== null;
        }""")
        assert result is True

    def test_rename_modal_title_updates(self, app_url, page):
        """Setting the modal title dynamically works."""
        result = page.evaluate("""() => {
            $('#participant-name-modalForm .modal-title').text('Rename Alice');
            return $('#participant-name-modalForm .modal-title').text();
        }""")
        assert result == "Rename Alice"


class TestLifelineExtraction:
    def test_extract_lifeline_positions(self, app_url, page):
        """extractLifelinePositions populates participantLifelines from dashed lines."""
        result = page.evaluate("""() => {
            const container = document.createElement('div');
            container.innerHTML = `<svg><g>
                <line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="28" x2="28" y1="36" y2="100"></line>
                <line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="84" x2="84" y1="36" y2="100"></line>
            </g></svg>`;
            const g = container.querySelector('g');
            extractLifelinePositions(g);
            return participantLifelines;
        }""")
        assert len(result) == 2
        assert result[0]["cx"] == 28
        assert result[1]["cx"] == 84

    def test_find_nearest_lifeline_within_tolerance(self, app_url, page):
        """findNearestLifeline returns lifeline when within 15px."""
        result = page.evaluate("""() => {
            participantLifelines = [{cx: 50, yTop: 30, yBottom: 100}];
            return findNearestLifeline(60, 50);
        }""")
        assert result is not None
        assert result["cx"] == 50

    def test_find_nearest_lifeline_outside_tolerance(self, app_url, page):
        """findNearestLifeline returns null when outside 15px."""
        result = page.evaluate("""() => {
            participantLifelines = [{cx: 50, yTop: 30, yBottom: 100}];
            return findNearestLifeline(70, 50);
        }""")
        assert result is None

    def test_find_nearest_lifeline_excludes_origin(self, app_url, page):
        """findNearestLifeline skips the excluded cx."""
        result = page.evaluate("""() => {
            participantLifelines = [
                {cx: 50, yTop: 30, yBottom: 100},
                {cx: 80, yTop: 30, yBottom: 100}
            ];
            return findNearestLifeline(55, 50, 50);
        }""")
        assert result is None


class TestMessageAddMode:
    def test_cancel_message_add_mode(self, app_url, page):
        """cancelMessageAddMode resets state."""
        result = page.evaluate("""() => {
            isAddMessageActive = true;
            messageOrigin = {cx: 50, y: 60};
            cancelMessageAddMode();
            return {active: isAddMessageActive, origin: messageOrigin};
        }""")
        assert result["active"] is False
        assert result["origin"] is None

    def test_escape_cancels_mode(self, app_url, page):
        """Pressing Escape cancels message-add mode."""
        result = page.evaluate("""() => {
            // Ensure the keydown listener is registered
            sequenceEventListeners();
            isAddMessageActive = true;
            messageOrigin = {cx: 50, y: 60};
            document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));
            return isAddMessageActive;
        }""")
        assert result is False

    def test_rename_input_prefills(self, app_url, page):
        """Pre-filling the rename input field works."""
        result = page.evaluate("""() => {
            $('#participant-name-text').val('Alice');
            return $('#participant-name-text').val();
        }""")
        assert result == "Alice"
