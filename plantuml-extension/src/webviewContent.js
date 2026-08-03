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

// The webview page: a shell that supplies the ids the web app's CSS and markup
// expect, and points at the frontend the sidecar serves.
//
// The markup lives in webviewContent.html rather than in a template literal
// here, so it can be edited and previewed as HTML -- and so that a stray
// backtick in the page cannot terminate a literal and turn the rest of the
// document into executable JavaScript. This module only fills in placeholders.

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');

const { buildCsp } = require('./webviewAssets');

const HTML_PATH = path.join(__dirname, 'webviewContent.html');

/** Cached template, read once; it cannot change while the host is running. */
let cachedTemplate;

/**
 * @returns {string} the raw webviewContent.html template.
 */
function readTemplate() {
	if (cachedTemplate === undefined) {
		cachedTemplate = fs.readFileSync(HTML_PATH, 'utf-8');
	}
	return cachedTemplate;
}

/**
 * Build the document loaded into the diagram panel.
 *
 * @param {object} options
 * @param {import('vscode').Webview} options.webview
 * @param {Awaited<ReturnType<import('./webviewAssets').resolveWebviewAssets>>} options.assets
 * @returns {string}
 */
function getWebviewContent({ webview, assets }) {
	const nonce = crypto.randomBytes(16).toString('base64');

	// Vendored Bootstrap first: the app's own stylesheet is written to override
	// it, and on equal specificity the later rule wins.
	const styleLinks = [...assets.vendorStyleUris, ...assets.styleHrefs]
		.map((href) => `\t<link rel="stylesheet" href="${href}">`)
		.join('\n');

	return fill(readTemplate(), {
		csp: buildCsp({ webview, assets, nonce }),
		nonce,
		styleLinks,
		menus: assets.menusHtml
	});
}

/**
 * Replace every {{name}} placeholder in `template`.
 *
 * Substituted through a replacer function so that a `$&` or `$1` appearing in
 * the menu markup or a URL is inserted literally rather than being read as a
 * replacement pattern.
 *
 * @param {string} template
 * @param {Record<string, string>} values
 * @returns {string}
 * @throws {Error} if the template names a placeholder that has no value
 */
function fill(template, values) {
	return template.replace(/\{\{(\w+)\}\}/g, (match, name) => {
		if (!(name in values)) {
			throw new Error(`webviewContent.html uses an unknown placeholder: ${match}`);
		}
		return values[name];
	});
}

module.exports = {
	getWebviewContent
};
