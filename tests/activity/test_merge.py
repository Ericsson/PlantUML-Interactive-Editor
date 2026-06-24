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

"""Tests for merge point element routes."""

from flask import json


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
