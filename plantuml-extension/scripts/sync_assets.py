#!/usr/bin/env python3
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

"""Copy the web app's frontend into the extension so the webview can load it.

The extension reuses the web app's interaction code verbatim -- activity.js,
sequence-*.js and the context-menu markup implement every diagram interaction
already, and reimplementing them would fork thousands of lines. The webview
cannot read out of src/plantuml_gui/, so the files are mirrored into
plantuml-extension/media/.

Copying by hand is what this script exists to prevent: two copies of
activity.js diverge, and then a bug gets fixed in one of them. Run
`npm run sync-assets` after touching anything under src/plantuml_gui/static or
templates/partials. `--check` verifies the mirror is current and is meant for
CI.

The menu partials are rendered through Jinja rather than copied, because
sequence_menus.html defines and calls a `color_select` macro -- a plain copy
would leave `{{ color_select(...) }}` in the HTML and the colour dropdowns
would silently not exist.
"""

import argparse
import sys
from pathlib import Path

from jinja2 import Environment, FileSystemLoader

EXTENSION_DIR = Path(__file__).resolve().parent.parent
REPO_ROOT = EXTENSION_DIR.parent
STATIC_DIR = REPO_ROOT / "src" / "plantuml_gui" / "static"
PARTIALS_DIR = REPO_ROOT / "src" / "plantuml_gui" / "templates" / "partials"
MEDIA_DIR = EXTENSION_DIR / "media"
NODE_MODULES = EXTENSION_DIR / "node_modules"

# Ace's PlantUML syntax mode. The webview has no Ace -- the VS Code editor is
# the source editor -- so this would be dead weight.
SKIP_JS = {"mode-plantuml.js"}

# Subtrees of media/ that this script owns end to end, and may therefore delete
# from. Hand-written files live directly in media/ (editorShim.js,
# webviewInit.js) and must survive a sync -- so pruning is confined to these.
SYNCED_SUBDIRS = ("app", "menus", "vendor")

# Third-party libraries the reused code needs at runtime. A webview's CSP
# blocks CDNs, so they ship with the extension. jQuery is pinned to 3.x
# because Bootstrap 4 requires <4.
VENDOR_FILES = {
    "jquery.min.js": "jquery/dist/jquery.min.js",
    "bootstrap.min.js": "bootstrap/dist/js/bootstrap.min.js",
    "bootstrap.min.css": "bootstrap/dist/css/bootstrap.min.css",
    "panzoom.min.js": "panzoom/dist/panzoom.min.js",
    "diff.min.js": "diff/dist/diff.min.js",
}


def collect():
    """Build the full {destination: content} mapping for the mirror.

    Returned rather than written directly so --check can compare without
    touching the working tree.
    """
    files: dict[Path, bytes] = {}

    for source in sorted(STATIC_DIR.glob("*.js")):
        if source.name not in SKIP_JS:
            files[MEDIA_DIR / "app" / source.name] = source.read_bytes()

    files[MEDIA_DIR / "app" / "styles.css"] = (STATIC_DIR / "styles.css").read_bytes()
    for source in sorted((STATIC_DIR / "css").glob("*.css")):
        files[MEDIA_DIR / "app" / "css" / source.name] = source.read_bytes()

    environment = Environment(loader=FileSystemLoader(PARTIALS_DIR), autoescape=False)
    for name in ("activity_menus.html", "sequence_menus.html"):
        rendered = environment.get_template(name).render()
        files[MEDIA_DIR / "menus" / name] = rendered.encode("utf-8")

    for name, relative in VENDOR_FILES.items():
        source = NODE_MODULES / relative
        if not source.is_file():
            raise SystemExit(
                f"Missing {source}. Run `npm install` in {EXTENSION_DIR} first."
            )
        files[MEDIA_DIR / "vendor" / name] = source.read_bytes()

    return files


def owned_files():
    """Every existing file in the subtrees this script owns."""
    for subdir in SYNCED_SUBDIRS:
        for existing in (MEDIA_DIR / subdir).rglob("*"):
            if existing.is_file():
                yield existing


def check(files):
    """Report mirrored files that are missing or out of date."""
    stale = [
        destination
        for destination, content in files.items()
        if not destination.is_file() or destination.read_bytes() != content
    ]

    # A file left behind after its source was renamed would still be loaded by
    # the webview, so treat extras as staleness too.
    expected = set(files)
    stale.extend(existing for existing in owned_files() if existing not in expected)

    return stale


def write(files):
    for destination, content in files.items():
        destination.parent.mkdir(parents=True, exist_ok=True)
        destination.write_bytes(content)

    expected = set(files)
    for existing in list(owned_files()):
        if existing not in expected:
            existing.unlink()

    # Prune directories left empty by the above, deepest first.
    for subdir in SYNCED_SUBDIRS:
        root = MEDIA_DIR / subdir
        for directory in sorted(root.rglob("*"), reverse=True):
            if directory.is_dir() and not any(directory.iterdir()):
                directory.rmdir()


def main(argv=None):
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument(
        "--check",
        action="store_true",
        help="exit non-zero if the mirror is out of date, without writing",
    )
    args = parser.parse_args(argv)

    files = collect()

    if args.check:
        stale = check(files)
        if stale:
            print("media/ is out of date:", file=sys.stderr)
            for destination in sorted(stale):
                print(f"  {destination.relative_to(EXTENSION_DIR)}", file=sys.stderr)
            print("\nRun `npm run sync-assets`.", file=sys.stderr)
            return 1
        print(f"media/ is up to date ({len(files)} files).")
        return 0

    write(files)
    print(f"Synced {len(files)} files into {MEDIA_DIR.relative_to(REPO_ROOT)}.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
