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

// The names and shapes of everything the user can configure.
//
// One module so that a setting id exists in exactly two places: here and
// package.json. Before this, ids were string literals in four files, three of
// which only used them to name the setting in an error message -- the kind of
// duplication that survives a rename and leaves the user reading advice about
// a setting that no longer exists.
//
// What this module deliberately does *not* own is the resolution policy: which
// source wins, and what happens when the winner is unusable. That lives with
// the callers, plantumlJar.js and sidecar.js, because each owns its own error
// type and its own notion of a usable value. This is values and predicates.

const fs = require('fs');
const vscode = require('vscode');

/** The configuration section every setting lives under. */
const SECTION = 'plantumlInteractive';

/** Keys within SECTION, as passed to `WorkspaceConfiguration.get`. */
const JAR_KEY = 'plantumlJar';
const PYTHON_KEY = 'pythonPath';

/** Fully qualified ids, as shown to the user and typed into the Settings UI. */
const JAR_SETTING = `${SECTION}.${JAR_KEY}`;
const PYTHON_SETTING = `${SECTION}.${PYTHON_KEY}`;

/**
 * Environment variables that stand in for the settings.
 *
 * PLANTUML_JAR is the same name the Flask app reads, so a repo .env already
 * configures the extension. PLANTUML_GUI_PYTHON exists because the Extension
 * Development Host launches without a workspace folder, where workspace
 * settings are not read at all; see plantuml-extension/README.md.
 */
const JAR_ENV = 'PLANTUML_JAR';
const PYTHON_ENV = 'PLANTUML_GUI_PYTHON';

/**
 * The provisioned install used inside Ericsson, tried when nothing is
 * configured.
 *
 * This was the `plantumlJar` default in package.json, which made it win over
 * PLANTUML_JAR for every user who never opened Settings -- `get()` returns the
 * manifest default, so the env var was unreachable. Keeping the path in code
 * lets it be what it was meant to be: a last resort.
 */
const SHARED_JAR_PATH =
	'/app/vbuild/tools/plantuml/1.2022.5/lib/plantuml.1.2022.5.jar';

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
 * Quotes inside the path are untouched.
 *
 * Intentionally does not expand `~`, `${workspaceFolder}` or `${env:...}`:
 * those look like features the setting supports everywhere once they work
 * anywhere, and VS Code does not expand them in values read with `get()`.
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
 * Read one of this extension's settings, normalized.
 *
 * @param {string} key one of JAR_KEY, PYTHON_KEY
 * @returns {string} the configured value, or '' when unset
 */
function readSetting(key) {
	return normalizePath(vscode.workspace.getConfiguration(SECTION).get(key));
}

/**
 * Read an environment variable as a path, normalized.
 *
 * @param {string} name one of JAR_ENV, PYTHON_ENV
 * @returns {string} the value, or '' when unset
 */
function readEnv(name) {
	return normalizePath(process.env[name]);
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
	JAR_KEY,
	PYTHON_KEY,
	JAR_SETTING,
	PYTHON_SETTING,
	JAR_ENV,
	PYTHON_ENV,
	SHARED_JAR_PATH,
	normalizePath,
	readSetting,
	readEnv,
	isFile
};
