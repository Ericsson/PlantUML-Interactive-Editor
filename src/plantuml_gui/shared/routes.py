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

import hashlib
import io
import os

from flask import Blueprint, jsonify, render_template, request, send_file

from ..__about__ import __version__
from .parse_changelog import parse_changelog
from .puml_encoder import plantuml_decode, plantuml_encode
from .render import _create_png_from_uml, _create_svg_from_uml

shared_bp = Blueprint(
    "shared",
    __name__,
    template_folder="../templates",
    static_folder="../static",
)


def generate_file_hash(file_path):
    with open(file_path, "rb") as file:
        file_content = file.read()
        return hashlib.sha256(file_content).hexdigest()[:8]


SCRIPT_PATH = os.path.join(shared_bp.static_folder, "sequence-operations.js")


@shared_bp.route("/")
def home():
    # generate hash for cache busting
    file_hash = generate_file_hash(SCRIPT_PATH)
    # pass hash to the template
    return render_template(
        "index.html", script_hash=file_hash, version=__version__
    )  # pragma: no cover


@shared_bp.route("/render", methods=["POST"])
def render():
    data = request.get_json()
    puml = data["plantuml"]
    return _create_svg_from_uml(puml)


@shared_bp.route("/renderPNG", methods=["POST"])
def renderpng():
    data = request.get_json()
    puml = data["plantuml"]

    # Create the PNG image from the PlantUML code
    image_bytes = _create_png_from_uml(puml)

    # Use io.BytesIO to handle the byte stream
    image_stream = io.BytesIO(image_bytes)

    # Set the correct content type and disposition
    return send_file(
        image_stream,
        mimetype="image/png",
        as_attachment=True,
        download_name="generated-image.png",
    )


@shared_bp.route("/encode", methods=["POST"])
def encode():
    data = request.get_json()
    puml = data["plantuml"]
    return plantuml_encode(puml)


@shared_bp.route("/decode", methods=["POST"])
def decode():
    data = request.get_json()
    hash = data["hash"]
    return plantuml_decode(hash)


@shared_bp.route("/changelog")
def changelog():
    return jsonify(parse_changelog())
