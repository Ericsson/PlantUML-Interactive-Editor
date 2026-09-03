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

// Where the PlantUML jar comes from.
//
// The jar is run by the backend (src/plantuml_gui/shared/render.py, which reads
// PLANTUML_JAR per call), not here. This side resolves the path so it can be
// checked before Python is spawned and handed down as PLANTUML_GUI_JAR_OVERRIDE.
// The check matters because serve.py's check_jar only warns on stderr, so an
// unchecked bad path first shows up as a 500 on the user's first render.
//
// Three sources, most explicit first: the setting, then PLANTUML_JAR, then the
// shared install path provisioned inside Ericsson.
//
// A source that is set but unusable stops resolution rather than falling
// through to the next one. Falling through is how config comes to look
// ignored: the user fixes the setting, mistypes it, and the extension renders
// from a jar they did not choose.

const vscode = require('vscode');
const { SECTION, normalizePath, isFile } = require('./settings');

/** Key within SECTION, and the id the user sees in Settings. */
const JAR_KEY = 'plantumlJar';
const JAR_SETTING = `${SECTION}.${JAR_KEY}`;

/**
 * The environment variable that stands in for the setting.
 *
 * The same name the Flask app reads, so a repo .env already configures the
 * extension.
 */
const JAR_ENV = 'PLANTUML_JAR';

/**
 * The provisioned install used inside Ericsson.
 *
 * Here rather than as the setting's manifest default so that it stays a last
 * resort: `get()` returns the manifest default whenever a setting is untouched,
 * which is what used to put this path ahead of PLANTUML_JAR for every user who
 * never opened Settings.
 */
const SHARED_JAR_PATH =
	'/app/vbuild/tools/plantuml/1.2022.5/lib/plantuml.1.2022.5.jar';

/** Thrown when the PlantUML jar is not configured or not on disk. */
class PlantUmlConfigError extends Error {}

/**
 * Resolve the configured path to plantuml.jar.
 *
 * @returns {string} Absolute path to plantuml.jar
 * @throws {PlantUmlConfigError} if nothing is configured, or if what is
 *   configured is not a file
 */
function resolvePlantUmlJarPath() {
	const configured = normalizePath(
		vscode.workspace.getConfiguration(SECTION).get(JAR_KEY)
	);

	if (configured) {
		return requireFile(configured, `the "${JAR_SETTING}" setting`);
	}

	const fromEnv = normalizePath(process.env[JAR_ENV]);

	if (fromEnv) {
		return requireFile(fromEnv, `the ${JAR_ENV} environment variable`);
	}

	if (isFile(SHARED_JAR_PATH)) {
		return SHARED_JAR_PATH;
	}

	throw new PlantUmlConfigError(
		'PlantUML jar path is not configured, and the shared install at ' +
			`"${SHARED_JAR_PATH}" is not available on this machine. Set ` +
			`"${JAR_SETTING}" in your VS Code settings (or the ` +
			`${JAR_ENV} environment variable) to the path of plantuml.jar.`
	);
}

/**
 * Return `candidate` if it is a file, otherwise say which knob produced it.
 *
 * Naming the source is the whole point: the same bad path means "fix your
 * settings" or "fix your .env" depending on where it came from, and the user
 * cannot tell those apart from the path alone.
 *
 * @param {string} candidate
 * @param {string} source human-readable description of where it came from
 * @returns {string}
 * @throws {PlantUmlConfigError}
 */
function requireFile(candidate, source) {
	if (!isFile(candidate)) {
		throw new PlantUmlConfigError(
			`The PlantUML jar configured in ${source} is not a file: "${candidate}". ` +
				`Check ${source}.`
		);
	}

	return candidate;
}

module.exports = {
	resolvePlantUmlJarPath,
	PlantUmlConfigError,
	JAR_KEY,
	JAR_SETTING,
	JAR_ENV,
	SHARED_JAR_PATH
};
