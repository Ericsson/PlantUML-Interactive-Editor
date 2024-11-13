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

from plantuml_gui.classes import PolyElement, SvgChunk


def index_of_clicked_element(svgchunklist: list[SvgChunk], clickedelement) -> int:
    count = 0
    for svgchunk in svgchunklist:
        count += 1
        if svgchunk.object == clickedelement:
            break
    return count


def checkifwhile(svgchunk: SvgChunk):
    if len(svgchunk.text_elements) < 3 or type(svgchunk.object) != PolyElement:
        return False
    points = svgchunk.object.points.split(",")
    y_values = []
    x_values = []
    text_y_value = svgchunk.text_elements[0].y
    text_x_value = svgchunk.text_elements[2].x

    for i in range(1, len(points), 2):
        y_values.append(float(points[i]))
    for y in y_values:
        if y > text_y_value:
            return False

    for i in range(0, len(points), 2):
        x_values.append(float(points[i]))
    for x in x_values:
        if x < text_x_value:
            return False

    return True
