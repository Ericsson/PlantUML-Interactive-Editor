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

const { getWebviewContent } = require('../src/webviewContent');
const { vendorRoot } = require('../src/webviewAssets');

const EXTENSION_PATH = path.join(__dirname, '..');

const MENUS = '<div id="activity-menu"><span>menu</span></div>';

/** Stand-in for resolveWebviewAssets' output; no sidecar needed to build a page. */
const ASSETS = {
	base: 'http://127.0.0.1:9999/',
	origin: 'http://127.0.0.1:9999',
	styleHrefs: ['http://127.0.0.1:9999/static/styles.css'],
	vendorStyleUris: ['https://file%2B.vscode-resource.test/bootstrap.min.css'],
	menusHtml: MENUS
};

suite('webview content', () => {
	let html;

	suiteSetup(() => {
		// A real webview is needed only for its cspSource; the page is built and
		// the panel closed straight away. Holding one open for the whole suite
		// leaves it covering the panel that test/webviewAssets.test.js loads the
		// frontend into, which then never paints and never reports back.
		const panel = vscode.window.createWebviewPanel(
			'test.content',
			'Test',
			vscode.ViewColumn.Active,
			{ enableScripts: true, localResourceRoots: [vendorRoot(EXTENSION_PATH)] }
		);
		try {
			html = getWebviewContent({ webview: panel.webview, assets: ASSETS });
		} finally {
			panel.dispose();
		}
	});

	test('every placeholder is substituted', () => {
		// A leftover {{name}} renders as visible text in the panel, and an
		// unsubstituted {{csp}} would silently drop the policy entirely.
		assert.ok(!/\{\{\w+\}\}/.test(html), html.match(/\{\{\w+\}\}/g)?.join(', '));
	});

	test('carries a content security policy naming the sidecar', () => {
		const csp = /content="([^"]*default-src[^"]*)"/.exec(html);
		assert.ok(csp, 'no CSP meta tag');
		assert.ok(csp[1].includes(ASSETS.origin), csp[1]);
		assert.ok(csp[1].includes("default-src 'none'"), csp[1]);
	});

	test('the inline script runs under the nonce the policy grants', () => {
		// The page's own script is the only inline script, and 'unsafe-inline'
		// is deliberately absent from script-src, so a mismatch here means a
		// blank panel with a console error and nothing else.
		const nonce = /script-src 'nonce-([^']+)'/.exec(html);
		assert.ok(nonce, 'script-src does not grant a nonce');
		assert.ok(html.includes(`<script nonce="${nonce[1]}">`), 'inline script is not nonced');
	});

	test('loads the stylesheets, vendored one first', () => {
		const hrefs = [...html.matchAll(/<link rel="stylesheet" href="([^"]+)">/g)].map((m) => m[1]);

		assert.deepStrictEqual(hrefs, [...ASSETS.vendorStyleUris, ...ASSETS.styleHrefs]);
	});

	test('inlines the menu markup', () => {
		assert.ok(html.includes(MENUS), 'menu markup missing from the page');
	});

	test('supplies the diagram ids the app stylesheet targets', () => {
		// #colb and #colb-container are the web app's own ids, which is what
		// makes the stylesheet served by the sidecar apply here unchanged.
		for (const id of ['colb', 'colb-container', 'error']) {
			assert.ok(html.includes(`id="${id}"`), `missing #${id}`);
		}
	});
});
