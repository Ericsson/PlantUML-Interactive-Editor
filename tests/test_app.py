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

from flask import json
from plantuml_gui.activity import activity_indices
from plantuml_gui.app import polychunktotext, svgtochunklistpolygon
from plantuml_gui.classes import PolyElement
from plantuml_gui.if_statements import (
    build_tree,
    find_start,
    findelsebounds,
    findifbounds,
)


class TestRender:
    def test_render(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
@enduml"""
        }
        with client:
            response = client.post(
                "/render",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            assert "<svg" in response.data.decode("utf-8")

    def test_render_png(self, client):
        # Test data containing PlantUML code
        test_data = {
            "plantuml": """@startuml
            :Activity;
            @enduml"""
        }
        with client:
            response = client.post(
                "/renderPNG",
                data=json.dumps(test_data),
                content_type="application/json",
            )

            # Assert the response status code is 200 (OK)
            assert response.status_code == 200

            # Assert the Content-Type header is "image/png"
            assert response.content_type == "image/png"


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


class TestAppRoutesMerge:
    def test_addtomergenoifmerge3(self, client):
        test_data = {
            "plantuml": """@startuml
start
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
detach
repeat
:Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="65.6523" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="59.25" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="59.25" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="84"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="104.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="84"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="104.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="181.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="202.9375" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,137.9688,106,149.9688,94,161.9688,82,149.9688,94,137.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="74.5,245.9375,113.5,245.9375,125.5,257.9375,113.5,269.9375,74.5,269.9375,62.5,257.9375,74.5,245.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="279.9922" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="74.5" y="261.5898" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="125.5" y="255.1875" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="149.5" y="181.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="159.5" y="202.9375" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="301.4922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="322.4609" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="84"></line><polygon fill="#181818" points="38.5,74,42.5,84,46.5,74,42.5,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="62" y2="84"></line><polygon fill="#181818" points="141.5,74,145.5,84,149.5,74,145.5,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="117.9688" y2="122.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="94" y1="122.9688" y2="122.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="122.9688" y2="137.9688"></line><polygon fill="#181818" points="90,127.9688,94,137.9688,98,127.9688,94,131.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="161.9688" y2="181.9688"></line><polygon fill="#181818" points="90,171.9688,94,181.9688,98,171.9688,94,175.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="125.5" x2="181" y1="257.9375" y2="257.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="181" y1="215.9375" y2="257.9375"></line><polygon fill="#181818" points="177,225.9375,181,215.9375,185,225.9375,181,221.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="181" y1="149.9688" y2="181.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="106" y1="149.9688" y2="149.9688"></line><polygon fill="#181818" points="116,145.9688,106,149.9688,116,153.9688,112,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="215.9375" y2="245.9375"></line><polygon fill="#181818" points="90,235.9375,94,245.9375,98,235.9375,94,239.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="269.9375" y2="301.4922"></line><polygon fill="#181818" points="90,291.4922,94,301.4922,98,291.4922,94,295.4922" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="94,137.9688,106,149.9688,94,161.9688,82,149.9688,94,137.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToMerge",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
detach
repeat
:Activity 1;
:Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_addtomergenoifmerge2(self, client):
        test_data = {
            "plantuml": """@startuml
start
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
detach
endif
repeat
  :Activity;
  backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="65.6523" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="59.25" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="59.25" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="84"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="104.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="84"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="104.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="181.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="202.9375" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,137.9688,106,149.9688,94,161.9688,82,149.9688,94,137.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="74.5,245.9375,113.5,245.9375,125.5,257.9375,113.5,269.9375,74.5,269.9375,62.5,257.9375,74.5,245.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="279.9922" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="74.5" y="261.5898" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="125.5" y="255.1875" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="149.5" y="181.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="159.5" y="202.9375" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="301.4922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="322.4609" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="84"></line><polygon fill="#181818" points="38.5,74,42.5,84,46.5,74,42.5,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="62" y2="84"></line><polygon fill="#181818" points="141.5,74,145.5,84,149.5,74,145.5,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="117.9688" y2="122.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="94" y1="122.9688" y2="122.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="122.9688" y2="137.9688"></line><polygon fill="#181818" points="90,127.9688,94,137.9688,98,127.9688,94,131.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="161.9688" y2="181.9688"></line><polygon fill="#181818" points="90,171.9688,94,181.9688,98,171.9688,94,175.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="125.5" x2="181" y1="257.9375" y2="257.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="181" y1="215.9375" y2="257.9375"></line><polygon fill="#181818" points="177,225.9375,181,215.9375,185,225.9375,181,221.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="181" y1="149.9688" y2="181.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="106" y1="149.9688" y2="149.9688"></line><polygon fill="#181818" points="116,145.9688,106,149.9688,116,153.9688,112,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="215.9375" y2="245.9375"></line><polygon fill="#181818" points="90,235.9375,94,245.9375,98,235.9375,94,239.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="269.9375" y2="301.4922"></line><polygon fill="#181818" points="90,291.4922,94,301.4922,98,291.4922,94,295.4922" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="94,137.9688,106,149.9688,94,161.9688,82,149.9688,94,137.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToMerge",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
detach
endif
repeat
:Activity 1;
  :Activity;
  backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_addtomergenoifmerge(self, client):
        test_data = {
            "plantuml": """@startuml
start
if (Statement) then (yes)
  :Activity;
detach
else (no)
  :Activity;
endif
repeat
  :Activity;
  backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="65.6523" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="59.25" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="59.25" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="84"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="104.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="84"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="104.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="181.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="202.9375" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,137.9688,106,149.9688,94,161.9688,82,149.9688,94,137.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="74.5,245.9375,113.5,245.9375,125.5,257.9375,113.5,269.9375,74.5,269.9375,62.5,257.9375,74.5,245.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="279.9922" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="74.5" y="261.5898" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="125.5" y="255.1875" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="149.5" y="181.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="159.5" y="202.9375" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="301.4922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="322.4609" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="84"></line><polygon fill="#181818" points="38.5,74,42.5,84,46.5,74,42.5,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="62" y2="84"></line><polygon fill="#181818" points="141.5,74,145.5,84,149.5,74,145.5,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="117.9688" y2="122.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="94" y1="122.9688" y2="122.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="122.9688" y2="137.9688"></line><polygon fill="#181818" points="90,127.9688,94,137.9688,98,127.9688,94,131.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="161.9688" y2="181.9688"></line><polygon fill="#181818" points="90,171.9688,94,181.9688,98,171.9688,94,175.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="125.5" x2="181" y1="257.9375" y2="257.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="181" y1="215.9375" y2="257.9375"></line><polygon fill="#181818" points="177,225.9375,181,215.9375,185,225.9375,181,221.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="181" y1="149.9688" y2="181.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="106" y1="149.9688" y2="149.9688"></line><polygon fill="#181818" points="116,145.9688,106,149.9688,116,153.9688,112,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="215.9375" y2="245.9375"></line><polygon fill="#181818" points="90,235.9375,94,245.9375,98,235.9375,94,239.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="269.9375" y2="301.4922"></line><polygon fill="#181818" points="90,291.4922,94,301.4922,98,291.4922,94,295.4922" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="94,137.9688,106,149.9688,94,161.9688,82,149.9688,94,137.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToMerge",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
if (Statement) then (yes)
  :Activity;
detach
else (no)
  :Activity;
endif
repeat
:Activity 1;
  :Activity;
  backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_get_merge_line(self, client):
        test_data = {
            "plantuml": """@startuml
start
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
repeat
  :Activity;
  :Activity;
  backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="65.6523" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="59.25" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="59.25" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="84"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="104.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="84"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="104.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,123.9688,106,135.9688,94,147.9688,82,135.9688,94,123.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="211.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="232.9375" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="280.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="301.9063" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,167.9688,106,179.9688,94,191.9688,82,179.9688,94,167.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="74.5,334.9063,113.5,334.9063,125.5,346.9063,113.5,358.9063,74.5,358.9063,62.5,346.9063,74.5,334.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="368.9609" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="74.5" y="350.5586" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="125.5" y="344.1563" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="149.5" y="246.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="159.5" y="267.4219" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="390.4609"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="411.4297" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="84"></line><polygon fill="#181818" points="38.5,74,42.5,84,46.5,74,42.5,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="62" y2="84"></line><polygon fill="#181818" points="141.5,74,145.5,84,149.5,74,145.5,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="117.9688" y2="135.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="135.9688" y2="135.9688"></line><polygon fill="#181818" points="72,131.9688,82,135.9688,72,139.9688,76,135.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="117.9688" y2="135.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="135.9688" y2="135.9688"></line><polygon fill="#181818" points="116,131.9688,106,135.9688,116,139.9688,112,135.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="245.9375" y2="280.9375"></line><polygon fill="#181818" points="90,270.9375,94,280.9375,98,270.9375,94,274.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="191.9688" y2="211.9688"></line><polygon fill="#181818" points="90,201.9688,94,211.9688,98,201.9688,94,205.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="125.5" x2="181" y1="346.9063" y2="346.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="181" y1="280.4219" y2="346.9063"></line><polygon fill="#181818" points="177,290.4219,181,280.4219,185,290.4219,181,286.4219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="181" y1="179.9688" y2="246.4531"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="106" y1="179.9688" y2="179.9688"></line><polygon fill="#181818" points="116,175.9688,106,179.9688,116,183.9688,112,179.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="314.9063" y2="334.9063"></line><polygon fill="#181818" points="90,324.9063,94,334.9063,98,324.9063,94,328.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="147.9688" y2="167.9688"></line><polygon fill="#181818" points="90,157.9688,94,167.9688,98,157.9688,94,161.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="358.9063" y2="390.4609"></line><polygon fill="#181818" points="90,380.4609,94,390.4609,98,380.4609,94,384.4609" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="94,123.9688,106,135.9688,94,147.9688,82,135.9688,94,123.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getMergeLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
        response_json = json.loads(response.data.decode("utf-8"))
        result_value = response_json.get("result")

        # Expected value
        expected_puml = 6

        # Assert the result value is as expected
        assert result_value == expected_puml

    def test_addtomerge2(self, client):
        test_data = {
            "plantuml": """@startuml
start
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
repeat
  :Activity;
  :Activity;
  backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="65.6523" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="59.25" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="59.25" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="84"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="104.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="84"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="104.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,123.9688,106,135.9688,94,147.9688,82,135.9688,94,123.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="211.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="232.9375" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="280.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="301.9063" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,167.9688,106,179.9688,94,191.9688,82,179.9688,94,167.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="74.5,334.9063,113.5,334.9063,125.5,346.9063,113.5,358.9063,74.5,358.9063,62.5,346.9063,74.5,334.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="368.9609" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="74.5" y="350.5586" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="125.5" y="344.1563" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="149.5" y="246.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="159.5" y="267.4219" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="390.4609"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="411.4297" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="84"></line><polygon fill="#181818" points="38.5,74,42.5,84,46.5,74,42.5,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="62" y2="84"></line><polygon fill="#181818" points="141.5,74,145.5,84,149.5,74,145.5,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="117.9688" y2="135.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="135.9688" y2="135.9688"></line><polygon fill="#181818" points="72,131.9688,82,135.9688,72,139.9688,76,135.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="117.9688" y2="135.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="135.9688" y2="135.9688"></line><polygon fill="#181818" points="116,131.9688,106,135.9688,116,139.9688,112,135.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="245.9375" y2="280.9375"></line><polygon fill="#181818" points="90,270.9375,94,280.9375,98,270.9375,94,274.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="191.9688" y2="211.9688"></line><polygon fill="#181818" points="90,201.9688,94,211.9688,98,201.9688,94,205.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="125.5" x2="181" y1="346.9063" y2="346.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="181" y1="280.4219" y2="346.9063"></line><polygon fill="#181818" points="177,290.4219,181,280.4219,185,290.4219,181,286.4219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="181" y1="179.9688" y2="246.4531"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="181" x2="106" y1="179.9688" y2="179.9688"></line><polygon fill="#181818" points="116,175.9688,106,179.9688,116,183.9688,112,179.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="314.9063" y2="334.9063"></line><polygon fill="#181818" points="90,324.9063,94,334.9063,98,324.9063,94,328.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="147.9688" y2="167.9688"></line><polygon fill="#181818" points="90,157.9688,94,167.9688,98,157.9688,94,161.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="358.9063" y2="390.4609"></line><polygon fill="#181818" points="90,380.4609,94,390.4609,98,380.4609,94,384.4609" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="94,123.9688,106,135.9688,94,147.9688,82,135.9688,94,123.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToMerge",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
:Activity 1;
repeat
  :Activity;
  :Activity;
  backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_addactivitymerge(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
if (Statement) then (yes)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
:Activity;
endif
:Activity;
else (no)
if (Statement) then (yes)
  :Activity;
else (no)
  :Actaivity;
endif
:Activity;
endif
:Activity;
@enduml""",
            "svg": """<ellipse cx="258.875" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="227.375" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="237.375" y="70.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="229.375,103.9688,288.375,103.9688,300.375,115.9688,288.375,127.9688,229.375,127.9688,217.375,115.9688,229.375,103.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="229.375" y="119.6211" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="197.375" y="113.2188" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="300.375" y="113.2188" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="83.25" y="137.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="93.25" y="158.9375" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="85.25,206.9375,144.25,206.9375,156.25,218.9375,144.25,230.9375,85.25,230.9375,73.25,218.9375,85.25,206.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="85.25" y="222.5898" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="53.25" y="216.1875" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="156.25" y="216.1875" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="240.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="261.9063" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="155.5" y="240.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="165.5" y="261.9063" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="157.5,309.9063,216.5,309.9063,228.5,321.9063,216.5,333.9063,157.5,333.9063,145.5,321.9063,157.5,309.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="157.5" y="325.5586" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="125.5" y="319.1563" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="228.5" y="319.1563" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="104" y="343.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="114" y="364.875" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="207" y="343.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="217" y="364.875" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="187,383.875,199,395.875,187,407.875,175,395.875,187,383.875" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="155.5" y="427.875"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="165.5" y="448.8438" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="114.75,467.8438,126.75,479.8438,114.75,491.8438,102.75,479.8438,114.75,467.8438" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="83.25" y="511.8438"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="93.25" y="532.8125" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="373.5,137.9688,432.5,137.9688,444.5,149.9688,432.5,161.9688,373.5,161.9688,361.5,149.9688,373.5,137.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="373.5" y="153.6211" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="341.5" y="147.2188" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="444.5" y="147.2188" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="320" y="171.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="330" y="192.9375" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="419" y="171.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="429" y="192.9375" style="pointer-events: none;">Actaivity</text><polygon fill="#F1F1F1" points="403,211.9375,415,223.9375,403,235.9375,391,223.9375,403,211.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="371.5" y="270.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="381.5" y="291.9063" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="258.875,551.8125,270.875,563.8125,258.875,575.8125,246.875,563.8125,258.875,551.8125" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="227.375" y="595.8125"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="237.375" y="616.7813" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="258.875" x2="258.875" y1="30" y2="50"></line><polygon fill="#181818" points="254.875,40,258.875,50,262.875,40,258.875,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="135.5" y1="321.9063" y2="321.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="135.5" y1="321.9063" y2="343.9063"></line><polygon fill="#181818" points="131.5,333.9063,135.5,343.9063,139.5,333.9063,135.5,337.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="228.5" x2="238.5" y1="321.9063" y2="321.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="238.5" x2="238.5" y1="321.9063" y2="343.9063"></line><polygon fill="#181818" points="234.5,333.9063,238.5,343.9063,242.5,333.9063,238.5,337.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="135.5" y1="377.875" y2="395.875"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="175" y1="395.875" y2="395.875"></line><polygon fill="#181818" points="165,391.875,175,395.875,165,399.875,169,395.875" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="238.5" x2="238.5" y1="377.875" y2="395.875"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="238.5" x2="199" y1="395.875" y2="395.875"></line><polygon fill="#181818" points="209,391.875,199,395.875,209,399.875,205,395.875" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="187" x2="187" y1="274.9063" y2="309.9063"></line><polygon fill="#181818" points="183,299.9063,187,309.9063,191,299.9063,187,303.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="187" x2="187" y1="407.875" y2="427.875"></line><polygon fill="#181818" points="183,417.875,187,427.875,191,417.875,187,421.875" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="73.25" x2="42.5" y1="218.9375" y2="218.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="218.9375" y2="240.9375"></line><polygon fill="#181818" points="38.5,230.9375,42.5,240.9375,46.5,230.9375,42.5,234.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="156.25" x2="187" y1="218.9375" y2="218.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="187" x2="187" y1="218.9375" y2="240.9375"></line><polygon fill="#181818" points="183,230.9375,187,240.9375,191,230.9375,187,234.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="274.9063" y2="479.8438"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="102.75" y1="479.8438" y2="479.8438"></line><polygon fill="#181818" points="92.75,475.8438,102.75,479.8438,92.75,483.8438,96.75,479.8438" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="187" x2="187" y1="461.8438" y2="479.8438"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="187" x2="126.75" y1="479.8438" y2="479.8438"></line><polygon fill="#181818" points="136.75,475.8438,126.75,479.8438,136.75,483.8438,132.75,479.8438" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="114.75" x2="114.75" y1="171.9375" y2="206.9375"></line><polygon fill="#181818" points="110.75,196.9375,114.75,206.9375,118.75,196.9375,114.75,200.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="114.75" x2="114.75" y1="491.8438" y2="511.8438"></line><polygon fill="#181818" points="110.75,501.8438,114.75,511.8438,118.75,501.8438,114.75,505.8438" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="361.5" x2="351.5" y1="149.9688" y2="149.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="149.9688" y2="171.9688"></line><polygon fill="#181818" points="347.5,161.9688,351.5,171.9688,355.5,161.9688,351.5,165.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="444.5" x2="454.5" y1="149.9688" y2="149.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="454.5" x2="454.5" y1="149.9688" y2="171.9688"></line><polygon fill="#181818" points="450.5,161.9688,454.5,171.9688,458.5,161.9688,454.5,165.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="205.9375" y2="223.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="391" y1="223.9375" y2="223.9375"></line><polygon fill="#181818" points="381,219.9375,391,223.9375,381,227.9375,385,223.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="454.5" x2="454.5" y1="205.9375" y2="223.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="454.5" x2="415" y1="223.9375" y2="223.9375"></line><polygon fill="#181818" points="425,219.9375,415,223.9375,425,227.9375,421,223.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="403" x2="403" y1="235.9375" y2="270.9375"></line><polygon fill="#181818" points="399,260.9375,403,270.9375,407,260.9375,403,264.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="217.375" x2="114.75" y1="115.9688" y2="115.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="114.75" x2="114.75" y1="115.9688" y2="137.9688"></line><polygon fill="#181818" points="110.75,127.9688,114.75,137.9688,118.75,127.9688,114.75,131.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300.375" x2="403" y1="115.9688" y2="115.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="403" x2="403" y1="115.9688" y2="137.9688"></line><polygon fill="#181818" points="399,127.9688,403,137.9688,407,127.9688,403,131.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="114.75" x2="114.75" y1="545.8125" y2="563.8125"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="114.75" x2="246.875" y1="563.8125" y2="563.8125"></line><polygon fill="#181818" points="236.875,559.8125,246.875,563.8125,236.875,567.8125,240.875,563.8125" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="403" x2="403" y1="304.9063" y2="563.8125"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="403" x2="270.875" y1="563.8125" y2="563.8125"></line><polygon fill="#181818" points="280.875,559.8125,270.875,563.8125,280.875,567.8125,276.875,563.8125" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="258.875" x2="258.875" y1="83.9688" y2="103.9688"></line><polygon fill="#181818" points="254.875,93.9688,258.875,103.9688,262.875,93.9688,258.875,97.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="258.875" x2="258.875" y1="575.8125" y2="595.8125"></line><polygon fill="#181818" points="254.875,585.8125,258.875,595.8125,262.875,585.8125,258.875,589.8125" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="403,211.9375,415,223.9375,403,235.9375,391,223.9375,403,211.9375" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToMerge",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
if (Statement) then (yes)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
:Activity;
endif
:Activity;
else (no)
if (Statement) then (yes)
  :Activity;
else (no)
  :Actaivity;
endif
:Activity 1;
:Activity;
endif
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result


class TestAppRoutesGroup:
    def test_gettextpartition(self, client):
        test_data = {
            "plantuml": """@startuml
partition hej {
:Activity;
}
@enduml""",
            "svg": """<rect fill="none" height="75.2656" style="stroke:#000000;stroke-width:1.5;" width="83" x="11" y="11"></rect><path d="M42,11 L42,20.2969 L32,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="21" x="14" y="24.7969">hej</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="21" y="40.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="31" y="61.2656" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<path d="M42,11 L42,20.2969 L32,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
        }
        with client:
            response = client.post(
                "/getGroupText",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = "hej"
            assert response.data.decode("utf-8") == expected_result

    def test_editpartition(self, client):
        test_data = {
            "plantuml": """@startuml
partition hej {
:Activity;
}
@enduml""",
            "svg": """<rect fill="none" height="75.2656" style="stroke:#000000;stroke-width:1.5;" width="83" x="11" y="11"></rect><path d="M42,11 L42,20.2969 L32,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="21" x="14" y="24.7969">hej</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="21" y="40.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="31" y="61.2656" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<path d="M42,11 L42,20.2969 L32,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
            "text": "bom",
        }
        with client:
            response = client.post(
                "/editGroup",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
partition bom {
:Activity;
}
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_get_group_line(self, client):
        test_data = {
            "plantuml": """@startuml
group group
:Activity 1;
end group
partition bom {
:Activity 8;
}
@enduml""",
            "svg": """<rect fill="none" height="75.2656" style="stroke:#000000;stroke-width:1.5;" width="95" x="11" y="11"></rect><path d="M62,11 L62,20.2969 L52,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="41" x="14" y="24.7969">group</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="21" y="40.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="31" y="61.2656" style="pointer-events: none;">Activity 1</text><rect fill="none" height="82.2656" style="stroke:#000000;stroke-width:1.5;" width="95" x="11" y="96.2656"></rect><path d="M52,96.2656 L52,105.5625 L42,115.5625 L11,115.5625 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="31" x="14" y="110.0625">bom</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="21" y="132.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="31" y="153.5313" style="pointer-events: none;">Activity 8</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="74.2656" y2="132.5625"></line><polygon fill="#181818" points="54.5,122.5625,58.5,132.5625,62.5,122.5625,58.5,126.5625" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M62,11 L62,20.2969 L52,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
        }
        with client:
            response = client.post(
                "/getGroupLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
        response_json = json.loads(response.data.decode("utf-8"))
        result_value = response_json.get("result")

        # Expected value
        expected_puml = [1, 3]

        # Assert the result value is as expected
        assert result_value == expected_puml

    def test_deletegroupwithpartition(self, client):
        test_data = {
            "plantuml": """@startuml
group group
:Activity 1;
end group
partition bom {
:Activity 8;
}
@enduml""",
            "svg": """<rect fill="none" height="75.2656" style="stroke:#000000;stroke-width:1.5;" width="95" x="11" y="11"></rect><path d="M62,11 L62,20.2969 L52,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="41" x="14" y="24.7969">group</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="21" y="40.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="31" y="61.2656" style="pointer-events: none;">Activity 1</text><rect fill="none" height="82.2656" style="stroke:#000000;stroke-width:1.5;" width="95" x="11" y="96.2656"></rect><path d="M52,96.2656 L52,105.5625 L42,115.5625 L11,115.5625 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="31" x="14" y="110.0625">bom</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="21" y="132.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="31" y="153.5313" style="pointer-events: none;">Activity 8</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="74.2656" y2="132.5625"></line><polygon fill="#181818" points="54.5,122.5625,58.5,132.5625,62.5,122.5625,58.5,126.5625" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M62,11 L62,20.2969 L52,30.2969 L11,30.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
        }
        with client:
            response = client.post(
                "/deleteGroup",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
:Activity 1;
partition bom {
:Activity 8;
}
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_deletegroup(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
note
end note
group group
if (Statement) then (yes)
  :Activity;
else (no)
group hej
  :Activity;
end group
endif
end group
stop
@enduml""",
            "svg": """<ellipse cx="106" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M157.5,54.418 L157.5,62.9844 L137.5,66.9844 L157.5,70.9844 L157.5,79.5508 A0,0 0 0 0 157.5,79.5508 L207.5,79.5508 A0,0 0 0 0 207.5,79.5508 L207.5,64.418 L197.5,54.418 L157.5,54.418 A0,0 0 0 0 157.5,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M197.5,54.418 L197.5,64.418 L207.5,64.418 L197.5,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="29" x="163.5" y="71.3008" style="pointer-events: none;">note</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="74.5" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="84.5" y="70.9688" style="pointer-events: none;">Activity</text><rect fill="none" height="194.5625" style="stroke:#000000;stroke-width:1.5;" width="208" x="11" y="93.9688"></rect><path d="M62,93.9688 L62,103.2656 L52,113.2656 L11,113.2656 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="41" x="14" y="107.7656">group</text><polygon fill="#F1F1F1" points="76.5,130.2656,135.5,130.2656,147.5,142.2656,135.5,154.2656,76.5,154.2656,64.5,142.2656,76.5,130.2656" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="76.5" y="145.918" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="44.5" y="139.5156" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="147.5" y="139.5156" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="23" y="164.2656"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="33" y="185.2344" style="pointer-events: none;">Activity</text><rect fill="none" height="82.2656" style="stroke:#000000;stroke-width:1.5;" width="83" x="116" y="164.2656"></rect><path d="M147,164.2656 L147,173.5625 L137,183.5625 L116,183.5625 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="21" x="119" y="178.0625">hej</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="126" y="200.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="136" y="221.5313" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="106,252.5313,118,264.5313,106,276.5313,94,264.5313,106,252.5313" style="stroke:#181818;stroke-width:0.5;"></polygon><ellipse cx="106" cy="319.5313" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="106" cy="319.5313" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="30" y2="50"></line><polygon fill="#181818" points="102,40,106,50,110,40,106,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="64.5" x2="54.5" y1="142.2656" y2="142.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="54.5" y1="142.2656" y2="164.2656"></line><polygon fill="#181818" points="50.5,154.2656,54.5,164.2656,58.5,154.2656,54.5,158.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="147.5" x2="157.5" y1="142.2656" y2="142.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="157.5" y1="142.2656" y2="200.5625"></line><polygon fill="#181818" points="153.5,190.5625,157.5,200.5625,161.5,190.5625,157.5,194.5625" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="54.5" y1="198.2344" y2="264.5313"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="94" y1="264.5313" y2="264.5313"></line><polygon fill="#181818" points="84,260.5313,94,264.5313,84,268.5313,88,264.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="157.5" y1="234.5313" y2="264.5313"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="118" y1="264.5313" y2="264.5313"></line><polygon fill="#181818" points="128,260.5313,118,264.5313,128,268.5313,124,264.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="83.9688" y2="130.2656"></line><polygon fill="#181818" points="102,120.2656,106,130.2656,110,120.2656,106,124.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="276.5313" y2="308.5313"></line><polygon fill="#181818" points="102,298.5313,106,308.5313,110,298.5313,106,302.5313" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M62,93.9688 L62,103.2656 L52,113.2656 L11,113.2656 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
        }
        with client:
            response = client.post(
                "/deleteGroup",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
note right
note
end note
if (Statement) then (yes)
  :Activity;
else (no)
group hej
  :Activity;
end group
endif
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_editgroupempty(self, client):
        test_data = {
            "plantuml": """@startuml
start
group group
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
end group
stop
@enduml""",
            "svg": """<ellipse cx="106" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="none" height="146.2656" style="stroke:#000000;stroke-width:1.5;" width="190" x="11" y="40"></rect><path d="M62,40 L62,49.2969 L52,59.2969 L11,59.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="41" x="14" y="53.7969">group</text><polygon fill="#F1F1F1" points="76.5,76.2969,135.5,76.2969,147.5,88.2969,135.5,100.2969,76.5,100.2969,64.5,88.2969,76.5,76.2969" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="76.5" y="91.9492" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="44.5" y="85.5469" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="147.5" y="85.5469" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="23" y="110.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="33" y="131.2656" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="126" y="110.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="136" y="131.2656" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="106,150.2656,118,162.2656,106,174.2656,94,162.2656,106,150.2656" style="stroke:#181818;stroke-width:0.5;"></polygon><ellipse cx="106" cy="217.2656" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="106" cy="217.2656" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="64.5" x2="54.5" y1="88.2969" y2="88.2969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="54.5" y1="88.2969" y2="110.2969"></line><polygon fill="#181818" points="50.5,100.2969,54.5,110.2969,58.5,100.2969,54.5,104.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="147.5" x2="157.5" y1="88.2969" y2="88.2969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="157.5" y1="88.2969" y2="110.2969"></line><polygon fill="#181818" points="153.5,100.2969,157.5,110.2969,161.5,100.2969,157.5,104.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="54.5" y1="144.2656" y2="162.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="94" y1="162.2656" y2="162.2656"></line><polygon fill="#181818" points="84,158.2656,94,162.2656,84,166.2656,88,162.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="157.5" y1="144.2656" y2="162.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="118" y1="162.2656" y2="162.2656"></line><polygon fill="#181818" points="128,158.2656,118,162.2656,128,166.2656,124,162.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="30" y2="76.2969"></line><polygon fill="#181818" points="102,66.2969,106,76.2969,110,66.2969,106,70.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="174.2656" y2="206.2656"></line><polygon fill="#181818" points="102,196.2656,106,206.2656,110,196.2656,106,200.2656" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M62,40 L62,49.2969 L52,59.2969 L11,59.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
            "text": "",
        }
        with client:
            response = client.post(
                "/editGroup",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_editgroup(self, client):
        test_data = {
            "plantuml": """@startuml
start
group group
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
end group
stop
@enduml""",
            "svg": """<ellipse cx="106" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="none" height="146.2656" style="stroke:#000000;stroke-width:1.5;" width="190" x="11" y="40"></rect><path d="M62,40 L62,49.2969 L52,59.2969 L11,59.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="41" x="14" y="53.7969">group</text><polygon fill="#F1F1F1" points="76.5,76.2969,135.5,76.2969,147.5,88.2969,135.5,100.2969,76.5,100.2969,64.5,88.2969,76.5,76.2969" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="76.5" y="91.9492" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="44.5" y="85.5469" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="147.5" y="85.5469" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="23" y="110.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="33" y="131.2656" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="126" y="110.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="136" y="131.2656" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="106,150.2656,118,162.2656,106,174.2656,94,162.2656,106,150.2656" style="stroke:#181818;stroke-width:0.5;"></polygon><ellipse cx="106" cy="217.2656" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="106" cy="217.2656" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="64.5" x2="54.5" y1="88.2969" y2="88.2969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="54.5" y1="88.2969" y2="110.2969"></line><polygon fill="#181818" points="50.5,100.2969,54.5,110.2969,58.5,100.2969,54.5,104.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="147.5" x2="157.5" y1="88.2969" y2="88.2969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="157.5" y1="88.2969" y2="110.2969"></line><polygon fill="#181818" points="153.5,100.2969,157.5,110.2969,161.5,100.2969,157.5,104.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="54.5" y1="144.2656" y2="162.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="54.5" x2="94" y1="162.2656" y2="162.2656"></line><polygon fill="#181818" points="84,158.2656,94,162.2656,84,166.2656,88,162.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="157.5" y1="144.2656" y2="162.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="157.5" x2="118" y1="162.2656" y2="162.2656"></line><polygon fill="#181818" points="128,158.2656,118,162.2656,128,166.2656,124,162.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="30" y2="76.2969"></line><polygon fill="#181818" points="102,66.2969,106,76.2969,110,66.2969,106,70.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106" x2="106" y1="174.2656" y2="206.2656"></line><polygon fill="#181818" points="102,196.2656,106,206.2656,110,196.2656,106,200.2656" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M62,40 L62,49.2969 L52,59.2969 L11,59.2969 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path>""",
            "text": "hej",
        }
        with client:
            response = client.post(
                "/editGroup",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
group hej
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
end group
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_gettextgroup(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
note
end note
group hello
if (Statement) then (yes)
group hej
  :Activity;
end group
else (no)
  :Activity;
endif
end group
fork
  :action;
note left
note
end note
fork again
  :action;
end fork
stop
@enduml""",
            "svg": """<ellipse cx="133" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M184.5,54.418 L184.5,62.9844 L164.5,66.9844 L184.5,70.9844 L184.5,79.5508 A0,0 0 0 0 184.5,79.5508 L234.5,79.5508 A0,0 0 0 0 234.5,79.5508 L234.5,64.418 L224.5,54.418 L184.5,54.418 A0,0 0 0 0 184.5,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M224.5,54.418 L224.5,64.418 L234.5,64.418 L224.5,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="29" x="190.5" y="71.3008" style="pointer-events: none;">note</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="101.5" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="111.5" y="70.9688" style="pointer-events: none;">Activity</text><rect fill="none" height="194.5625" style="stroke:#000000;stroke-width:1.5;" width="216" x="20" y="93.9688"></rect><path d="M63,93.9688 L63,103.2656 L53,113.2656 L20,113.2656 " fill="transparent" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="33" x="23" y="107.7656" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="103.5,130.2656,162.5,130.2656,174.5,142.2656,162.5,154.2656,103.5,154.2656,91.5,142.2656,103.5,130.2656" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="103.5" y="145.918" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="71.5" y="139.5156" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="174.5" y="139.5156" style="pointer-events: none;">no</text><rect fill="none" height="82.2656" style="stroke:#000000;stroke-width:1.5;" width="83" x="40" y="164.2656"></rect><path d="M71,164.2656 L71,173.5625 L61,183.5625 L40,183.5625 " fill="transparent" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="21" x="43" y="178.0625" style="pointer-events: none;">hej</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="50" y="200.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="60" y="221.5313" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="153" y="164.2656"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="163" y="185.2344" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="133,252.5313,145,264.5313,133,276.5313,121,264.5313,133,252.5313" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="242" x="11" y="308.5313"></rect><path d="M25,338.9492 L25,364.082 A0,0 0 0 0 25,364.082 L75,364.082 A0,0 0 0 0 75,364.082 L75,356.9492 L95,351.5156 L75,348.9492 L75,348.9492 L65,338.9492 L25,338.9492 A0,0 0 0 0 25,338.9492 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M65,338.9492 L65,348.9492 L75,348.9492 L65,338.9492 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="29" x="31" y="355.832" style="pointer-events: none;">note</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="95" y="334.5313"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="105" y="355.5" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="182" y="334.5313"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="192" y="355.5" style="pointer-events: none;">action</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="242" x="11" y="388.5"></rect><ellipse cx="133" cy="425.5" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="133" cy="425.5" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133" x2="133" y1="30" y2="50"></line><polygon fill="#181818" points="129,40,133,50,137,40,133,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="91.5" x2="81.5" y1="142.2656" y2="142.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="81.5" x2="81.5" y1="142.2656" y2="200.5625"></line><polygon fill="#181818" points="77.5,190.5625,81.5,200.5625,85.5,190.5625,81.5,194.5625" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="174.5" x2="184.5" y1="142.2656" y2="142.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184.5" x2="184.5" y1="142.2656" y2="164.2656"></line><polygon fill="#181818" points="180.5,154.2656,184.5,164.2656,188.5,154.2656,184.5,158.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="81.5" x2="81.5" y1="234.5313" y2="264.5313"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="81.5" x2="121" y1="264.5313" y2="264.5313"></line><polygon fill="#181818" points="111,260.5313,121,264.5313,111,268.5313,115,264.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184.5" x2="184.5" y1="198.2344" y2="264.5313"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184.5" x2="145" y1="264.5313" y2="264.5313"></line><polygon fill="#181818" points="155,260.5313,145,264.5313,155,268.5313,151,264.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133" x2="133" y1="83.9688" y2="130.2656"></line><polygon fill="#181818" points="129,120.2656,133,130.2656,137,120.2656,133,124.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="124.5" x2="124.5" y1="314.5313" y2="334.5313"></line><polygon fill="#181818" points="120.5,324.5313,124.5,334.5313,128.5,324.5313,124.5,328.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="211.5" x2="211.5" y1="314.5313" y2="334.5313"></line><polygon fill="#181818" points="207.5,324.5313,211.5,334.5313,215.5,324.5313,211.5,328.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="124.5" x2="124.5" y1="368.5" y2="388.5"></line><polygon fill="#181818" points="120.5,378.5,124.5,388.5,128.5,378.5,124.5,382.5" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="211.5" x2="211.5" y1="368.5" y2="388.5"></line><polygon fill="#181818" points="207.5,378.5,211.5,388.5,215.5,378.5,211.5,382.5" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133" x2="133" y1="276.5313" y2="308.5313"></line><polygon fill="#181818" points="129,298.5313,133,308.5313,137,298.5313,133,302.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133" x2="133" y1="394.5" y2="414.5"></line><polygon fill="#181818" points="129,404.5,133,414.5,137,404.5,133,408.5" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M71,164.2656 L71,173.5625 L61,183.5625 L40,183.5625 " fill="transparent" style="stroke:#000000;stroke-width:1.5;"></path>""",
        }
        with client:
            response = client.post(
                "/getGroupText",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = "hej"
            assert response.data.decode("utf-8") == expected_result


class TestAppRouteEncodeDecode:
    def test_decode(self, client):
        test_data = {"hash": """SoWkIImgAStDuG8pk1nIyrA0F00="""}
        with client:
            response = client.post(
                "/decode",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_encode(self, client):
        test_data = {
            "plantuml": """@startuml
start
@enduml"""
        }
        with client:
            response = client.post(
                "/encode",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """SoWkIImgAStDuG8pk1nIyrA0F00="""
            assert response.data.decode("utf-8") == expected_result


class TestAppRoutesWhile:
    def test_addforkbreak(self, client):
        test_data = {
            "plantuml": """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
stop
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="67.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="88.5781" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="90" y="46.1094" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="48" y="27.707" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="21" y="21.3047" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="143.5781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="164.5469" style="pointer-events: none;">hello again</text><ellipse cx="86" cy="208.5469" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="86" cy="208.5469" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="36.0547" y2="67.6094"></line><polygon fill="#181818" points="82,57.6094,86,67.6094,90,57.6094,86,61.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="101.5781" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="148" y1="111.5781" y2="111.5781"></line><polygon fill="#181818" points="144,76.1914,148,66.1914,152,76.1914,148,72.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="148" y1="24.0547" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="136" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="146,20.0547,136,24.0547,146,28.0547,142,24.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="36" x2="24" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="20,62.1914,24,72.1914,28,62.1914,24,66.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="24.0547" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="86" y1="123.5781" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="123.5781" y2="143.5781"></line><polygon fill="#181818" points="82,133.5781,86,143.5781,90,133.5781,86,137.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="177.5469" y2="197.5469"></line><polygon fill="#181818" points="82,187.5469,86,197.5469,90,187.5469,86,191.5469" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "type": "fork",
            "where": "break",
        }
        with client:
            response = client.post(
                "/addToWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
fork
:action;
fork again
:action;
end fork
:hello again;
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_addifloop(self, client):
        test_data = {
            "plantuml": """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
stop
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="67.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="88.5781" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="90" y="46.1094" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="48" y="27.707" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="21" y="21.3047" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="143.5781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="164.5469" style="pointer-events: none;">hello again</text><ellipse cx="86" cy="208.5469" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="86" cy="208.5469" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="36.0547" y2="67.6094"></line><polygon fill="#181818" points="82,57.6094,86,67.6094,90,57.6094,86,61.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="101.5781" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="148" y1="111.5781" y2="111.5781"></line><polygon fill="#181818" points="144,76.1914,148,66.1914,152,76.1914,148,72.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="148" y1="24.0547" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="136" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="146,20.0547,136,24.0547,146,28.0547,142,24.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="36" x2="24" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="20,62.1914,24,72.1914,28,62.1914,24,66.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="24.0547" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="86" y1="123.5781" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="123.5781" y2="143.5781"></line><polygon fill="#181818" points="82,133.5781,86,143.5781,90,133.5781,86,137.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="177.5469" y2="197.5469"></line><polygon fill="#181818" points="82,187.5469,86,197.5469,90,187.5469,86,191.5469" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "type": "if",
            "where": "loop",
        }
        with client:
            response = client.post(
                "/addToWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
if (Statement) then (yes)
:Activity;
else (no)
:Activity;
endif
endwhile (No);
:hello again;
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_delwhile(self, client):
        test_data = {
            "plantuml": """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
stop
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="67.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="88.5781" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="90" y="46.1094" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="48" y="27.707" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="21" y="21.3047" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="143.5781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="164.5469" style="pointer-events: none;">hello again</text><ellipse cx="86" cy="208.5469" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="86" cy="208.5469" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="36.0547" y2="67.6094"></line><polygon fill="#181818" points="82,57.6094,86,67.6094,90,57.6094,86,61.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="101.5781" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="148" y1="111.5781" y2="111.5781"></line><polygon fill="#181818" points="144,76.1914,148,66.1914,152,76.1914,148,72.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="148" y1="24.0547" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="136" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="146,20.0547,136,24.0547,146,28.0547,142,24.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="36" x2="24" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="20,62.1914,24,72.1914,28,62.1914,24,66.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="24.0547" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="86" y1="123.5781" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="123.5781" y2="143.5781"></line><polygon fill="#181818" points="82,133.5781,86,143.5781,90,133.5781,86,137.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="177.5469" y2="197.5469"></line><polygon fill="#181818" points="82,187.5469,86,197.5469,90,187.5469,86,191.5469" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
:hello again;
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_get_while_line(self, client):
        test_data = {
            "plantuml": """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
stop
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="67.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="88.5781" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="90" y="46.1094" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="48" y="27.707" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="21" y="21.3047" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="143.5781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="164.5469" style="pointer-events: none;">hello again</text><ellipse cx="86" cy="208.5469" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="86" cy="208.5469" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="36.0547" y2="67.6094"></line><polygon fill="#181818" points="82,57.6094,86,67.6094,90,57.6094,86,61.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="101.5781" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="148" y1="111.5781" y2="111.5781"></line><polygon fill="#181818" points="144,76.1914,148,66.1914,152,76.1914,148,72.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="148" y1="24.0547" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="136" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="146,20.0547,136,24.0547,146,28.0547,142,24.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="36" x2="24" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="20,62.1914,24,72.1914,28,62.1914,24,66.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="24.0547" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="86" y1="123.5781" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="123.5781" y2="143.5781"></line><polygon fill="#181818" points="82,133.5781,86,143.5781,90,133.5781,86,137.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="177.5469" y2="197.5469"></line><polygon fill="#181818" points="82,187.5469,86,197.5469,90,187.5469,86,191.5469" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getWhileLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = [1, 3]

            # Assert the result value is as expected
            assert result_value == expected_puml

    def test_editwhilemultiplenests(self, client):
        test_data = {
            "plantuml": """@startuml
start
while (ST_ONGOING) is (Yes)
    :hello;
    while (ST_ONGOING) is (Yes)
    :hello;
    while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:activity;
endwhile (No);
:activity;
endwhile (No);
:activity;
while (ST_ONGOING) is (Yes)
    :hello;
    while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:activity;
endwhile (No);
:activity;
@enduml""",
            "svg": """<ellipse cx="122" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="97" y="105.5547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="107" y="126.5234" style="pointer-events: none;">hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="97" y="215.0781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="107" y="236.0469" style="pointer-events: none;">hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="97" y="329.8516"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="107" y="350.8203" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="84,269.0469,160,269.0469,172,281.0469,160,293.0469,84,293.0469,72,281.0469,84,269.0469" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="126" y="303.1016" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="84" y="284.6992" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="57" y="278.2969" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="90.5" y="405.8203"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="100.5" y="426.7891" style="pointer-events: none;">activity</text><polygon fill="#F1F1F1" points="84,159.5234,160,159.5234,172,171.5234,160,183.5234,84,183.5234,72,171.5234,84,159.5234" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="126" y="193.5781" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="84" y="175.1758" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="57" y="168.7734" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="90.5" y="481.7891"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="100.5" y="502.7578" style="pointer-events: none;">activity</text><polygon fill="#F1F1F1" points="84,50,160,50,172,62,160,74,84,74,72,62,84,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="126" y="84.0547" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="84" y="65.6523" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="57" y="59.25" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="90.5" y="557.7578"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="100.5" y="578.7266" style="pointer-events: none;">activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="97" y="667.2813"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="107" y="688.25" style="pointer-events: none;">hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="97" y="782.0547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="107" y="803.0234" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="84,721.25,160,721.25,172,733.25,160,745.25,84,745.25,72,733.25,84,721.25" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="126" y="755.3047" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="84" y="736.9023" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="57" y="730.5" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="90.5" y="858.0234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="100.5" y="878.9922" style="pointer-events: none;">activity</text><polygon fill="#F1F1F1" points="84,611.7266,160,611.7266,172,623.7266,160,635.7266,84,635.7266,72,623.7266,84,611.7266" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="126" y="645.7813" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="84" y="627.3789" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="57" y="620.9766" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="90.5" y="933.9922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="100.5" y="954.9609" style="pointer-events: none;">activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="293.0469" y2="329.8516"></line><polygon fill="#181818" points="118,319.8516,122,329.8516,126,319.8516,122,323.8516" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="363.8203" y2="373.8203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="184" y1="373.8203" y2="373.8203"></line><polygon fill="#181818" points="180,338.4336,184,328.4336,188,338.4336,184,334.4336" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184" x2="184" y1="281.0469" y2="373.8203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184" x2="172" y1="281.0469" y2="281.0469"></line><polygon fill="#181818" points="182,277.0469,172,281.0469,182,285.0469,178,281.0469" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="72" x2="60" y1="281.0469" y2="281.0469"></line><polygon fill="#181818" points="56,324.4336,60,334.4336,64,324.4336,60,328.4336" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="60" x2="60" y1="281.0469" y2="385.8203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="60" x2="122" y1="385.8203" y2="385.8203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="385.8203" y2="405.8203"></line><polygon fill="#181818" points="118,395.8203,122,405.8203,126,395.8203,122,399.8203" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="249.0469" y2="269.0469"></line><polygon fill="#181818" points="118,259.0469,122,269.0469,126,259.0469,122,263.0469" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="183.5234" y2="215.0781"></line><polygon fill="#181818" points="118,205.0781,122,215.0781,126,205.0781,122,209.0781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="439.7891" y2="449.7891"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="196" y1="449.7891" y2="449.7891"></line><polygon fill="#181818" points="192,320.0313,196,310.0313,200,320.0313,196,316.0313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="196" x2="196" y1="171.5234" y2="449.7891"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="196" x2="172" y1="171.5234" y2="171.5234"></line><polygon fill="#181818" points="182,167.5234,172,171.5234,182,175.5234,178,171.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="72" x2="42" y1="171.5234" y2="171.5234"></line><polygon fill="#181818" points="38,306.0313,42,316.0313,46,306.0313,42,310.0313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42" x2="42" y1="171.5234" y2="461.7891"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42" x2="122" y1="461.7891" y2="461.7891"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="461.7891" y2="481.7891"></line><polygon fill="#181818" points="118,471.7891,122,481.7891,126,471.7891,122,475.7891" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="139.5234" y2="159.5234"></line><polygon fill="#181818" points="118,149.5234,122,159.5234,126,149.5234,122,153.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="74" y2="105.5547"></line><polygon fill="#181818" points="118,95.5547,122,105.5547,126,95.5547,122,99.5547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="515.7578" y2="525.7578"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="208" y1="525.7578" y2="525.7578"></line><polygon fill="#181818" points="204,301.6289,208,291.6289,212,301.6289,208,297.6289" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="208" x2="208" y1="62" y2="525.7578"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="208" x2="172" y1="62" y2="62"></line><polygon fill="#181818" points="182,58,172,62,182,66,178,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="72" x2="24" y1="62" y2="62"></line><polygon fill="#181818" points="20,287.6289,24,297.6289,28,287.6289,24,291.6289" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="62" y2="537.7578"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="122" y1="537.7578" y2="537.7578"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="537.7578" y2="557.7578"></line><polygon fill="#181818" points="118,547.7578,122,557.7578,126,547.7578,122,551.7578" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="30" y2="50"></line><polygon fill="#181818" points="118,40,122,50,126,40,122,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="745.25" y2="782.0547"></line><polygon fill="#181818" points="118,772.0547,122,782.0547,126,772.0547,122,776.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="816.0234" y2="826.0234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="184" y1="826.0234" y2="826.0234"></line><polygon fill="#181818" points="180,790.6367,184,780.6367,188,790.6367,184,786.6367" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184" x2="184" y1="733.25" y2="826.0234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="184" x2="172" y1="733.25" y2="733.25"></line><polygon fill="#181818" points="182,729.25,172,733.25,182,737.25,178,733.25" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="72" x2="60" y1="733.25" y2="733.25"></line><polygon fill="#181818" points="56,776.6367,60,786.6367,64,776.6367,60,780.6367" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="60" x2="60" y1="733.25" y2="838.0234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="60" x2="122" y1="838.0234" y2="838.0234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="838.0234" y2="858.0234"></line><polygon fill="#181818" points="118,848.0234,122,858.0234,126,848.0234,122,852.0234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="701.25" y2="721.25"></line><polygon fill="#181818" points="118,711.25,122,721.25,126,711.25,122,715.25" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="635.7266" y2="667.2813"></line><polygon fill="#181818" points="118,657.2813,122,667.2813,126,657.2813,122,661.2813" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="891.9922" y2="901.9922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="196" y1="901.9922" y2="901.9922"></line><polygon fill="#181818" points="192,772.2344,196,762.2344,200,772.2344,196,768.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="196" x2="196" y1="623.7266" y2="901.9922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="196" x2="172" y1="623.7266" y2="623.7266"></line><polygon fill="#181818" points="182,619.7266,172,623.7266,182,627.7266,178,623.7266" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="72" x2="42" y1="623.7266" y2="623.7266"></line><polygon fill="#181818" points="38,758.2344,42,768.2344,46,758.2344,42,762.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42" x2="42" y1="623.7266" y2="913.9922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42" x2="122" y1="913.9922" y2="913.9922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="913.9922" y2="933.9922"></line><polygon fill="#181818" points="118,923.9922,122,933.9922,126,923.9922,122,927.9922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="122" x2="122" y1="591.7266" y2="611.7266"></line><polygon fill="#181818" points="118,601.7266,122,611.7266,126,601.7266,122,605.7266" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "whilestatement": "A",
            "break": "B",
            "loop": "C",
            "svgelement": """<polygon fill="#F1F1F1" points="84,721.25,160,721.25,172,733.25,160,745.25,84,745.25,72,733.25,84,721.25" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
while (ST_ONGOING) is (Yes)
    :hello;
    while (ST_ONGOING) is (Yes)
    :hello;
    while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:activity;
endwhile (No);
:activity;
endwhile (No);
:activity;
while (ST_ONGOING) is (Yes)
    :hello;
    while (A) is (C)
    :hello;
endwhile (B);
:activity;
endwhile (No);
:activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_editwhilenested(self, client):
        test_data = {
            "plantuml": """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
    while (Hej) is (Bom)
    :hello;
endwhile (Bam);
:hello again;
endwhile (No);
:hello again;
stop
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="67.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="88.5781" style="pointer-events: none;">hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="182.3828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="203.3516" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="74,121.5781,98,121.5781,110,133.5781,98,145.5781,74,145.5781,62,133.5781,74,121.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="26" x="90" y="155.6328" style="pointer-events: none;">Bom</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="18" x="77" y="137.2305" style="pointer-events: none;">Hej</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="26" x="36" y="130.8281" style="pointer-events: none;">Bam</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="258.3516"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="279.3203" style="pointer-events: none;">hello again</text><polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="90" y="46.1094" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="48" y="27.707" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="21" y="21.3047" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="334.3203"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="355.2891" style="pointer-events: none;">hello again</text><ellipse cx="86" cy="399.2891" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="86" cy="399.2891" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="145.5781" y2="182.3828"></line><polygon fill="#181818" points="82,172.3828,86,182.3828,90,172.3828,86,176.3828" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="216.3516" y2="226.3516"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="123" y1="226.3516" y2="226.3516"></line><polygon fill="#181818" points="119,190.9648,123,180.9648,127,190.9648,123,186.9648" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="123" x2="123" y1="133.5781" y2="226.3516"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="123" x2="110" y1="133.5781" y2="133.5781"></line><polygon fill="#181818" points="120,129.5781,110,133.5781,120,137.5781,116,133.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="62" x2="49" y1="133.5781" y2="133.5781"></line><polygon fill="#181818" points="45,176.9648,49,186.9648,53,176.9648,49,180.9648" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="49" x2="49" y1="133.5781" y2="238.3516"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="49" x2="86" y1="238.3516" y2="238.3516"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="238.3516" y2="258.3516"></line><polygon fill="#181818" points="82,248.3516,86,258.3516,90,248.3516,86,252.3516" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="101.5781" y2="121.5781"></line><polygon fill="#181818" points="82,111.5781,86,121.5781,90,111.5781,86,115.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="36.0547" y2="67.6094"></line><polygon fill="#181818" points="82,57.6094,86,67.6094,90,57.6094,86,61.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="292.3203" y2="302.3203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="148" y1="302.3203" y2="302.3203"></line><polygon fill="#181818" points="144,172.5625,148,162.5625,152,172.5625,148,168.5625" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="148" y1="24.0547" y2="302.3203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="136" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="146,20.0547,136,24.0547,146,28.0547,142,24.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="36" x2="24" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="20,158.5625,24,168.5625,28,158.5625,24,162.5625" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="24.0547" y2="314.3203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="86" y1="314.3203" y2="314.3203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="314.3203" y2="334.3203"></line><polygon fill="#181818" points="82,324.3203,86,334.3203,90,324.3203,86,328.3203" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="368.2891" y2="388.2891"></line><polygon fill="#181818" points="82,378.2891,86,388.2891,90,378.2891,86,382.2891" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "whilestatement": "A",
            "break": "B",
            "loop": "C",
            "svgelement": """<polygon fill="#F1F1F1" points="74,121.5781,98,121.5781,110,133.5781,98,145.5781,74,145.5781,62,133.5781,74,121.5781" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
    while (A) is (C)
    :hello;
endwhile (B);
:hello again;
endwhile (No);
:hello again;
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_editwhile(self, client):
        test_data = {
            "plantuml": """@startuml
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
stop
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="61" y="67.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="71" y="88.5781" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="90" y="46.1094" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="48" y="27.707" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="21" y="21.3047" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="41.5" y="143.5781"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="51.5" y="164.5469" style="pointer-events: none;">hello again</text><ellipse cx="86" cy="208.5469" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="86" cy="208.5469" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="36.0547" y2="67.6094"></line><polygon fill="#181818" points="82,57.6094,86,67.6094,90,57.6094,86,61.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="101.5781" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="148" y1="111.5781" y2="111.5781"></line><polygon fill="#181818" points="144,76.1914,148,66.1914,152,76.1914,148,72.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="148" y1="24.0547" y2="111.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="148" x2="136" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="146,20.0547,136,24.0547,146,28.0547,142,24.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="36" x2="24" y1="24.0547" y2="24.0547"></line><polygon fill="#181818" points="20,62.1914,24,72.1914,28,62.1914,24,66.1914" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="24.0547" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="86" y1="123.5781" y2="123.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="123.5781" y2="143.5781"></line><polygon fill="#181818" points="82,133.5781,86,143.5781,90,133.5781,86,137.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="86" x2="86" y1="177.5469" y2="197.5469"></line><polygon fill="#181818" points="82,187.5469,86,197.5469,90,187.5469,86,191.5469" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "whilestatement": "Hej",
            "break": "Bom",
            "loop": "Bam",
            "svgelement": """<polygon fill="#F1F1F1" points="48,12.0547,124,12.0547,136,24.0547,124,36.0547,48,36.0547,36,24.0547,48,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
while (Hej) is (Bam)
    :hello;
endwhile (Bom);
:hello again;
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_getwhiletext(self, client):
        test_data = {
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="70.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="64.5,103.9688,123.5,103.9688,135.5,115.9688,123.5,127.9688,64.5,127.9688,52.5,115.9688,64.5,103.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="119.6211" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="113.2188" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="113.2188" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="137.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="158.9375" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="137.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="158.9375" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,177.9375,106,189.9375,94,201.9375,82,189.9375,94,177.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="69" y="277.4922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="79" y="298.4609" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="56,221.9375,132,221.9375,144,233.9375,132,245.9375,56,245.9375,44,233.9375,56,221.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="98" y="255.9922" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="56" y="237.5898" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="29" y="231.1875" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="49.5" y="353.4609"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="59.5" y="374.4297" style="pointer-events: none;">hello again</text><ellipse cx="94" cy="418.4297" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="94" cy="418.4297" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="115.9688" y2="115.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="115.9688" y2="137.9688"></line><polygon fill="#181818" points="38.5,127.9688,42.5,137.9688,46.5,127.9688,42.5,131.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="115.9688" y2="115.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="115.9688" y2="137.9688"></line><polygon fill="#181818" points="141.5,127.9688,145.5,137.9688,149.5,127.9688,145.5,131.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="171.9375" y2="189.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="189.9375" y2="189.9375"></line><polygon fill="#181818" points="72,185.9375,82,189.9375,72,193.9375,76,189.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="171.9375" y2="189.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="189.9375" y2="189.9375"></line><polygon fill="#181818" points="116,185.9375,106,189.9375,116,193.9375,112,189.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="83.9688" y2="103.9688"></line><polygon fill="#181818" points="90,93.9688,94,103.9688,98,93.9688,94,97.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="245.9375" y2="277.4922"></line><polygon fill="#181818" points="90,267.4922,94,277.4922,98,267.4922,94,271.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="311.4609" y2="321.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="156" y1="321.4609" y2="321.4609"></line><polygon fill="#181818" points="152,286.0742,156,276.0742,160,286.0742,156,282.0742" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="156" x2="156" y1="233.9375" y2="321.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="156" x2="144" y1="233.9375" y2="233.9375"></line><polygon fill="#181818" points="154,229.9375,144,233.9375,154,237.9375,150,233.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="32" y1="233.9375" y2="233.9375"></line><polygon fill="#181818" points="28,272.0742,32,282.0742,36,272.0742,32,276.0742" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="32" x2="32" y1="233.9375" y2="333.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="32" x2="94" y1="333.4609" y2="333.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="333.4609" y2="353.4609"></line><polygon fill="#181818" points="90,343.4609,94,353.4609,98,343.4609,94,347.4609" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="201.9375" y2="221.9375"></line><polygon fill="#181818" points="90,211.9375,94,221.9375,98,211.9375,94,215.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="387.4297" y2="407.4297"></line><polygon fill="#181818" points="90,397.4297,94,407.4297,98,397.4297,94,401.4297" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="56,221.9375,132,221.9375,144,233.9375,132,245.9375,56,245.9375,44,233.9375,56,221.9375" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getTextWhile",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = ["ST_ONGOING", "No", "Yes"]
            assert json.loads(response.data.decode("utf-8")) == expected_result


class TestAppRouteArrow:
    def test_case_duplicate_check(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
case ( condition 2)
    :Activity;
endswitch
@enduml""",
            "svg": """<ellipse cx="118.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="104.5,50,132.5,50,144.5,62,132.5,74,104.5,74,92.5,62,104.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="104.5" y="65.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="130.748" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="128.5" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="138.5" y="130.748" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="118.5,153.5781,118.5,153.5781,130.5,165.5781,118.5,177.5781,118.5,177.5781,106.5,165.5781,118.5,153.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="92.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="109.6094"></line><polygon fill="#181818" points="38.5,99.6094,42.5,109.6094,46.5,99.6094,42.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="46.5" y="89.6128">condition 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="144.5" x2="160" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="62" y2="109.6094"></line><polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="164" y="89.6128">condition 2</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="106.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="96.5,161.5781,106.5,165.5781,96.5,169.5781,100.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="130.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="140.5,161.5781,130.5,165.5781,140.5,169.5781,136.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="118.5" y1="30" y2="50"></line><polygon fill="#181818" points="114.5,40,118.5,50,122.5,40,118.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/checkDuplicateArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            assert not result_value

    def test_check_arrow_duplicate(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="84.3594"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="105.3281" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="91" x="126.5" y="159.8828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="67" x="140.5" y="180.8516" style="pointer-events: none;">2. activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="84.3594"></line><polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="259" x="176" y="51.3047">Nsmf_PDUSession_CreateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="105" x="176" y="64.1094">received from AMF</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="118.3281" y2="159.8828"></line><polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="82" x="176" y="139.6328">label on arrow</text>""",
            "svgelement": """<polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/checkDuplicateArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            assert not result_value

    def test_get_arrow_line(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="84.3594"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="105.3281" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="91" x="126.5" y="159.8828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="67" x="140.5" y="180.8516" style="pointer-events: none;">2. activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="84.3594"></line><polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="259" x="176" y="51.3047">Nsmf_PDUSession_CreateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="105" x="176" y="64.1094">received from AMF</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="118.3281" y2="159.8828"></line><polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="82" x="176" y="139.6328">label on arrow</text>""",
            "svgelement": """<polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getArrowLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = [5, 5]

            # Assert the result value is as expected
            assert result_value == expected_puml

    def test_edit_switch_case_multiline(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
switch (test?)
case (condition\nnewline)
    :Activity;
case (hello)
    :Activity;
endswitch
@enduml""",
            "svg": """<ellipse cx="93.75" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="79.75,50,107.75,50,119.75,62,107.75,74,79.75,74,67.75,62,79.75,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="79.75" y="65.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="134.5083"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="155.647" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="113.5" y="121.7036"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="123.5" y="142.8423" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="93.75,178.4771,93.75,178.4771,105.75,190.4771,93.75,202.4771,93.75,202.4771,81.75,190.4771,93.75,178.4771" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="67.75" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="134.5083"></line><polygon fill="#181818" points="38.5,124.5083,42.5,134.5083,46.5,124.5083,42.5,128.5083" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="51" x="42.5" y="95.3047">condition</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="43" x="42.5" y="108.1094">newline</text><line style="stroke:#181818;stroke-width:1.0;" x1="119.75" x2="145" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145" x2="145" y1="62" y2="121.7036"></line><polygon fill="#181818" points="141,111.7036,145,121.7036,149,111.7036,145,115.7036" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="27" x="145" y="95.3047">hello</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="168.4771" y2="190.4771"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="81.75" y1="190.4771" y2="190.4771"></line><polygon fill="#181818" points="71.75,186.4771,81.75,190.4771,71.75,194.4771,75.75,190.4771" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145" x2="145" y1="155.6724" y2="190.4771"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145" x2="105.75" y1="190.4771" y2="190.4771"></line><polygon fill="#181818" points="115.75,186.4771,105.75,190.4771,115.75,194.4771,111.75,190.4771" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="93.75" x2="93.75" y1="30" y2="50"></line><polygon fill="#181818" points="89.75,40,93.75,50,97.75,40,93.75,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#181818" points="38.5,124.5083,42.5,134.5083,46.5,124.5083,42.5,128.5083" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "text": "hello",
        }
        with client:
            response = client.post(
                "/editArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
switch (test?)
case (hello)
    :Activity;
case (hello)
    :Activity;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_delete_switch_case_nestedswitch(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
    switch (test?)
    case ( condition 1)
        :Activity;
    case ( condition 2)
        :Activity;
    endswitch
case ( condition 2)
    :Activity;
endswitch
@enduml""",
            "svg": """<ellipse cx="177.25" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="163.25,50,191.25,50,203.25,62,191.25,74,163.25,74,151.25,62,163.25,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="163.25" y="65.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="87" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="97" y="130.748" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="104.5,163.5781,132.5,163.5781,144.5,175.5781,132.5,187.5781,104.5,187.5781,92.5,175.5781,104.5,163.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="104.5" y="179.3862" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="223.1875"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="244.3262" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="128.5" y="223.1875"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="138.5" y="244.3262" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="118.5,267.1563,118.5,267.1563,130.5,279.1563,118.5,291.1563,118.5,291.1563,106.5,279.1563,118.5,267.1563" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="236" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="246" y="130.748" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="177.25,301.1563,177.25,301.1563,189.25,313.1563,177.25,325.1563,177.25,325.1563,165.25,313.1563,177.25,301.1563" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="92.5" x2="42.5" y1="175.5781" y2="175.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="175.5781" y2="223.1875"></line><polygon fill="#181818" points="38.5,213.1875,42.5,223.1875,46.5,213.1875,42.5,217.1875" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="46.5" y="203.1909">condition 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="144.5" x2="160" y1="175.5781" y2="175.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="175.5781" y2="223.1875"></line><polygon fill="#181818" points="156,213.1875,160,223.1875,164,213.1875,160,217.1875" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="164" y="203.1909">condition 2</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="257.1563" y2="279.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="106.5" y1="279.1563" y2="279.1563"></line><polygon fill="#181818" points="96.5,275.1563,106.5,279.1563,96.5,283.1563,100.5,279.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="257.1563" y2="279.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="130.5" y1="279.1563" y2="279.1563"></line><polygon fill="#181818" points="140.5,275.1563,130.5,279.1563,140.5,283.1563,136.5,279.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="118.5" y1="143.5781" y2="163.5781"></line><polygon fill="#181818" points="114.5,153.5781,118.5,163.5781,122.5,153.5781,118.5,157.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="151.25" x2="118.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="118.5" y1="62" y2="109.6094"></line><polygon fill="#181818" points="114.5,99.6094,118.5,109.6094,122.5,99.6094,118.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="122.5" y="89.6128">condition 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="203.25" x2="267.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="267.5" x2="267.5" y1="62" y2="109.6094"></line><polygon fill="#181818" points="263.5,99.6094,267.5,109.6094,271.5,99.6094,267.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="271.5" y="89.6128">condition 2</text><line style="stroke:#181818;stroke-width:1.0;" x1="118.5" x2="118.5" y1="291.1563" y2="313.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="165.25" y1="313.1563" y2="313.1563"></line><polygon fill="#181818" points="155.25,309.1563,165.25,313.1563,155.25,317.1563,159.25,313.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="267.5" x2="267.5" y1="143.5781" y2="313.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="267.5" x2="189.25" y1="313.1563" y2="313.1563"></line><polygon fill="#181818" points="199.25,309.1563,189.25,313.1563,199.25,317.1563,195.25,313.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="177.25" x2="177.25" y1="30" y2="50"></line><polygon fill="#181818" points="173.25,40,177.25,50,181.25,40,177.25,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#181818" points="114.5,99.6094,118.5,109.6094,122.5,99.6094,118.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
switch (test?)
case ( condition 2)
    :Activity;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_delete_switch_case(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
case ( condition 2)
    :Activity;
endswitch
@enduml""",
            "svg": """<ellipse cx="118.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="104.5,50,132.5,50,144.5,62,132.5,74,104.5,74,92.5,62,104.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="104.5" y="65.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="130.748" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="128.5" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="138.5" y="130.748" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="118.5,153.5781,118.5,153.5781,130.5,165.5781,118.5,177.5781,118.5,177.5781,106.5,165.5781,118.5,153.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="92.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="109.6094"></line><polygon fill="#181818" points="38.5,99.6094,42.5,109.6094,46.5,99.6094,42.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="46.5" y="89.6128">condition 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="144.5" x2="160" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="62" y2="109.6094"></line><polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="164" y="89.6128">condition 2</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="106.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="96.5,161.5781,106.5,165.5781,96.5,169.5781,100.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="130.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="140.5,161.5781,130.5,165.5781,140.5,169.5781,136.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="118.5" y1="30" y2="50"></line><polygon fill="#181818" points="114.5,40,118.5,50,122.5,40,118.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_edit_switch_case(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
case ( condition 2)
    :Activity;
endswitch
@enduml""",
            "svg": """<ellipse cx="118.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="104.5,50,132.5,50,144.5,62,132.5,74,104.5,74,92.5,62,104.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="104.5" y="65.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="130.748" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="128.5" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="138.5" y="130.748" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="118.5,153.5781,118.5,153.5781,130.5,165.5781,118.5,177.5781,118.5,177.5781,106.5,165.5781,118.5,153.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="92.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="109.6094"></line><polygon fill="#181818" points="38.5,99.6094,42.5,109.6094,46.5,99.6094,42.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="46.5" y="89.6128">condition 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="144.5" x2="160" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="62" y2="109.6094"></line><polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="164" y="89.6128">condition 2</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="106.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="96.5,161.5781,106.5,165.5781,96.5,169.5781,100.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="130.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="140.5,161.5781,130.5,165.5781,140.5,169.5781,136.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="118.5" y1="30" y2="50"></line><polygon fill="#181818" points="114.5,40,118.5,50,122.5,40,118.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "text": "hello",
        }
        with client:
            response = client.post(
                "/editArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
case (hello)
    :Activity;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_edit_arrow(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="84.3594"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="105.3281" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="91" x="126.5" y="159.8828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="67" x="140.5" y="180.8516" style="pointer-events: none;">2. activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="84.3594"></line><polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="259" x="176" y="51.3047">Nsmf_PDUSession_CreateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="105" x="176" y="64.1094">received from AMF</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="118.3281" y2="159.8828"></line><polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="82" x="176" y="139.6328">label on arrow</text>""",
            "svgelement": """<polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "text": "hello",
        }
        with client:
            response = client.post(
                "/editArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
->hello;
: 2. activity2;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_getarrowtext(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="84.3594"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="105.3281" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="91" x="126.5" y="159.8828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="67" x="140.5" y="180.8516" style="pointer-events: none;">2. activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="84.3594"></line><polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="259" x="176" y="51.3047">Nsmf_PDUSession_CreateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="105" x="176" y="64.1094">received from AMF</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="118.3281" y2="159.8828"></line><polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="82" x="176" y="139.6328">label on arrow</text>""",
            "svgelement": """<polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getArrowText",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = "label on arrow"
            assert response.data.decode("utf-8") == expected_result

    def test_deletearrow3(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="84.3594"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="105.3281" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="91" x="126.5" y="159.8828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="67" x="140.5" y="180.8516" style="pointer-events: none;">2. activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="84.3594"></line><polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="259" x="176" y="51.3047">Nsmf_PDUSession_CreateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="105" x="176" y="64.1094">received from AMF</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="118.3281" y2="159.8828"></line><polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="82" x="176" y="139.6328">label on arrow</text>""",
            "svgelement": """<polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request
received from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
: 2. activity2;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_deletearrow2(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
-> Nsmf_PDUSession_CreateSMContext Request\nreceived from AMF;
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="84.3594"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="105.3281" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="91" x="126.5" y="159.8828"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="67" x="140.5" y="180.8516" style="pointer-events: none;">2. activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="84.3594"></line><polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="259" x="176" y="51.3047">Nsmf_PDUSession_CreateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="105" x="176" y="64.1094">received from AMF</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="118.3281" y2="159.8828"></line><polygon fill="#181818" points="168,149.8828,172,159.8828,176,149.8828,172,153.8828" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="82" x="176" y="139.6328">label on arrow</text>""",
            "svgelement": """<polygon fill="#181818" points="168,74.3594,172,84.3594,176,74.3594,172,78.3594" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
: 1. Nsmf_PDUSession_CreateSMContext Request;
-> label on arrow;
: 2. activity2;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_deletearrow(self, client):
        test_data = {
            "plantuml": r"""@startuml
start
  ->Hej;
  :Activity;
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="71.5547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="92.5234" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="71.5547"></line><polygon fill="#181818" points="38.5,61.5547,42.5,71.5547,46.5,61.5547,42.5,65.5547" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="18" x="46.5" y="51.3047">Hej</text>""",
            "svgelement": """<polygon fill="#181818" points="38.5,61.5547,42.5,71.5547,46.5,61.5547,42.5,65.5547" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delArrow",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = r"""@startuml
start
  :Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result


class TestAppRoutesTitle:
    def test_edittitle_remove_title(self, client):
        test_data = {
            "plantuml": """@startuml
title
Placeholder Title
endtitle
:Activity 1;
@enduml""",
            "title": "",
        }
        with client:
            response = client.post(
                "/editTitle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_addtitle_there_already_is_one(self, client):
        test_data = {
            "plantuml": """@startuml
title
This is a title
endtitle
:Activity 1;
@enduml"""
        }
        with client:
            response = client.post(
                "/addTitle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
title
This is a title
endtitle
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_addtitle(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
@enduml"""
        }
        with client:
            response = client.post(
                "/addTitle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
title
Placeholder Title
endtitle
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_edittitle(self, client):
        test_data = {
            "plantuml": """@startuml
title
Placeholder Title
endtitle
:Activity 1;
@enduml""",
            "title": "Hej",
        }
        with client:
            response = client.post(
                "/editTitle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
title
Hej
endtitle
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_gettitleline(self, client):
        test_data = {
            "plantuml": """@startuml
title
Placeholder Title
Hello
endtitle
:Activity 1;
@enduml"""
        }
        with client:
            response = client.post(
                "/getTitleLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_result = [1, 4]

            # Assert the result value is as expected
            assert result_value == expected_result

    def test_deletetitle(self, client):
        test_data = {
            "plantuml": """@startuml
title
Placeholder Title
Hello
endtitle
:Activity 1;
@enduml"""
        }
        with client:
            response = client.post(
                "/deleteTitle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_gettitle(self, client):
        test_data = {
            "plantuml": """@startuml
title
Placeholder Title
Hello
endtitle
:Activity 1;
@enduml"""
        }
        with client:
            response = client.post(
                "/getTextTitle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """Placeholder Title
Hello"""
            assert response.data.decode("utf-8") == expected_result


class TestAppRoutesConnector:
    def test_get_char_connector(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
note left
note
end note
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/getCharConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected = "A"
            assert response.data.decode("utf-8") == expected

    def test_edit_colored_connector_with_colored_activity(self, client):
        test_data = {
            "plantuml": """@startuml
#yellow:Activity;
#green:(A)
note left
note
end note
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
            "text": "C",
        }
        with client:
            response = client.post(
                "/editCharConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
#yellow:Activity;
#green:(C)
note left
note
end note
detach
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_colored_connector(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
#green:(A)
note left
note
end note
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
            "text": "C",
        }
        with client:
            response = client.post(
                "/editCharConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
#green:(C)
note left
note
end note
detach
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_connector(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
note left
note
end note
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
            "text": "C",
        }
        with client:
            response = client.post(
                "/editCharConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
(C)
note left
note
end note
detach
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_while_connector(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
note left
note
end note
detach
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
            "where": "below",
            "type": "while",
        }
        with client:
            response = client.post(
                "/addToConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
(A)
note left
note
end note
detach
while (Statement) is (yes)
:Activity;
endwhile (no)
:Activity;
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_activity_connector2(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
note left
note
end note
detach
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
            "where": "below",
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
(A)
note left
note
end note
detach
:Activity 1;
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_notetoconnector(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
            "where": "below",
            "type": "note",
        }
        with client:
            response = client.post(
                "/addToConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
(A)
note right
note
end note
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_toggle_detach2(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
note right
note
end note
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/detachConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
(A)
note right
note
end note
detach
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_toggle_detach(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
detach
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/detachConnector",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
(A)
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteconnectorwithnote(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
note left
note
end note
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/connectorDelete",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteconnector(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
detach
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/connectorDelete",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
@endumll"""
            assert response.data.decode("utf-8") == expected_puml

    def test_get_connector_line(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
(A)
detach
@endumll""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,71.1406 L41,75.4844 L44.2188,75.4844 L42.6094,71.1406 Z M41.9375,69.9688 L43.2813,69.9688 L46.6094,78.7188 L45.375,78.7188 L44.5781,76.4688 L40.6406,76.4688 L39.8438,78.7188 L38.5938,78.7188 L41.9375,69.9688 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="38.5,54.9688,42.5,64.9688,46.5,54.9688,42.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="74.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/getConnectorLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = 3

            # Assert the result value is as expected
            assert result_value == expected_puml


class TestAppRoutesEllipse:
    def test_addconnectorbelowwithconnector(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
(A)
detach
stop
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="113.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,110.1406 L41,114.4844 L44.2188,114.4844 L42.6094,110.1406 Z M41.9375,108.9688 L43.2813,108.9688 L46.6094,117.7188 L45.375,117.7188 L44.5781,115.4688 L40.6406,115.4688 L39.8438,117.7188 L38.5938,117.7188 L41.9375,108.9688 Z " fill="#000000"></path><ellipse cx="42.5" cy="144.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="42.5" cy="144.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="83.9688" y2="103.9688"></line><polygon fill="#181818" points="38.5,93.9688,42.5,103.9688,46.5,93.9688,42.5,97.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="144.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse>""",
            "where": "below",
            "type": "connector",
        }
        with client:
            response = client.post(
                "/addToEllipse",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
:Activity;
(A)
detach
stop
(C)
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addactivitybelowwithconnector(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
(A)
detach
stop
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><ellipse cx="42.5" cy="113.9688" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,110.1406 L41,114.4844 L44.2188,114.4844 L42.6094,110.1406 Z M41.9375,108.9688 L43.2813,108.9688 L46.6094,117.7188 L45.375,117.7188 L44.5781,115.4688 L40.6406,115.4688 L39.8438,117.7188 L38.5938,117.7188 L41.9375,108.9688 Z " fill="#000000"></path><ellipse cx="42.5" cy="144.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="42.5" cy="144.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="83.9688" y2="103.9688"></line><polygon fill="#181818" points="38.5,93.9688,42.5,103.9688,46.5,93.9688,42.5,97.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="42.5" cy="144.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse>""",
            "where": "below",
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToEllipse",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
:Activity;
(A)
detach
stop
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteellipse(self, client):
        test_data = {
            "plantuml": """@startuml
start
stop
@enduml""",
            "svg": """<ellipse cx="24" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="24" cy="61" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="24" cy="61" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="30" y2="50"></line><polygon fill="#181818" points="20,40,24,50,28,40,24,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="24" cy="61" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/deleteEllipse",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_get_ellipse_line(self, client):
        test_data = {
            "plantuml": """@startuml
start
stop
@enduml""",
            "svg": """<ellipse cx="24" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="24" cy="61" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="24" cy="61" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="30" y2="50"></line><polygon fill="#181818" points="20,40,24,50,28,40,24,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<ellipse cx="24" cy="61" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse>""",
        }
        with client:
            response = client.post(
                "/getEllipseLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = 3

            # Assert the result value is as expected
            assert result_value == expected_puml


class TestAppRoutesNote:
    def test_togglenoteleft(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note left
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
        }
        with client:
            response = client.post(
                "/noteToggle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
note right
Hello
end note
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_togglenote(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
        }
        with client:
            response = client.post(
                "/noteToggle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
note left
Hello
end note
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_deletenote(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
        }
        with client:
            response = client.post(
                "/deleteNote",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_get_note_line(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
        }
        with client:
            response = client.post(
                "/getNoteLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
        response_json = json.loads(response.data.decode("utf-8"))
        result_value = response_json.get("result")

        # Expected value
        expected_puml = [3, 5]

        # Assert the result value is as expected
        assert result_value == expected_puml

    def test_editnote_empty(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
            "text": "",
        }
        with client:
            response = client.post(
                "/editNote",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def test_editnote(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
            "text": """Bom""",
        }
        with client:
            response = client.post(
                "/editNote",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = """@startuml
start
:Activity;
note right
Bom
end note
@enduml"""
            assert response.data.decode("utf-8") == expected_result

    def testgettextnote(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Activity;
note right
Hello
end note
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M137,54.418 L137,64.418 L147,64.418 L137,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="100" y="71.3008" style="pointer-events: none;">Hello</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="70.9688" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M94,54.418 L94,62.9844 L74,66.9844 L94,70.9844 L94,79.5508 A0,0 0 0 0 94,79.5508 L147,79.5508 A0,0 0 0 0 147,79.5508 L147,64.418 L137,54.418 L94,54.418 A0,0 0 0 0 94,54.418 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
        }
        with client:
            response = client.post(
                "/getNoteText",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = "Hello"
            assert response.data.decode("utf-8") == expected_result

    def testgettextnotebug(self, client):
        test_data = {
            "plantuml": """@startuml
title
This is the title of this diagram
endtitle
start
:Link to [[google.com Start]];
note right
start
end note
if (Statement) then (yes)
  :Activity;
while (While ?) is (yes)
  :Activity;
endwhile (no)
#red:Activity;
note left
end
end note
else (no)
  :Activity;
group group
if (Statement) then (yes)
  :Activity;
(C)
detach
else (no)
#lightgreen:Activity;
note right
hej
end note
fork
  :action;
stop
fork again
  :action;
fork again
  :action;
note right
action
end note
end merge
endif
end group
partition partition {
while (While ?) is (yes)
  :Activity;
endwhile (no)
(C)
note right
end
end note
}
endif
detach
@enduml
""",
            "svg": """<text fill="#000000" font-family="sans-serif" font-size="14" font-weight="bold" lengthAdjust="spacing" textLength="238" x="197" y="32.7969">This is the title of this diagram</text><ellipse cx="219.5" cy="57.2969" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><path d="M287.5,91.7148 L287.5,100.2813 L267.5,104.2813 L287.5,108.2813 L287.5,116.8477 A0,0 0 0 0 287.5,116.8477 L338.5,116.8477 A0,0 0 0 0 338.5,116.8477 L338.5,101.7148 L328.5,91.7148 L287.5,91.7148 A0,0 0 0 0 287.5,91.7148 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M328.5,91.7148 L328.5,101.7148 L338.5,101.7148 L328.5,91.7148 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="30" x="293.5" y="108.5977" style="pointer-events: none;">start</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="96" x="171.5" y="87.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="41" x="181.5" y="108.2656" style="pointer-events: none;">Link to</text><a href="google.com" target="_top" title="google.com" xlink:actuate="onRequest" xlink:href="google.com" xlink:show="new" xlink:title="google.com" xlink:type="simple"><text fill="#0000FF" font-family="sans-serif" font-size="12" lengthAdjust="spacing" text-decoration="underline" textLength="31" x="226.5" y="108.2656" style="pointer-events: none;">Start</text></a><polygon fill="#F1F1F1" points="190,141.2656,249,141.2656,261,153.2656,249,165.2656,190,165.2656,178,153.2656,190,141.2656" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="190" y="156.918" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="158" y="150.5156" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="261" y="150.5156" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="75" y="175.2656"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="85" y="196.2344" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="75" y="290.0391"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="85" y="311.0078" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="87,229.2344,126,229.2344,138,241.2344,126,253.2344,87,253.2344,75,241.2344,87,229.2344" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="110.5" y="263.2891" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="87" y="244.8867" style="pointer-events: none;">While ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="61" y="238.4844" style="pointer-events: none;">no</text><path d="M10,386.9336 L10,412.0664 A0,0 0 0 0 10,412.0664 L55,412.0664 A0,0 0 0 0 55,412.0664 L55,404.9336 L75,399.5 L55,396.9336 L55,396.9336 L45,386.9336 L10,386.9336 A0,0 0 0 0 10,386.9336 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M45,386.9336 L45,396.9336 L55,396.9336 L45,386.9336 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="24" x="16" y="403.8164" style="pointer-events: none;">end</text><rect fill="#FF0000" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="75" y="382.5156"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="85" y="403.4844" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="301" y="175.2656"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="311" y="196.2344" style="pointer-events: none;">Activity</text><rect fill="none" height="301.7422" style="stroke:#000000;stroke-width:1.5;" width="454" x="170" y="229.2344"></rect><path d="M221,229.2344 L221,238.5313 L211,248.5313 L170,248.5313 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="41" x="173" y="243.0313">group</text><polygon fill="#F1F1F1" points="303,265.5313,362,265.5313,374,277.5313,362,289.5313,303,289.5313,291,277.5313,303,265.5313" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="303" y="281.1836" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="271" y="274.7813" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="374" y="274.7813" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="190" y="299.5313"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="200" y="320.5" style="pointer-events: none;">Activity</text><ellipse cx="221.5" cy="378.0078" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M224.7344,374.4297 L224.7344,375.6797 Q224.125,375.1172 223.4531,374.8516 Q222.7813,374.5703 222.0156,374.5703 Q220.5156,374.5703 219.7188,375.4922 Q218.9219,376.4141 218.9219,378.1484 Q218.9219,379.8672 219.7188,380.7891 Q220.5156,381.7109 222.0156,381.7109 Q222.7813,381.7109 223.4531,381.4297 Q224.125,381.1484 224.7344,380.6016 L224.7344,381.8359 Q224.1094,382.2578 223.4063,382.4766 Q222.7188,382.6797 221.9531,382.6797 Q219.9531,382.6797 218.8125,381.4609 Q217.6719,380.2422 217.6719,378.1484 Q217.6719,376.0391 218.8125,374.8203 Q219.9531,373.6016 221.9531,373.6016 Q222.7344,373.6016 223.4219,373.8203 Q224.125,374.0234 224.7344,374.4297 Z " fill="#000000" style="pointer-events: none;"></path><path d="M495,303.9492 L495,312.5156 L475,316.5156 L495,320.5156 L495,329.082 A0,0 0 0 0 495,329.082 L535,329.082 A0,0 0 0 0 535,329.082 L535,313.9492 L525,303.9492 L495,303.9492 A0,0 0 0 0 495,303.9492 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M525,303.9492 L525,313.9492 L535,313.9492 L525,303.9492 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="19" x="501" y="320.832" style="pointer-events: none;">hej</text><rect fill="#90EE90" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="412" y="299.5313"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="422" y="320.5" style="pointer-events: none;">Activity</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="339" x="273" y="368.0078"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="287" y="394.0078"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="297" y="414.9766" style="pointer-events: none;">action</text><ellipse cx="316.5" cy="473.9766" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="316.5" cy="473.9766" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="374" y="422.5078"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="384" y="443.4766" style="pointer-events: none;">action</text><path d="M540,426.9258 L540,435.4922 L520,439.4922 L540,443.4922 L540,452.0586 A0,0 0 0 0 540,452.0586 L600,452.0586 A0,0 0 0 0 600,452.0586 L600,436.9258 L590,426.9258 L540,426.9258 A0,0 0 0 0 540,426.9258 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M590,426.9258 L590,436.9258 L600,436.9258 L590,426.9258 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="39" x="546" y="443.8086" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="461" y="422.5078"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="471" y="443.4766" style="pointer-events: none;">action</text><polygon fill="#F1F1F1" points="443.5,494.9766,455.5,506.9766,443.5,518.9766,431.5,506.9766,443.5,494.9766" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="none" height="202.3867" style="stroke:#000000;stroke-width:1.5;" width="150.5" x="267" y="540.9766"></rect><path d="M333,540.9766 L333,550.2734 L323,560.2734 L267,560.2734 " fill="none" style="stroke:#000000;stroke-width:1.5;"></path><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="56" x="270" y="554.7734">partition</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="301" y="632.8281"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="311" y="653.7969" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="313,577.2734,352,577.2734,364,589.2734,352,601.2734,313,601.2734,301,589.2734,313,577.2734" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="336.5" y="611.3281" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="313" y="592.9258" style="pointer-events: none;">While ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="287" y="586.5234" style="pointer-events: none;">no</text><path d="M362.5,706.2305 L362.5,714.7969 L342.5,718.7969 L362.5,722.7969 L362.5,731.3633 A0,0 0 0 0 362.5,731.3633 L407.5,731.3633 A0,0 0 0 0 407.5,731.3633 L407.5,716.2305 L397.5,706.2305 L362.5,706.2305 A0,0 0 0 0 362.5,706.2305 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M397.5,706.2305 L397.5,716.2305 L407.5,716.2305 L397.5,706.2305 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="24" x="368.5" y="723.1133" style="pointer-events: none;">end</text><ellipse cx="332.5" cy="718.7969" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M335.7344,715.2188 L335.7344,716.4688 Q335.125,715.9063 334.4531,715.6406 Q333.7813,715.3594 333.0156,715.3594 Q331.5156,715.3594 330.7188,716.2813 Q329.9219,717.2031 329.9219,718.9375 Q329.9219,720.6563 330.7188,721.5781 Q331.5156,722.5 333.0156,722.5 Q333.7813,722.5 334.4531,722.2188 Q335.125,721.9375 335.7344,721.3906 L335.7344,722.625 Q335.1094,723.0469 334.4063,723.2656 Q333.7188,723.4688 332.9531,723.4688 Q330.9531,723.4688 329.8125,722.25 Q328.6719,721.0313 328.6719,718.9375 Q328.6719,716.8281 329.8125,715.6094 Q330.9531,714.3906 332.9531,714.3906 Q333.7344,714.3906 334.4219,714.6094 Q335.125,714.8125 335.7344,715.2188 Z " fill="#000000" style="pointer-events: none;"></path><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="219.5" x2="219.5" y1="67.2969" y2="87.2969"></line><polygon fill="#181818" points="215.5,77.2969,219.5,87.2969,223.5,77.2969,219.5,81.2969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106.5" x2="106.5" y1="253.2344" y2="290.0391"></line><polygon fill="#181818" points="102.5,280.0391,106.5,290.0391,110.5,280.0391,106.5,284.0391" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106.5" x2="106.5" y1="324.0078" y2="336.0078"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106.5" x2="150" y1="336.0078" y2="336.0078"></line><polygon fill="#181818" points="146,298.6211,150,288.6211,154,298.6211,150,294.6211" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="150" x2="150" y1="241.2344" y2="336.0078"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="150" x2="138" y1="241.2344" y2="241.2344"></line><polygon fill="#181818" points="148,237.2344,138,241.2344,148,245.2344,144,241.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="75" x2="63" y1="241.2344" y2="241.2344"></line><polygon fill="#181818" points="59,284.6211,63,294.6211,67,284.6211,63,288.6211" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="63" x2="63" y1="241.2344" y2="348.0078"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="63" x2="106.5" y1="348.0078" y2="348.0078"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106.5" x2="106.5" y1="348.0078" y2="382.5156"></line><polygon fill="#181818" points="102.5,372.5156,106.5,382.5156,110.5,372.5156,106.5,376.5156" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106.5" x2="106.5" y1="209.2344" y2="229.2344"></line><polygon fill="#181818" points="102.5,219.2344,106.5,229.2344,110.5,219.2344,106.5,223.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="221.5" x2="221.5" y1="333.5" y2="368.0078"></line><polygon fill="#181818" points="217.5,358.0078,221.5,368.0078,225.5,358.0078,221.5,362.0078" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="316.5" x2="316.5" y1="427.9766" y2="462.9766"></line><polygon fill="#181818" points="312.5,452.9766,316.5,462.9766,320.5,452.9766,316.5,456.9766" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="316.5" x2="316.5" y1="374.0078" y2="394.0078"></line><polygon fill="#181818" points="312.5,384.0078,316.5,394.0078,320.5,384.0078,316.5,388.0078" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="403.5" x2="403.5" y1="374.0078" y2="422.5078"></line><polygon fill="#181818" points="399.5,412.5078,403.5,422.5078,407.5,412.5078,403.5,416.5078" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="490.5" x2="490.5" y1="374.0078" y2="422.5078"></line><polygon fill="#181818" points="486.5,412.5078,490.5,422.5078,494.5,412.5078,490.5,416.5078" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="403.5" x2="403.5" y1="456.4766" y2="506.9766"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="403.5" x2="431.5" y1="506.9766" y2="506.9766"></line><polygon fill="#181818" points="421.5,502.9766,431.5,506.9766,421.5,510.9766,425.5,506.9766" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="490.5" x2="490.5" y1="456.4766" y2="506.9766"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="490.5" x2="455.5" y1="506.9766" y2="506.9766"></line><polygon fill="#181818" points="465.5,502.9766,455.5,506.9766,465.5,510.9766,461.5,506.9766" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="443.5" x2="443.5" y1="333.5" y2="368.0078"></line><polygon fill="#181818" points="439.5,358.0078,443.5,368.0078,447.5,358.0078,443.5,362.0078" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="291" x2="221.5" y1="277.5313" y2="277.5313"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="221.5" x2="221.5" y1="277.5313" y2="299.5313"></line><polygon fill="#181818" points="217.5,289.5313,221.5,299.5313,225.5,289.5313,221.5,293.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="374" x2="443.5" y1="277.5313" y2="277.5313"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="443.5" x2="443.5" y1="277.5313" y2="299.5313"></line><polygon fill="#181818" points="439.5,289.5313,443.5,299.5313,447.5,289.5313,443.5,293.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="443.5" x2="443.5" y1="518.9766" y2="523.9766"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="443.5" x2="332.5" y1="523.9766" y2="523.9766"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="332.5" y1="523.9766" y2="577.2734"></line><polygon fill="#181818" points="328.5,567.2734,332.5,577.2734,336.5,567.2734,332.5,571.2734" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="332.5" y1="209.2344" y2="265.5313"></line><polygon fill="#181818" points="328.5,255.5313,332.5,265.5313,336.5,255.5313,332.5,259.5313" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="332.5" y1="601.2734" y2="632.8281"></line><polygon fill="#181818" points="328.5,622.8281,332.5,632.8281,336.5,622.8281,332.5,626.8281" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="332.5" y1="666.7969" y2="676.7969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="376" y1="676.7969" y2="676.7969"></line><polygon fill="#181818" points="372,641.4102,376,631.4102,380,641.4102,376,637.4102" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="376" x2="376" y1="589.2734" y2="676.7969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="376" x2="364" y1="589.2734" y2="589.2734"></line><polygon fill="#181818" points="374,585.2734,364,589.2734,374,593.2734,370,589.2734" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="301" x2="289" y1="589.2734" y2="589.2734"></line><polygon fill="#181818" points="285,627.4102,289,637.4102,293,627.4102,289,631.4102" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="289" x2="289" y1="589.2734" y2="688.7969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="289" x2="332.5" y1="688.7969" y2="688.7969"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="332.5" y1="688.7969" y2="708.7969"></line><polygon fill="#181818" points="328.5,698.7969,332.5,708.7969,336.5,698.7969,332.5,702.7969" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="178" x2="106.5" y1="153.2656" y2="153.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="106.5" x2="106.5" y1="153.2656" y2="175.2656"></line><polygon fill="#181818" points="102.5,165.2656,106.5,175.2656,110.5,165.2656,106.5,169.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="261" x2="332.5" y1="153.2656" y2="153.2656"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="332.5" x2="332.5" y1="153.2656" y2="175.2656"></line><polygon fill="#181818" points="328.5,165.2656,332.5,175.2656,336.5,165.2656,332.5,169.2656" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="219.5" x2="219.5" y1="121.2656" y2="141.2656"></line><polygon fill="#181818" points="215.5,131.2656,219.5,141.2656,223.5,131.2656,219.5,135.2656" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<path d="M495,303.9492 L495,312.5156 L475,316.5156 L495,320.5156 L495,329.082 A0,0 0 0 0 495,329.082 L535,329.082 A0,0 0 0 0 535,329.082 L535,313.9492 L525,303.9492 L495,303.9492 A0,0 0 0 0 495,303.9492 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path>""",
        }
        with client:
            response = client.post(
                "/getNoteText",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = "hej"
            assert response.data.decode("utf-8") == expected_result


class TestAppRoutesSwitch:
    def test_gettext_switch(self, client):
        test_data = {
            "plantuml": """@startuml
switch (asdfasdfasdf)
case ( condition A )
:Text 1;
switch (hej)
case ( condition A )
:Text 1;
case ( condition B )
:Text 2;
case ( condition C )
:Text 3;
endswitch
case ( condition B )
:Text 2;
case ( condition C )
:Text 3;
endswitch
@enduml""",
            "svg": """<polygon fill="#F1F1F1" points="253,10,328,10,340,22,328,34,253,34,241,22,253,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="75" x="253" y="25.8081" style="pointer-events: none;">asdfasdfasdf</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="141.5" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="151.5" y="90.748" style="pointer-events: none;">Text 1</text><polygon fill="#F1F1F1" points="158.5,123.5781,182.5,123.5781,194.5,135.5781,182.5,147.5781,158.5,147.5781,146.5,135.5781,158.5,123.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="162" y="139.3862" style="pointer-events: none;">hej</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="11" y="183.1875"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="21" y="204.3262" style="pointer-events: none;">Text 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="120" y="183.1875"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="130" y="204.3262" style="pointer-events: none;">Text 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="240" y="183.1875"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="250" y="204.3262" style="pointer-events: none;">Text 3</text><polygon fill="#F1F1F1" points="170.5,237.1563,170.5,237.1563,182.5,249.1563,170.5,261.1563,170.5,261.1563,158.5,249.1563,170.5,237.1563" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="350" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="360" y="90.748" style="pointer-events: none;">Text 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="460" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="470" y="90.748" style="pointer-events: none;">Text 3</text><polygon fill="#F1F1F1" points="290.5,271.1563,290.5,271.1563,302.5,283.1563,290.5,295.1563,290.5,295.1563,278.5,283.1563,290.5,271.1563" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="146.5" x2="40" y1="135.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="40" y1="135.5781" y2="183.1875"></line><polygon fill="#181818" points="36,173.1875,40,183.1875,44,173.1875,40,177.1875" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="44" y="163.1909">condition A</text><line style="stroke:#181818;stroke-width:1.0;" x1="194.5" x2="269" y1="135.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="135.5781" y2="183.1875"></line><polygon fill="#181818" points="265,173.1875,269,183.1875,273,173.1875,269,177.1875" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="273" y="163.1909">condition C</text><line style="stroke:#181818;stroke-width:1.0;" x1="170.5" x2="170.5" y1="147.5781" y2="159.4479"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="149" y1="159.4479" y2="159.4479"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="159.4479" y2="183.1875"></line><polygon fill="#181818" points="145,173.1875,149,183.1875,153,173.1875,149,177.1875" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="153" y="164.1909">condition B</text><line style="stroke:#181818;stroke-width:1.0;" x1="40" x2="40" y1="217.1563" y2="249.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="158.5" y1="249.1563" y2="249.1563"></line><polygon fill="#181818" points="148.5,245.1563,158.5,249.1563,148.5,253.1563,152.5,249.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="217.1563" y2="249.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="182.5" y1="249.1563" y2="249.1563"></line><polygon fill="#181818" points="192.5,245.1563,182.5,249.1563,192.5,253.1563,188.5,249.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="217.1563" y2="222.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="170.5" y1="222.1563" y2="222.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="170.5" y1="222.1563" y2="237.1563"></line><polygon fill="#181818" points="166.5,227.1563,170.5,237.1563,174.5,227.1563,170.5,231.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="170.5" y1="103.5781" y2="123.5781"></line><polygon fill="#181818" points="166.5,113.5781,170.5,123.5781,174.5,113.5781,170.5,117.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="241" x2="170.5" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="170.5" y1="22" y2="69.6094"></line><polygon fill="#181818" points="166.5,59.6094,170.5,69.6094,174.5,59.6094,170.5,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="174.5" y="49.6128">condition A</text><line style="stroke:#181818;stroke-width:1.0;" x1="340" x2="489" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="489" x2="489" y1="22" y2="69.6094"></line><polygon fill="#181818" points="485,59.6094,489,69.6094,493,59.6094,489,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="493" y="49.6128">condition C</text><line style="stroke:#181818;stroke-width:1.0;" x1="379" x2="379" y1="22" y2="69.6094"></line><polygon fill="#181818" points="375,59.6094,379,69.6094,383,59.6094,379,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="383" y="44.6128">condition B</text><line style="stroke:#181818;stroke-width:1.0;" x1="170.5" x2="170.5" y1="261.1563" y2="283.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="278.5" y1="283.1563" y2="283.1563"></line><polygon fill="#181818" points="268.5,279.1563,278.5,283.1563,268.5,287.1563,272.5,283.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="489" x2="489" y1="103.5781" y2="283.1563"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="489" x2="302.5" y1="283.1563" y2="283.1563"></line><polygon fill="#181818" points="312.5,279.1563,302.5,283.1563,312.5,287.1563,308.5,283.1563" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="379" x2="379" y1="103.5781" y2="283.1563"></line><polygon fill="#181818" points="375,273.1563,379,283.1563,383,273.1563,379,277.1563" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="253,10,328,10,340,22,328,34,253,34,241,22,253,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getTextPoly",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            output = ["asdfasdfasdf", "", ""]
            json.loads(response.data.decode("utf-8")) == output

    def test_switch_again2(self, client):
        test_data = {
            "plantuml": """@startuml
switch (test?)
case ( condition A)
:Text 1;
case ( condition B)
:Text 2;
case ( condition 2)
:Text 3;
endswitch
@enduml""",
            "svg": """<polygon fill="#F1F1F1" points="156.5,10,184.5,10,196.5,22,184.5,34,156.5,34,144.5,22,156.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="156.5" y="25.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="11" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="21" y="90.748" style="pointer-events: none;">Text 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="120" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="130" y="90.748" style="pointer-events: none;">Text 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="230" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="240" y="90.748" style="pointer-events: none;">Text 3</text><polygon fill="#F1F1F1" points="170.5,123.5781,170.5,123.5781,182.5,135.5781,170.5,147.5781,170.5,147.5781,158.5,135.5781,170.5,123.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="144.5" x2="40" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="40" y1="22" y2="69.6094"></line><polygon fill="#181818" points="36,59.6094,40,69.6094,44,59.6094,40,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="44" y="49.6128">condition A</text><line style="stroke:#181818;stroke-width:1.0;" x1="196.5" x2="259" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="259" y1="22" y2="69.6094"></line><polygon fill="#181818" points="255,59.6094,259,69.6094,263,59.6094,259,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="263" y="49.6128">condition C</text><line style="stroke:#181818;stroke-width:1.0;" x1="170.5" x2="170.5" y1="34" y2="45.8698"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="149" y1="45.8698" y2="45.8698"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="45.8698" y2="69.6094"></line><polygon fill="#181818" points="145,59.6094,149,69.6094,153,59.6094,149,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="153" y="50.6128">condition B</text><line style="stroke:#181818;stroke-width:1.0;" x1="40" x2="40" y1="103.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="158.5" y1="135.5781" y2="135.5781"></line><polygon fill="#181818" points="148.5,131.5781,158.5,135.5781,148.5,139.5781,152.5,135.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="259" y1="103.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="182.5" y1="135.5781" y2="135.5781"></line><polygon fill="#181818" points="192.5,131.5781,182.5,135.5781,192.5,139.5781,188.5,135.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="103.5781" y2="108.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="170.5" y1="108.5781" y2="108.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="170.5" y1="108.5781" y2="123.5781"></line><polygon fill="#181818" points="166.5,113.5781,170.5,123.5781,174.5,113.5781,170.5,117.5781" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="156.5,10,184.5,10,196.5,22,184.5,34,156.5,34,144.5,22,156.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/switchAgain",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
switch (test?)
case ( condition A)
:Text 1;
case ( condition B)
:Text 2;
case ( condition 2)
:Text 3;
case ( condition 3)
:Activity;
endswitch
@enduml"""

            assert response.data.decode("utf-8") == expected_puml

    def test_switch_again(self, client):
        test_data = {
            "plantuml": """@startuml
switch (test?)
case ( condition A )
:Text 1;
case ( condition B )
:Text 2;
case ( condition C )
:Text 3;
endswitch
@enduml""",
            "svg": """<polygon fill="#F1F1F1" points="156.5,10,184.5,10,196.5,22,184.5,34,156.5,34,144.5,22,156.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="156.5" y="25.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="11" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="21" y="90.748" style="pointer-events: none;">Text 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="120" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="130" y="90.748" style="pointer-events: none;">Text 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="230" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="240" y="90.748" style="pointer-events: none;">Text 3</text><polygon fill="#F1F1F1" points="170.5,123.5781,170.5,123.5781,182.5,135.5781,170.5,147.5781,170.5,147.5781,158.5,135.5781,170.5,123.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="144.5" x2="40" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="40" y1="22" y2="69.6094"></line><polygon fill="#181818" points="36,59.6094,40,69.6094,44,59.6094,40,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="44" y="49.6128">condition A</text><line style="stroke:#181818;stroke-width:1.0;" x1="196.5" x2="259" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="259" y1="22" y2="69.6094"></line><polygon fill="#181818" points="255,59.6094,259,69.6094,263,59.6094,259,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="263" y="49.6128">condition C</text><line style="stroke:#181818;stroke-width:1.0;" x1="170.5" x2="170.5" y1="34" y2="45.8698"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="149" y1="45.8698" y2="45.8698"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="45.8698" y2="69.6094"></line><polygon fill="#181818" points="145,59.6094,149,69.6094,153,59.6094,149,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="153" y="50.6128">condition B</text><line style="stroke:#181818;stroke-width:1.0;" x1="40" x2="40" y1="103.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="158.5" y1="135.5781" y2="135.5781"></line><polygon fill="#181818" points="148.5,131.5781,158.5,135.5781,148.5,139.5781,152.5,135.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="259" y1="103.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="182.5" y1="135.5781" y2="135.5781"></line><polygon fill="#181818" points="192.5,131.5781,182.5,135.5781,192.5,139.5781,188.5,135.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="103.5781" y2="108.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="170.5" y1="108.5781" y2="108.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="170.5" y1="108.5781" y2="123.5781"></line><polygon fill="#181818" points="166.5,113.5781,170.5,123.5781,174.5,113.5781,170.5,117.5781" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="156.5,10,184.5,10,196.5,22,184.5,34,156.5,34,144.5,22,156.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/switchAgain",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
switch (test?)
case ( condition A )
:Text 1;
case ( condition B )
:Text 2;
case ( condition C )
:Text 3;
case ( condition 1)
:Activity;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_switch1(self, client):
        test_data = {
            "plantuml": """@startuml
switch (test?)
case ( condition A )
:Text 1;
case ( condition B )
:Text 2;
case ( condition C )
:Text 3;
endswitch
@enduml""",
            "svg": """<polygon fill="#F1F1F1" points="156.5,10,184.5,10,196.5,22,184.5,34,156.5,34,144.5,22,156.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="156.5" y="25.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="11" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="21" y="90.748" style="pointer-events: none;">Text 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="120" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="130" y="90.748" style="pointer-events: none;">Text 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="58" x="230" y="69.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="38" x="240" y="90.748" style="pointer-events: none;">Text 3</text><polygon fill="#F1F1F1" points="170.5,123.5781,170.5,123.5781,182.5,135.5781,170.5,147.5781,170.5,147.5781,158.5,135.5781,170.5,123.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="144.5" x2="40" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="40" y1="22" y2="69.6094"></line><polygon fill="#181818" points="36,59.6094,40,69.6094,44,59.6094,40,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="44" y="49.6128">condition A</text><line style="stroke:#181818;stroke-width:1.0;" x1="196.5" x2="259" y1="22" y2="22"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="259" y1="22" y2="69.6094"></line><polygon fill="#181818" points="255,59.6094,259,69.6094,263,59.6094,259,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="263" y="49.6128">condition C</text><line style="stroke:#181818;stroke-width:1.0;" x1="170.5" x2="170.5" y1="34" y2="45.8698"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="149" y1="45.8698" y2="45.8698"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="45.8698" y2="69.6094"></line><polygon fill="#181818" points="145,59.6094,149,69.6094,153,59.6094,149,63.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="63" x="153" y="50.6128">condition B</text><line style="stroke:#181818;stroke-width:1.0;" x1="40" x2="40" y1="103.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="40" x2="158.5" y1="135.5781" y2="135.5781"></line><polygon fill="#181818" points="148.5,131.5781,158.5,135.5781,148.5,139.5781,152.5,135.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="259" y1="103.5781" y2="135.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="259" x2="182.5" y1="135.5781" y2="135.5781"></line><polygon fill="#181818" points="192.5,131.5781,182.5,135.5781,192.5,139.5781,188.5,135.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="149" y1="103.5781" y2="108.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="149" x2="170.5" y1="108.5781" y2="108.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="170.5" x2="170.5" y1="108.5781" y2="123.5781"></line><polygon fill="#181818" points="166.5,113.5781,170.5,123.5781,174.5,113.5781,170.5,117.5781" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "State",
            "branch1": "bam",
            "branch2": "bom",
            "svgelement": """<polygon fill="#F1F1F1" points="156.5,10,184.5,10,196.5,22,184.5,34,156.5,34,144.5,22,156.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
switch (State)
case ( condition A )
:Text 1;
case ( condition B )
:Text 2;
case ( condition C )
:Text 3;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_puml


class TestAppRoutesRepeatWhile:
    def test_checkrepeathasbackward2(self, client):
        test_data = {
            "plantuml": """@startuml
repeat
  :Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="54"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="74.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,10,63.5,22,51.5,34,39.5,22,51.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="142.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="123.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="117.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="163.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="184.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="34" y2="54"></line><polygon fill="#181818" points="47.5,44,51.5,54,55.5,44,51.5,48" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="95" y1="119.9688" y2="119.9688"></line><polygon fill="#181818" points="91,80.9844,95,70.9844,99,80.9844,95,76.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="95" y1="22" y2="119.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="63.5" y1="22" y2="22"></line><polygon fill="#181818" points="73.5,18,63.5,22,73.5,26,69.5,22" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="87.9688" y2="107.9688"></line><polygon fill="#181818" points="47.5,97.9688,51.5,107.9688,55.5,97.9688,51.5,101.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="131.9688" y2="163.5234"></line><polygon fill="#181818" points="47.5,153.5234,51.5,163.5234,55.5,153.5234,51.5,157.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/checkIfRepeatHasBackward",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """empty"""
            assert response.data.decode("utf-8") == expected_puml

    def test_checkrepeathasbackward(self, client):
        test_data = {
            "plantuml": """@startuml
repeat
  :Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="54"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="74.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,10,63.5,22,51.5,34,39.5,22,51.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="142.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="123.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="117.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="163.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="184.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="34" y2="54"></line><polygon fill="#181818" points="47.5,44,51.5,54,55.5,44,51.5,48" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="95" y1="119.9688" y2="119.9688"></line><polygon fill="#181818" points="91,80.9844,95,70.9844,99,80.9844,95,76.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="95" y1="22" y2="119.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="63.5" y1="22" y2="22"></line><polygon fill="#181818" points="73.5,18,63.5,22,73.5,26,69.5,22" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="87.9688" y2="107.9688"></line><polygon fill="#181818" points="47.5,97.9688,51.5,107.9688,55.5,97.9688,51.5,101.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="131.9688" y2="163.5234"></line><polygon fill="#181818" points="47.5,153.5234,51.5,163.5234,55.5,153.5234,51.5,157.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/checkIfRepeatHasBackward",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """backward"""
            assert response.data.decode("utf-8") == expected_puml

    def test_checkrepeat(self, client):
        test_data = {
            "plantuml": """@startuml
repeat
  :Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="54"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="74.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,10,63.5,22,51.5,34,39.5,22,51.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="142.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="123.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="117.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="163.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="184.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="34" y2="54"></line><polygon fill="#181818" points="47.5,44,51.5,54,55.5,44,51.5,48" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="95" y1="119.9688" y2="119.9688"></line><polygon fill="#181818" points="91,80.9844,95,70.9844,99,80.9844,95,76.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="95" y1="22" y2="119.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="63.5" y1="22" y2="22"></line><polygon fill="#181818" points="73.5,18,63.5,22,73.5,26,69.5,22" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="87.9688" y2="107.9688"></line><polygon fill="#181818" points="47.5,97.9688,51.5,107.9688,55.5,97.9688,51.5,101.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="131.9688" y2="163.5234"></line><polygon fill="#181818" points="47.5,153.5234,51.5,163.5234,55.5,153.5234,51.5,157.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/checkWhatPoly",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """repeat"""
            assert response.data.decode("utf-8") == expected_puml

    def test_gettext_repeatwhile(self, client):
        test_data = {
            "plantuml": """@startuml
repeat
  :Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="54"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="74.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,10,63.5,22,51.5,34,39.5,22,51.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="142.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="123.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="117.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="163.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="184.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="34" y2="54"></line><polygon fill="#181818" points="47.5,44,51.5,54,55.5,44,51.5,48" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="95" y1="119.9688" y2="119.9688"></line><polygon fill="#181818" points="91,80.9844,95,70.9844,99,80.9844,95,76.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="95" y1="22" y2="119.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="63.5" y1="22" y2="22"></line><polygon fill="#181818" points="73.5,18,63.5,22,73.5,26,69.5,22" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="87.9688" y2="107.9688"></line><polygon fill="#181818" points="47.5,97.9688,51.5,107.9688,55.5,97.9688,51.5,101.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="131.9688" y2="163.5234"></line><polygon fill="#181818" points="47.5,153.5234,51.5,163.5234,55.5,153.5234,51.5,157.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getTextPoly",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            output = ["while ?", "no", "yes"]
            json.loads(response.data.decode("utf-8")) == output

    def test_add_backwards_already_exists(self, client):
        test_data = {
            "plantuml": """@startuml
repeat
  :Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="54"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="74.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,10,63.5,22,51.5,34,39.5,22,51.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="142.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="123.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="117.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="163.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="184.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="34" y2="54"></line><polygon fill="#181818" points="47.5,44,51.5,54,55.5,44,51.5,48" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="95" y1="119.9688" y2="119.9688"></line><polygon fill="#181818" points="91,80.9844,95,70.9844,99,80.9844,95,76.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="95" y1="22" y2="119.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="63.5" y1="22" y2="22"></line><polygon fill="#181818" points="73.5,18,63.5,22,73.5,26,69.5,22" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="87.9688" y2="107.9688"></line><polygon fill="#181818" points="47.5,97.9688,51.5,107.9688,55.5,97.9688,51.5,101.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="131.9688" y2="163.5234"></line><polygon fill="#181818" points="47.5,153.5234,51.5,163.5234,55.5,153.5234,51.5,157.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/addBackwards",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
repeat
  :Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_backwards(self, client):
        test_data = {
            "plantuml": """@startuml
repeat
  :Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="54"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="74.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,10,63.5,22,51.5,34,39.5,22,51.5,10" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="142.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="123.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="117.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="163.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="184.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="34" y2="54"></line><polygon fill="#181818" points="47.5,44,51.5,54,55.5,44,51.5,48" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="95" y1="119.9688" y2="119.9688"></line><polygon fill="#181818" points="91,80.9844,95,70.9844,99,80.9844,95,76.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="95" y1="22" y2="119.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="95" x2="63.5" y1="22" y2="22"></line><polygon fill="#181818" points="73.5,18,63.5,22,73.5,26,69.5,22" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="87.9688" y2="107.9688"></line><polygon fill="#181818" points="47.5,97.9688,51.5,107.9688,55.5,97.9688,51.5,101.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="131.9688" y2="163.5234"></line><polygon fill="#181818" points="47.5,153.5234,51.5,163.5234,55.5,153.5234,51.5,157.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,107.9688,71,107.9688,83,119.9688,71,131.9688,32,131.9688,20,119.9688,32,107.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/addBackwards",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
repeat
  :Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_repeat_while(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
  :b;
  :b;
  repeat
  :aa;
  :aa;
repeat while (a) is (a) not (a)
repeat while (b) is (b) not (b)
@enduml""",
            "svg": """<ellipse cx="44" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="30" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="40" y="114.9688" style="pointer-events: none;">b</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="30" y="147.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="40" y="168.9375" style="pointer-events: none;">b</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="36" x="26" y="253.4375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="16" x="36" y="274.4063" style="pointer-events: none;">aa</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="36" x="26" y="314.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="16" x="36" y="335.875" style="pointer-events: none;">aa</text><polygon fill="#F1F1F1" points="44,201.9375,56,213.9375,44,225.9375,32,213.9375,44,201.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,368.875,56,368.875,68,380.875,56,392.875,32,392.875,20,380.875,32,368.875" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="48" y="402.9297" style="pointer-events: none;">a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="40.5" y="384.5273" style="pointer-events: none;">a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="68" y="378.125" style="pointer-events: none;">a</text><polygon fill="#F1F1F1" points="44,50,56,62,44,74,32,62,44,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,424.4297,56,424.4297,68,436.4297,56,448.4297,32,448.4297,20,436.4297,32,424.4297" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="48" y="458.4844" style="pointer-events: none;">b</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="40.5" y="440.082" style="pointer-events: none;">b</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="68" y="433.6797" style="pointer-events: none;">b</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="127.9688" y2="147.9688"></line><polygon fill="#181818" points="40,137.9688,44,147.9688,48,137.9688,44,141.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="287.4063" y2="314.9063"></line><polygon fill="#181818" points="40,304.9063,44,314.9063,48,304.9063,44,308.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="225.9375" y2="253.4375"></line><polygon fill="#181818" points="40,243.4375,44,253.4375,48,243.4375,44,247.4375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="68" x2="80" y1="380.875" y2="380.875"></line><polygon fill="#181818" points="76,307.4063,80,297.4063,84,307.4063,80,303.4063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="80" x2="80" y1="213.9375" y2="380.875"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="80" x2="56" y1="213.9375" y2="213.9375"></line><polygon fill="#181818" points="66,209.9375,56,213.9375,66,217.9375,62,213.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="348.875" y2="368.875"></line><polygon fill="#181818" points="40,358.875,44,368.875,48,358.875,44,362.875" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="181.9375" y2="201.9375"></line><polygon fill="#181818" points="40,191.9375,44,201.9375,48,191.9375,44,195.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="74" y2="94"></line><polygon fill="#181818" points="40,84,44,94,48,84,44,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="68" x2="98" y1="436.4297" y2="436.4297"></line><polygon fill="#181818" points="94,245.9375,98,235.9375,102,245.9375,98,241.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="98" x2="98" y1="62" y2="436.4297"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="98" x2="56" y1="62" y2="62"></line><polygon fill="#181818" points="66,58,56,62,66,66,62,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="392.875" y2="424.4297"></line><polygon fill="#181818" points="40,414.4297,44,424.4297,48,414.4297,44,418.4297" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="30" y2="50"></line><polygon fill="#181818" points="40,40,44,50,48,40,44,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,424.4297,56,424.4297,68,436.4297,56,448.4297,32,448.4297,20,436.4297,32,424.4297" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "where": "right",
            "type": "fork",
        }
        with client:
            response = client.post(
                "/addToIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
  :b;
  :b;
  repeat
  :aa;
  :aa;
repeat while (a) is (a) not (a)
repeat while (b) is (b) not (b)
fork
:action;
fork again
:action;
end fork
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_repeatwhile4(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
:activity;
repeat while (hej) is (yes) not (no)
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="114.9688" style="pointer-events: none;">activity</text><polygon fill="#F1F1F1" points="94,50,106,62,94,74,82,62,94,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="82,147.9688,106,147.9688,118,159.9688,106,171.9688,82,171.9688,70,159.9688,82,147.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="182.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="85.5" y="163.6211" style="pointer-events: none;">hej</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="118" y="157.2188" style="pointer-events: none;">yes</text><polygon fill="#F1F1F1" points="64.5,203.5234,123.5,203.5234,135.5,215.5234,123.5,227.5234,64.5,227.5234,52.5,215.5234,64.5,203.5234" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="219.1758" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="212.7734" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="212.7734" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="237.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="258.4922" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="237.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="258.4922" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,277.4922,106,289.4922,94,301.4922,82,289.4922,94,277.4922" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="94"></line><polygon fill="#181818" points="90,84,94,94,98,84,94,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118" x2="137.5" y1="159.9688" y2="159.9688"></line><polygon fill="#181818" points="133.5,120.9844,137.5,110.9844,141.5,120.9844,137.5,116.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="137.5" x2="137.5" y1="62" y2="159.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="137.5" x2="106" y1="62" y2="62"></line><polygon fill="#181818" points="116,58,106,62,116,66,112,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="127.9688" y2="147.9688"></line><polygon fill="#181818" points="90,137.9688,94,147.9688,98,137.9688,94,141.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="215.5234" y2="215.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="215.5234" y2="237.5234"></line><polygon fill="#181818" points="38.5,227.5234,42.5,237.5234,46.5,227.5234,42.5,231.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="215.5234" y2="215.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="215.5234" y2="237.5234"></line><polygon fill="#181818" points="141.5,227.5234,145.5,237.5234,149.5,227.5234,145.5,231.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="271.4922" y2="289.4922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="289.4922" y2="289.4922"></line><polygon fill="#181818" points="72,285.4922,82,289.4922,72,293.4922,76,289.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="271.4922" y2="289.4922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="289.4922" y2="289.4922"></line><polygon fill="#181818" points="116,285.4922,106,289.4922,116,293.4922,112,289.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="171.9688" y2="203.5234"></line><polygon fill="#181818" points="90,193.5234,94,203.5234,98,193.5234,94,197.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "State",
            "branch1": "bam",
            "branch2": "bom",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,203.5234,123.5,203.5234,135.5,215.5234,123.5,227.5234,64.5,227.5234,52.5,215.5234,64.5,203.5234" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
:activity;
repeat while (hej) is (yes) not (no)
if (State) then (bam)
  :Activity;
else (bom)
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_repeatwhile3(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
:activity;
repeat while (hej) is (yes) not (no)
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="114.9688" style="pointer-events: none;">activity</text><polygon fill="#F1F1F1" points="94,50,106,62,94,74,82,62,94,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="82,147.9688,106,147.9688,118,159.9688,106,171.9688,82,171.9688,70,159.9688,82,147.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="182.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="85.5" y="163.6211" style="pointer-events: none;">hej</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="118" y="157.2188" style="pointer-events: none;">yes</text><polygon fill="#F1F1F1" points="64.5,203.5234,123.5,203.5234,135.5,215.5234,123.5,227.5234,64.5,227.5234,52.5,215.5234,64.5,203.5234" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="219.1758" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="212.7734" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="212.7734" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="237.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="258.4922" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="237.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="258.4922" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,277.4922,106,289.4922,94,301.4922,82,289.4922,94,277.4922" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="94"></line><polygon fill="#181818" points="90,84,94,94,98,84,94,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118" x2="137.5" y1="159.9688" y2="159.9688"></line><polygon fill="#181818" points="133.5,120.9844,137.5,110.9844,141.5,120.9844,137.5,116.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="137.5" x2="137.5" y1="62" y2="159.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="137.5" x2="106" y1="62" y2="62"></line><polygon fill="#181818" points="116,58,106,62,116,66,112,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="127.9688" y2="147.9688"></line><polygon fill="#181818" points="90,137.9688,94,147.9688,98,137.9688,94,141.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="215.5234" y2="215.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="215.5234" y2="237.5234"></line><polygon fill="#181818" points="38.5,227.5234,42.5,237.5234,46.5,227.5234,42.5,231.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="215.5234" y2="215.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="215.5234" y2="237.5234"></line><polygon fill="#181818" points="141.5,227.5234,145.5,237.5234,149.5,227.5234,145.5,231.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="271.4922" y2="289.4922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="289.4922" y2="289.4922"></line><polygon fill="#181818" points="72,285.4922,82,289.4922,72,293.4922,76,289.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="271.4922" y2="289.4922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="289.4922" y2="289.4922"></line><polygon fill="#181818" points="116,285.4922,106,289.4922,116,293.4922,112,289.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="171.9688" y2="203.5234"></line><polygon fill="#181818" points="90,193.5234,94,203.5234,98,193.5234,94,197.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "State",
            "branch1": "bam",
            "branch2": "bom",
            "svgelement": """<polygon fill="#F1F1F1" points="82,147.9688,106,147.9688,118,159.9688,106,171.9688,82,171.9688,70,159.9688,82,147.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
:activity;
repeat while (State) is (bom) not (bam)
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_repeatwhile2(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
  :b;
  :b;
  repeat
  :aa;
  :aa;
repeat while (a) is (a) not (a)
repeat while (b) is (b) not (b)
@enduml""",
            "svg": """<ellipse cx="44" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="30" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="40" y="114.9688" style="pointer-events: none;">b</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="30" y="147.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="40" y="168.9375" style="pointer-events: none;">b</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="36" x="26" y="253.4375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="16" x="36" y="274.4063" style="pointer-events: none;">aa</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="36" x="26" y="314.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="16" x="36" y="335.875" style="pointer-events: none;">aa</text><polygon fill="#F1F1F1" points="44,201.9375,56,213.9375,44,225.9375,32,213.9375,44,201.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,368.875,56,368.875,68,380.875,56,392.875,32,392.875,20,380.875,32,368.875" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="48" y="402.9297" style="pointer-events: none;">a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="40.5" y="384.5273" style="pointer-events: none;">a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="68" y="378.125" style="pointer-events: none;">a</text><polygon fill="#F1F1F1" points="44,50,56,62,44,74,32,62,44,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,424.4297,56,424.4297,68,436.4297,56,448.4297,32,448.4297,20,436.4297,32,424.4297" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="48" y="458.4844" style="pointer-events: none;">b</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="40.5" y="440.082" style="pointer-events: none;">b</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="68" y="433.6797" style="pointer-events: none;">b</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="127.9688" y2="147.9688"></line><polygon fill="#181818" points="40,137.9688,44,147.9688,48,137.9688,44,141.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="287.4063" y2="314.9063"></line><polygon fill="#181818" points="40,304.9063,44,314.9063,48,304.9063,44,308.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="225.9375" y2="253.4375"></line><polygon fill="#181818" points="40,243.4375,44,253.4375,48,243.4375,44,247.4375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="68" x2="80" y1="380.875" y2="380.875"></line><polygon fill="#181818" points="76,307.4063,80,297.4063,84,307.4063,80,303.4063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="80" x2="80" y1="213.9375" y2="380.875"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="80" x2="56" y1="213.9375" y2="213.9375"></line><polygon fill="#181818" points="66,209.9375,56,213.9375,66,217.9375,62,213.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="348.875" y2="368.875"></line><polygon fill="#181818" points="40,358.875,44,368.875,48,358.875,44,362.875" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="181.9375" y2="201.9375"></line><polygon fill="#181818" points="40,191.9375,44,201.9375,48,191.9375,44,195.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="74" y2="94"></line><polygon fill="#181818" points="40,84,44,94,48,84,44,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="68" x2="98" y1="436.4297" y2="436.4297"></line><polygon fill="#181818" points="94,245.9375,98,235.9375,102,245.9375,98,241.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="98" x2="98" y1="62" y2="436.4297"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="98" x2="56" y1="62" y2="62"></line><polygon fill="#181818" points="66,58,56,62,66,66,62,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="392.875" y2="424.4297"></line><polygon fill="#181818" points="40,414.4297,44,424.4297,48,414.4297,44,418.4297" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="30" y2="50"></line><polygon fill="#181818" points="40,40,44,50,48,40,44,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "State",
            "branch1": "bam",
            "branch2": "bom",
            "svgelement": """<polygon fill="#F1F1F1" points="32,424.4297,56,424.4297,68,436.4297,56,448.4297,32,448.4297,20,436.4297,32,424.4297" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
  :b;
  :b;
  repeat
  :aa;
  :aa;
repeat while (a) is (a) not (a)
repeat while (State) is (bom) not (bam)
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_nested_repeatwhile(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
  :b;
  :b;
  repeat
  :aa;
  :aa;
repeat while (a) is (a) not (a)
repeat while (b) is (b) not (b)
@enduml""",
            "svg": """<ellipse cx="44" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="30" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="40" y="114.9688" style="pointer-events: none;">b</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="30" y="147.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="40" y="168.9375" style="pointer-events: none;">b</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="36" x="26" y="253.4375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="16" x="36" y="274.4063" style="pointer-events: none;">aa</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="36" x="26" y="314.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="16" x="36" y="335.875" style="pointer-events: none;">aa</text><polygon fill="#F1F1F1" points="44,201.9375,56,213.9375,44,225.9375,32,213.9375,44,201.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,368.875,56,368.875,68,380.875,56,392.875,32,392.875,20,380.875,32,368.875" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="48" y="402.9297" style="pointer-events: none;">a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="40.5" y="384.5273" style="pointer-events: none;">a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="68" y="378.125" style="pointer-events: none;">a</text><polygon fill="#F1F1F1" points="44,50,56,62,44,74,32,62,44,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,424.4297,56,424.4297,68,436.4297,56,448.4297,32,448.4297,20,436.4297,32,424.4297" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="48" y="458.4844" style="pointer-events: none;">b</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="40.5" y="440.082" style="pointer-events: none;">b</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="68" y="433.6797" style="pointer-events: none;">b</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="127.9688" y2="147.9688"></line><polygon fill="#181818" points="40,137.9688,44,147.9688,48,137.9688,44,141.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="287.4063" y2="314.9063"></line><polygon fill="#181818" points="40,304.9063,44,314.9063,48,304.9063,44,308.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="225.9375" y2="253.4375"></line><polygon fill="#181818" points="40,243.4375,44,253.4375,48,243.4375,44,247.4375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="68" x2="80" y1="380.875" y2="380.875"></line><polygon fill="#181818" points="76,307.4063,80,297.4063,84,307.4063,80,303.4063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="80" x2="80" y1="213.9375" y2="380.875"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="80" x2="56" y1="213.9375" y2="213.9375"></line><polygon fill="#181818" points="66,209.9375,56,213.9375,66,217.9375,62,213.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="348.875" y2="368.875"></line><polygon fill="#181818" points="40,358.875,44,368.875,48,358.875,44,362.875" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="181.9375" y2="201.9375"></line><polygon fill="#181818" points="40,191.9375,44,201.9375,48,191.9375,44,195.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="74" y2="94"></line><polygon fill="#181818" points="40,84,44,94,48,84,44,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="68" x2="98" y1="436.4297" y2="436.4297"></line><polygon fill="#181818" points="94,245.9375,98,235.9375,102,245.9375,98,241.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="98" x2="98" y1="62" y2="436.4297"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="98" x2="56" y1="62" y2="62"></line><polygon fill="#181818" points="66,58,56,62,66,66,62,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="392.875" y2="424.4297"></line><polygon fill="#181818" points="40,414.4297,44,424.4297,48,414.4297,44,418.4297" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="44" y1="30" y2="50"></line><polygon fill="#181818" points="40,40,44,50,48,40,44,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,368.875,56,368.875,68,380.875,56,392.875,32,392.875,20,380.875,32,368.875" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
  :b;
  :b;
repeat while (b) is (b) not (b)
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifnestedinrepeatwhile(self, client):
        test_data = {
            "plantuml": """@startuml
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
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="64.5,94,123.5,94,135.5,106,123.5,118,64.5,118,52.5,106,64.5,94" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="109.6523" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="103.25" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="103.25" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="128"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="148.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="128"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="148.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,167.9688,106,179.9688,94,191.9688,82,179.9688,94,167.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="82" x="53" y="216.9844"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="62" x="63" y="237.9531" style="pointer-events: none;">read data</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="140" x="24" y="270.9531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="120" x="34" y="291.9219" style="pointer-events: none;">generate diagrams</text><polygon fill="#F1F1F1" points="94,50,106,62,94,74,82,62,94,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="61.5,324.9219,126.5,324.9219,138.5,336.9219,126.5,348.9219,61.5,348.9219,49.5,336.9219,61.5,324.9219" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="358.9766" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="65" x="61.5" y="340.5742" style="pointer-events: none;">more data?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="138.5" y="334.1719" style="pointer-events: none;">yes</text><polygon fill="#F1F1F1" points="81,380.4766,107,380.4766,119,392.4766,107,404.4766,81,404.4766,69,392.4766,81,380.4766" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="26" x="81" y="396.1289" style="pointer-events: none;">Bom</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="6" x="63" y="389.7266" style="pointer-events: none;">y</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="119" y="389.7266" style="pointer-events: none;">n</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="21" y="414.4766"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="31" y="435.4453" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="104" y="414.4766"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="114" y="435.4453" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,454.4453,106,466.4453,94,478.4453,82,466.4453,94,454.4453" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="106" y2="106"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="106" y2="128"></line><polygon fill="#181818" points="38.5,118,42.5,128,46.5,118,42.5,122" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="106" y2="106"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="106" y2="128"></line><polygon fill="#181818" points="141.5,118,145.5,128,149.5,118,145.5,122" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="161.9688" y2="179.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="179.9688" y2="179.9688"></line><polygon fill="#181818" points="72,175.9688,82,179.9688,72,183.9688,76,179.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="161.9688" y2="179.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="179.9688" y2="179.9688"></line><polygon fill="#181818" points="116,175.9688,106,179.9688,116,183.9688,112,179.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="191.9688" y2="216.9844"></line><polygon fill="#181818" points="90,206.9844,94,216.9844,98,206.9844,94,210.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="250.9531" y2="270.9531"></line><polygon fill="#181818" points="90,260.9531,94,270.9531,98,260.9531,94,264.9531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="94"></line><polygon fill="#181818" points="90,84,94,94,98,84,94,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="191" y1="336.9219" y2="336.9219"></line><polygon fill="#181818" points="187,211.9688,191,201.9688,195,211.9688,191,207.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="191" y1="62" y2="336.9219"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="106" y1="62" y2="62"></line><polygon fill="#181818" points="116,58,106,62,116,66,112,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="304.9219" y2="324.9219"></line><polygon fill="#181818" points="90,314.9219,94,324.9219,98,314.9219,94,318.9219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="69" x2="52.5" y1="392.4766" y2="392.4766"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="52.5" y1="392.4766" y2="414.4766"></line><polygon fill="#181818" points="48.5,404.4766,52.5,414.4766,56.5,404.4766,52.5,408.4766" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="119" x2="135.5" y1="392.4766" y2="392.4766"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="135.5" y1="392.4766" y2="414.4766"></line><polygon fill="#181818" points="131.5,404.4766,135.5,414.4766,139.5,404.4766,135.5,408.4766" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="52.5" y1="448.4453" y2="466.4453"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="82" y1="466.4453" y2="466.4453"></line><polygon fill="#181818" points="72,462.4453,82,466.4453,72,470.4453,76,466.4453" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="135.5" y1="448.4453" y2="466.4453"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="106" y1="466.4453" y2="466.4453"></line><polygon fill="#181818" points="116,462.4453,106,466.4453,116,470.4453,112,466.4453" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="348.9219" y2="380.4766"></line><polygon fill="#181818" points="90,370.4766,94,380.4766,98,370.4766,94,374.4766" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,94,123.5,94,135.5,106,123.5,118,64.5,118,52.5,106,64.5,94" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
  :read data;
  :generate diagrams;
repeat while (more data?) is (yes) not (no)
if (Bom) then (y)
  :Activity;
else (n)
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifwithrepeatwhileabove(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
  :read data;
  :generate diagrams;
repeat while (more data?) is (yes) not (no)
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="82" x="53" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="62" x="63" y="114.9688" style="pointer-events: none;">read data</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="140" x="24" y="155.4688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="120" x="34" y="176.4375" style="pointer-events: none;">generate diagrams</text><polygon fill="#F1F1F1" points="94,50,106,62,94,74,82,62,94,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="61.5,209.4375,126.5,209.4375,138.5,221.4375,126.5,233.4375,61.5,233.4375,49.5,221.4375,61.5,209.4375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="243.4922" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="65" x="61.5" y="225.0898" style="pointer-events: none;">more data?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="138.5" y="218.6875" style="pointer-events: none;">yes</text><polygon fill="#F1F1F1" points="64.5,264.9922,123.5,264.9922,135.5,276.9922,123.5,288.9922,64.5,288.9922,52.5,276.9922,64.5,264.9922" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="280.6445" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="274.2422" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="274.2422" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="298.9922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="319.9609" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="298.9922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="319.9609" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,338.9609,106,350.9609,94,362.9609,82,350.9609,94,338.9609" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="127.9688" y2="155.4688"></line><polygon fill="#181818" points="90,145.4688,94,155.4688,98,145.4688,94,149.4688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="94"></line><polygon fill="#181818" points="90,84,94,94,98,84,94,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="176" y1="221.4375" y2="221.4375"></line><polygon fill="#181818" points="172,147.9688,176,137.9688,180,147.9688,176,143.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="176" x2="176" y1="62" y2="221.4375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="176" x2="106" y1="62" y2="62"></line><polygon fill="#181818" points="116,58,106,62,116,66,112,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="189.4375" y2="209.4375"></line><polygon fill="#181818" points="90,199.4375,94,209.4375,98,199.4375,94,203.4375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="276.9922" y2="276.9922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="276.9922" y2="298.9922"></line><polygon fill="#181818" points="38.5,288.9922,42.5,298.9922,46.5,288.9922,42.5,292.9922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="276.9922" y2="276.9922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="276.9922" y2="298.9922"></line><polygon fill="#181818" points="141.5,288.9922,145.5,298.9922,149.5,288.9922,145.5,292.9922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="332.9609" y2="350.9609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="350.9609" y2="350.9609"></line><polygon fill="#181818" points="72,346.9609,82,350.9609,72,354.9609,76,350.9609" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="332.9609" y2="350.9609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="350.9609" y2="350.9609"></line><polygon fill="#181818" points="116,346.9609,106,350.9609,116,354.9609,112,350.9609" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="233.4375" y2="264.9922"></line><polygon fill="#181818" points="90,254.9922,94,264.9922,98,254.9922,94,258.9922" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,264.9922,123.5,264.9922,135.5,276.9922,123.5,288.9922,64.5,288.9922,52.5,276.9922,64.5,264.9922" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
  :read data;
  :generate diagrams;
repeat while (more data?) is (yes) not (no)
@enduml"""
            assert response.data.decode("utf-8") == expected_puml


class TestAppRoutesIf:
    def test_build_tree(self):
        lines = """@startuml
:Activity 1;
if (st0) then (yes)
    if (st1) then (yes)
        :activity 2;
    else (no)
    endif
    if (st2) then (yes)
        if (st3) then (yes)
        else (no)
            :activity 3;
        endif
    else (no)
    endif
    :activity 4;
endif
@enduml""".splitlines()
        output = [3, 8, 7, 2]
        assert build_tree(lines) == output

    def test_addforkrightbranchinsiderepeat(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
repeat while (hej) is (yes) not (no)
:activity;
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="64.5,94,123.5,94,135.5,106,123.5,118,64.5,118,52.5,106,64.5,94" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="109.6523" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="103.25" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="103.25" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="128"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="148.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="128"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="148.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,167.9688,106,179.9688,94,191.9688,82,179.9688,94,167.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="94,50,106,62,94,74,82,62,94,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="82,211.9688,106,211.9688,118,223.9688,106,235.9688,82,235.9688,70,223.9688,82,211.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="98" y="246.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="85.5" y="227.6211" style="pointer-events: none;">hej</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="118" y="221.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="267.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="288.4922" style="pointer-events: none;">activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="106" y2="106"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="106" y2="128"></line><polygon fill="#181818" points="38.5,118,42.5,128,46.5,118,42.5,122" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="106" y2="106"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="106" y2="128"></line><polygon fill="#181818" points="141.5,118,145.5,128,149.5,118,145.5,122" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="161.9688" y2="179.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="179.9688" y2="179.9688"></line><polygon fill="#181818" points="72,175.9688,82,179.9688,72,183.9688,76,179.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="161.9688" y2="179.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="179.9688" y2="179.9688"></line><polygon fill="#181818" points="116,175.9688,106,179.9688,116,183.9688,112,179.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="94"></line><polygon fill="#181818" points="90,84,94,94,98,84,94,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118" x2="191" y1="223.9688" y2="223.9688"></line><polygon fill="#181818" points="187,152.9844,191,142.9844,195,152.9844,191,148.9844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="191" y1="62" y2="223.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="106" y1="62" y2="62"></line><polygon fill="#181818" points="116,58,106,62,116,66,112,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="191.9688" y2="211.9688"></line><polygon fill="#181818" points="90,201.9688,94,211.9688,98,201.9688,94,205.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="235.9688" y2="267.5234"></line><polygon fill="#181818" points="90,257.5234,94,267.5234,98,257.5234,94,261.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,94,123.5,94,135.5,106,123.5,118,64.5,118,52.5,106,64.5,94" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "where": "right",
            "type": "fork",
        }
        with client:
            response = client.post(
                "/addToIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
fork
:action;
fork again
:action;
end fork
endif
repeat while (hej) is (yes) not (no)
:activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addforkrightbranch(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="56.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="66.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="119.9375">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="94,138.9375,106,150.9375,94,162.9375,82,150.9375,94,138.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="38.5,88.9688,42.5,98.9688,46.5,88.9688,42.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="141.5,88.9688,145.5,98.9688,149.5,88.9688,145.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="72,146.9375,82,150.9375,72,154.9375,76,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="116,146.9375,106,150.9375,116,154.9375,112,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="90,54.9688,94,64.9688,98,54.9688,94,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "where": "right",
            "type": "fork",
        }
        with client:
            response = client.post(
                "/addToIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
fork
:action;
fork again
:action;
end fork
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addrepeatleftbranch(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="56.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="66.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="119.9375">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="94,138.9375,106,150.9375,94,162.9375,82,150.9375,94,138.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="38.5,88.9688,42.5,98.9688,46.5,88.9688,42.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="141.5,88.9688,145.5,98.9688,149.5,88.9688,145.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="72,146.9375,82,150.9375,72,154.9375,76,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="116,146.9375,106,150.9375,116,154.9375,112,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="90,54.9688,94,64.9688,98,54.9688,94,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "where": "left",
            "type": "repeat",
        }
        with client:
            response = client.post(
                "/addToIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
repeat
:Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
else (no)
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_toggledetach2(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="56.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="66.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="119.9375">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="94,138.9375,106,150.9375,94,162.9375,82,150.9375,94,138.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="38.5,88.9688,42.5,98.9688,46.5,88.9688,42.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="141.5,88.9688,145.5,98.9688,149.5,88.9688,145.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="72,146.9375,82,150.9375,72,154.9375,76,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="116,146.9375,106,150.9375,116,154.9375,112,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="90,54.9688,94,64.9688,98,54.9688,94,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/detachIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_toggledetach(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="56.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="66.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="119.9375">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="94,138.9375,106,150.9375,94,162.9375,82,150.9375,94,138.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="38.5,88.9688,42.5,98.9688,46.5,88.9688,42.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="141.5,88.9688,145.5,98.9688,149.5,88.9688,145.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="72,146.9375,82,150.9375,72,154.9375,76,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="116,146.9375,106,150.9375,116,154.9375,112,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="90,54.9688,94,64.9688,98,54.9688,94,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/detachIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
detach
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_editifwithwhileabove(self, client):
        test_data = {
            "plantuml": """@startuml
start
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
stop
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="50" x="69" y="105.5547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="30" x="79" y="126.5234" style="pointer-events: none;">hello</text><polygon fill="#F1F1F1" points="56,50,132,50,144,62,132,74,56,74,44,62,56,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="98" y="84.0547" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="76" x="56" y="65.6523" style="pointer-events: none;">ST_ONGOING</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="29" y="59.25" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="89" x="49.5" y="181.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="59.5" y="202.4922" style="pointer-events: none;">hello again</text><polygon fill="#F1F1F1" points="64.5,235.4922,123.5,235.4922,135.5,247.4922,123.5,259.4922,64.5,259.4922,52.5,247.4922,64.5,235.4922" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="251.1445" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="244.7422" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="244.7422" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="269.4922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="290.4609" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="269.4922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="290.4609" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,309.4609,106,321.4609,94,333.4609,82,321.4609,94,309.4609" style="stroke:#181818;stroke-width:0.5;"></polygon><ellipse cx="94" cy="364.4609" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="94" cy="364.4609" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="105.5547"></line><polygon fill="#181818" points="90,95.5547,94,105.5547,98,95.5547,94,99.5547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="139.5234" y2="149.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="156" y1="149.5234" y2="149.5234"></line><polygon fill="#181818" points="152,114.1367,156,104.1367,160,114.1367,156,110.1367" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="156" x2="156" y1="62" y2="149.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="156" x2="144" y1="62" y2="62"></line><polygon fill="#181818" points="154,58,144,62,154,66,150,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="44" x2="32" y1="62" y2="62"></line><polygon fill="#181818" points="28,100.1367,32,110.1367,36,100.1367,32,104.1367" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="32" x2="32" y1="62" y2="161.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="32" x2="94" y1="161.5234" y2="161.5234"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="161.5234" y2="181.5234"></line><polygon fill="#181818" points="90,171.5234,94,181.5234,98,171.5234,94,175.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="247.4922" y2="247.4922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="247.4922" y2="269.4922"></line><polygon fill="#181818" points="38.5,259.4922,42.5,269.4922,46.5,259.4922,42.5,263.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="247.4922" y2="247.4922"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="247.4922" y2="269.4922"></line><polygon fill="#181818" points="141.5,259.4922,145.5,269.4922,149.5,259.4922,145.5,263.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="303.4609" y2="321.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="321.4609" y2="321.4609"></line><polygon fill="#181818" points="72,317.4609,82,321.4609,72,325.4609,76,321.4609" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="303.4609" y2="321.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="321.4609" y2="321.4609"></line><polygon fill="#181818" points="116,317.4609,106,321.4609,116,325.4609,112,321.4609" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="215.4922" y2="235.4922"></line><polygon fill="#181818" points="90,225.4922,94,235.4922,98,225.4922,94,229.4922" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="333.4609" y2="353.4609"></line><polygon fill="#181818" points="90,343.4609,94,353.4609,98,343.4609,94,347.4609" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "State",
            "branch1": "bam",
            "branch2": "bom",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,235.4922,123.5,235.4922,135.5,247.4922,123.5,259.4922,64.5,259.4922,52.5,247.4922,64.5,235.4922" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
while (ST_ONGOING) is (Yes)
    :hello;
endwhile (No);
:hello again;
if (State) then (bam)
  :Activity;
else (bom)
  :Activity;
endif
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_gettextpolynobranch(self, client):
        test_data = {
            "plantuml": """@startuml
if (Statement) then (yes)
  :Activity;
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="58.4023"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="79.3711">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="127.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="148.3398">Activity</text><polygon fill="#F1F1F1" points="32,10,91,10,103,22,91,34,32,34,20,22,32,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="65.5" y="44.0547">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="32" y="25.6523">Statement</text><polygon fill="#F1F1F1" points="61.5,181.3398,73.5,193.3398,61.5,205.3398,49.5,193.3398,61.5,181.3398" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="92.3711" y2="127.3711"></line><polygon fill="#181818" points="57.5,117.3711,61.5,127.3711,65.5,117.3711,61.5,121.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="34" y2="58.4023"></line><polygon fill="#181818" points="57.5,48.4023,61.5,58.4023,65.5,48.4023,61.5,52.4023" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="103" x2="115" y1="22" y2="22"></line><polygon fill="#181818" points="111,99.8711,115,109.8711,119,99.8711,115,103.8711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="115" y1="22" y2="193.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="73.5" y1="193.3398" y2="193.3398"></line><polygon fill="#181818" points="83.5,189.3398,73.5,193.3398,83.5,197.3398,79.5,193.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="161.3398" y2="181.3398"></line><polygon fill="#181818" points="57.5,171.3398,61.5,181.3398,65.5,171.3398,61.5,175.3398" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,10,91,10,103,22,91,34,32,34,20,22,32,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getTextPoly",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = ["Statement", "yes"]
            assert json.loads(response.data.decode("utf-8")) == expected_result

    def test_editnoelsebranchempty(self, client):
        test_data = {
            "plantuml": """@startuml
if (Statement) then (yes)
  :Activity;
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="58.4023"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="79.3711">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="127.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="148.3398">Activity</text><polygon fill="#F1F1F1" points="32,10,91,10,103,22,91,34,32,34,20,22,32,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="65.5" y="44.0547">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="32" y="25.6523">Statement</text><polygon fill="#F1F1F1" points="61.5,181.3398,73.5,193.3398,61.5,205.3398,49.5,193.3398,61.5,181.3398" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="92.3711" y2="127.3711"></line><polygon fill="#181818" points="57.5,117.3711,61.5,127.3711,65.5,117.3711,61.5,121.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="34" y2="58.4023"></line><polygon fill="#181818" points="57.5,48.4023,61.5,58.4023,65.5,48.4023,61.5,52.4023" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="103" x2="115" y1="22" y2="22"></line><polygon fill="#181818" points="111,99.8711,115,109.8711,119,99.8711,115,103.8711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="115" y1="22" y2="193.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="73.5" y1="193.3398" y2="193.3398"></line><polygon fill="#181818" points="83.5,189.3398,73.5,193.3398,83.5,197.3398,79.5,193.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="161.3398" y2="181.3398"></line><polygon fill="#181818" points="57.5,171.3398,61.5,181.3398,65.5,171.3398,61.5,175.3398" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "Statement",
            "branch1": "yes",
            "branch2": "",
            "svgelement": """<polygon fill="#F1F1F1" points="32,10,91,10,103,22,91,34,32,34,20,22,32,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
if (Statement) then (yes)
  :Activity;
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_editnoelsebranch(self, client):
        test_data = {
            "plantuml": """@startuml
if (Statement) then (yes)
  :Activity;
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="58.4023"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="79.3711">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="30" y="127.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="40" y="148.3398">Activity</text><polygon fill="#F1F1F1" points="32,10,91,10,103,22,91,34,32,34,20,22,32,10" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="65.5" y="44.0547">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="32" y="25.6523">Statement</text><polygon fill="#F1F1F1" points="61.5,181.3398,73.5,193.3398,61.5,205.3398,49.5,193.3398,61.5,181.3398" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="92.3711" y2="127.3711"></line><polygon fill="#181818" points="57.5,117.3711,61.5,127.3711,65.5,117.3711,61.5,121.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="34" y2="58.4023"></line><polygon fill="#181818" points="57.5,48.4023,61.5,58.4023,65.5,48.4023,61.5,52.4023" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="103" x2="115" y1="22" y2="22"></line><polygon fill="#181818" points="111,99.8711,115,109.8711,119,99.8711,115,103.8711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="115" y1="22" y2="193.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="115" x2="73.5" y1="193.3398" y2="193.3398"></line><polygon fill="#181818" points="83.5,189.3398,73.5,193.3398,83.5,197.3398,79.5,193.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="61.5" x2="61.5" y1="161.3398" y2="181.3398"></line><polygon fill="#181818" points="57.5,171.3398,61.5,181.3398,65.5,171.3398,61.5,175.3398" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "Statement",
            "branch1": "yes",
            "branch2": "right",
            "svgelement": """<polygon fill="#F1F1F1" points="32,10,91,10,103,22,91,34,32,34,20,22,32,10" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
if (Statement) then (yes)
  :Activity;
  :Activity;
else (right)
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addleftifnested(self, client):
        test_data = {
            "plantuml": """@startuml
:activity;
if (Statement) then (yes)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
else (no)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="165.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="175.5" y="31.9688" style="pointer-events: none;">activity</text><polygon fill="#F1F1F1" points="167.5,64.9688,226.5,64.9688,238.5,76.9688,226.5,88.9688,167.5,88.9688,155.5,76.9688,167.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="167.5" y="80.6211" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="135.5" y="74.2188" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="238.5" y="74.2188" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="119.9375" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="64.5,152.9375,123.5,152.9375,135.5,164.9375,123.5,176.9375,64.5,176.9375,52.5,164.9375,64.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="168.5898" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="162.1875" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="162.1875" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="207.9063" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="207.9063" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,226.9063,106,238.9063,94,250.9063,82,238.9063,94,226.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="268.5" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="278.5" y="119.9375" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="270.5,152.9375,329.5,152.9375,341.5,164.9375,329.5,176.9375,270.5,176.9375,258.5,164.9375,270.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="270.5" y="168.5898" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="238.5" y="162.1875" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="341.5" y="162.1875" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="217" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="227" y="207.9063" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="320" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="330" y="207.9063" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="300,226.9063,312,238.9063,300,250.9063,288,238.9063,300,226.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="197,256.9063,209,268.9063,197,280.9063,185,268.9063,197,256.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="38.5,176.9375,42.5,186.9375,46.5,176.9375,42.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="141.5,176.9375,145.5,186.9375,149.5,176.9375,145.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="72,234.9063,82,238.9063,72,242.9063,76,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="116,234.9063,106,238.9063,116,242.9063,112,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="132.9375" y2="152.9375"></line><polygon fill="#181818" points="90,142.9375,94,152.9375,98,142.9375,94,146.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="258.5" x2="248.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="248.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="244.5,176.9375,248.5,186.9375,252.5,176.9375,248.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="341.5" x2="351.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="347.5,176.9375,351.5,186.9375,355.5,176.9375,351.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="248.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="288" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="278,234.9063,288,238.9063,278,242.9063,282,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="312" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="322,234.9063,312,238.9063,322,242.9063,318,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="132.9375" y2="152.9375"></line><polygon fill="#181818" points="296,142.9375,300,152.9375,304,142.9375,300,146.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="155.5" x2="94" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="90,88.9688,94,98.9688,98,88.9688,94,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="238.5" x2="300" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="296,88.9688,300,98.9688,304,88.9688,300,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="250.9063" y2="268.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="185" y1="268.9063" y2="268.9063"></line><polygon fill="#181818" points="175,264.9063,185,268.9063,175,272.9063,179,268.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="250.9063" y2="268.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="209" y1="268.9063" y2="268.9063"></line><polygon fill="#181818" points="219,264.9063,209,268.9063,219,272.9063,215,268.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="197" x2="197" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="193,54.9688,197,64.9688,201,54.9688,197,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="167.5,64.9688,226.5,64.9688,238.5,76.9688,226.5,88.9688,167.5,88.9688,155.5,76.9688,167.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
            "where": "left",
            "type": "if",
        }
        with client:
            response = client.post(
                "/addToIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:activity;
if (Statement) then (yes)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
if (Statement) then (yes)
:Activity;
else (no)
:Activity;
endif
else (no)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_get_if_line(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
detach
else (no)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="159.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="169.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="167.5,64.9688,226.5,64.9688,238.5,76.9688,226.5,88.9688,167.5,88.9688,155.5,76.9688,167.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="167.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="135.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="238.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="64.5,152.9375,123.5,152.9375,135.5,164.9375,123.5,176.9375,64.5,176.9375,52.5,164.9375,64.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="168.5898">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="162.1875">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="162.1875">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="207.9063">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="207.9063">Activity</text><polygon fill="#F1F1F1" points="94,226.9063,106,238.9063,94,250.9063,82,238.9063,94,226.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="268.5" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="278.5" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="270.5,152.9375,329.5,152.9375,341.5,164.9375,329.5,176.9375,270.5,176.9375,258.5,164.9375,270.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="270.5" y="168.5898">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="238.5" y="162.1875">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="341.5" y="162.1875">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="217" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="227" y="207.9063">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="320" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="330" y="207.9063">Activity</text><polygon fill="#F1F1F1" points="300,226.9063,312,238.9063,300,250.9063,288,238.9063,300,226.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="197,256.9063,209,268.9063,197,280.9063,185,268.9063,197,256.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="38.5,176.9375,42.5,186.9375,46.5,176.9375,42.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="141.5,176.9375,145.5,186.9375,149.5,176.9375,145.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="72,234.9063,82,238.9063,72,242.9063,76,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="116,234.9063,106,238.9063,116,242.9063,112,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="132.9375" y2="152.9375"></line><polygon fill="#181818" points="90,142.9375,94,152.9375,98,142.9375,94,146.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="258.5" x2="248.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="248.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="244.5,176.9375,248.5,186.9375,252.5,176.9375,248.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="341.5" x2="351.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="347.5,176.9375,351.5,186.9375,355.5,176.9375,351.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="248.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="288" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="278,234.9063,288,238.9063,278,242.9063,282,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="312" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="322,234.9063,312,238.9063,322,242.9063,318,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="132.9375" y2="152.9375"></line><polygon fill="#181818" points="296,142.9375,300,152.9375,304,142.9375,300,146.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="155.5" x2="94" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="90,88.9688,94,98.9688,98,88.9688,94,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="238.5" x2="300" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="296,88.9688,300,98.9688,304,88.9688,300,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="250.9063" y2="268.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="185" y1="268.9063" y2="268.9063"></line><polygon fill="#181818" points="175,264.9063,185,268.9063,175,272.9063,179,268.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="250.9063" y2="268.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="209" y1="268.9063" y2="268.9063"></line><polygon fill="#181818" points="219,264.9063,209,268.9063,219,272.9063,215,268.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="197" x2="197" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="193,54.9688,197,64.9688,201,54.9688,197,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,152.9375,123.5,152.9375,135.5,164.9375,123.5,176.9375,64.5,176.9375,52.5,164.9375,64.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getIfLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = [4, 6, 8]

            # Assert the result value is as expected
            assert result_value == expected_puml

    def test_get_if_line2(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
  :Activity;
  backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<ellipse cx="51.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="114.9688" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,50,63.5,62,51.5,74,39.5,62,51.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,157.9688,71,157.9688,83,169.9688,71,181.9688,32,181.9688,20,169.9688,32,157.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="192.0234" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="173.6211" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="167.2188" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="107" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="117" y="114.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="213.5234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="234.4922" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="74" y2="94"></line><polygon fill="#181818" points="47.5,84,51.5,94,55.5,84,51.5,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="138.5" y1="169.9688" y2="169.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="138.5" y1="127.9688" y2="169.9688"></line><polygon fill="#181818" points="134.5,137.9688,138.5,127.9688,142.5,137.9688,138.5,133.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="138.5" y1="62" y2="94"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="63.5" y1="62" y2="62"></line><polygon fill="#181818" points="73.5,58,63.5,62,73.5,66,69.5,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="127.9688" y2="157.9688"></line><polygon fill="#181818" points="47.5,147.9688,51.5,157.9688,55.5,147.9688,51.5,151.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="30" y2="50"></line><polygon fill="#181818" points="47.5,40,51.5,50,55.5,40,51.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="181.9688" y2="213.5234"></line><polygon fill="#181818" points="47.5,203.5234,51.5,213.5234,55.5,203.5234,51.5,207.5234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="32,157.9688,71,157.9688,83,169.9688,71,181.9688,32,181.9688,20,169.9688,32,157.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getIfLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = 5

            # Assert the result value is as expected
            assert result_value == expected_puml

    def test_get_if_line3(self, client):
        test_data = {
            "plantuml": """@startuml
start
switch (test?)
case ( condition 1)
    :Activity;
case ( condition 2)
    :Activity;
endswitch
@enduml""",
            "svg": """<ellipse cx="118.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="104.5,50,132.5,50,144.5,62,132.5,74,104.5,74,92.5,62,104.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="28" x="104.5" y="65.8081" style="pointer-events: none;">test?</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="130.748" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="128.5" y="109.6094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="138.5" y="130.748" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="118.5,153.5781,118.5,153.5781,130.5,165.5781,118.5,177.5781,118.5,177.5781,106.5,165.5781,118.5,153.5781" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="92.5" x2="42.5" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="62" y2="109.6094"></line><polygon fill="#181818" points="38.5,99.6094,42.5,109.6094,46.5,99.6094,42.5,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="46.5" y="89.6128">condition 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="144.5" x2="160" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="62" y2="109.6094"></line><polygon fill="#181818" points="156,99.6094,160,109.6094,164,99.6094,160,103.6094" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="62" x="164" y="89.6128">condition 2</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="106.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="96.5,161.5781,106.5,165.5781,96.5,169.5781,100.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="160" y1="143.5781" y2="165.5781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="160" x2="130.5" y1="165.5781" y2="165.5781"></line><polygon fill="#181818" points="140.5,161.5781,130.5,165.5781,140.5,169.5781,136.5,165.5781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="118.5" x2="118.5" y1="30" y2="50"></line><polygon fill="#181818" points="114.5,40,118.5,50,122.5,40,118.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="104.5,50,132.5,50,144.5,62,132.5,74,104.5,74,92.5,62,104.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getIfLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            # Expected value
            expected_puml = [2, 7]

            # Assert the result value is as expected
            assert result_value == expected_puml

    def test_deleterepeatweirdnest(self, client):
        test_data = {
            "plantuml": """@startuml

start
if ( 8. IUPF is selected or not in step 4) then (yes)
    :PFCP Session Establishment Request with IUPF;
    repeat
        :Start T1 timer;
        if (Wait) then (PFCP Session Establishment Response)
            break
        endif
        -> T1 Timeout;
        backward:9. Retransmit PFCP Session Establishment Request with IUPF;
    repeat while (Number of retries < N1?) is (Yes) not (No)
    if (PFCP Session Establishment Positive Response?) then (No)
        :5.- Nsmf_PDUSession_CreateSMContext Negative Response
        - Release session without sending N1N2 to AMF;
        stop
    endif
    -> Yes;
endif
:10. Nsmf_PDUSession_CreateSMContext Response with hoState == PREPARING;
: Start Tsrn2 Timer;
repeat
    if (Wait) then (Tsrn2 timeout)
        :11. Start t4to5ho timer;
        if (Wait) then (t4to5ho timeout)
            :12. Release Session;
            stop
        else (Nsmf_PDUSession_UpdateSMContext Request \n hoState == CANCELLED)
            :13. Rollback to EPS;
            stop
        endif
    else (Nsmf_PDUSession_UpdateSMContext Request)
    endif
    backward: 14. Nsmf_PDUSession_UpdateSMContext Negative Response;
repeat while (Message format is valid?) is (No) not (Yes)
:Activity;
@enduml""",
            "svg": """<ellipse cx="269" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="313" x="112.5" y="98.4023"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="293" x="122.5" y="119.3711" style="pointer-events: none;">PFCP Session Establishment Request with IUPF</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="106" x="216" y="196.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="86" x="226" y="217.3398" style="pointer-events: none;">Start T1 timer</text><polygon fill="#F1F1F1" points="257,252.4063,281,252.4063,293,264.4063,281,276.4063,257,276.4063,245,264.4063,257,252.4063" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="223" x="273" y="286.4609" style="pointer-events: none;">PFCP Session Establishment Response</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="23" x="257.5" y="268.0586" style="pointer-events: none;">Wait</text><polygon fill="#F1F1F1" points="269,152.3711,281,164.3711,269,176.3711,257,164.3711,269,152.3711" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="199,361.4609,339,361.4609,351,373.4609,339,385.4609,199,385.4609,187,373.4609,199,361.4609" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="273" y="395.5156" style="pointer-events: none;">No</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="140" x="199" y="377.1133" style="pointer-events: none;">Number of retries &lt; N1?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="351" y="370.7109" style="pointer-events: none;">Yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="401" x="375" y="240.3398"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="381" x="385" y="261.3086" style="pointer-events: none;">9. Retransmit PFCP Session Establishment Request with IUPF</text><polygon fill="#F1F1F1" points="269,417.0156,281,429.0156,269,441.0156,257,429.0156,269,417.0156" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="47.9375" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="391" x="73.5" y="509.418"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="371" x="83.5" y="530.3867" style="pointer-events: none;">5.- Nsmf_PDUSession_CreateSMContext Negative Response</text><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="83.5" y="544.3555" style="pointer-events: none;">- Release session without sending N1N2 to AMF</text><ellipse cx="269" cy="589.8867" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="269" cy="589.8867" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="130.5,461.0156,407.5,461.0156,419.5,473.0156,407.5,485.0156,130.5,485.0156,118.5,473.0156,130.5,461.0156" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="273" y="495.0703" style="pointer-events: none;">No</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="277" x="130.5" y="476.668" style="pointer-events: none;">PFCP Session Establishment Positive Response?</text><polygon fill="#F1F1F1" points="168.5,50,369.5,50,381.5,62,369.5,74,168.5,74,156.5,62,168.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="273" y="84.0547" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="197" x="172.5" y="65.6523" style="pointer-events: none;">8. IUPF is selected or not in step 4</text><polygon fill="#F1F1F1" points="269,646.9414,281,658.9414,269,670.9414,257,658.9414,269,646.9414" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="275" y="644.1914" style="pointer-events: none;">Yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="516" x="11" y="690.9414"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="496" x="21" y="711.9102" style="pointer-events: none;">10. Nsmf_PDUSession_CreateSMContext Response with hoState == PREPARING</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="132" x="203" y="744.9102"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="108" x="217" y="765.8789" style="pointer-events: none;">Start Tsrn2 Timer</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="165" x="186.5" y="891.2813"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="145" x="196.5" y="912.25" style="pointer-events: none;">11. Start t4to5ho timer</text><polygon fill="#F1F1F1" points="257,950.1094,281,950.1094,293,962.1094,281,974.1094,257,974.1094,245,962.1094,257,950.1094" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="23" x="257.5" y="965.7617" style="pointer-events: none;">Wait</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="90" x="155" y="959.3594" style="pointer-events: none;">t4to5ho timeout</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="261" x="293" y="946.5547" style="pointer-events: none;">Nsmf_PDUSession_UpdateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="135" x="297" y="959.3594" style="pointer-events: none;">hoState == CANCELLED</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="147" x="113.5" y="984.1094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="127" x="123.5" y="1005.0781" style="pointer-events: none;">12. Release Session</text><ellipse cx="187" cy="1049.0781" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="187" cy="1049.0781" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="141" x="280.5" y="984.1094"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="121" x="290.5" y="1005.0781" style="pointer-events: none;">13. Rollback to EPS</text><ellipse cx="351" cy="1049.0781" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="351" cy="1049.0781" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="257,842.8789,281,842.8789,293,854.8789,281,866.8789,257,866.8789,245,854.8789,257,842.8789" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="80" x="273" y="876.9336" style="pointer-events: none;">Tsrn2 timeout</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="23" x="257.5" y="858.5313" style="pointer-events: none;">Wait</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="261" x="293" y="852.1289" style="pointer-events: none;">Nsmf_PDUSession_UpdateSMContext Request</text><polygon fill="#F1F1F1" points="269,798.8789,281,810.8789,269,822.8789,257,810.8789,269,798.8789" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="197.5,1102.0781,340.5,1102.0781,352.5,1114.0781,340.5,1126.0781,197.5,1126.0781,185.5,1114.0781,197.5,1102.0781" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="273" y="1136.1328" style="pointer-events: none;">Yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="143" x="197.5" y="1117.7305" style="pointer-events: none;">Message format is valid?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="352.5" y="1111.3281" style="pointer-events: none;">No</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="403" x="604" y="954.3203"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="379" x="618" y="975.2891" style="pointer-events: none;">14. Nsmf_PDUSession_UpdateSMContext Negative Response</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="237.5" y="1157.6328"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="247.5" y="1178.6016" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="276.4063" y2="300.8086"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="177" y1="300.8086" y2="300.8086"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="177" x2="177" y1="300.8086" y2="429.0156"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="177" x2="257" y1="429.0156" y2="429.0156"></line><polygon fill="#181818" points="247,425.0156,257,429.0156,247,433.0156,251,429.0156" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="293" x2="305" y1="264.4063" y2="264.4063"></line><polygon fill="#181818" points="301,287.8086,305,297.8086,309,287.8086,305,291.8086" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="305" x2="305" y1="264.4063" y2="319.8086"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="305" x2="269" y1="319.8086" y2="319.8086"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="230.3398" y2="252.4063"></line><polygon fill="#181818" points="265,242.4063,269,252.4063,273,242.4063,269,246.4063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="176.3711" y2="196.3711"></line><polygon fill="#181818" points="265,186.3711,269,196.3711,273,186.3711,269,190.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351" x2="575.5" y1="373.4609" y2="373.4609"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="575.5" x2="575.5" y1="274.3086" y2="373.4609"></line><polygon fill="#181818" points="571.5,284.3086,575.5,274.3086,579.5,284.3086,575.5,280.3086" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="575.5" x2="575.5" y1="164.3711" y2="240.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="575.5" x2="281" y1="164.3711" y2="164.3711"></line><polygon fill="#181818" points="291,160.3711,281,164.3711,291,168.3711,287,164.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="319.8086" y2="361.4609"></line><polygon fill="#181818" points="265,351.4609,269,361.4609,273,351.4609,269,355.4609" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="64" x="273" y="341.1133">T1 Timeout</text><line style="stroke:#181818;stroke-width:1.0;" x1="269" x2="269" y1="385.4609" y2="417.0156"></line><polygon fill="#181818" points="265,407.0156,269,417.0156,273,407.0156,269,411.0156" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="132.3711" y2="152.3711"></line><polygon fill="#181818" points="265,142.3711,269,152.3711,273,142.3711,269,146.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="557.3555" y2="578.8867"></line><polygon fill="#181818" points="265,568.8867,269,578.8867,273,568.8867,269,572.8867" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="485.0156" y2="509.418"></line><polygon fill="#181818" points="265,499.418,269,509.418,273,499.418,269,503.418" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="419.5" x2="474.5" y1="473.0156" y2="473.0156"></line><polygon fill="#181818" points="470.5,548.8867,474.5,558.8867,478.5,548.8867,474.5,552.8867" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="474.5" x2="474.5" y1="473.0156" y2="622.8867"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="474.5" x2="269" y1="622.8867" y2="622.8867"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="622.8867" y2="646.9414"></line><polygon fill="#181818" points="265,636.9414,269,646.9414,273,636.9414,269,640.9414" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="441.0156" y2="461.0156"></line><polygon fill="#181818" points="265,451.0156,269,461.0156,273,451.0156,269,455.0156" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="74" y2="98.4023"></line><polygon fill="#181818" points="265,88.4023,269,98.4023,273,88.4023,269,92.4023" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="381.5" x2="786" y1="62" y2="62"></line><polygon fill="#181818" points="782,340.3633,786,350.3633,790,340.3633,786,344.3633" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="786" x2="786" y1="62" y2="658.9414"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="786" x2="281" y1="658.9414" y2="658.9414"></line><polygon fill="#181818" points="291,654.9414,281,658.9414,291,662.9414,287,658.9414" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="30" y2="50"></line><polygon fill="#181818" points="265,40,269,50,273,40,269,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="670.9414" y2="690.9414"></line><polygon fill="#181818" points="265,680.9414,269,690.9414,273,680.9414,269,684.9414" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="724.9102" y2="744.9102"></line><polygon fill="#181818" points="265,734.9102,269,744.9102,273,734.9102,269,738.9102" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="187" x2="187" y1="1018.0781" y2="1038.0781"></line><polygon fill="#181818" points="183,1028.0781,187,1038.0781,191,1028.0781,187,1032.0781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351" x2="351" y1="1018.0781" y2="1038.0781"></line><polygon fill="#181818" points="347,1028.0781,351,1038.0781,355,1028.0781,351,1032.0781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="245" x2="187" y1="962.1094" y2="962.1094"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="187" x2="187" y1="962.1094" y2="984.1094"></line><polygon fill="#181818" points="183,974.1094,187,984.1094,191,974.1094,187,978.1094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="293" x2="351" y1="962.1094" y2="962.1094"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351" x2="351" y1="962.1094" y2="984.1094"></line><polygon fill="#181818" points="347,974.1094,351,984.1094,355,974.1094,351,978.1094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="925.25" y2="950.1094"></line><polygon fill="#181818" points="265,940.1094,269,950.1094,273,940.1094,269,944.1094" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="866.8789" y2="891.2813"></line><polygon fill="#181818" points="265,881.2813,269,891.2813,273,881.2813,269,885.2813" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="293" x2="568" y1="854.8789" y2="854.8789"></line><polygon fill="#181818" points="564,967.3047,568,977.3047,572,967.3047,568,971.3047" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="568" x2="568" y1="854.8789" y2="1082.0781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="568" x2="269" y1="1082.0781" y2="1082.0781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="1082.0781" y2="1102.0781"></line><polygon fill="#181818" points="265,1092.0781,269,1102.0781,273,1092.0781,269,1096.0781" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="822.8789" y2="842.8789"></line><polygon fill="#181818" points="265,832.8789,269,842.8789,273,832.8789,269,836.8789" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="352.5" x2="805.5" y1="1114.0781" y2="1114.0781"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="805.5" x2="805.5" y1="988.2891" y2="1114.0781"></line><polygon fill="#181818" points="801.5,998.2891,805.5,988.2891,809.5,998.2891,805.5,994.2891" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="805.5" x2="805.5" y1="810.8789" y2="954.3203"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="805.5" x2="281" y1="810.8789" y2="810.8789"></line><polygon fill="#181818" points="291,806.8789,281,810.8789,291,814.8789,287,810.8789" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="778.8789" y2="798.8789"></line><polygon fill="#181818" points="265,788.8789,269,798.8789,273,788.8789,269,792.8789" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="1126.0781" y2="1157.6328"></line><polygon fill="#181818" points="265,1147.6328,269,1157.6328,273,1147.6328,269,1151.6328" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="197.5,1102.0781,340.5,1102.0781,352.5,1114.0781,340.5,1126.0781,197.5,1126.0781,185.5,1114.0781,197.5,1102.0781" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml

start
if ( 8. IUPF is selected or not in step 4) then (yes)
    :PFCP Session Establishment Request with IUPF;
    repeat
        :Start T1 timer;
        if (Wait) then (PFCP Session Establishment Response)
            break
        endif
        -> T1 Timeout;
        backward:9. Retransmit PFCP Session Establishment Request with IUPF;
    repeat while (Number of retries < N1?) is (Yes) not (No)
    if (PFCP Session Establishment Positive Response?) then (No)
        :5.- Nsmf_PDUSession_CreateSMContext Negative Response
        - Release session without sending N1N2 to AMF;
        stop
    endif
    -> Yes;
endif
:10. Nsmf_PDUSession_CreateSMContext Response with hoState == PREPARING;
: Start Tsrn2 Timer;
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifstatementnested2(self, client):
        test_data = {
            "plantuml": """@startuml
if (hoState) then (hoState == PREPARED)
    if (Check N2 IE) then (N2 Handover Request Acknowledge Transfer)
        if (Default QoS flow in QoSFlowSetupResponseList IE?) then (Yes)
        else (No)
            :15.  Nsmf_PDUSession_UpdateSMContext Negative Response;
            :Start t4to5ho timer;
            if (Wait) then (t4to5ho Timeout)
                :16 Release Session;
                stop
            else (Nsmf_PDUSession_UpdateSMContext Request \n hoState == CANCELLED)
                :13. Rollback to EPS;
                stop
            endif
        endif
        :17. Handle optional AMF Change;
        :18. Nsmf_PDUSession_UpdateSMContext Response with hoState == PREPARED;
    else (N2 Handover Resource Allocation Unsuccessful Transfer)
        :19.  Nsmf_PDUSession_UpdateSMContext Negative Response;
        : Start t4to5ho timer;
        if (Wait) then (t4to5ho Timeout)
            :20. Release Session;
            stop
        else (Nsmf_PDUSession_UpdateSMContext Request \n hoState == CANCELLED)
            :13. Rollback to EPS;
            stop
        endif
    endif
else (hoState == CANCELLED)
    : 13. Rollback to EPS;
    stop
endif
end
@enduml""",
            "svg": """<polygon fill="#F1F1F1" points="842.125,12.0547,886.125,12.0547,898.125,24.0547,886.125,36.0547,842.125,36.0547,830.125,24.0547,842.125,12.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="44" x="842.125" y="27.707" style="pointer-events: none;">hoState</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="127" x="703.125" y="21.3047" style="pointer-events: none;">hoState == PREPARED</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="135" x="898.125" y="21.3047" style="pointer-events: none;">hoState == CANCELLED</text><polygon fill="#F1F1F1" points="501.75,46.0547,568.75,46.0547,580.75,58.0547,568.75,70.0547,501.75,70.0547,489.75,58.0547,501.75,46.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="67" x="501.75" y="61.707" style="pointer-events: none;">Check N2 IE</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="253" x="236.75" y="55.3047" style="pointer-events: none;">N2 Handover Request Acknowledge Transfer</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="321" x="580.75" y="55.3047" style="pointer-events: none;">N2 Handover Resource Allocation Unsuccessful Transfer</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="403" x="67.5" y="128.457"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="383" x="77.5" y="149.4258" style="pointer-events: none;">15.  Nsmf_PDUSession_UpdateSMContext Negative Response</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="141" x="198.5" y="197.4258"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="121" x="208.5" y="218.3945" style="pointer-events: none;">Start t4to5ho timer</text><polygon fill="#F1F1F1" points="257,268.0039,281,268.0039,293,280.0039,281,292.0039,257,292.0039,245,280.0039,257,268.0039" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="23" x="257.5" y="283.6563" style="pointer-events: none;">Wait</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="93" x="152" y="277.2539" style="pointer-events: none;">t4to5ho Timeout</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="261" x="293" y="264.4492" style="pointer-events: none;">Nsmf_PDUSession_UpdateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="135" x="297" y="277.2539" style="pointer-events: none;">hoState == CANCELLED</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="143" x="116.5" y="302.0039"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="123" x="126.5" y="322.9727" style="pointer-events: none;">16 Release Session</text><ellipse cx="188" cy="375.5703" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="188" cy="375.5703" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="141" x="279.5" y="302.0039"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="121" x="289.5" y="322.9727" style="pointer-events: none;">13. Rollback to EPS</text><ellipse cx="350" cy="375.5703" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="350" cy="375.5703" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="123.5,80.0547,414.5,80.0547,426.5,92.0547,414.5,104.0547,123.5,104.0547,111.5,92.0547,123.5,80.0547" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="15" x="273" y="114.1094" style="pointer-events: none;">No</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="291" x="123.5" y="95.707" style="pointer-events: none;">Default QoS flow in QoSFlowSetupResponseList IE?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="21" x="426.5" y="89.3047" style="pointer-events: none;">Yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="224" x="157" y="428.5703"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="204" x="167" y="449.5391" style="pointer-events: none;">17. Handle optional AMF Change</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="516" x="11" y="482.5391"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="496" x="21" y="503.5078" style="pointer-events: none;">18. Nsmf_PDUSession_UpdateSMContext Response with hoState == PREPARED</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="403" x="600" y="80.0547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="383" x="610" y="101.0234" style="pointer-events: none;">19.  Nsmf_PDUSession_UpdateSMContext Negative Response</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="145" x="729" y="149.0234"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="121" x="743" y="169.9922" style="pointer-events: none;">Start t4to5ho timer</text><polygon fill="#F1F1F1" points="789.5,219.6016,813.5,219.6016,825.5,231.6016,813.5,243.6016,789.5,243.6016,777.5,231.6016,789.5,219.6016" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="23" x="790" y="235.2539" style="pointer-events: none;">Wait</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="93" x="684.5" y="228.8516" style="pointer-events: none;">t4to5ho Timeout</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="261" x="825.5" y="216.0469" style="pointer-events: none;">Nsmf_PDUSession_UpdateSMContext Request</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="135" x="829.5" y="228.8516" style="pointer-events: none;">hoState == CANCELLED</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="147" x="646" y="253.6016"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="127" x="656" y="274.5703" style="pointer-events: none;">20. Release Session</text><ellipse cx="719.5" cy="333.5703" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="719.5" cy="333.5703" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="141" x="813" y="253.6016"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="121" x="823" y="274.5703" style="pointer-events: none;">13. Rollback to EPS</text><ellipse cx="883.5" cy="333.5703" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="883.5" cy="333.5703" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="145" x="1100.5" y="46.0547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="121" x="1114.5" y="67.0234" style="pointer-events: none;">13. Rollback to EPS</text><ellipse cx="1173" cy="126.0234" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="1173" cy="126.0234" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><ellipse cx="864.125" cy="546.5078" fill="transparent" rx="10" ry="10" style="stroke:#222222;stroke-width:1.5;"></ellipse><line style="stroke: rgb(34, 34, 34); stroke-width: 2.5; pointer-events: none;" x1="857.9378" x2="870.3122" y1="540.3206" y2="552.695"></line><line style="stroke: rgb(34, 34, 34); stroke-width: 2.5; pointer-events: none;" x1="870.3122" x2="857.9378" y1="540.3206" y2="552.695"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="162.4258" y2="197.4258"></line><polygon fill="#181818" points="265,187.4258,269,197.4258,273,187.4258,269,191.4258" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="188" x2="188" y1="335.9727" y2="364.5703"></line><polygon fill="#181818" points="184,354.5703,188,364.5703,192,354.5703,188,358.5703" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="350" x2="350" y1="335.9727" y2="364.5703"></line><polygon fill="#181818" points="346,354.5703,350,364.5703,354,354.5703,350,358.5703" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="245" x2="188" y1="280.0039" y2="280.0039"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="188" x2="188" y1="280.0039" y2="302.0039"></line><polygon fill="#181818" points="184,292.0039,188,302.0039,192,292.0039,188,296.0039" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="293" x2="350" y1="280.0039" y2="280.0039"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="350" x2="350" y1="280.0039" y2="302.0039"></line><polygon fill="#181818" points="346,292.0039,350,302.0039,354,292.0039,350,296.0039" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="231.3945" y2="268.0039"></line><polygon fill="#181818" points="265,258.0039,269,268.0039,273,258.0039,269,262.0039" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="104.0547" y2="128.457"></line><polygon fill="#181818" points="265,118.457,269,128.457,273,118.457,269,122.457" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="426.5" x2="568" y1="92.0547" y2="92.0547"></line><polygon fill="#181818" points="564,250.7148,568,260.7148,572,250.7148,568,254.7148" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="568" x2="568" y1="92.0547" y2="408.5703"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="568" x2="269" y1="408.5703" y2="408.5703"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="408.5703" y2="428.5703"></line><polygon fill="#181818" points="265,418.5703,269,428.5703,273,418.5703,269,422.5703" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="462.5391" y2="482.5391"></line><polygon fill="#181818" points="265,472.5391,269,482.5391,273,472.5391,269,476.5391" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="801.5" x2="801.5" y1="114.0234" y2="149.0234"></line><polygon fill="#181818" points="797.5,139.0234,801.5,149.0234,805.5,139.0234,801.5,143.0234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="719.5" x2="719.5" y1="287.5703" y2="322.5703"></line><polygon fill="#181818" points="715.5,312.5703,719.5,322.5703,723.5,312.5703,719.5,316.5703" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="883.5" x2="883.5" y1="287.5703" y2="322.5703"></line><polygon fill="#181818" points="879.5,312.5703,883.5,322.5703,887.5,312.5703,883.5,316.5703" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="777.5" x2="719.5" y1="231.6016" y2="231.6016"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="719.5" x2="719.5" y1="231.6016" y2="253.6016"></line><polygon fill="#181818" points="715.5,243.6016,719.5,253.6016,723.5,243.6016,719.5,247.6016" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="825.5" x2="883.5" y1="231.6016" y2="231.6016"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="883.5" x2="883.5" y1="231.6016" y2="253.6016"></line><polygon fill="#181818" points="879.5,243.6016,883.5,253.6016,887.5,243.6016,883.5,247.6016" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="801.5" x2="801.5" y1="182.9922" y2="219.6016"></line><polygon fill="#181818" points="797.5,209.6016,801.5,219.6016,805.5,209.6016,801.5,213.6016" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="489.75" x2="269" y1="58.0547" y2="58.0547"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="58.0547" y2="80.0547"></line><polygon fill="#181818" points="265,70.0547,269,80.0547,273,70.0547,269,74.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="580.75" x2="801.5" y1="58.0547" y2="58.0547"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="801.5" x2="801.5" y1="58.0547" y2="80.0547"></line><polygon fill="#181818" points="797.5,70.0547,801.5,80.0547,805.5,70.0547,801.5,74.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="269" y1="516.5078" y2="521.5078"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="269" x2="864.125" y1="521.5078" y2="521.5078"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="864.125" x2="864.125" y1="521.5078" y2="536.5078"></line><polygon fill="#181818" points="860.125,526.5078,864.125,536.5078,868.125,526.5078,864.125,530.5078" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="1173" x2="1173" y1="80.0234" y2="115.0234"></line><polygon fill="#181818" points="1169,105.0234,1173,115.0234,1177,105.0234,1173,109.0234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="830.125" x2="535.25" y1="24.0547" y2="24.0547"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="535.25" x2="535.25" y1="24.0547" y2="46.0547"></line><polygon fill="#181818" points="531.25,36.0547,535.25,46.0547,539.25,36.0547,535.25,40.0547" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="898.125" x2="1173" y1="24.0547" y2="24.0547"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="1173" x2="1173" y1="24.0547" y2="46.0547"></line><polygon fill="#181818" points="1169,36.0547,1173,46.0547,1177,36.0547,1173,40.0547" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="257,268.0039,281,268.0039,293,280.0039,281,292.0039,257,292.0039,245,280.0039,257,268.0039" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
if (hoState) then (hoState == PREPARED)
    if (Check N2 IE) then (N2 Handover Request Acknowledge Transfer)
        if (Default QoS flow in QoSFlowSetupResponseList IE?) then (Yes)
        else (No)
            :15.  Nsmf_PDUSession_UpdateSMContext Negative Response;
            :Start t4to5ho timer;
        endif
        :17. Handle optional AMF Change;
        :18. Nsmf_PDUSession_UpdateSMContext Response with hoState == PREPARED;
    else (N2 Handover Resource Allocation Unsuccessful Transfer)
        :19.  Nsmf_PDUSession_UpdateSMContext Negative Response;
        : Start t4to5ho timer;
        if (Wait) then (t4to5ho Timeout)
            :20. Release Session;
            stop
        else (Nsmf_PDUSession_UpdateSMContext Request \n hoState == CANCELLED)
            :13. Rollback to EPS;
            stop
        endif
    endif
else (hoState == CANCELLED)
    : 13. Rollback to EPS;
    stop
endif
end
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifstatementnestedemptyelse(self, client):
        test_data = {
            "plantuml": """@startuml
start
if (Statement) then (yes)
    :Activity;
    if (Statement) then (yes)
        :Activity;
    else (no)
        :Activity;
    endif
    :Activity;
else (no)
endif
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="98.4023"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="119.3711" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="64.5,152.3711,123.5,152.3711,135.5,164.3711,123.5,176.3711,64.5,176.3711,52.5,164.3711,64.5,152.3711" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="168.0234" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="161.6211" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="161.6211" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="186.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="207.3398" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="186.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="207.3398" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,226.3398,106,238.3398,94,250.3398,82,238.3398,94,226.3398" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="270.3398"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="291.3086" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="98" y="84.0547" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="65.6523" style="pointer-events: none;">Statement</text><polygon fill="#F1F1F1" points="94,324.3086,106,336.3086,94,348.3086,82,336.3086,94,324.3086" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="164.3711" y2="164.3711"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="164.3711" y2="186.3711"></line><polygon fill="#181818" points="38.5,176.3711,42.5,186.3711,46.5,176.3711,42.5,180.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="164.3711" y2="164.3711"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="164.3711" y2="186.3711"></line><polygon fill="#181818" points="141.5,176.3711,145.5,186.3711,149.5,176.3711,145.5,180.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="220.3398" y2="238.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="238.3398" y2="238.3398"></line><polygon fill="#181818" points="72,234.3398,82,238.3398,72,242.3398,76,238.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="220.3398" y2="238.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="238.3398" y2="238.3398"></line><polygon fill="#181818" points="116,234.3398,106,238.3398,116,242.3398,112,238.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="132.3711" y2="152.3711"></line><polygon fill="#181818" points="90,142.3711,94,152.3711,98,142.3711,94,146.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="250.3398" y2="270.3398"></line><polygon fill="#181818" points="90,260.3398,94,270.3398,98,260.3398,94,264.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="98.4023"></line><polygon fill="#181818" points="90,88.4023,94,98.4023,98,88.4023,94,92.4023" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="191" y1="62" y2="62"></line><polygon fill="#181818" points="187,191.3555,191,201.3555,195,191.3555,191,195.3555" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="191" y1="62" y2="336.3086"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="106" y1="336.3086" y2="336.3086"></line><polygon fill="#181818" points="116,332.3086,106,336.3086,116,340.3086,112,336.3086" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="304.3086" y2="324.3086"></line><polygon fill="#181818" points="90,314.3086,94,324.3086,98,314.3086,94,318.3086" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifstatementnestednoelse(self, client):
        test_data = {
            "plantuml": """@startuml
start
if (Statement) then (yes)
    :Activity;
    if (Statement) then (yes)
        :Activity;
    else (no)
        :Activity;
    endif
    :Activity;
endif
@enduml""",
            "svg": """<ellipse cx="94" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="98.4023"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="119.3711" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="64.5,152.3711,123.5,152.3711,135.5,164.3711,123.5,176.3711,64.5,176.3711,52.5,164.3711,64.5,152.3711" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="168.0234" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="161.6211" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="161.6211" style="pointer-events: none;">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="186.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="207.3398" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="186.3711"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="207.3398" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="94,226.3398,106,238.3398,94,250.3398,82,238.3398,94,226.3398" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="270.3398"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="291.3086" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="98" y="84.0547" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="65.6523" style="pointer-events: none;">Statement</text><polygon fill="#F1F1F1" points="94,324.3086,106,336.3086,94,348.3086,82,336.3086,94,324.3086" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="164.3711" y2="164.3711"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="164.3711" y2="186.3711"></line><polygon fill="#181818" points="38.5,176.3711,42.5,186.3711,46.5,176.3711,42.5,180.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="164.3711" y2="164.3711"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="164.3711" y2="186.3711"></line><polygon fill="#181818" points="141.5,176.3711,145.5,186.3711,149.5,176.3711,145.5,180.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="220.3398" y2="238.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="238.3398" y2="238.3398"></line><polygon fill="#181818" points="72,234.3398,82,238.3398,72,242.3398,76,238.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="220.3398" y2="238.3398"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="238.3398" y2="238.3398"></line><polygon fill="#181818" points="116,234.3398,106,238.3398,116,242.3398,112,238.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="132.3711" y2="152.3711"></line><polygon fill="#181818" points="90,142.3711,94,152.3711,98,142.3711,94,146.3711" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="250.3398" y2="270.3398"></line><polygon fill="#181818" points="90,260.3398,94,270.3398,98,260.3398,94,264.3398" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="74" y2="98.4023"></line><polygon fill="#181818" points="90,88.4023,94,98.4023,98,88.4023,94,92.4023" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="191" y1="62" y2="62"></line><polygon fill="#181818" points="187,191.3555,191,201.3555,195,191.3555,191,195.3555" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="191" y1="62" y2="336.3086"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="191" x2="106" y1="336.3086" y2="336.3086"></line><polygon fill="#181818" points="116,332.3086,106,336.3086,116,340.3086,112,336.3086" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="304.3086" y2="324.3086"></line><polygon fill="#181818" points="90,314.3086,94,324.3086,98,314.3086,94,318.3086" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="30" y2="50"></line><polygon fill="#181818" points="90,40,94,50,98,40,94,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,50,123.5,50,135.5,62,123.5,74,64.5,74,52.5,62,64.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifstatement_check_branch_cov(self, client):
        test_data = {
            "plantuml": """@startuml
start
if (Statement) then (yes)
    :Activity;
else (no)
    stop
endif
if (Statement) then (yes)
    stop
else (no)
    (A)
endif
end
@enduml""",
            "svg": """<g><ellipse cx="75.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="46,50,105,50,117,62,105,74,46,74,34,62,46,50" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="46" y="65.8081" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="14" y="59.4058" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="117" y="59.4058" style="pointer-events: none;">no</text><ellipse cx="24" cy="94" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M24.1094,90.1719 L22.5,94.5156 L25.7188,94.5156 L24.1094,90.1719 Z M23.4375,89 L24.7813,89 L28.1094,97.75 L26.875,97.75 L26.0781,95.5 L22.1406,95.5 L21.3438,97.75 L20.0938,97.75 L23.4375,89 Z " fill="#000000" style="pointer-events: none;"></path><ellipse cx="127" cy="95" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;fill:none;"></ellipse><ellipse cx="127" cy="95" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="46,126,105,126,117,138,105,150,46,150,34,138,46,126" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="46" y="141.8081" style="pointer-events: none;">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="14" y="135.4058" style="pointer-events: none;">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="117" y="135.4058" style="pointer-events: none;">no</text><ellipse cx="24" cy="171" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;fill:none;"></ellipse><ellipse cx="24" cy="171" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><ellipse cx="127" cy="170" fill="#F1F1F1" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M127.1094,166.1719 L125.5,170.5156 L128.7188,170.5156 L127.1094,166.1719 Z M126.4375,165 L127.7813,165 L131.1094,173.75 L129.875,173.75 L129.0781,171.5 L125.1406,171.5 L124.3438,173.75 L123.0938,173.75 L126.4375,165 Z " fill="#000000" style="pointer-events: none;"></path><ellipse cx="75.5" cy="212" rx="10" ry="10" style="stroke:#222222;stroke-width:1.5;fill:transparent;" fill="transparent"></ellipse><line style="stroke: rgb(34, 34, 34); stroke-width: 2.5; fill: none; pointer-events: none;" x1="69.3128" x2="81.6872" y1="205.8128" y2="218.1872"></line><line style="stroke: rgb(34, 34, 34); stroke-width: 2.5; fill: none; pointer-events: none;" x1="81.6872" x2="69.3128" y1="205.8128" y2="218.1872"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; fill: none; pointer-events: none;" x1="34" x2="24" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; fill: none; pointer-events: none;" x1="24" x2="24" y1="62" y2="84"></line><polygon fill="#181818" points="20,74,24,84,28,74,24,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="117" x2="127" y1="62" y2="62"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="127" x2="127" y1="62" y2="84"></line><polygon fill="#181818" points="123,74,127,84,131,74,127,78" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="104" y2="111"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="75.5" y1="111" y2="111"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="75.5" x2="75.5" y1="111" y2="126"></line><polygon fill="#181818" points="71.5,116,75.5,126,79.5,116,75.5,120" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="75.5" x2="75.5" y1="30" y2="50"></line><polygon fill="#181818" points="71.5,40,75.5,50,79.5,40,75.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="34" x2="24" y1="138" y2="138"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="24" x2="24" y1="138" y2="160"></line><polygon fill="#181818" points="20,150,24,160,28,150,24,154" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="117" x2="127" y1="138" y2="138"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="127" x2="127" y1="138" y2="160"></line><polygon fill="#181818" points="123,150,127,160,131,150,127,154" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="127" x2="127" y1="180" y2="187"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="127" x2="75.5" y1="187" y2="187"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="75.5" x2="75.5" y1="187" y2="202"></line><polygon fill="#181818" points="71.5,192,75.5,202,79.5,192,75.5,196" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="46,126,105,126,117,138,105,150,46,150,34,138,46,126" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
if (Statement) then (yes)
    :Activity;
else (no)
    stop
endif
end
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deleteifstatement(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
detach
else (no)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="159.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="169.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="167.5,64.9688,226.5,64.9688,238.5,76.9688,226.5,88.9688,167.5,88.9688,155.5,76.9688,167.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="167.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="135.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="238.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="62.5" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="72.5" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="64.5,152.9375,123.5,152.9375,135.5,164.9375,123.5,176.9375,64.5,176.9375,52.5,164.9375,64.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="168.5898">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="162.1875">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="162.1875">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="207.9063">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="207.9063">Activity</text><polygon fill="#F1F1F1" points="94,226.9063,106,238.9063,94,250.9063,82,238.9063,94,226.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="268.5" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="278.5" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="270.5,152.9375,329.5,152.9375,341.5,164.9375,329.5,176.9375,270.5,176.9375,258.5,164.9375,270.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="270.5" y="168.5898">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="238.5" y="162.1875">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="341.5" y="162.1875">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="217" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="227" y="207.9063">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="320" y="186.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="330" y="207.9063">Activity</text><polygon fill="#F1F1F1" points="300,226.9063,312,238.9063,300,250.9063,288,238.9063,300,226.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="197,256.9063,209,268.9063,197,280.9063,185,268.9063,197,256.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="38.5,176.9375,42.5,186.9375,46.5,176.9375,42.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="141.5,176.9375,145.5,186.9375,149.5,176.9375,145.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="72,234.9063,82,238.9063,72,242.9063,76,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="116,234.9063,106,238.9063,116,242.9063,112,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="132.9375" y2="152.9375"></line><polygon fill="#181818" points="90,142.9375,94,152.9375,98,142.9375,94,146.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="258.5" x2="248.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="248.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="244.5,176.9375,248.5,186.9375,252.5,176.9375,248.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="341.5" x2="351.5" y1="164.9375" y2="164.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="164.9375" y2="186.9375"></line><polygon fill="#181818" points="347.5,176.9375,351.5,186.9375,355.5,176.9375,351.5,180.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="248.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="248.5" x2="288" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="278,234.9063,288,238.9063,278,242.9063,282,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="351.5" y1="220.9063" y2="238.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="351.5" x2="312" y1="238.9063" y2="238.9063"></line><polygon fill="#181818" points="322,234.9063,312,238.9063,322,242.9063,318,238.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="132.9375" y2="152.9375"></line><polygon fill="#181818" points="296,142.9375,300,152.9375,304,142.9375,300,146.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="155.5" x2="94" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="90,88.9688,94,98.9688,98,88.9688,94,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="238.5" x2="300" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="296,88.9688,300,98.9688,304,88.9688,300,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="250.9063" y2="268.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="185" y1="268.9063" y2="268.9063"></line><polygon fill="#181818" points="175,264.9063,185,268.9063,175,272.9063,179,268.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="300" y1="250.9063" y2="268.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="300" x2="209" y1="268.9063" y2="268.9063"></line><polygon fill="#181818" points="219,264.9063,209,268.9063,219,272.9063,215,268.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="197" x2="197" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="193,54.9688,197,64.9688,201,54.9688,197,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,152.9375,123.5,152.9375,135.5,164.9375,123.5,176.9375,64.5,176.9375,52.5,164.9375,64.5,152.9375" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/delIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_get_text_no_branchif(self, client):
        test_data = {
            "plantuml": """@startuml

start
-> 1;
: 1. Nsmf_PDUSession_CreateSMContext Request;
if (statement1a) then (downa)
    :2;
    stop
else (righta)
endif

:3;
:4;
if (statement2) then (down)
    :5;
    stop
else (right)
endif
:Activity;
@enduml""",
            "svg": """<ellipse cx="172" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="322" x="11" y="71.5547"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="298" x="25" y="92.5234" style="pointer-events: none;">1. Nsmf_PDUSession_CreateSMContext Request</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="158" y="173.9258"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="168" y="194.8945" style="pointer-events: none;">2</text><ellipse cx="172" cy="247.4102" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="172" cy="247.4102" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="136,125.5234,208,125.5234,220,137.5234,208,149.5234,136,149.5234,124,137.5234,136,125.5234" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="37" x="176" y="159.5781" style="pointer-events: none;">downa</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="72" x="136" y="141.1758" style="pointer-events: none;">statement1a</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="33" x="220" y="134.7734" style="pointer-events: none;">righta</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="158" y="300.4102"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="168" y="321.3789" style="pointer-events: none;">3</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="158" y="354.3789"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="168" y="375.3477" style="pointer-events: none;">4</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="28" x="158" y="456.75"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="8" x="168" y="477.7188" style="pointer-events: none;">5</text><ellipse cx="172" cy="530.2344" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="172" cy="530.2344" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><polygon fill="#F1F1F1" points="139.5,408.3477,204.5,408.3477,216.5,420.3477,204.5,432.3477,139.5,432.3477,127.5,420.3477,139.5,408.3477" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="30" x="176" y="442.4023" style="pointer-events: none;">down</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="65" x="139.5" y="424" style="pointer-events: none;">statement2</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="26" x="216.5" y="417.5977" style="pointer-events: none;">right</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="140.5" y="583.2344"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="150.5" y="604.2031" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="30" y2="71.5547"></line><polygon fill="#181818" points="168,61.5547,172,71.5547,176,61.5547,172,65.5547" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="7" x="176" y="51.3047">1</text><line style="stroke:#181818;stroke-width:1.0;" x1="172" x2="172" y1="207.8945" y2="236.4102"></line><polygon fill="#181818" points="168,226.4102,172,236.4102,176,226.4102,172,230.4102" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="149.5234" y2="173.9258"></line><polygon fill="#181818" points="168,163.9258,172,173.9258,176,163.9258,172,167.9258" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220" x2="232" y1="137.5234" y2="137.5234"></line><polygon fill="#181818" points="228,206.4102,232,216.4102,236,206.4102,232,210.4102" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="232" x2="232" y1="137.5234" y2="280.4102"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="232" x2="172" y1="280.4102" y2="280.4102"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="280.4102" y2="300.4102"></line><polygon fill="#181818" points="168,290.4102,172,300.4102,176,290.4102,172,294.4102" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="105.5234" y2="125.5234"></line><polygon fill="#181818" points="168,115.5234,172,125.5234,176,115.5234,172,119.5234" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="334.3789" y2="354.3789"></line><polygon fill="#181818" points="168,344.3789,172,354.3789,176,344.3789,172,348.3789" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="490.7188" y2="519.2344"></line><polygon fill="#181818" points="168,509.2344,172,519.2344,176,509.2344,172,513.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="432.3477" y2="456.75"></line><polygon fill="#181818" points="168,446.75,172,456.75,176,446.75,172,450.75" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="216.5" x2="228.5" y1="420.3477" y2="420.3477"></line><polygon fill="#181818" points="224.5,489.2344,228.5,499.2344,232.5,489.2344,228.5,493.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="228.5" x2="228.5" y1="420.3477" y2="563.2344"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="228.5" x2="172" y1="563.2344" y2="563.2344"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="563.2344" y2="583.2344"></line><polygon fill="#181818" points="168,573.2344,172,583.2344,176,573.2344,172,577.2344" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="172" x2="172" y1="388.3477" y2="408.3477"></line><polygon fill="#181818" points="168,398.3477,172,408.3477,176,398.3477,172,402.3477" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="139.5,408.3477,204.5,408.3477,216.5,420.3477,204.5,432.3477,139.5,432.3477,127.5,420.3477,139.5,408.3477" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getTextPoly",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = ["statement2", "down", "right"]
            assert json.loads(response.data.decode("utf-8")) == expected_result

    def test_gettextpoly(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (Statement) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="56.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="66.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="59" x="64.5" y="80.6211">Statement</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="32.5" y="74.2188">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="135.5" y="74.2188">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="119.9375">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="114" y="98.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="124" y="119.9375">Activity</text><polygon fill="#F1F1F1" points="94,138.9375,106,150.9375,94,162.9375,82,150.9375,94,138.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="42.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="38.5,88.9688,42.5,98.9688,46.5,88.9688,42.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="135.5" x2="145.5" y1="76.9688" y2="76.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="76.9688" y2="98.9688"></line><polygon fill="#181818" points="141.5,88.9688,145.5,98.9688,149.5,88.9688,145.5,92.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="82" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="72,146.9375,82,150.9375,72,154.9375,76,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="145.5" y1="132.9375" y2="150.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="145.5" x2="106" y1="150.9375" y2="150.9375"></line><polygon fill="#181818" points="116,146.9375,106,150.9375,116,154.9375,112,150.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="94" x2="94" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="90,54.9688,94,64.9688,98,54.9688,94,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<polygon fill="#F1F1F1" points="64.5,64.9688,123.5,64.9688,135.5,76.9688,123.5,88.9688,64.5,88.9688,52.5,76.9688,64.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/getTextPoly",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_result = ["Statement", "yes", "no"]
            assert json.loads(response.data.decode("utf-8")) == expected_result

    def test_editmultilineifstatement(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
if (hej
hej) then (yes
yes)
  :Activity;
else (no
no)
  :Activity;
endif
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="46.5" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="56.5" y="31.9688">Activity 1</text><polygon fill="#F1F1F1" points="72,69.0234,96,69.0234,108,81.8281,96,94.6328,72,94.6328,60,81.8281,72,69.0234" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="75.5" y="79.0781">hej</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="17" x="75.5" y="91.8828">hej</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="40" y="66.2734">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="40" y="79.0781">yes</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="108" y="66.2734">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="108" y="79.0781">no</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="104.6328"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="125.6016">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="94" y="104.6328"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="104" y="125.6016">Activity</text><polygon fill="#F1F1F1" points="84,144.6016,96,156.6016,84,168.6016,72,156.6016,84,144.6016" style="stroke:#181818;stroke-width:0.5;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="60" x2="42.5" y1="81.8281" y2="81.8281"></line><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="81.8281" y2="104.6328"></line><polygon fill="#181818" points="38.5,94.6328,42.5,104.6328,46.5,94.6328,42.5,98.6328" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="108" x2="125.5" y1="81.8281" y2="81.8281"></line><line style="stroke:#181818;stroke-width:1.0;" x1="125.5" x2="125.5" y1="81.8281" y2="104.6328"></line><polygon fill="#181818" points="121.5,94.6328,125.5,104.6328,129.5,94.6328,125.5,98.6328" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="138.6016" y2="156.6016"></line><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="72" y1="156.6016" y2="156.6016"></line><polygon fill="#181818" points="62,152.6016,72,156.6016,62,160.6016,66,156.6016" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="125.5" x2="125.5" y1="138.6016" y2="156.6016"></line><line style="stroke:#181818;stroke-width:1.0;" x1="125.5" x2="96" y1="156.6016" y2="156.6016"></line><polygon fill="#181818" points="106,152.6016,96,156.6016,106,160.6016,102,156.6016" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="84" x2="84" y1="44.9688" y2="69.0234"></line><polygon fill="#181818" points="80,59.0234,84,69.0234,88,59.0234,84,63.0234" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "statement": "hej",
            "branch1": "yes",
            "branch2": "no",
            "svgelement": """<polygon fill="#F1F1F1" points="72,69.0234,96,69.0234,108,81.8281,96,94.6328,72,94.6328,60,81.8281,72,69.0234" style="stroke:#181818;stroke-width:0.5;"></polygon>""",
        }
        with client:
            response = client.post(
                "/editTextIf",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
if (hej) then (yes)
  :Activity;
else (no)
  :Activity;
endif
@enduml"""
            assert response.data.decode("utf-8") == expected_puml


class TestAppRoutesFork:
    def test_delfork3(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action;
fork again
  :action;
fork
  :action;
fork again
  :action;
end fork
end fork
  :Activity;
@enduml""",
            "line": 11,
        }
        with client:
            response = client.post(
                "/deleteFork2",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
  :Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_delfork2(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action;
fork again
  :action;
end fork
@enduml""",
            "line": 6,
        }
        with client:
            response = client.post(
                "/deleteFork2",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_togglefork3(self, client):
        test_data = {
            "plantuml": """@startuml
fork
    :action;
end fork
@enduml""",
            "line": 3,
        }
        with client:
            response = client.post(
                "/forkToggle2",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
fork
    :action;
end merge
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_togglefork2(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action;
fork again
  :action;
end fork
@enduml""",
            "line": 6,
        }
        with client:
            response = client.post(
                "/forkToggle2",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
fork
  :action;
fork again
  :action;
end merge
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addtofork(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action;
fork again
  :action;
end fork
@enduml""",
            "line": 6,
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToFork",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
fork
  :action;
fork again
  :action;
end fork
:Activity 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_forktogglefork(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
end merge
stop
@enduml""",
            "svg": """<ellipse cx="139.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="23" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="33" y="96.9688" style="pointer-events: none;">action 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="104" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="114" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="185" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="195" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="129.9688"></rect><ellipse cx="139.5" cy="166.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="139.5" cy="166.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="56" y2="76"></line><polygon fill="#181818" points="54.5,66,58.5,76,62.5,66,58.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="56" y2="76"></line><polygon fill="#181818" points="135.5,66,139.5,76,143.5,66,139.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="56" y2="76"></line><polygon fill="#181818" points="216.5,66,220.5,76,224.5,66,220.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="54.5,119.9688,58.5,129.9688,62.5,119.9688,58.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="135.5,119.9688,139.5,129.9688,143.5,119.9688,139.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="216.5,119.9688,220.5,129.9688,224.5,119.9688,220.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="30" y2="50"></line><polygon fill="#181818" points="135.5,40,139.5,50,143.5,40,139.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="135.5,145.9688,139.5,155.9688,143.5,145.9688,139.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect>""",
        }
        with client:
            response = client.post(
                "/forkToggle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
end fork
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_forktogglemerge(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
end fork
stop
@enduml""",
            "svg": """<ellipse cx="139.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="23" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="33" y="96.9688" style="pointer-events: none;">action 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="104" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="114" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="185" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="195" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="129.9688"></rect><ellipse cx="139.5" cy="166.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="139.5" cy="166.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="56" y2="76"></line><polygon fill="#181818" points="54.5,66,58.5,76,62.5,66,58.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="56" y2="76"></line><polygon fill="#181818" points="135.5,66,139.5,76,143.5,66,139.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="56" y2="76"></line><polygon fill="#181818" points="216.5,66,220.5,76,224.5,66,220.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="54.5,119.9688,58.5,129.9688,62.5,119.9688,58.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="135.5,119.9688,139.5,129.9688,143.5,119.9688,139.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="216.5,119.9688,220.5,129.9688,224.5,119.9688,220.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="30" y2="50"></line><polygon fill="#181818" points="135.5,40,139.5,50,143.5,40,139.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="135.5,145.9688,139.5,155.9688,143.5,145.9688,139.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect>""",
        }
        with client:
            response = client.post(
                "/forkToggle",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
end merge
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_forkagainwithnestedmerge(self, client):
        test_data = {
            "plantuml": """@startuml
fork
  :action;
fork again
  :action;
fork
  :action;
fork again
  :action;
fork again
  :action;
end merge
fork again
  :action;
fork
  :action;
fork again
  :action;
fork
  :action;
fork again
  :acation;
end fork
fork again
  :actioasdn;
fork again
  :action;
fork again
  :action;
end fork
end fork
stop
@enduml""",
            "svg": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="856.5" x="11" y="11"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="23" y="157.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="33" y="178.9375" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="173" y="88.4844"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="183" y="109.4531" style="pointer-events: none;">action</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="221" x="92" y="157.4531"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="104" y="183.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="114" y="204.4219" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="173" y="183.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="183" y="204.4219" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="242" y="183.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="252" y="204.4219" style="pointer-events: none;">action</text><polygon fill="#F1F1F1" points="202.5,237.4219,214.5,249.4219,202.5,261.4219,190.5,249.4219,202.5,237.4219" style="stroke:#181818;stroke-width:0.5;"></polygon><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="573.5" y="37"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="583.5" y="57.9688" style="pointer-events: none;">action</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="532.5" x="323" y="105.9688"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="335" y="192.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="345" y="213.4219" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="475" y="131.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="485" y="152.9375" style="pointer-events: none;">action</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="182" x="413.5" y="200.9375"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="427.5" y="226.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="437.5" y="247.9063" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="67" x="514.5" y="226.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="47" x="524.5" y="247.9063" style="pointer-events: none;">acation</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="182" x="413.5" y="280.9063"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="82" x="623.5" y="192.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="62" x="633.5" y="213.4219" style="pointer-events: none;">actioasdn</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="715.5" y="192.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="725.5" y="213.4219" style="pointer-events: none;">action</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="59" x="784.5" y="192.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="39" x="794.5" y="213.4219" style="pointer-events: none;">action</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="532.5" x="323" y="306.9063"></rect><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="856.5" x="11" y="332.9063"></rect><ellipse cx="415" cy="369.9063" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="415" cy="369.9063" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133.5" x2="133.5" y1="163.4531" y2="183.4531"></line><polygon fill="#181818" points="129.5,173.4531,133.5,183.4531,137.5,173.4531,133.5,177.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="202.5" x2="202.5" y1="163.4531" y2="183.4531"></line><polygon fill="#181818" points="198.5,173.4531,202.5,183.4531,206.5,173.4531,202.5,177.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="271.5" x2="271.5" y1="163.4531" y2="183.4531"></line><polygon fill="#181818" points="267.5,173.4531,271.5,183.4531,275.5,173.4531,271.5,177.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133.5" x2="133.5" y1="217.4219" y2="249.4219"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="133.5" x2="190.5" y1="249.4219" y2="249.4219"></line><polygon fill="#181818" points="180.5,245.4219,190.5,249.4219,180.5,253.4219,184.5,249.4219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="202.5" x2="202.5" y1="217.4219" y2="237.4219"></line><polygon fill="#181818" points="198.5,227.4219,202.5,237.4219,206.5,227.4219,202.5,231.4219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="271.5" x2="271.5" y1="217.4219" y2="249.4219"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="271.5" x2="214.5" y1="249.4219" y2="249.4219"></line><polygon fill="#181818" points="224.5,245.4219,214.5,249.4219,224.5,253.4219,220.5,249.4219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="202.5" x2="202.5" y1="122.4531" y2="157.4531"></line><polygon fill="#181818" points="198.5,147.4531,202.5,157.4531,206.5,147.4531,202.5,151.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="457" x2="457" y1="206.9375" y2="226.9375"></line><polygon fill="#181818" points="453,216.9375,457,226.9375,461,216.9375,457,220.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="548" x2="548" y1="206.9375" y2="226.9375"></line><polygon fill="#181818" points="544,216.9375,548,226.9375,552,216.9375,548,220.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="457" x2="457" y1="260.9063" y2="280.9063"></line><polygon fill="#181818" points="453,270.9063,457,280.9063,461,270.9063,457,274.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="548" x2="548" y1="260.9063" y2="280.9063"></line><polygon fill="#181818" points="544,270.9063,548,280.9063,552,270.9063,548,274.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="504.5" x2="504.5" y1="165.9375" y2="200.9375"></line><polygon fill="#181818" points="500.5,190.9375,504.5,200.9375,508.5,190.9375,504.5,194.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="364.5" x2="364.5" y1="111.9688" y2="192.4531"></line><polygon fill="#181818" points="360.5,182.4531,364.5,192.4531,368.5,182.4531,364.5,186.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="504.5" x2="504.5" y1="111.9688" y2="131.9688"></line><polygon fill="#181818" points="500.5,121.9688,504.5,131.9688,508.5,121.9688,504.5,125.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="664.5" x2="664.5" y1="111.9688" y2="192.4531"></line><polygon fill="#181818" points="660.5,182.4531,664.5,192.4531,668.5,182.4531,664.5,186.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="745" x2="745" y1="111.9688" y2="192.4531"></line><polygon fill="#181818" points="741,182.4531,745,192.4531,749,182.4531,745,186.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="814" x2="814" y1="111.9688" y2="192.4531"></line><polygon fill="#181818" points="810,182.4531,814,192.4531,818,182.4531,814,186.4531" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="364.5" x2="364.5" y1="226.4219" y2="306.9063"></line><polygon fill="#181818" points="360.5,296.9063,364.5,306.9063,368.5,296.9063,364.5,300.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="504.5" x2="504.5" y1="286.9063" y2="306.9063"></line><polygon fill="#181818" points="500.5,296.9063,504.5,306.9063,508.5,296.9063,504.5,300.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="664.5" x2="664.5" y1="226.4219" y2="306.9063"></line><polygon fill="#181818" points="660.5,296.9063,664.5,306.9063,668.5,296.9063,664.5,300.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="745" x2="745" y1="226.4219" y2="306.9063"></line><polygon fill="#181818" points="741,296.9063,745,306.9063,749,296.9063,745,300.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="814" x2="814" y1="226.4219" y2="306.9063"></line><polygon fill="#181818" points="810,296.9063,814,306.9063,818,296.9063,814,300.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="603" x2="603" y1="70.9688" y2="105.9688"></line><polygon fill="#181818" points="599,95.9688,603,105.9688,607,95.9688,603,99.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="52.5" y1="17" y2="157.9688"></line><polygon fill="#181818" points="48.5,147.9688,52.5,157.9688,56.5,147.9688,52.5,151.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="202.5" x2="202.5" y1="17" y2="88.4844"></line><polygon fill="#181818" points="198.5,78.4844,202.5,88.4844,206.5,78.4844,202.5,82.4844" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="603" x2="603" y1="17" y2="37"></line><polygon fill="#181818" points="599,27,603,37,607,27,603,31" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="52.5" x2="52.5" y1="191.9375" y2="332.9063"></line><polygon fill="#181818" points="48.5,322.9063,52.5,332.9063,56.5,322.9063,52.5,326.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="202.5" x2="202.5" y1="261.4219" y2="332.9063"></line><polygon fill="#181818" points="198.5,322.9063,202.5,332.9063,206.5,322.9063,202.5,326.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="603" x2="603" y1="312.9063" y2="332.9063"></line><polygon fill="#181818" points="599,322.9063,603,332.9063,607,322.9063,603,326.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="415" x2="415" y1="338.9063" y2="358.9063"></line><polygon fill="#181818" points="411,348.9063,415,358.9063,419,348.9063,415,352.9063" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="532.5" x="323" y="105.9688"></rect>""",
        }
        with client:
            response = client.post(
                "/forkAgain",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
fork
  :action;
fork again
  :action;
fork
  :action;
fork again
  :action;
fork again
  :action;
end merge
fork again
  :action;
fork
  :action;
fork again
  :action;
fork
  :action;
fork again
  :acation;
end fork
fork again
  :actioasdn;
fork again
  :action;
fork again
  :action;
fork again
  :action;
end fork
end fork
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_forkagain(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
end fork
stop
@enduml""",
            "svg": """<ellipse cx="139.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="23" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="33" y="96.9688" style="pointer-events: none;">action 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="104" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="114" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="185" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="195" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="129.9688"></rect><ellipse cx="139.5" cy="166.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="139.5" cy="166.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="56" y2="76"></line><polygon fill="#181818" points="54.5,66,58.5,76,62.5,66,58.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="56" y2="76"></line><polygon fill="#181818" points="135.5,66,139.5,76,143.5,66,139.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="56" y2="76"></line><polygon fill="#181818" points="216.5,66,220.5,76,224.5,66,220.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="54.5,119.9688,58.5,129.9688,62.5,119.9688,58.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="135.5,119.9688,139.5,129.9688,143.5,119.9688,139.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="216.5,119.9688,220.5,129.9688,224.5,119.9688,220.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="30" y2="50"></line><polygon fill="#181818" points="135.5,40,139.5,50,143.5,40,139.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="135.5,145.9688,139.5,155.9688,143.5,145.9688,139.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect>""",
        }
        with client:
            response = client.post(
                "/forkAgain",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
fork again
  :action;
end fork
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deletenestedfork(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action 2;
fork
:action 1;
fork again
:action 2;
end fork
fork again
  :action 2;
fork
:action 1;
fork again
:action 2;
end fork
end fork
stop
@enduml""",
            "svg": """<ellipse cx="231" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="440" x="11" y="50"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="84.5" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="94.5" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="194" x="23" y="129.9688"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="35" y="155.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="45" y="176.9375" style="pointer-events: none;">action 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="134" y="155.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="144" y="176.9375" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="194" x="23" y="209.9375"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="306.5" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="316.5" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="194" x="245" y="129.9688"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="257" y="155.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="267" y="176.9375" style="pointer-events: none;">action 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="356" y="155.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="366" y="176.9375" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="194" x="245" y="209.9375"></rect><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="440" x="11" y="235.9375"></rect><ellipse cx="231" cy="272.9375" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="231" cy="272.9375" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="70.5" x2="70.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="66.5,145.9688,70.5,155.9688,74.5,145.9688,70.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="169.5" x2="169.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="165.5,145.9688,169.5,155.9688,173.5,145.9688,169.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="70.5" x2="70.5" y1="189.9375" y2="209.9375"></line><polygon fill="#181818" points="66.5,199.9375,70.5,209.9375,74.5,199.9375,70.5,203.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="169.5" x2="169.5" y1="189.9375" y2="209.9375"></line><polygon fill="#181818" points="165.5,199.9375,169.5,209.9375,173.5,199.9375,169.5,203.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="120" x2="120" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="116,119.9688,120,129.9688,124,119.9688,120,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="292.5" x2="292.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="288.5,145.9688,292.5,155.9688,296.5,145.9688,292.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="391.5" x2="391.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="387.5,145.9688,391.5,155.9688,395.5,145.9688,391.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="292.5" x2="292.5" y1="189.9375" y2="209.9375"></line><polygon fill="#181818" points="288.5,199.9375,292.5,209.9375,296.5,199.9375,292.5,203.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="391.5" x2="391.5" y1="189.9375" y2="209.9375"></line><polygon fill="#181818" points="387.5,199.9375,391.5,209.9375,395.5,199.9375,391.5,203.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="342" x2="342" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="338,119.9688,342,129.9688,346,119.9688,342,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="120" x2="120" y1="56" y2="76"></line><polygon fill="#181818" points="116,66,120,76,124,66,120,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="342" x2="342" y1="56" y2="76"></line><polygon fill="#181818" points="338,66,342,76,346,66,342,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="120" x2="120" y1="215.9375" y2="235.9375"></line><polygon fill="#181818" points="116,225.9375,120,235.9375,124,225.9375,120,229.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="342" x2="342" y1="215.9375" y2="235.9375"></line><polygon fill="#181818" points="338,225.9375,342,235.9375,346,225.9375,342,229.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="231" x2="231" y1="30" y2="50"></line><polygon fill="#181818" points="227,40,231,50,235,40,231,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="231" x2="231" y1="241.9375" y2="261.9375"></line><polygon fill="#181818" points="227,251.9375,231,261.9375,235,251.9375,231,255.9375" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="194" x="245" y="129.9688"></rect>""",
        }
        with client:
            response = client.post(
                "/deleteFork",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
fork
  :action 2;
fork
:action 1;
fork again
:action 2;
end fork
fork again
  :action 2;
end fork
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_deletefork(self, client):
        test_data = {
            "plantuml": """@startuml
start
fork
  :action 1;
fork again
  :action 2;
fork again
  :action 2;
end fork
stop
@enduml""",
            "svg": """<ellipse cx="139.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="23" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="33" y="96.9688" style="pointer-events: none;">action 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="104" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="114" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="185" y="76"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="195" y="96.9688" style="pointer-events: none;">action 2</text><rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="129.9688"></rect><ellipse cx="139.5" cy="166.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="139.5" cy="166.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="56" y2="76"></line><polygon fill="#181818" points="54.5,66,58.5,76,62.5,66,58.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="56" y2="76"></line><polygon fill="#181818" points="135.5,66,139.5,76,143.5,66,139.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="56" y2="76"></line><polygon fill="#181818" points="216.5,66,220.5,76,224.5,66,220.5,70" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="58.5" x2="58.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="54.5,119.9688,58.5,129.9688,62.5,119.9688,58.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="135.5,119.9688,139.5,129.9688,143.5,119.9688,139.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="220.5" x2="220.5" y1="109.9688" y2="129.9688"></line><polygon fill="#181818" points="216.5,119.9688,220.5,129.9688,224.5,119.9688,220.5,123.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="30" y2="50"></line><polygon fill="#181818" points="135.5,40,139.5,50,143.5,40,139.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="139.5" x2="139.5" y1="135.9688" y2="155.9688"></line><polygon fill="#181818" points="135.5,145.9688,139.5,155.9688,143.5,145.9688,139.5,149.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#555555" height="6" rx="2.5" ry="2.5" style="stroke:#555555;stroke-width:1.0;" width="257" x="11" y="50"></rect>""",
        }
        with client:
            response = client.post(
                "/deleteFork",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
stop
@enduml"""
            assert response.data.decode("utf-8") == expected_puml


class TestAppRoutesActivity:
    def test_break_colored_activity_with_colored_connector(self, client):
        test_data = {
            "plantuml": """@startuml
start
#green:(A)
#red:Activity;
:Activity;
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="42.5" cy="60" fill="#008000" rx="10" ry="10" style="stroke:#181818;stroke-width:0.5;"></ellipse><path d="M42.6094,56.1719 L41,60.5156 L44.2188,60.5156 L42.6094,56.1719 Z M41.9375,55 L43.2813,55 L46.6094,63.75 L45.375,63.75 L44.5781,61.5 L40.6406,61.5 L39.8438,63.75 L38.5938,63.75 L41.9375,55 Z " fill="#000000" style="pointer-events: none;"></path><rect fill="#FF0000" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="90"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="111.1387" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="143.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="165.1074" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="50"></line><polygon fill="#181818" points="38.5,40,42.5,50,46.5,40,42.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="70" y2="90"></line><polygon fill="#181818" points="38.5,80,42.5,90,46.5,80,42.5,84" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="123.9688" y2="143.9688"></line><polygon fill="#181818" points="38.5,133.9688,42.5,143.9688,46.5,133.9688,42.5,137.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#FF0000" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="90"></rect>""",
        }
        with client:
            response = client.post(
                "/breakActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
#green:(A)
#red:Activity;
break
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addarrow3(self, client):
        test_data = {
            "plantuml": """@startuml
start
-> Arrow label 1;
:Activity;
:Activity;
@enduml""",
            "svg": """<ellipse cx="42.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="71.3989"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="92.5376" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="125.3677"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="146.5063" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="42.5" x2="42.5" y1="30" y2="71.3989"></line><polygon fill="#181818" points="38.5,61.3989,42.5,71.3989,46.5,61.3989,42.5,65.3989" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="75" x="46.5" y="51.3047">Arrow label 1</text><line style="stroke:#181818;stroke-width:1.0;" x1="42.5" x2="42.5" y1="105.3677" y2="125.3677"></line><polygon fill="#181818" points="38.5,115.3677,42.5,125.3677,46.5,115.3677,42.5,119.3677" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="125.3677"></rect>""",
            "where": "below",
        }
        with client:
            response = client.post(
                "/addArrowLabel",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
-> Arrow label 1;
:Activity;
:Activity;
-> Arrow label 2;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addarrow2(self, client):
        test_data = {
            "plantuml": """@startuml
start
  :Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect>""",
            "where": "below",
        }
        with client:
            response = client.post(
                "/addArrowLabel",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
  :Activity;
-> Arrow label 1;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addarrow(self, client):
        test_data = {
            "plantuml": """@startuml
start
  :Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect>""",
            "where": "above",
        }
        with client:
            response = client.post(
                "/addArrowLabel",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
-> Arrow label 1;
  :Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_break3(self, client):
        test_data = {
            "plantuml": """@startuml
  :Activity;
break
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/breakActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
  :Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_detach2(self, client):
        test_data = {
            "plantuml": """@startuml
  :Activity;
break
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/detachActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
  :Activity;
detach
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_break2(self, client):
        test_data = {
            "plantuml": """@startuml
  :Activity;
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/breakActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
  :Activity;
break
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_break(self, client):
        test_data = {
            "plantuml": """@startuml
  :Activity;
note right
note
end note
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/breakActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
  :Activity;
note right
note
end note
break
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_checkbackward(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
repeat
  :Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="31.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="108.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="129.9375" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,64.9688,63.5,76.9688,51.5,88.9688,39.5,76.9688,51.5,64.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,172.9375,71,172.9375,83,184.9375,71,196.9375,32,196.9375,20,184.9375,32,172.9375" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="206.9922" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="188.5898" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="182.1875" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="107" y="108.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="117" y="129.9375" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="228.4922"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="249.4609" style="pointer-events: none;">Activity</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="88.9688" y2="108.9688"></line><polygon fill="#181818" points="47.5,98.9688,51.5,108.9688,55.5,98.9688,51.5,102.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="138.5" y1="184.9375" y2="184.9375"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="138.5" y1="142.9375" y2="184.9375"></line><polygon fill="#181818" points="134.5,152.9375,138.5,142.9375,142.5,152.9375,138.5,148.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="138.5" y1="76.9688" y2="108.9688"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="138.5" x2="63.5" y1="76.9688" y2="76.9688"></line><polygon fill="#181818" points="73.5,72.9688,63.5,76.9688,73.5,80.9688,69.5,76.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="142.9375" y2="172.9375"></line><polygon fill="#181818" points="47.5,162.9375,51.5,172.9375,55.5,162.9375,51.5,166.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="47.5,54.9688,51.5,64.9688,55.5,54.9688,51.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="196.9375" y2="228.4922"></line><polygon fill="#181818" points="47.5,218.4922,51.5,228.4922,55.5,218.4922,51.5,222.4922" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="107" y="108.9688"></rect>""",
        }
        with client:
            response = client.post(
                "/checkBackward",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """backward:Activity;"""
            assert response.data.decode("utf-8") == expected_puml

    def test_activity_indexes(self):
        output = [3, 5, 7, 6, 10, 9, 12]
        lines = """@startuml
start
repeat
:Activity;
repeat
#blue:Activity;
backward:Activity2;
:Activity;
repeat while (while ?) is (yes) not (no)
backward:Activity2;
:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml""".splitlines()
        assert activity_indices(lines, 0) == output

    def test_editcoloredactivity(self, client):
        test_data = {
            "plantuml": """@startuml
#lightblue:PPSI = 1, PPEI = 0;
@enduml""",
            "svg": """<rect fill="#ADD8E6" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="134" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="114" x="21" y="31.9688" style="pointer-events: none;">PPSI = 1, PPEI = 0</text>""",
            "newname": "Hej",
            "oldname": "PPSI = 1, PPEI = 0",
            "svgelement": """<rect fill="#ADD8E6" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="134" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/editText",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
#lightblue:Hej;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_toggledetach2(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
note right
note
end note
detach
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/detachActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
note right
note
end note
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addnote2(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/addNoteActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
note right
note
end note
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addswitchtoactivity(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
            "type": "switch",
        }
        with client:
            response = client.post(
                "/addToActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
switch (test?)
case ( condition 1)
:Activity;
case ( condition 2)
:Activity;
endswitch
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addtoactivity(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
            "type": "repeat",
        }
        with client:
            response = client.post(
                "/addToActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
repeat
:Activity;
backward:Activity;
repeat while (while ?) is (yes) not (no)
:Activity;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addactivitytoactivity(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
            "type": "activity",
        }
        with client:
            response = client.post(
                "/addToActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
:Activity 2;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_addnote(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
note right
note
end note
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/addNoteActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
note right
note
end note
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_toggledetach(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity;
note right
note
end note
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">activity 1</text>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/detachActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity;
note right
note
end note
detach
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_text_empty(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
:Activity 2;
:Activity 3;
:Activity 4;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688">Activity 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="85.9375">Activity 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="139.9063">Activity 3</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="172.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="193.875">Activity 4</text><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="44.5,54.9688,48.5,64.9688,52.5,54.9688,48.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="98.9375" y2="118.9375"></line><polygon fill="#181818" points="44.5,108.9375,48.5,118.9375,52.5,108.9375,48.5,112.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="152.9063" y2="172.9063"></line><polygon fill="#181818" points="44.5,162.9063,48.5,172.9063,52.5,162.9063,48.5,166.9063" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "newname": "",
            "oldname": "Activity 3",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect>""",
        }
        with client:
            response = client.post(
                "/editText", data=json.dumps(test_data), content_type="application/json"
            )
            expected_puml = """@startuml
:Activity 1;
:Activity 2;
:Activity 4;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_text_multiline(self, client):
        test_data = {
            "plantuml": """@startuml
  :Activity
  ASdasdasd
  asdasdasd;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="61.9063" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="90" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="21" y="31.9688" style="pointer-events: none;">Activity</text><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="70" x="21" y="45.9375" style="pointer-events: none;">ASdasdasd</text><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="69" x="21" y="59.9063" style="pointer-events: none;">asdasdasd</text>""",
            "newname": "Hej",
            "oldname": "Activity 3",
            "svgelement": """<rect fill="#F1F1F1" height="61.9063" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="90" x="11" y="11"></rect>""",
        }
        with client:
            response = client.post(
                "/editText", data=json.dumps(test_data), content_type="application/json"
            )
            expected_puml = """@startuml
  :Hej;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_text(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
:Activity 2;
:Activity 3;
:Activity 4;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688">Activity 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="85.9375">Activity 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="139.9063">Activity 3</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="172.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="193.875">Activity 4</text><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="44.5,54.9688,48.5,64.9688,52.5,54.9688,48.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="98.9375" y2="118.9375"></line><polygon fill="#181818" points="44.5,108.9375,48.5,118.9375,52.5,108.9375,48.5,112.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="152.9063" y2="172.9063"></line><polygon fill="#181818" points="44.5,162.9063,48.5,172.9063,52.5,162.9063,48.5,166.9063" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "newname": "Hej",
            "oldname": "Activity 3",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect>""",
        }
        with client:
            response = client.post(
                "/editText", data=json.dumps(test_data), content_type="application/json"
            )
            expected_puml = """@startuml
:Activity 1;
:Activity 2;
:Hej;
:Activity 4;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_get_text_link(self, client):
        test_data = {
            "plantuml": """@startuml
start
:Link to [[google.com Google]];
stop
@enduml""",
            "svg": """<ellipse cx="65.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="109" x="11" y="50"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="41" x="21" y="70.9688" style="pointer-events: none;">Link to</text><a href="google.com" target="_top" title="google.com" xlink:actuate="onRequest" xlink:href="google.com" xlink:show="new" xlink:title="google.com" xlink:type="simple"><text fill="#0000FF" font-family="sans-serif" font-size="12" lengthAdjust="spacing" text-decoration="underline" textLength="44" x="66" y="70.9688" style="pointer-events: none;">Google</text></a><ellipse cx="65.5" cy="114.9688" fill="transparent" rx="11" ry="11" style="stroke:#222222;stroke-width:1.0;"></ellipse><ellipse cx="65.5" cy="114.9688" fill="#222222" rx="6" ry="6" style="stroke:#111111;stroke-width:1.0;"></ellipse><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="65.5" x2="65.5" y1="30" y2="50"></line><polygon fill="#181818" points="61.5,40,65.5,50,69.5,40,65.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="65.5" x2="65.5" y1="83.9688" y2="103.9688"></line><polygon fill="#181818" points="61.5,93.9688,65.5,103.9688,69.5,93.9688,65.5,97.9688" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="109" x="11" y="50"></rect>""",
        }
        with client:
            response = client.post(
                "/getText", data=json.dumps(test_data), content_type="application/json"
            )
            expected_output = """Link to [[google.com Google]]"""
            assert response.data.decode("utf-8") == expected_output

    def test_get_text(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
:Activity 2;
:Activity 3
Hej
Bom;
:Activity 4;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688">Activity 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="85.9375">Activity 2</text><rect fill="#F1F1F1" height="61.9063" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="139.9063">Activity 3</text><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="20" x="21" y="153.875">Hej</text><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="27" x="21" y="167.8438">Bom</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="200.8438"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="221.8125">Activity 4</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="48.5" x2="48.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="44.5,54.9688,48.5,64.9688,52.5,54.9688,48.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="48.5" x2="48.5" y1="98.9375" y2="118.9375"></line><polygon fill="#181818" points="44.5,108.9375,48.5,118.9375,52.5,108.9375,48.5,112.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="48.5" x2="48.5" y1="180.8438" y2="200.8438"></line><polygon fill="#181818" points="44.5,190.8438,48.5,200.8438,52.5,190.8438,48.5,194.8438" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="61.9063" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect>""",
        }
        with client:
            response = client.post(
                "/getText", data=json.dumps(test_data), content_type="application/json"
            )
            expected_output = """Activity 3
Hej
Bom"""
            assert response.data.decode("utf-8") == expected_output

    def test_delete_activitywithnote(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
:Activity 2;
note right
note
end note
detach
:Activity 3;
:Activity 4;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688" style="pointer-events: none;">Activity 1</text><path d="M106,69.3867 L106,77.9531 L86,81.9531 L106,85.9531 L106,94.5195 A0,0 0 0 0 106,94.5195 L156,94.5195 A0,0 0 0 0 156,94.5195 L156,79.3867 L146,69.3867 L106,69.3867 A0,0 0 0 0 106,69.3867 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><path d="M146,69.3867 L146,79.3867 L156,79.3867 L146,69.3867 " fill="#FEFFDD" style="stroke:#181818;stroke-width:0.5;"></path><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="29" x="112" y="86.2695" style="pointer-events: none;">note</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="85.9375" style="pointer-events: none;">Activity 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="139.9063" style="pointer-events: none;">Activity 3</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="172.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="193.875" style="pointer-events: none;">Activity 4</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="48.5" x2="48.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="44.5,54.9688,48.5,64.9688,52.5,54.9688,48.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="48.5" x2="48.5" y1="98.9375" y2="118.9375"></line><polygon fill="#181818" points="44.5,108.9375,48.5,118.9375,52.5,108.9375,48.5,112.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="48.5" x2="48.5" y1="152.9063" y2="172.9063"></line><polygon fill="#181818" points="44.5,162.9063,48.5,172.9063,52.5,162.9063,48.5,166.9063" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect>""",
        }
        with client:
            response = client.post(
                "/deleteActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
:Activity 3;
:Activity 4;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_delete_activity2(self, client):
        test_data = {
            "plantuml": """@startuml
start
repeat
:Activity;
repeat
:Activity;
backward:Activity2;
:Activity;
repeat while (while ?) is (yes) not (no)
backward:Activity2;
:Activity;
repeat while (while ?) is (yes) not (no)
@enduml""",
            "svg": """<ellipse cx="51.5" cy="20" fill="#222222" rx="10" ry="10" style="stroke:#222222;stroke-width:1.0;"></ellipse><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="94"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="114.9688" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="191.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="212.9375" style="pointer-events: none;">Activity</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="260.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="281.9063" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,147.9688,63.5,159.9688,51.5,171.9688,39.5,159.9688,51.5,147.9688" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,314.9063,71,314.9063,83,326.9063,71,338.9063,32,338.9063,20,326.9063,32,314.9063" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="348.9609" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="330.5586" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="324.1563" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="107" y="226.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="117" y="247.4219" style="pointer-events: none;">Activity2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="20" y="370.4609"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="43" x="30" y="391.4297" style="pointer-events: none;">Activity</text><polygon fill="#F1F1F1" points="51.5,50,63.5,62,51.5,74,39.5,62,51.5,50" style="stroke:#181818;stroke-width:0.5;"></polygon><polygon fill="#F1F1F1" points="32,424.4297,71,424.4297,83,436.4297,71,448.4297,32,448.4297,20,436.4297,32,424.4297" style="stroke:#181818;stroke-width:0.5;"></polygon><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="14" x="55.5" y="458.4844" style="pointer-events: none;">no</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="39" x="32" y="440.082" style="pointer-events: none;">while ?</text><text fill="#000000" font-family="sans-serif" font-size="11" lengthAdjust="spacing" textLength="20" x="83" y="433.6797" style="pointer-events: none;">yes</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="188" y="226.4531"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="51" x="198" y="247.4219" style="pointer-events: none;">Activity2</text><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="225.9375" y2="260.9375"></line><polygon fill="#181818" points="47.5,250.9375,51.5,260.9375,55.5,250.9375,51.5,254.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="171.9688" y2="191.9688"></line><polygon fill="#181818" points="47.5,181.9688,51.5,191.9688,55.5,181.9688,51.5,185.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="142.5" y1="326.9063" y2="326.9063"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="142.5" x2="142.5" y1="260.4219" y2="326.9063"></line><polygon fill="#181818" points="138.5,270.4219,142.5,260.4219,146.5,270.4219,142.5,266.4219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="142.5" x2="142.5" y1="159.9688" y2="226.4531"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="142.5" x2="63.5" y1="159.9688" y2="159.9688"></line><polygon fill="#181818" points="73.5,155.9688,63.5,159.9688,73.5,163.9688,69.5,159.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="294.9063" y2="314.9063"></line><polygon fill="#181818" points="47.5,304.9063,51.5,314.9063,55.5,304.9063,51.5,308.9063" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="127.9688" y2="147.9688"></line><polygon fill="#181818" points="47.5,137.9688,51.5,147.9688,55.5,137.9688,51.5,141.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="338.9063" y2="370.4609"></line><polygon fill="#181818" points="47.5,360.4609,51.5,370.4609,55.5,360.4609,51.5,364.4609" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="74" y2="94"></line><polygon fill="#181818" points="47.5,84,51.5,94,55.5,84,51.5,88" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="83" x2="223.5" y1="436.4297" y2="436.4297"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="223.5" x2="223.5" y1="260.4219" y2="436.4297"></line><polygon fill="#181818" points="219.5,270.4219,223.5,260.4219,227.5,270.4219,223.5,266.4219" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="223.5" x2="223.5" y1="62" y2="226.4531"></line><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="223.5" x2="63.5" y1="62" y2="62"></line><polygon fill="#181818" points="73.5,58,63.5,62,73.5,66,69.5,62" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="404.4297" y2="424.4297"></line><polygon fill="#181818" points="47.5,414.4297,51.5,424.4297,55.5,414.4297,51.5,418.4297" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke: rgb(24, 24, 24); stroke-width: 1; pointer-events: none;" x1="51.5" x2="51.5" y1="30" y2="50"></line><polygon fill="#181818" points="47.5,40,51.5,50,55.5,40,51.5,44" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="71" x="107" y="226.4531"></rect>""",
        }
        with client:
            response = client.post(
                "/deleteActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
start
repeat
:Activity;
repeat
:Activity;
:Activity;
repeat while (while ?) is (yes) not (no)
backward:Activity2;
:Activity;
repeat while (while ?) is (yes) not (no)
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_delete_activity(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
:Activity 2;
:Activity 3;
:Activity 4;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688">Activity 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="85.9375">Activity 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="139.9063">Activity 3</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="172.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="193.875">Activity 4</text><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="44.5,54.9688,48.5,64.9688,52.5,54.9688,48.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="98.9375" y2="118.9375"></line><polygon fill="#181818" points="44.5,108.9375,48.5,118.9375,52.5,108.9375,48.5,112.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="152.9063" y2="172.9063"></line><polygon fill="#181818" points="44.5,162.9063,48.5,172.9063,52.5,162.9063,48.5,166.9063" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect>""",
        }
        with client:
            response = client.post(
                "/deleteActivity",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
:Activity 1;
:Activity 2;
:Activity 4;
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_activity_line(self, client):
        test_data = {
            "plantuml": """@startuml
:Activity 1;
:Activity 2;
:Activity 3;
:Activity 4;
@enduml""",
            "svg": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="11"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="31.9688">Activity 1</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="64.9688"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="85.9375">Activity 2</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="139.9063">Activity 3</text><rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="172.9063"></rect><text fill="#000000" font-family="sans-serif" font-size="12" lengthAdjust="spacing" textLength="55" x="21" y="193.875">Activity 4</text><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="44.9688" y2="64.9688"></line><polygon fill="#181818" points="44.5,54.9688,48.5,64.9688,52.5,54.9688,48.5,58.9688" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="98.9375" y2="118.9375"></line><polygon fill="#181818" points="44.5,108.9375,48.5,118.9375,52.5,108.9375,48.5,112.9375" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="48.5" x2="48.5" y1="152.9063" y2="172.9063"></line><polygon fill="#181818" points="44.5,162.9063,48.5,172.9063,52.5,162.9063,48.5,166.9063" style="stroke:#181818;stroke-width:1.0;"></polygon>""",
            "svgelement": """<rect fill="#F1F1F1" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="75" x="11" y="118.9375"></rect>""",
        }
        with client:
            response = client.post(
                "/getActivityLine",
                data=json.dumps(test_data),
                content_type="application/json",
            )

            response_json = json.loads(response.data.decode("utf-8"))
            result_value = response_json.get("result")

            expected_output = [3, 3]
            assert result_value == expected_output


class TestAppRoutesParticipant:
    def test_add_participant(self, client):
        test_data = {
            "plantuml": """@startuml
participant bob
@enduml""",
            "svg": """<line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="25" x2="25" y1="36.2969" y2="56.2969"></line><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="24.9951">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="55.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="75.292">bob</text>""",
            "svgelement": """<rect fill="#FF0000" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="90"></rect>""",
            "cx": 85,
        }
        with client:
            response = client.post(
                "/addParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant bob
participant participant2
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_another_participant(self, client):
        test_data = {
            "plantuml": """@startuml
participant bob
participant participant1
@enduml""",
            "svg": """<g><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="25" x2="25" y1="36.2969" y2="56.2969"></line><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="108" x2="108" y1="36.2969" y2="56.2969"></line><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="24.9951">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="55.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="75.292">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="104" x="56" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="90" x="63" y="24.9951">placeholder1</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="104" x="56" y="55.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="90" x="63" y="75.292">placeholder1</text>""",
            "svgelement": """<rect fill="#FF0000" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="90"></rect>""",
            "cx": -20,
        }
        with client:
            response = client.post(
                "/addParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant participant3
participant bob
participant participant1
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_participant_empty_diagram(self, client):
        test_data = {
            "plantuml": """@startuml
@enduml""",
            "svg": """<text fill="#000000" font-family="sans-serif" font-size="12" font-weight="bold" lengthAdjust="spacing" textLength="159" x="5" y="16.1387">Welcome to PlantUML!</text>""",
            "svgelement": """<rect fill="#FF0000" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="90"></rect>""",
            "cx": -20,
        }
        with client:
            response = client.post(
                "/addParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant participant1
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_participant_messages(self, client):
        test_data = {
            "plantuml": """@startuml
participant bob
participant fred

bob -> fred: Hello
fred -> bob: Bye

@enduml""",
            "svg": """<g><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="25" x2="25" y1="36.2969" y2="114.5625"></line><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="81" x2="81" y1="36.2969" y2="114.5625"></line><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="24.9951">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="113.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="133.5576">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="61" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="68" y="24.9951">fred</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="61" y="113.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="68" y="133.5576">fred</text><polygon fill="#181818" points="69.5,63.4297,79.5,67.4297,69.5,71.4297,73.5,67.4297" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="25.5" x2="75.5" y1="67.4297" y2="67.4297"></line><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="32" x="32.5" y="62.3638">Hello</text><polygon fill="#181818" points="36.5,92.5625,26.5,96.5625,36.5,100.5625,32.5,96.5625" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="30.5" x2="80.5" y1="96.5625" y2="96.5625"></line><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="24" x="42.5" y="91.4966">Bye</text></g>""",
            "svgelement": """<rect fill="#FF0000" height="33.9688" rx="12.5" ry="12.5" style="stroke:#181818;stroke-width:0.5;" width="63" x="11" y="90"></rect>""",
            "cx": -20,
        }
        with client:
            response = client.post(
                "/addParticipant",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant participant3
participant bob
participant fred

bob -> fred: Hello
fred -> bob: Bye

@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_add_message(self, client):
        test_data = {
            "plantuml": """@startuml
participant bob
participant fred
@enduml""",
            "svg": """<g><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="25" x2="25" y1="36.2969" y2="56.2969"></line><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="76" x2="76" y1="36.2969" y2="56.2969"></line><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="24.9951">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="55.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="75.292">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="56" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="63" y="24.9951">fred</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="56" y="55.2969"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="63" y="75.292">fred</text></g>""",
            "message": "hello fred",
            "firstcoordinates": [34, 43],
            "secondcoordinates": [71, 39],
        }
        with client:
            response = client.post(
                "/addMessage",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant bob
participant fred
bob -> fred: hello fred
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_participant_name(self, client):
        test_data = {
            "plantuml": """@startuml
participant bob
participant fred
bob -> fred: test
fred -> bob: test2
@enduml""",
            "svg": """<g><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="25" x2="25" y1="36.2969" y2="114.5625"></line><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="82" x2="82" y1="36.2969" y2="114.5625"></line><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="24.9951" style="pointer-events: none;">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="5" y="113.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="12" y="133.5576" style="pointer-events: none;">bob</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="62" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="69" y="24.9951" style="pointer-events: none;">fred</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="62" y="113.5625"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="69" y="133.5576" style="pointer-events: none;">fred</text><polygon fill="#181818" points="70.5,63.4297,80.5,67.4297,70.5,71.4297,74.5,67.4297" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="25.5" x2="76.5" y1="67.4297" y2="67.4297"></line><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="25" x="32.5" y="62.3638" style="pointer-events: none;">test</text><polygon fill="#181818" points="36.5,92.5625,26.5,96.5625,36.5,100.5625,32.5,96.5625" style="stroke:#181818;stroke-width:1.0;"></polygon><line style="stroke:#181818;stroke-width:1.0;" x1="30.5" x2="81.5" y1="96.5625" y2="96.5625"></line><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="33" x="42.5" y="91.4966" style="pointer-events: none;">test2</text></g>""",
            "name": "bobby",
            "cx": 5,
        }
        with client:
            response = client.post(
                "/editParticipantName",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant bobby
participant fred
bobby -> fred: test
fred -> bobby: test2
@enduml"""
            assert response.data.decode("utf-8") == expected_puml

    def test_edit_participant_name_selfmessage(self, client):
        test_data = {
            "plantuml": """@startuml
participant bobby
participant fred
bobby -> bobby: hello
@enduml""",
            "svg": """<g><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="33" x2="33" y1="36.2969" y2="98.4297"></line><line style="stroke:#181818;stroke-width:0.5;stroke-dasharray:5.0,5.0;" x1="92" x2="92" y1="36.2969" y2="98.4297"></line><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="57" x="5" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="43" x="12" y="24.9951" style="pointer-events: none;">bobby</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="57" x="5" y="97.4297"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="43" x="12" y="117.4248" style="pointer-events: none;">bobby</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="72" y="5"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="79" y="24.9951" style="pointer-events: none;">fred</text><rect fill="#E2E2F0" height="30.2969" rx="2.5" ry="2.5" style="stroke:#181818;stroke-width:0.5;" width="41" x="72" y="97.4297"></rect><text fill="#000000" font-family="sans-serif" font-size="14" lengthAdjust="spacing" textLength="27" x="79" y="117.4248" style="pointer-events: none;">fred</text><line style="stroke:#181818;stroke-width:1.0;" x1="33.5" x2="75.5" y1="67.4297" y2="67.4297"></line><line style="stroke:#181818;stroke-width:1.0;" x1="75.5" x2="75.5" y1="67.4297" y2="80.4297"></line><line style="stroke:#181818;stroke-width:1.0;" x1="34.5" x2="75.5" y1="80.4297" y2="80.4297"></line><polygon fill="#181818" points="44.5,76.4297,34.5,80.4297,44.5,84.4297,40.5,80.4297" style="stroke:#181818;stroke-width:1.0;"></polygon><text fill="#000000" font-family="sans-serif" font-size="13" lengthAdjust="spacing" textLength="30" x="40.5" y="62.3638" style="pointer-events: none;">hello</text></g>""",
            "name": "bob",
            "cx": 5,
        }
        with client:
            response = client.post(
                "/editParticipantName",
                data=json.dumps(test_data),
                content_type="application/json",
            )
            expected_puml = """@startuml
participant bob
participant fred
bob -> bob: hello
@enduml"""
            assert response.data.decode("utf-8") == expected_puml
