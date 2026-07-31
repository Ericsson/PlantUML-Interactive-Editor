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

// PlantUML -> SVG rendering, isolated from VS Code extension lifecycle code.
//
// Mirrors the invocation used by the existing PlantUML-Interactive-Editor
// Flask app (src/plantuml_gui/shared/render.py, `_create_svg_from_uml`):
// it shells out to `java -jar <plantuml.jar> -pipe -tsvg`, feeding the
// PlantUML source on stdin and reading the rendered SVG from stdout.
// That Python helper resolves the jar path from a PLANTUML_JAR environment
// variable (loaded from a .env file via python-dotenv), which is specific
// to the Flask app's process and not reusable from a VS Code extension.
// Here the jar path instead comes from the `plantumlInteractive.plantumlJar`
// VS Code setting (falling back to a PLANTUML_JAR environment variable for
// convenience), keeping the same underlying rendering mechanism. The
// setting's own default value in package.json is a known shared install
// path, used out-of-the-box on networks where it's provisioned.

const { spawn } = require('child_process');
const fs = require('fs');
const vscode = require('vscode');

/** Thrown when PlantUML cannot be invoked or configured correctly. */
class PlantUmlConfigError extends Error {}

/** Thrown when PlantUML runs but reports a failure (non-zero exit / stderr). */
class PlantUmlRenderError extends Error {}

/**
 * Resolve the configured path to plantuml.jar.
 *
 * Looks up the `plantumlInteractive.plantumlJar` setting first, falling
 * back to the PLANTUML_JAR environment variable (the same variable name
 * used by the existing Flask app) for convenience. The setting's own
 * default value, declared in package.json, is a known shared install path,
 * so most users get a working jar path out of the box without configuring
 * anything. Throws PlantUmlConfigError with an actionable message if
 * nothing is configured or the configured path does not exist on disk.
 *
 * @returns {string} Absolute path to plantuml.jar
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

	return jarPath;
}

/**
 * Render PlantUML source to an SVG string by invoking PlantUML via Java,
 * the same way the existing Flask app's _create_svg_from_uml does.
 *
 * @param {string} plantUmlSource
 * @returns {Promise<string>} the rendered SVG markup
 * @throws {PlantUmlConfigError} if PlantUML/Java cannot be located or run
 * @throws {PlantUmlRenderError} if PlantUML runs but fails to render
 */
function renderPlantUmlToSvg(plantUmlSource) {
	return new Promise((resolve, reject) => {
		let jarPath;
		try {
			jarPath = resolvePlantUmlJarPath();
		} catch (err) {
			reject(err);
			return;
		}

		let child;
		try {
			// Launch PlantUML via Java:
			//   -DPLANTUML_LIMIT_SIZE=16384  raise PlantUML's internal max image size
			//   -jar jarPath                 the plantuml.jar resolved above
			//   -pipe                        read source from stdin, write result to stdout
			//                                 (no temp files touched on disk)
			//   -tsvg                        render output as SVG
			child = spawn('java', [
				'-DPLANTUML_LIMIT_SIZE=16384',
				'-jar',
				jarPath,
				'-pipe',
				'-tsvg'
			]);
		} catch (err) {
			// Synchronous throw from spawn() itself (rare - e.g. invalid
			// arguments). Async failures like "java not found" surface via
			// the 'error' event below instead.
			reject(
				new PlantUmlConfigError(
					`Failed to launch Java to run PlantUML: ${err.message}. Ensure Java is ` +
						'installed and available on your PATH.'
				)
			);
			return;
		}

		// Buffer raw output chunks instead of building strings incrementally,
		// since the SVG/error text is only meaningful once the process has
		// fully finished (see the 'close' handler below).
		const stdoutChunks = [];
		const stderrChunks = [];

		// Fires if the process could not be spawned/run at all (e.g. the
		// `java` binary is missing from PATH). Distinct from a non-zero
		// exit code, which means Java *did* run but PlantUML itself failed.
		child.on('error', (err) => {
			reject(
				new PlantUmlConfigError(
					`Failed to launch Java to run PlantUML: ${err.message}. Ensure Java is ` +
						'installed and available on your PATH.'
				)
			);
		});

		// Accumulate stdout (the rendered SVG) and stderr (any PlantUML
		// error/warning text) as they arrive.
		child.stdout.on('data', (chunk) => stdoutChunks.push(chunk));
		child.stderr.on('data', (chunk) => stderrChunks.push(chunk));

		// 'close' fires once the process has exited AND all of its stdio
		// streams have been fully drained - unlike 'exit', which can fire
		// before the last 'data' events arrive. Using 'close' guarantees
		// stdoutChunks/stderrChunks are complete before we read them.
		child.on('close', (code) => {
			const stdout = Buffer.concat(stdoutChunks).toString('utf-8');
			const stderr = Buffer.concat(stderrChunks).toString('utf-8');

			// Non-zero exit code: PlantUML ran but reported failure
			// (e.g. syntax error in the source). Surface stderr if present.
			if (code !== 0) {
				reject(
					new PlantUmlRenderError(
						`PlantUML exited with code ${code}.${stderr ? ` ${stderr.trim()}` : ''}`
					)
				);
				return;
			}

			// Exit code 0 but nothing on stdout: treat as a failure too,
			// since a successful render should always produce SVG markup.
			if (!stdout || !stdout.trim()) {
				reject(
					new PlantUmlRenderError(
						`PlantUML produced no output.${stderr ? ` ${stderr.trim()}` : ''}`
					)
				);
				return;
			}

			// Success: stdout contains the rendered SVG markup.
			resolve(stdout);
		});

		child.stdin.on('error', () => {
			// Ignore EPIPE-style write errors; a non-zero exit or empty
			// stdout is handled above and surfaces a clearer message.
		});

		// Feed the PlantUML source in on stdin, then close it so the
		// process knows input is complete and can start/finish rendering.
		child.stdin.write(plantUmlSource, 'utf-8');
		child.stdin.end();
	});
}

module.exports = {
	renderPlantUmlToSvg,
	resolvePlantUmlJarPath,
	PlantUmlConfigError,
	PlantUmlRenderError
};
