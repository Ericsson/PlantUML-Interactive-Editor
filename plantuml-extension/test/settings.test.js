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

const settings = require('../src/settings');

suite('settings: path normalization', () => {
	test('strips surrounding whitespace', () => {
		assert.strictEqual(settings.normalizePath('  /usr/bin/python3\t'), '/usr/bin/python3');
	});

	test('strips one pair of surrounding double quotes', () => {
		// The form a path takes when copied out of a shell command.
		assert.strictEqual(settings.normalizePath('"/usr/bin/python3"'), '/usr/bin/python3');
	});

	test('strips one pair of surrounding single quotes', () => {
		assert.strictEqual(settings.normalizePath("'/usr/bin/python3'"), '/usr/bin/python3');
	});

	test('strips whitespace inside the quotes too', () => {
		assert.strictEqual(settings.normalizePath('  " /usr/bin/python3 "  '), '/usr/bin/python3');
	});

	test('leaves an unmatched quote alone', () => {
		// A half-quoted value is a mistake, and keeping the quote in the value
		// keeps it in the error message. Guessing which end to trim would hide it.
		assert.strictEqual(settings.normalizePath('"/usr/bin/python3'), '"/usr/bin/python3');
		assert.strictEqual(settings.normalizePath('\'/usr/bin/python3"'), '\'/usr/bin/python3"');
	});

	test('leaves quotes inside the path alone', () => {
		assert.strictEqual(settings.normalizePath('/opt/my "tool"/bin/java'), '/opt/my "tool"/bin/java');
	});

	test('strips only the outermost pair', () => {
		assert.strictEqual(settings.normalizePath('""/usr/bin/python3""'), '"/usr/bin/python3"');
	});

	test('yields an empty string for anything unusable', () => {
		// The callers treat '' as "not configured", so every non-value has to
		// arrive as '' rather than as undefined or a stray object.
		assert.strictEqual(settings.normalizePath(undefined), '');
		assert.strictEqual(settings.normalizePath(null), '');
		assert.strictEqual(settings.normalizePath('   '), '');
		assert.strictEqual(settings.normalizePath(42), '');
		assert.strictEqual(settings.normalizePath({}), '');
	});

	test('does not expand ~ or variables', () => {
		// VS Code does not expand these in values read with `get()`, so they
		// reach the filesystem exactly as typed.
		assert.strictEqual(settings.normalizePath('~/plantuml.jar'), '~/plantuml.jar');
		assert.strictEqual(
			settings.normalizePath('${workspaceFolder}/plantuml.jar'),
			'${workspaceFolder}/plantuml.jar'
		);
	});
});

suite('settings: isFile', () => {
	test('accepts a file that exists', () => {
		assert.strictEqual(settings.isFile(__filename), true);
	});

	test('rejects a directory', () => {
		// The distinction that matters: a directory named plantuml.jar passes an
		// existence check and then fails inside java.
		assert.strictEqual(settings.isFile(__dirname), false);
	});

	test('rejects a path that does not exist', () => {
		assert.strictEqual(settings.isFile(path.join(__dirname, 'no-such-file.jar')), false);
	});

	test('rejects an empty path without throwing', () => {
		assert.strictEqual(settings.isFile(''), false);
	});
});

suite('settings: the manifest', () => {
	const declared = require('../package.json').contributes.configuration.properties;
	const { JAR_SETTING } = require('../src/plantumlJar');
	const { PYTHON_SETTING } = require('../src/sidecar');

	test('every declared property is in the section this module owns', () => {
		// A property declared outside SECTION would never be read: both
		// resolvers only ever look in one place.
		for (const id of Object.keys(declared)) {
			assert.ok(
				id.startsWith(`${settings.SECTION}.`),
				`${id} is not under ${settings.SECTION}`
			);
		}
	});

	test('the ids the resolvers read are the ones the manifest declares', () => {
		// Both directions, so neither a rename in a resolver nor an addition to
		// the manifest can pass unnoticed. The ids come from the modules that
		// own them rather than being spelled out again here.
		assert.deepStrictEqual(
			Object.keys(declared).sort(),
			[JAR_SETTING, PYTHON_SETTING].sort()
		);
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
