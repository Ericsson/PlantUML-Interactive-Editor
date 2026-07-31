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
const { EventEmitter } = require('events');
const { PassThrough } = require('stream');

const {
	buildEnv,
	describeStartFailure,
	readPortLine,
	resolvePythonPath,
	SidecarStartError,
	PORT_LINE_PREFIX
} = require('../src/sidecar');

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
	const original = process.env.PLANTUML_GUI_PYTHON;

	teardown(() => {
		if (original === undefined) {
			delete process.env.PLANTUML_GUI_PYTHON;
		} else {
			process.env.PLANTUML_GUI_PYTHON = original;
		}
	});

	test('honours PLANTUML_GUI_PYTHON', async () => {
		// The Extension Development Host launches with no folder open, so
		// workspace settings are not read; the env var is how launch.json
		// configures development.
		process.env.PLANTUML_GUI_PYTHON = '/custom/python';

		assert.strictEqual(await resolvePythonPath(), '/custom/python');
	});

	test('throws instead of guessing when nothing is configured', async () => {
		delete process.env.PLANTUML_GUI_PYTHON;

		// The backend is a Python package no machine has by default, so an
		// interpreter found by searching almost certainly cannot import
		// plantuml_gui. Spawning one would blame the wrong thing.
		await assert.rejects(() => resolvePythonPath(), SidecarStartError);
	});

	test('the unconfigured error names both knobs', async () => {
		delete process.env.PLANTUML_GUI_PYTHON;

		await assert.rejects(() => resolvePythonPath(), (err) => {
			assert.ok(err.message.includes('plantumlInteractive.pythonPath'), err.message);
			assert.ok(err.message.includes('PLANTUML_GUI_PYTHON'), err.message);
			return true;
		});
	});
});

suite('sidecar: startup failure messages', () => {
	test('a missing interpreter names the setting to fix', () => {
		const message = describeStartFailure('py3', '', { code: 'ENOENT' });

		assert.ok(message.includes('py3'));
		assert.ok(message.includes('plantumlInteractive.pythonPath'));
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
