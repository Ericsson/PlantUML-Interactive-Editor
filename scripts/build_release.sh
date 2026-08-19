#!/bin/bash
# Build the extension, backend included
#
# Usage: scripts/build_release.sh [destination] [--force]
#
# A release is one file: the .vsix carries the backend wheel, which the
# extension installs into a virtual environment of its own the first time a
# diagram is opened. Both halves therefore come from this one commit, which is
# what keeps the frontend -- shipped inside the wheel -- in step with the
# extension talking to it.
#
# If destination already contains a published release, publishing aborts unless
# --force is given, so you don't accidentally clobber a colleague's
# not-yet-downloaded release.
set -euo pipefail
shopt -s nullglob

REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DEST=${1:-}
FORCE=0
for arg in "$@"; do
	[[ $arg == --force ]] && FORCE=1
done

cd "$REPO"

# The backend wheel is built straight into the extension, because that is where
# it ships from: plantuml-extension/backend/ is inside the vsix packaged below.
# Cleared first because the extension globs for exactly one wheel, and a version
# bump would otherwise leave the previous one beside it.
rm -rf plantuml-extension/backend
mkdir -p plantuml-extension/backend
uv build --wheel --out-dir plantuml-extension/backend

# The extension -> plantuml-extension/, cleared for the same reason. npm ci
# because the browser libraries are bundled into the vsix, and lint because
# packaging runs no checks of its own. Lint only: `npm test` launches a real
# VS Code and needs a display, which a build host will not have.
cd plantuml-extension
rm -f ./*.vsix
npm ci
npm run lint
npm run package
cd "$REPO"

echo "built:"
ls -1 plantuml-extension/backend/plantuml_gui-*.whl plantuml-extension/plantuml-editor-*.vsix

[[ -n $DEST ]] || { echo "no destination given, not publishing"; exit 0; }

# Only one release may be live: the install instructions glob the version out of
# the filename, so a leftover would make the glob match two files. The wheel is
# matched too, to clear the separately published one that releases up to 0.31
# left there.
old=("$DEST"/plantuml-editor-*.vsix "$DEST"/plantuml_gui-*.whl)
if (( ${#old[@]} )); then
	if (( ! FORCE )); then
		echo "error: $DEST already contains a published release:" >&2
		printf '  %s\n' "${old[@]}" >&2
		echo "rerun with --force to overwrite" >&2
		exit 1
	fi
	rm -f "${old[@]}"
fi

# 664 so a colleague can publish the next release over yours
install -m 664 plantuml-extension/plantuml-editor-*.vsix "$DEST/"

echo "published to $DEST:"
ls -l "$DEST"
