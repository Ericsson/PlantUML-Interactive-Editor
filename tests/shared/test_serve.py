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

import io
import os
from pathlib import Path
from urllib.parse import urlsplit

import pytest
from flask import Flask, jsonify
from plantuml_gui import serve
from pyquery import PyQuery

# plantuml_gui is a namespace package, so it has no __file__ of its own.
PACKAGE_DIR = Path(serve.__file__).parent

TOKEN = "s3cret"

BASE = "http://127.0.0.1:5555/"

# What vscode.Webview.asWebviewUri hands back, in shape.
CSP_SOURCE = "https://*.vscode-cdn.net"
VENDOR_SCRIPTS = [
    "https://abc.vscode-cdn.net/node_modules/jquery/dist/jquery.min.js",
    "https://abc.vscode-cdn.net/node_modules/bootstrap/dist/js/bootstrap.min.js",
]
VENDOR_STYLES = [
    "https://abc.vscode-cdn.net/node_modules/bootstrap/dist/css/bootstrap.min.css"
]


@pytest.fixture()
def bare_app():
    """A throwaway Flask app, so hooks installed by a test do not leak into
    the shared `plantuml_gui.app.app` used by every other test module."""
    app = Flask(__name__)

    @app.route("/editText", methods=["POST"])
    def _edit_text():
        return jsonify({"ok": True})

    return app


@pytest.fixture()
def webview_app():
    """A throwaway app pointed at the real templates and static files.

    Same reason as `bare_app` -- installing the route on `plantuml_gui.app.app`
    would leave it registered for every later test -- but the webview route
    renders Jinja and links static files, so it needs both folders.
    """
    app = Flask(
        __name__,
        template_folder=str(PACKAGE_DIR / "templates"),
        static_folder=str(PACKAGE_DIR / "static"),
    )
    serve.install_webview_route(app, TOKEN)
    return app


def get_webview(app, **overrides):
    """GET the webview page with the arguments the extension sends."""
    params = {
        "base": BASE,
        "csp_source": CSP_SOURCE,
        "vendor_script": VENDOR_SCRIPTS,
        "vendor_style": VENDOR_STYLES,
    }
    params.update(overrides)
    return app.test_client().get(serve.WEBVIEW_ROUTE, query_string=params)


def webview_page(app, **overrides):
    response = get_webview(app, **overrides)
    assert response.status_code == 200, response.get_data(as_text=True)
    return PyQuery(response.get_data(as_text=True))


def script_sources(page):
    return [
        element.attrib["src"] for element in page("script") if "src" in element.attrib
    ]


def local_path(url):
    """The package-relative path a `{{ base }}...` URL points at, or None."""
    if not url.startswith(BASE):
        return None
    return urlsplit(url[len(BASE) :]).path


def test_health_route_reports_ok(bare_app):
    serve.install_health_route(bare_app)

    response = bare_app.test_client().get("/health")

    assert response.status_code == 200
    assert response.get_json() == {"status": "ok"}


def test_no_token_configured_leaves_routes_open(bare_app):
    """`python -m plantuml_gui` for web use must be unaffected by the sidecar's
    auth, so an empty/absent token installs no check at all."""
    serve.install_token_auth(bare_app, None)

    assert bare_app.test_client().post("/editText").status_code == 200


def test_request_without_token_is_rejected(bare_app):
    serve.install_token_auth(bare_app, "s3cret")

    response = bare_app.test_client().post("/editText")

    assert response.status_code == 403


def test_request_with_wrong_token_is_rejected(bare_app):
    serve.install_token_auth(bare_app, "s3cret")

    response = bare_app.test_client().post(
        "/editText", headers={serve.TOKEN_HEADER: "guess"}
    )

    assert response.status_code == 403


def test_request_with_correct_token_is_allowed(bare_app):
    serve.install_token_auth(bare_app, "s3cret")

    response = bare_app.test_client().post(
        "/editText", headers={serve.TOKEN_HEADER: "s3cret"}
    )

    assert response.status_code == 200
    assert response.get_json() == {"ok": True}


def test_cors_preflight_is_allowed_through_token_auth(bare_app):
    """The bug that made every webview request fail with "Failed to fetch".

    A browser strips custom headers from a preflight, so the token check
    rejected OPTIONS with 403, the preflight failed, and the real request was
    never sent.
    """
    serve.install_cors(bare_app)
    serve.install_token_auth(bare_app, "s3cret")

    response = bare_app.test_client().options(
        "/editText",
        headers={
            "Origin": "vscode-webview://abc",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "content-type,x-plantuml-token",
        },
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "*"


def test_cors_preflight_permits_the_headers_the_client_sends(bare_app):
    serve.install_cors(bare_app)

    allowed = (
        bare_app.test_client()
        .options("/editText")
        .headers["Access-Control-Allow-Headers"]
        .lower()
    )

    # Neither is CORS-safelisted, so both must be named or the browser blocks.
    assert "content-type" in allowed
    assert "x-plantuml-token" in allowed


def test_cors_headers_are_on_real_responses_too(bare_app):
    """Without these the browser completes the request but hides the response
    body from JavaScript, which also surfaces as "Failed to fetch"."""
    serve.install_cors(bare_app)
    serve.install_token_auth(bare_app, "s3cret")

    response = bare_app.test_client().post(
        "/editText", headers={serve.TOKEN_HEADER: "s3cret"}
    )

    assert response.status_code == 200
    assert response.headers["Access-Control-Allow-Origin"] == "*"


def test_preflight_exemption_does_not_weaken_auth(bare_app):
    """Letting OPTIONS through must not let a real request through."""
    serve.install_cors(bare_app)
    serve.install_token_auth(bare_app, "s3cret")

    assert bare_app.test_client().post("/editText").status_code == 403


def test_webview_page_supplies_the_ids_the_frontend_dereferences(webview_app):
    """The app's code calls getElementById on these without a null check, so
    one missing id throws during setup and kills every interaction while the
    diagram still renders -- a failure that looks like nothing at all."""
    page = webview_page(webview_app)

    for element_id in (
        "popup",
        "editor",
        "version",
        "version-panel",
        "colb-container",
        "colb",
        "loading-overlay",
    ):
        assert page(f"#{element_id}"), f"#{element_id} is missing from the page"


def test_webview_page_includes_the_menus_from_the_same_partials_as_index(webview_app):
    """The context menus are ~95 of the ids the frontend needs. Sharing the
    partials with index.html is what keeps them from drifting apart."""
    page = webview_page(webview_app)

    assert page("#activity-menu"), "activity_menus.html was not included"
    assert page("#sequence-menu"), "sequence_menus.html was not included"


def test_webview_page_runs_the_menu_partials_through_jinja(webview_app):
    """sequence_menus.html defines and calls a `color_select` macro. Served as
    a plain file the markup would carry a literal {{ color_select(...) }} and
    the colour dropdowns would silently not exist."""
    response = get_webview(webview_app)
    body = response.get_data(as_text=True)

    assert "{{" not in body and "{%" not in body
    assert PyQuery(body)('option[value="LightBlue"]'), "color_select did not render"


def test_webview_page_has_no_inline_script(webview_app):
    """What the shims need is on <body> instead. No inline script is what lets
    the CSP below carry no nonce and no script-src exception."""
    page = webview_page(webview_app)

    for element in page("script"):
        assert "src" in element.attrib, "the page has an inline <script>"


def test_webview_page_tells_the_fetch_shim_how_to_reach_the_sidecar(webview_app):
    page = webview_page(webview_app)
    body = page("body")

    assert body.attr("data-plantuml-api") == BASE
    assert body.attr("data-plantuml-token") == TOKEN
    # Read rather than hardcoded in the shim, so the two cannot drift.
    assert body.attr("data-plantuml-token-header") == serve.TOKEN_HEADER


def test_webview_page_addresses_the_frontend_absolutely(webview_app):
    """The document is handed to VS Code as a string, so its own origin is
    vscode-webview://<uuid> and every relative path resolves to nothing."""
    page = webview_page(webview_app)
    vendor = set(VENDOR_SCRIPTS + VENDOR_STYLES)

    urls = script_sources(page) + [link.attrib["href"] for link in page("link")]

    for url in urls:
        assert url in vendor or url.startswith(BASE), f"{url} is not absolute"


def test_webview_page_only_links_files_that_exist(webview_app):
    """A wrong path is a silent 404 inside the webview: the diagram still
    renders and the interaction that needed the file just never works."""
    page = webview_page(webview_app)

    urls = script_sources(page) + [link.attrib["href"] for link in page("link")]

    for url in urls:
        relative = local_path(url)
        if relative is None:
            continue
        assert (PACKAGE_DIR / relative).is_file(), f"{relative} does not exist"


def test_webview_page_loads_the_scripts_in_the_order_they_depend_on(webview_app):
    """The invariant the whole page rests on. jQuery before Bootstrap, which
    requires it; editorShim before script.js, which dereferences `ace` at load
    time and would throw mid-parse; webviewInit last, because it assigns
    script.js's top-level `let editor`."""
    order = [
        local_path(src) or src for src in script_sources(webview_page(webview_app))
    ]

    assert order[: len(VENDOR_SCRIPTS)] == VENDOR_SCRIPTS
    assert order[len(VENDOR_SCRIPTS) : len(VENDOR_SCRIPTS) + 2] == [
        "static/vscode/fetchShim.js",
        "static/vscode/editorShim.js",
    ]
    assert order[len(VENDOR_SCRIPTS) + 2] == "static/script.js"
    assert order[-1] == "static/vscode/webviewInit.js"


def test_webview_page_allows_only_the_two_sources_it_needs(webview_app):
    """What makes it safe to innerHTML PlantUML-rendered SVG from an untrusted
    .puml file: injected markup can carry neither origin, so an inline <script>
    or an SVG onload handler is blocked."""
    page = webview_page(webview_app)
    policy = " ".join(
        page('meta[http-equiv="Content-Security-Policy"]').attr("content").split()
    )

    directives = {
        part.split(" ")[0]: part
        for part in (p.strip() for p in policy.split(";"))
        if part
    }

    assert directives["default-src"] == "default-src 'none'"
    assert CSP_SOURCE in directives["script-src"]
    assert "http://127.0.0.1:5555" in directives["script-src"]
    # A nonce would only exist to permit inline script, and there is none.
    assert "'unsafe-inline'" not in directives["script-src"]
    assert "nonce-" not in directives["script-src"]
    # Styles are the one exception: Bootstrap and the app both set them inline.
    assert "'unsafe-inline'" in directives["style-src"]


def test_webview_page_serves_the_same_scripts_as_the_web_app(webview_app):
    """Both pages render partials/app_scripts.html, which is the point: the
    extension used to keep a copy of this list and mirror it by hand."""
    page = webview_page(webview_app)
    served = {local_path(src) for src in script_sources(page)}

    index = PyQuery(
        webview_app.jinja_env.get_template("index.html").render(
            script_hash="x", version="0"
        )
    )
    for element in index("script"):
        src = element.attrib.get("src", "")
        if src.startswith("static/"):
            assert urlsplit(src).path in served, f"{src} is not on the webview page"


@pytest.mark.parametrize(
    "overrides",
    [
        {"base": ""},
        {"base": "javascript:alert(1)"},
        {"base": "not a url"},
        # Would append a CSP directive of the caller's choosing.
        {"csp_source": "https://x; script-src *"},
        # Double quote would close the content attribute.
        {"csp_source": 'https://x" https://evil'},
        {"vendor_script": ["https://x/a.js https://evil/b.js"]},
        {"vendor_style": ['https://x/a.css" onload="alert(1)']},
    ],
)
def test_webview_page_rejects_values_it_cannot_render_safely(webview_app, overrides):
    """Every one of these is reflected into the document. Escaping does not
    cover them: a semicolon starts a new CSP directive and whitespace splits
    one value into several, both inside a perfectly well-formed attribute."""
    assert get_webview(webview_app, **overrides).status_code == 400


def test_webview_page_accepts_compound_csp_source(webview_app):
    """VS Code Remote-SSH sends csp_source with single-quoted keywords and
    space-separated sources, e.g. \"'self' https://*.vscode-cdn.net\". These
    are legitimate CSP grammar and must not be rejected."""
    response = get_webview(webview_app, csp_source="'self' https://*.vscode-cdn.net")
    assert response.status_code == 200


def test_webview_page_requires_the_token(webview_app):
    """It is a GET, but the extension host fetches it and can send the header,
    so unlike the static files it stays checked."""
    serve.install_token_auth(webview_app, TOKEN)

    assert get_webview(webview_app).status_code == 403


def test_webview_page_is_served_when_the_token_is_sent(webview_app):
    serve.install_token_auth(webview_app, TOKEN)

    response = webview_app.test_client().get(
        serve.WEBVIEW_ROUTE,
        query_string={"base": BASE, "csp_source": CSP_SOURCE},
        headers={serve.TOKEN_HEADER: TOKEN},
    )

    assert response.status_code == 200


def test_static_files_are_exempt_from_the_token(webview_app):
    """A <script src> cannot send a header, and the alternative -- the secret
    in a query string -- would land in werkzeug's request log."""
    serve.install_token_auth(webview_app, TOKEN)

    response = webview_app.test_client().get("/static/vscode/fetchShim.js")

    assert response.status_code == 200


def test_jar_override_beats_dotenv(monkeypatch):
    """The whole point of the override: a value the parent process passes must
    win over whatever load_dotenv(override=True) already put in os.environ."""
    monkeypatch.setitem(os.environ, "PLANTUML_JAR", "/from/dotenv.jar")
    monkeypatch.setitem(os.environ, serve.JAR_ENV, "/from/parent.jar")

    serve.apply_jar_override()

    assert os.environ["PLANTUML_JAR"] == "/from/parent.jar"


def test_no_jar_override_leaves_existing_value(monkeypatch):
    monkeypatch.setitem(os.environ, "PLANTUML_JAR", "/from/dotenv.jar")
    monkeypatch.delenv(serve.JAR_ENV, raising=False)

    serve.apply_jar_override()

    assert os.environ["PLANTUML_JAR"] == "/from/dotenv.jar"


def test_check_jar_warns_when_unset(monkeypatch):
    monkeypatch.delenv("PLANTUML_JAR", raising=False)
    stream = io.StringIO()

    assert serve.check_jar(stream) is False
    assert "PLANTUML_JAR is not set" in stream.getvalue()


def test_check_jar_warns_when_path_is_missing(monkeypatch):
    monkeypatch.setitem(os.environ, "PLANTUML_JAR", "/no/such/plantuml.jar")
    stream = io.StringIO()

    assert serve.check_jar(stream) is False
    # The .env hint matters: it is the likeliest cause of a stale path.
    assert "does not exist" in stream.getvalue()
    assert ".env" in stream.getvalue()


def test_check_jar_passes_for_a_real_file(monkeypatch, tmp_path):
    jar = tmp_path / "plantuml.jar"
    jar.write_bytes(b"")
    monkeypatch.setitem(os.environ, "PLANTUML_JAR", str(jar))
    stream = io.StringIO()

    assert serve.check_jar(stream) is True
    assert stream.getvalue() == ""
