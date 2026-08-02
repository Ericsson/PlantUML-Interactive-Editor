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

"""Sidecar entry point: run the Flask app for a non-browser client.

`python -m plantuml_gui` serves the web UI on the fixed port 5000 with the
debug reloader on. That is wrong for a client that spawns this as a child
process (the VS Code extension): the fixed port may be taken and we want one
server per editor window, and the reloader forks a second process the parent
cannot cleanly kill.

This entry point instead binds an ephemeral port, prints it in a machine-
readable form for the parent to read, and optionally requires a shared token
so that other local processes cannot drive edits into the user's files.

It also serves the webview its frontend: the same static JS and CSS the web
app loads, plus the context menus rendered from the Jinja partials. Serving
them means the extension needs no copy of the web app's frontend, and so
cannot run a stale one.

Run with `python -m plantuml_gui.serve`. See docs/vscode_extension_interactivity.md.
"""

import os
import sys

from flask import jsonify, render_template, request
from werkzeug.serving import make_server

from .app import app

# Line written to stdout once the port is known. The parent process scans
# stdout for this exact prefix, so do not reformat it without updating
# plantuml-extension/src/sidecar.js.
PORT_LINE_PREFIX = "PLANTUML_GUI_PORT="

TOKEN_HEADER = "X-PlantUML-Token"

TOKEN_ENV = "PLANTUML_GUI_TOKEN"
JAR_ENV = "PLANTUML_GUI_JAR_OVERRIDE"

# Headers the client sends that are not CORS-safelisted, and therefore have to
# be named in the preflight response or the browser blocks the real request.
CORS_ALLOW_HEADERS = f"Content-Type, {TOKEN_HEADER}"

# Chromium caps this at 2 hours; asking for more just gets clamped. Without it
# every single request pays for a preflight round-trip.
CORS_MAX_AGE = "7200"

# Where the webview fetches the context-menu markup from. Sidecar-only, like
# /health -- the web app gets the same markup from an {% include %} in
# index.html.
MENUS_ROUTE = "/webview/menus"

# The two partials index.html includes, in the order it includes them.
MENU_PARTIALS = ("partials/activity_menus.html", "partials/sequence_menus.html")

# Requests that only read; see _require_token for why that distinction earns an
# exemption.
SAFE_METHODS = frozenset({"GET", "HEAD"})

# Endpoints serving the frontend's own files. `static` is Flask's built-in
# static endpoint, which is what /static/<path> resolves to here -- the
# app-level rule is registered before the blueprint's and wins the match.
# Matched by endpoint rather than by path prefix so that a route mounted under
# /static later cannot silently inherit the exemption.
ASSET_ENDPOINTS = frozenset({"static"})


def apply_jar_override():
    """Let the parent process choose the PlantUML jar, overriding any .env.

    `shared.render` calls `load_dotenv(..., override=True)` at import time, so
    a repo-root .env beats the environment this process was launched with --
    a client that passes PLANTUML_JAR would be silently ignored. Because
    render reads `os.environ["PLANTUML_JAR"]` per call rather than at import,
    assigning it here (after `.app` has been imported, and therefore after
    load_dotenv has run) wins without changing the web app's behaviour.
    """
    jar = os.environ.get(JAR_ENV)
    if jar:
        os.environ["PLANTUML_JAR"] = jar


def install_cors(flask_app):
    """Allow a webview to call this server cross-origin.

    The client is a VS Code webview, whose page origin is `vscode-webview://
    <uuid>`, so every request here is cross-origin -- unlike the web app, where
    the page and Flask share an origin. Because the client sends
    `Content-Type: application/json` and a token header, neither of which is
    CORS-safelisted, the browser first sends an OPTIONS preflight and blocks
    the real request unless the response permits it.

    `*` rather than a specific origin because the webview's uuid changes per
    panel. That is not a hole: it grants any page permission to *attempt* a
    request, while install_token_auth still rejects anything that cannot
    produce the per-launch token. Note also that `*` bars the browser from
    sending cookies, and this server has no cookie or session state anyway.
    """

    @flask_app.after_request
    def _add_cors_headers(response):
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = CORS_ALLOW_HEADERS
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Max-Age"] = CORS_MAX_AGE
        return response


def install_token_auth(flask_app, token):
    """Reject requests that do not carry `token`, if a token is configured.

    This server listens on loopback, which is not a trust boundary: any
    process on the machine can reach it, and every route here rewrites
    PlantUML source. The parent passes a per-launch random token so only it
    can drive those routes. No token configured means no check installed, so
    normal `python -m plantuml_gui` web use is unaffected.
    """
    if not token:
        return

    @flask_app.before_request
    def _require_token():
        # A CORS preflight cannot carry the token: browsers strip custom
        # headers from OPTIONS by design, sending them as
        # Access-Control-Request-Headers instead. Rejecting it here fails the
        # preflight and the real request never happens. Letting it through
        # gives away nothing -- the preflight response carries no data, and the
        # real request that follows is still checked.
        if request.method == "OPTIONS":
            return None

        # The webview loads the frontend's JS and CSS from here with <script
        # src> and <link href>, and neither can carry a header -- so an
        # authenticated static file is only possible by putting the secret in a
        # query string, where it would land in werkzeug's request log. Exempt
        # them instead. It gives away nothing: these are non-secret, read-only
        # files that any process able to reach loopback can already read off
        # disk. Every route that rewrites the user's source is a POST and stays
        # checked, and so does MENUS_ROUTE, which the extension host fetches
        # and can therefore send the header for.
        if request.method in SAFE_METHODS and request.endpoint in ASSET_ENDPOINTS:
            return None

        if request.headers.get(TOKEN_HEADER) != token:
            return jsonify({"error": "invalid or missing token"}), 403
        return None


def check_jar(stream=sys.stderr):
    """Warn early if the PlantUML jar is missing or misconfigured.

    `shared.render` reads os.environ["PLANTUML_JAR"] per request, so a bad
    setting otherwise surfaces as a KeyError or an empty render inside a 500
    response -- from the client's point of view, an opaque failure on first
    use. Warn at startup instead, where the parent is capturing stderr.

    Deliberately a warning rather than a hard exit: rendering is only some of
    the routes, and the puml-rewriting ones work fine without a jar.
    """
    jar = os.environ.get("PLANTUML_JAR")

    if not jar:
        print(
            "warning: PLANTUML_JAR is not set; rendering will fail. Set the "
            "plantumlInteractive.plantumlJar setting (or PLANTUML_JAR) to "
            "plantuml.jar.",
            file=stream,
            flush=True,
        )
        return False

    if not os.path.isfile(jar):
        print(
            f'warning: PLANTUML_JAR points at "{jar}", which does not exist; '
            "rendering will fail. Note that a repo-root .env overrides the "
            "environment for the web app.",
            file=stream,
            flush=True,
        )
        return False

    return True


def install_health_route(flask_app):
    """Add the readiness probe the parent polls until the server answers.

    Registered here rather than on the blueprints so the web app's route table
    is unchanged; only the sidecar exposes it.
    """

    @flask_app.route("/health")
    def _health():
        return jsonify({"status": "ok"})


def install_menus_route(flask_app):
    """Serve the context-menu markup the webview needs, rendered.

    The extension owns the webview's HTML, but not this part of it: the menus
    are ~95 of the DOM ids the frontend calls getElementById on, and
    sequence_menus.html *defines and calls* a `color_select` macro. Reading the
    partials as files would leave `{{ color_select(...) }}` as literal text and
    the colour dropdowns would silently not exist -- so they have to go through
    Jinja, and Jinja lives here.

    Registered by the sidecar rather than on a blueprint, like the health
    route, so the web app's route table is unchanged; index.html gets the same
    markup from `{% include %}`.
    """

    @flask_app.route(MENUS_ROUTE)
    def _webview_menus():
        return "\n".join(render_template(name) for name in MENU_PARTIALS)


def main():
    apply_jar_override()
    check_jar()
    install_health_route(app)
    install_menus_route(app)
    install_cors(app)
    install_token_auth(app, os.environ.get(TOKEN_ENV))

    # Port 0 asks the OS for any free port; make_server binds immediately, so
    # server.port below is the real port rather than a guess.
    server = make_server("127.0.0.1", 0, app, threaded=True)

    # flush: the parent blocks reading this line, and without an explicit
    # flush Python's block buffering (stdout is a pipe, not a tty) would hold
    # it until the buffer fills -- which never happens.
    print(f"{PORT_LINE_PREFIX}{server.port}", flush=True)

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        pass
    return 0


if __name__ == "__main__":
    sys.exit(main())
