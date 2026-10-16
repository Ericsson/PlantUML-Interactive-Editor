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
from functools import lru_cache

from flask import Blueprint, Response, jsonify, render_template, request, send_file

from ..__about__ import __version__
from ..sequence.pages import clamp_page, page_count
from .parse_changelog import parse_changelog
from .puml_encoder import plantuml_decode, plantuml_encode
from .render import _create_png_from_uml, _create_svg_from_uml
from .title import add_title, delete_title, edit_title_text, get_title_text

shared_bp = Blueprint(
    "shared",
    __name__,
    template_folder="../templates",
    static_folder="../static",
)


@lru_cache(maxsize=1)
def generate_static_js_hash():
    """Hash all static JS files so editing any of them busts the browser cache.

    The template applies a single ?v=<hash> query string to every script tag,
    so the hash must cover every served JS file (not just script.js) to avoid
    browsers serving a stale module after it changes. Walks subdirectories too,
    because static/vscode/ holds the shims the sidecar's page loads. Cached
    for the life of the process: static files don't change without a restart,
    so re-reading and re-hashing every JS file on every request to / is wasted
    work.
    """
    static_dir = shared_bp.static_folder
    hasher = hashlib.sha256()
    for dirpath, dirnames, filenames in os.walk(static_dir):
        # Sorted in place so os.walk descends in a stable order; without it the
        # hash would depend on the filesystem's directory ordering.
        dirnames.sort()
        for name in sorted(filenames):
            if name.endswith(".js"):
                with open(os.path.join(dirpath, name), "rb") as file:
                    hasher.update(file.read())
    return hasher.hexdigest()[:8]


@shared_bp.route("/")
def home():
    # Cache-busting hash covering all static JS files.
    file_hash = generate_static_js_hash()
    # pass hash to the template
    return render_template(
        "index.html", script_hash=file_hash, version=__version__
    )  # pragma: no cover


# Response header carrying how many pages (``newpage``) the diagram has. The
# VS Code webview reads it cross-origin, so serve.py's CORS layer must expose it.
PAGE_COUNT_HEADER = "X-PlantUML-Page-Count"


@shared_bp.route("/render", methods=["POST"])
def render():
    data = request.get_json()
    puml = data["plantuml"]
    page = clamp_page(puml, data.get("page", 0))
    response = Response(_create_svg_from_uml(puml, page), mimetype="text/html")
    response.headers[PAGE_COUNT_HEADER] = str(page_count(puml))
    return response


@shared_bp.route("/renderPNG", methods=["POST"])
def renderpng():
    data = request.get_json()
    puml = data["plantuml"]
    page = clamp_page(puml, data.get("page", 0))

    # Create the PNG image from the PlantUML code
    image_bytes = _create_png_from_uml(puml, page)

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


def _plain_text(text: str) -> Response:
    """Return ``text`` as ``text/plain``.

    Flask serves a bare ``str`` as ``text/html``, so puml text echoed back from
    the request would be rendered as markup if a browser ever opened the URL
    directly (CodeQL ``py/reflective-xss``). The editor reads these responses
    with ``response.text()``, so the body is unchanged.
    """
    return Response(text, mimetype="text/plain")


# Diagram title routes. The title block (title ... endtitle) is diagram-agnostic
# puml, edited the same way for activity and sequence diagrams, so these live in
# the shared blueprint. URLs are unchanged from when they lived on activity_bp
# (no blueprint carries a url_prefix).
@shared_bp.route("/addTitle", methods=["POST"])
def addtitle():
    data = request.get_json()
    puml = data["plantuml"]
    return _plain_text(add_title(puml))


@shared_bp.route("/getTextTitle", methods=["POST"])
def gettexttile():
    data = request.get_json()
    puml = data["plantuml"]
    return _plain_text(get_title_text(puml))


@shared_bp.route("/editTitle", methods=["POST"])
def edittitle():
    data = request.get_json()
    puml = data["plantuml"]
    title = data["title"]
    return _plain_text(edit_title_text(puml, title))


@shared_bp.route("/deleteTitle", methods=["POST"])
def deletetitle():
    data = request.get_json()
    puml = data["plantuml"]
    return _plain_text(delete_title(puml))
