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
const path = require('path');
const vscode = require('vscode');

const config = require('../src/config');

suite('config: path normalization', () => {
	test('strips surrounding whitespace', () => {
		assert.strictEqual(config.normalizePath('  /usr/bin/python3\t'), '/usr/bin/python3');
	});

	test('strips one pair of surrounding double quotes', () => {
		// The form a path takes when copied out of a shell command.
		assert.strictEqual(config.normalizePath('"/usr/bin/python3"'), '/usr/bin/python3');
	});

	test('strips one pair of surrounding single quotes', () => {
		assert.strictEqual(config.normalizePath("'/usr/bin/python3'"), '/usr/bin/python3');
	});

	test('strips whitespace inside the quotes too', () => {
		assert.strictEqual(config.normalizePath('  " /usr/bin/python3 "  '), '/usr/bin/python3');
	});

	test('leaves an unmatched quote alone', () => {
		// A half-quoted value is a mistake, and keeping the quote in the value
		// keeps it in the error message. Guessing which end to trim would hide it.
		assert.strictEqual(config.normalizePath('"/usr/bin/python3'), '"/usr/bin/python3');
		assert.strictEqual(config.normalizePath('\'/usr/bin/python3"'), '\'/usr/bin/python3"');
	});

	test('leaves quotes inside the path alone', () => {
		assert.strictEqual(config.normalizePath('/opt/my "tool"/bin/java'), '/opt/my "tool"/bin/java');
	});

	test('strips only the outermost pair', () => {
		assert.strictEqual(config.normalizePath('""/usr/bin/python3""'), '"/usr/bin/python3"');
	});

	test('yields an empty string for anything unusable', () => {
		// The callers treat '' as "not configured", so every non-value has to
		// arrive as '' rather than as undefined or a stray object.
		assert.strictEqual(config.normalizePath(undefined), '');
		assert.strictEqual(config.normalizePath(null), '');
		assert.strictEqual(config.normalizePath('   '), '');
		assert.strictEqual(config.normalizePath(42), '');
		assert.strictEqual(config.normalizePath({}), '');
	});

	test('does not expand ~ or variables', () => {
		// VS Code does not expand these in values read with `get()`, so they
		// reach the filesystem exactly as typed.
		assert.strictEqual(config.normalizePath('~/plantuml.jar'), '~/plantuml.jar');
		assert.strictEqual(
			config.normalizePath('${workspaceFolder}/plantuml.jar'),
			'${workspaceFolder}/plantuml.jar'
		);
	});
});

suite('config: isFile', () => {
	test('accepts a file that exists', () => {
		assert.strictEqual(config.isFile(__filename), true);
	});

	test('rejects a directory', () => {
		// The distinction that matters: a directory named plantuml.jar passes an
		// existence check and then fails inside java.
		assert.strictEqual(config.isFile(__dirname), false);
	});

	test('rejects a path that does not exist', () => {
		assert.strictEqual(config.isFile(path.join(__dirname, 'no-such-file.jar')), false);
	});

	test('rejects an empty path without throwing', () => {
		assert.strictEqual(config.isFile(''), false);
	});
});

suite('config: setting ids', () => {
	const declared = require('../package.json').contributes.configuration.properties;

	test('every declared property is in the section this module owns', () => {
		// A property declared outside SECTION would never be read: readSetting
		// only ever looks in one place.
		for (const id of Object.keys(declared)) {
			assert.ok(
				id.startsWith(`${config.SECTION}.`),
				`${id} is not under ${config.SECTION}`
			);
		}
	});

	test('the ids this module exposes are the ones the manifest declares', () => {
		// Both directions, so neither a rename here nor an addition there can
		// pass unnoticed.
		assert.deepStrictEqual(
			Object.keys(declared).sort(),
			[config.JAR_SETTING, config.PYTHON_SETTING].sort()
		);
	});

	test('the dotted ids agree with the section and keys used to read them', () => {
		assert.strictEqual(config.JAR_SETTING, `${config.SECTION}.${config.JAR_KEY}`);
		assert.strictEqual(config.PYTHON_SETTING, `${config.SECTION}.${config.PYTHON_KEY}`);
	});

	test('both settings are machine-overridable', () => {
		// These are absolute paths to things installed on one machine. At the
		// default `window` scope they ride Settings Sync to machines where they
		// mean nothing, and land in a repo's .vscode/settings.json for coworkers
		// whose interpreter is somewhere else.
		for (const [id, property] of Object.entries(declared)) {
			assert.strictEqual(property.scope, 'machine-overridable', id);
		}
	});

	test('both settings describe themselves in the Settings UI', () => {
		for (const [id, property] of Object.entries(declared)) {
			assert.ok(property.markdownDescription, `${id} has no markdownDescription`);
			assert.ok(typeof property.order === 'number', `${id} has no order`);
		}
	});
});

suite('config: readSetting', () => {
	test('returns a normalized value', async () => {
		// End to end through the real configuration API: normalization is only
		// useful if it happens on the way out of it.
		const target = vscode.workspace.getConfiguration(config.SECTION);
		await target.update(config.PYTHON_KEY, '  "/usr/bin/python3"  ', vscode.ConfigurationTarget.Global);

		try {
			assert.strictEqual(config.readSetting(config.PYTHON_KEY), '/usr/bin/python3');
		} finally {
			await target.update(config.PYTHON_KEY, undefined, vscode.ConfigurationTarget.Global);
		}
	});

	test('returns an empty string when the setting is unset', () => {
		assert.strictEqual(config.readSetting(config.PYTHON_KEY), '');
	});
});

suite('config: readEnv', () => {
	let original;

	setup(() => {
		original = process.env[config.PYTHON_ENV];
	});

	teardown(() => {
		if (original === undefined) {
			delete process.env[config.PYTHON_ENV];
		} else {
			process.env[config.PYTHON_ENV] = original;
		}
	});

	test('normalizes like a setting does', () => {
		// A .env file or a launch.json env block is just as likely to carry a
		// quoted path as the Settings UI is.
		process.env[config.PYTHON_ENV] = '"/usr/bin/python3" ';
		assert.strictEqual(config.readEnv(config.PYTHON_ENV), '/usr/bin/python3');
	});

	test('returns an empty string when unset', () => {
		delete process.env[config.PYTHON_ENV];
		assert.strictEqual(config.readEnv(config.PYTHON_ENV), '');
	});
});
