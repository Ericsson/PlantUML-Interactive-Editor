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
const vscode = require('vscode');

const extension = require('../extension');

const COMMAND_ID = 'plantuml-interactive-editor.openDiagram';

suite('extension: activation', () => {
	suiteSetup(async () => {
		// Contributed commands are not in getCommands() until the extension
		// has been activated, and nothing in a test run triggers that. Find it
		// by manifest name: there is no publisher field, so the extension id is
		// not stable enough to look up directly.
		const self = vscode.extensions.all.find(
			(candidate) => candidate.packageJSON.name === 'plantuml-editor'
		);
		assert.ok(self, 'the extension under test was not loaded');
		await self.activate();
	});

	test('exports the lifecycle hooks VS Code calls', () => {
		assert.strictEqual(typeof extension.activate, 'function');
		assert.strictEqual(typeof extension.deactivate, 'function');
	});

	test('registers the declared command', async () => {
		// The manifest promises it; a rename on one side and not the other
		// leaves an entry in the palette that does nothing.
		const declared = require('../package.json').contributes.commands.map((c) => c.command);
		assert.ok(declared.includes(COMMAND_ID), `not in package.json: ${declared}`);

		const registered = await vscode.commands.getCommands(true);
		assert.ok(registered.includes(COMMAND_ID), 'command was not registered');
	});

	test('can dispatch the action offered on configuration errors', async () => {
		// The Open Settings button runs a built-in command by name; a rename or
		// a typo would leave a button that does nothing.
		const registered = await vscode.commands.getCommands(true);

		assert.ok(
			registered.includes('workbench.action.openSettings'),
			'workbench.action.openSettings is not available'
		);
	});

	test('does not render in Node', () => {
		// The single-renderer invariant: rendering happens in the sidecar, via
		// shared/render.py. A second java invocation on this side would drift
		// from the one whose SVG the backend's ~71 routes parse.
		for (const [relative, source] of readSources()) {
			assert.ok(!/spawn\(\s*['"]java['"]/.test(source), `${relative} spawns java`);
		}
	});

	test('does not build the webview page in Node', () => {
		// The single-page invariant, and the reason this extension carries no
		// copy of the frontend: serve.py renders the whole document from the
		// same templates and static files the web app uses. A document built
		// here is a document that can go stale against them.
		const fs = require('fs');
		const path = require('path');
		const root = path.join(__dirname, '..');

		for (const [relative, source] of readSources()) {
			assert.ok(!/<!DOCTYPE|<\/html>/i.test(source), `${relative} builds a document`);
		}

		const templates = fs
			.readdirSync(path.join(root, 'src'))
			.filter((name) => name.endsWith('.html'));
		assert.deepStrictEqual(templates, [], 'src/ should hold no HTML template');
	});
});

suite('extension: message protocol', () => {
	test('handles every message type the webview posts', () => {
		// The two ends live in different packages and are kept in step by
		// hand; this is the check that they still are. See "Cross-runtime
		// contracts" in docs/extension.md. It matters because the channel has
		// no acks and both handlers are if/else-if chains, so a type the page
		// posts and the host misses is dropped in silence -- the button simply
		// does nothing.
		const posted = new Set();

		for (const source of readWebviewShims()) {
			for (const [, type] of source.matchAll(/post(?:Message)?\(\{\s*type:\s*'([^']+)'/g)) {
				posted.add(type);
			}
		}

		const [, extensionSource] = readSources().find(([relative]) => relative === 'extension.js');
		const handled = new Set(
			[...extensionSource.matchAll(/message\.type === '([^']+)'/g)].map(([, type]) => type)
		);

		assert.ok(posted.has('savePng'), 'the shims no longer post savePng');
		assert.deepStrictEqual(
			[...posted].filter((type) => !handled.has(type)),
			[],
			'posted by the webview, not handled by the host'
		);
	});
});

/**
 * @returns {string[]} the contents of the webview-side shims, which live in
 *   the Python package rather than here; see the header of fetchShim.js.
 */
function readWebviewShims() {
	const fs = require('fs');
	const path = require('path');
	const shims = path.join(__dirname, '..', '..', 'src', 'plantuml_gui', 'static', 'vscode');

	return fs
		.readdirSync(shims)
		.filter((name) => name.endsWith('.js'))
		.map((name) => fs.readFileSync(path.join(shims, name), 'utf-8'));
}

/**
 * @returns {[string, string][]} every source file the extension ships, as
 *   [path relative to the extension root, contents].
 */
function readSources() {
	const fs = require('fs');
	const path = require('path');
	const root = path.join(__dirname, '..');

	return ['extension.js']
		.concat(
			fs
				.readdirSync(path.join(root, 'src'))
				.filter((name) => name.endsWith('.js'))
				.map((name) => path.join('src', name))
		)
		.map((relative) => [relative, fs.readFileSync(path.join(root, relative), 'utf-8')]);
}
