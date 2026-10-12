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

"""ARROW_RE: what it matches, and that it stays linear on hostile input."""

import time

import pytest
from plantuml_gui.sequence.classes import ARROW_RE


class TestArrowRegex:
    @pytest.mark.parametrize(
        ("head", "arrow"),
        [
            ("A -> B", "->"),
            ("A ->> B", "->>"),
            ("A --> B", "-->"),
            ("A <- B", "<-"),
            ("A <-> B", "<->"),
            ("A -[#red]> B", "-[#red]>"),
            ("A -[#red]-> B", "-[#red]->"),
            ("A <-[#blue]- B", "<-[#blue]-"),
            ("A -x B", "-x"),
            ("A -o B", "-o"),
        ],
    )
    def test_matches_the_arrow(self, head, arrow):
        match = ARROW_RE.search(head)
        assert match is not None
        assert match.group(0) == arrow

    @pytest.mark.parametrize("head", ["Web-Server", "A B", "-", "---", ""])
    def test_does_not_match_a_non_arrow(self, head):
        assert ARROW_RE.search(head) is None

    @pytest.mark.parametrize(
        "hostile",
        [
            "-" * 20000,
            "-" + "--" * 20000,
            "-[#" * 20000,
            "<-[#" * 20000,
            "-[#" * 20000 + "-",
        ],
        ids=[
            "dashes",
            "double-dashes",
            "dash-color",
            "reverse-dash-color",
            "dash-color-tail",
        ],
    )
    def test_hostile_input_is_matched_in_linear_time(self, hostile):
        """Regression (CodeQL py/polynomial-redos): a run of dashes without an
        arrow head used to be retried from every start position and split
        between two adjacent dash classes, so the work grew cubically (~2.5s at
        800 characters). The bound is loose for a slow machine yet far below
        what the old pattern needed at this size.
        """
        start = time.perf_counter()
        ARROW_RE.search(hostile)
        elapsed = time.perf_counter() - start

        assert elapsed < 0.5
