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


def add_title(puml):
    index = 0
    lines = puml.splitlines()
    for index, line in enumerate(lines):
        if line == "@startuml":
            if lines[index + 1].startswith("title"):
                break
            else:
                lines.insert(index + 1, "endtitle")
                lines.insert(index + 1, "Placeholder Title")
                lines.insert(index + 1, "title")
                break
    return "\n".join(lines)


def get_title_text(puml):
    lines = puml.splitlines()
    intitle = False
    text = ""
    for line in lines:
        if line == "endtitle" or line == "end title":
            break
        if intitle:
            if text == "":
                text += line
            else:
                text += "\n" + line
        if line == "title":
            intitle = True
    return text


def edit_title_text(puml, title):
    lines = puml.splitlines()
    title_lines = title.splitlines()
    start, end = find_title_bounds(lines)

    if title == "":
        del lines[start : end + 1]
        return "\n".join(lines)

    lines[start + 1 : end] = title_lines
    return "\n".join(lines)


def find_title_bounds(lines):
    start, end = -1, -1
    for index, line in enumerate(lines):
        if line.startswith("title"):
            start = index
        if line.startswith("endtitle") or line.startswith("end title"):
            end = index
    return start, end


def delete_title(puml):
    lines = puml.splitlines()
    start, end = find_title_bounds(lines)
    del lines[start : end + 1]
    return "\n".join(lines)
