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
