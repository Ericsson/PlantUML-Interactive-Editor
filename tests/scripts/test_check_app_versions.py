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

"""Tests for scripts/check_app_versions.py.

Uses small fixture __about__.py/package.json/package-lock.json files rather than
the repo's real ones, so a failure here always means the *checker* is wrong --
not that someone bumped one file without the others, which is what the checker
itself (and the pre-commit hook) is responsible for catching. The one exception
is test_against_the_real_repo_files.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_app_versions import (  # noqa: E402
    VersionCheckError,
    check_app_versions,
    parse_version,
)


def _write_fixture(
    tmp_path: Path,
    *,
    backend_version: str = "0.31.0",
    extension_version: str = "0.31.0",
    lock_version: str | None = "0.31.0",
    lock_root_version: str | None = "0.31.0",
) -> tuple[Path, Path, Path]:
    """Write an __about__.py/package.json/package-lock.json trio to tmp_path.

    A lock version of None leaves that field out.
    """
    about_path = tmp_path / "__about__.py"
    about_path.write_text(f'__version__ = "{backend_version}"\n', encoding="utf-8")

    package_json_path = tmp_path / "package.json"
    package_json_path.write_text(
        json.dumps({"name": "fixture", "version": extension_version}),
        encoding="utf-8",
    )

    root_package: dict[str, str] = {"name": "fixture"}
    if lock_root_version is not None:
        root_package["version"] = lock_root_version
    lock: dict[str, object] = {"name": "fixture", "packages": {"": root_package}}
    if lock_version is not None:
        lock["version"] = lock_version
    package_lock_path = tmp_path / "package-lock.json"
    package_lock_path.write_text(json.dumps(lock), encoding="utf-8")

    return about_path, package_json_path, package_lock_path


class TestCheckAppVersions:
    def test_matching_versions_pass(self, tmp_path):
        assert check_app_versions(*_write_fixture(tmp_path)) == "0.31.0"

    def test_extension_patch_mismatch_fails(self, tmp_path):
        # The extension's patch component is no longer free: one X.Y.Z for all.
        paths = _write_fixture(tmp_path, extension_version="0.31.1")

        with pytest.raises(VersionCheckError) as error:
            check_app_versions(*paths)

        assert "package.json is at 0.31.1" in str(error.value)
        assert "0.31.0" in str(error.value)

    def test_backend_minor_mismatch_fails(self, tmp_path):
        paths = _write_fixture(tmp_path, backend_version="0.32.0")

        with pytest.raises(VersionCheckError, match="__about__.py is at 0.32.0"):
            check_app_versions(*paths)

    def test_stale_lockfile_top_level_version_fails(self, tmp_path):
        paths = _write_fixture(tmp_path, lock_version="0.30.0")

        with pytest.raises(VersionCheckError) as error:
            check_app_versions(*paths)

        assert "package-lock.json (version) is at 0.30.0" in str(error.value)
        assert "packages" not in str(error.value)

    def test_stale_lockfile_root_package_version_fails(self, tmp_path):
        paths = _write_fixture(tmp_path, lock_root_version="0.30.0")

        with pytest.raises(VersionCheckError) as error:
            check_app_versions(*paths)

        assert 'packages[""].version) is at 0.30.0' in str(error.value)

    def test_every_stale_file_is_named(self, tmp_path):
        paths = _write_fixture(
            tmp_path, extension_version="0.30.0", lock_version="0.30.0"
        )

        with pytest.raises(VersionCheckError) as error:
            check_app_versions(*paths)

        assert "package.json is at 0.30.0" in str(error.value)
        assert "package-lock.json (version) is at 0.30.0" in str(error.value)

    def test_two_component_version_fails_even_when_all_agree(self, tmp_path):
        paths = _write_fixture(
            tmp_path,
            backend_version="0.31",
            extension_version="0.31",
            lock_version="0.31",
            lock_root_version="0.31",
        )

        with pytest.raises(VersionCheckError, match="not of the form X.Y.Z"):
            check_app_versions(*paths)

    def test_two_component_backend_against_three_component_extension_fails(
        self, tmp_path
    ):
        # The pre-migration pairing (0.31 / 0.31.0) is no longer accepted.
        paths = _write_fixture(tmp_path, backend_version="0.31")

        with pytest.raises(VersionCheckError, match="not of the form X.Y.Z"):
            check_app_versions(*paths)

    def test_missing_backend_version_raises(self, tmp_path):
        about_path, package_json_path, package_lock_path = _write_fixture(tmp_path)
        about_path.write_text("# no __version__ here\n", encoding="utf-8")

        with pytest.raises(VersionCheckError, match="__version__"):
            check_app_versions(about_path, package_json_path, package_lock_path)

    def test_missing_extension_version_raises(self, tmp_path):
        about_path, package_json_path, package_lock_path = _write_fixture(tmp_path)
        package_json_path.write_text(json.dumps({"name": "fixture"}), encoding="utf-8")

        with pytest.raises(VersionCheckError, match="no version field"):
            check_app_versions(about_path, package_json_path, package_lock_path)

    def test_missing_lockfile_version_raises(self, tmp_path):
        paths = _write_fixture(tmp_path, lock_root_version=None)

        with pytest.raises(VersionCheckError, match="no version field"):
            check_app_versions(*paths)

    def test_against_the_real_repo_files(self):
        """The real versions this hook guards should agree right now.

        A failure here means one file was bumped alone -- the same drift the
        pre-commit hook exists to catch -- and should be fixed in the same
        commit, not just acknowledged by this test.
        """
        assert check_app_versions()


class TestParseVersion:
    def test_three_components(self):
        assert parse_version("0.31.2", "x") == (0, 31, 2)

    @pytest.mark.parametrize(
        "version",
        ["0.31", "0.31.0.1", "0.31.x", "v0.31.0", "0.031.0", "", "0.31.0-rc1"],
    )
    def test_rejects_anything_but_plain_x_y_z(self, version):
        with pytest.raises(VersionCheckError, match="not of the form X.Y.Z"):
            parse_version(version, "x")
