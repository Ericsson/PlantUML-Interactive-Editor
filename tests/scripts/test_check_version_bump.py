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

"""Tests for scripts/check_version_bump.py."""

import sys
from pathlib import Path

import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[2] / "scripts"))

from check_app_versions import VersionCheckError  # noqa: E402
from check_version_bump import check_version_bump, main  # noqa: E402


class TestCheckVersionBump:
    @pytest.mark.parametrize(
        ("base", "head"),
        [("0.31.0", "0.31.1"), ("0.31.4", "0.32.0"), ("0.31.9", "0.31.10")],
    )
    def test_one_step_passes(self, base, head):
        assert check_version_bump(base, head) == f"{base} -> {head}"

    @pytest.mark.parametrize(
        ("head", "message"),
        [
            ("0.31.0", "not above main's"),
            ("0.30.9", "not above main's"),
            ("0.31.2", "more than one"),
            ("0.33.0", "more than one"),
            ("0.32.1", "more than one"),
            ("1.0.0", "more than one"),
        ],
    )
    def test_anything_else_fails_and_says_how_to_fix(self, head, message):
        with pytest.raises(VersionCheckError, match=message) as error:
            check_version_bump("0.31.0", head)

        assert "bump_version.py" in str(error.value)

    def test_unreadable_base_ref_fails(self, capsys):
        assert main(["--base-ref", "no-such-ref-for-this-test"]) == 1

        assert "could not read the version" in capsys.readouterr().err
