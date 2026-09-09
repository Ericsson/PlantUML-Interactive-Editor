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

// Where the webview's page comes from.
//
// It is not built here. The page is the web app's frontend -- its interaction
// code, its CSS, its context menus -- and the sidecar is already a web server
// that has all of it plus the Jinja to render it, so the sidecar renders the
// whole document and this module asks for it. There is no HTML in this
// extension, no copy of the frontend, no build or sync step, and no way for
// the webview to run a stale copy of a file that was edited in
// src/plantuml_gui/.
//
// What the sidecar cannot know, and this module therefore tells it:
//   - the browser libraries. The web app loads jQuery, Bootstrap, panzoom and
//     diff from CDNs, which a webview's CSP blocks, so they are taken straight
//     out of node_modules and reached through webview-specific URLs.
//   - `webview.cspSource`, the origin those URLs are on. Per-panel.
//   - the address the webview should call the sidecar on, which is not the one
//     this process reaches it at whenever the UI is running elsewhere.
//
// Working on the frontend: edit src/plantuml_gui/templates/webview.html,
// static/vscode/ or static/, then reopen the diagram panel.

const path = require('path');
const vscode = require('vscode');
const { TOKEN_HEADER } = require('./sidecar');

// Must match WEBVIEW_ROUTE in src/plantuml_gui/serve.py.
const WEBVIEW_PATH = 'webview';

// A local server that has already answered /health; a slow answer here means
// something is wrong rather than merely busy.
const PAGE_TIMEOUT_MS = 5000;

// node_modules-relative, and ordered: the sidecar emits the <script> tags in
// the order these arrive, and Bootstrap requires jQuery. jQuery is pinned to
// 3.x because Bootstrap 4 requires <4.
const VENDOR_SCRIPTS = [
	'jquery/dist/jquery.min.js',
	'bootstrap/dist/js/bootstrap.min.js',
	'panzoom/dist/panzoom.min.js',
	'diff/dist/diff.min.js'
];

const VENDOR_STYLES = ['bootstrap/dist/css/bootstrap.min.css'];

/** Thrown when the page cannot be loaded from a running sidecar. */
class WebviewPageError extends Error {}

/**
 * The node_modules directory, for `localResourceRoots`.
 *
 * The libraries are loaded from where npm put them instead of being copied
 * into the extension, which is why they are runtime `dependencies` rather than
 * devDependencies: vsce packages those into the VSIX.
 *
 * @param {string} extensionPath
 * @returns {import('vscode').Uri}
 */
function vendorRoot(extensionPath) {
	return vscode.Uri.file(path.join(extensionPath, 'node_modules'));
}

/**
 * @param {import('vscode').Webview} webview
 * @param {import('vscode').Uri} root
 * @param {string[]} relatives paths below `root`
 * @returns {string[]} webview-loadable URIs
 */
function localUris(webview, root, relatives) {
	return relatives.map((relative) =>
		webview
			.asWebviewUri(vscode.Uri.joinPath(root, ...relative.split('/')))
			.toString()
	);
}

/**
 * @param {string} url
 * @returns {string} the same URL, guaranteed to end in a slash so relative
 *   paths can be appended.
 */
function withTrailingSlash(url) {
	return url.endsWith('/') ? url : `${url}/`;
}

/**
 * Fetch the document to load into the diagram panel.
 *
 * The request is made here, in Node, rather than by the page, for two reasons:
 * it can carry the token header, and it reaches the sidecar on loopback --
 * where this process runs, which is where the sidecar runs. The address the
 * *webview* must use is a separate question, answered by asExternalUri and
 * passed along as `base`.
 *
 * @param {object} options
 * @param {import('./sidecar').Sidecar} options.sidecar a running sidecar
 * @param {import('vscode').Webview} options.webview used to build resource URIs
 * @param {string} options.extensionPath
 * @returns {Promise<string>} the page's HTML
 * @throws {WebviewPageError}
 */
async function fetchWebviewPage({ sidecar, webview, extensionPath }) {
	// The sidecar binds loopback, which the webview cannot reach directly under
	// Remote-SSH, WSL or Codespaces; asExternalUri returns an address that
	// works from wherever the UI is actually running.
	const base = withTrailingSlash(
		(await vscode.env.asExternalUri(vscode.Uri.parse(sidecar.baseUrl))).toString()
	);

	const vendor = vendorRoot(extensionPath);

	const query = new URLSearchParams();
	query.set('base', base);
	query.set('csp_source', webview.cspSource);
	// append, not set: the sidecar reads these back with getlist, which
	// preserves the order they appear in.
	for (const uri of localUris(webview, vendor, VENDOR_SCRIPTS)) {
		query.append('vendor_script', uri);
	}
	for (const uri of localUris(webview, vendor, VENDOR_STYLES)) {
		query.append('vendor_style', uri);
	}

	let response;

	try {
		response = await fetch(`${sidecar.baseUrl}${WEBVIEW_PATH}?${query}`, {
			headers: { [TOKEN_HEADER]: sidecar.token },
			signal: AbortSignal.timeout(PAGE_TIMEOUT_MS)
		});
	} catch (err) {
		throw new WebviewPageError(
			`Could not load the diagram page from the PlantUML backend: ${err.message}`
		);
	}

	if (!response.ok) {
		throw new WebviewPageError(
			`The PlantUML backend returned ${response.status} for the diagram page.`
		);
	}

	return response.text();
}

module.exports = {
	fetchWebviewPage,
	vendorRoot,
	WebviewPageError,
	VENDOR_SCRIPTS,
	VENDOR_STYLES,
	WEBVIEW_PATH
};
