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

Uses small fixture __about__.py/package.json files rather than the repo's real
ones, so a failure here always means the *checker* is wrong -- not that someone
released one side without the other, which is what the checker itself (and the
pre-commit hook) is responsible for catching. The one exception is
test_against_the_real_repo_files.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_app_versions import VersionCheckError, check_app_versions  # noqa: E402


def _write_fixture(
    tmp_path: Path,
    *,
    backend_version: str = "0.31",
    extension_version: str = "0.31.0",
) -> tuple[Path, Path]:
    """Write an __about__.py/package.json pair to tmp_path."""
    about_path = tmp_path / "__about__.py"
    about_path.write_text(f'__version__ = "{backend_version}"\n', encoding="utf-8")

    package_json_path = tmp_path / "package.json"
    package_json_path.write_text(
        json.dumps({"name": "fixture", "version": extension_version}),
        encoding="utf-8",
    )

    return about_path, package_json_path


class TestCheckAppVersions:
    def test_matching_versions_pass(self, tmp_path):
        about_path, package_json_path = _write_fixture(tmp_path)

        message = check_app_versions(about_path, package_json_path)

        assert "0.31" in message
        assert "0.31.0" in message

    def test_extension_patch_component_is_free(self, tmp_path):
        # An extension-only fix may ship without a backend release.
        about_path, package_json_path = _write_fixture(
            tmp_path, extension_version="0.31.4"
        )

        assert check_app_versions(about_path, package_json_path)

    def test_reports_mismatch(self, tmp_path):
        about_path, package_json_path = _write_fixture(
            tmp_path, backend_version="0.32", extension_version="0.31.0"
        )

        with pytest.raises(VersionCheckError) as error:
            check_app_versions(about_path, package_json_path)

        assert "0.32" in str(error.value)
        assert "0.31.0" in str(error.value)

    def test_against_the_real_repo_files(self):
        """The real versions this hook guards should agree right now.

        A failure here means one side was bumped alone -- the same drift the
        pre-commit hook exists to catch -- and should be fixed in the same
        commit, not just acknowledged by this test.
        """
        assert check_app_versions()

    def test_missing_backend_version_raises(self, tmp_path):
        about_path = tmp_path / "__about__.py"
        about_path.write_text("# no __version__ here\n", encoding="utf-8")
        package_json_path = tmp_path / "package.json"
        package_json_path.write_text(
            json.dumps({"name": "fixture", "version": "0.31.0"}), encoding="utf-8"
        )

        with pytest.raises(VersionCheckError, match="__version__"):
            check_app_versions(about_path, package_json_path)

    def test_missing_extension_version_raises(self, tmp_path):
        about_path = tmp_path / "__about__.py"
        about_path.write_text('__version__ = "0.31"\n', encoding="utf-8")
        package_json_path = tmp_path / "package.json"
        package_json_path.write_text(json.dumps({"name": "fixture"}), encoding="utf-8")

        with pytest.raises(VersionCheckError, match="no version field"):
            check_app_versions(about_path, package_json_path)
