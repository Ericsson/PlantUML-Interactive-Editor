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

from plantuml_gui.util import checkifwhile

from .classes import PolyElement, SvgChunk


def whiletotext(svgchunklist: list[SvgChunk], clickedelement: PolyElement) -> list[str]:
    texts = []
    for chunk in svgchunklist:
        if chunk.object == clickedelement:
            texts.append(chunk.text_elements[1].label)
            texts.append(chunk.text_elements[2].label)
            texts.append(chunk.text_elements[0].label)
            break
    return texts


def find_index_loop(puml, svgchunklist, clickedelement):
    count = whilecount(svgchunklist, clickedelement)
    lines = puml.splitlines()
    while_start = findwhilebounds(lines, count)
    endwhile_start = findendwhilebounds(lines, while_start)
    return endwhile_start


def find_index_break(puml, svgchunklist, clickedelement):
    count = whilecount(svgchunklist, clickedelement)
    lines = puml.splitlines()
    while_start = findwhilebounds(lines, count)
    endwhile_start = findendwhilebounds(lines, while_start)
    return endwhile_start + 1


def delete_while(puml, svgchunklist, clickedelement):
    count = whilecount(svgchunklist, clickedelement)
    lines = puml.splitlines()
    while_start = findwhilebounds(lines, count)
    endwhile_start = findendwhilebounds(lines, while_start)
    del lines[while_start : endwhile_start + 1]
    return "\n".join(lines)


def editwhile(
    puml: str,
    svgchunklist: list[SvgChunk],
    whilestatement: str,
    breakstatement: str,
    loop: str,
    clickedelement,
):
    count = whilecount(svgchunklist, clickedelement)
    lines = puml.splitlines()
    while_start = findwhilebounds(lines, count)

    while_text = lines[while_start]
    while_text = re.sub(
        r"while \((.*?)\)",
        f"while ({whilestatement})",
        while_text,
        flags=re.DOTALL,
    )
    while_text = re.sub(
        r"is \((.*?)\)",
        f"is ({loop})",
        while_text,
        flags=re.DOTALL,
    )

    lines[while_start] = while_text

    endwhile_start = findendwhilebounds(lines, while_start)
    endwhile_text = lines[endwhile_start]
    endwhile_text = re.sub(
        r"endwhile \((.*?)\)",
        f"endwhile ({breakstatement})",
        endwhile_text,
        flags=re.DOTALL,
    )
    lines[endwhile_start] = endwhile_text

    return "\n".join(lines)


def findendwhilebounds(lines, start_while):
    start_endwhile = -1
    index = start_while

    level = 0
    while index < len(lines):
        line = lines[index]
        clean_line = line.strip()

        if level == 1:
            if clean_line.startswith("endwhile"):
                start_endwhile = index
                break

        if clean_line.startswith("while"):
            level += 1

        if level != 1 and clean_line.startswith("endwhile"):
            level -= 1  # pragma: no cover

        index += 1

    return start_endwhile


def findwhilebounds(lines, count):
    start_while = -1
    index = 0
    nesting_level = 0
    nested_stacks = []
    current_stack = []

    # Traverse the lines to find all while statements and their nesting levels
    while index < len(lines):
        line = lines[index]
        clean_line = line.strip()
        if clean_line.startswith("while"):
            current_stack.append((index, nesting_level))
            nesting_level += 1
        elif clean_line.startswith("endwhile"):
            nesting_level -= 1
            if nesting_level == 0:
                # Sort the current stack and add to nested_stacks
                current_stack.sort(key=lambda x: x[1], reverse=True)
                nested_stacks.append(current_stack)
                current_stack = []
        index += 1

    # Combine all nested stacks
    combined_stack = [item for sublist in nested_stacks for item in sublist]

    # Traverse the combined stack to find the correct while based on count
    for index, level in combined_stack:
        if count == 1:
            start_while = index
            break
        count -= 1

    return start_while


def get_while_line(puml, svgchunklist, clickedelement):
    count = whilecount(svgchunklist, clickedelement)
    lines = puml.splitlines()
    while_start = findwhilebounds(lines, count)
    while_end = findendwhilebounds(lines, while_start)
    return while_start, while_end


def whilecount(svgchunklist: list[SvgChunk], clickedelement: PolyElement):
    count = 0
    for svgchunk in svgchunklist:  # counts occurances of while polys
        if svgchunk.text_elements and checkifwhile(svgchunk):
            count += 1
        if svgchunk.object == clickedelement:
            break
    return count
