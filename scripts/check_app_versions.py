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

"""Pre-commit hook (see .pre-commit-config.yaml) guarding that every file
holding the app's version agrees on it, exactly.

The extension and the ``plantuml-gui`` backend are installed as a pair and the
frontend ships inside the backend (see scripts/build_release.sh, which builds
both from one commit), so they carry one version: three-component ``X.Y.Z``,
which a VS Code manifest requires anyway. It lives in three files:

- ``src/plantuml_gui/__about__.py`` -- the package version (hatch reads it)
- ``plantuml-extension/package.json`` -- the extension manifest
- ``plantuml-extension/package-lock.json`` -- twice: top level and ``packages[""]``

Nothing at runtime notices if only one is bumped -- the extension just launches
whatever backend is installed -- so the mismatch would only surface as an old UI
in the webview, or a lockfile that ``npm ci`` quietly rewrites. Hence this check.

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
EXTENSION_PACKAGE_LOCK = REPO_ROOT / "plantuml-extension" / "package-lock.json"

# __about__.py is read rather than imported: importing the package would pull
# in Flask and the rest of the app just to read one string.
VERSION_RE = re.compile(r"^__version__\s*=\s*[\"']([^\"']+)[\"']", re.MULTILINE)

# Plain X.Y.Z, each component a non-negative integer without leading zeros
# (leading zeros are not valid semver, and vsce refuses them).
SEMVER_RE = re.compile(r"^(0|[1-9]\d*)\.(0|[1-9]\d*)\.(0|[1-9]\d*)$")


class VersionCheckError(Exception):
    """A version could not be read, is malformed, or the files disagree."""


def parse_version(version: str, source: str) -> tuple[int, int, int]:
    """Return ``X.Y.Z`` as ``(X, Y, Z)``; raise if it is not of that form."""
    match = SEMVER_RE.match(version)
    if not match:
        raise VersionCheckError(
            f"{source} has version {version!r}, which is not of the form X.Y.Z"
        )
    major, minor, patch = (int(component) for component in match.groups())
    return major, minor, patch


def read_backend_version(about_path: Path = ABOUT_PATH) -> str:
    """Return the ``__version__`` string assigned in an ``__about__.py``."""
    return backend_version_from_text(
        about_path.read_text(encoding="utf-8"), str(about_path)
    )


def backend_version_from_text(text: str, source: str) -> str:
    """Return the ``__version__`` assigned in ``__about__.py`` source text."""
    match = VERSION_RE.search(text)
    if not match:
        raise VersionCheckError(f"could not find a __version__ assignment in {source}")
    return match.group(1)


def read_extension_version(package_json_path: Path = EXTENSION_PACKAGE_JSON) -> str:
    """Return the ``version`` field of the extension's package.json."""
    package_json = json.loads(package_json_path.read_text(encoding="utf-8"))
    version = package_json.get("version")
    if not version:
        raise VersionCheckError(f"{package_json_path} has no version field")
    return version


def read_lockfile_versions(
    package_lock_path: Path = EXTENSION_PACKAGE_LOCK,
) -> dict[str, str]:
    """Return the lockfile's two copies of the package's own version.

    npm records it at the top level and again under ``packages[""]`` (the root
    package); both are keyed by where they sit, so a stale one can be named.
    """
    lock = json.loads(package_lock_path.read_text(encoding="utf-8"))
    root_package = lock.get("packages", {}).get("", {})
    versions = {
        f"{package_lock_path.name} (version)": lock.get("version"),
        f'{package_lock_path.name} (packages[""].version)': root_package.get("version"),
    }
    for source, version in versions.items():
        if not version:
            raise VersionCheckError(f"{source} has no version field")
    return versions  # type: ignore[return-value]  # None ruled out above


def check_app_versions(
    about_path: Path = ABOUT_PATH,
    package_json_path: Path = EXTENSION_PACKAGE_JSON,
    package_lock_path: Path = EXTENSION_PACKAGE_LOCK,
) -> str:
    """Check every version-holding file carries the same ``X.Y.Z``.

    Returns the agreed version; raises VersionCheckError if any version cannot
    be read, is not ``X.Y.Z``, or differs from ``__about__.py``'s.
    """
    versions = {
        about_path.name: read_backend_version(about_path),
        f"{package_json_path.parent.name}/{package_json_path.name}": (
            read_extension_version(package_json_path)
        ),
        **{
            f"{package_lock_path.parent.name}/{source}": version
            for source, version in read_lockfile_versions(package_lock_path).items()
        },
    }

    for source, version in versions.items():
        parse_version(version, source)

    expected = versions[about_path.name]
    stale = {
        source: version for source, version in versions.items() if version != expected
    }
    if stale:
        listing = ", ".join(
            f"{source} is at {version}" for source, version in stale.items()
        )
        raise VersionCheckError(
            f"{about_path.name} is at {expected} but {listing} - every file must "
            "carry the same version. Bump with scripts/bump_version.py rather "
            "than by hand."
        )

    return expected


def main() -> int:
    try:
        print(f"OK all version files agree on {check_app_versions()}")
    except VersionCheckError as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
