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

#!/usr/bin/env python3
"""Contains the class that converts inline PlantUML code to image links to new image files."""

import os
from pathlib import Path
from subprocess import PIPE, run

from dotenv import load_dotenv

load_dotenv(Path(__file__).parent.parent.parent / ".env", override=True)


def _create_svg_from_uml(uml):
    """Create a scalable vector graphic(SVG) from a UML string
    :param uml: The input UML text used for creating the image
    :return: The content of generated svg
    """
    base_command = [
        "java",
        "-DPLANTUML_LIMIT_SIZE=16384",
        "-jar",
        os.environ["PLANTUML_JAR"],
        "-pipe",
        "-tsvg",  # output in svg format
    ]
    process = run(
        base_command,
        stdout=PIPE,
        stderr=PIPE,
        input=bytes(uml, "utf-8"),
        check=False,
    )
    return process.stdout.decode("utf-8")


def _create_png_from_uml(uml):
    """Create a PNG image from a UML string
    :param uml: The input UML text used for creating the image
    :return: The content of generated png
    """
    base_command = [
        "java",
        "-DPLANTUML_LIMIT_SIZE=16384",
        "-jar",
        os.environ["PLANTUML_JAR"],
        "-pipe",
        "-tpng",  # output in png format
    ]
    process = run(
        base_command,
        stdout=PIPE,
        stderr=PIPE,
        input=bytes(uml, "utf-8"),
        check=False,
    )
    return process.stdout
