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

"""Pre-commit hook (see .pre-commit-config.yaml) guarding an assumption
webviewPage.js documents but cannot check at runtime: that the browser
libraries loaded from node_modules (plantuml-extension/package.json's
``dependencies``) are the same versions the web app loads from CDNs in
index.html. The two never talk to each other -- the extension vendors its
own copies so the webview's CSP does not have to allow those CDNs -- so
nothing else notices if one is bumped without the other.

Run directly with ``python scripts/check_vendor_versions.py``, or via the
``check-vendor-versions`` pre-commit hook, which is the only place this and
the repo's other checks (ruff, mypy) run, locally and in CI (see
.github/workflows/pre-commit.yml).
"""

from __future__ import annotations

import json
import re
import sys
from dataclasses import dataclass
from pathlib import Path

REPO_ROOT = Path(__file__).resolve().parent.parent
EXTENSION_PACKAGE_JSON = REPO_ROOT / "plantuml-extension" / "package.json"
INDEX_HTML_PATH = REPO_ROOT / "src" / "plantuml_gui" / "templates" / "index.html"

# dependency name in package.json -> regex extracting its version from
# index.html's CDN URLs. Deliberately excludes popper.js and ace, which
# index.html loads but package.json does not vendor (not needed inside the
# webview's context menus/editor, which use VS Code's own equivalents).
CDN_VERSION_PATTERNS = {
    "jquery": re.compile(r"code\.jquery\.com/jquery-(\d+\.\d+\.\d+)"),
    "bootstrap": re.compile(r"cdn\.jsdelivr\.net/npm/bootstrap@([\d.]+)"),
    "diff": re.compile(r"cdnjs\.cloudflare\.com/ajax/libs/jsdiff/([\d.]+)"),
    "panzoom": re.compile(r"unpkg\.com/panzoom@([\d.]+)"),
}

_RANGE_OPERATOR_RE = re.compile(r"^[^\d]*")


def _strip_range_operator(version_range: str) -> str:
    """Strip any leading range operator (``^``, ``~``, etc.) from a
    package.json version specifier, so it can be compared against an exact
    CDN version.
    """
    return _RANGE_OPERATOR_RE.sub("", version_range)


@dataclass(frozen=True)
class VersionCheckResult:
    name: str
    ok: bool
    message: str


def check_vendor_versions(
    package_json_path: Path = EXTENSION_PACKAGE_JSON,
    index_html_path: Path = INDEX_HTML_PATH,
) -> list[VersionCheckResult]:
    """Compare every vendored dependency in CDN_VERSION_PATTERNS against the
    version index.html loads it at.

    Returns one result per entry in CDN_VERSION_PATTERNS, in that order.
    """
    package_json = json.loads(package_json_path.read_text(encoding="utf-8"))
    dependencies = package_json.get("dependencies", {})
    index_html = index_html_path.read_text(encoding="utf-8")

    results = []
    for name, pattern in CDN_VERSION_PATTERNS.items():
        dependency_version = dependencies.get(name)
        if not dependency_version:
            results.append(
                VersionCheckResult(
                    name,
                    False,
                    f"{name} is checked against index.html's CDN but is "
                    "missing from package.json dependencies",
                )
            )
            continue

        match = pattern.search(index_html)
        if not match:
            results.append(
                VersionCheckResult(
                    name,
                    False,
                    f"could not find a {name} CDN URL in index.html matching "
                    f"{pattern.pattern}; update CDN_VERSION_PATTERNS if the "
                    "URL changed",
                )
            )
            continue

        package_version = _strip_range_operator(dependency_version)
        cdn_version = match.group(1)
        if package_version != cdn_version:
            results.append(
                VersionCheckResult(
                    name,
                    False,
                    f"package.json pins {name}@{dependency_version}, but "
                    f"index.html's CDN URL is for {cdn_version} - the "
                    "webview and the web app would render with different "
                    "library versions. Bump whichever one is stale.",
                )
            )
            continue

        results.append(
            VersionCheckResult(name, True, f"{name}@{package_version} matches")
        )

    return results


def main() -> int:
    results = check_vendor_versions()
    failures = [result for result in results if not result.ok]

    for result in results:
        print(f"{'OK' if result.ok else 'FAIL'} {result.message}")

    if failures:
        print(
            f"\n{len(failures)} vendor library version mismatch(es) between "
            "plantuml-extension/package.json and "
            "src/plantuml_gui/templates/index.html.",
            file=sys.stderr,
        )
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())
