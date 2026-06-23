# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2026 Ericsson
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

"""Tests for if-statement parsing functions: find_start, polychunktotext, findelsebounds, findifbounds."""

import pytest
from plantuml_gui.activity.classes import PolyElement
from plantuml_gui.activity.if_statements import (
    find_start,
    findelsebounds,
    findifbounds,
    get_line_for_adding_into_if,
    polychunktotext,
    svgtochunklistpolygon,
)


class TestIfStatements:
    def test_find_start(self):
        lines = """@startuml
start
repeat
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
  :read data;
  :generate diagrams;
repeat while (more data?) is (yes) not (no)
if (Bom) then (y)
  :Activity;
else (n)
  :Activity;
endif
@enduml""".splitlines()
        output = 3
        count = 1
        assert find_start(lines, count) == output

    def test_polychunk(self):
        clickedsvg = PolyElement.from_svg(
            """<polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,77.7734,123.5,90.5781,64.5,90.5781,52.5,77.7734,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>"""
        )
        svgchunklist = svgtochunklistpolygon(
            """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="56.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="66.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,77.7734,123.5,90.5781,64.5,90.5781,52.5,77.7734,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="75.0234">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="64.5" y="87.8281">Hello</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="75.0234">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="75.0234">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="100.5781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="121.5469">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="100.5781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="121.5469">Activity</text><polygon fill="#F1F1F1" points="94,140.5469,106,152.5469,94,164.5469,82,152.5469,94,140.5469" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="77.7734" y2="77.7734"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="77.7734" y2="100.5781"></line><polygon fill="#181818" points="38.5,90.5781,42.5,100.5781,46.5,90.5781,42.5,94.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="77.7734" y2="77.7734"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="77.7734" y2="100.5781"></line><polygon fill="#181818" points="141.5,90.5781,145.5,100.5781,149.5,90.5781,145.5,94.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="134.5469" y2="152.5469"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="152.5469" y2="152.5469"></line><polygon fill="#181818" points="72,148.5469,82,152.5469,72,156.5469,76,152.5469" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="134.5469" y2="152.5469"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="152.5469" y2="152.5469"></line><polygon fill="#181818" points="116,148.5469,106,152.5469,116,156.5469,112,152.5469" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="90,54.9688,94,64.9688,98,54.9688,94,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>"""
        )
        output = ["Statement\nHello", "yes", "no"]
        assert (
            polychunktotext(
                """@startuml
    :Activity 1;
    if (Statement
    Hello) then (yes)
      :Activity;
    else (no)
      :Activity;
    endif
    @enduml""",
                svgchunklist,
                clickedsvg,
            )
            == output
        )

    def test_polytotextbothbranchempty(self):
        clickedsvg = PolyElement.from_svg(
            """<polygon fill="#F1F1F1" points="46,64.9688,105,64.9688,117,76.9688,105,88.9688,46,88.9688,34,76.9688,46,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>"""
        )
        svgchunklist = svgtochunklistpolygon(
            """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="38" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="48" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="46,64.9688,105,64.9688,117,76.9688,105,88.9688,46,88.9688,34,76.9688,46,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="46" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="14" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="117" y="74.2188">no</text><polygon fill="#F1F1F1" points="75.5,104.9688,87.5,116.9688,75.5,128.9688,63.5,116.9688,75.5,104.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="34" x2="24" y1="76.9688" y2="76.9688"></line><polygon fill="#181818" points="20,86.9688,24,96.9688,28,86.9688,24,90.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="76.9688" y2="116.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="63.5" y1="116.9688" y2="116.9688"></line><polygon fill="#181818" points="53.5,112.9688,63.5,116.9688,53.5,120.9688,57.5,116.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="117" x2="127" y1="76.9688" y2="76.9688"></line><polygon fill="#181818" points="123,86.9688,127,96.9688,131,86.9688,127,90.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="127" x2="127" y1="76.9688" y2="116.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="127" x2="87.5" y1="116.9688" y2="116.9688"></line><polygon fill="#181818" points="97.5,112.9688,87.5,116.9688,97.5,120.9688,93.5,116.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="75.5" x2="75.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="71.5,54.9688,75.5,64.9688,79.5,54.9688,75.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>"""
        )
        output = ["Statement", "yes", "no"]
        assert (
            polychunktotext(
                """@startuml
:Activity 1;
if (Statement) then (yes)
else (no)
endif
@enduml""",
                svgchunklist,
                clickedsvg,
            )
            == output
        )

    def test_link_in_statement(self):
        clickedsvg = PolyElement.from_svg(
            """<polygon fill="#F1F1F1" points="64.5,64.9688,141.5,64.9688,153.5,76.9688,141.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>"""
        )
        svgchunklist = svgtochunklistpolygon(
            """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="65.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="75.5" y="32.1387" style="pointer-events: none;">Activity 1</text><polygon fill="#F1F1F1" points="64.5,64.9688,141.5,64.9688,153.5,76.9688,141.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="64.5" y="80.7769" style="pointer-events: none;">hej</text><a href="google.com" target="_top" title="google.com" xlink:actuate="onRequest" xlink:href="google.com" xlink:show="new" xlink:title="google.com" xlink:type="simple"><text fill="#0000FF" font-family="sans-serif" font-size="11" lengthAdjust="spacing" text-decoration="underline" textLength="38" x="85.5" y="80.7769" style="pointer-events: none;">google</text></a><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="127.5" y="80.7769" style="pointer-events: none;">då</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="74.3745" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="153.5" y="74.3745" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="120.1074" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="132" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="142" y="120.1074" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="103,138.9375,115,150.9375,103,162.9375,91,150.9375,103,138.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="38.5,88.9688,42.5,98.9688,46.5,88.9688,42.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="153.5" x2="163.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="163.5" x2="163.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="159.5,88.9688,163.5,98.9688,167.5,88.9688,163.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="91" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="81,146.9375,91,150.9375,81,154.9375,85,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="163.5" x2="163.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="163.5" x2="115" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="125,146.9375,115,150.9375,125,154.9375,121,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="103" x2="103" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="99,54.9688,103,64.9688,107,54.9688,103,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>"""
        )
        output = ["hej [[google.com google]] då", "yes", "no"]
        assert (
            polychunktotext(
                """@startuml
:Activity 1;
if (hej [[google.com google]] då) then (yes)
    :Activity;
else (no)
    :Activity;
endif
@enduml""",
                svgchunklist,
                clickedsvg,
            )
            == output
        )

    def test_polytotextbranch1empty(self):
        clickedsvg = PolyElement.from_svg(
            """<polygon fill="#F1F1F1" points="32,64.9688,91,64.9688,103,76.9688,91,88.9688,32,88.9688,20,76.9688,32,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>"""
        )
        svgchunklist = svgtochunklistpolygon(
            """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="24" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="34" y="31.9688">Activity 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="113.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="134.3398">Activity</text><polygon fill="#F1F1F1" points="32,64.9688,91,64.9688,103,76.9688,91,88.9688,32,88.9688,20,76.9688,32,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="65.5" y="99.0234">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="32" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="103" y="74.2188">yes</text><polygon fill="#F1F1F1" points="61.5,167.3398,73.5,179.3398,61.5,191.3398,49.5,179.3398,61.5,167.3398" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="88.9688" y2="113.3711"></line><polygon fill="#181818" points="57.5,103.3711,61.5,113.3711,65.5,103.3711,61.5,107.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="103" x2="115" y1="76.9688" y2="76.9688"></line><polygon fill="#181818" points="111,120.3555,115,130.3555,119,120.3555,115,124.3555" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="115" y1="76.9688" y2="179.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="73.5" y1="179.3398" y2="179.3398"></line><polygon fill="#181818" points="83.5,175.3398,73.5,179.3398,83.5,183.3398,79.5,179.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="147.3398" y2="167.3398"></line><polygon fill="#181818" points="57.5,157.3398,61.5,167.3398,65.5,157.3398,61.5,161.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="57.5,54.9688,61.5,64.9688,65.5,54.9688,61.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>"""
        )
        output = ["Statement", "yes", "no"]
        assert (
            polychunktotext(
                """@startuml
:Activity 1;
if (Statement) then (yes)
else (no)
  :Activity;
endif
@enduml""",
                svgchunklist,
                clickedsvg,
            )
            == output
        )

    def test_polytotextbranch2empty(self):
        clickedsvg = PolyElement.from_svg(
            """<polygon fill="#F1F1F1" points="32,64.9688,91,64.9688,103,76.9688,91,88.9688,32,88.9688,20,76.9688,32,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>"""
        )
        svgchunklist = svgtochunklistpolygon(
            """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="24" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="34" y="31.9688">Activity 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="113.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="134.3398">Activity</text><polygon fill="#F1F1F1" points="32,64.9688,91,64.9688,103,76.9688,91,88.9688,32,88.9688,20,76.9688,32,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="65.5" y="99.0234">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="32" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="103" y="74.2188">no</text><polygon fill="#F1F1F1" points="61.5,167.3398,73.5,179.3398,61.5,191.3398,49.5,179.3398,61.5,167.3398" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="88.9688" y2="113.3711"></line><polygon fill="#181818" points="57.5,103.3711,61.5,113.3711,65.5,103.3711,61.5,107.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="103" x2="115" y1="76.9688" y2="76.9688"></line><polygon fill="#181818" points="111,120.3555,115,130.3555,119,120.3555,115,124.3555" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="115" y1="76.9688" y2="179.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="73.5" y1="179.3398" y2="179.3398"></line><polygon fill="#181818" points="83.5,175.3398,73.5,179.3398,83.5,183.3398,79.5,179.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="147.3398" y2="167.3398"></line><polygon fill="#181818" points="57.5,157.3398,61.5,167.3398,65.5,157.3398,61.5,161.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="57.5,54.9688,61.5,64.9688,65.5,54.9688,61.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>"""
        )
        output = ["Statement", "yes", "no"]
        assert (
            polychunktotext(
                """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
endif
@enduml""",
                svgchunklist,
                clickedsvg,
            )
            == output
        )

    def test_findelseindex(self):
        if_start = 4
        lines = """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (noasdasd
asdfasdf
asdfasdf)
  :Activity;
endif
else (no)
  :Activity;
endif
@enduml""".splitlines()
        output = 6, 8
        assert findelsebounds(lines, if_start) == output

    def test_findifindex(self):
        start = 4
        lines = """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
if (Statement
asdf) then (yes)
  :Activity;
else (no)
  :Activity;
endif
else (no)
  :Activity;
endif
@enduml""".splitlines()
        output = 4, 5
        assert findifbounds(lines, start) == output


def test_get_if_index_raises_exception_if_invalid_combination_of_arguments():
    with pytest.raises(ValueError):
        get_line_for_adding_into_if("plantuml", "svg", PolyElement("points"), "left")
