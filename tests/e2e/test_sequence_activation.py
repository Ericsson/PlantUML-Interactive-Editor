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

"""End-to-end tests for sequence diagram activation bar JS logic."""


class TestActivationMenus:
    def test_activate_menu_item_exists(self, app_url, page):
        """The Activate item exists in the sequence (lifeline) context menu."""
        result = page.evaluate(
            "() => document.getElementById('seq-addActivation') !== null"
        )
        assert result is True

    def test_end_type_chooser_exists(self, app_url, page):
        """The Deactivate/Destroy chooser and its items exist in the DOM."""
        result = page.evaluate("""() => {
            return document.getElementById('activation-end-menu') !== null
                && document.getElementById('activation-deactivate') !== null
                && document.getElementById('activation-destroy') !== null;
        }""")
        assert result is True


class TestActivationAddMode:
    def test_lifeline_listeners_do_not_accumulate(self, app_url, page):
        """Re-rendering must not stack duplicate mousemove handlers.

        Regression: setupLifelineInteraction used to add a listener (capturing a
        now-stale svg) on every render, so one mouse move ran the handler many
        times with conflicting coordinates -- breaking the ghost and placing the
        bar using a stale click. After the fix the handler runs exactly once.
        """
        # Re-render several times with growing diagrams to attempt accumulation.
        for msgs in [
            "A1 -> A2: a",
            "A1 -> A2: a\\nA2 -> A1: b",
            "A1 -> A2: a\\nA2 -> A1: b\\nA1 -> A2: c",
        ]:
            page.evaluate(
                """(msgs) => {
                    editor.session.setValue(
                        "@startuml\\nparticipant A1\\nparticipant A2\\n"
                        + msgs + "\\n@enduml");
                }""",
                msgs,
            )
            page.wait_for_timeout(3000)

        count = page.evaluate("""() => {
            window.__amm = 0;
            const orig = handleActivationMouseMove;
            handleActivationMouseMove = function() {
                window.__amm++;
                return orig.apply(this, arguments);
            };
            // Enter activation mode with a synthetic origin (the count does not
            // depend on real snapping data, only on how many listeners fire).
            activationOrigin = {cx: 80, name: 'A2', startMessageIndex: 3, startCy: 60};
            isAddActivationActive = true;

            const svg = document.querySelector('#colb svg');
            const r = svg.getBoundingClientRect();
            document.getElementById('colb-container').dispatchEvent(
                new MouseEvent('mousemove',
                    {clientX: r.x + r.width / 2,
                     clientY: r.y + r.height / 2, bubbles: true}));

            const c = window.__amm;
            handleActivationMouseMove = orig;
            cancelActivationAddMode();
            return c;
        }""")
        assert count == 1

    def test_is_activation_add_mode_reflects_flag(self, app_url, page):
        """isActivationAddMode reflects the mode flag."""
        result = page.evaluate("""() => {
            isAddActivationActive = true;
            const on = isActivationAddMode();
            isAddActivationActive = false;
            const off = isActivationAddMode();
            return {on, off};
        }""")
        assert result["on"] is True
        assert result["off"] is False

    def test_cancel_activation_add_mode_resets_state(self, app_url, page):
        """cancelActivationAddMode clears mode, origin, and end message."""
        result = page.evaluate("""() => {
            isAddActivationActive = true;
            activationOrigin = {cx: 50, name: 'Bob', startMessageIndex: 3, startCy: 40};
            activationEndMessage = {index: 4, cy: 90};
            cancelActivationAddMode();
            return {
                active: isAddActivationActive,
                origin: activationOrigin,
                endMessage: activationEndMessage
            };
        }""")
        assert result["active"] is False
        assert result["origin"] is None
        assert result["endMessage"] is None

    def test_escape_cancels_activation_mode(self, app_url, page):
        """Pressing Escape cancels activation-add mode."""
        result = page.evaluate("""() => {
            sequenceEventListeners();
            isAddActivationActive = true;
            activationOrigin = {cx: 50, name: 'Bob', startMessageIndex: 3, startCy: 40};
            document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));
            return isActivationAddMode();
        }""")
        assert result is False


class TestActivationFlow:
    def _load_diagram(self, page):
        page.evaluate("""() => {
            editor.session.setValue(
                "@startuml\\nparticipant Alice\\nparticipant Bob\\n"
                + "Alice -> Bob: hello\\n@enduml");
        }""")
        page.wait_for_timeout(5000)

    def test_deactivate_flow_updates_puml(self, app_url, page):
        """A full activate -> deactivate gesture adds a balanced pair to the puml."""
        self._load_diagram(page)
        names = page.evaluate("() => participantLifelines.map(l => l.name)")
        assert names == ["Alice", "Bob"]

        # hello is at line index 3 in the loaded puml
        page.evaluate("""() => {
            const bob = participantLifelines[1];
            activationOrigin = {cx: bob.cx, name: bob.name, startMessageIndex: 3, startCy: 60};
            activationEndMessage = {index: 3, cy: 60};
            submitActivation('deactivate');
        }""")
        page.wait_for_timeout(5000)

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert "activate Bob" in lines
        assert "deactivate Bob" in lines

    def test_destroy_flow_updates_puml(self, app_url, page):
        """A full activate -> destroy gesture adds activate + destroy to the puml."""
        self._load_diagram(page)

        page.evaluate("""() => {
            const bob = participantLifelines[1];
            activationOrigin = {cx: bob.cx, name: bob.name, startMessageIndex: 3, startCy: 60};
            activationEndMessage = {index: 3, cy: 60};
            submitActivation('destroy');
        }""")
        page.wait_for_timeout(5000)

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert "activate Bob" in lines
        assert "destroy Bob" in lines

    def test_second_bar_uses_refreshed_message_positions(self, app_url, page):
        """Adding a second bar must work once one already exists.

        After the first bar renders, fetchMessagePositions runs against an SVG
        that now contains an activation rect. This is the scenario that used to
        500 (activation rect mistaken for a participant). Verify message
        positions still resolve and a second balanced bar is added.
        """
        # Three messages so positions are unambiguous.
        page.evaluate("""() => {
            editor.session.setValue(
                "@startuml\\nparticipant Alice\\nparticipant Bob\\n"
                + "Alice -> Bob: m1\\nBob -> Alice: m2\\nAlice -> Bob: m3\\n@enduml");
        }""")
        page.wait_for_timeout(5000)

        # First bar around the first message, driven by the fetched positions.
        page.evaluate("""() => {
            const bob = participantLifelines[1];
            const m = messagePositions[0];
            activationOrigin = {cx: bob.cx, name: bob.name,
                                startMessageIndex: m.index, startCy: m.cy};
            activationEndMessage = {index: m.index, cy: m.cy};
            submitActivation('deactivate');
        }""")
        page.wait_for_timeout(5000)

        # After the bar rendered, positions must still resolve (no 500).
        msg_count = page.evaluate("() => messagePositions.length")
        assert msg_count == 3

        # Second bar around the last message.
        page.evaluate("""() => {
            const bob = participantLifelines[1];
            const m = messagePositions[messagePositions.length - 1];
            activationOrigin = {cx: bob.cx, name: bob.name,
                                startMessageIndex: m.index, startCy: m.cy};
            activationEndMessage = {index: m.index, cy: m.cy};
            submitActivation('deactivate');
        }""")
        page.wait_for_timeout(5000)

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert lines.count("activate Bob") == 2
        assert lines.count("deactivate Bob") == 2


class TestDeleteActivationFlow:
    def _load_bar_diagram(self, page):
        # The page renders its default demo once on load; that late async
        # render can clobber #colb after our setValue. Re-render the sequence
        # diagram until its activation bar is stably present (past the one-time
        # demo render), which makes this robust regardless of render timing.
        bar_present = """() => Array.from(document.querySelectorAll('#colb g rect'))
            .some(r => (r.getAttribute('style') || '')
                .includes('stroke:#181818;stroke-width:1.0')
                && parseFloat(r.getAttribute('x')) < 200)"""
        for _ in range(12):
            page.evaluate("""() => {
                editor.session.setValue(
                    "@startuml\\nparticipant Alice\\nparticipant Bob\\n"
                    + "Alice -> Bob: m1\\nactivate Bob\\nBob -> Alice: m2\\n"
                    + "deactivate Bob\\nAlice -> Bob: m3\\n@enduml");
            }""")
            page.wait_for_timeout(2500)
            if page.evaluate(bar_present):
                return
        raise AssertionError("activation bar never rendered")

    def _right_click_bar(self, page):
        # Dispatch a contextmenu on the activation bar at mapped client coords so
        # it bubbles to the background handler (which detects the bar target).
        return page.evaluate("""() => {
            const bar = Array.from(document.querySelectorAll('#colb g rect'))
                .find(r => (r.getAttribute('style') || '').includes('stroke:#181818;stroke-width:1.0'));
            if (!bar) return false;
            const svg = document.querySelector('#colb svg');
            const x = parseFloat(bar.getAttribute('x'))
                + parseFloat(bar.getAttribute('width')) / 2;
            const y = parseFloat(bar.getAttribute('y')) + 5;
            const pt = svg.createSVGPoint();
            pt.x = x; pt.y = y;
            const s = pt.matrixTransform(svg.getScreenCTM());
            bar.dispatchEvent(new MouseEvent('contextmenu',
                {bubbles: true, cancelable: true, clientX: s.x, clientY: s.y}));
            return true;
        }""")

    def test_right_click_bar_shows_delete_in_sequence_menu(self, app_url, page):
        self._load_bar_diagram(page)
        assert self._right_click_bar(page) is True
        state = page.evaluate("""() => ({
            menu: document.getElementById('sequence-menu').style.display,
            del: document.getElementById('seq-deleteActivation-item').style.display,
            addMsg: document.getElementById('addMessageSolid') !== null,
            activate: document.getElementById('seq-addActivation') !== null
        })""")
        # Full lifeline menu is shown, with the Delete item now visible.
        assert state["menu"] == "block"
        assert state["del"] != "none"
        assert state["addMsg"] is True
        assert state["activate"] is True

    def test_delete_bar_removes_lines(self, app_url, page):
        self._load_bar_diagram(page)
        self._right_click_bar(page)
        page.evaluate("() => document.getElementById('seq-deleteActivation').click()")
        page.wait_for_timeout(5000)

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert "activate Bob" not in lines
        assert "deactivate Bob" not in lines
        # Messages remain.
        assert "Alice -> Bob: m1" in lines
        assert "Bob -> Alice: m2" in lines

    def test_delete_item_hidden_when_not_on_bar(self, app_url, page):
        self._load_bar_diagram(page)
        # Right-click the lifeline line (not a bar rect), near its bottom.
        hidden = page.evaluate("""() => {
            const svg = document.querySelector('#colb svg');
            const lines = Array.from(document.querySelectorAll('#colb g line'))
                .filter(l => (l.getAttribute('style') || '').includes('stroke-dasharray'));
            if (lines.length === 0) return 'no-lifeline';
            // Rightmost dashed lifeline is Bob's.
            const line = lines.reduce((a, b) =>
                parseFloat(a.getAttribute('x1')) > parseFloat(b.getAttribute('x1')) ? a : b);
            const x = parseFloat(line.getAttribute('x1'));
            const y2 = parseFloat(line.getAttribute('y2'));
            const pt = svg.createSVGPoint();
            pt.x = x; pt.y = y2 - 3;
            const s = pt.matrixTransform(svg.getScreenCTM());
            line.dispatchEvent(new MouseEvent('contextmenu',
                {bubbles: true, cancelable: true, clientX: s.x, clientY: s.y}));
            return document.getElementById('seq-deleteActivation-item').style.display;
        }""")
        assert hidden == "none"
