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

// Lifecycle for the Python sidecar: the existing Flask app, run as a child
// process on an ephemeral loopback port.
//
// The ~71 routes that rewrite PlantUML source live in Python
// (src/plantuml_gui/), and reimplementing them in JavaScript would fork ~4,500
// lines plus their test suite. Instead the extension spawns
// `python -m plantuml_gui.serve` (see src/plantuml_gui/serve.py) and the
// webview POSTs to it directly, so the web app's frontend code can be reused
// with only its relative URLs rewritten.

const { spawn } = require('child_process');
const crypto = require('crypto');
const vscode = require('vscode');
const { SECTION, normalizePath, isFile } = require('./settings');

/** Key within SECTION, and the id the user sees in Settings. */
const PYTHON_KEY = 'pythonPath';
const PYTHON_SETTING = `${SECTION}.${PYTHON_KEY}`;

/**
 * The environment variable that stands in for the setting.
 *
 * It exists because the Extension Development Host launches without a workspace
 * folder, where workspace settings are not read at all; see
 * plantuml-extension/README.md.
 */
const PYTHON_ENV = 'PLANTUML_GUI_PYTHON';

// Must match PORT_LINE_PREFIX in src/plantuml_gui/serve.py.
const PORT_LINE_PREFIX = 'PLANTUML_GUI_PORT=';

// Must match TOKEN_HEADER in src/plantuml_gui/serve.py, which answers 403 to
// anything else. Exported so every caller names the header from one place.
const TOKEN_HEADER = 'X-PlantUML-Token';

// The sidecar has to boot Python, import Flask, and bind a socket. Slow on a
// cold filesystem or with an antivirus scanning the interpreter.
const STARTUP_TIMEOUT_MS = 30000;

const HEALTH_TIMEOUT_MS = 2000;

/** Thrown when the sidecar cannot be started or does not become ready. */
class SidecarStartError extends Error {}

/**
 * Thrown when the interpreter is missing or unusable, before anything is spawned.
 *
 * A subclass rather than a flag so `extension.js` can tell the one failure the
 * user fixes in Settings apart from a spawn crash or a health timeout, while
 * callers that only know the base class keep catching it.
 */
class PythonConfigError extends SidecarStartError {}

/**
 * A running sidecar: the child process plus the address and token needed to
 * talk to it.
 */
class Sidecar {
	/**
	 * @param {import('child_process').ChildProcess} process
	 * @param {number} port
	 * @param {string} token
	 */
	constructor(process, port, token) {
		this.process = process;
		this.port = port;
		this.token = token;
		this.baseUrl = `http://127.0.0.1:${port}/`;
	}

	/** @returns {boolean} whether the child is still running. */
	get isRunning() {
		return this.process.exitCode === null && this.process.signalCode === null;
	}

	dispose() {
		if (this.isRunning) {
			this.process.kill();
		}
	}
}

/**
 * Resolve the Python interpreter to run the sidecar with.
 *
 * Two explicit sources only, most explicit first. Nothing is guessed: the
 * backend is a Python package that no machine has by default, so an
 * interpreter found by searching is one that almost certainly cannot import
 * plantuml_gui, and spawning it would report the failure against the wrong
 * thing. Failing here names the knob to turn instead.
 *
 * The path is checked here so that a mistake is reported against the knob that
 * caused it, rather than as an ENOENT off the child's error event once a
 * process has been launched and a panel is waiting on it.
 *
 * See plantuml-extension/README.md for which knob to use when.
 *
 * @returns {Promise<string>} an interpreter path.
 * @throws {PythonConfigError} when no interpreter is configured, or the
 *   configured one is not a file
 */
async function resolvePythonPath() {
	const configured = normalizePath(
		vscode.workspace.getConfiguration(SECTION).get(PYTHON_KEY)
	);

	// An explicit setting wins even if it is wrong: a clear "could not run X"
	// beats silently running some other interpreter than the one asked for.
	if (configured) {
		return requireInterpreter(configured, `the "${PYTHON_SETTING}" setting`);
	}

	const fromEnv = normalizePath(process.env[PYTHON_ENV]);

	if (fromEnv) {
		return requireInterpreter(fromEnv, `the ${PYTHON_ENV} environment variable`);
	}

	throw new PythonConfigError(
		'No Python interpreter is configured for the PlantUML backend. Set ' +
			`"${PYTHON_SETTING}" to an interpreter that has the ` +
			`plantuml-gui package installed, or set ${PYTHON_ENV}.`
	);
}

/**
 * Return `candidate` if it is a file, otherwise say which knob produced it.
 *
 * @param {string} candidate
 * @param {string} source human-readable description of where it came from
 * @returns {string}
 * @throws {PythonConfigError}
 */
function requireInterpreter(candidate, source) {
	if (!isFile(candidate)) {
		throw new PythonConfigError(
			`The Python interpreter configured in ${source} is not a file: ` +
				`"${candidate}". Check ${source}.`
		);
	}

	return candidate;
}

/**
 * Build the environment for the child process.
 *
 * The jar is passed as PLANTUML_GUI_JAR_OVERRIDE rather than PLANTUML_JAR
 * because shared/render.py calls load_dotenv(override=True) at import time, so
 * a repo-root .env would otherwise beat anything we set here. serve.py applies
 * the override after that import. See apply_jar_override there.
 *
 * @param {string} token
 * @param {string|undefined} jarPath
 * @returns {NodeJS.ProcessEnv}
 */
function buildEnv(token, jarPath) {
	const env = { ...process.env, PLANTUML_GUI_TOKEN: token };

	if (jarPath) {
		env.PLANTUML_GUI_JAR_OVERRIDE = jarPath;
	}

	// Unbuffered, so the port line reaches us as soon as it is printed rather
	// than sitting in Python's block buffer (stdout is a pipe, not a tty).
	env.PYTHONUNBUFFERED = '1';

	return env;
}

/**
 * Turn a failure to spawn or boot into a message that says what to install.
 *
 * @param {string} pythonPath
 * @param {string} stderr
 * @param {Error|undefined} spawnError
 * @returns {string}
 */
function describeStartFailure(pythonPath, stderr, spawnError) {
	if (spawnError && spawnError.code === 'ENOENT') {
		// resolvePythonPath already checked the path is a file, so reaching here
		// means it stopped being runnable in between, or is not executable.
		return (
			`Could not run Python at "${pythonPath}". Check that it is an ` +
			`executable interpreter, and that "${PYTHON_SETTING}" (or ` +
			`${PYTHON_ENV}) points at it.`
		);
	}

	if (/No module named ['"]?plantuml_gui/.test(stderr)) {
		return (
			`Python at "${pythonPath}" does not have the plantuml-gui package. ` +
			'Install it into that interpreter, e.g. "pip install -e ." from the ' +
			'repository root.'
		);
	}

	const detail = stderr.trim();
	return (
		'The PlantUML backend failed to start.' + (detail ? `\n\n${detail}` : '')
	);
}

/**
 * Wait until the sidecar answers /health, so callers never send a real request
 * to a socket that is bound but not yet serving.
 *
 * @param {Sidecar} sidecar
 * @param {number} deadline epoch ms after which to give up
 */
async function waitForHealthy(sidecar, deadline) {
	let lastError;

	while (Date.now() < deadline) {
		if (!sidecar.isRunning) {
			throw new SidecarStartError('The PlantUML backend exited during startup.');
		}

		try {
			const response = await fetch(`${sidecar.baseUrl}health`, {
				headers: { [TOKEN_HEADER]: sidecar.token },
				signal: AbortSignal.timeout(HEALTH_TIMEOUT_MS)
			});
			if (response.ok) {
				return;
			}
			lastError = new Error(`/health returned ${response.status}`);
		} catch (err) {
			lastError = err;
		}

		await new Promise((resolve) => setTimeout(resolve, 100));
	}

	throw new SidecarStartError(
		`The PlantUML backend did not become ready within ${STARTUP_TIMEOUT_MS}ms.` +
			(lastError ? ` Last error: ${lastError.message}` : '')
	);
}

/**
 * Start the sidecar and wait until it is serving.
 *
 * @param {object} [options]
 * @param {string} [options.jarPath] absolute path to plantuml.jar
 * @param {import('vscode').OutputChannel} [options.output] receives sidecar stderr, so
 *   Python tracebacks are visible instead of being swallowed
 * @returns {Promise<Sidecar>}
 * @throws {SidecarStartError}
 */
async function startSidecar(options = {}) {
	const { jarPath, output } = options;
	const pythonPath = await resolvePythonPath();
	output?.appendLine(`Starting PlantUML backend with interpreter: ${pythonPath}`);
	// Per-launch secret: this is an HTTP server on loopback, which any local
	// process can reach, and every route rewrites the user's source.
	const token = crypto.randomBytes(24).toString('hex');

	const child = spawn(pythonPath, ['-m', 'plantuml_gui.serve'], {
		env: buildEnv(token, jarPath)
	});

	let stderr = '';
	child.stderr.setEncoding('utf-8');
	child.stderr.on('data', (chunk) => {
		// Cap what we retain: werkzeug logs every request here for the life of
		// the process, so this would otherwise grow without bound.
		stderr = (stderr + chunk).slice(-8000);
		if (output) {
			output.append(chunk);
		}
	});

	const port = await readPortLine(child, pythonPath, () => stderr);
	const sidecar = new Sidecar(child, port, token);

	try {
		await waitForHealthy(sidecar, Date.now() + STARTUP_TIMEOUT_MS);
	} catch (err) {
		// The child bound a port but never answered. Kill it here: no caller
		// receives a handle to it, so this is the last chance to stop it holding
		// that port for the life of the editor.
		sidecar.dispose();
		throw err;
	}

	return sidecar;
}

/**
 * Read the port the sidecar bound to off its stdout.
 *
 * Scans for the prefix rather than reading the first line: anything printed
 * during import would otherwise be mistaken for the port line.
 *
 * @param {import('child_process').ChildProcess} child
 * @param {string} pythonPath
 * @param {() => string} getStderr
 * @returns {Promise<number>}
 */
function readPortLine(child, pythonPath, getStderr) {
	return new Promise((resolve, reject) => {
		let buffered = '';
		let settled = false;

		const finish = (fn, arg) => {
			if (settled) return;
			settled = true;
			clearTimeout(timer);
			fn(arg);
		};

		const timer = setTimeout(() => {
			child.kill();
			finish(
				reject,
				new SidecarStartError(
					`The PlantUML backend did not report a port within ${STARTUP_TIMEOUT_MS}ms.`
				)
			);
		}, STARTUP_TIMEOUT_MS);

		child.stdout.setEncoding('utf-8');
		child.stdout.on('data', (chunk) => {
			buffered += chunk;

			// Only complete lines: a chunk boundary can fall mid-number.
			const lines = buffered.split('\n');
			buffered = lines.pop() ?? '';

			for (const line of lines) {
				if (line.startsWith(PORT_LINE_PREFIX)) {
					const port = Number.parseInt(line.slice(PORT_LINE_PREFIX.length), 10);
					if (Number.isInteger(port) && port > 0) {
						finish(resolve, port);
						return;
					}
				}
			}
		});

		child.on('error', (err) => {
			finish(
				reject,
				new SidecarStartError(describeStartFailure(pythonPath, getStderr(), err))
			);
		});

		child.on('exit', (code) => {
			finish(
				reject,
				new SidecarStartError(
					describeStartFailure(pythonPath, getStderr(), undefined) +
						`\n\n(exit code ${code})`
				)
			);
		});
	});
}

module.exports = {
	startSidecar,
	resolvePythonPath,
	buildEnv,
	describeStartFailure,
	readPortLine,
	Sidecar,
	SidecarStartError,
	PythonConfigError,
	PYTHON_KEY,
	PYTHON_SETTING,
	PYTHON_ENV,
	PORT_LINE_PREFIX,
	TOKEN_HEADER
};
