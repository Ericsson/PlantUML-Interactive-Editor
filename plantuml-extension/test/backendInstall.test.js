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
// No Python is installed by any of these. The candidate loop is driven by fake
// interpreters -- shell scripts on a PATH of this suite's own making, each
// exiting with the code the real installer would use -- which is what makes
// "too old, try the next" and "a real failure, stop" testable in milliseconds
// and without a network.

const assert = require('assert');
const fs = require('fs');
const os = require('os');
const path = require('path');

const {
	bundledWheel,
	managedVenv,
	venvInterpreter,
	installBackend,
	runInstaller,
	BundledWheelError,
	BackendInstallError,
	NoInterpreterError,
	BACKEND_DIR,
	VENV_PREFIX,
	PYTHON_CANDIDATES,
	INSTALLER_MODULE,
	EXIT_UNSUITABLE_INTERPRETER,
	EXIT_FAILED
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
 * A directory to put on PATH, holding stand-ins for interpreters.
 *
 * Each stand-in echoes its arguments and exits with the code it was given. One
 * exiting 0 also creates the interpreter inside `--target`, because that is what
 * a real install leaves behind and what installBackend checks for.
 *
 * Written in the platform's own script language so the suite runs wherever the
 * extension does.
 *
 * @param {Record<string, number>} exits stand-in name to the exit code it
 *   should produce
 * @returns {string} the directory
 */
function fakeInterpreters(exits) {
	const dir = tempDir('bin-');

	for (const [name, code] of Object.entries(exits)) {
		const succeeds = code === 0;

		if (process.platform === 'win32') {
			fs.writeFileSync(
				path.join(dir, `${name}.cmd`),
				'@echo off\r\n' +
					'echo %0 ran with: %* 1>&2\r\n' +
					// The venv the installer would have built; --target is the
					// last argument this is called with.
					(succeeds
						? 'for %%a in (%*) do set LAST=%%a\r\n' +
							'mkdir "%LAST%\\Scripts" 2>nul\r\n' +
							'type nul > "%LAST%\\Scripts\\python.exe"\r\n'
						: '') +
					`exit /b ${code}\r\n`
			);
			continue;
		}

		const script = path.join(dir, name);
		fs.writeFileSync(
			script,
			'#!/bin/sh\n' +
				'echo "$0 ran with: $*" >&2\n' +
				// The venv the installer would have built. --target is passed
				// last, so the last argument is where it goes. mkdir by absolute
				// path: PATH holds this directory alone while a test runs.
				(succeeds
					? 'for a in "$@"; do last="$a"; done\n' +
						'/bin/mkdir -p "$last/bin" && : > "$last/bin/python"\n'
					: '') +
				`exit ${code}\n`
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
		// Windows keeps it in Scripts and gives it an extension. install_venv.py
		// makes the same choice; test_install_venv.py checks it from that side.
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

suite('backendInstall: the contract with install_venv.py', () => {
	const installerPy = fs.readFileSync(
		path.join(
			__dirname,
			'..',
			'..',
			'src',
			'plantuml_gui',
			'install_venv.py'
		),
		'utf-8'
	);

	test('names the module it runs', () => {
		// The dotted path the extension spawns has to be the module's own.
		assert.strictEqual(INSTALLER_MODULE, 'plantuml_gui.install_venv');
		assert.ok(installerPy.includes('python -m plantuml_gui.install_venv'));
	});

	test('agrees on the exit code that means "try the next interpreter"', () => {
		const declared = /^EXIT_UNSUITABLE_INTERPRETER = (\d+)$/m.exec(installerPy);

		assert.ok(declared, 'install_venv.py does not declare the exit code');
		assert.strictEqual(EXIT_UNSUITABLE_INTERPRETER, Number(declared[1]));
	});

	test('agrees on the exit code that means "the install failed"', () => {
		// The one that stops the search. Every other unexpected code is read as
		// "that was not a Python", so this constant is what separates a broken
		// install from a candidate to move on from.
		const declared = /^EXIT_FAILED = (\d+)$/m.exec(installerPy);

		assert.ok(declared, 'install_venv.py does not declare the exit code');
		assert.strictEqual(EXIT_FAILED, Number(declared[1]));
	});

	test('passes the arguments the installer requires', () => {
		assert.ok(installerPy.includes('"--wheel"'), 'no --wheel argument');
		assert.ok(installerPy.includes('"--target"'), 'no --target argument');
	});

	test('the package is importable from a zip, which the installer needs', () => {
		// zipimport finds regular packages inside a wheel but not namespace
		// packages, and the installer is run straight out of the wheel.
		const packageInit = path.join(
			__dirname,
			'..',
			'..',
			'src',
			'plantuml_gui',
			'__init__.py'
		);

		assert.ok(fs.existsSync(packageInit), `${packageInit} must exist`);
	});
});

suite('backendInstall: running the installer', () => {
	test('reports the exit code the interpreter gave', async () => {
		const bin = fakeInterpreters({ py: 7 });

		const result = await runInstaller([path.join(bin, 'py')], {
			wheel: '/wheels/w.whl',
			target: '/storage/venv-0.31'
		});

		assert.strictEqual(result.code, 7);
		assert.strictEqual(result.spawned, true);
	});

	test('reports an interpreter that is not there without throwing', async () => {
		const result = await runInstaller(['/nonexistent/python3'], {
			wheel: '/wheels/w.whl',
			target: '/storage/venv-0.31'
		});

		assert.strictEqual(result.spawned, false);
	});

	test('passes the wheel and the target through', async () => {
		const bin = fakeInterpreters({ py: 0 });
		const target = tempDir('target-');

		const result = await runInstaller([path.join(bin, 'py')], {
			wheel: '/wheels/w.whl',
			target
		});

		assert.ok(result.output.includes('-m plantuml_gui.install_venv'), result.output);
		assert.ok(result.output.includes('--wheel /wheels/w.whl'), result.output);
		assert.ok(result.output.includes(`--target ${target}`), result.output);
	});

	test('hands the installer output to the caller as it arrives', async () => {
		const bin = fakeInterpreters({ py: 0 });
		let seen = '';

		await runInstaller([path.join(bin, 'py')], {
			wheel: '/wheels/w.whl',
			target: tempDir('target-'),
			output: { append: (text) => (seen += text) }
		});

		assert.ok(seen.includes('ran with'), seen);
	});
});

suite('backendInstall: launching through a prefix', () => {
	test('passes the prefix before the module, as py -3 needs', () => {
		// The Windows launcher takes the version as an argument, so a candidate
		// is an argv prefix rather than a name.
		const bin = fakeInterpreters({ launcher: 0 });

		return runInstaller([path.join(bin, 'launcher'), '-3'], {
			wheel: '/wheels/w.whl',
			target: tempDir('target-')
		}).then((result) => {
			assert.ok(
				/-3 -m plantuml_gui\.install_venv/.test(result.output),
				result.output
			);
		});
	});
});

suite('backendInstall: choosing an interpreter', () => {
	const extension = () => extensionWith(['plantuml_gui-0.31-py3-none-any.whl']);

	/** The names the candidate list actually looks for on this platform. */
	const [first, second] = PYTHON_CANDIDATES.map((candidate) => candidate[0]);

	let savedPath;
	let storage;

	setup(() => {
		savedPath = process.env.PATH;
		// A real directory, because installBackend now checks that a candidate
		// claiming success left an interpreter behind.
		storage = tempDir('storage-');
	});

	teardown(() => {
		process.env.PATH = savedPath;
	});

	test('returns the managed interpreter once one succeeds', async () => {
		const dir = extension();
		process.env.PATH = fakeInterpreters({ [first]: 0 });

		const python = await installBackend({
			extensionPath: dir,
			globalStoragePath: storage
		});

		assert.strictEqual(python, managedVenv(storage, '0.31').python);
	});

	test('moves on from an interpreter that reports itself too old', async () => {
		const dir = extension();
		process.env.PATH = fakeInterpreters({
			[first]: EXIT_UNSUITABLE_INTERPRETER,
			[second]: 0
		});

		const python = await installBackend({
			extensionPath: dir,
			globalStoragePath: storage
		});

		assert.strictEqual(python, managedVenv(storage, '0.31').python);
	});

	test('moves on from a candidate that is not installed', async () => {
		// The ordinary case: most of the list is absent on any given machine.
		const dir = extension();
		process.env.PATH = fakeInterpreters({ [second]: 0 });

		const python = await installBackend({
			extensionPath: dir,
			globalStoragePath: storage
		});

		assert.strictEqual(python, managedVenv(storage, '0.31').python);
	});

	test('moves on from something that answers but is not a Python', async () => {
		// The Microsoft Store alias named python3 on Windows, or a shell
		// reporting 9009: it runs, so it is not a missing command, and it is not
		// a failed install either. The next candidate gets its turn.
		const dir = extension();
		process.env.PATH = fakeInterpreters({ [first]: 9009, [second]: 0 });

		const python = await installBackend({
			extensionPath: dir,
			globalStoragePath: storage
		});

		assert.strictEqual(python, managedVenv(storage, '0.31').python);
	});

	test('moves on from one that claims success and installs nothing', async () => {
		// Belt and braces for the same class of impostor: exit 0 is only
		// believed if the interpreter it should have built is there.
		const dir = extension();
		const liar = tempDir('bin-');
		fs.writeFileSync(path.join(liar, first), '#!/bin/sh\nexit 0\n');
		fs.chmodSync(path.join(liar, first), 0o755);
		const working = fakeInterpreters({ [second]: 0 });
		process.env.PATH = `${liar}${path.delimiter}${working}`;

		const python = await installBackend({
			extensionPath: dir,
			globalStoragePath: storage
		});

		assert.strictEqual(python, managedVenv(storage, '0.31').python);
	});

	test('stops at a failed install rather than trying the rest', async () => {
		// A failure that is not about the interpreter must not be reported as
		// "no Python found", and the later candidates must not run.
		const dir = extension();
		process.env.PATH = fakeInterpreters({ [first]: EXIT_FAILED, [second]: 0 });

		await assert.rejects(
			() => installBackend({ extensionPath: dir, globalStoragePath: storage }),
			(err) => {
				assert.ok(err instanceof BackendInstallError, err.constructor.name);
				assert.ok(!(err instanceof NoInterpreterError), 'wrong subclass');
				return true;
			}
		);
	});

	test('a failed install carries what the installer said', async () => {
		const dir = extension();
		process.env.PATH = fakeInterpreters({ [first]: EXIT_FAILED });

		await assert.rejects(
			() => installBackend({ extensionPath: dir, globalStoragePath: storage }),
			(err) => {
				assert.ok(err.message.includes('ran with'), err.message);
				return true;
			}
		);
	});

	test('reports every candidate when none will do', async () => {
		const dir = extension();
		process.env.PATH = fakeInterpreters({ [first]: EXIT_UNSUITABLE_INTERPRETER });

		await assert.rejects(
			() => installBackend({ extensionPath: dir, globalStoragePath: storage }),
			(err) => {
				assert.ok(err instanceof NoInterpreterError, err.constructor.name);
				assert.ok(err.message.includes(`${first}: too old`), err.message);
				assert.ok(err.message.includes(`${second}: not found`), err.message);
				return true;
			}
		);
	});

	test('the message says what the user can do about it', async () => {
		const dir = extension();
		process.env.PATH = fakeInterpreters({});

		await assert.rejects(
			() => installBackend({ extensionPath: dir, globalStoragePath: storage }),
			(err) => {
				assert.ok(err.message.includes('3.10 or newer'), err.message);
				assert.ok(err.message.includes('plantumlInteractive.pythonPath'), err.message);
				return true;
			}
		);
	});

	test('fails before looking for an interpreter when no wheel is bundled', async () => {
		const dir = extensionWith([]);
		process.env.PATH = fakeInterpreters({ [first]: 0 });

		await assert.rejects(
			() => installBackend({ extensionPath: dir, globalStoragePath: storage }),
			BundledWheelError
		);
	});

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
