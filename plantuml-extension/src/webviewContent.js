// Builds the webview page that hosts the reused web app frontend.
//
// This file is a shell, not an implementation: it supplies the DOM ids the web
// app's code expects (#colb, #popup, ...), loads the vendored libraries, the
// editor shim, the mirrored app scripts, and the real context-menu markup. All
// diagram behaviour comes from those files -- see media/editorShim.js for how
// the VS Code document stands in for Ace, and
// docs/vscode_extension_interactivity.md for the design.

const crypto = require('crypto');
const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

// Load order is significant:
//   - editorShim defines the global `ace` that app/script.js dereferences at
//     load time, so it must come first.
//   - webviewInit assigns script.js's `let editor` binding, so it must come
//     last, after every app script has been parsed.
const APP_SCRIPTS = [
	'app/script.js',
	'app/title.js',
	'app/hover-highlight.js',
	'app/sequence-message.js',
	'app/sequence-activation.js',
	'app/sequence-group.js',
	'app/sequence-box.js',
	'app/sequence-operations.js',
	'app/activity.js'
];

const VENDOR_SCRIPTS = [
	'vendor/jquery.min.js',
	'vendor/bootstrap.min.js',
	'vendor/panzoom.min.js',
	'vendor/diff.min.js'
];

const MENU_PARTIALS = ['menus/activity_menus.html', 'menus/sequence_menus.html'];

/**
 * @param {object} options
 * @param {string} options.apiBase base URL of the sidecar
 * @param {string} options.token per-launch token the sidecar requires
 * @param {import('vscode').Webview} options.webview used to build resource URIs
 * @param {string} options.mediaRoot absolute path to the extension's media dir
 * @returns {string} the HTML document loaded into the webview.
 */
function getWebviewContent({ apiBase, token, webview, mediaRoot }) {
	const nonce = crypto.randomBytes(16).toString('base64');
	const uri = (relative) =>
		webview.asWebviewUri(
			vscode.Uri.file(path.join(mediaRoot, ...relative.split('/')))
		);

	const csp = [
		"default-src 'none'",
		`img-src ${webview.cspSource} data:`,
		// 'unsafe-inline' for styles only: Bootstrap and the app CSS both set
		// inline styles, and the app code toggles element.style directly.
		`style-src ${webview.cspSource} 'unsafe-inline'`,
		`script-src 'nonce-${nonce}' ${webview.cspSource}`,
		`font-src ${webview.cspSource}`,
		`connect-src ${new URL(apiBase).origin}`
	].join('; ');

	const menus = MENU_PARTIALS.map((relative) =>
		fs.readFileSync(path.join(mediaRoot, ...relative.split('/')), 'utf-8')
	).join('\n');

	const scripts = [...VENDOR_SCRIPTS, 'editorShim.js', ...APP_SCRIPTS, 'webviewInit.js']
		.map((relative) => `<script nonce="${nonce}" src="${uri(relative)}"></script>`)
		.join('\n\t');

	return `<!DOCTYPE html>
<html lang="en">
<head>
	<meta charset="UTF-8">
	<meta http-equiv="Content-Security-Policy" content="${csp}">
	<meta name="viewport" content="width=device-width, initial-scale=1.0">
	<title>PlantUML Interactive Diagram</title>
	<link rel="stylesheet" href="${uri('vendor/bootstrap.min.css')}">
	<link rel="stylesheet" href="${uri('app/styles.css')}">
	<style>
		/* The app CSS is written for the full two-pane web layout. Here the
		   diagram is the whole page, so undo the parts that assume a shell. */
		html, body {
			margin: 0;
			padding: 0;
			height: 100%;
			overflow: hidden;
			background-color: var(--vscode-editor-background);
			color: var(--vscode-editor-foreground);
			font-family: var(--vscode-font-family);
		}
		#colb-container {
			position: absolute;
			inset: 0;
			overflow: hidden;
		}
		#colb { transform-origin: 0 0; padding: 12px; }
		#colb svg { max-width: none; }
		/* The VS Code editor is the source editor; the app's Ace container is
		   only present because hover-highlight.js reads editor.container. */
		#editor, #version, #version-panel { display: none !important; }
		#popup {
			visibility: hidden;
			position: absolute;
			top: 0;
			left: 0;
			right: 0;
			z-index: 5000;
			padding: 8px 12px;
			background: var(--vscode-inputValidation-errorBackground);
			color: var(--vscode-errorForeground);
			border-bottom: 1px solid var(--vscode-inputValidation-errorBorder);
			white-space: pre-wrap;
			font-family: var(--vscode-editor-font-family);
			font-size: 12px;
		}
		#loading-overlay {
			display: none;
			position: absolute;
			inset: 0;
			background: rgba(0, 0, 0, 0.08);
			z-index: 4000;
		}
	</style>
</head>
<body>
	<!-- Ids below are required by the reused app code; see the id cross-check
	     in the design doc. #editor exists only so editor.container is non-null. -->
	<div id="popup">Error message</div>
	<div id="editor"></div>
	<span id="version"></span>
	<div id="version-panel"></div>

	<div id="colb-container">
		<div id="colb"></div>
		<div id="loading-overlay"></div>
	</div>

${menus}

	<script nonce="${nonce}">
		// Consumed by the fetch shim below, which the app code's ~150 relative
		// fetch() calls go through.
		window.__PLANTUML_API__ = ${JSON.stringify(apiBase)};
		window.__PLANTUML_TOKEN__ = ${JSON.stringify(token)};
	</script>
	<script nonce="${nonce}" src="${uri('fetchShim.js')}"></script>
	${scripts}
</body>
</html>`;
}

module.exports = {
	getWebviewContent,
	APP_SCRIPTS,
	VENDOR_SCRIPTS,
	MENU_PARTIALS
};
