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

"""Bump the app version by one patch or minor step above ``origin/main``.

    uv run python scripts/bump_version.py patch   # bug fix, internal change
    uv run python scripts/bump_version.py minor   # new user-facing feature

The new version is one step above the version on the base branch (default
``origin/main``; ``git fetch`` first), not above the branch's own, so running
it again after ``main`` moved on renumbers the branch rather than bumping twice.

Updates every file check_app_versions.py guards (__about__.py, the extension's
package.json and package-lock.json). In CHANGELOG.md, the branch's own version
section (one the base branch does not have) is renamed to the new version; if
there is none yet, ``## [Unreleased]`` becomes ``## [X.Y.Z] - <date>`` with a
fresh empty ``[Unreleased]`` above it. The extension's CHANGELOG.md is treated
the same way, but only gets a section if it has entries. Nothing is written
unless every file can be updated.
"""

from __future__ import annotations

import argparse
import json
import re
import subprocess
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
    backend_version_from_text,
    check_app_versions,
    parse_version,
    read_backend_version,
)

CHANGELOG = REPO_ROOT / "CHANGELOG.md"
EXTENSION_CHANGELOG = REPO_ROOT / "plantuml-extension" / "CHANGELOG.md"

DEFAULT_BASE_REF = "origin/main"

UNRELEASED_HEADING = "## [Unreleased]"
NEXT_SECTION_RE = re.compile(r"^## \[", re.MULTILINE)
VERSION_HEADING_RE = re.compile(r"^## \[(\d[^\]]*)\].*$", re.MULTILINE)


class BumpError(Exception):
    """The bump cannot be made; nothing has been written."""


@dataclass(frozen=True)
class Paths:
    about: Path = ABOUT_PATH
    package_json: Path = EXTENSION_PACKAGE_JSON
    package_lock: Path = EXTENSION_PACKAGE_LOCK
    changelog: Path = CHANGELOG
    extension_changelog: Path = EXTENSION_CHANGELOG


def git_show(ref: str, path: Path, repo: Path = REPO_ROOT) -> str | None:
    """Return ``path`` as it is at ``ref``, or None if git cannot read it."""
    result = subprocess.run(
        ["git", "show", f"{ref}:{path.relative_to(repo).as_posix()}"],
        cwd=repo,
        capture_output=True,
        text=True,
        encoding="utf-8",
        check=False,
    )
    return result.stdout if result.returncode == 0 else None


def normalize_version(version: str) -> str:
    """Pad a pre-X.Y.Z two-part version: ``"0.31"`` -> ``"0.31.0"``."""
    return f"{version}.0" if version.count(".") == 1 else version


def read_base_version(
    ref: str, about_path: Path = ABOUT_PATH, repo: Path = REPO_ROOT
) -> str | None:
    """Return the version in ``__about__.py`` at ``ref``, or None if unreadable."""
    text = git_show(ref, about_path, repo)
    if text is None:
        return None
    return normalize_version(
        backend_version_from_text(text, f"{ref}:{about_path.name}")
    )


def next_version(version: str, part: str) -> str:
    """Return ``version`` one ``part`` ("patch" or "minor") step on."""
    major, minor, patch = parse_version(version, "current")
    if part == "patch":
        return f"{major}.{minor}.{patch + 1}"
    if part == "minor":
        return f"{major}.{minor + 1}.0"
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


def version_sections(text: str) -> list[tuple[re.Match[str], str]]:
    """Return each version heading with its section's body (stripped)."""
    headings = list(VERSION_HEADING_RE.finditer(text))
    sections = []
    for heading in headings:
        next_section = NEXT_SECTION_RE.search(text, heading.end())
        body_end = next_section.start() if next_section else len(text)
        sections.append((heading, text[heading.end() : body_end].strip()))
    return sections


def own_section(text: str, base_text: str) -> re.Match[str] | None:
    """Return the heading of the branch's own version section, if any.

    That is a section whose body the base branch does not have, and whose
    version either the base branch does not have or appears twice here -- the
    case after a rebase onto a ``main`` that released the same number. An old
    section that was only edited keeps its version once, so it is not mistaken
    for the branch's.
    """
    base = version_sections(base_text)
    base_versions = {heading.group(1) for heading, _ in base}
    base_bodies = {body for _, body in base}
    sections = version_sections(text)
    counts: dict[str, int] = {}
    for heading, _ in sections:
        counts[heading.group(1)] = counts.get(heading.group(1), 0) + 1

    own = [
        heading
        for heading, body in sections
        if body not in base_bodies
        and (heading.group(1) not in base_versions or counts[heading.group(1)] > 1)
    ]
    if len(own) > 1:
        versions = ", ".join(heading.group(1) for heading in own)
        raise BumpError(
            f"more than one version section is not on the base branch ({versions})"
            " - merge them into one"
        )
    return own[0] if own else None


def update_changelog(
    text: str,
    base_text: str | None,
    version: str,
    today: date,
    name: str,
    required: bool,
) -> str | None:
    """Return the changelog with the branch's changes under ``version``, or
    None if it has nothing to release.

    Renames the branch's own section if it has one, else releases
    ``[Unreleased]``. ``required`` makes an empty changelog an error.
    """
    own = own_section(text, base_text) if base_text is not None else None
    if own:
        if has_unreleased_entries(text):
            raise BumpError(
                f"{name} has entries both under '{UNRELEASED_HEADING}' and in this"
                f" branch's [{own.group(1)}] section - move them into one"
            )
        heading = f"## [{version}] - {today.isoformat()}"
        return text[: own.start()] + heading + text[own.end() :]
    if has_unreleased_entries(text):
        return release_unreleased(text, version, today)
    if required:
        raise BumpError(
            f"{name} has no entries under '{UNRELEASED_HEADING}'"
            " - describe the change there before bumping"
        )
    return None


def bump(
    part: str,
    paths: Paths = Paths(),
    today: date | None = None,
    base_ref: str = DEFAULT_BASE_REF,
    repo: Path = REPO_ROOT,
) -> str:
    """Set every version file one ``part`` step above ``base_ref``'s version;
    return the new version."""
    today = today or date.today()
    ref: str | None = base_ref
    base = read_base_version(base_ref, paths.about, repo)
    if base is None:
        base = read_backend_version(paths.about)
        ref = None
        print(
            f"WARNING could not read {base_ref}; bumping from this branch's"
            f" {base} instead, so running this twice bumps twice",
            file=sys.stderr,
        )
    new = next_version(base, part)

    # Compute every new text first, so a failure leaves nothing half-written.
    updates = {
        paths.about: set_about_version(read_text(paths.about), new),
        paths.package_json: set_package_version(read_text(paths.package_json), new),
        paths.package_lock: set_package_version(read_text(paths.package_lock), new),
    }
    for changelog, required in (
        (paths.changelog, True),
        (paths.extension_changelog, False),
    ):
        base_text = git_show(ref, changelog, repo) if ref else None
        text = update_changelog(
            read_text(changelog), base_text, new, today, changelog.name, required
        )
        if text is not None:
            updates[changelog] = text

    for path, text in updates.items():
        path.write_text(text, encoding="utf-8")

    check_app_versions(paths.about, paths.package_json, paths.package_lock)
    print(f"{base} ({ref or 'local'}) -> {new}")
    for path in updates:
        print(f"  {path}")
    return new


def read_text(path: Path) -> str:
    return path.read_text(encoding="utf-8")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument(
        "part",
        choices=["patch", "minor"],
        help="patch: bug fix or internal change; minor: new user-facing feature",
    )
    parser.add_argument(
        "--base-ref",
        default=DEFAULT_BASE_REF,
        help=f"branch to bump above (default: {DEFAULT_BASE_REF})",
    )
    args = parser.parse_args(argv)
    try:
        bump(args.part, base_ref=args.base_ref)
    except (BumpError, VersionCheckError) as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
