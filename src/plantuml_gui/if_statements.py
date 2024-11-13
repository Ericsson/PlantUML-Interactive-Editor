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
from typing import Literal

from plantuml_gui.util import checkifwhile  # pragma: no cover
from pyquery import PyQuery as Pq

from .classes import (
    IfElseNode,
    PolyElement,
    RepeatSwitchNode,
    SvgChunk,
    TextElement,
    find_end,
    findelsebounds,
)


def svgtochunklistpolygon(svg: str) -> list[SvgChunk]:
    chunks = []
    d = Pq(svg)

    polys = d("polygon")
    for poly in polys:
        poly = Pq(poly)
        poly_svg = str(poly)
        poly_svg = poly_svg[:-2] + "></polygon>"
        poly_obj = PolyElement.from_svg(poly_svg)
        if poly_obj.is_merge():
            continue  # differentiate between merge polygons and statements.

        text_elements = []
        next_elem = poly.next()

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

        chunks.append(SvgChunk(object=poly_obj, text_elements=text_elements))

    return chunks


def polychunktotext(
    puml: str, svgchunklist: list[SvgChunk], clickedelement: PolyElement
) -> list[str]:
    max_x, min_x = None, None
    max_y, min_y = None, None
    pairs = clickedelement.get_points()
    for pair in pairs:
        # Convert string values to integers
        x = float(pair[0])
        y = float(pair[1])

        # Update max_x and min_x
        if max_x is None or x > max_x:
            max_x = x
        if min_x is None or x < min_x:
            min_x = x

        # Update max_y and min_y
        if max_y is None or y > max_y:
            max_y = y
        if min_y is None or y < min_y:
            min_y = y

    lines = puml.splitlines()
    texts = []

    # Containers for the categorized texts
    inside_texts = []
    left_texts = []
    right_texts = []

    for chunk in svgchunklist:
        if chunk.object == clickedelement:
            # Dictionary to group texts by their y value
            y_groups: dict[float, list[str]] = {}

            for text_element in chunk.text_elements:
                curr_x = text_element.x
                curr_y = text_element.y

                # Check the position of the text_element
                if min_x <= curr_x < max_x and min_y < curr_y < max_y:
                    # Group texts by their y coordinate because embedded links will split a line into multiple svg elements.
                    if curr_y not in y_groups:
                        y_groups[curr_y] = []
                    y_groups[curr_y].append(text_element.label)
                elif curr_x < min_x or curr_y > max_y:
                    left_texts.append(text_element.label)
                elif curr_x >= max_x:
                    right_texts.append(text_element.label)

            # Combine the grouped texts into single strings for the same y value
            for grouped_texts in y_groups.values():
                inside_texts.append(" ".join(grouped_texts))

    # Combine the categorized texts into the final output
    if inside_texts:
        texts.append("\n".join(inside_texts))
    if left_texts:
        texts.append("\n".join(left_texts))
    if right_texts:
        texts.append("\n".join(right_texts))

    count = polyelementcount(svgchunklist, clickedelement)
    start = find_start(lines, count)
    end = find_end(lines, start)
    if_start, if_end = findifbounds(lines, start)
    else_start, else_end = findelsebounds(lines, start)
    if if_start == else_start - 1 and end - 1 != else_end:
        texts[1], texts[2] = texts[2], texts[1]
    return texts


def edittextinternalif2(
    puml: str,
    svgchunklist: list[SvgChunk],
    statement: str,
    branch1: str,
    branch2: str,
    clickedelement: PolyElement,
):
    count = polyelementcount(svgchunklist, clickedelement)
    lines = puml.splitlines()

    start = find_start(lines, count)
    end = find_end(lines, start)

    if lines[start].startswith("if"):
        if_start, if_end = findifbounds(lines, start)

        if_lines = lines[if_start : if_end + 1]
        if_text = "\n".join(if_lines)
        if_text = re.sub(
            r"if \((.*?)\)",
            f"if ({statement})",
            if_text,
            flags=re.DOTALL,
        )
        if_text = re.sub(
            r"then \((.*?)\)",
            f"then ({branch1})",
            if_text,
            flags=re.DOTALL,
        )

        if_lines = if_text.replace("\n", "\\n").splitlines()
        lines[if_start : if_end + 1] = if_lines

        else_start, else_end = findelsebounds(lines, if_start)
        if else_start == -1 and else_end == -1 and branch2 != "":
            start = find_start(lines, count)
            end = find_end(lines, start)
            lines.insert(end, f"else ({branch2})")

        else:
            else_lines = lines[else_start : else_end + 1]
            else_text = "\n".join(else_lines)
            else_text = re.sub(
                r"else \((.*?)\)",
                f"else ({branch2})",
                else_text,
                flags=re.DOTALL,
            )
            else_lines = else_text.replace("\n", "\\n").splitlines()
            lines[else_start : else_end + 1] = else_lines
        return "\n".join(lines)
    elif lines[start] == "repeat":
        repeatwhile_text = lines[end]
        repeatwhile_text = re.sub(
            r"while \((.*?)\)",
            f"while ({statement})",
            repeatwhile_text,
            flags=re.DOTALL,
        )
        repeatwhile_text = re.sub(
            r"is \((.*?)\)",
            f"is ({branch2})",
            repeatwhile_text,
            flags=re.DOTALL,
        )
        repeatwhile_text = re.sub(
            r"not \((.*?)\)",
            f"not ({branch1})",
            repeatwhile_text,
            flags=re.DOTALL,
        )
        lines[end] = repeatwhile_text.replace("\n", "\\n")
        return "\n".join(lines)
    elif lines[start].startswith("switch"):
        switch_text = lines[start]
        switch_text = re.sub(
            r"switch \((.*?)\)",
            f"switch ({statement})",
            switch_text,
            flags=re.DOTALL,
        )
        switch_lines = switch_text.splitlines()
        switch_text = "\n".join(switch_lines)
        lines[start] = switch_text.replace("\n", "\\n")
        return "\n".join(lines)


def findifbounds(lines, start):
    start_if = start
    end_if = -1
    index = start
    parentheses = 0
    then_found = False

    while index < len(lines):  # find index of the correct if statement.
        line = lines[index]
        clean_line = line.strip()
        parentheses += clean_line.count("(")
        parentheses -= clean_line.count(")")

        if "then" in clean_line:
            then_found = True

        if parentheses == 0 and then_found:
            end_if = index
            break
        index += 1
    return start_if, end_if


# def add_note_if(puml: str, svgchunklist: list[SvgChunk], clickedelement: PolyElement):
#     count = polyelementcount(svgchunklist, clickedelement)
#     lines = puml.splitlines()

#     start_if, end_if = findwholeifbounds(lines, count)
#     lines.insert(end_if + 1, "end note")
#     lines.insert(end_if + 1, "note")
#     lines.insert(end_if + 1, "note right")
#     return "\n".join(lines)


def deleteif(puml: str, svgchunklist: list[SvgChunk], clickedelement: PolyElement):
    count = polyelementcount(svgchunklist, clickedelement)
    lines = puml.splitlines()

    start_if = find_start(lines, count)
    end_if = find_end(lines, start_if)
    if lines[end_if + 1] == "detach":
        end_if += 1
    del lines[start_if : end_if + 1]
    return "\n".join(lines)


def findwholeifbounds(lines: list[str], count: int):
    start_if, end_if = -1, -1
    index = 0
    level = 0
    inside_if = False
    while index < len(lines):
        line = lines[index]
        clean_line = line.strip()

        if clean_line.startswith("if") or clean_line == "repeat":
            if count == 1 and not inside_if:
                start_if = index  # found start if index
                inside_if = True
                continue
            count -= 1
        if inside_if and clean_line.startswith("if") or clean_line == "repeat":
            level += 1
        if (
            clean_line.startswith("endif")
            or clean_line.startswith("repeat while")
            or clean_line.startswith("repeatwhile")
        ):
            level -= 1
            if inside_if and level == 0:
                end_if = index
                break
        index += 1

    return start_if, end_if


def build_tree(lines):
    indices = []
    roots = []
    stack = []
    for index, line in enumerate(lines):
        line = line.strip()
        if line.startswith("if"):
            newnode = IfElseNode(
                index=index, ifbranch=[], elsebranch=[], inside_ifbranch=True
            )
            add_node(roots, stack, newnode)

        if line.startswith("else"):
            stack[-1].inside_ifbranch = False

        if line == "repeat" or line.startswith("switch"):
            newnode = RepeatSwitchNode(index=index, branch=[])
            add_node(roots, stack, newnode)
        if startswith(line, "endif", "repeat while", "repeatwhile", "switch"):
            stack.pop()
    for node in roots:
        node.add_indices(indices, lines)
    return indices


def add_node(roots, stack, newnode):
    if not stack:
        roots.append(newnode)
    else:
        stack[-1].add_node(newnode)
    stack.append(newnode)


def startswith(line, *args):
    return any(line.startswith(arg) for arg in args)


def find_start(lines, count):
    elements = build_tree(lines)
    for index in elements:
        if count == 1:
            return index
            break
        count -= 1

    raise ValueError


def get_if_line(puml, svgchunklist, clickedelement):
    count = polyelementcount(svgchunklist, clickedelement)
    lines = puml.splitlines()
    start = find_start(lines, count)
    end = find_end(lines, start)
    if lines[start].strip() == "repeat":
        return end
    elif lines[start].strip().startswith("switch"):
        return start, end

    else:
        else_start, else_end = findelsebounds(lines, start)
        return start, else_start, end


def get_line_for_adding_into_if(
    puml: str, svg: str, clickedelement: PolyElement, where: Literal["left", "right"]
) -> int:
    svgchunklist = svgtochunklistpolygon(svg)
    count = polyelementcount(svgchunklist, clickedelement)
    lines = puml.splitlines()
    start = find_start(lines, count)
    end = find_end(lines, start)

    if lines[start].startswith("if"):
        start_if, end_if = findifbounds(lines, count)
        start_else, end_else = findelsebounds(lines, start_if)

        if where == "left":
            return end_else
        else:
            return end
    else:  # repeat while
        if where == "right":
            return end + 1
    raise ValueError(
        f"get_if_index called with unexpected combination of arguments {clickedelement=} and {where=}"
    )  # pragma: no cover


def polyelementcount(svgchunklist: list[SvgChunk], clickedelement: PolyElement):
    count = 0
    for svgchunk in svgchunklist:  # counts occurances of poly chunks (if statements)
        if svgchunk.text_elements and not checkifwhile(svgchunk):
            count += 1
        if svgchunk.object == clickedelement:
            break
    return count


def check_what_poly(puml, svgchunklist, clickedelement):
    count = polyelementcount(svgchunklist, clickedelement)
    lines = puml.splitlines()

    start = find_start(lines, count)
    return lines[start]


def add_backwards(puml, svgchunklist, clickedelement):
    count = polyelementcount(svgchunklist, clickedelement)
    lines = puml.splitlines()

    start = find_start(lines, count)
    end = find_end(lines, start)
    index = start
    while index < end:
        line = lines[index].strip()
        if line.startswith("backward"):
            return puml
        index += 1
    lines.insert(index, "backward:Activity;")
    return "\n".join(lines)


def check_if_repeat_has_backward(puml, svgchunklist, clickedelement):
    count = polyelementcount(svgchunklist, clickedelement)
    lines = puml.splitlines()

    start = find_start(lines, count)
    end = find_end(lines, start)
    index = start
    while index < end:
        line = lines[index].strip()
        if line.startswith("backward"):
            return "backward"
        index += 1
    return "empty"


def detach_if(puml, svgchunklist, clickedelement):
    count = polyelementcount(svgchunklist, clickedelement)
    lines = puml.splitlines()
    start, end = findwholeifbounds(lines, count)
    if lines[end + 1] == "detach":
        del lines[end + 1]
    else:
        lines.insert(end + 1, "detach")
    return "\n".join(lines)


def switch_again(puml, svgchunklist, clickedelement):
    count = polyelementcount(svgchunklist, clickedelement)
    lines = puml.splitlines()
    start = find_start(lines, count)
    end = find_end(lines, start)

    condition_label_numbers = []
    for line in lines:
        match = re.search(r"case \( condition (\d+)\)", line)
        if match:
            condition_label_numbers.append(int(match.group(1)))

    # Determine the next condition label number
    if condition_label_numbers:
        next_label_number = max(condition_label_numbers) + 1
    else:
        next_label_number = 1

    lines.insert(end, ":Activity;")
    lines.insert(end, f"case ( condition {next_label_number})")
    return "\n".join(lines)
