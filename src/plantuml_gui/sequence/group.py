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

"""Group block logic for sequence diagrams.

Supports the keywords ``group``, ``alt``, ``opt``, and ``loop``.  A group
wraps a range of messages (identified by their puml line indexes) in a
``<keyword> <label> ... end`` block.
"""

VALID_GROUP_TYPES = ("group", "alt", "opt", "loop")


def add_group(
    puml: str,
    group_type: str,
    label: str,
    start_message_index: int,
    end_message_index: int,
) -> str:
    """Insert a group block wrapping messages between two line indexes.

    ``start_message_index`` and ``end_message_index`` are puml line numbers of
    the bounding messages.  The range is normalized so the opening line is
    inserted before the earlier message and the closing ``end`` line is inserted
    after the later message.

    Raises ``ValueError`` if ``group_type`` is not one of the valid keywords.
    """
    if group_type not in VALID_GROUP_TYPES:
        raise ValueError(
            f"Invalid group type '{group_type}'. "
            f"Must be one of: {', '.join(VALID_GROUP_TYPES)}"
        )

    # Normalize so start <= end (user may have selected bottom-to-top)
    start = min(start_message_index, end_message_index)
    end = max(start_message_index, end_message_index)

    lines = puml.splitlines()

    # Insert end line after the end message, then the opening line before the
    # start message.  Inserting the later line first keeps the start index valid.
    lines.insert(end + 1, "end")
    lines.insert(start, f"{group_type} {label}")

    return "\n".join(lines)
