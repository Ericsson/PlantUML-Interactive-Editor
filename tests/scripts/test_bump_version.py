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

"""Tests for scripts/bump_version.py, run against fixture copies of the files."""

import json
import shutil
import sys
from datetime import date
from pathlib import Path

import pytest

REPO_ROOT = Path(__file__).resolve().parents[2]
sys.path.insert(0, str(REPO_ROOT / "scripts"))

from bump_version import (  # noqa: E402
    BumpError,
    Paths,
    bump,
    has_unreleased_entries,
    main,
    next_version,
    release_unreleased,
    set_package_version,
)
from check_app_versions import VersionCheckError, check_app_versions  # noqa: E402

TODAY = date(2026, 11, 2)

CHANGELOG = """\
# Changelog

## [Unreleased]

### External

- Added a thing.

### Internal

- Refactored a thing.

## [0.31] - 2026-07-22

### External

- Older entry.
"""

EXTENSION_CHANGELOG = """\
# Change Log

## [Unreleased]

## [0.31.0]

- First packaged release.
"""


def _write_fixture(
    tmp_path: Path,
    *,
    version: str = "0.31.0",
    changelog: str = CHANGELOG,
    extension_changelog: str = EXTENSION_CHANGELOG,
) -> Paths:
    paths = Paths(
        about=tmp_path / "__about__.py",
        package_json=tmp_path / "package.json",
        package_lock=tmp_path / "package-lock.json",
        changelog=tmp_path / "CHANGELOG.md",
        extension_changelog=tmp_path / "EXTENSION_CHANGELOG.md",
    )
    paths.about.write_text(f'# header\n__version__ = "{version}"\n', encoding="utf-8")
    paths.package_json.write_text(
        json.dumps({"name": "fixture", "version": version}, indent=2) + "\n",
        encoding="utf-8",
    )
    lock = {
        "name": "fixture",
        "version": version,
        "packages": {
            "": {"name": "fixture", "version": version},
            "node_modules/dep": {"version": "1.2.3"},
        },
    }
    paths.package_lock.write_text(json.dumps(lock, indent=2) + "\n", encoding="utf-8")
    paths.changelog.write_text(changelog, encoding="utf-8")
    paths.extension_changelog.write_text(extension_changelog, encoding="utf-8")
    return paths


class TestNextVersion:
    @pytest.mark.parametrize(
        ("version", "part", "expected"),
        [
            ("0.31.0", "patch", "0.31.1"),
            ("0.31.9", "patch", "0.31.10"),
            ("0.31.4", "minor", "0.32.0"),
            ("1.9.2", "minor", "1.10.0"),
        ],
    )
    def test_steps(self, version, part, expected):
        assert next_version(version, part) == expected

    def test_rejects_a_two_part_version(self):
        with pytest.raises(VersionCheckError):
            next_version("0.31", "patch")


class TestReleaseUnreleased:
    def test_moves_entries_under_a_dated_heading(self):
        result = release_unreleased(CHANGELOG, "0.31.1", TODAY)

        assert result == CHANGELOG.replace(
            "## [Unreleased]\n\n### External",
            "## [Unreleased]\n\n## [0.31.1] - 2026-11-02\n\n### External",
        )

    def test_unreleased_as_last_section(self):
        text = "# Change Log\n\n## [Unreleased]\n\n- Only entry.\n"

        assert release_unreleased(text, "0.31.1", TODAY) == (
            "# Change Log\n\n## [Unreleased]\n\n"
            "## [0.31.1] - 2026-11-02\n\n- Only entry.\n"
        )

    def test_missing_unreleased_heading(self):
        with pytest.raises(BumpError, match="Unreleased"):
            release_unreleased("# Changelog\n", "0.31.1", TODAY)

    def test_entries_are_found_only_under_unreleased(self):
        assert has_unreleased_entries(CHANGELOG)
        assert not has_unreleased_entries(EXTENSION_CHANGELOG)
        # Subsection headings alone are not entries.
        assert not has_unreleased_entries(
            "## [Unreleased]\n\n### External\n\n### Internal\n\n## [0.31]\n\n- x\n"
        )


class TestSetPackageVersion:
    def test_lockfile_sets_both_copies_and_leaves_dependencies(self):
        lock = {
            "version": "0.31.0",
            "packages": {
                "": {"version": "0.31.0"},
                "node_modules/x": {"version": "1.0.0"},
            },
        }

        result = json.loads(set_package_version(json.dumps(lock), "0.31.1"))

        assert result["version"] == "0.31.1"
        assert result["packages"][""]["version"] == "0.31.1"
        assert result["packages"]["node_modules/x"]["version"] == "1.0.0"

    @pytest.mark.parametrize("name", ["package.json", "package-lock.json"])
    def test_real_files_only_change_on_version_lines(self, name):
        """npm's own formatting survives, so the diff is just the version."""
        original = (REPO_ROOT / "plantuml-extension" / name).read_text(encoding="utf-8")
        current = json.loads(original)["version"]

        result = set_package_version(original, "9.9.9")

        changed = [
            (old, new)
            for old, new in zip(original.splitlines(), result.splitlines())
            if old != new
        ]
        assert len(original.splitlines()) == len(result.splitlines())
        assert changed and all(
            old.replace(current, "9.9.9") == new for old, new in changed
        )


class TestBump:
    def test_patch_updates_every_file(self, tmp_path):
        paths = _write_fixture(tmp_path)

        assert bump("patch", paths, TODAY) == "0.31.1"

        assert (
            check_app_versions(paths.about, paths.package_json, paths.package_lock)
            == "0.31.1"
        )
        assert paths.about.read_text(encoding="utf-8").startswith("# header\n")
        changelog = paths.changelog.read_text(encoding="utf-8")
        assert (
            "## [Unreleased]\n\n## [0.31.1] - 2026-11-02\n\n### External" in changelog
        )

    def test_minor_resets_the_patch(self, tmp_path):
        paths = _write_fixture(tmp_path, version="0.31.4")

        assert bump("minor", paths, TODAY) == "0.32.0"

    def test_extension_changelog_untouched_without_entries(self, tmp_path):
        paths = _write_fixture(tmp_path)

        bump("patch", paths, TODAY)

        assert (
            paths.extension_changelog.read_text(encoding="utf-8") == EXTENSION_CHANGELOG
        )

    def test_extension_changelog_released_with_entries(self, tmp_path):
        paths = _write_fixture(
            tmp_path,
            extension_changelog=EXTENSION_CHANGELOG.replace(
                "## [Unreleased]\n", "## [Unreleased]\n\n- Markdown support.\n"
            ),
        )

        bump("minor", paths, TODAY)

        text = paths.extension_changelog.read_text(encoding="utf-8")
        assert (
            "## [Unreleased]\n\n## [0.32.0] - 2026-11-02\n\n- Markdown support.\n"
            in text
        )

    def test_refuses_without_changelog_entries_and_writes_nothing(self, tmp_path):
        empty = "# Changelog\n\n## [Unreleased]\n\n## [0.31] - 2026-07-22\n\n- x\n"
        paths = _write_fixture(tmp_path, changelog=empty)
        before = {p: p.read_text(encoding="utf-8") for p in vars(paths).values()}

        with pytest.raises(BumpError, match="no entries under"):
            bump("patch", paths, TODAY)

        assert {p: p.read_text(encoding="utf-8") for p in before} == before

    def test_refuses_when_files_already_disagree(self, tmp_path):
        paths = _write_fixture(tmp_path)
        paths.package_json.write_text('{"version": "0.30.0"}\n', encoding="utf-8")

        with pytest.raises(VersionCheckError):
            bump("patch", paths, TODAY)

        assert '"0.31.0"' in paths.about.read_text(encoding="utf-8")


class TestMain:
    def test_rejects_an_unknown_part(self):
        with pytest.raises(SystemExit):
            main(["major"])

    def test_real_files_end_to_end(self, tmp_path):
        """On copies of the real files, with an entry added to [Unreleased]."""
        files = {
            "about": REPO_ROOT / "src" / "plantuml_gui" / "__about__.py",
            "package_json": REPO_ROOT / "plantuml-extension" / "package.json",
            "package_lock": REPO_ROOT / "plantuml-extension" / "package-lock.json",
            "changelog": REPO_ROOT / "CHANGELOG.md",
            "extension_changelog": REPO_ROOT / "plantuml-extension" / "CHANGELOG.md",
        }
        copies = {}
        for field, source in files.items():
            copies[field] = tmp_path / f"{field}{source.suffix}"
            shutil.copy(source, copies[field])
        paths = Paths(**copies)
        changelog = paths.changelog.read_text(encoding="utf-8")
        paths.changelog.write_text(
            changelog.replace(
                "## [Unreleased]\n", "## [Unreleased]\n\n- Test entry.\n", 1
            ),
            encoding="utf-8",
        )
        current = check_app_versions(
            paths.about, paths.package_json, paths.package_lock
        )

        new = bump("patch", paths, TODAY)

        assert new == next_version(current, "patch")
        assert f"## [{new}] - 2026-11-02" in paths.changelog.read_text(encoding="utf-8")
