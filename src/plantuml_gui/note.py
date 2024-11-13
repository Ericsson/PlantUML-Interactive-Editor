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


def note_count(svg, clickedelement):
    count = 0
    d = Pq(svg)

    paths = d("path")
    for path in paths:
        path = Pq(path)
        if (
            path[0].get("style") == "pointer-events: none;"
        ):  # to make sure the path creating the text inside connectors doesnt affect note count
            continue
        path_svg = str(path)
        path_svg = path_svg[:-2] + "></path>"
        next = path.next()
        if next[0].tag == "path":  # notes have a second path in top corner
            count += 1
            if path_svg == clickedelement:
                break
    return count


def find_note_bounds(lines, count):
    note_start, note_end = -1, -1
    index = 0
    inside_note = False

    while index < len(lines):
        line = lines[index]
        clean_line = line.strip()

        if clean_line.startswith("note left") or clean_line.startswith("note right"):
            if count == 1:
                note_start = index
                inside_note = True
            count -= 1
        if inside_note and clean_line.startswith("end note"):
            note_end = index
            break
        index += 1
    return note_start, note_end


def get_note_text(puml, svg, clickedelement):
    lines = puml.splitlines()
    count = note_count(svg, clickedelement)
    note_start, note_end = find_note_bounds(lines, count)
    note_textlines = lines[note_start + 1 : note_end]
    return "\n".join(note_textlines)


def edit_note(puml, svg, clickedelement, text):
    lines = puml.splitlines()
    count = note_count(svg, clickedelement)
    note_start, note_end = find_note_bounds(lines, count)
    if text == "":
        del lines[note_start : note_end + 1]
        return "\n".join(lines)
    new_note_textlines = text.splitlines()
    lines[note_start + 1 : note_end] = new_note_textlines
    return "\n".join(lines)


def delete_note(puml, svg, clickedelement):
    lines = puml.splitlines()
    count = note_count(svg, clickedelement)
    note_start, note_end = find_note_bounds(lines, count)
    del lines[note_start : note_end + 1]
    return "\n".join(lines)


def get_note_line(puml, svg, clickedelement):
    lines = puml.splitlines()
    count = note_count(svg, clickedelement)
    note_start, note_end = find_note_bounds(lines, count)
    return note_start, note_end


def note_toggle(puml, svg, clickedelement):
    lines = puml.splitlines()
    count = note_count(svg, clickedelement)
    note_start, note_end = find_note_bounds(lines, count)
    if lines[note_start] == "note left":
        lines[note_start] = "note right"
    else:
        lines[note_start] = "note left"
    return "\n".join(lines)
