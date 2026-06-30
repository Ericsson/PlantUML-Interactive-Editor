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

"""Activation bar logic for sequence diagrams.

A single user gesture creates one balanced activation bar for one participant:
an ``activate <P>`` line before the message at ``start_index`` and a closing
``deactivate <P>`` or ``destroy <P>`` line after the message at ``end_index``.
Because the gesture always starts by activating and inserts a matched pair, a
participant can never be deactivated without first being activated.
"""


def add_activation(
    puml: str,
    participant_name: str,
    start_index: int,
    end_index: int,
    end_type: str,
) -> str:
    """Insert a matched activate + close pair for a participant by line index.

    ``start_index`` and ``end_index`` are the puml line numbers of the messages
    nearest to where the user started and ended the gesture. The ``activate``
    line is inserted just *after* the start message and the closing line just
    *after* the end message, so both anchor below their nearest message. The bar
    therefore covers the messages following the start message up to and
    including the end message. ``end_type`` is ``"destroy"`` to end the lifeline
    with an X, otherwise the bar is closed with ``deactivate``.

    The closing line is inserted first (it sits at a greater-or-equal line
    index), then the ``activate`` line, so the start insertion index stays valid.
    """
    keyword = "destroy" if end_type == "destroy" else "deactivate"

    lines = puml.splitlines()

    # Insert the closing line after the end message, then the opening line after
    # the start message. Inserting the (lower) end line first keeps the start
    # insertion index valid.
    lines.insert(end_index + 1, f"{keyword} {participant_name}")
    lines.insert(start_index + 1, f"activate {participant_name}")
    return "\n".join(lines)
