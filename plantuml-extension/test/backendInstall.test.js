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

// Tests for finding the bundled wheel, placing the venv, and choosing the
// interpreter that builds it.
//
// Every interpreter here is a shell script on a PATH of this suite's own making,
// which answers the probe with whatever version a test needs and plays the two
// steps of the install. That is what makes "too old, try the next", "a real
// failure, stop", and the atomic rename testable in milliseconds and without a
// network.

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {
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
	PYTHON_CANDIDATES,
	MIN_PYTHON,
	TMP_SUFFIX
} = require('../src/backendInstall');

/** @type {string[]} directories to remove when the suite finishes. */
const temporary = [];

/** @returns {string} a fresh directory that will be cleaned up. */
function tempDir(prefix) {
	const dir = fs.mkdtempSync(path.join(os.tmpdir(), prefix));
	temporary.push(dir);
	return dir;
}

/**
 * An extension directory carrying the named wheels.
 *
 * @param {string[]} wheels filenames to create in `backend/`
 * @returns {string} the extension path
 */
function extensionWith(wheels) {
	const dir = tempDir('ext-');
	fs.mkdirSync(path.join(dir, BACKEND_DIR));
	for (const wheel of wheels) {
		fs.writeFileSync(path.join(dir, BACKEND_DIR, wheel), '');
	}
	return dir;
}

/**
 * A stand-in for a Python interpreter, named as a candidate would be.
 *
 * It plays every part of an install: it answers the probe, it builds something
 * venv-shaped when asked for a venv -- including a copy of itself as that venv's
 * interpreter, so the pip step has something to run -- and it reports success
 * for pip. Each option turns one of those into a failure instead. Every
 * invocation is appended to a log, so a test can assert what ran, with which
 * arguments, and in what order.
 *
 * `/bin/mkdir` and `/bin/cp` by absolute path, and the script's own path baked
 * in, because a test that drives the candidate loop replaces PATH with the
 * directory this returns.
 *
 * POSIX only: Node refuses to spawn a `.cmd` without a shell, and finds it only
 * through PATHEXT when it has one, so nothing can stand in for an interpreter on
 * Windows. The suites that use this skip there.
 *
 * @param {string} name what to call it, so PATH lookup finds it as a candidate
 * @param {object} [options]
 * @param {string} [options.probe] the line it answers the probe with
 * @param {number} [options.venvExit] make `-m venv` fail with this code
 * @param {number} [options.pipExit] make `-m pip install` fail with this code
 * @param {string} [options.claims] a directory for pip to create as a
 *   side effect, standing in for another window finishing while this one builds
 * @returns {{ dir: string, path: string, calls: () => string[] }}
 */
function fakePython(
	name,
	{ probe = 'probe 3 12 True True', venvExit = 0, pipExit = 0, claims = '' } = {}
) {
	const dir = tempDir('py-');
	const script = path.join(dir, name);
	const log = path.join(dir, 'calls.log');

	fs.writeFileSync(
		script,
		'#!/bin/sh\n' +
			`SELF="${script}"\n` +
			`echo "$*" >> "${log}"\n` +
			'echo "$0 ran with: $*" >&2\n' +
			// Skip an argv prefix, as `py -3` passes one, so the step is
			// recognised by what follows it.
			'while [ $# -gt 0 ] && [ "$1" != "-I" ] && [ "$1" != "-m" ]; do shift; done\n' +
			// The probe is the only thing passed -I.
			`if [ "$1" = "-I" ]; then echo "${probe}"; exit 0; fi\n` +
			// Both remaining steps put their directory last.
			'for a in "$@"; do last="$a"; done\n' +
			'if [ "$1" = "-m" ] && [ "$2" = "venv" ]; then\n' +
			(venvExit === 0
				? '  /bin/mkdir -p "$last/bin" && /bin/cp "$SELF" "$last/bin/python"\n' +
					'  exit $?\n'
				: `  echo "Error: could not create venv" >&2\n  exit ${venvExit}\n`) +
			'fi\n' +
			'if [ "$1" = "-m" ] && [ "$2" = "pip" ]; then\n' +
			(claims
				? `  /bin/mkdir -p "${claims}" && : > "${claims}/theirs"\n`
				: '') +
			(pipExit === 0
				? '  echo "Successfully installed plantuml-gui"\n  exit 0\n'
				: `  echo "ERROR: no matching distribution" >&2\n  exit ${pipExit}\n`) +
			'fi\n' +
			'exit 1\n'
	);
	fs.chmodSync(script, 0o755);

	return {
		dir,
		path: script,
		calls: () =>
			fs.existsSync(log)
				? fs.readFileSync(log, 'utf-8').split('\n').filter(Boolean)
				: []
	};
}

/** Skips the suite calling it on Windows; see fakePython. */
function posixOnly() {
	suiteSetup(function () {
		if (process.platform === 'win32') {
			this.skip();
		}
	});
}

/**
 * A directory to put on PATH, holding stand-ins that answer the probe.
 *
 * A stand-in either prints a line and exits 0, as an interpreter answering the
 * probe does, or exits with a code of its own, as an App Execution Alias, a
 * shell reporting 9009 or a wrapper script does.
 *
 * @param {Record<string, string | number>} answers stand-in name to the line it
 *   should print, or to an exit code to produce silently
 * @returns {string} the directory
 */
function fakeProbes(answers) {
	const dir = tempDir('probe-');

	for (const [name, answer] of Object.entries(answers)) {
		const line = typeof answer === 'string' ? answer : '';
		const code = typeof answer === 'string' ? 0 : answer;

		if (process.platform === 'win32') {
			fs.writeFileSync(
				path.join(dir, `${name}.cmd`),
				'@echo off\r\n' +
					(line ? `echo ${line}\r\n` : '') +
					`exit /b ${code}\r\n`
			);
			continue;
		}

		const script = path.join(dir, name);
		fs.writeFileSync(
			script,
			'#!/bin/sh\n' + (line ? `echo "${line}"\n` : '') + `exit ${code}\n`
		);
		fs.chmodSync(script, 0o755);
	}

	return dir;
}

suite('backendInstall: the bundled wheel', () => {
	test('is found by its filename, with its version', () => {
		const dir = extensionWith(['plantuml_gui-0.31-py3-none-any.whl']);

		assert.deepStrictEqual(bundledWheel(dir), {
			path: path.join(dir, BACKEND_DIR, 'plantuml_gui-0.31-py3-none-any.whl'),
			version: '0.31'
		});
	});

	test('reads a three-component version too', () => {
		// An extension-only patch release leaves the backend at major.minor,
		// but nothing stops the backend having a patch of its own.
		const dir = extensionWith(['plantuml_gui-0.31.2-py3-none-any.whl']);

		assert.strictEqual(bundledWheel(dir).version, '0.31.2');
	});

	test('ignores anything that is not a wheel of ours', () => {
		const dir = extensionWith([
			'plantuml_gui-0.31-py3-none-any.whl',
			'README.txt',
			'flask-3.1.3-py3-none-any.whl'
		]);

		assert.strictEqual(bundledWheel(dir).version, '0.31');
	});

	test('refuses a build that produced none', () => {
		const dir = extensionWith([]);

		assert.throws(() => bundledWheel(dir), BundledWheelError);
	});

	test('refuses two, rather than picking one', () => {
		const dir = extensionWith([
			'plantuml_gui-0.31-py3-none-any.whl',
			'plantuml_gui-0.32-py3-none-any.whl'
		]);

		assert.throws(() => bundledWheel(dir), (err) => {
			assert.ok(err instanceof BundledWheelError, err.constructor.name);
			assert.ok(err.message.includes('found 2'), err.message);
			return true;
		});
	});

	test('says how to fix a checkout that has never been built', () => {
		const dir = tempDir('nobackend-');

		assert.throws(() => bundledWheel(dir), (err) => {
			assert.ok(err.message.includes('build_release.sh'), err.message);
			return true;
		});
	});
});

suite('backendInstall: where the venv goes', () => {
	test('is named after the version it holds', () => {
		const dir = path.join('/storage', `${VENV_PREFIX}0.31`);

		assert.deepStrictEqual(managedVenv('/storage', '0.31'), {
			dir,
			python: venvInterpreter(dir)
		});
	});

	test('the interpreter is where this platform keeps it', () => {
		// Windows keeps it in Scripts and gives it an extension. The only copy
		// of that rule now that the install is all on this side.
		const python = venvInterpreter('/venv');

		assert.strictEqual(
			python,
			process.platform === 'win32'
				? path.join('/venv', 'Scripts', 'python.exe')
				: path.join('/venv', 'bin', 'python')
		);
	});

	test('a new version is a different directory', () => {
		// The whole of the update story: the new path does not exist yet, so
		// the install runs, and the old venv is left where it was.
		assert.notStrictEqual(
			managedVenv('/storage', '0.31').dir,
			managedVenv('/storage', '0.32').dir
		);
	});

	test('the interpreter is inside the venv', () => {
		const venv = managedVenv('/storage', '0.31');

		assert.ok(venv.python.startsWith(venv.dir + path.sep));
	});
});

suite('backendInstall: asking an interpreter about itself', () => {
	test('reads the version, and the two modules a venv needs', async () => {
		const bin = fakeProbes({ py: 'probe 3 12 True True' });

		const attempt = await probeInterpreter([path.join(bin, 'py')]);

		assert.strictEqual(attempt.spawned, true);
		assert.deepStrictEqual(attempt.probe, {
			version: [3, 12],
			venv: true,
			ensurepip: true
		});
	});

	test('reads a missing module as missing', async () => {
		const bin = fakeProbes({ py: 'probe 3 12 True False' });

		const attempt = await probeInterpreter([path.join(bin, 'py')]);

		assert.strictEqual(attempt.probe.ensurepip, false);
		assert.strictEqual(attempt.probe.venv, true);
	});

	test('reports an interpreter that is not there without throwing', async () => {
		const attempt = await probeInterpreter(['/nonexistent/python3']);

		assert.strictEqual(attempt.spawned, false);
		assert.strictEqual(attempt.probe, null);
	});

	test('has no answer from something that is not a Python', async () => {
		// The Microsoft Store alias, a shell reporting 9009, a wrapper script:
		// it ran, so it is not a missing command, but it did not answer.
		const bin = fakeProbes({ py: 9009 });

		const attempt = await probeInterpreter([path.join(bin, 'py')]);

		assert.strictEqual(attempt.spawned, true);
		// Not the code itself: 9009 is what cmd reports, and POSIX truncates an
		// exit status to 8 bits. What matters is that it answered, and that the
		// answer was not the probe's.
		assert.notStrictEqual(attempt.code, 0);
		assert.strictEqual(attempt.probe, null);
	});

	test('has no answer from something that exits 0 saying nothing useful', async () => {
		const bin = fakeProbes({ py: 'Python 3.12.1' });

		const attempt = await probeInterpreter([path.join(bin, 'py')]);

		assert.strictEqual(attempt.code, 0);
		assert.strictEqual(attempt.probe, null);
	});

	test('passes the prefix before the probe, as py -3 needs', async function () {
		// The Windows launcher takes the version as an argument, so a candidate
		// is an argv prefix rather than a name. What is under test is the argv the
		// probe travels in.
		if (process.platform === 'win32') {
			this.skip();
		}

		const python = fakePython('launcher');

		const attempt = await probeInterpreter([python.path, '-3']);

		assert.ok(/-3 -I -c/.test(attempt.output), attempt.output);
	});

	test('a real interpreter answers it', async function () {
		// The only test that would catch a syntax error in the probe, or a
		// version of Python that stops printing what it is parsed for.
		const attempt = await probeInterpreter(['python3']);

		if (!attempt.spawned) {
			this.skip();
		}

		assert.ok(attempt.probe, attempt.output);
		assert.strictEqual(attempt.probe.version[0], 3);
		assert.ok(attempt.probe.version[1] >= 0);
	});
});

suite('backendInstall: choosing the interpreter to build with', () => {
	/** The names the candidate list actually looks for on this platform. */
	const [first, second] = PYTHON_CANDIDATES.map((candidate) => candidate[0]);

	const suitable = 'probe 3 12 True True';

	let savedPath;

	setup(() => {
		savedPath = process.env.PATH;
	});

	teardown(() => {
		process.env.PATH = savedPath;
	});

	test('takes the first candidate that can host the backend', async () => {
		process.env.PATH = fakeProbes({ [first]: suitable });

		assert.deepStrictEqual(await selectInterpreter(), {
			command: PYTHON_CANDIDATES[0],
			version: '3.12'
		});
	});

	test('moves on from one that is too old', async () => {
		process.env.PATH = fakeProbes({
			[first]: 'probe 3 9 True True',
			[second]: suitable
		});

		const chosen = await selectInterpreter();

		assert.deepStrictEqual(chosen.command, PYTHON_CANDIDATES[1]);
	});

	test('takes the floor itself', async () => {
		process.env.PATH = fakeProbes({
			[first]: `probe ${MIN_PYTHON.join(' ')} True True`
		});

		assert.strictEqual(await selectInterpreter().then((c) => c.version), MIN_PYTHON.join('.'));
	});

	test('moves on from a candidate that is not installed', async () => {
		// The ordinary case: most of the list is absent on any given machine.
		process.env.PATH = fakeProbes({ [second]: suitable });

		const chosen = await selectInterpreter();

		assert.deepStrictEqual(chosen.command, PYTHON_CANDIDATES[1]);
	});

	test('moves on from something that answers but is not a Python', async () => {
		process.env.PATH = fakeProbes({ [first]: 9009, [second]: suitable });

		const chosen = await selectInterpreter();

		assert.deepStrictEqual(chosen.command, PYTHON_CANDIDATES[1]);
	});

	test('reports every candidate, and its version, when none will do', async () => {
		process.env.PATH = fakeProbes({ [first]: 'probe 3 9 True True' });

		await assert.rejects(() => selectInterpreter(), (err) => {
			assert.ok(err instanceof NoInterpreterError, err.constructor.name);
			assert.ok(err.message.includes(`${first}: Python 3.9, too old`), err.message);
			assert.ok(err.message.includes(`${second}: not found`), err.message);
			return true;
		});
	});

	test('the message says what the user can do about it', async () => {
		process.env.PATH = fakeProbes({});

		await assert.rejects(() => selectInterpreter(), (err) => {
			assert.ok(err.message.includes('3.10 or newer'), err.message);
			assert.ok(err.message.includes('plantumlInteractive.pythonPath'), err.message);
			return true;
		});
	});

	test('stops at a new-enough interpreter that has no ensurepip', async () => {
		// The Debian and Ubuntu case, where venv comes without pip. The message
		// names the package to install, which it can do because the probe
		// reported the version.
		process.env.PATH = fakeProbes({
			[first]: 'probe 3 12 True False',
			[second]: suitable
		});

		await assert.rejects(() => selectInterpreter(), (err) => {
			assert.ok(err instanceof BackendInstallError, err.constructor.name);
			assert.ok(!(err instanceof NoInterpreterError), 'wrong subclass');
			assert.ok(err.message.includes('python3.12-venv'), err.message);
			return true;
		});
	});

	test('stops at a new-enough interpreter that has no venv module', async () => {
		process.env.PATH = fakeProbes({
			[first]: 'probe 3 12 False True',
			[second]: suitable
		});

		await assert.rejects(() => selectInterpreter(), (err) => {
			assert.ok(err instanceof BackendInstallError, err.constructor.name);
			assert.ok(err.message.includes('no venv module'), err.message);
			return true;
		});
	});

	test('the floor matches requires-python', () => {
		// The gate and the metadata pip enforces have to agree. A gate above
		// requires-python would refuse interpreters that work; below it, the
		// install would get as far as pip and fail there, blaming the wheel for
		// the interpreter's age.
		const pyproject = fs.readFileSync(
			path.join(__dirname, '..', '..', 'pyproject.toml'),
			'utf-8'
		);
		const declared = /requires-python\s*=\s*"[><=]*(\d+)\.(\d+)"/.exec(pyproject);

		assert.ok(declared, 'no requires-python found in pyproject.toml');
		assert.deepStrictEqual(MIN_PYTHON, [
			Number(declared[1]),
			Number(declared[2])
		]);
	});
});

suite('backendInstall: publishing a finished venv', () => {
	posixOnly();

	test('moves the build into place', () => {
		const dir = tempDir('claim-');
		const built = path.join(dir, `venv${TMP_SUFFIX}1`);
		fs.mkdirSync(built);
		fs.writeFileSync(path.join(built, 'marker'), '');
		const target = path.join(dir, 'venv');

		assert.strictEqual(claim(built, target), true);
		assert.ok(fs.existsSync(path.join(target, 'marker')));
		assert.ok(!fs.existsSync(built));
	});

	test('yields to a venv that arrived first', () => {
		// The loser of a two-window race uses the winner's venv, which is safe
		// because a target that exists is a finished one.
		const dir = tempDir('claim-');
		const built = path.join(dir, `venv${TMP_SUFFIX}2`);
		fs.mkdirSync(built);
		fs.writeFileSync(path.join(built, 'mine'), '');
		const target = path.join(dir, 'venv');
		fs.mkdirSync(target);
		fs.writeFileSync(path.join(target, 'theirs'), '');

		assert.strictEqual(claim(built, target), false);
		assert.ok(fs.existsSync(path.join(target, 'theirs')));
		assert.ok(!fs.existsSync(path.join(target, 'mine')));
	});

	test('discards its own build when it loses', () => {
		const dir = tempDir('claim-');
		const built = path.join(dir, `venv${TMP_SUFFIX}3`);
		fs.mkdirSync(built);
		const target = path.join(dir, 'venv');
		fs.mkdirSync(target);

		claim(built, target);

		assert.ok(!fs.existsSync(built));
	});

	test('a failure that is not a race is raised', () => {
		// A target whose parent does not exist is a bug, not a lost race.
		const dir = tempDir('claim-');
		const built = path.join(dir, `venv${TMP_SUFFIX}4`);
		fs.mkdirSync(built);

		assert.throws(() => claim(built, path.join(dir, 'absent', 'venv')));
	});
});

suite('backendInstall: building the venv', () => {
	posixOnly();

	/** @returns {{ append: (text: string) => void, text: string }} */
	function sink() {
		return {
			text: '',
			append(chunk) {
				this.text += chunk;
			}
		};
	}

	/**
	 * @param {{ calls: () => string[] }} python a stand-in that has been asked
	 *   to build a venv
	 * @returns {string} the directory it was asked to build it in
	 */
	function builtIn(python) {
		const venvCall = python.calls().find((call) => call.startsWith('-m venv'));

		assert.ok(venvCall, `nothing built a venv: ${python.calls().join(', ')}`);

		return venvCall.replace('-m venv --clear ', '');
	}

	test('creates the venv and installs the wheel into it', async () => {
		const python = fakePython('python3');
		const target = path.join(tempDir('storage-'), 'venv-0.31');

		await install({
			command: [python.path],
			wheel: '/wheels/plantuml_gui-0.31.whl',
			target
		});

		assert.ok(fs.existsSync(target));
		const [venv, pip] = python.calls();
		assert.ok(venv.startsWith('-m venv --clear '), venv);
		assert.ok(pip.includes('-m pip install'), pip);
		assert.ok(pip.endsWith('/wheels/plantuml_gui-0.31.whl'), pip);
	});

	test('builds somewhere else and renames', async () => {
		// What makes the target's existence mean the install finished.
		const python = fakePython('python3');
		const target = path.join(tempDir('storage-'), 'venv-0.31');

		await install({ command: [python.path], wheel: '/wheels/w.whl', target });

		const built = builtIn(python);
		assert.notStrictEqual(built, target);
		assert.ok(built.startsWith(`${target}${TMP_SUFFIX}`), built);
		assert.ok(!fs.existsSync(built));
	});

	test('runs pip through the interpreter of the venv it just built', async () => {
		// Through the interpreter, whose path the rename leaves working; bin/pip
		// records an absolute path in its shebang.
		const python = fakePython('python3');
		const target = path.join(tempDir('storage-'), 'venv-0.31');

		await install({ command: [python.path], wheel: '/wheels/w.whl', target });

		// The stand-in copies itself into the venv it is asked to build, so the
		// pip call was logged by that copy, from inside the build directory.
		assert.ok(fs.existsSync(venvInterpreter(target)));
		assert.ok(
			python.calls().some((call) => call.includes('-m pip install')),
			python.calls().join('\n')
		);
	});

	test('passes the prefix through to the venv step, as py -3 needs', async () => {
		const python = fakePython('launcher');
		const target = path.join(tempDir('storage-'), 'venv-0.31');

		await install({
			command: [python.path, '-3'],
			wheel: '/wheels/w.whl',
			target
		});

		assert.ok(python.calls()[0].startsWith('-3 -m venv'), python.calls()[0]);
	});

	test('creates the storage directory', async () => {
		// VS Code promises the global storage path, not the directory.
		const target = path.join(tempDir('storage-'), 'never', 'made', 'venv-0.31');

		await install({
			command: [fakePython('python3').path],
			wheel: '/wheels/w.whl',
			target
		});

		assert.ok(fs.existsSync(target));
	});

	test('leaves an existing venv alone, and says so', async () => {
		const python = fakePython('python3');
		const target = path.join(tempDir('storage-'), 'venv-0.31');
		fs.mkdirSync(target);
		const output = sink();

		await install({
			command: [python.path],
			wheel: '/wheels/w.whl',
			target,
			output
		});

		assert.deepStrictEqual(python.calls(), []);
		assert.ok(output.text.includes('already installed'), output.text);
	});

	test('removes the build when pip fails, leaving nothing behind', async () => {
		const python = fakePython('python3', { pipExit: 1 });
		const storage = tempDir('storage-');
		const target = path.join(storage, 'venv-0.31');

		await assert.rejects(
			() => install({ command: [python.path], wheel: '/wheels/w.whl', target }),
			BackendInstallError
		);

		assert.ok(!fs.existsSync(target));
		assert.deepStrictEqual(fs.readdirSync(storage), []);
	});

	test('a failed pip carries what pip said', async () => {
		const python = fakePython('python3', { pipExit: 1 });
		const target = path.join(tempDir('storage-'), 'venv-0.31');

		await assert.rejects(
			() =>
				install({
					command: [python.path],
					wheel: '/wheels/plantuml_gui-0.31.whl',
					target
				}),
			(err) => {
				assert.ok(err.message.includes('plantuml_gui-0.31.whl'), err.message);
				assert.ok(err.message.includes('no matching distribution'), err.message);
				return true;
			}
		);
	});

	test('reports a venv that could not be created', async () => {
		const python = fakePython('python3', { venvExit: 1 });
		const storage = tempDir('storage-');
		const target = path.join(storage, 'venv-0.31');

		await assert.rejects(
			() => install({ command: [python.path], wheel: '/wheels/w.whl', target }),
			(err) => {
				assert.ok(err instanceof BackendInstallError, err.constructor.name);
				assert.ok(err.message.includes('could not create venv'), err.message);
				return true;
			}
		);

		assert.deepStrictEqual(fs.readdirSync(storage), []);
	});

	test('reuses a venv that appeared while it was building', async () => {
		// The other window's install finished between the check and the claim.
		const storage = tempDir('storage-');
		const target = path.join(storage, 'venv-0.31');
		const python = fakePython('python3', { claims: target });
		const output = sink();

		await install({
			command: [python.path],
			wheel: '/wheels/w.whl',
			target,
			output
		});

		assert.ok(fs.existsSync(path.join(target, 'theirs')));
		assert.ok(output.text.includes('another window installed'), output.text);
		assert.deepStrictEqual(fs.readdirSync(storage), ['venv-0.31']);
	});

	test('hands the output to the caller as it arrives', async () => {
		const python = fakePython('python3');
		const output = sink();

		await install({
			command: [python.path],
			wheel: '/wheels/w.whl',
			target: path.join(tempDir('storage-'), 'venv-0.31'),
			output
		});

		assert.ok(output.text.includes('creating a virtual environment'), output.text);
		assert.ok(output.text.includes('Successfully installed'), output.text);
	});
});

suite('backendInstall: installing the backend', () => {
	posixOnly();

	const extension = () => extensionWith(['plantuml_gui-0.31-py3-none-any.whl']);

	/** The names the candidate list actually looks for on this platform. */
	const [first, second] = PYTHON_CANDIDATES.map((candidate) => candidate[0]);

	let savedPath;
	let storage;

	setup(() => {
		savedPath = process.env.PATH;
		storage = tempDir('storage-');
	});

	teardown(() => {
		process.env.PATH = savedPath;
	});

	test('returns the managed interpreter once one succeeds', async () => {
		const dir = extension();
		process.env.PATH = fakePython(first).dir;

		const python = await installBackend({
			extensionPath: dir,
			globalStoragePath: storage
		});

		assert.strictEqual(python, managedVenv(storage, '0.31').python);
		assert.ok(fs.existsSync(python));
	});

	test('moves on from an interpreter that is too old', async () => {
		const dir = extension();
		const working = fakePython(second);
		process.env.PATH = [
			fakeProbes({ [first]: 'probe 3 9 True True' }),
			working.dir
		].join(path.delimiter);

		const python = await installBackend({
			extensionPath: dir,
			globalStoragePath: storage
		});

		assert.strictEqual(python, managedVenv(storage, '0.31').python);
	});

	test('builds with the interpreter it chose, and only that one', async () => {
		// The install runs once, against a candidate already known to be
		// suitable, so the wheel reaches that candidate alone.
		const dir = extension();
		const chosen = fakePython(first);
		const later = fakePython(second);
		process.env.PATH = [chosen.dir, later.dir].join(path.delimiter);

		await installBackend({ extensionPath: dir, globalStoragePath: storage });

		assert.ok(
			chosen.calls().some((call) => call.includes('-m pip install')),
			chosen.calls().join('\n')
		);
		assert.deepStrictEqual(later.calls(), []);
	});

	test('does not look for an interpreter when the venv is there', async () => {
		// Resolving an already-installed backend costs a stat: nothing is
		// spawned, not even a probe.
		const dir = extension();
		const venv = managedVenv(storage, '0.31');
		fs.mkdirSync(path.dirname(venv.python), { recursive: true });
		fs.writeFileSync(venv.python, '');
		const python = fakePython(first);
		process.env.PATH = python.dir;

		const resolved = await installBackend({
			extensionPath: dir,
			globalStoragePath: storage
		});

		assert.strictEqual(resolved, venv.python);
		assert.deepStrictEqual(python.calls(), []);
	});

	test('stops at a failed install rather than trying the rest', async () => {
		// A failure that is not about the interpreter must not be reported as
		// "no Python found", and the later candidates must not run.
		const dir = extension();
		const broken = fakePython(first, { pipExit: 1 });
		const later = fakePython(second);
		process.env.PATH = [broken.dir, later.dir].join(path.delimiter);

		await assert.rejects(
			() => installBackend({ extensionPath: dir, globalStoragePath: storage }),
			(err) => {
				assert.ok(err instanceof BackendInstallError, err.constructor.name);
				assert.ok(!(err instanceof NoInterpreterError), 'wrong subclass');
				return true;
			}
		);

		assert.deepStrictEqual(later.calls(), []);
	});

	test('reports that no interpreter would do', async () => {
		const dir = extension();
		process.env.PATH = fakeProbes({ [first]: 'probe 3 9 True True' });

		await assert.rejects(
			() => installBackend({ extensionPath: dir, globalStoragePath: storage }),
			NoInterpreterError
		);
	});

	test('fails before looking for an interpreter when no wheel is bundled', async () => {
		const dir = extensionWith([]);
		const python = fakePython(first);
		process.env.PATH = python.dir;

		await assert.rejects(
			() => installBackend({ extensionPath: dir, globalStoragePath: storage }),
			BundledWheelError
		);

		assert.deepStrictEqual(python.calls(), []);
	});
});

suite('backendInstall: the candidate list', () => {
	test('tries what the platform calls its own Python first', () => {
		assert.deepStrictEqual(
			PYTHON_CANDIDATES[0],
			process.platform === 'win32' ? ['py', '-3'] : ['python3']
		);
	});

	test('can reach every version the backend supports', () => {
		// requires-python is >=3.10. On Windows `py -3` already means "the
		// newest installed", so one candidate covers them all; elsewhere a
		// machine whose python3 is older needs each tried by name.
		if (process.platform === 'win32') {
			assert.ok(PYTHON_CANDIDATES.some((c) => c[0] === 'py' && c[1] === '-3'));
			return;
		}

		for (const version of ['3.10', '3.11', '3.12', '3.13']) {
			assert.ok(
				PYTHON_CANDIDATES.some((c) => c[0] === `python${version}`),
				`python${version} is not a candidate`
			);
		}
	});

	test('leaves the Store alias out of the Windows list', () => {
		// Spawning it opens the Microsoft Store, which is a worse first run than
		// trying the next candidate.
		if (process.platform !== 'win32') {
			return;
		}

		assert.ok(!PYTHON_CANDIDATES.some((c) => c[0] === 'python3'));
	});
});

suiteTeardown(() => {
	for (const dir of temporary) {
		fs.rmSync(dir, { recursive: true, force: true });
	}
});
