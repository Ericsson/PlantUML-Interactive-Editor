# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2024 Ericsson
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


from typing import Literal


def add(
    puml: str,
    index: int,
    type: Literal[
        "activity",
        "connector",
        "if",
        "fork",
        "while",
        "start",
        "stop",
        "end",
        "note",
        "repeat",
        "switch",
    ],
):
    lines = puml.splitlines()

    if type == "activity":
        lines.insert(index, ":Activity;")

    if type == "connector":
        lines.insert(index, "(C)")

    if type == "if":
        if_lines = [
            "if (Statement) then (yes)",
            ":Activity;",
            "else (no)",
            ":Activity;",
            "endif",
        ]

        lines = lines[:index] + if_lines + lines[index:]

    if type == "fork":
        fork_lines = [
            "fork",
            ":action;",
            "fork again",
            ":action;",
            "end fork",
        ]

        lines = lines[:index] + fork_lines + lines[index:]

    if type == "while":
        while_lines = [
            "while (Statement) is (yes)",
            ":Activity;",
            "endwhile (no)",
            ":Activity;",
        ]

        lines = lines[:index] + while_lines + lines[index:]

    if type in ["start", "stop", "end"]:  # pragma: no cover
        lines.insert(index, type)

    if type == "note":
        lines.insert(index, "end note")
        lines.insert(index, "note")
        lines.insert(index, "note right")

    if type == "repeat":
        repeat_lines = [
            "repeat",
            ":Activity;",
            "backward:Activity;",
            "repeat while (while ?) is (yes) not (no)",
            ":Activity;",
        ]
        lines = lines[:index] + repeat_lines + lines[index:]

    if type == "switch":
        switch_lines = [
            "switch (test?)",
            "case ( condition 1)",
            ":Activity;",
            "case ( condition 2)",
            ":Activity;",
            "endswitch",
        ]
        lines = lines[:index] + switch_lines + lines[index:]

    return "\n".join(lines)
