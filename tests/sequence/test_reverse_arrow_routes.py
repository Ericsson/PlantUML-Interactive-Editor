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

"""Full-stack regression for the reported reverse-arrow bug.

Drives the real HTTP routes the frontend uses (``/render``,
``/getSequencePositions``, ``/deleteMessage``) with the user's exact teoz
diagram (nested boxes, ``...`` delay, colored reverse arrows). Confirms the
message->source-line mapping that hover highlighting and delete depend on is
correct end-to-end, so hovering/deleting ``SMF<-Access:CreateBearerResponse``
resolves to its own line rather than an unrelated one.

Deterministic on purpose: it uses the Flask test client and a single render,
avoiding the browser render-race flakiness a live_server probe would add, while
still exercising the full backend request path against real teoz-rendered SVG.
"""

import re

from pyquery import PyQuery as Pq

# The exact diagram from the bug report.
PUML = """@startuml
!pragma teoz true
skinparam maxMessageSize 500

box
box
participant Access
end box
participant SMF
participant PCF
end box
autonumber
SMF<-PCF:PcfEventNotificationPolicyUpdateRequest
SMF->PCF:PcfEventNotificationPolicyUpdateResponse [NoContent (204)]
SMF->Access:CreateBearerRequest
SMF<[#red]-PCF:  <font color=red>PcfEventNotificationPolicyUpdateRequest\\n<font color=red>(RuleUpdate/Rule Remove)
SMF-[#red]>PCF: <font color=red>PcfEventNotificationPolicyUpdateResponse [NoContent (204)]
SMF<-Access:CreateBearerResponse
SMF -> SMF: 123
SMF->PCF:PolicyUpdateRequest (SRA)
SMF<-PCF:PolicyUpdateResponse [NoContent (204)]

alt <size:12>a) Rule Update</size>
SMF-[#red]>Access:<font color=red>UpdateBearerRequest
SMF<[#red]-Access:<font color=red>UpdateBearerResponse
else <size:12>b) Rule Remove</size>
SMF --> Access: test
SMF-[#red]>Access:<font color=red>DeleteBearerRequest
SMF<[#red]-Access:<font color=red>DeleteBearerResponse
end
@enduml"""

# 0-based source-line index each of the 14 messages must map to, in order.
EXPECTED_MESSAGE_LINES = [12, 13, 14, 15, 16, 17, 18, 19, 20, 23, 24, 26, 27, 28]


def _render_inner(client):
    """Render PUML via /render and return the top-level <g> innerHTML."""
    resp = client.post("/render", json={"plantuml": PUML})
    svg = resp.data.decode("utf-8")
    return re.search(r"<g>(.*)</g>", svg, re.DOTALL).group(1)


def _nth_message_text_element(svg_inner, message_index):
    """Return the <text> outerHTML of the nth message group (0-based)."""
    elements = list(Pq(svg_inner)("*").items())
    i = 0
    count = 0
    while i < len(elements):
        group = elements[i : i + 5]
        tags = [el[0].tag for el in group]
        if tags[:4] == ["polygon", "polygon", "line", "text"]:
            step, text = 4, group[3]
        elif tags[:5] == ["line", "line", "line", "polygon", "text"]:
            step, text = 5, group[4]
        elif tags[:3] == ["polygon", "line", "text"]:
            step, text = 3, group[2]
        else:
            i += 1
            continue
        if count == message_index:
            return str(text)
        count += 1
        i += step
    return None


def test_positions_map_every_message_to_its_own_line(client):
    """/getSequencePositions returns a correct line index for every message."""
    inner = _render_inner(client)
    resp = client.post("/getSequencePositions", json={"plantuml": PUML, "svg": inner})
    messages = resp.get_json()["messages"]

    assert [m["index"] for m in messages] == EXPECTED_MESSAGE_LINES
    # The reported hover case: the 6th message (SMF<-Access:CreateBearerResponse,
    # 0-based index 5) maps to its own line, not the UpdateBearerRequest line it
    # used to resolve to.
    lines = PUML.splitlines()
    assert lines[messages[5]["index"]] == "SMF<-Access:CreateBearerResponse"


def test_delete_reverse_arrow_message_removes_its_own_line(client):
    """/deleteMessage on a reverse arrow removes that line, not a neighbor."""
    inner = _render_inner(client)
    # 6th message (0-based 5) is the reverse arrow SMF<-Access:CreateBearerResponse.
    element = _nth_message_text_element(inner, 5)
    resp = client.post(
        "/deleteMessage",
        json={"plantuml": PUML, "svg": inner, "svgelement": element},
    )
    result = resp.get_json()["plantuml"]

    assert "SMF<-Access:CreateBearerResponse" not in result
    # Neighbours and the diagram frame are untouched.
    assert "SMF -> SMF: 123" in result
    assert "@enduml" in result
    assert result.count("\n") == PUML.count("\n") - 1
