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
// The setting's default value in package.json is a known shared install path,
// so the jar resolves out of the box on networks where it is provisioned.

const fs = require('fs');
const vscode = require('vscode');

/** Thrown when the PlantUML jar is not configured or not on disk. */
class PlantUmlConfigError extends Error {}

/**
 * Resolve the configured path to plantuml.jar.
 *
 * Looks up the `plantumlInteractive.plantumlJar` setting first, falling back
 * to the PLANTUML_JAR environment variable (the same variable name the Flask
 * app uses) for convenience. Note that `get()` returns the package.json
 * default when the setting is untouched, so the env var is only reached once
 * the setting has been explicitly cleared.
 *
 * @returns {string} Absolute path to plantuml.jar
 * @throws {PlantUmlConfigError} if nothing is configured or the path is absent
 */
function resolvePlantUmlJarPath() {
	const configured = vscode.workspace
		.getConfiguration('plantumlInteractive')
		.get('plantumlJar');

	const jarPath = configured || process.env.PLANTUML_JAR;

	if (!jarPath) {
		throw new PlantUmlConfigError(
			'PlantUML jar path is not configured. Set "plantumlInteractive.plantumlJar" ' +
				'in your VS Code settings (or the PLANTUML_JAR environment variable) to the ' +
				'path of plantuml.jar.'
		);
	}

	if (!fs.existsSync(jarPath)) {
		throw new PlantUmlConfigError(
			`Configured PlantUML jar was not found at "${jarPath}". Check the ` +
				'"plantumlInteractive.plantumlJar" setting.'
		);
	}

	return /** @type {string} */ (jarPath);
}

module.exports = {
	resolvePlantUmlJarPath,
	PlantUmlConfigError
};
