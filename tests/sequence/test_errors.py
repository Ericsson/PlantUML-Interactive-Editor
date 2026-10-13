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

"""Edit errors reach the browser as fixed messages, never as raw exception text."""

import json

import pytest
from plantuml_gui.sequence.errors import (
    GENERIC_MESSAGE,
    USER_MESSAGES,
    EditError,
    user_message,
)
from plantuml_gui.sequence.group import VALID_GROUP_TYPES


def test_every_code_has_a_message_and_round_trips():
    for code, message in USER_MESSAGES.items():
        error = EditError(code)
        assert isinstance(error, ValueError)
        assert str(error) == message
        assert user_message(error) == message


def test_group_type_message_lists_the_valid_types():
    message = USER_MESSAGES["invalid_group_type"]
    assert message.endswith(", ".join(VALID_GROUP_TYPES))


@pytest.mark.parametrize(
    "error", [ValueError("secret detail"), KeyError("x"), RuntimeError()]
)
def test_other_exceptions_get_the_generic_message(error):
    assert user_message(error) == GENERIC_MESSAGE


def test_group_route_does_not_echo_the_request_value(client):
    payload = {
        "plantuml": "@startuml\nA -> B: hi\n@enduml",
        "groupType": "<script>alert(1)</script>",
        "label": "x",
        "startMessageIndex": 1,
        "endMessageIndex": 1,
    }
    response = client.post(
        "/addGroup", data=json.dumps(payload), content_type="application/json"
    )
    assert response.status_code == 400
    error = response.get_json()["error"]
    assert error == USER_MESSAGES["invalid_group_type"]
    assert "script" not in error
