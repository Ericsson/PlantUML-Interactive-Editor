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

from .classes import RectElement, SvgChunk, TextElement


def index_of_clicked_activity(svg, clickedelement):
    count = 0
    d = Pq(svg)

    rects = d("rect")
    for rect in rects:
        if (
            float(rect.get("height")) > 6
            and rect.get("style") == "stroke:#181818;stroke-width:0.5;"
        ):  # check that the rect is an activity and not a fork bar
            rect = Pq(rect)  # rect svg is self closing, so no </rect> is in this.
            rect_svg = str(rect)
            rect_svg = rect_svg[:-2] + "></rect>"
            rect_obj = RectElement.from_svg(rect_svg)
            count += 1
            if rect_obj == clickedelement:
                break
    return count


def activity_indices(lines, i) -> list[int]:
    return _activity_indices(lines, i)[0]


def _activity_indices(lines, i) -> tuple[list[int], int]:
    index = i
    indices = []
    backward = -1

    while index < len(lines):
        line = lines[index]
        clean_line = line.strip()

        if (
            clean_line.startswith("#") and not clean_line.endswith(")")
        ) or clean_line.startswith(":"):
            indices.append(index)

        if clean_line.startswith("backward"):
            backward = index

        if clean_line == "repeat":
            rlist, index = _activity_indices(lines, index + 1)
            indices += rlist
        if clean_line.startswith("repeat while") or clean_line.startswith(
            "repeatwhile"
        ):
            indices.append(backward)
            return indices, index
        index += 1
    return indices, index


def find_activity_start(lines, count) -> int:
    indices = activity_indices(lines, 0)
    start = -1
    for index in indices:
        if count == 1:
            start = index
            break
        count -= 1
    return start


def find_activity_end(lines, start) -> int:
    index = start

    while index < len(lines):
        if lines[index].endswith(";"):
            end = index
            break

        index += 1

    return end


def find_text_bounds(lines, count):
    start = find_activity_start(lines, count)
    end = find_activity_end(lines, start)
    return start, end


def check_backward(puml, svg, clickedelement):
    lines = puml.splitlines()
    count = index_of_clicked_activity(svg, clickedelement)
    start = find_activity_start(lines, count)
    return lines[start].strip()


def edit_activity(puml, svg, clickedelement, text):
    lines = puml.splitlines()
    count = index_of_clicked_activity(svg, clickedelement)
    start = find_activity_start(lines, count)
    end = find_activity_end(lines, start)
    if text == "":
        return delete_activity(puml, svg, clickedelement)

    activity_lines = lines[start : end + 1]
    activity_text = "\n".join(activity_lines)
    activity_text = re.sub(r"(?<=:).*?(?=;)", text, activity_text, flags=re.DOTALL)

    activity_lines = activity_text.splitlines()
    lines[start : end + 1] = activity_lines

    return "\n".join(lines)


def delete_activity(puml, svg, clickedelement):
    lines = puml.splitlines()
    start, end = find_full_bounds(puml, svg, clickedelement)
    del lines[start : end + 1]

    return "\n".join(lines)


def add_note_activity(puml, svg, clickedelement):
    lines = puml.splitlines()
    count = index_of_clicked_activity(svg, clickedelement)
    start = find_activity_start(lines, count)
    end = find_activity_end(lines, start)
    if not lines[end + 1].startswith("note"):
        lines.insert(end + 1, "end note")
        lines.insert(end + 1, "note")
        lines.insert(end + 1, "note right")
    return "\n".join(lines)


def detach_activity(puml, svg, clickedelement):
    lines = puml.splitlines()
    count = index_of_clicked_activity(svg, clickedelement)
    start = find_activity_start(lines, count)
    end = find_activity_end(lines, start)
    if lines[end + 1].strip().startswith("note"):
        while lines[end] != "end note":
            end += 1
    if lines[end + 1].strip() == "break":
        lines[end + 1] = "detach"
    elif lines[end + 1].strip() == "detach":
        del lines[end + 1]
    else:
        lines.insert(end + 1, "detach")
    return "\n".join(lines)


def break_activity(puml, svg, clickedelement):
    lines = puml.splitlines()
    count = index_of_clicked_activity(svg, clickedelement)
    start = find_activity_start(lines, count)
    end = find_activity_end(lines, start)
    if lines[end + 1].strip().startswith("note"):
        while lines[end] != "end note":
            end += 1
    if lines[end + 1].strip() == "detach":
        lines[end + 1] = "break"
    elif lines[end + 1].strip() == "break":
        del lines[end + 1]
    else:
        lines.insert(end + 1, "break")
    return "\n".join(lines)


def find_full_bounds(puml, svg, clickedelement) -> tuple[int, int]:
    lines = puml.splitlines()
    count = index_of_clicked_activity(svg, clickedelement)
    start = find_activity_start(lines, count)
    end = find_activity_end(lines, start)
    if lines[end + 1].startswith("note"):
        while lines[end] != "end note":
            end += 1
    if lines[end + 1] in ["detach", "break"]:
        end += 1
    return start, end


def add_arrow_label(puml, svg, where, clickedelement):
    lines = puml.splitlines()
    start, end = find_full_bounds(puml, svg, clickedelement)

    # Find all existing arrow labels in the format "-> Arrow label x;" where x is an integer.
    arrow_label_numbers = []
    for line in lines:
        match = re.search(r"-> Arrow label (\d+);", line)
        if match:
            arrow_label_numbers.append(int(match.group(1)))

    # Determine the next arrow label number
    if arrow_label_numbers:
        next_label_number = max(arrow_label_numbers) + 1
    else:
        next_label_number = 1

    # Insert the arrow label at the correct position
    if where == "above":
        lines.insert(start, f"-> Arrow label {next_label_number};")
    else:
        lines.insert(end + 1, f"-> Arrow label {next_label_number};")

    return "\n".join(lines)


def svgtochunklist(svg: str) -> list[SvgChunk]:
    chunks = []
    d = Pq(svg)

    rects = d("rect")
    for rect in rects:
        if (
            float(rect.get("height")) > 6
            and rect.get("style") == "stroke:#181818;stroke-width:0.5;"
        ):  # check that the rect is an activity and not a fork bar
            rect = Pq(rect)  # rect svg is self-closing, so no </rect> is in this.
            rect_svg = str(rect)
            rect_svg = rect_svg[:-2] + "></rect>"
            rect_obj = RectElement.from_svg(rect_svg)

            text_elements = []
            next_elem = rect.next()

            # Unified handling for both 'text' and 'a' elements
            while next_elem and next_elem[0].tag in {"text", "a"}:
                if next_elem[0].tag == "text":
                    # Handle text elements as before
                    element = TextElement.from_svg(next_elem)
                    next_elem = next_elem.next()
                elif next_elem[0].tag == "a":
                    # Handle 'a' elements similarly to text
                    link_href = next_elem[0].get("href")
                    link_text = next_elem[0].find("text").text

                    # Create a temporary TextElement for the <a> tag, excluding the link text itself from the label
                    element = TextElement(label=f"[[{link_href} {link_text}]]")
                    element.x = float(next_elem[0].find("text").get("x"))
                    element.y = float(next_elem[0].find("text").get("y"))
                    next_elem = next_elem.next()

                # Append to the text elements list
                text_elements.append(element)

            chunks.append(SvgChunk(object=rect_obj, text_elements=text_elements))

    return chunks


def svgchunktotext(svgchunklist: list[SvgChunk], clickedsvg: RectElement):
    text = ""

    for chunk in svgchunklist:
        if chunk.object == clickedsvg:
            previous_y = None  # Initialize previous Y value

            for index, text_element in enumerate(chunk.text_elements):
                if index == 0:
                    text += text_element.label
                else:
                    # Compare current element's Y with the previous one
                    if text_element.y == previous_y:
                        text += " " + text_element.label  # Same Y, add with space
                    else:
                        text += (
                            "\n" + text_element.label
                        )  # Different Y, add with newline

                previous_y = text_element.y  # Update previous Y value

    return text
