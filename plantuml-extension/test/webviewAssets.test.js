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
const crypto = require('crypto');
const fs = require('fs');
const http = require('http');
const path = require('path');
const vscode = require('vscode');

const {
	resolveWebviewAssets,
	buildCsp,
	vendorRoot,
	fetchMenus,
	AssetLoadError,
	APP_SCRIPTS,
	VENDOR_SCRIPTS,
	VENDOR_STYLES,
	MENUS_PATH,
	TOKEN_HEADER
} = require('../src/webviewAssets');

const EXTENSION_PATH = path.join(__dirname, '..');
const STATIC_DIR = path.join(EXTENSION_PATH, '..', 'src', 'plantuml_gui', 'static');

const TOKEN = 'test-token';

const MENUS_BODY = '<div id="activity-menu"></div>';

const MIME = { '.js': 'text/javascript', '.css': 'text/css' };

/**
 * A stand-in for the sidecar: the same two behaviours the webview depends on,
 * serving the frontend's real files, without needing a Python interpreter.
 *
 * Flask's own half of the contract -- that /static is exempt from the token
 * check and that /webview/menus renders the Jinja partials -- is covered by
 * tests/shared/test_serve.py. What cannot be tested from Python is whether a
 * webview will *load* any of it, which is what these tests are for.
 *
 * @returns {Promise<{ baseUrl: string, token: string, close: () => void }>}
 */
function startFakeSidecar() {
	const server = http.createServer((request, response) => {
		const url = new URL(request.url, 'http://127.0.0.1');

		if (url.pathname === `/${MENUS_PATH}`) {
			// The real route requires the token; the extension host fetches it
			// and can send the header.
			if (request.headers[TOKEN_HEADER.toLowerCase()] !== TOKEN) {
				response.writeHead(403).end('forbidden');
				return;
			}
			response.writeHead(200, { 'Content-Type': 'text/html' }).end(MENUS_BODY);
			return;
		}

		if (url.pathname.startsWith('/static/')) {
			// No token check, mirroring the exemption in serve.py: a <script
			// src> cannot send a header.
			const file = path.join(STATIC_DIR, url.pathname.slice('/static/'.length));
			if (!fs.existsSync(file)) {
				response.writeHead(404).end('not found');
				return;
			}
			response
				.writeHead(200, { 'Content-Type': MIME[path.extname(file)] ?? 'text/plain' })
				.end(fs.readFileSync(file));
			return;
		}

		response.writeHead(404).end('not found');
	});

	return new Promise((resolve) => {
		server.listen(0, '127.0.0.1', () => {
			resolve({
				baseUrl: `http://127.0.0.1:${server.address().port}/`,
				token: TOKEN,
				close: () => server.close()
			});
		});
	});
}

/**
 * @param {object} [options]
 * @returns {import('vscode').WebviewPanel}
 */
function createPanel(options = {}) {
	return vscode.window.createWebviewPanel(
		'test.assets',
		'Test',
		vscode.ViewColumn.Active,
		{
			enableScripts: true,
			localResourceRoots: [vendorRoot(EXTENSION_PATH)],
			...options
		}
	);
}

suite('webview assets: URLs', () => {
	let sidecar;
	let panel;
	let assets;

	suiteSetup(async () => {
		sidecar = await startFakeSidecar();
		panel = createPanel();
		assets = await resolveWebviewAssets({
			sidecar,
			webview: panel.webview,
			extensionPath: EXTENSION_PATH
		});
	});

	suiteTeardown(() => {
		panel?.dispose();
		sidecar?.close();
	});

	test('serves every app script from the sidecar, in load order', () => {
		assert.strictEqual(assets.scriptSrcs.length, APP_SCRIPTS.length);
		assert.ok(assets.scriptSrcs[0].endsWith('/static/script.js'));
		assert.ok(assets.scriptSrcs.at(-1).endsWith('/static/activity.js'));
		for (const src of assets.scriptSrcs) {
			assert.strictEqual(new URL(src).origin, assets.origin);
		}
	});

	test('leaves out the Ace syntax mode', () => {
		// There is no Ace here -- the VS Code editor is the source editor --
		// so mode-plantuml.js would be dead weight and a confusing 404 hunt.
		assert.ok(!assets.scriptSrcs.some((src) => src.includes('mode-plantuml')));
	});

	test('loads only the stylesheet entry point', () => {
		// styles.css @imports six files from static/css/, and over HTTP those
		// resolve against the sidecar on their own -- unlike a mirror, where
		// the subtree has to be copied.
		assert.deepStrictEqual(
			assets.styleHrefs.map((href) => new URL(href).pathname),
			['/static/styles.css']
		);
	});

	test('loads the browser libraries from node_modules, not the sidecar', () => {
		// The web app gets these from CDNs, which a webview's CSP blocks, and
		// they are not part of the Python package.
		const uris = [...assets.vendorScriptUris, ...assets.vendorStyleUris];

		assert.strictEqual(uris.length, VENDOR_SCRIPTS.length + VENDOR_STYLES.length);
		for (const uri of uris) {
			assert.ok(!uri.startsWith(assets.origin), `${uri} should not come from the sidecar`);
		}
	});

	test('every vendored library is actually on disk', () => {
		// The failure mode otherwise is a silent 404 inside the webview: the
		// diagram still renders and nothing is clickable.
		for (const relative of [...VENDOR_SCRIPTS, ...VENDOR_STYLES]) {
			const file = path.join(EXTENSION_PATH, 'node_modules', ...relative.split('/'));
			assert.ok(fs.existsSync(file), `missing ${relative} - run npm install`);
		}
	});

	test('inlines the menu markup the sidecar rendered', () => {
		assert.strictEqual(assets.menusHtml, MENUS_BODY);
	});
});

suite('webview assets: menus', () => {
	let sidecar;

	setup(async () => {
		sidecar = await startFakeSidecar();
	});

	teardown(() => sidecar.close());

	test('sends the token', async () => {
		assert.strictEqual(await fetchMenus(sidecar.baseUrl, TOKEN), MENUS_BODY);
	});

	test('reports a rejected request instead of returning empty markup', async () => {
		// Menus that quietly failed to load would look like a working diagram
		// with no context menus, which is indistinguishable from a broken
		// handler.
		await assert.rejects(
			() => fetchMenus(sidecar.baseUrl, 'wrong-token'),
			(err) => err instanceof AssetLoadError && /403/.test(err.message)
		);
	});
});

suite('webview assets: content security policy', () => {
	let panel;

	suiteSetup(() => {
		panel = createPanel();
	});

	suiteTeardown(() => panel.dispose());

	/** @returns {Record<string, string>} the policy, split by directive. */
	function policy() {
		const csp = buildCsp({
			webview: panel.webview,
			assets: { origin: 'http://127.0.0.1:53421' },
			nonce: 'NONCE'
		});
		return Object.fromEntries(
			csp.split('; ').map((directive) => {
				const parts = directive.split(' ');
				return [parts[0], parts.slice(1).join(' ')];
			})
		);
	}

	test('allows the frontend to load and call the sidecar', () => {
		const csp = policy();

		assert.ok(csp['script-src'].includes('http://127.0.0.1:53421'));
		assert.ok(csp['style-src'].includes('http://127.0.0.1:53421'));
		assert.strictEqual(csp['connect-src'], 'http://127.0.0.1:53421');
	});

	test('permits scripts only via the nonce or a known origin', () => {
		// What makes it safe to innerHTML PlantUML-rendered SVG from an
		// untrusted .puml file: injected markup can carry neither the nonce nor
		// a permitted origin, so inline <script> and SVG onload are blocked.
		const csp = policy();

		assert.ok(csp['script-src'].includes("'nonce-NONCE'"));
		assert.ok(!csp['script-src'].includes("'unsafe-inline'"));
		assert.strictEqual(csp['default-src'], "'none'");
	});
});

suite('webview assets: loading from the sidecar', () => {
	let sidecar;
	let panel;

	setup(async () => {
		sidecar = await startFakeSidecar();
	});

	teardown(() => {
		panel?.dispose();
		sidecar.close();
	});

	/**
	 * Load the frontend into a real webview and report back what arrived.
	 *
	 * This is the test the whole approach rests on. Everything else here is
	 * string manipulation; only a real webview can answer whether Chromium
	 * will execute a script served over HTTP from another origin under the
	 * policy we set. If this fails, assets have to be inlined or mirrored
	 * instead.
	 *
	 * `title.js` is the probe because it is nothing but function declarations:
	 * no `ace`, no DOM, no shims, so a failure here is about loading and
	 * nothing else.
	 *
	 * @returns {Promise<{ script: string, style: string }>}
	 */
	function probe() {
		panel = createPanel();

		const assetsPromise = resolveWebviewAssets({
			sidecar,
			webview: panel.webview,
			extensionPath: EXTENSION_PATH
		});

		return assetsPromise.then(
			(assets) =>
				new Promise((resolve, reject) => {
					const nonce = crypto.randomBytes(16).toString('base64');
					const timer = setTimeout(
						() => reject(new Error('the webview never reported back')),
						15000
					);

					panel.webview.onDidReceiveMessage((message) => {
						clearTimeout(timer);
						resolve(message);
					});

					panel.webview.html = `<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="Content-Security-Policy" content="${buildCsp({
		webview: panel.webview,
		assets,
		nonce
	})}">
	<link rel="stylesheet" href="${assets.styleHrefs[0]}">
</head>
<body>
	<script src="${assets.base}static/title.js"></script>
	<script nonce="${nonce}">
		const vscodeApi = acquireVsCodeApi();
		// A stylesheet arrives asynchronously, so read it after a paint.
		requestAnimationFrame(() => {
			vscodeApi.postMessage({
				script: typeof titleEventListeners,
				style: getComputedStyle(document.documentElement)
					.getPropertyValue('--toolbar-height')
					.trim()
			});
		});
	</script>
</body>
</html>`;
				})
		);
	}

	test('executes an app script served over HTTP', async function () {
		this.timeout(30000);

		assert.strictEqual((await probe()).script, 'function');
	});

	test('follows the stylesheet @import chain back to the sidecar', async function () {
		this.timeout(30000);

		// --toolbar-height is defined in static/css/tokens.css, which is only
		// reachable by resolving styles.css's @import against the sidecar
		// origin. Under a mirror this subtree had to be copied by hand.
		assert.strictEqual((await probe()).style, '30px');
	});
});
