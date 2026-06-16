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

from pyquery import PyQuery as Pq  # pragma: no cover


def group_count(svg, clickedelement):
    count = 0
    d = Pq(svg)

    paths = d("path")
    for path in paths:
        path = Pq(path)
        path_svg = str(path)
        path_svg = path_svg[:-2] + "></path>"
        if path[0].get("style") == "stroke:#000000;stroke-width:1.5;":
            count += 1
            if path_svg == clickedelement:
                break
    return count


def find_group_bounds(lines, count):
    group_start, group_end = -1, -1
    index = 0
    inside_group = False
    level = 0

    while index < len(lines):
        line = lines[index]
        clean_line = line.strip()

        if clean_line.startswith("group") or clean_line.startswith("partition"):
            if count == 1:
                group_start = index
                inside_group = True
                count -= 1
                index += 1
                continue
            count -= 1
        if (
            inside_group
            and clean_line.startswith("group")
            or clean_line.startswith("partition")
        ):
            level += 1
        if inside_group and clean_line == "end group" or clean_line == "}":
            if level == 0:
                group_end = index
                break
            level -= 1
        index += 1
    return group_start, group_end


def get_group_text(puml, svg, clickedelement: Literal["group", "partition"]) -> str:
    lines = puml.splitlines()
    count = group_count(svg, clickedelement)
    group_start, _ = find_group_bounds(lines, count)
    group_line = lines[group_start]
    if group_line.startswith("group"):
        return group_line.split(" ", 1)[1]
    else:  # partition
        return group_line.split("partition", 1)[1].split("{", 1)[0].strip()


def edit_group(puml, svg, clickedelement, text):
    lines = puml.splitlines()
    count = group_count(svg, clickedelement)
    group_start, group_end = find_group_bounds(lines, count)
    if text == "":
        del lines[group_start]
        del lines[group_end - 1]
    else:
        if lines[group_start].startswith("group"):
            lines[group_start] = f"group {text}"
        else:
            lines[group_start] = f"partition {text} {{"
    return "\n".join(lines)


def delete_group(puml, svg, clickedelement):
    lines = puml.splitlines()
    count = group_count(svg, clickedelement)
    group_start, group_end = find_group_bounds(lines, count)
    del lines[group_start]
    del lines[group_end - 1]
    return "\n".join(lines)


def get_group_line(puml, svg, clickedelement):
    lines = puml.splitlines()
    count = group_count(svg, clickedelement)
    group_start, group_end = find_group_bounds(lines, count)
    return group_start, group_end
