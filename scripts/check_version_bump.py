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

"""CI check: the version on this branch is exactly one patch or minor step
above the base branch's.

    python scripts/check_version_bump.py --base-ref origin/main

Run by .github/workflows/version-check.yml on pull requests to main. The fix
for every failure is the same: fetch, rebase onto main, and run
scripts/bump_version.py patch|minor.
"""

from __future__ import annotations

import argparse
import sys

from bump_version import DEFAULT_BASE_REF, next_version, read_base_version
from check_app_versions import VersionCheckError, check_app_versions, parse_version

FIX = "run 'git fetch', rebase onto main, then scripts/bump_version.py patch|minor"


def check_version_bump(base: str, head: str) -> str:
    """Return a message if ``head`` is one patch or minor step above
    ``base``; raise VersionCheckError otherwise."""
    allowed = {next_version(base, "patch"), next_version(base, "minor")}
    if head in allowed:
        return f"{base} -> {head}"

    if parse_version(head, "this branch") <= parse_version(base, "main"):
        problem = f"the version on this branch ({head}) is not above main's ({base})"
    else:
        problem = (
            f"{head} is more than one patch or minor step above main's {base}"
            f" (expected {' or '.join(sorted(allowed))})"
        )
    raise VersionCheckError(f"{problem} - {FIX}")


def main(argv: list[str] | None = None) -> int:
    parser = argparse.ArgumentParser(description=__doc__.splitlines()[0])
    parser.add_argument("--base-ref", default=DEFAULT_BASE_REF)
    args = parser.parse_args(argv)
    try:
        base = read_base_version(args.base_ref)
        if base is None:
            raise VersionCheckError(f"could not read the version at {args.base_ref}")
        print(f"OK {check_version_bump(base, check_app_versions())}")
    except VersionCheckError as error:
        print(f"FAIL {error}", file=sys.stderr)
        return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
