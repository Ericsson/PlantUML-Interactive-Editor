#!/bin/bash
# Build the extension, backend included
#
# Usage: scripts/build_release.sh [destination]
#
# A release is one file: the .vsix carries the backend wheel, which the
# extension installs into a virtual environment of its own the first time a
# diagram is opened. Both halves therefore come from this one commit, which is
# what keeps the frontend -- shipped inside the wheel -- in step with the
# extension talking to it.
#
# If destination already contains a published release, it's moved into
# destination/old/ before the new one is installed.
#
# Every published version is tagged vX.Y.Z, so one version number can never
# name two different builds: publishing refuses when the tag already exists on
# another commit (bump with scripts/bump_version.py first), and otherwise tags
# this commit and pushes the tag to origin.
set -euo pipefail
shopt -s nullglob

REPO=$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)
DEST=${1:-}

cd "$REPO"

# Also checks that every version file agrees, before anything is built.
VERSION=$(python3 -c 'import sys; sys.path.insert(0, "scripts"); from check_app_versions import check_app_versions; print(check_app_versions())')
TAG="v$VERSION"

if [[ -n $DEST ]]; then
	git diff --quiet HEAD || { echo "uncommitted changes: a release must be built from a commit, so its tag names what shipped" >&2; exit 1; }
	git fetch --quiet --tags origin
fi
if tagged=$(git rev-parse -q --verify "refs/tags/$TAG^{commit}"); then
	if [[ $tagged != $(git rev-parse HEAD) ]]; then
		echo "$VERSION was already released from ${tagged:0:7}; bump the version (scripts/bump_version.py) before releasing again" >&2
		exit 1
	fi
fi

archive_old() {
	local dest=$1
	shift
	local files=("$@")
	(( ${#files[@]} )) || return 0
	mkdir -p "$dest/old"
	mv -f "${files[@]}" "$dest/old/"
}

# The backend wheel is built straight into the extension, because that is where
# it ships from: plantuml-extension/backend/ is inside the vsix packaged below.
# Cleared first because the extension globs for exactly one wheel, and a version
# bump would otherwise leave the previous one beside it. This is a build
# intermediate, not a release artefact, so it's discarded rather than archived.
rm -rf plantuml-extension/backend
mkdir -p plantuml-extension/backend
uv build --wheel --out-dir plantuml-extension/backend

# The extension -> plantuml-extension/, cleared the same way. npm ci because
# the browser libraries are bundled into the vsix, and lint because packaging
# runs no checks of its own. Lint only: `npm test` launches a real VS Code and
# needs a display, which a build host will not have.
cd plantuml-extension
old_vsix=(./*.vsix)
archive_old . "${old_vsix[@]}"
npm ci
npm run lint
npm run package
cd "$REPO"

echo "built:"
ls -1 plantuml-extension/backend/plantuml_gui-*.whl plantuml-extension/plantuml-editor-*.vsix

[[ -n $DEST ]] || { echo "no destination given, not publishing"; exit 0; }

# Only one release may be live: the install instructions glob the version out of
# the filename, so a leftover would make the glob match two files. The wheel is
# matched too, to archive the separately published one that releases up to
# 0.31 left there.
old=("$DEST"/plantuml-editor-*.vsix "$DEST"/plantuml_gui-*.whl)
archive_old "$DEST" "${old[@]}"

# 664 so a colleague can publish the next release over yours
install -m 664 plantuml-extension/plantuml-editor-*.vsix "$DEST/"

echo "published to $DEST:"
ls -l "$DEST"

# Tag after publishing, so a failed publish leaves no tag behind. Already
# tagged when republishing the same commit.
if ! git rev-parse -q --verify "refs/tags/$TAG" >/dev/null; then
	git tag -a "$TAG" -m "Release $VERSION"
	git push --quiet origin "$TAG"
	echo "tagged $TAG"
fi
