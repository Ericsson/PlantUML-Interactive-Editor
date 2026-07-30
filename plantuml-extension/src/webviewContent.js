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
