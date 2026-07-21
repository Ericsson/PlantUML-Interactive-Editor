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

from playwright.sync_api import TimeoutError as PlaywrightTimeoutError

_PUML = (
    "@startuml\\ntitle\\nMy Sequence Title\\nendtitle\\n"
    "participant Alice\\nparticipant Bob\\nAlice -> Bob: hi\\n@enduml"
)


def _load_sequence_with_title(page, retries=12, wait_ms=2500):
    """Load a titled sequence diagram, retrying until it renders stably.

    Mirrors the render-race-tolerant load helpers used by the other sequence
    e2e tests: the page's initial demo render can complete late and clobber a
    single setValue, so re-set until both lifelines and the title element exist.

    The title is detected the same way title.js does: newer PlantUML renders it
    as bold, font-size-14 <text>; older PlantUML wrapped it in an invisible
    #00000000 bounding <rect>."""
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
                const hasTitleText = Array.from(svg.querySelectorAll('text')).some(
                    t => t.getAttribute('font-size') === '14'
                        && t.getAttribute('font-weight') === 'bold'
                );
                const hasTitleRect = Array.from(svg.querySelectorAll('rect')).some(
                    r => (r.getAttribute('style') || '').includes('#00000000')
                );
                return hasTitleText || hasTitleRect;
            }"""
        )
        if ready:
            return
    raise AssertionError("titled sequence diagram never rendered")


def _title_center(page):
    """Screen coordinates of the title element's center (or None).

    Prefers the bold font-size-14 title text (newer PlantUML) and falls back to
    the #00000000 bounding rect (older PlantUML), matching title.js."""
    return page.evaluate(
        """() => {
            const svg = document.querySelector('#colb svg');
            const el = Array.from(svg.querySelectorAll('text')).find(
                t => t.getAttribute('font-size') === '14'
                    && t.getAttribute('font-weight') === 'bold'
            ) || Array.from(svg.querySelectorAll('rect')).find(
                r => (r.getAttribute('style') || '').includes('#00000000')
            );
            if (!el) return null;
            const b = el.getBoundingClientRect();
            return [b.x + b.width / 2, b.y + b.height / 2];
        }"""
    )


def _dblclick_title_until_modal(page, attempts=8):
    """Double-click the title, retrying until the edit modal opens.

    The diagram re-renders a few times right after load and the SVG handlers are
    (re)attached asynchronously after each render, so a single double-click can
    land in the gap between the SVG being swapped in and setupTitleHandler
    binding the dblclick / re-enabling pointer events on the title text.
    Recomputing the title center and retrying makes the gesture robust against
    that render race without hiding a genuine failure (the final attempt still
    raises)."""
    for attempt in range(attempts):
        center = _title_center(page)
        if center is not None:
            page.mouse.dblclick(center[0], center[1])
        try:
            page.wait_for_selector(
                "#modalFormTitle.show", state="visible", timeout=5000
            )
            return
        except PlaywrightTimeoutError:
            if attempt == attempts - 1:
                raise


class TestSequenceTitleDoubleClick:
    def test_double_click_title_opens_modal_prefilled(self, app_url, page):
        _load_sequence_with_title(page)

        _dblclick_title_until_modal(page)
        assert page.input_value("#title-text") == "My Sequence Title"

    def test_double_click_title_edit_updates_puml(self, app_url, page):
        _load_sequence_with_title(page)

        _dblclick_title_until_modal(page)

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
