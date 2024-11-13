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


from plantuml_gui.util import index_of_clicked_element  # pragma: no cover
from pyquery import PyQuery as Pq

from .classes import Ellipse, SvgChunk


def svgtochunklistellipse(svg):
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
            next_elem and next_elem[0].tag == "ellipse"
        ):  # this part is done because the "end" element has two ellipses and we only want to count one of
            next_elem = Pq(next_elem)
            next_elem_svg = str(next_elem)
            next_elem_svg = next_elem_svg[:-2] + "></ellipse>"
            next_elem_obj = Ellipse.from_svg(next_elem_svg)
            if next_elem_obj == ellipse_obj:
                continue
        if (
            next_elem
            and next_elem[0].tag == "path"
            and next_elem[0].get("fill") == "#000000"
        ):
            continue
        chunks.append(SvgChunk(object=ellipse_obj, text_elements=[]))
    return chunks


def delete_ellipse_element(puml, svgchunklist, clickedelement):
    index = 0
    count = index_of_clicked_element(svgchunklist, clickedelement)
    lines = puml.splitlines()
    while index < len(lines):
        line = lines[index]
        clean_line = line.strip()
        if not lines[index - 1].startswith("note"):
            if clean_line.startswith(("stop", "start", "end")):
                count -= 1
            if count == 0:
                if clean_line.startswith(("stop", "start", "end")):
                    del lines[index]
                    break
        index += 1
    return "\n".join(lines)


def get_index_ellipse(puml, svgchunklist, clickedelement, where) -> int:
    index = 0
    count = index_of_clicked_element(svgchunklist, clickedelement)
    lines = puml.splitlines()
    for index, line in enumerate(lines):
        clean_line = line.strip()
        if not lines[index - 1].startswith("note"):
            if clean_line in ["stop", "start", "end"]:
                count -= 1
            if count == 0:
                if clean_line in ["stop", "start", "end"]:
                    break
    return index + 1
