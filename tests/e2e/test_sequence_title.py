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

"""E2E tests for double-click title editing in sequence diagrams.

Parity with the activity diagram: the title is rendered as an invisible
bounding <rect> that setupTitleHandler makes double-clickable, opening the
shared #modalFormTitle. The getTextTitle/editTitle routes are diagram-agnostic
and the modal's submit handler is wired once via addUtilEventListeners, so this
verifies the whole path works while a sequence diagram is loaded.
"""

_PUML = (
    "@startuml\\ntitle\\nMy Sequence Title\\nendtitle\\n"
    "participant Alice\\nparticipant Bob\\nAlice -> Bob: hi\\n@enduml"
)


def _load_sequence_with_title(page, retries=12, wait_ms=2500):
    """Load a titled sequence diagram, retrying until it renders stably.

    Mirrors the render-race-tolerant load helpers used by the other sequence
    e2e tests: the page's initial demo render can complete late and clobber a
    single setValue, so re-set until both lifelines and the title rect exist."""
    for _ in range(retries):
        page.evaluate(f"() => editor.session.setValue('{_PUML}')")
        page.wait_for_timeout(wait_ms)
        ready = page.evaluate(
            """() => {
                if (!participantLifelines || participantLifelines.length !== 2) {
                    return false;
                }
                const svg = document.querySelector('#colb svg');
                if (!svg) return false;
                return Array.from(svg.querySelectorAll('rect')).some(
                    r => (r.getAttribute('style') || '').includes('#00000000')
                );
            }"""
        )
        if ready:
            return
    raise AssertionError("titled sequence diagram never rendered")


def _title_rect_center(page):
    """Screen coordinates of the title rect's center (or None)."""
    return page.evaluate(
        """() => {
            const svg = document.querySelector('#colb svg');
            const rect = Array.from(svg.querySelectorAll('rect')).find(
                r => (r.getAttribute('style') || '').includes('#00000000')
            );
            if (!rect) return null;
            const b = rect.getBoundingClientRect();
            return [b.x + b.width / 2, b.y + b.height / 2];
        }"""
    )


class TestSequenceTitleDoubleClick:
    def test_double_click_title_opens_modal_prefilled(self, app_url, page):
        _load_sequence_with_title(page)

        x, y = _title_rect_center(page)
        page.mouse.dblclick(x, y)

        page.wait_for_selector("#modalFormTitle.show", state="visible", timeout=15000)
        assert page.input_value("#title-text") == "My Sequence Title"

    def test_double_click_title_edit_updates_puml(self, app_url, page):
        _load_sequence_with_title(page)

        x, y = _title_rect_center(page)
        page.mouse.dblclick(x, y)
        page.wait_for_selector("#modalFormTitle.show", state="visible", timeout=15000)

        page.fill("#title-text", "Renamed Title")
        page.click("#submit-title")
        page.wait_for_function(
            "() => editor.session.getValue().includes('Renamed Title')",
            timeout=15000,
        )

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert "Renamed Title" in lines
        assert "My Sequence Title" not in lines
