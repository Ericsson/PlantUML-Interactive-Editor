#!/usr/bin/env python
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

"""Pre-commit hook (see .pre-commit-config.yaml) guarding the version pairing
plantuml-extension/CHANGELOG.md documents: the extension's version tracks the
``plantuml-gui`` backend it is built against, because the two are installed as
a pair and the frontend ships inside the backend (see scripts/build_release.sh,
which builds both from one commit). A VS Code manifest requires three-component
semver, so backend ``0.31`` is extension ``0.31.x``.

Nothing at runtime notices if only one side is bumped -- the extension just
launches whatever backend is installed -- so the mismatch would only surface as
an old UI in the webview. Hence this check.

The extension's patch component is free, so an extension-only fix can ship as
``0.31.1`` without a backend release; ``major.minor`` must agree. That the
extension's version is three-component semver at all is left to ``vsce
package``, which refuses to build otherwise.

Run directly with ``python scripts/check_app_versions.py``, or via the
``check-app-versions`` pre-commit hook, which is where this and the repo's
other checks run, locally and in CI (see .github/workflows/pre-commit.yml).
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
ABOUT_PATH = REPO_ROOT / "src" / "plantuml_gui" / "__about__.py"
EXTENSION_PACKAGE_JSON = REPO_ROOT / "plantuml-extension" / "package.json"

# __about__.py is read rather than imported: importing the package would pull
# in Flask and the rest of the app just to read one string.
VERSION_RE = re.compile(r"^__version__\s*=\s*[\"']([^\"']+)[\"']", re.MULTILINE)


class VersionCheckError(Exception):
    """A version could not be read, or the two do not agree."""


def _read_backend_version(about_path: Path) -> str:
    match = VERSION_RE.search(about_path.read_text(encoding="utf-8"))
    if not match:
        raise VersionCheckError(
            f"could not find a __version__ assignment in {about_path}"
        )
    return match.group(1)


def _read_extension_version(package_json_path: Path) -> str:
    package_json = json.loads(package_json_path.read_text(encoding="utf-8"))
    version = package_json.get("version")
    if not version:
        raise VersionCheckError(f"{package_json_path} has no version field")
    return version


def _major_minor(version: str, source: str) -> tuple[int, int]:
    """Return a version's (major, minor), ignoring any further components."""
    components = version.split(".")
    if len(components) < 2:
        raise VersionCheckError(
            f"{source} version {version!r} is not of the form major.minor"
        )
    try:
        return int(components[0]), int(components[1])
    except ValueError:
        raise VersionCheckError(
            f"{source} version {version!r} has non-numeric major/minor components"
        ) from None


def check_app_versions(
    about_path: Path = ABOUT_PATH,
    package_json_path: Path = EXTENSION_PACKAGE_JSON,
) -> str:
    """Compare the web app's version against the extension's.

    Returns a message describing the agreement; raises VersionCheckError if
    either version cannot be read or the two disagree.
    """
    backend_version = _read_backend_version(about_path)
    extension_version = _read_extension_version(package_json_path)

    backend_major_minor = _major_minor(backend_version, "web app")
    extension_major_minor = _major_minor(extension_version, "extension")

    if backend_major_minor != extension_major_minor:
        raise VersionCheckError(
            f"web app is at {backend_version} ({about_path.name}) but the "
            f"extension is at {extension_version} "
            f"({package_json_path.parent.name}/{package_json_path.name}) - the "
            "two ship as a pair, so the webview would run an unrelated "
            "backend version. Bump whichever one is stale (and its CHANGELOG)."
        )

    return f"web app {backend_version} and extension {extension_version} agree"


def main() -> int:
    try:
        print(f"OK {check_app_versions()}")
    except VersionCheckError as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
