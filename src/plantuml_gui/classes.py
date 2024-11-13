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

from dataclasses import dataclass

from pyquery import PyQuery as Pq  # pragma: no cover


@dataclass
class Activity:
    label: str


@dataclass
class If:
    statement: str
    branch1: str
    branch2: str


@dataclass
class PumlChunk:
    text: str
    object: Activity | If | None


@dataclass
class Ellipse:
    cx: float
    cy: float

    def __eq__(self, other):
        return (
            isinstance(other, Ellipse) and self.cx == other.cx and self.cy == other.cy
        )

    @classmethod
    def from_svg(cls, svgtext: str):
        svg = Pq(svgtext)
        ellipse = svg("ellipse")
        return cls(float(ellipse.attr("cx")), float(ellipse.attr("cy")))  # type: ignore


@dataclass
class PolyElement:
    points: str

    def __eq__(self, other):
        return isinstance(other, PolyElement) and self.points == other.points

    @classmethod
    def from_svg(cls, svgtext: str):
        svg = Pq(svgtext)
        poly = svg("polygon")
        return cls(str(poly.attr("points")))

    def get_points(self):
        elements = self.points.split(",")
        pairs = [(elements[i], elements[i + 1]) for i in range(0, len(elements) - 1, 2)]

        unique_pairs = []
        seen = set()

        for pair in pairs:
            identifier = tuple(pair)
            if identifier not in seen:
                seen.add(identifier)
                unique_pairs.append(pair)

        return unique_pairs

    def is_merge(
        self,
    ):  # We need to check if its not a merge polygon. Merge polygons after switch statements have equal points to statement polys.
        elements = self.points.split(",")
        pairs = [(elements[i], elements[i + 1]) for i in range(0, len(elements) - 1, 2)]

        unique_pairs = []
        seen = set()

        for pair in pairs:
            identifier = tuple(pair)
            if identifier not in seen:
                seen.add(identifier)
                unique_pairs.append(pair)

        return len(unique_pairs) != 6


@dataclass(kw_only=True)
class TreeNode:
    index: int

    def add_node(self, node: "TreeNode"):
        pass  # pragma: no cover

    def add_indices(self, indices: list[int], lines: list[str]):
        pass  # pragma: no cover


@dataclass(kw_only=True)
class IfElseNode(TreeNode):
    ifbranch: list["TreeNode"]
    elsebranch: list["TreeNode"]
    inside_ifbranch: bool = True

    def add_node(self, node: TreeNode):
        if self.inside_ifbranch:
            self.ifbranch.append(node)
        else:
            self.elsebranch.append(node)

    def add_indices(self, indices: list[int], lines: list[str]):
        if not check_branch(lines, self.index):
            indices.append(self.index)
        for node in self.ifbranch:
            node.add_indices(indices, lines)
        for node in self.elsebranch:
            node.add_indices(indices, lines)
        if check_branch(lines, self.index):
            indices.append(self.index)


@dataclass(kw_only=True)
class RepeatSwitchNode(TreeNode):
    branch: list["TreeNode"]

    def add_node(self, node: TreeNode):
        self.branch.append(node)

    def add_indices(self, indices: list[int], lines: list[str]):
        if not lines[self.index].strip() == "repeat":
            indices.append(self.index)
        for node in self.branch:
            node.add_indices(indices, lines)
        if lines[self.index].strip() == "repeat":
            indices.append(self.index)


@dataclass
class RectElement:
    x: float
    y: float

    def __eq__(self, other):
        return (
            isinstance(other, RectElement) and self.x == other.x and self.y == other.y
        )

    @classmethod
    def from_svg(cls, svgtext: str):
        svg = Pq(svgtext)
        rect = svg("rect")
        return cls(float(rect.attr("x")), float(rect.attr("y")))  # type: ignore


@dataclass
class TextElement:
    label: str
    x: float | None = None
    y: float | None = None

    @classmethod
    def from_svg(cls, svgtext: str | Pq):
        svg = Pq(svgtext)
        text = svg("text")
        return cls(text.text(), float(text.attr("x")), float(text.attr("y")))  # type: ignore


@dataclass
class SvgChunk:
    object: RectElement | PolyElement | Ellipse
    text_elements: list[TextElement]


def check_branch(
    lines, index
):  # checks if we need to increment nesting due to if branch
    else_start, else_end = findelsebounds(lines, index)
    end = find_end(lines, index)
    if (
        else_end == -1  # no else branch
        or end == else_end + 1  # empty else branch
        or index == else_start - 1  # empty if branch
    ):
        return True
    else:
        if else_start - index == 2:
            if lines[index + 1].strip().startswith("(") or lines[
                index + 1
            ].strip().startswith("stop"):
                return True
        if end - else_end == 2:
            if lines[else_end + 1].strip().startswith("(") or lines[
                else_end + 1
            ].strip().startswith("stop"):
                return True

    return False


def findelsebounds(lines, if_start):
    start_else = -1
    end_else = -1
    index = if_start
    inside_else = False
    parentheses = 0

    level = 0
    while index < len(lines):  # find index of correct else line
        line = lines[index]
        clean_line = line.strip()
        if (
            level == 1
        ):  # if at level 1 its the correct else (level will always start off as 1 since the first line is the if statement were on)
            if clean_line.startswith("else"):
                start_else = index
                inside_else = True
        if clean_line.startswith(
            "if"
        ):  # nested if statement, we need to find two elses.
            level += 1
        if level != 1 and clean_line.startswith("else"):
            level -= 1

        if inside_else:
            parentheses += clean_line.count("(")
            parentheses -= clean_line.count(")")
            if parentheses == 0:
                end_else = index
                break
        index += 1

    return start_else, end_else


def find_end(lines, start_if):
    end_if = -1
    index = start_if
    level = 0
    start_line = lines[start_if].strip()

    if start_line == "repeat":
        while index < len(lines):
            line = lines[index]
            clean_line = line.strip()

            if level == 1:
                if clean_line.startswith("repeat while") or clean_line.startswith(
                    "repeatwhile"
                ):
                    end_if = index
                    break

            if clean_line == "repeat":
                level += 1

            if (
                level != 1
                and clean_line.startswith("repeat while")
                or clean_line.startswith("repeatwhile")
            ):
                level -= 1

            index += 1
    elif start_line.startswith("if"):
        while index < len(lines):
            line = lines[index]
            clean_line = line.strip()

            if level == 1:
                if clean_line.startswith("endif"):
                    end_if = index
                    break

            if clean_line.startswith("if"):
                level += 1

            if level != 1 and clean_line.startswith("endif"):
                level -= 1

            index += 1
    elif start_line.startswith("switch"):
        while index < len(lines):
            line = lines[index]
            clean_line = line.strip()

            if level == 1:
                if clean_line.startswith("endswitch"):
                    end_if = index
                    break

            if clean_line.startswith("switch"):
                level += 1

            if level != 1 and clean_line.startswith("endswitch"):
                level -= 1

            index += 1

    return end_if
