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

"""Release a new version: bump it and date the changelog.

    uv run python scripts/bump_version.py patch   # bug fixes only
    uv run python scripts/bump_version.py minor   # new features
    uv run python scripts/bump_version.py major   # incompatible changes

Run it when you decide to release, not in every PR: look at the entries under
``## [Unreleased]`` in CHANGELOG.md and pick the step semver calls for.

Updates every file check_app_versions.py guards (__about__.py, the extension's
package.json and package-lock.json) and turns ``## [Unreleased]`` in
CHANGELOG.md into ``## [X.Y.Z] - <date>``, with a fresh empty ``[Unreleased]``
above it. The extension's CHANGELOG.md gets the same heading only if its
``[Unreleased]`` section has entries. Nothing is written unless every file can
be updated.
"""

from __future__ import annotations

import argparse
import json
import re
import sys
from dataclasses import dataclass
from datetime import date
from pathlib import Path

from check_app_versions import (
    ABOUT_PATH,
    EXTENSION_PACKAGE_JSON,
    EXTENSION_PACKAGE_LOCK,
    REPO_ROOT,
    VERSION_RE,
    VersionCheckError,
    check_app_versions,
    parse_version,
)

CHANGELOG = REPO_ROOT / "CHANGELOG.md"
EXTENSION_CHANGELOG = REPO_ROOT / "plantuml-extension" / "CHANGELOG.md"

PARTS = ("patch", "minor", "major")
UNRELEASED_HEADING = "## [Unreleased]"
NEXT_SECTION_RE = re.compile(r"^## \[", re.MULTILINE)


class BumpError(Exception):
    """The bump cannot be made; nothing has been written."""


@dataclass(frozen=True)
class Paths:
    about: Path = ABOUT_PATH
    package_json: Path = EXTENSION_PACKAGE_JSON
    package_lock: Path = EXTENSION_PACKAGE_LOCK
    changelog: Path = CHANGELOG
    extension_changelog: Path = EXTENSION_CHANGELOG


def next_version(version: str, part: str) -> str:
    """Return ``version`` one ``part`` ("patch", "minor" or "major") step on."""
    major, minor, patch = parse_version(version, "current")
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
    if part == "major":
        return f"{major + 1}.0.0"
    raise ValueError(f"unknown part {part!r}")


def set_about_version(text: str, version: str) -> str:
    """Return __about__.py source with ``__version__`` set to ``version``."""
    return VERSION_RE.sub(f'__version__ = "{version}"', text, count=1)


def set_package_version(text: str, version: str) -> str:
    """Return package.json or package-lock.json text with the package's own
    version set; a lockfile's ``packages[""]`` copy is set too.

    Re-serialised the way npm writes it (2-space indent, trailing newline).
    """
    data = json.loads(text)
    data["version"] = version
    root_package = data.get("packages", {}).get("")
    if root_package is not None:
        root_package["version"] = version
    return json.dumps(data, indent=2, ensure_ascii=False) + "\n"


def _unreleased_span(text: str) -> tuple[int, int, int]:
    """Return where the ``[Unreleased]`` heading starts, and where its body
    starts and ends."""
    heading = text.find(UNRELEASED_HEADING)
    if heading == -1:
        raise BumpError(f"no '{UNRELEASED_HEADING}' heading")
    body_start = heading + len(UNRELEASED_HEADING)
    next_section = NEXT_SECTION_RE.search(text, body_start)
    return heading, body_start, next_section.start() if next_section else len(text)


def has_unreleased_entries(text: str) -> bool:
    """Whether the ``[Unreleased]`` section holds at least one bullet."""
    _, start, end = _unreleased_span(text)
    return any(line.startswith("- ") for line in text[start:end].splitlines())


def release_unreleased(text: str, version: str, today: date) -> str:
    """Move the ``[Unreleased]`` entries under a new ``[version] - today``
    heading, leaving an empty ``[Unreleased]`` above it."""
    heading, start, end = _unreleased_span(text)
    body = text[start:end].strip("\n")
    rest = text[end:]
    return (
        f"{text[:heading]}{UNRELEASED_HEADING}\n\n"
        f"## [{version}] - {today.isoformat()}\n\n{body}\n"
        + (f"\n{rest}" if rest else "")
    )


def bump(part: str, paths: Paths = Paths(), today: date | None = None) -> str:
    """Bump every version file by one ``part`` step; return the new version."""
    today = today or date.today()
    current = check_app_versions(paths.about, paths.package_json, paths.package_lock)
    new = next_version(current, part)

    changelog = read_text(paths.changelog)
    if not has_unreleased_entries(changelog):
        raise BumpError(
            f"{paths.changelog.name} has no entries under '{UNRELEASED_HEADING}'"
            " - there is nothing to release"
        )

    # Compute every new text first, so a failure leaves nothing half-written.
    updates = {
        paths.about: set_about_version(read_text(paths.about), new),
        paths.package_json: set_package_version(read_text(paths.package_json), new),
        paths.package_lock: set_package_version(read_text(paths.package_lock), new),
        paths.changelog: release_unreleased(changelog, new, today),
    }
    extension_changelog = read_text(paths.extension_changelog)
    if has_unreleased_entries(extension_changelog):
        updates[paths.extension_changelog] = release_unreleased(
            extension_changelog, new, today
        )

    for path, text in updates.items():
        path.write_text(text, encoding="utf-8")

    check_app_versions(paths.about, paths.package_json, paths.package_lock)
    print(f"{current} -> {new}")
    for path in updates:
        print(f"  {path}")
    return new


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "part",
        choices=PARTS,
        help="patch: bug fixes; minor: new features; major: incompatible changes",
    )
    args = parser.parse_args(argv)
    try:
        bump(args.part)
    except (BumpError, VersionCheckError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
