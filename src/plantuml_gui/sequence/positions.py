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

"""Per-render element positions for every sequence diagram element type.

Powers editor<->diagram hover highlighting and the activation/group gestures:
one fetch per render returns the position table for every element type, so the
frontend makes a single round-trip instead of one per type. Unlike the activity
equivalent, the sub-tables keep their own geometry-carrying shapes (participants
carry lifeline bounds, messages/notes carry SVG Y-coordinates) because sequence
elements are matched to the SVG spatially rather than by ordinal - this is a
transport aggregation, not a data-model change, so each sub-table is exactly
what its own get_*_positions function already returned.
"""

from typing import Dict

from .box import get_box_positions
from .group import get_group_positions
from .message import get_message_positions
from .note import get_note_positions
from .participant import get_participant_positions


def get_sequence_positions(puml: str, svg: str) -> Dict[str, object]:
    """Return the per-render position table for every sequence element type."""
    return {
        "participants": get_participant_positions(puml, svg),
        "messages": get_message_positions(puml, svg),
        "notes": get_note_positions(puml, svg),
        "groups": get_group_positions(puml, svg),
        "boxes": get_box_positions(puml, svg),
    }
