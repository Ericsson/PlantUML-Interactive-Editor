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

const assert = require('assert');
const fs = require('fs');
const { EventEmitter } = require('events');
const { PassThrough } = require('stream');
const vscode = require('vscode');

const {
	buildEnv,
	describeStartFailure,
	readPortLine,
	resolvePythonPath,
	EXPECTED_BACKEND_VERSION,
	PythonConfigError,
	BackendMissingError,
	Sidecar,
	SidecarStartError,
	PYTHON_KEY,
	PYTHON_SETTING,
	PYTHON_ENV,
	PORT_LINE_PREFIX,
	TOKEN_HEADER
} = require('../src/sidecar');
const settings = require('../src/settings');

/** A stand-in for a spawned child process, so the port handshake can be
 * driven deterministically without launching Python. */
function fakeChild() {
	const child = new EventEmitter();
	child.stdout = new PassThrough();
	child.stderr = new PassThrough();
	child.kill = () => {
		child.killed = true;
	};
	return child;
}

suite('sidecar: the contract with serve.py', () => {
	// Two constants are declared once on each side of the process boundary, so
	// only a test can hold them together. Both mismatches are invisible until
	// the backend is running: a changed prefix hangs startup for 30s, a changed
	// header turns every request into a 403.
	const servePy = require('fs').readFileSync(
		require('path').join(__dirname, '..', '..', 'src', 'plantuml_gui', 'serve.py'),
		'utf-8'
	);

	/**
	 * @param {string} name a module-level constant in serve.py
	 * @returns {string} its string literal value
	 */
	const pythonConstant = (name) => {
		const match = new RegExp(`^${name} = "([^"]*)"`, 'm').exec(servePy);
		assert.ok(match, `${name} not found in serve.py`);
		return match[1];
	};

	test('announces the port with the prefix serve.py prints', () => {
		assert.strictEqual(PORT_LINE_PREFIX, pythonConstant('PORT_LINE_PREFIX'));
	});

	test('sends the token in the header serve.py checks', () => {
		assert.strictEqual(TOKEN_HEADER, pythonConstant('TOKEN_HEADER'));
	});
});

suite('sidecar: environment', () => {
	test('passes the jar as an override, not as PLANTUML_JAR', () => {
		// shared/render.py calls load_dotenv(override=True) at import time, so
		// setting PLANTUML_JAR here would be silently beaten by a repo .env.
		const env = buildEnv('tok', '/path/to/plantuml.jar');

		assert.strictEqual(env.PLANTUML_GUI_JAR_OVERRIDE, '/path/to/plantuml.jar');
		assert.strictEqual(env.PLANTUML_GUI_TOKEN, 'tok');
	});

	test('omits the override when no jar is configured', () => {
		const env = buildEnv('tok', undefined);

		assert.ok(!('PLANTUML_GUI_JAR_OVERRIDE' in env));
	});

	test('disables Python output buffering', () => {
		// Without this the port line can sit in a block buffer, since stdout
		// is a pipe rather than a tty, and startup appears to hang.
		assert.strictEqual(buildEnv('tok').PYTHONUNBUFFERED, '1');
	});
});

suite('sidecar: version compatibility', () => {
	// Kept in step by hand with _major_minor in scripts/check_app_versions.py
	// -- the pre-commit hook's build-time half of this same rule. A test
	// reads that file's source rather than importing it, the same reasoning
	// as the PORT_LINE_PREFIX/TOKEN_HEADER contract tests above: a Python
	// script and a Node module cannot share a definition, only agree by hand.
	const checkAppVersionsPy = require('fs').readFileSync(
		require('path').join(__dirname, '..', '..', 'scripts', 'check_app_versions.py'),
		'utf-8'
	);

	test('expects the backend at this extension\'s major.minor', () => {
		// The patch component is free -- an extension-only fix can ship as
		// 0.31.1 against the same 0.31 backend -- so it is dropped here rather
		// than compared.
		const [major, minor] = require('../package.json').version.split('.');

		assert.strictEqual(EXPECTED_BACKEND_VERSION, `${major}.${minor}`);
	});

	test('applies the same major.minor rule as check_app_versions.py', () => {
		// Read _major_minor's own behaviour off the source: patch components
		// split off and ignored, same as the expected version here.
		assert.ok(
			/version\.split\(["']\.["']\)/.test(checkAppVersionsPy),
			'check_app_versions.py no longer splits on "." the way this test assumes'
		);
		assert.ok(
			checkAppVersionsPy.includes('components[0]') &&
				checkAppVersionsPy.includes('components[1]'),
			'check_app_versions.py no longer takes the first two components'
		);
	});
});

suite('sidecar: interpreter resolution', () => {
	const original = process.env[PYTHON_ENV];
	let restoreFs;

	/**
	 * Make `paths` the only files on disk for the duration of a test.
	 *
	 * @param {string[]} paths
	 * @param {string[]} [directories] paths that exist but are not files
	 */
	function stubFilesystem(paths, directories = []) {
		const originalStat = fs.statSync;

		fs.statSync = (candidate) => {
			if (paths.includes(candidate)) {
				return { isFile: () => true };
			}
			if (directories.includes(candidate)) {
				return { isFile: () => false };
			}
			const err = new Error(`ENOENT: ${candidate}`);
			err.code = 'ENOENT';
			throw err;
		};

		restoreFs = () => {
			fs.statSync = originalStat;
		};
	}

	/**
	 * @param {string|undefined} value
	 * @returns {Promise<() => Promise<void>>} a restore function
	 */
	async function setPythonSetting(value) {
		const target = vscode.workspace.getConfiguration(settings.SECTION);
		await target.update(PYTHON_KEY, value, vscode.ConfigurationTarget.Global);
		return async () => {
			await target.update(PYTHON_KEY, undefined, vscode.ConfigurationTarget.Global);
		};
	}

	teardown(() => {
		restoreFs?.();
		restoreFs = undefined;
		if (original === undefined) {
			delete process.env[PYTHON_ENV];
		} else {
			process.env[PYTHON_ENV] = original;
		}
	});

	test('the setting wins over PLANTUML_GUI_PYTHON', async () => {
		stubFilesystem(['/configured/python', '/env/python']);
		process.env[PYTHON_ENV] = '/env/python';

		const restore = await setPythonSetting('/configured/python');
		try {
			assert.strictEqual(await resolvePythonPath(), '/configured/python');
		} finally {
			await restore();
		}
	});

	test('honours PLANTUML_GUI_PYTHON when the setting is unset', async () => {
		// The Extension Development Host launches with no folder open, so
		// workspace settings are not read; the env var is how launch.json
		// configures development.
		stubFilesystem(['/custom/python']);
		process.env[PYTHON_ENV] = '/custom/python';

		assert.strictEqual(await resolvePythonPath(), '/custom/python');
	});

	test('throws instead of guessing when nothing is configured', async () => {
		// Nothing on disk, including the standard venv: PATH is deliberately
		// not searched, because the backend is a Python package no machine has
		// by default. An interpreter found that way almost certainly cannot
		// import plantuml_gui, and spawning it would blame the wrong thing.
		stubFilesystem([]);
		delete process.env[PYTHON_ENV];

		await assert.rejects(() => resolvePythonPath(), PythonConfigError);
	});

	test('the unconfigured error is still a SidecarStartError', async () => {
		// PythonConfigError is a subclass so that callers which only know about
		// the base class keep working.
		stubFilesystem([]);
		delete process.env[PYTHON_ENV];

		await assert.rejects(() => resolvePythonPath(), SidecarStartError);
	});

	test('the unconfigured error names both knobs', async () => {
		stubFilesystem([]);
		delete process.env[PYTHON_ENV];

		await assert.rejects(() => resolvePythonPath(), (err) => {
			assert.ok(err.message.includes(PYTHON_SETTING), err.message);
			assert.ok(err.message.includes(PYTHON_ENV), err.message);
			return true;
		});
	});

	test('the managed venv is used when nothing is configured', async () => {
		// The ordinary path for anyone who only installed the vsix: the venv the
		// extension built for itself, passed in by ensureBackendPython.
		stubFilesystem(['/storage/venv-0.31/bin/python']);
		delete process.env[PYTHON_ENV];

		assert.strictEqual(
			await resolvePythonPath({ managedPython: '/storage/venv-0.31/bin/python' }),
			'/storage/venv-0.31/bin/python'
		);
	});

	test('the setting wins over the managed venv', async () => {
		stubFilesystem(['/configured/python', '/storage/venv-0.31/bin/python']);
		delete process.env[PYTHON_ENV];

		const restore = await setPythonSetting('/configured/python');
		try {
			assert.strictEqual(
				await resolvePythonPath({ managedPython: '/storage/venv-0.31/bin/python' }),
				'/configured/python'
			);
		} finally {
			await restore();
		}
	});

	test('the environment variable wins over the managed venv', async () => {
		stubFilesystem(['/env/python', '/storage/venv-0.31/bin/python']);
		process.env[PYTHON_ENV] = '/env/python';

		assert.strictEqual(
			await resolvePythonPath({ managedPython: '/storage/venv-0.31/bin/python' }),
			'/env/python'
		);
	});

	test('nothing installed at all asks for an install, not for Settings', async () => {
		// BackendMissingError is what extension.js answers by installing the
		// bundled wheel; every other resolution failure is the user's to fix.
		stubFilesystem([]);
		delete process.env[PYTHON_ENV];

		await assert.rejects(
			() => resolvePythonPath({ managedPython: '/storage/venv-0.31/bin/python' }),
			BackendMissingError
		);
	});

	test('a bad setting is not answered by installing', async () => {
		stubFilesystem([]);
		delete process.env[PYTHON_ENV];

		const restore = await setPythonSetting('/typo/python');
		try {
			await assert.rejects(
				() => resolvePythonPath({ managedPython: '/storage/venv-0.31/bin/python' }),
				(err) => {
					assert.ok(err instanceof PythonConfigError, err.constructor.name);
					assert.ok(!(err instanceof BackendMissingError), 'wrong subclass');
					return true;
				}
			);
		} finally {
			await restore();
		}
	});

	test('a bad environment variable does not fall through to the managed venv', async () => {
		// Same rule as every other source: set but unusable stops resolution,
		// so a typo cannot be masked by a working fallback.
		stubFilesystem(['/storage/venv-0.31/bin/python']);
		process.env[PYTHON_ENV] = '/typo/python';

		await assert.rejects(
			() => resolvePythonPath({ managedPython: '/storage/venv-0.31/bin/python' }),
			PythonConfigError
		);
	});

	test('the not-found message says where a backend comes from', async () => {
		// Only reachable with no wheel bundled, since a bundled one is
		// installed instead; so the fix is to build one, or to name your own.
		stubFilesystem([]);
		delete process.env[PYTHON_ENV];

		await assert.rejects(() => resolvePythonPath(), (err) => {
			assert.ok(err.message.includes('build_release.sh'), err.message);
			assert.ok(err.message.includes(PYTHON_SETTING), err.message);
			return true;
		});
	});

	test('rejects a configured interpreter that does not exist, before spawning', async () => {
		// The check belongs ahead of the spawn so the report names the knob,
		// rather than arriving as an ENOENT once a panel is waiting on a child.
		stubFilesystem([]);
		delete process.env[PYTHON_ENV];

		const restore = await setPythonSetting('/typo/python');
		try {
			await assert.rejects(() => resolvePythonPath(), (err) => {
				assert.ok(err instanceof PythonConfigError, err.constructor.name);
				assert.ok(err.message.includes('/typo/python'), err.message);
				assert.ok(err.message.includes(PYTHON_SETTING), err.message);
				return true;
			});
		} finally {
			await restore();
		}
	});

	test('rejects an interpreter path that is a directory', async () => {
		stubFilesystem([], ['/usr/bin']);
		delete process.env[PYTHON_ENV];

		const restore = await setPythonSetting('/usr/bin');
		try {
			await assert.rejects(() => resolvePythonPath(), PythonConfigError);
		} finally {
			await restore();
		}
	});

	test('a bad setting does not fall through to a working env var', async () => {
		stubFilesystem(['/env/python']);
		process.env[PYTHON_ENV] = '/env/python';

		const restore = await setPythonSetting('/typo/python');
		try {
			await assert.rejects(() => resolvePythonPath(), PythonConfigError);
		} finally {
			await restore();
		}
	});

	test('names the environment variable when that is the bad source', async () => {
		stubFilesystem([]);
		process.env[PYTHON_ENV] = '/typo/python';

		await assert.rejects(() => resolvePythonPath(), (err) => {
			assert.ok(err.message.includes(PYTHON_ENV), err.message);
			return true;
		});
	});

	test('a quoted, padded setting value resolves', async () => {
		// What lands in settings.json when a path is pasted out of a shell.
		stubFilesystem(['/usr/bin/python3']);
		delete process.env[PYTHON_ENV];

		const restore = await setPythonSetting('  "/usr/bin/python3"  ');
		try {
			assert.strictEqual(await resolvePythonPath(), '/usr/bin/python3');
		} finally {
			await restore();
		}
	});
});

suite('sidecar: startup failure messages', () => {
	test('a missing interpreter names the setting to fix', () => {
		const message = describeStartFailure('py3', '', { code: 'ENOENT' });

		assert.ok(message.includes('py3'));
		assert.ok(message.includes(PYTHON_SETTING));
	});

	test('a missing package blames the interpreter that was named', () => {
		// Only reachable through a configured interpreter, the managed venv
		// having the package installed into it by construction. So the fix is
		// that setting: point it somewhere else, or stop pointing it anywhere.
		const message = describeStartFailure(
			'python',
			"ModuleNotFoundError: No module named 'plantuml_gui'",
			undefined
		);

		assert.ok(message.includes('plantuml-gui'));
		assert.ok(message.includes('"python"'), message);
		assert.ok(message.includes(PYTHON_SETTING), message);
	});

	test('any other failure surfaces the sidecar stderr', () => {
		const message = describeStartFailure('python', 'Traceback: boom', undefined);

		assert.ok(message.includes('Traceback: boom'));
	});
});

suite('sidecar: port handshake', () => {
	test('reads the port from the announcement line', async () => {
		const child = fakeChild();
		const port = readPortLine(child, 'python', () => '');

		child.stdout.write(`${PORT_LINE_PREFIX}54321\n`);

		assert.strictEqual(await port, 54321);
	});

	test('ignores output printed before the port line', async () => {
		// Regression guard: puml_encoder.py used to print at import time, so
		// reading only the first line of stdout picked up debug output and the
		// handshake failed. Scan, do not assume line 1.
		const child = fakeChild();
		const port = readPortLine(child, 'python', () => '');

		child.stdout.write('Bob -> Alice : hello\n');
		child.stdout.write('some other noise\n');
		child.stdout.write(`${PORT_LINE_PREFIX}54321\n`);

		assert.strictEqual(await port, 54321);
	});

	test('tolerates the line arriving split across chunks', async () => {
		const child = fakeChild();
		const port = readPortLine(child, 'python', () => '');

		child.stdout.write(`${PORT_LINE_PREFIX}54`);
		child.stdout.write('3');
		child.stdout.write('21\n');

		assert.strictEqual(await port, 54321);
	});

	test('does not accept an incomplete line as a port', async () => {
		// "5432" with no newline could be the first half of 54321.
		const child = fakeChild();
		let settled = false;
		readPortLine(child, 'python', () => '').then(
			() => {
				settled = true;
			},
			() => {
				settled = true;
			}
		);

		child.stdout.write(`${PORT_LINE_PREFIX}5432`);
		await new Promise((resolve) => setImmediate(resolve));

		assert.strictEqual(settled, false, 'resolved before the line was complete');
	});

	test('rejects with an actionable message when the child cannot spawn', async () => {
		const child = fakeChild();
		const port = readPortLine(child, 'nonexistent-python', () => '');

		child.emit('error', Object.assign(new Error('spawn failed'), { code: 'ENOENT' }));

		await assert.rejects(port, /nonexistent-python/);
	});

	test('rejects when the child exits before reporting a port', async () => {
		const child = fakeChild();
		const port = readPortLine(
			child,
			'python',
			() => "ModuleNotFoundError: No module named 'plantuml_gui'"
		);

		child.emit('exit', 1);

		await assert.rejects(port, /does not have the plantuml-gui package/);
	});
});

suite('sidecar: telling a stop we asked for from a death', () => {
	// The child's `exit` event is the same event either way, so whoever listens
	// needs this flag to know whether to report it: killing the backend in
	// deactivate() must not raise an error notification on the way out, and a
	// backend that died on its own must not pass for an orderly stop.
	const liveChild = () => Object.assign(fakeChild(), { exitCode: null, signalCode: null });

	test('is not marked while running', () => {
		assert.strictEqual(new Sidecar(liveChild(), 1234, 'token').disposing, false);
	});

	test('marks a stop before killing, so the exit handler cannot miss it', () => {
		const child = liveChild();
		let markedAtKill;
		const sidecar = new Sidecar(child, 1234, 'token');
		child.kill = () => {
			markedAtKill = sidecar.disposing;
		};

		sidecar.dispose();

		assert.strictEqual(markedAtKill, true, 'killed before the stop was marked');
		assert.strictEqual(sidecar.disposing, true);
	});

	test('leaves a child killed from outside unmarked', () => {
		// The reproducer for the bug this flag exists to keep fixed: `kill
		// <pid>` from a terminal. Nothing called dispose, so the exit is a
		// failure to report.
		const child = liveChild();
		const sidecar = new Sidecar(child, 1234, 'token');

		child.emit('exit', null, 'SIGTERM');

		assert.strictEqual(sidecar.disposing, false);
	});
});

suite('sidecar: waiting for the child to actually go', () => {
	// What the reinstall needs on top of dispose(): kill() returns as soon as
	// the signal is sent, and the venv about to be deleted is the directory the
	// child's own interpreter is running out of. Windows refuses to unlink a
	// running executable's image, so deleting straight after the kill fails
	// there -- and the reinstall then installs over a venv that never went.
	const liveChild = () => Object.assign(fakeChild(), { exitCode: null, signalCode: null });

	test('resolves once the child has exited', async () => {
		const child = liveChild();
		const sidecar = new Sidecar(child, 1234, 'token');

		const stopped = sidecar.stop(1000);
		child.emit('exit', 0);

		assert.strictEqual(await stopped, true);
		assert.strictEqual(child.killed, true, 'the child was never killed');
		assert.strictEqual(sidecar.disposing, true, 'the stop was not marked as ours');
	});

	test('does not report a child gone while it is still running', async () => {
		const child = liveChild();
		const sidecar = new Sidecar(child, 1234, 'token');
		let settled = false;

		sidecar.stop(1000).then(() => {
			settled = true;
		});
		await new Promise((resolve) => setImmediate(resolve));

		assert.strictEqual(settled, false, 'resolved before the child had exited');
	});

	test('gives up rather than waiting forever on a child that will not go', async () => {
		// A child that ignores the signal must not hang the command in silence;
		// the caller is told, and decides what to do about it.
		const child = liveChild();
		const sidecar = new Sidecar(child, 1234, 'token');

		assert.strictEqual(await sidecar.stop(10), false);
	});

	test('an already-dead child needs no wait, and no second kill', async () => {
		const child = Object.assign(fakeChild(), { exitCode: 0, signalCode: null });
		const sidecar = new Sidecar(child, 1234, 'token');

		assert.strictEqual(await sidecar.stop(10), true);
		assert.strictEqual(child.killed, undefined, 'killed a child that had already exited');
		assert.strictEqual(sidecar.disposing, true);
	});
});
