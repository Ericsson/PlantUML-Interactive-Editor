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

"""Errors raised by sequence-diagram edits that are safe to show the user.

The routes report these to the browser. Returning ``str(error)`` would send
whatever text the exception carries, so instead each error has a *code* and the
route looks the message up in :data:`USER_MESSAGES`, a table of fixed strings.
Nothing taken from the request or from the exception itself can reach the
response (CodeQL ``py/stack-trace-exposure``).
"""

USER_MESSAGES = {
    "invalid_group_type": ("Invalid group type. Must be one of: group, alt, opt, loop"),
    "box_crosses_box": ("Box overlaps an existing box. Boxes may nest but not cross."),
    "box_participant_undeclared": (
        "A participant can only be put in a box if it is declared on its "
        'own line. Add a "participant" line for it first.'
    ),
}

GENERIC_MESSAGE = "The request could not be applied."


class EditError(ValueError):
    """An edit that cannot be applied, identified by a ``USER_MESSAGES`` code.

    Subclasses ``ValueError`` so callers (and tests) that catch ``ValueError``
    keep working; ``str(error)`` is the same fixed message the route reports.
    """

    def __init__(self, code: str) -> None:
        super().__init__(USER_MESSAGES[code])
        self.code = code


def user_message(error: Exception) -> str:
    """Return the fixed, user-facing message for ``error``.

    Any exception that is not an :class:`EditError` gets a generic message.
    """
    if isinstance(error, EditError):
        return USER_MESSAGES.get(error.code, GENERIC_MESSAGE)
    return GENERIC_MESSAGE
