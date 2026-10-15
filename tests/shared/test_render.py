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

"""Tests for SVG/PNG rendering and PlantUML URL encoding/decoding."""

import re
import struct

from flask import json


def extract_g_element(svg_string):
    match = re.search(r"<g>(.*?)</g>", svg_string, re.DOTALL)
    if match:
        return f"<g>{match.group(1)}</g>"
    return None


def _png_size(png_bytes):
    """Read the pixel width/height from a PNG's IHDR chunk."""
    width, height = struct.unpack(">II", png_bytes[16:24])
    return width, height


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

            # Assert the PNG is rendered at a higher resolution than
            # PlantUML's low-res default (84x54 for this diagram at the
            # default 96 DPI), so downloaded diagrams aren't blurry.
            width, height = _png_size(response.data)
            assert width > 150
            assert height > 100


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
