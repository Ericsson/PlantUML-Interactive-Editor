// SPDX-License-Identifier: MIT

// MIT License

// Copyright (c) 2026 Ericsson

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

// The configuration section, and how configured paths are treated.
//
// Only what more than one file needs. Each setting's own vocabulary -- its key,
// its dotted id, its environment variable, its fallback -- lives with the code
// that resolves it, in plantumlJar.js and sidecar.js, so that reading either
// one tells the whole story of where that value comes from without a detour
// through here.
//
// The section is shared because three files need it: the two resolvers, and
// extension.js to open the Settings UI filtered to it. The two functions are
// shared because they are rules that have to agree -- what counts as a
// pasteable path, and what counts as a usable file -- and the alternative is
// the same twenty lines copied into both resolvers, where one copy can be
// changed without the other.
//
// Requires nothing from vscode, which is what makes it testable in plain Node.

const fs = require('fs');

/** The configuration section every setting lives under. */
const SECTION = 'plantumlInteractive';

/** Quote characters a shell would strip and users expect to be able to paste. */
const QUOTES = ['"', "'"];

/**
 * Clean up a path a human typed or pasted.
 *
 * Copying a path out of a terminal or a chat message brings surrounding
 * whitespace and quotes with it, and neither survives being handed to
 * `spawn()` or `statSync()` -- the failure is a not-found error naming a path
 * that looks correct on screen. Stripping them is not guesswork: no real path
 * is improved by a trailing space or by starting *and* ending with the same
 * quote.
 *
 * Only one matching pair is removed, and only when both ends agree, so a lone
 * quote is left in place to fail loudly rather than being silently reinterpreted.
 * Quotes inside the path are untouched. `~` and `${...}` are literal: VS Code
 * does not expand them in values read with `get()`.
 *
 * @param {unknown} value
 * @returns {string} the cleaned path, or '' for anything unusable
 */
function normalizePath(value) {
	if (typeof value !== 'string') {
		return '';
	}

	const trimmed = value.trim();

	const quote = QUOTES.find(
		(candidate) =>
			trimmed.length >= 2 &&
			trimmed.startsWith(candidate) &&
			trimmed.endsWith(candidate)
	);

	// Trim again: the quotes may have been wrapped around a padded path.
	return quote ? trimmed.slice(1, -1).trim() : trimmed;
}

/**
 * Whether `candidate` is a file that exists.
 *
 * A file rather than merely something that exists, because a directory called
 * plantuml.jar passes an existence check and then fails inside java, far from
 * the setting that caused it. Matches `check_jar` in serve.py, which uses
 * os.path.isfile.
 *
 * @param {string} candidate
 * @returns {boolean}
 */
function isFile(candidate) {
	try {
		return fs.statSync(candidate).isFile();
	} catch {
		// Missing, unreadable, or a broken symlink: all "not a usable file".
		return false;
	}
}

module.exports = {
	SECTION,
	normalizePath,
	isFile
};
