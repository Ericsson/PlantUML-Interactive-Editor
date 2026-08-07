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

It also renders the webview's page. The frontend inside that page -- the
interaction code, the CSS and the context menus -- is the web app's, and this
is already the server that has it, so the whole document is built here rather
than assembled by the extension. The extension supplies only what a Flask
process cannot know about a VS Code webview: the URLs of the browser libraries
it loads off disk, and the webview's own CSP source.

Run with `python -m plantuml_gui.serve`.
"""

import os
import sys
from typing import TextIO
from urllib.parse import urlsplit

from flask import Flask, Response, jsonify, render_template, request
from flask.typing import ResponseReturnValue
from werkzeug.serving import make_server

from .app import app
from .shared.routes import generate_static_js_hash

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

# The webview's page. Sidecar-only, like /health: the web app's own page is
# index.html at /, and this one is the same frontend without the shell.
# Must match WEBVIEW_PATH in plantuml-extension/src/webviewPage.js.
WEBVIEW_ROUTE = "/webview"

WEBVIEW_TEMPLATE = "webview.html"

# Requests that only read; see _require_token for why that distinction earns an
# exemption.
SAFE_METHODS = frozenset({"GET", "HEAD"})

# Endpoints serving the frontend's own files. `static` is Flask's built-in
# static endpoint, which is what /static/<path> resolves to here -- the
# app-level rule is registered before the blueprint's and wins the match.
# Matched by endpoint rather than by path prefix so that a route mounted under
# /static later cannot silently inherit the exemption.
ASSET_ENDPOINTS = frozenset({"static"})

# Characters that would break out of the attribute or the CSP directive the
# extension's values are rendered into. Jinja escapes quotes on its own, but a
# semicolon in a CSP source expression starts a new directive, and whitespace
# splits one value into several -- neither of which escaping catches.
UNSAFE_IN_VALUE = set("\"'<>;") | set(" \t\r\n\f\v")

# csp_source is rendered inside a content="..." attribute of a <meta> CSP tag.
# Single quotes are legitimate CSP keywords ('self', 'unsafe-inline') and
# spaces separate multiple source expressions -- both are part of the CSP
# grammar. Double quotes, angle brackets, and semicolons remain dangerous
# (break attribute, break tag, or start a new directive respectively).
UNSAFE_IN_CSP_SOURCE = set('"<>;') | set("\t\r\n\f\v")


def apply_jar_override() -> None:
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


def install_cors(flask_app: Flask) -> None:
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
    def _add_cors_headers(response: Response) -> Response:
        response.headers["Access-Control-Allow-Origin"] = "*"
        response.headers["Access-Control-Allow-Headers"] = CORS_ALLOW_HEADERS
        response.headers["Access-Control-Allow-Methods"] = "GET, POST, OPTIONS"
        response.headers["Access-Control-Max-Age"] = CORS_MAX_AGE
        return response


def install_token_auth(flask_app: Flask, token: str | None) -> None:
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
    def _require_token() -> ResponseReturnValue | None:
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
        # checked, and so does WEBVIEW_ROUTE, which the extension host fetches
        # and can therefore send the header for.
        if request.method in SAFE_METHODS and request.endpoint in ASSET_ENDPOINTS:
            return None

        if request.headers.get(TOKEN_HEADER) != token:
            return jsonify({"error": "invalid or missing token"}), 403
        return None


def check_jar(stream: TextIO = sys.stderr) -> bool:
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


def install_health_route(flask_app: Flask) -> None:
    """Add the readiness probe the parent polls until the server answers.

    Registered here rather than on the blueprints so the web app's route table
    is unchanged; only the sidecar exposes it.
    """

    @flask_app.route("/health")
    def _health() -> ResponseReturnValue:
        return jsonify({"status": "ok"})


def _is_safe_value(value: str) -> bool:
    """Whether `value` can be rendered into an attribute or the CSP verbatim."""
    return bool(value) and not (UNSAFE_IN_VALUE & set(value))


def _is_safe_csp_source(value: str) -> bool:
    """Whether `value` is safe to render into the CSP meta tag's content attr.

    More permissive than _is_safe_value: single quotes (for CSP keywords like
    'self') and spaces (separating multiple source expressions) are legitimate
    parts of the CSP grammar and cannot break out of the content attribute.
    """
    return bool(value) and not (UNSAFE_IN_CSP_SOURCE & set(value))


def _is_http_url(value: str) -> bool:
    parts = urlsplit(value)
    return parts.scheme in ("http", "https") and bool(parts.netloc)


def install_webview_route(flask_app: Flask, token: str | None) -> None:
    """Serve the webview its page, complete.

    Everything about the document is decided here: the shell markup, the CSP,
    the context menus and the script load order. That is deliberate -- the
    frontend it loads is this package's, and the alternative is an extension
    that keeps its own copy of the script list and its own HTML template, kept
    in step with these files by comment.

    Three things it cannot know, so the caller passes them:

    `base`      where the webview should reach this server. Not derivable from
                the request: the extension host fetches this page over loopback,
                but under Remote-SSH, WSL or Codespaces the webview itself is on
                another machine and needs the address vscode.env.asExternalUri
                handed back.
    `csp_source` the webview's own resource origin, a per-panel uuid.
    `vendor_script` / `vendor_style`
                repeated, order significant. The browser libraries the web app
                takes from CDNs, which a webview's CSP blocks; the extension
                loads them off disk instead and these are the URLs that reach
                them.

    All four are reflected into the document, so they are validated rather than
    escaped-and-hoped: a semicolon in `csp_source` would append a CSP directive
    of the caller's choosing, and whitespace anywhere would split one value into
    several. Registered on the app rather than a blueprint, like the health
    route, so the web app's route table is unchanged.
    """

    @flask_app.route(WEBVIEW_ROUTE)
    def _webview_page() -> ResponseReturnValue:
        base = request.args.get("base", "")
        csp_source = request.args.get("csp_source", "")
        vendor_scripts = request.args.getlist("vendor_script")
        vendor_styles = request.args.getlist("vendor_style")

        if not _is_http_url(base) or not _is_safe_value(base):
            return jsonify({"error": "base must be an http(s) URL"}), 400

        if not _is_safe_csp_source(csp_source):
            return jsonify({"error": "csp_source is not a usable CSP source"}), 400

        if not all(map(_is_safe_value, vendor_scripts + vendor_styles)):
            return jsonify({"error": "vendor URLs are not usable as sources"}), 400

        parts = urlsplit(base)

        return render_template(
            WEBVIEW_TEMPLATE,
            # Trailing slash so the template can append relative paths to it.
            base=base if base.endswith("/") else base + "/",
            origin=f"{parts.scheme}://{parts.netloc}",
            csp_source=csp_source,
            vendor_scripts=vendor_scripts,
            vendor_styles=vendor_styles,
            token=token or "",
            token_header=TOKEN_HEADER,
            script_hash=generate_static_js_hash(),
        )


def main() -> int:
    apply_jar_override()
    check_jar()
    install_health_route(app)
    install_webview_route(app, os.environ.get(TOKEN_ENV))
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
