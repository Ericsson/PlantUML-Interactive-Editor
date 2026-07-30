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
// setting's own default value is a known shared install path, used
// out-of-the-box on networks where it's provisioned.

const { spawn } = require('child_process');
const fs = require('fs');
const vscode = require('vscode');

/** Thrown when PlantUML cannot be invoked or configured correctly. */
class PlantUmlConfigError extends Error {}

/** Thrown when PlantUML runs but reports a failure (non-zero exit / stderr). */
class PlantUmlRenderError extends Error {}

// Known shared install path for plantuml.jar. Used as a last-resort default
// when neither the setting nor the environment variable is configured, so
// users on networks where this path is provisioned get a working jar path
// out of the box. Only used if it actually exists on disk, since this
// extension may also run in environments without it.
const SHARED_DEFAULT_JAR_PATH =
	'/app/vbuild/tools/plantuml/1.2022.5/lib/plantuml.1.2022.5.jar';

/**
 * Resolve the configured path to plantuml.jar.
 *
 * Looks up the `plantumlInteractive.plantumlJar` setting first, falling
 * back to the PLANTUML_JAR environment variable (the same variable name
 * used by the existing Flask app) for convenience. The setting's own
 * schema default is the known shared install path, so most users get a
 * working jar path out of the box without configuring anything. Because
 * that value comes from the schema rather than something the user typed,
 * it does not take precedence over the environment variable, and if it
 * doesn't exist on disk (e.g. outside the network where it's provisioned)
 * it's treated the same as nothing being configured, rather than
 * surfacing a "jar not found" error for a path the user never chose.
 * Throws PlantUmlConfigError with an actionable message if nothing is
 * configured (or only the unusable shared default is in effect) or the
 * configured path does not exist on disk.
 *
 * @returns {string} Absolute path to plantuml.jar
 */
function resolvePlantUmlJarPath() {
	const configured = vscode.workspace
		.getConfiguration('plantumlInteractive')
		.get('plantumlJar');

	// `configured` is the schema default (the shared path) whenever the
	// user hasn't set the setting themselves, so it must not out-rank the
	// environment variable the way an explicit user setting would.
	const isSchemaDefault = configured === SHARED_DEFAULT_JAR_PATH;

	let jarPath = (!isSchemaDefault && configured) || process.env.PLANTUML_JAR;

	if (!jarPath && isSchemaDefault) {
		if (fs.existsSync(SHARED_DEFAULT_JAR_PATH)) {
			jarPath = SHARED_DEFAULT_JAR_PATH;
		}
		// If it doesn't exist here, leave jarPath unset so we fall through
		// to the "not configured" error below instead of a "not found"
		// error that would be confusing on machines outside the network
		// where this path is provisioned.
	}

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
			child = spawn('java', [
				'-DPLANTUML_LIMIT_SIZE=16384',
				'-jar',
				jarPath,
				'-pipe',
				'-tsvg'
			]);
		} catch (err) {
			reject(
				new PlantUmlConfigError(
					`Failed to launch Java to run PlantUML: ${err.message}. Ensure Java is ` +
						'installed and available on your PATH.'
				)
			);
			return;
		}

		const stdoutChunks = [];
		const stderrChunks = [];

		child.on('error', (err) => {
			reject(
				new PlantUmlConfigError(
					`Failed to launch Java to run PlantUML: ${err.message}. Ensure Java is ` +
						'installed and available on your PATH.'
				)
			);
		});

		child.stdout.on('data', (chunk) => stdoutChunks.push(chunk));
		child.stderr.on('data', (chunk) => stderrChunks.push(chunk));

		child.on('close', (code) => {
			const stdout = Buffer.concat(stdoutChunks).toString('utf-8');
			const stderr = Buffer.concat(stderrChunks).toString('utf-8');

			if (code !== 0) {
				reject(
					new PlantUmlRenderError(
						`PlantUML exited with code ${code}.${stderr ? ` ${stderr.trim()}` : ''}`
					)
				);
				return;
			}

			if (!stdout || !stdout.trim()) {
				reject(
					new PlantUmlRenderError(
						`PlantUML produced no output.${stderr ? ` ${stderr.trim()}` : ''}`
					)
				);
				return;
			}

			resolve(stdout);
		});

		child.stdin.on('error', () => {
			// Ignore EPIPE-style write errors; a non-zero exit or empty
			// stdout is handled above and surfaces a clearer message.
		});
		child.stdin.write(plantUmlSource, 'utf-8');
		child.stdin.end();
	});
}

module.exports = {
	renderPlantUmlToSvg,
	resolvePlantUmlJarPath,
	PlantUmlConfigError,
	PlantUmlRenderError,
	SHARED_DEFAULT_JAR_PATH
};
