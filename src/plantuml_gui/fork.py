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

from pyquery import PyQuery as Pq  # pragma: no cover

from .classes import RectElement, SvgChunk


def svgtochunklistfork(svg: str) -> list[SvgChunk]:
    chunks = []
    d = Pq(svg)

    rects = d("rect")
    for rect in rects:
        if float(rect.get("height")) == 6:
            rect = Pq(rect)
            rect_svg = str(rect)
            rect_svg = rect_svg[:-2] + "></rect>"
            rect_obj = RectElement.from_svg(rect_svg)
            chunks.append(SvgChunk(object=rect_obj, text_elements=[]))
    return chunks


def findforkbounds(lines, count):
    start_fork = -1
    end_fork = -1
    index = 0
    level = 0
    inside_fork = False

    while index < len(lines):
        line = lines[index]
        clean_line = line.strip()

        if clean_line == "fork":
            if count == 1 and not inside_fork:
                start_fork = index
                inside_fork = True
                continue
            count -= 1
        if inside_fork and clean_line == "fork":
            level += 1
        if (
            clean_line == "end fork" or clean_line == "end merge"
        ):  # fork can end in both
            if inside_fork:
                level -= 1
                if level == 0:
                    end_fork = index
                    break
            if (
                clean_line == "end fork"
            ):  # if its an end merge there wasnt an extra count due to the rect.
                count -= 1
        index += 1
    return start_fork, end_fork


def forkcount(svgchunklist: list[SvgChunk], clickedelement: RectElement):
    count = 0
    for svgchunk in svgchunklist:  # counts occurances of poly chunks (if statements)
        count += 1
        if svgchunk.object == clickedelement:
            print("found clicked fork")
            break
    return count


# def add_note_fork(puml: str, svgchunklist: list[SvgChunk], clickedelement: RectElement):
#     count = forkcount(svgchunklist, clickedelement)
#     lines = puml.splitlines()

#     start_fork, end_fork = findforkbounds(lines, count)

#     lines.insert(end_fork + 1, "end note")
#     lines.insert(end_fork + 1, "note")
#     lines.insert(end_fork + 1, "note right")
#     return "\n".join(lines)


def deletefork(puml: str, svgchunklist: list[SvgChunk], clickedelement: RectElement):
    count = forkcount(svgchunklist, clickedelement)
    lines = puml.splitlines()

    start_fork, end_fork = findforkbounds(lines, count)
    del lines[start_fork : end_fork + 1]
    return "\n".join(lines)


def fork_again(puml: str, svgchunklist: list[SvgChunk], clickedelement: RectElement):
    count = forkcount(svgchunklist, clickedelement)
    lines = puml.splitlines()

    start_fork, end_fork = findforkbounds(lines, count)
    lines.insert(end_fork, "  :action;")
    lines.insert(end_fork, "fork again")
    return "\n".join(lines)


def fork_toggle(puml: str, svgchunklist: list[SvgChunk], clickedelement: RectElement):
    count = forkcount(svgchunklist, clickedelement)
    lines = puml.splitlines()

    start_fork, end_fork = findforkbounds(lines, count)
    if lines[end_fork].strip() == "end fork":
        lines[end_fork] = "end merge"
    else:
        lines[end_fork] = "end fork"
    return "\n".join(lines)


def fork_toggle2(puml, index):
    lines = puml.splitlines()
    if lines[index].strip() == "end fork":
        lines[index] = "end merge"
    return "\n".join(lines)


def delete_fork2(puml, index):
    end = index
    start = -1
    i = index - 1
    level = 0
    lines = puml.splitlines()

    while i > 0:
        line = lines[i].strip()
        if line == "fork":
            if level == 0:
                start = i
                break
            else:
                level -= 1
        if line in ["end merge", "end fork"]:
            level += 1
        i -= 1

    del lines[start : end + 1]
    return "\n".join(lines)
