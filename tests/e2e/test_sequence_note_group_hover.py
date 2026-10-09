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

"""E2E probe for note hover behavior while an add-mode gesture is active.

Regression guard for the "note turns black during group ghost-box creation"
bug: the note mouseover bails out while an add-mode gesture (group/box/etc.)
is active and therefore never captures the note's original fill, so the
mouseout handler must not write that uncaptured (empty) fill back - doing so
blanks the fill attribute and the note renders black.
"""


def _probe_note_hover(page, mode):
    """Build a standalone rnote rect, run the real setupNoteHandlers wiring,
    then simulate hover-in/hover-out and report the fill at each step.

    `mode` is either "normal" (no add gesture) or "group" (group ghost-box
    active, which makes isSequenceAddMode() true)."""
    return page.evaluate(
        """(mode) => {
            isAddMessageActive = false;
            isAddActivationActive = false;
            isAddGroupActive = false;
            isAddNoteActive = false;
            sequenceHighlighted = [];
            notePositions = [];

            if (mode === 'group') {
                isAddGroupActive = true;
            }

            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            // An rnote rect: note stroke-width, no rounded corners, a real fill.
            const note = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            note.setAttribute('style', 'stroke:#000000;stroke-width:0.5;');
            note.setAttribute('fill', '#feffdd');
            svg.appendChild(note);
            setupNoteHandlers([note]);

            const initialFill = note.getAttribute('fill');

            note.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            const hoverFill = note.getAttribute('fill');

            note.dispatchEvent(new MouseEvent('mouseout', {bubbles: true}));
            const afterMouseoutFill = note.getAttribute('fill');

            // Read the mode flag before tearing it down, otherwise the reset
            // below would make this always report normal mode.
            const sequenceAddMode = isSequenceAddMode();
            isAddGroupActive = false;

            return {
                sequenceAddMode,
                initialFill,
                hoverFill,
                afterMouseoutFill
            };
        }""",
        mode,
    )


class TestSequenceNoteHoverDuringAddMode:
    def test_normal_mode_highlights_and_restores_fill(self, app_url, page):
        result = _probe_note_hover(page, "normal")

        assert result["sequenceAddMode"] is False
        assert result["initialFill"] == "#feffdd"
        # Hover recolors to the highlight gray, mouseout restores the original.
        assert result["hoverFill"] == "#d8d8d8"
        assert result["afterMouseoutFill"] == "#feffdd"

    def test_group_add_mode_leaves_note_fill_untouched(self, app_url, page):
        result = _probe_note_hover(page, "group")

        assert result["sequenceAddMode"] is True
        assert result["initialFill"] == "#feffdd"
        # During an add-mode gesture the note must not be recolored on hover...
        assert result["hoverFill"] == "#feffdd"
        # ...and mouseout must not blank the fill (the bug rendered it black).
        assert result["afterMouseoutFill"] == "#feffdd"
        assert result["afterMouseoutFill"] not in ("", None)
