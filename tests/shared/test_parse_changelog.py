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

"""Tests for shared/parse_changelog.py: the CHANGELOG.md -> Version History feed.

The file keeps one section per X.Y.Z (every merged PR bumps the version); users
are shown one per X.Y. Most tests use a fixture changelog, so a failure means
the parser is wrong rather than that CHANGELOG.md was edited.
"""

import re

import pytest
from plantuml_gui.__about__ import __version__
from plantuml_gui.shared.parse_changelog import (
    display_version,
    group_by_minor,
    parse_changelog,
    parse_changelog_sections,
)

FIXTURE = """\
# Changelog

Preamble that is not a version.

## [Unreleased]

### External

- Pending feature.

## [0.32.2] - 2026-11-20

### External

- Fixed note colour.

### Internal

- Refactored box hit-testing.

## [0.32.1] - 2026-11-12

### Internal

- Bumped Playwright.

## [0.32.0] - 2026-11-05

### External

- Added multi-page navigation.
- Added duplicate participant.

## [0.31.1] - 2026-08-01

### Internal

- Internal-only patch on top of a two-part release.

## [0.31] - 2026-07-22

### External

- Legacy two-part release.

## [0.30.0] - 2026-07-03

### Internal

- A minor with no user-facing change.
"""


@pytest.fixture()
def changelog(tmp_path):
    path = tmp_path / "CHANGELOG.md"
    path.write_text(FIXTURE, encoding="utf-8")
    return path


class TestDisplayVersion:
    @pytest.mark.parametrize(
        ("version", "expected"),
        [
            ("0.32.3", "0.32"),
            ("1.0.0", "1.0"),
            ("0.31", "0.31"),
            ("Unreleased", "Unreleased"),
        ],
    )
    def test_trims_to_major_minor(self, version, expected):
        assert display_version(version) == expected


class TestParseChangelogSections:
    def test_one_section_per_heading_as_written(self, changelog):
        versions = [s["version"] for s in parse_changelog_sections(changelog)]

        assert versions == [
            "Unreleased",
            "0.32.2",
            "0.32.1",
            "0.32.0",
            "0.31.1",
            "0.31",
            "0.30.0",
        ]

    def test_only_external_entries_are_collected(self, changelog):
        sections = {s["version"]: s for s in parse_changelog_sections(changelog)}

        assert sections["0.32.2"]["entries"] == ["Fixed note colour."]
        assert sections["0.32.1"]["entries"] == []


class TestParseChangelog:
    def test_patches_fold_into_one_entry_per_minor(self, changelog):
        versions = [v["version"] for v in parse_changelog(changelog)]

        assert versions == ["Unreleased", "0.32", "0.31"]

    def test_entries_keep_file_order_latest_patch_first(self, changelog):
        minor = next(v for v in parse_changelog(changelog) if v["version"] == "0.32")

        assert minor["entries"] == [
            "Fixed note colour.",
            "Added multi-page navigation.",
            "Added duplicate participant.",
        ]

    def test_date_is_when_the_minor_first_shipped(self, changelog):
        minor = next(v for v in parse_changelog(changelog) if v["version"] == "0.32")

        assert minor["date"] == "2026-11-05"

    def test_legacy_two_part_heading_groups_with_its_patches(self, changelog):
        minor = next(v for v in parse_changelog(changelog) if v["version"] == "0.31")

        assert minor["entries"] == ["Legacy two-part release."]
        assert minor["date"] == "2026-07-22"

    def test_minor_with_only_internal_changes_is_dropped(self, changelog):
        assert "0.30" not in [v["version"] for v in parse_changelog(changelog)]

    def test_unreleased_is_kept_even_when_empty(self):
        sections = [{"version": "Unreleased", "date": "", "entries": []}]

        assert group_by_minor(sections) == sections

    def test_real_changelog_shows_only_major_minor(self):
        """CHANGELOG.md as committed: no X.Y.Z ever reaches the panel."""
        for version in parse_changelog():
            assert version["version"] == "Unreleased" or re.fullmatch(
                r"\d+\.\d+", str(version["version"])
            ), version["version"]


class TestRoutes:
    def test_changelog_route_returns_grouped_versions(self, client):
        response = client.get("/changelog")

        assert response.status_code == 200
        assert response.get_json() == parse_changelog()

    def test_version_badge_shows_major_minor(self, client):
        html = client.get("/").get_data(as_text=True)

        badge = re.search(r'id="version"[^>]*>v([^<]+)<', html)
        assert badge, "version badge not found in index.html"
        assert badge.group(1) == display_version(__version__)
        assert re.fullmatch(r"\d+\.\d+", badge.group(1))
