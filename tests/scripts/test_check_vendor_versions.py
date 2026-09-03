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

"""Tests for scripts/check_vendor_versions.py.

Uses small fixture package.json/index.html files rather than the repo's real
ones, so a test failure here always means the *checker* is wrong -- not that
someone bumped a real dependency and forgot the other side, which is exactly
what the checker itself (and the pre-commit hook) is responsible for catching.
"""

import json
import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_vendor_versions import check_vendor_versions  # noqa: E402

INDEX_HTML_TEMPLATE = """<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap@{bootstrap}/dist/css/bootstrap.min.css">
    <script src="https://code.jquery.com/jquery-{jquery}.slim.min.js"></script>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@{bootstrap}/dist/js/bootstrap.min.js"></script>
    <script src="https://cdnjs.cloudflare.com/ajax/libs/jsdiff/{diff}/diff.min.js"></script>
    <script src='https://unpkg.com/panzoom@{panzoom}/dist/panzoom.min.js'></script>
</head>
</html>
"""


def _write_fixture(
    tmp_path: Path,
    *,
    jquery: str = "3.7.1",
    bootstrap: str = "4.6.2",
    diff: str = "8.0.3",
    panzoom: str = "9.4.0",
    dependencies: dict[str, str] | None = None,
) -> tuple[Path, Path]:
    """Write a package.json/index.html pair to tmp_path and return their paths.

    By default, the CDN versions and the package.json dependencies all agree,
    so tests only need to override what they are exercising.
    """
    if dependencies is None:
        dependencies = {
            "jquery": jquery,
            "bootstrap": bootstrap,
            "diff": diff,
            "panzoom": panzoom,
        }

    package_json_path = tmp_path / "package.json"
    package_json_path.write_text(
        json.dumps({"name": "fixture", "dependencies": dependencies}),
        encoding="utf-8",
    )

    index_html_path = tmp_path / "index.html"
    index_html_path.write_text(
        INDEX_HTML_TEMPLATE.format(
            jquery=jquery, bootstrap=bootstrap, diff=diff, panzoom=panzoom
        ),
        encoding="utf-8",
    )

    return package_json_path, index_html_path


class TestCheckVendorVersions:
    def test_all_versions_matching_pass(self, tmp_path):
        package_json_path, index_html_path = _write_fixture(tmp_path)

        results = check_vendor_versions(package_json_path, index_html_path)

        assert len(results) == 4
        assert all(result.ok for result in results)

    def test_reports_mismatched_version(self, tmp_path):
        package_json_path, index_html_path = _write_fixture(tmp_path, bootstrap="4.6.2")
        # Simulate index.html not having been bumped alongside package.json.
        index_html_path.write_text(
            index_html_path.read_text(encoding="utf-8").replace(
                "bootstrap@4.6.2", "bootstrap@4.0.0"
            ),
            encoding="utf-8",
        )

        results = check_vendor_versions(package_json_path, index_html_path)
        by_name = {result.name: result for result in results}

        assert not by_name["bootstrap"].ok
        assert "4.6.2" in by_name["bootstrap"].message
        assert "4.0.0" in by_name["bootstrap"].message
        # Everything else still agrees and should not be flagged.
        assert by_name["jquery"].ok
        assert by_name["diff"].ok
        assert by_name["panzoom"].ok

    def test_strips_range_operator_before_comparing(self, tmp_path):
        # package.json may pin with a range (e.g. "^8.0.4"); only the exact
        # CDN version can ever be loaded, so the comparison should look past
        # the operator rather than always failing on it.
        package_json_path, index_html_path = _write_fixture(tmp_path, diff="8.0.3")
        package_json_path.write_text(
            package_json_path.read_text(encoding="utf-8").replace(
                '"diff": "8.0.3"', '"diff": "^8.0.3"'
            ),
            encoding="utf-8",
        )

        results = check_vendor_versions(package_json_path, index_html_path)
        by_name = {result.name: result for result in results}

        assert by_name["diff"].ok

    def test_reports_dependency_missing_from_package_json(self, tmp_path):
        package_json_path, index_html_path = _write_fixture(
            tmp_path,
            dependencies={
                "bootstrap": "4.6.2",
                "diff": "8.0.3",
                "panzoom": "9.4.0",
                # jquery deliberately omitted.
            },
        )

        results = check_vendor_versions(package_json_path, index_html_path)
        by_name = {result.name: result for result in results}

        assert not by_name["jquery"].ok
        assert "missing from package.json" in by_name["jquery"].message

    def test_reports_cdn_url_not_found_in_index_html(self, tmp_path):
        package_json_path, index_html_path = _write_fixture(tmp_path)
        index_html_path.write_text("<html><head></head></html>", encoding="utf-8")

        results = check_vendor_versions(package_json_path, index_html_path)

        assert all(not result.ok for result in results)
        assert all("could not find a" in result.message for result in results)

    @pytest.mark.parametrize("name", ["jquery", "bootstrap", "diff", "panzoom"])
    def test_against_the_real_repo_files(self, name):
        """The real files this hook guards should actually agree right now.

        A failure here means a real version was bumped on only one side --
        the same drift the pre-commit hook exists to catch -- and should be
        fixed in the same commit, not just acknowledged by this test.
        """
        results = check_vendor_versions()
        by_name = {result.name: result for result in results}

        assert by_name[name].ok, by_name[name].message
