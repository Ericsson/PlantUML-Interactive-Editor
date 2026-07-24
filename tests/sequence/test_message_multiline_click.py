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

"""Regression tests for clicking multi-line message text and unmatched elements.

A multi-line message (``A -> B: line1\\nline2``) renders its text as several
<text> elements. Clicking any line must resolve to that message. A truly
unmatched element must be a safe no-op, never a silent wrong-message edit/delete
(the old code indexed ``messages[idx - 1]`` with ``idx == -1``, i.e.
``messages[-2]``, deleting an unrelated message).
"""

import re

from plantuml_gui.sequence.message import (
    delete_message,
    edit_message_text,
    get_message_text,
    index_of_clicked_message,
)
from plantuml_gui.shared.render import _create_svg_from_uml
from pyquery import PyQuery as Pq

# m2 has multi-line text; several messages follow so messages[-2] is a distinct,
# recognizable line (the old bug deleted this one for any unmatched element).
PUML = """@startuml
participant Alice
participant Bob
participant Server
Alice -> Bob: first
Bob -> Server: line one\\nline two\\nline three
Server -> Alice: third
Alice -> Bob: fourth
Alice -> Bob: WRONG_TARGET
Alice -> Alice: last
@enduml"""


def _inner(puml):
    svg = _create_svg_from_uml(puml)
    return re.search(r"<g>(.*)</g>", svg, re.DOTALL).group(1)


def _text_element(inner, contains):
    for t in Pq(inner)("text").items():
        if contains in (t.text() or ""):
            return str(t)
    return None


def test_clicking_second_line_resolves_to_its_message():
    inner = _inner(PUML)
    second_line = _text_element(inner, "line two")
    third_line = _text_element(inner, "line three")
    assert second_line and third_line

    # Both continuation lines resolve to message #2 (same as the first line).
    assert index_of_clicked_message(inner, second_line) == 2
    assert index_of_clicked_message(inner, third_line) == 2


def test_delete_via_continuation_line_removes_that_message():
    inner = _inner(PUML)
    second_line = _text_element(inner, "line two")
    result = delete_message(PUML, inner, second_line)

    # The clicked message is removed; the old bug removed WRONG_TARGET instead.
    assert "line one" not in result
    assert "WRONG_TARGET" in result


def test_edit_via_continuation_line_edits_that_message():
    inner = _inner(PUML)
    second_line = _text_element(inner, "line two")
    result = edit_message_text(PUML, inner, second_line, "EDITED")

    lines = result.splitlines()
    edited = [ln for ln in lines if "EDITED" in ln]
    assert edited and edited[0].startswith("Bob -> Server:")
    assert "WRONG_TARGET" in result  # untouched


def test_unmatched_element_is_a_safe_noop():
    inner = _inner(PUML)
    # A participant header rect is never a message; it must not match anything.
    foreign = "<rect x='0' y='0' width='1' height='1' />"
    assert index_of_clicked_message(inner, foreign) == -1
    assert delete_message(PUML, inner, foreign) == PUML
    assert edit_message_text(PUML, inner, foreign, "X") == PUML
    assert get_message_text(PUML, inner, foreign) == ""
