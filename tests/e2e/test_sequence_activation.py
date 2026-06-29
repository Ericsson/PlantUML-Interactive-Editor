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
        """cancelActivationAddMode clears mode and origin."""
        result = page.evaluate("""() => {
            isAddActivationActive = true;
            activationOrigin = {cx: 50, name: 'Bob', startY: 40};
            activationEndY = 90;
            cancelActivationAddMode();
            return {
                active: isAddActivationActive,
                origin: activationOrigin,
                endY: activationEndY
            };
        }""")
        assert result["active"] is False
        assert result["origin"] is None
        assert result["endY"] is None

    def test_escape_cancels_activation_mode(self, app_url, page):
        """Pressing Escape cancels activation-add mode."""
        result = page.evaluate("""() => {
            sequenceEventListeners();
            isAddActivationActive = true;
            activationOrigin = {cx: 50, name: 'Bob', startY: 40};
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

        page.evaluate("""() => {
            const bob = participantLifelines[1];
            activationOrigin = {cx: bob.cx, name: bob.name, startY: bob.yTop + 5};
            activationEndY = bob.yBottom - 5;
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
            activationOrigin = {cx: bob.cx, name: bob.name, startY: bob.yTop + 5};
            activationEndY = bob.yBottom - 5;
            submitActivation('destroy');
        }""")
        page.wait_for_timeout(5000)

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert "activate Bob" in lines
        assert "destroy Bob" in lines
