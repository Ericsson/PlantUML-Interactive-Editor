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

from pyquery import PyQuery as Pq  # pragma: no cover


def svgtoarrowtext(svg, clickedelement):  # works for arrows and switch condition text
    text = []
    d = Pq(svg)

    polys = d("polygon")
    for poly in polys:
        poly = Pq(poly)
        poly_svg = str(poly)
        poly_svg = poly_svg[:-2] + "></polygon>"
        if poly_svg == clickedelement:
            next_elem = poly.next()
            while next_elem and next_elem[0].tag == "text":
                text.append(next_elem.text())
                next_elem = next_elem.next()
    return "\n".join(text)


def check_for_duplicate_arrow(puml, svg, clickedelement):
    numbers = []
    arrow_text = svgtoarrowtext(svg, clickedelement)
    lines = puml.splitlines()
    start, end = -1, -1
    for index, line in enumerate(lines):
        start, end = -1, -1
        clean_line = line.strip()

        if clean_line.startswith("case"):  # condition text
            start, end = index, index
            condition_text = re.search(r"\(([^)]+)\)", lines[index]).group(1).strip()
            if condition_text.replace("\\n", "\n") == arrow_text.replace("\\n", "\n"):
                numbers.append(start)

        elif clean_line.startswith("-"):
            start = index
            while not lines[index].strip().endswith(";"):
                index += 1
            end = index

            arrow_lines = lines[start : end + 1]
            stripped_arrow_lines = []
            for line in arrow_lines:
                stripped_arrow_lines.append(line.strip())
            puml_arrow_text = "\n".join(stripped_arrow_lines)
            cleaned_text = puml_arrow_text.strip()
            pattern = r"^.*?>\s*"
            cleaned_text = re.sub(pattern, "", cleaned_text)
            cleaned_text = cleaned_text[:-1]
            if cleaned_text.replace("\\n", "\n") == arrow_text.replace("\\n", "\n"):
                numbers.append(start)
    return len(numbers) > 1


def find_arrow_bounds(puml, svg, clickedelement) -> tuple[int, int]:
    arrow_text = svgtoarrowtext(svg, clickedelement)
    lines = puml.splitlines()
    start, end = -1, -1
    for index, line in enumerate(lines):
        start, end = -1, -1
        clean_line = line.strip()

        if clean_line.startswith("case"):  # condition text
            start, end = index, index
            match = re.search(r"\(([^)]+)\)", lines[index])
            if match:
                condition_text = match.group(1).strip()
            if condition_text.replace("\\n", "\n") == arrow_text.replace("\\n", "\n"):
                break

        elif clean_line.startswith("-"):
            start = index
            while not lines[index].strip().endswith(";"):
                index += 1
            end = index

            arrow_lines = lines[start : end + 1]
            stripped_arrow_lines = []
            for line in arrow_lines:
                stripped_arrow_lines.append(line.strip())
            puml_arrow_text = "\n".join(stripped_arrow_lines)
            cleaned_text = puml_arrow_text.strip()
            pattern = r"^.*?>\s*"
            cleaned_text = re.sub(pattern, "", cleaned_text)
            cleaned_text = cleaned_text[:-1]
            if cleaned_text.replace("\\n", "\n") == arrow_text.replace("\\n", "\n"):
                break
    return start, end


def get_arrow_line(puml, svg, clickedelement):
    start, end = find_arrow_bounds(puml, svg, clickedelement)
    return start, end


def get_arrow_type(puml, svg, clickedelement):
    lines = puml.splitlines()
    start, end = find_arrow_bounds(puml, svg, clickedelement)
    if lines[start].strip().startswith("case"):
        return "case"
    else:
        return "arrow"


def edit_arrow(puml, svg, text, clickedelement):
    lines = puml.splitlines()
    start, end = find_arrow_bounds(puml, svg, clickedelement)
    arrow_lines = lines[start : end + 1]

    if lines[start].startswith("case"):
        arrow_text = "\n".join(arrow_lines)
        arrow_text = re.sub(r"\(([^)]+)\)", f"({text})", arrow_text, flags=re.DOTALL)
        lines[start] = arrow_text.replace(
            "\n", "\\n"
        )  # case condition is always on the same line in the editor

    else:
        arrow_text = "\n".join(arrow_lines)
        arrow_text = re.sub(r">(.*?)\;", f">{text};", arrow_text, flags=re.DOTALL)

        arrow_lines = arrow_text.splitlines()
        lines[start : end + 1] = arrow_lines

    return "\n".join(lines)


def delete_arrow(puml, svg, clickedelement):
    start, end = find_arrow_bounds(puml, svg, clickedelement)
    lines = puml.splitlines()

    if lines[start].startswith("case"):
        index = start
        level = 0
        while index < len(lines) - 1:
            if lines[index + 1].strip().startswith("switch"):
                level += 1
            if level == 0:
                if (
                    lines[index + 1].strip().startswith("case")
                    or lines[index + 1].strip() == "endswitch"
                ):
                    end = index
                    break
            else:
                if lines[index + 1].strip() == "endswitch":
                    level -= 1
            index += 1

    del lines[start : end + 1]
    return "\n".join(lines)
