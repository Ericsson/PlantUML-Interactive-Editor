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

// Points the reused app code's relative fetch() calls at the sidecar.
//
// Everything in static/vscode/ runs only inside the VS Code extension's diagram
// panel, never on the web page at /. It lives here rather than in the extension
// because it is a <script src> on webview.html, which this server renders:
// serving it next to script.js costs nothing, and the alternative is the
// extension resolving a webview URL for it and passing that in.
//
// The web app calls fetch("editText", ...), fetch("render", ...) and so on with
// relative URLs, which in a browser resolve against the Flask origin. In a
// webview the page URL has a vscode-webview-ish origin, so they would resolve
// to nonsense. Rewriting them here is the only change those ~150 call sites
// need -- which is why this is a shim and not a refactor.
//
// Must load before any app script.
//
// Note that this makes every request cross-origin, and the token header below
// is not CORS-safelisted, so the sidecar has to answer preflights. See
// install_cors in serve.py.
//
// Where the address, the token and the header's name come from: webview.html
// puts all three on <body>, so this file stays a static file that Flask can
// serve as-is rather than a template, and the page needs no inline script.

(function () {
	const nativeFetch = window.fetch.bind(window);
	const {
		plantumlApi: base,
		plantumlToken: token,
		plantumlTokenHeader: tokenHeader
	} = document.body.dataset;

	window.fetch = function (url, options = {}) {
		const target = String(url);
		const absolute = /^[a-z]+:\/\//i.test(target)
			? target
			: base + target.replace(/^\//, '');

		return nativeFetch(absolute, {
			...options,
			headers: { ...(options.headers || {}), [tokenHeader]: token }
		});
	};
})();
