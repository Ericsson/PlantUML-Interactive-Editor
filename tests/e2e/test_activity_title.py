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

"""E2E tests for double-click title editing in activity diagrams.

Shares the title implementation (title.js) with sequence diagrams. This guards
the activity side against renderer-version drift: newer PlantUML renders the
title as bold font-size-14 <text> (no bounding rect), while older PlantUML wraps
it in an invisible #00000000 <rect>; setupTitleHandler handles both.
"""

_PUML = (
    "@startuml\\ntitle\\nMy Activity Title\\nendtitle\\n"
    "start\\n:Activity;\\nstop\\n@enduml"
)


def _load_activity_with_title(page, retries=12, wait_ms=2500):
    """Load a titled activity diagram, retrying until it renders stably.

    Detects the title the same way title.js does: bold font-size-14 <text>
    (newer PlantUML) or the invisible #00000000 bounding <rect> (older)."""
    for _ in range(retries):
        page.evaluate(f"() => editor.session.setValue('{_PUML}')")
        page.wait_for_timeout(wait_ms)
        ready = page.evaluate(
            """() => {
                if (!editor.session.getValue().includes('My Activity Title')) {
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
    raise AssertionError("titled activity diagram never rendered")


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


class TestActivityTitleDoubleClick:
    def test_double_click_title_opens_modal_prefilled(self, app_url, page):
        _load_activity_with_title(page)

        x, y = _title_center(page)
        page.mouse.dblclick(x, y)

        page.wait_for_selector("#modalFormTitle.show", state="visible", timeout=15000)
        assert page.input_value("#title-text") == "My Activity Title"

    def test_double_click_title_edit_updates_puml(self, app_url, page):
        _load_activity_with_title(page)

        x, y = _title_center(page)
        page.mouse.dblclick(x, y)
        page.wait_for_selector("#modalFormTitle.show", state="visible", timeout=15000)

        page.fill("#title-text", "Renamed Activity Title")
        page.click("#submit-title")
        page.wait_for_function(
            "() => editor.session.getValue().includes('Renamed Activity Title')",
            timeout=15000,
        )

        lines = page.evaluate(
            "() => editor.session.getValue().split('\\n').map(l => l.trim())"
        )
        assert "Renamed Activity Title" in lines
        assert "My Activity Title" not in lines
