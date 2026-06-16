# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2024 Ericsson
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


def parse_changelog(
    path: Path | None = None,
) -> list[dict[str, str | list[str]]]:
    """Parse CHANGELOG.md and extract External entries per version.

    Returns a list of dicts with keys: version, date, entries.
    """
    if path is None:
        path = Path(__file__).parent.parent.parent / "CHANGELOG.md"

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
