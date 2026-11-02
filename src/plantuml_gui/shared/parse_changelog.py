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

import re
from pathlib import Path

ChangelogSection = dict[str, str | list[str]]


def display_version(version: str) -> str:
    """Trim a version to ``X.Y``: ``"0.32.3"`` -> ``"0.32"``."""
    parts = version.split(".")
    return ".".join(parts[:2]) if len(parts) > 2 else version


def parse_changelog(
    path: Path | None = None,
) -> list[ChangelogSection]:
    """Parse CHANGELOG.md into one entry per ``X.Y``, newest first."""
    return group_by_minor(parse_changelog_sections(path))


def group_by_minor(sections: list[ChangelogSection]) -> list[ChangelogSection]:
    """Merge ``X.Y.Z`` sections into one ``X.Y`` section each.

    The date is the oldest patch's; groups without entries are dropped,
    except ``Unreleased``.
    """
    groups: dict[str, ChangelogSection] = {}
    for section in sections:
        key = display_version(str(section["version"]))
        group = groups.setdefault(key, {"version": key, "date": "", "entries": []})
        entries = group["entries"]
        assert isinstance(entries, list)  # type narrowing for mypy
        entries.extend(section["entries"])
        if section["date"]:
            group["date"] = section["date"]
    return [
        group
        for group in groups.values()
        if group["entries"] or group["version"] == "Unreleased"
    ]


def parse_changelog_sections(
    path: Path | None = None,
) -> list[ChangelogSection]:
    """Parse CHANGELOG.md and extract External entries per version heading.

    Returns a list of dicts with keys: version, date, entries.
    """
    if path is None:
        path = Path(__file__).parent.parent.parent.parent / "CHANGELOG.md"

    content = path.read_text(encoding="utf-8")
    versions: list[dict[str, str | list[str]]] = []
    current: dict[str, str | list[str]] | None = None
    in_external = False

    for line in content.splitlines():
        # Detect version headers like "## [0.28] - 2025-08-18" or "## [Unreleased]"
        version_match = re.match(r"^## \[(.+?)\]\s*-?\s*(.*)", line)
        if version_match:
            # Save the previous version section before starting a new one
            if current:
                versions.append(current)
            current = {
                "version": version_match.group(1),
                "date": version_match.group(2).strip(),
                "entries": [],
            }
            in_external = False
            continue

        # Skip lines before the first version header
        if current is None:
            continue

        # Track whether we're inside an ### External subsection
        if line.strip() == "### External":
            in_external = True
            continue
        elif line.startswith("### "):
            # Any other subsection (e.g. ### Internal) exits External
            in_external = False
            continue

        # Collect bullet points from the External subsection
        if in_external and line.startswith("- "):
            entries = current["entries"]
            assert isinstance(entries, list)  # type narrowing for mypy
            entries.append(line[2:])

    # Don't forget the last version section
    if current:
        versions.append(current)

    return versions
