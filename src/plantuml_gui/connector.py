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

import re

from plantuml_gui.util import index_of_clicked_element  # pragma: no cover
from pyquery import PyQuery as Pq

from .classes import Ellipse, SvgChunk


def svgtochunklistconnector(svg):
    chunks = []
    d = Pq(svg)

    ellipses = d("ellipse")
    for ellipse in ellipses:
        ellipse = Pq(
            ellipse
        )  # ellipse svg is self closing, so no </ellipse> is in this.
        ellipse_svg = str(ellipse)
        ellipse_svg = ellipse_svg[:-2] + "></ellipse>"
        ellipse_obj = Ellipse.from_svg(ellipse_svg)

        next_elem = ellipse.next()
        if (
            next_elem
            and next_elem[0].tag == "path"
            and next_elem[0].get("fill") == "#000000"
        ):
            chunks.append(SvgChunk(object=ellipse_obj, text_elements=[]))
    return chunks


def delete_connector(puml, svgchunklist, clickedelement):
    start, end = get_index_connector(puml, svgchunklist, clickedelement, "below")
    lines = puml.splitlines()
    del lines[start : end + 1]
    return "\n".join(lines)


def get_index_connector(puml, svgchunklist, clickedelement, where) -> tuple[int, int]:
    index = 0
    count = index_of_clicked_element(svgchunklist, clickedelement)
    lines = puml.splitlines()
    for index, line in enumerate(lines):
        clean_line = line.strip()
        if clean_line.startswith("(") or (
            clean_line.startswith("#") and clean_line.endswith(")")
        ):
            count -= 1
        if count == 0:
            if clean_line.startswith("(") or (
                clean_line.startswith("#") and clean_line.endswith(")")
            ):
                start = index
                if where == "below":
                    if lines[index + 1].startswith("note"):
                        while lines[index] != "end note":
                            index += 1
                    if lines[index + 1] == "detach":
                        index += 1
                    break
    end = index
    return start, end


def find_index_connector(puml, svgchunklist, clickedelement):
    index = 0
    count = index_of_clicked_element(svgchunklist, clickedelement)
    lines = puml.splitlines()
    while index < len(lines):
        line = lines[index]
        clean_line = line.strip()
        if clean_line.startswith("(") or (
            clean_line.startswith("#") and clean_line.endswith(")")
        ):
            count -= 1
        if count == 0:
            if clean_line.startswith("(") or (
                clean_line.startswith("#") and clean_line.endswith(")")
            ):
                return index + 1
        index += 1


def detach_connector(puml, svgchunklist, clickedelement):
    start, end = get_index_connector(puml, svgchunklist, clickedelement, "below")
    lines = puml.splitlines()
    if lines[end].strip().startswith("detach"):
        del lines[end]
    else:
        lines.insert(end + 1, "detach")
    return "\n".join(lines)


def get_connector_char(puml, svgchunklist, clickedelement) -> str:
    lines = puml.splitlines()
    index = find_index_connector(puml, svgchunklist, clickedelement)
    matching_text = ""
    if match := re.search(r"\((.)\)", lines[index - 1]):
        matching_text = match.group(1)
    return matching_text


def edit_connector_char(puml, svgchunklist, clickedelement, text):
    lines = puml.splitlines()
    index = find_index_connector(puml, svgchunklist, clickedelement)
    lines[index - 1] = re.sub(r"\((.*?)\)", f"({text})", lines[index - 1])
    return "\n".join(lines)
