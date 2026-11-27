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

"""Tests for the Help modal opened by the global bar's (?) button."""

import pytest


def _open_help(page):
    page.wait_for_timeout(2000)
    page.locator(".global-bar [data-tippy-content='Help']").click()
    modal = page.locator("#helpModal")
    modal.wait_for(state="visible", timeout=2000)
    return modal


def _wait_for_image_loaded(page, selector: str) -> None:
    """Wait until the <img> has finished loading a real image (raises on timeout)."""
    page.wait_for_function(
        "s => { const i = document.querySelector(s); return i.complete && i.naturalWidth > 0; }",
        arg=selector,
        timeout=5000,
    )


def test_help_button_opens_on_getting_started(app_url, page):
    """The modal opens on the Getting started tab, with both walkthroughs."""
    modal = _open_help(page)
    assert modal.locator("#help-tab-start").get_attribute("aria-selected") == "true"
    start = modal.locator("#help-start")
    assert start.is_visible()
    assert start.locator("text=Activity diagrams").is_visible()
    assert start.locator("text=Sequence diagrams").is_visible()


@pytest.mark.parametrize(
    "gif", ["static/help/activity-editing.gif", "static/help/sequence-editing.gif"]
)
def test_getting_started_gif_loads(app_url, page, gif):
    """Both walkthrough GIFs are served and load, with alt text."""
    _open_help(page)
    selector = f"#help-start img[src='{gif}']"
    img = page.locator(selector)
    img.scroll_into_view_if_needed()
    _wait_for_image_loaded(page, selector)
    assert img.get_attribute("alt")


@pytest.mark.parametrize(
    ("tab", "pane", "text"),
    [
        ("#help-tab-usage", "#help-usage", "Highlight its line in the editor"),
        ("#help-tab-resources", "#help-resources", "Sequence Diagram Documentation"),
    ],
)
def test_tabs_switch(app_url, page, tab, pane, text):
    """Each tab shows its own pane and hides Getting started."""
    modal = _open_help(page)
    modal.locator(tab).click()
    modal.locator(pane).wait_for(state="visible", timeout=2000)
    assert modal.locator(tab).get_attribute("aria-selected") == "true"
    assert modal.locator(pane).locator(f"text={text}").is_visible()
    assert not modal.locator("#help-start").is_visible()


def test_help_modal_closes(app_url, page):
    """The header's close button closes the modal."""
    modal = _open_help(page)
    modal.locator("button.close").click()
    modal.wait_for(state="hidden", timeout=2000)
