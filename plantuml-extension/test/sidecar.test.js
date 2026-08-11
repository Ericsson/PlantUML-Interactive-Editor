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
	PythonConfigError,
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
		delete process.env[PYTHON_ENV];

		// The backend is a Python package no machine has by default, so an
		// interpreter found by searching almost certainly cannot import
		// plantuml_gui. Spawning one would blame the wrong thing.
		await assert.rejects(() => resolvePythonPath(), PythonConfigError);
	});

	test('the unconfigured error is still a SidecarStartError', async () => {
		// PythonConfigError is a subclass so that callers which only know about
		// the base class keep working.
		delete process.env[PYTHON_ENV];

		await assert.rejects(() => resolvePythonPath(), SidecarStartError);
	});

	test('the unconfigured error names both knobs', async () => {
		delete process.env[PYTHON_ENV];

		await assert.rejects(() => resolvePythonPath(), (err) => {
			assert.ok(err.message.includes(PYTHON_SETTING), err.message);
			assert.ok(err.message.includes(PYTHON_ENV), err.message);
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

	test('a missing package says how to install it', () => {
		const message = describeStartFailure(
			'python',
			"ModuleNotFoundError: No module named 'plantuml_gui'",
			undefined
		);

		assert.ok(message.includes('plantuml-gui'));
		assert.ok(message.includes('pip install'));
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

		await assert.rejects(port, /pip install/);
	});
});
