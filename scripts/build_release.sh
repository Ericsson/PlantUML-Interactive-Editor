#!/bin/bash
# Build the extension and its backend
#
# Usage: scripts/build_release.sh [destination] [--force]
#
# Both artefacts must come from the same commit: the frontend ships inside the
# wheel, so a mismatched pair means an old UI.
#
# If destination already contains a published wheel/vsix pair, publishing
# aborts unless --force is given, so you don't accidentally clobber a
# colleague's not-yet-downloaded release.
set -euo pipefail
shopt -s nullglob

REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DEST=${1:-}
FORCE=0
for arg in "$@"; do
	[[ $arg == --force ]] && FORCE=1
done

cd "$REPO"

# The Python backend -> dist/, and a copy into plantuml-extension/backend/,
# which is inside the vsix packaged below: the extension installs that copy
# into a venv of its own on first use, so the vsix is the whole install.
#
# Both directories are cleared first because everything downstream globs for
# exactly one wheel -- the publish step here, and the extension's lookup of the
# wheel it ships -- and a version bump would otherwise leave two behind.
rm -f dist/*.whl
uv build --wheel

rm -rf plantuml-extension/backend
mkdir -p plantuml-extension/backend
install -m 644 dist/plantuml_gui-*.whl plantuml-extension/backend/

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
ls -1 dist/plantuml_gui-*.whl plantuml-extension/plantuml-editor-*.vsix

[[ -n $DEST ]] || { echo "no destination given, not publishing"; exit 0; }

# Only one pair may be live: the install instructions glob the version out of
# the filenames, so a leftover would make the glob match two files
old=("$DEST"/plantuml_gui-*.whl "$DEST"/plantuml-editor-*.vsix)
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
install -m 664 dist/plantuml_gui-*.whl "$DEST/"
install -m 664 plantuml-extension/plantuml-editor-*.vsix "$DEST/"

echo "published to $DEST:"
ls -l "$DEST"
