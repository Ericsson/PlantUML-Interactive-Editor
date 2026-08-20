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

// The backend the extension provisions for itself: where the wheel it ships is,
// where the virtual environment that wheel gets installed into goes, and which
// interpreter builds it.
//
// The vsix carries the wheel (see scripts/build_release.sh), giving the
// extension everything it needs to produce a working backend.
//
// The install is Python: src/plantuml_gui/install_venv.py, run straight out of
// the bundled wheel, since a wheel is a zip and Python imports out of one
// without it being installed first. The division of labour:
//
//   this file discovers, install_venv.py judges.
//
// Enumerating candidate interpreters is this side's job. Each is spawned
// against that module, which is the authority on its own suitability because
// it *is* the interpreter in question, and the version rule lives once, next
// to requires-python. EXIT_UNSUITABLE_INTERPRETER means try the next
// candidate; any other non-zero exit is a real failure and stops the search.
// See that module's docstring for the other half of this.
//
// Everything else here is paths and names, with no side effects, so that
// resolving an already-installed backend costs a stat, and so the rules can
// be tested without building a venv.
//
// The caller passes the two directories it owns, the extension's own path and
// its global storage path, and an optional sink for the installer's output.
// That is what lets this be tested in plain Node, as with settings.js.

const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');

/**
 * The directory inside the extension holding the bundled wheel.
 *
 * Kept in step with scripts/build_release.sh, which puts the wheel here, and
 * with .vscodeignore, which must not exclude it.
 */
const BACKEND_DIR = 'backend';

/**
 * The bundled wheel's filename, and the version inside it.
 *
 * Anchored on the distribution name, open about the compatibility tags that
 * follow the version, so any pure-Python wheel of this package matches.
 *
 * The version must start with a digit, which is what makes it safe to use as a
 * directory name below: a filename cannot contain a path separator, `-` is
 * excluded by the capture, and `.` and `..` cannot match.
 */
const WHEEL_NAME = /^plantuml_gui-([0-9][^-]*)-.*\.whl$/;

/**
 * Prefix of the managed venv's directory name; the backend version follows it.
 *
 * See managedVenv for why the version is in the name.
 */
const VENV_PREFIX = 'venv-';

/** Thrown when the extension is not carrying exactly one usable wheel. */
class BundledWheelError extends Error {}

/** Thrown when the managed backend could not be installed. */
class BackendInstallError extends Error {}

/**
 * Thrown when no interpreter on this machine can host the backend.
 *
 * A subclass so a caller that only wants to say "the install failed" can catch
 * the base class, while the one message a user can act on differently -- install
 * a Python, or point the setting at one you already have -- can be told apart.
 */
class NoInterpreterError extends BackendInstallError {}

/**
 * The wheel this build of the extension ships, and its version.
 *
 * Exactly one must be present. Zero means a development checkout that has
 * never run a build, since `backend/` is a build product and gitignored as
 * one; the build clears the directory before copying, so more than one means
 * something put it there by hand. The message names the directory, because
 * the fix is to run the build.
 *
 * @param {string} extensionPath the extension's own directory
 * @returns {{ path: string, version: string }} the wheel, and the version read
 *   out of its filename
 * @throws {BundledWheelError}
 */
function bundledWheel(extensionPath) {
	const dir = path.join(extensionPath, BACKEND_DIR);

	let entries;

	try {
		entries = fs.readdirSync(dir);
	} catch (err) {
		throw new BundledWheelError(
			`Could not read the bundled backend directory "${dir}": ${err.message}. ` +
				'Build it with scripts/build_release.sh.'
		);
	}

	const wheels = entries
		.map((entry) => ({ entry, match: WHEEL_NAME.exec(entry) }))
		.filter(({ match }) => match);

	if (wheels.length !== 1) {
		throw new BundledWheelError(
			`Expected exactly one plantuml_gui wheel in "${dir}", found ` +
				`${wheels.length}. Build it with scripts/build_release.sh.`
		);
	}

	const { entry, match } = wheels[0];

	return { path: path.join(dir, entry), version: match[1] };
}

/**
 * Where the backend of a given version lives, and the interpreter inside it.
 *
 * Under the extension's global storage, the directory VS Code hands each
 * extension for its machine-local data. Under Remote-SSH it resolves on the
 * remote machine, which is where the extension host runs and therefore where
 * the venv has to be. It belongs to this extension alone, so it can be
 * rebuilt freely.
 *
 * The version is in the directory name, which is the whole of the update story:
 * after an extension update the path for the newly bundled wheel does not exist
 * yet, so the install runs again, and reinstalling an older vsix finds its own
 * venv still beside it.
 *
 * `bin/python`, and so Linux and macOS only; Windows puts it in
 * `Scripts/python.exe`. Matches venv_python() in install_venv.py, which builds
 * the venv this points into.
 *
 * @param {string} globalStoragePath `context.globalStorageUri.fsPath`
 * @param {string} version as returned by bundledWheel
 * @returns {{ dir: string, python: string }} the venv and its interpreter
 */
function managedVenv(globalStoragePath, version) {
	const dir = path.join(globalStoragePath, `${VENV_PREFIX}${version}`);

	return { dir, python: path.join(dir, 'bin', 'python') };
}

/**
 * The interpreters tried, in order, to build the venv with.
 *
 * These are names, looked up on PATH by spawn(). `python3` first because it
 * is what the machine considers its Python. The versioned names follow,
 * newest first, for a machine whose `python3` is too old but which has a
 * newer one installed alongside.
 */
const PYTHON_CANDIDATES = [
	'python3',
	'python3.13',
	'python3.12',
	'python3.11',
	'python3.10'
];

/**
 * The module inside the wheel that performs the install.
 *
 * Must match the path of src/plantuml_gui/install_venv.py.
 */
const INSTALLER_MODULE = 'plantuml_gui.install_venv';

/**
 * "This interpreter cannot host the backend": try the next candidate.
 *
 * Must match EXIT_UNSUITABLE_INTERPRETER in src/plantuml_gui/install_venv.py.
 * Every other non-zero exit is a genuine failure, so this constant is the whole
 * of what separates "keep looking" from "stop and report".
 */
const EXIT_UNSUITABLE_INTERPRETER = 2;

/**
 * How long the install may take before it is abandoned.
 *
 * Generous: it creates a venv and pip fetches Flask, lxml and the rest over the
 * network on a cold cache. It bounds an index that accepts the connection and
 * then stalls.
 */
const INSTALL_TIMEOUT_MS = 300000;

/** How much of the installer's output to keep for an error message. */
const RETAINED_OUTPUT = 8000;

/**
 * Run the installer under one candidate interpreter.
 *
 * Reports the outcome of a failed run, letting the caller decide which
 * failures are worth continuing past.
 *
 * @param {string} python interpreter name or path, looked up on PATH
 * @param {object} options
 * @param {string} options.wheel the wheel to install
 * @param {string} options.target the venv to create
 * @param {{ append: (text: string) => void }} [options.output] receives the
 *   installer's progress and pip's own output as it arrives
 * @returns {Promise<{ code: number | null, spawned: boolean, output: string }>}
 */
function runInstaller(python, { wheel, target, output }) {
	return new Promise((resolve) => {
		const child = spawn(
			python,
			['-m', INSTALLER_MODULE, '--wheel', wheel, '--target', target],
			{
				env: {
					...process.env,
					// How the installer is found at all: it is inside the wheel,
					// which is not installed yet. Set here so this wheel is the
					// only place the module comes from.
					PYTHONPATH: wheel,
					// Unbuffered, so pip's progress reaches the output channel
					// while it is happening (stdout here is a pipe, not a tty).
					PYTHONUNBUFFERED: '1'
				}
			}
		);

		let text = '';
		let settled = false;

		const finish = (result) => {
			if (settled) return;
			settled = true;
			clearTimeout(timer);
			resolve(result);
		};

		const timer = setTimeout(() => {
			child.kill();
			finish({ code: null, spawned: true, output: text });
		}, INSTALL_TIMEOUT_MS);

		// The installer writes its progress and pip's output to stderr; both
		// streams are collected regardless.
		for (const stream of [child.stdout, child.stderr]) {
			stream.setEncoding('utf-8');
			stream.on('data', (chunk) => {
				text = (text + chunk).slice(-RETAINED_OUTPUT);
				output?.append(chunk);
			});
		}

		// ENOENT for a candidate that is not installed, the ordinary case for
		// most of the list.
		child.on('error', () => finish({ code: null, spawned: false, output: text }));

		child.on('exit', (code) => finish({ code, spawned: true, output: text }));
	});
}

/**
 * Install the bundled wheel into a venv of the extension's own, and return the
 * interpreter to run the backend with.
 *
 * Safe to call when the backend is already installed: the Python side leaves
 * an existing venv alone, and this closes the window between a caller's check
 * and this call.
 *
 * @param {object} options
 * @param {string} options.extensionPath the extension's own directory
 * @param {string} options.globalStoragePath `context.globalStorageUri.fsPath`
 * @param {{ append: (text: string) => void }} [options.output]
 * @returns {Promise<string>} the managed venv's interpreter
 * @throws {BundledWheelError} when the vsix carries no usable wheel
 * @throws {NoInterpreterError} when no candidate interpreter is new enough
 * @throws {BackendInstallError} when an install was attempted and failed
 */
async function installBackend({ extensionPath, globalStoragePath, output }) {
	const wheel = bundledWheel(extensionPath);
	const venv = managedVenv(globalStoragePath, wheel.version);

	const rejected = [];

	for (const candidate of PYTHON_CANDIDATES) {
		const attempt = await runInstaller(candidate, {
			wheel: wheel.path,
			target: venv.dir,
			output
		});

		if (attempt.code === 0) {
			return venv.python;
		}

		if (!attempt.spawned) {
			// Not on this machine. Only worth mentioning if nothing else works.
			rejected.push(`${candidate}: not found`);
			continue;
		}

		if (attempt.code === EXIT_UNSUITABLE_INTERPRETER) {
			rejected.push(`${candidate}: too old`);
			continue;
		}

		throw new BackendInstallError(
			`Could not install the PlantUML backend into "${venv.dir}" using ` +
				`${candidate}.` +
				(attempt.code === null
					? ` It did not finish within ${INSTALL_TIMEOUT_MS / 1000}s.`
					: '') +
				detail(attempt.output)
		);
	}

	throw new NoInterpreterError(
		'The PlantUML backend needs Python 3.10 or newer to install itself, and ' +
			`none was found:\n\n  ${rejected.join('\n  ')}\n\n` +
			'Install one, or set "plantumlInteractive.pythonPath" to an interpreter ' +
			'that already has the plantuml-gui package.'
	);
}

/**
 * @param {string} output
 * @returns {string} the tail of `output`, ready to append to a message, or ''
 */
function detail(output) {
	const trimmed = output.trim();
	return trimmed ? `\n\n${trimmed}` : '';
}

module.exports = {
	bundledWheel,
	managedVenv,
	installBackend,
	runInstaller,
	BundledWheelError,
	BackendInstallError,
	NoInterpreterError,
	BACKEND_DIR,
	VENV_PREFIX,
	WHEEL_NAME,
	PYTHON_CANDIDATES,
	INSTALLER_MODULE,
	EXIT_UNSUITABLE_INTERPRETER,
	INSTALL_TIMEOUT_MS
};
