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

// Minimal webview content for the PlantUML diagram panel.
//
// The webview holds only a diagram container and just enough script to
// receive `{ type: "updateDiagram", svg }` and `{ type: "renderError", message }`
// messages posted from the extension via panel.webview.postMessage(...).
// It intentionally contains no PlantUML source, no code editor, and no
// Ace Editor - the VS Code text editor remains the only source editor.
//
// The markup itself lives in webviewContent.html (a plain, global static
// file) so it can be edited/previewed as regular HTML rather than a JS
// template string. This module just reads it from disk and caches it.

const fs = require('fs');
const path = require('path');

const HTML_PATH = path.join(__dirname, 'webviewContent.html');

/** Cached file contents, populated on first call to getWebviewContent(). */
let cachedHtml;

/**
 * @returns {string} the static HTML document loaded into the webview.
 */
function getWebviewContent() {
	if (cachedHtml === undefined) {
		cachedHtml = fs.readFileSync(HTML_PATH, 'utf-8');
	}
	return cachedHtml;
}

module.exports = {
	getWebviewContent
};
