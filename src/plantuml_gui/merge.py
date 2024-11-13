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

from .classes import PolyElement


def get_index_merge(puml, svg, clickedelement):
    count = index_of_clicked_merge(svg, clickedelement)
    lines = puml.splitlines()
    return find_merge_index(lines, count)


def index_of_clicked_merge(svg, clickedelement):
    count = 0
    d = Pq(svg)

    polys = d("polygon")
    for poly in polys:
        poly = Pq(poly)
        poly_svg = str(poly)
        poly_svg = poly_svg[:-2] + "></polygon>"
        poly_obj = PolyElement.from_svg(poly_svg)
        if (
            poly[0].get("style") == "stroke:#181818;stroke-width:0.5;"
            and poly_obj.is_merge()
        ):
            count += 1
            if poly_svg == clickedelement:
                break
    return count


def find_merge_index(lines, count):
    merge_index = -1
    index = 0

    while index < len(lines):
        line = lines[index]
        clean_line = line.strip()

        if clean_line in {"endif", "end merge", "repeat", "endswitch"}:
            if clean_line == "endif":
                if not check_endif_merge(
                    lines, index
                ):  # checks if the endif merge exists or not, detach can make it dissapear.
                    index += 1
                    continue
            if count == 1:
                merge_index = index
                break
            count -= 1
        index += 1
    return merge_index


def check_endif_merge(lines, index):
    if (
        lines[index + 1].strip() == "detach"
        or lines[index - 1].strip() == "detach"
        or lines[index - 1].strip().startswith("else")
        or lines[index - 1].strip() in ["stop", "end"]
    ):  # checks for detach before and after endif line
        return False

    while (
        index > 0
    ):  # checks for endif before else statements and also works for nested ifs.
        level = 0
        if lines[index].strip().startswith("else") and level == 0:
            if lines[index - 1].strip() == "detach":
                return False
        if lines[index].strip() == "endif":
            level += 1
        if lines[index].startswith("if"):
            level -= 1

        index -= 1

    return True
