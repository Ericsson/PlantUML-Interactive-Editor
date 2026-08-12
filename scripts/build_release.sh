#!/bin/bash
# Build the extension and its backend
#
# Usage: scripts/build_release.sh [destination]
#
# Both artefacts must come from the same commit: the frontend ships inside the
# wheel, so a mismatched pair means an old UI.
set -euo pipefail
shopt -s nullglob

REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DEST=${1:-}

cd "$REPO"

# The Python backend -> dist/. Old wheels are cleared first because the publish
# step below globs for one file, and a version bump would otherwise leave two
# in dist/ and publish both.
rm -f dist/*.whl
uv build --wheel

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
	rm -f "${old[@]}"
fi

# 664 so a colleague can publish the next release over yours
install -m 664 dist/plantuml_gui-*.whl "$DEST/"
install -m 664 plantuml-extension/plantuml-editor-*.vsix "$DEST/"

echo "published to $DEST:"
ls -l "$DEST"
