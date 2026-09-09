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
const http = require('http');
const path = require('path');
const vscode = require('vscode');

const {
	fetchWebviewPage,
	vendorRoot,
	WebviewPageError,
	VENDOR_SCRIPTS,
	VENDOR_STYLES,
	WEBVIEW_PATH
} = require('../src/webviewPage');
const { TOKEN_HEADER } = require('../src/sidecar');

const EXTENSION_PATH = path.join(__dirname, '..');

const TOKEN = 'test-token';

const PAGE_BODY = '<!DOCTYPE html><html><body>rendered by the sidecar</body></html>';

/**
 * A stand-in for the sidecar. It does not render anything -- what the real
 * route renders is covered by tests/shared/test_serve.py, which can run Jinja.
 * What cannot be tested from Python is the half of the contract this side
 * owns: that the request carries the token, and that the values Flask cannot
 * derive arrive correctly. So this records the request and answers with a
 * fixed body.
 *
 * @param {number} [status]
 * @returns {Promise<object>}
 */
function startFakeSidecar(status = 200) {
	const received = [];

	const server = http.createServer((request, response) => {
		const url = new URL(request.url, 'http://127.0.0.1');
		received.push({ url, headers: request.headers });

		if (url.pathname !== `/${WEBVIEW_PATH}`) {
			response.writeHead(404).end('not found');
			return;
		}

		// The real route requires the token; the extension host fetches it and
		// can send the header.
		if (request.headers[TOKEN_HEADER.toLowerCase()] !== TOKEN) {
			response.writeHead(403).end('forbidden');
			return;
		}

		response.writeHead(status, { 'Content-Type': 'text/html' }).end(PAGE_BODY);
	});

	return new Promise((resolve) => {
		server.listen(0, '127.0.0.1', () => {
			resolve({
				baseUrl: `http://127.0.0.1:${server.address().port}/`,
				token: TOKEN,
				received,
				close: () => server.close()
			});
		});
	});
}

/** @returns {import('vscode').WebviewPanel} */
function createPanel() {
	return vscode.window.createWebviewPanel('test.page', 'Test', vscode.ViewColumn.Active, {
		enableScripts: true,
		localResourceRoots: [vendorRoot(EXTENSION_PATH)]
	});
}

suite('webview page: the request', () => {
	let sidecar;
	let panel;
	let html;
	let query;

	suiteSetup(async () => {
		sidecar = await startFakeSidecar();
		panel = createPanel();
		html = await fetchWebviewPage({
			sidecar,
			webview: panel.webview,
			extensionPath: EXTENSION_PATH
		});
		query = sidecar.received[0].url.searchParams;
	});

	suiteTeardown(() => {
		panel?.dispose();
		sidecar?.close();
	});

	test('returns the page the sidecar rendered, unmodified', () => {
		// The whole point: no assembly on this side.
		assert.strictEqual(html, PAGE_BODY);
	});

	test('sends the token', () => {
		assert.strictEqual(sidecar.received[0].headers[TOKEN_HEADER.toLowerCase()], TOKEN);
	});

	test('sends a base the page can append relative paths to', () => {
		// Every src and href in the page is built by concatenating onto this,
		// so a missing slash silently produces .../plantuml_guistatic/script.js.
		const base = query.get('base');
		assert.ok(base.endsWith('/'), `base does not end in a slash: ${base}`);
		assert.strictEqual(new URL(base).protocol, 'http:');
	});

	test('sends the webview CSP source, which only this side knows', () => {
		// Per-panel, so the sidecar cannot derive it and the page's script-src
		// would not cover the browser libraries without it.
		assert.strictEqual(query.get('csp_source'), panel.webview.cspSource);
	});

	test('sends the browser libraries in load order', () => {
		// The sidecar emits <script> tags in the order these arrive, and
		// Bootstrap throws on load if jQuery is not already there.
		assert.deepStrictEqual(
			query.getAll('vendor_script').map((uri) => path.basename(new URL(uri).pathname)),
			VENDOR_SCRIPTS.map((relative) => path.basename(relative))
		);
	});

	test('sends the browser libraries from node_modules, not the sidecar', () => {
		// The web app gets these from CDNs, which a webview's CSP blocks, and
		// they are not part of the Python package.
		const origin = new URL(sidecar.baseUrl).origin;
		const uris = query.getAll('vendor_script').concat(query.getAll('vendor_style'));

		assert.strictEqual(query.getAll('vendor_style').length, VENDOR_STYLES.length);
		for (const uri of uris) {
			assert.ok(!uri.startsWith(origin), `${uri} should not come from the sidecar`);
		}
	});

	test('every vendored library is actually on disk', () => {
		// The failure mode otherwise is a silent 404 inside the webview, which
		// leaves the menu markup unstyled rather than reporting anything.
		for (const relative of VENDOR_SCRIPTS.concat(VENDOR_STYLES)) {
			const file = path.join(EXTENSION_PATH, 'node_modules', ...relative.split('/'));
			assert.ok(fs.existsSync(file), `missing ${relative} - run npm install`);
		}
	});
});

suite('webview page: failures', () => {
	let panel;

	suiteSetup(() => {
		panel = createPanel();
	});

	suiteTeardown(() => panel?.dispose());

	test('reports a rejected request instead of returning an empty page', async () => {
		// A page that quietly failed to load leaves a blank panel with no clue
		// which of the backend, the token or the jar is at fault.
		const sidecar = await startFakeSidecar();
		try {
			await assert.rejects(
				() =>
					fetchWebviewPage({
						sidecar: { ...sidecar, token: 'wrong-token' },
						webview: panel.webview,
						extensionPath: EXTENSION_PATH
					}),
				(err) => err instanceof WebviewPageError && /403/.test(err.message)
			);
		} finally {
			sidecar.close();
		}
	});

	test('reports an unreachable backend', async () => {
		const sidecar = await startFakeSidecar();
		sidecar.close();

		await assert.rejects(
			() =>
				fetchWebviewPage({
					sidecar,
					webview: panel.webview,
					extensionPath: EXTENSION_PATH
				}),
			(err) => err instanceof WebviewPageError
		);
	});
});
