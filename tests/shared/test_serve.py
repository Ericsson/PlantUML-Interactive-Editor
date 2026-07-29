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

import pytest
from flask import Flask, jsonify
from plantuml_gui import serve


@pytest.fixture()
def bare_app():
    """A throwaway Flask app, so hooks installed by a test do not leak into
    the shared `plantuml_gui.app.app` used by every other test module."""
    app = Flask(__name__)

    @app.route("/editText", methods=["POST"])
    def _edit_text():
        return jsonify({"ok": True})

    return app


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
