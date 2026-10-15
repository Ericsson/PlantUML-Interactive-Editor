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
// The install is two spawns of a chosen interpreter -- `-m venv`, then `-m pip
// install` into what that produced -- followed by a rename that publishes the
// result. Choosing the interpreter is the one part Node cannot do alone, so
// each candidate is asked about itself by a one-line Python probe passed on the
// command line; see PROBE_SOURCE. Probing is cheap, so every candidate is asked
// before anything is built, and the install then runs once against an
// interpreter already known to be suitable, so a failure of it is a failed
// install, reported as one.
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
const { isFile } = require('./settings');

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
 * @param {string} globalStoragePath `context.globalStorageUri.fsPath`
 * @param {string} version as returned by bundledWheel
 * @returns {{ dir: string, python: string }} the venv and its interpreter
 */
function managedVenv(globalStoragePath, version) {
	const dir = path.join(globalStoragePath, `${VENV_PREFIX}${version}`);

	return { dir, python: venvInterpreter(dir) };
}

/**
 * The interpreter inside a virtual environment at `dir`.
 *
 * Windows keeps it in `Scripts` and gives it an extension; everywhere else it is
 * `bin/python`. The only copy of this rule: the install goes through this
 * interpreter for pip, and the sidecar is spawned with it afterwards.
 *
 * @param {string} dir a virtual environment
 * @returns {string}
 */
function venvInterpreter(dir) {
	return process.platform === 'win32'
		? path.join(dir, 'Scripts', 'python.exe')
		: path.join(dir, 'bin', 'python');
}

/**
 * The interpreters tried, in order, to build the venv with.
 *
 * Argv prefixes rather than bare names, because the usual way to reach a chosen
 * Python on Windows is through a launcher that takes the version as an argument.
 * The first element is looked up on PATH by spawn().
 *
 * On Windows, `py -3` comes first: the launcher ships with every python.org
 * install and already means "the newest Python 3 on this machine", so it needs
 * no version list behind it. `python` follows, for a machine with an interpreter
 * on PATH but no launcher. `python3` is deliberately absent -- Windows 10 and
 * later ship an App Execution Alias by that name that opens the Microsoft
 * Store, and putting a Store window on screen is a worse first run than trying
 * the next candidate.
 *
 * Elsewhere `python3` is what the machine considers its Python, and the
 * versioned names follow, newest first, for one whose `python3` is too old but
 * which has a newer one installed alongside.
 */
const PYTHON_CANDIDATES =
	process.platform === 'win32'
		? [['py', '-3'], ['python']]
		: [
			['python3'],
			['python3.13'],
			['python3.12'],
			['python3.11'],
			['python3.10']
		];

/**
 * The oldest interpreter that can host the backend.
 *
 * Must match requires-python in pyproject.toml, which pip enforces a second
 * time when the wheel is installed. Checked here first so a too-old candidate
 * is passed over before a venv is built for it, and so the message names the
 * interpreter's age as the problem.
 */
const MIN_PYTHON = [3, 10];

/**
 * What a candidate interpreter is asked about itself.
 *
 * The three facts only the interpreter itself can report: whether *this*
 * interpreter is new enough, and whether it has the two stdlib modules needed
 * to build a venv with pip in it. It prints them in a format agreed in advance,
 * and selectInterpreter judges them. The version is among them because the
 * messages quote it -- "python3: Python 3.9, too old", and the name of the
 * python3.12-venv package to install.
 *
 * Constraints, both of which outlive whoever edits this next:
 *
 * - Single quotes and spaces only. It is passed as one argv element through
 *   CreateProcess on Windows, and staying inside that character set keeps it
 *   there intact. Hence `print(a, b)` for the formatting.
 * - Python 3.6 syntax. Python compiles the whole thing before running any of
 *   it, so the syntax has to be old enough for every interpreter this is put
 *   to. A Python 2 reaching it stops at `importlib.util`, which is the answer
 *   wanted from a Python 2.
 */
const PROBE_SOURCE =
	'import sys, importlib.util as u; ' +
	"print('probe', sys.version_info[0], sys.version_info[1], " +
	"u.find_spec('venv') is not None, u.find_spec('ensurepip') is not None)";

/**
 * The probe's answer, and the whole of "was that a Python at all?".
 *
 * A candidate that answers without this line -- the Microsoft Store alias, a
 * shell reporting 9009, a wrapper script -- is one to move past. `\r?` because
 * Windows ends the line with one.
 */
const PROBE_LINE = /^probe (\d+) (\d+) (True|False) (True|False)\r?$/m;

/**
 * How long a candidate has to answer the probe.
 *
 * Short: it imports two stdlib modules and prints a line. It bounds a candidate
 * that hangs instead of answering, which is a candidate to move past rather
 * than a reason to stop.
 */
const PROBE_TIMEOUT_MS = 10000;

/**
 * Suffix of the directory the venv is built in before it is renamed into place.
 *
 * The pid gives each of our own processes its own build directory, so two
 * windows building at once stay clear of each other. See claim().
 */
const TMP_SUFFIX = '.tmp-';

/**
 * How long each step of the install may take before it is abandoned.
 *
 * Generous: creating the venv runs ensurepip, and pip then fetches Flask, lxml
 * and the rest over the network on a cold cache. It bounds an index that accepts
 * the connection and then stalls.
 */
const INSTALL_TIMEOUT_MS = 300000;

/** How much of the installer's output to keep for an error message. */
const RETAINED_OUTPUT = 8000;

/**
 * Run a command and collect what it prints.
 *
 * Resolves for every outcome, including a command that is absent and one that
 * runs too long, since each is something the caller acts on. Both streams go
 * into the one buffer: the steps here put their progress on whichever they
 * please, and all of it belongs in the output channel.
 *
 * @param {string[]} argv the command; its first element is looked up on PATH
 * @param {object} options
 * @param {number} options.timeoutMs how long it may run before it is killed
 * @param {{ append: (text: string) => void }} [options.output] receives the
 *   output as it arrives
 * @param {Record<string, string>} [options.env] replaces the environment
 * @returns {Promise<{ code: number | null, spawned: boolean, output: string }>}
 *   `code` is null when it was killed for taking too long; `spawned` is false
 *   when the command is not on this machine
 */
function spawnAndCollect(argv, { timeoutMs, output, env }) {
	return new Promise((resolve) => {
		const [executable, ...args] = argv;
		const child = spawn(executable, args, env ? { env } : undefined);

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
		}, timeoutMs);

		for (const stream of [child.stdout, child.stderr]) {
			stream.setEncoding('utf-8');
			stream.on('data', (chunk) => {
				text = (text + chunk).slice(-RETAINED_OUTPUT);
				output?.append(chunk);
			});
		}

		// ENOENT for a candidate that is not installed, the ordinary case for
		// most of the candidate list.
		child.on('error', () => finish({ code: null, spawned: false, output: text }));

		// close, not exit: exit can arrive before the pipes have been drained,
		// and for the probe the output *is* the result.
		child.on('close', (code) => finish({ code, spawned: true, output: text }));
	});
}

/**
 * Ask one candidate interpreter about itself.
 *
 * @param {string[]} command an argv prefix that runs an interpreter; its first
 *   element is looked up on PATH
 * @returns {Promise<{ spawned: boolean, code: number | null, probe: ProbeResult | null, output: string }>}
 */
async function probeInterpreter(command) {
	// -I so the answer is the interpreter's own: no user site directory, no
	// PYTHONPATH, no sitecustomize with opinions. An interpreter too old to know
	// the flag exits with a usage error and no marker line, which is the right
	// answer for one that old.
	const attempt = await spawnAndCollect([...command, '-I', '-c', PROBE_SOURCE], {
		timeoutMs: PROBE_TIMEOUT_MS
	});

	return { ...attempt, probe: parseProbe(attempt.output) };
}

/**
 * What the probe said, or null if that was not the probe answering.
 *
 * @typedef {{ version: number[], venv: boolean, ensurepip: boolean }} ProbeResult
 * @param {string} text everything the candidate printed
 * @returns {ProbeResult | null}
 */
function parseProbe(text) {
	const match = PROBE_LINE.exec(text);

	if (!match) {
		return null;
	}

	return {
		version: [Number(match[1]), Number(match[2])],
		venv: match[3] === 'True',
		ensurepip: match[4] === 'True'
	};
}

/**
 * @param {number[]} version as reported by the probe
 * @returns {boolean} whether it is at or above MIN_PYTHON
 */
function meetsMinimum([major, minor]) {
	return (
		major > MIN_PYTHON[0] || (major === MIN_PYTHON[0] && minor >= MIN_PYTHON[1])
	);
}

/**
 * The first candidate interpreter that can build the backend's venv.
 *
 * Probing is cheap, so every candidate is asked before anything is built, and
 * the install then runs once against an interpreter already known to be
 * suitable. That is what makes a failed install unambiguously a failed install.
 *
 * The two ways a new-enough interpreter can still be unusable stop the search,
 * because the message they produce is the useful outcome: it names the stdlib
 * module missing, and on Debian and Ubuntu the package that supplies it.
 *
 * @returns {Promise<{ command: string[], version: string }>}
 * @throws {NoInterpreterError} when no candidate is new enough
 * @throws {BackendInstallError} when one is, but cannot create a venv with pip
 */
async function selectInterpreter() {
	const rejected = [];

	for (const candidate of PYTHON_CANDIDATES) {
		const label = candidate.join(' ');
		const attempt = await probeInterpreter(candidate);

		if (!attempt.spawned) {
			// Not on this machine. Only worth mentioning if nothing else works.
			rejected.push(`${label}: not found`);
			continue;
		}

		if (!attempt.probe) {
			rejected.push(
				attempt.code === null
					? `${label}: did not answer within ${PROBE_TIMEOUT_MS / 1000}s`
					: `${label}: not a Python (exit code ${attempt.code})`
			);
			continue;
		}

		const version = attempt.probe.version.join('.');

		if (!meetsMinimum(attempt.probe.version)) {
			rejected.push(`${label}: Python ${version}, too old`);
			continue;
		}

		if (!attempt.probe.venv) {
			throw new BackendInstallError(
				`${label} is Python ${version}, but it has no venv module, so it ` +
					'cannot create the virtual environment the backend runs in.'
			);
		}

		if (!attempt.probe.ensurepip) {
			// Debian and Ubuntu ship ensurepip separately, so venv comes out
			// without pip on an otherwise perfectly good interpreter. Nameable
			// because the probe reported the version.
			throw new BackendInstallError(
				`${label} is Python ${version}, but it cannot create a virtual ` +
					'environment with pip in it: the ensurepip module is missing. On ' +
					`Debian and Ubuntu this is the python${version}-venv package.`
			);
		}

		return { command: candidate, version };
	}

	throw new NoInterpreterError(
		`The PlantUML backend needs Python ${MIN_PYTHON.join('.')} or newer to ` +
			`install itself, and none was found:\n\n  ${rejected.join('\n  ')}\n\n` +
			'Install one, or set "plantumlInteractive.pythonPath" to an interpreter ' +
			'that already has the plantuml-gui package.'
	);
}

/**
 * Build an empty venv, with pip in it, at `directory`.
 *
 * `--clear` empties the directory first, so a build left behind by a killed
 * process is started over. The interpreter has already told the probe it has
 * both `venv` and `ensurepip`, so a failure here is a real one: disk space,
 * permissions, a broken stdlib.
 *
 * @param {string[]} command the chosen interpreter, as an argv prefix
 * @param {string} directory where to build it
 * @param {{ append: (text: string) => void }} [output]
 * @throws {BackendInstallError}
 */
async function createVenv(command, directory, output) {
	const attempt = await spawnAndCollect(
		[...command, '-m', 'venv', '--clear', directory],
		{ timeoutMs: INSTALL_TIMEOUT_MS, output }
	);

	if (attempt.code !== 0) {
		throw new BackendInstallError(
			`Could not create a virtual environment at "${directory}" using ` +
				`${command.join(' ')}${describeExit(attempt)}.${detail(attempt.output)}`
		);
	}
}

/**
 * Install `wheel` into the venv `python` belongs to.
 *
 * Through the interpreter, whose path the rename in claim() leaves working.
 * `bin/pip` records an absolute path in its shebang, which the rename
 * invalidates; pip's is the only console script in the venv this applies to.
 *
 * @param {string} python the venv's own interpreter
 * @param {string} wheel the wheel to install
 * @param {{ append: (text: string) => void }} [output]
 * @throws {BackendInstallError}
 */
async function pipInstall(python, wheel, output) {
	const attempt = await spawnAndCollect(
		[
			python,
			'-m',
			'pip',
			'install',
			// No terminal to prompt at.
			'--no-input',
			'--disable-pip-version-check',
			wheel
		],
		{
			timeoutMs: INSTALL_TIMEOUT_MS,
			output,
			env: {
				...process.env,
				// Unbuffered, so pip's progress reaches the output channel while
				// it is happening (its stdout here is a pipe, not a tty).
				PYTHONUNBUFFERED: '1'
			}
		}
	);

	if (attempt.code !== 0) {
		throw new BackendInstallError(
			`pip could not install ${path.basename(wheel)}` +
				`${describeExit(attempt)}.${detail(attempt.output)}`
		);
	}
}

/**
 * Move a finished venv to where the extension looks for it.
 *
 * Returns whether this process was the one that put it there.
 *
 * The rename is what makes the install atomic, and both reasons matter:
 *
 * *Only a finished venv is visible.* The extension decides the backend is
 * installed by looking for the interpreter inside `target`. Building elsewhere
 * and renaming a finished result means a `target` that exists has the package
 * installed, through a cancelled window, a killed process or a full disk
 * between `-m venv` and pip.
 *
 * *Two windows racing settle through the filesystem.* Each VS Code window is its
 * own extension host, so both may find the venv missing and both start building.
 * They build in separate pid-suffixed directories and then race to rename: the
 * loser finds `target` already a directory, discards its own work, and uses the
 * winner's. That is safe precisely because of the previous paragraph -- a
 * `target` that exists is a finished venv, whoever made it.
 *
 * Renaming a venv works for the two ways this one is ever used: `pyvenv.cfg`
 * records the *base* interpreter's location, not the venv's own, and `sys.prefix`
 * is derived at run time from the path the interpreter was invoked by.
 *
 * @param {string} built the finished venv
 * @param {string} target where it belongs
 * @returns {boolean} whether this process won
 */
function claim(built, target) {
	try {
		fs.renameSync(built, target);
		return true;
	} catch (err) {
		// Which errno this is depends on the platform -- POSIX reports
		// ENOTEMPTY or EEXIST, Windows EPERM or EACCES -- so what settles it is
		// the state of the filesystem, not the code.
		if (isDirectory(target)) {
			// Somebody else claimed target first; keep their result, drop ours.
			fs.rmSync(built, { recursive: true, force: true });
			return false;
		}

		throw err;
	}
}

/**
 * Create the venv at `target` and install `wheel` into it.
 *
 * Idempotent: an existing `target` is a finished install by the invariant claim()
 * maintains, so it is left alone. Checked here as well as by the caller, closing
 * the window between that check and this call, which belongs to whatever the
 * user's other editor windows are doing.
 *
 * @param {object} options
 * @param {string[]} options.command the chosen interpreter, as an argv prefix
 * @param {string} options.wheel the wheel to install
 * @param {string} options.target the venv to create
 * @param {{ append: (text: string) => void }} [options.output]
 * @throws {BackendInstallError}
 */
async function install({ command, wheel, target, output }) {
	if (isDirectory(target)) {
		output?.append(`already installed at ${target}\n`);
		return;
	}

	// The extension's global storage directory is promised to it but not created
	// for it, and the rename needs the parent to exist.
	fs.mkdirSync(path.dirname(target), { recursive: true });

	const built = `${target}${TMP_SUFFIX}${process.pid}`;
	fs.rmSync(built, { recursive: true, force: true });

	try {
		output?.append(`creating a virtual environment at ${target}\n`);
		await createVenv(command, built, output);
		await pipInstall(venvInterpreter(built), wheel, output);

		// On its own line, because optional chaining short-circuits the arguments
		// along with the call: inside the append below, this would run only for a
		// caller that passed a sink.
		const won = claim(built, target);

		output?.append(
			won
				? `installed the backend into ${target}\n`
				: `another window installed ${target} first; using that\n`
		);
	} catch (err) {
		// The build directory's name carries this pid, so nothing else would
		// ever clean it up.
		fs.rmSync(built, { recursive: true, force: true });
		throw err;
	}
}

/**
 * @param {string} target
 * @returns {boolean} whether it is a directory
 */
function isDirectory(target) {
	try {
		return fs.statSync(target).isDirectory();
	} catch {
		return false;
	}
}

/**
 * @param {{ code: number | null }} attempt
 * @returns {string} how it ended, ready to append to a message
 */
function describeExit(attempt) {
	return attempt.code === null
		? ` (it did not finish within ${INSTALL_TIMEOUT_MS / 1000}s)`
		: ` (exit code ${attempt.code})`;
}

/**
 * Install the bundled wheel into a venv of the extension's own, and return the
 * interpreter to run the backend with.
 *
 * Safe to call when the backend is already installed: an existing venv is left
 * alone, which also closes the window between a caller's check and this call.
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

	if (!isDirectory(venv.dir)) {
		const interpreter = await selectInterpreter();

		await install({
			command: interpreter.command,
			wheel: wheel.path,
			target: venv.dir,
			output
		});
	}

	if (!isFile(venv.python)) {
		// The invariant claim() maintains says this cannot happen: a venv
		// directory that exists is a finished one. Checked because the whole
		// point of the invariant is that callers may rely on this path.
		throw new BackendInstallError(
			`The PlantUML backend was installed into "${venv.dir}", but there is ` +
				`no interpreter at "${venv.python}".`
		);
	}

	return venv.python;
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
	venvInterpreter,
	installBackend,
	install,
	claim,
	probeInterpreter,
	selectInterpreter,
	BundledWheelError,
	BackendInstallError,
	NoInterpreterError,
	BACKEND_DIR,
	VENV_PREFIX,
	WHEEL_NAME,
	PYTHON_CANDIDATES,
	MIN_PYTHON,
	PROBE_SOURCE,
	PROBE_TIMEOUT_MS,
	TMP_SUFFIX,
	INSTALL_TIMEOUT_MS
};
