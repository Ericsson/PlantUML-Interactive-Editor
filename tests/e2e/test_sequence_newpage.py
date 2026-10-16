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

"""Multi-page (newpage) sequence diagrams: page navigation and paged editing."""

import json

from playwright.sync_api import expect

THREE_PAGES = """@startuml
participant Alice
participant Bob
Alice -> Bob: p1m1
newpage Second
Alice -> Bob: p2m1
Bob -> Alice: p2m2
newpage
Alice -> Bob: p3m1
@enduml"""

SINGLE_PAGE = "@startuml\nAlice -> Bob: only\n@enduml"


def _load(page, puml):
    page.evaluate(f"setPuml({json.dumps(puml)})")


def _diagram_text(page):
    return page.locator("#colb svg")


class TestPageNavigation:
    def test_hidden_for_single_page_diagram(self, app_url, page):
        _load(page, SINGLE_PAGE)
        expect(_diagram_text(page)).to_contain_text("only")
        expect(page.locator("#page-nav")).to_be_hidden()

    def test_prev_next_walk_the_pages(self, app_url, page):
        _load(page, THREE_PAGES)
        expect(page.locator("#page-indicator")).to_have_text("Page 1 / 3")
        expect(page.locator("#page-nav")).to_be_visible()
        expect(page.locator("#page-prev")).to_be_disabled()
        expect(_diagram_text(page)).to_contain_text("p1m1")

        page.click("#page-next")
        expect(page.locator("#page-indicator")).to_have_text("Page 2 / 3")
        expect(_diagram_text(page)).to_contain_text("p2m1")
        expect(_diagram_text(page)).not_to_contain_text("p1m1")

        page.click("#page-next")
        expect(page.locator("#page-indicator")).to_have_text("Page 3 / 3")
        expect(page.locator("#page-next")).to_be_disabled()
        expect(_diagram_text(page)).to_contain_text("p3m1")

        page.click("#page-prev")
        expect(page.locator("#page-indicator")).to_have_text("Page 2 / 3")

    def test_removing_pages_clamps_the_current_page(self, app_url, page):
        _load(page, THREE_PAGES)
        page.click("#page-next")
        page.click("#page-next")
        expect(page.locator("#page-indicator")).to_have_text("Page 3 / 3")
        _load(page, THREE_PAGES.replace("newpage\n", ""))
        expect(page.locator("#page-indicator")).to_have_text("Page 2 / 2")

    def test_new_diagram_starts_on_page_one(self, app_url, page):
        _load(page, THREE_PAGES)
        page.click("#page-next")
        expect(page.locator("#page-indicator")).to_have_text("Page 2 / 3")
        page.evaluate("document.getElementById('clear').click()")
        expect(page.locator("#page-nav")).to_be_hidden()
        assert page.evaluate("currentPage") == 0


class TestEditingOnLaterPages:
    def test_edit_message_on_page_two_changes_its_line(self, app_url, page):
        _load(page, THREE_PAGES)
        page.click("#page-next")
        expect(_diagram_text(page)).to_contain_text("p2m2")

        page.locator("#colb text", has_text="p2m2").click(button="right")
        expect(page.locator("#message-menu")).to_be_visible()
        page.click("#editMessage")
        expect(page.locator("#participant-message-text")).to_have_value("p2m2")
        page.fill("#participant-message-text", "edited")
        page.click("#submit-participant-message")

        expect(_diagram_text(page)).to_contain_text("edited")
        lines = page.evaluate("editor.session.getValue()").splitlines()
        assert lines[6] == "Bob -> Alice: edited"
        assert lines[3] == "Alice -> Bob: p1m1"
        expect(page.locator("#page-indicator")).to_have_text("Page 2 / 3")

    def test_requests_carry_the_current_page(self, app_url, page):
        _load(page, THREE_PAGES)
        page.click("#page-next")
        with page.expect_request("**/getSequencePositions") as request:
            page.click("#page-next")
        assert request.value.post_data_json["page"] == 2


class TestCursorSync:
    def test_cursor_on_another_page_switches_to_it(self, app_url, page):
        _load(page, THREE_PAGES)
        expect(page.locator("#page-indicator")).to_have_text("Page 1 / 3")
        page.evaluate("editor.gotoLine(9, 0)")  # Alice -> Bob: p3m1
        expect(page.locator("#page-indicator")).to_have_text("Page 3 / 3")
        expect(_diagram_text(page)).to_contain_text("p3m1")

    def test_diagram_edit_does_not_jump_back_to_page_one(self, app_url, page):
        _load(page, THREE_PAGES)
        page.click("#page-next")
        expect(page.locator("#page-indicator")).to_have_text("Page 2 / 3")
        # setPuml moves Ace's cursor to row 0 on page 1; that is not navigation.
        _load(page, THREE_PAGES.replace("p2m1", "p2m1x"))
        expect(_diagram_text(page)).to_contain_text("p2m1x")
        expect(page.locator("#page-indicator")).to_have_text("Page 2 / 3")


class TestPngDownload:
    def test_png_requests_the_page_on_screen(self, app_url, page):
        _load(page, THREE_PAGES)
        page.click("#page-next")
        expect(page.locator("#page-indicator")).to_have_text("Page 2 / 3")
        with (
            page.expect_download() as download,
            page.expect_request("**/renderPNG") as request,
        ):
            page.click("#png")
        assert request.value.post_data_json["page"] == 1
        assert download.value.suggested_filename == "diagram-page-2.png"
