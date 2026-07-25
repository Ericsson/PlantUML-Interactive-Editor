const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vscode = require('vscode');

const {
	getWebviewContent,
	APP_SCRIPTS,
	VENDOR_SCRIPTS
} = require('../src/webviewContent');

const MEDIA_ROOT = path.join(__dirname, '..', 'media');

/** Build the page against a real webview, so asWebviewUri behaves normally. */
function render() {
	const panel = vscode.window.createWebviewPanel(
		'test.panel',
		'Test',
		vscode.ViewColumn.Active,
		{ enableScripts: true, localResourceRoots: [vscode.Uri.file(MEDIA_ROOT)] }
	);
	try {
		return getWebviewContent({
			apiBase: 'http://127.0.0.1:53421/',
			token: 'test-token',
			webview: panel.webview,
			mediaRoot: MEDIA_ROOT
		});
	} finally {
		panel.dispose();
	}
}

/**
 * First capture group of `pattern` in `text`, asserting that it matched.
 *
 * @param {RegExp} pattern
 * @param {string} text
 * @returns {string}
 */
function capture(pattern, text) {
	const match = pattern.exec(text);
	assert.ok(match, `no match for ${pattern}`);
	return match[1];
}

/**
 * @param {string} html
 * @returns {Record<string, string>} the CSP meta tag, split by directive.
 */
function parseCsp(html) {
	const content = capture(/Content-Security-Policy" content="([^"]+)"/, html);
	return Object.fromEntries(
		content.split('; ').map((directive) => {
			const parts = directive.split(' ');
			return [parts[0], parts.slice(1).join(' ')];
		})
	);
}

suite('webview: content security policy', () => {
	test('allows connections to the sidecar origin only', () => {
		assert.strictEqual(parseCsp(render())['connect-src'], 'http://127.0.0.1:53421');
	});

	test('permits scripts only via nonce or local resources', () => {
		// What makes it safe to innerHTML PlantUML-rendered SVG from an
		// untrusted .puml file: injected markup can carry neither the nonce nor
		// a local resource origin, so inline <script> and SVG onload handlers
		// are both blocked.
		const csp = parseCsp(render());

		assert.match(csp['script-src'], /^'nonce-[^']+'/);
		assert.doesNotMatch(csp['script-src'], /unsafe-inline/);
		assert.doesNotMatch(csp['script-src'], /unsafe-eval/);
		assert.strictEqual(csp['default-src'], "'none'");
	});

	test('uses a fresh nonce per panel', () => {
		const first = capture(/'nonce-([^']+)'/, render());
		const second = capture(/'nonce-([^']+)'/, render());

		assert.notStrictEqual(first, second);
	});
});

suite('webview: script load order', () => {
	/**
	 * @param {string} html
	 * @returns {string[]} the media-relative script sources, in document order.
	 */
	function scriptOrder(html) {
		return [...html.matchAll(/<script[^>]+src="([^"]+)"/g)]
			.map((match) => decodeURIComponent(match[1]))
			.map((src) => src.slice(src.lastIndexOf('/media/') + '/media/'.length));
	}

	test('the editor shim precedes the app scripts', () => {
		// app/script.js dereferences `ace` at load time, so a later shim throws
		// while the app script is still parsing.
		const order = scriptOrder(render());

		assert.ok(
			order.indexOf('editorShim.js') < order.indexOf('app/script.js'),
			`shim must come first, got ${order.join(', ')}`
		);
	});

	test('the fetch shim precedes the app scripts', () => {
		const order = scriptOrder(render());

		assert.ok(order.indexOf('fetchShim.js') < order.indexOf('app/script.js'));
	});

	test('the init script comes last', () => {
		// It assigns app/script.js's `let editor` binding, which only works
		// once every app script has been parsed.
		const order = scriptOrder(render());

		assert.strictEqual(order[order.length - 1], 'webviewInit.js');
	});

	test('every declared script is actually present on disk', () => {
		// A typo in APP_SCRIPTS yields a silently missing <script>, and the
		// diagram then loads but does nothing.
		for (const relative of [...VENDOR_SCRIPTS, ...APP_SCRIPTS]) {
			const file = path.join(MEDIA_ROOT, ...relative.split('/'));
			assert.ok(fs.existsSync(file), `missing ${relative} - run npm run sync-assets`);
		}
	});
});

suite('webview: DOM contract with the reused app code', () => {
	// The app code calls getElementById on these and dereferences the result
	// without a null check, so a missing id throws during setup and kills every
	// interaction. Cross-checked against the app sources in the design doc.
	const REQUIRED_IDS = [
		'colb',
		'colb-container',
		'loading-overlay',
		'popup',
		'editor',
		'version',
		'version-panel'
	];

	test('supplies the shell ids the app code dereferences', () => {
		const html = render();

		for (const id of REQUIRED_IDS) {
			assert.ok(
				new RegExp(`id\\s*=\\s*"${id}"`).test(html),
				`webview shell is missing #${id}`
			);
		}
	});

	test('inlines the real context menus', () => {
		const html = render();

		// A sample from each partial, so a failed sync is caught here.
		assert.ok(/id\s*=\s*"activity-menu"/.test(html), 'activity menus missing');
		assert.ok(/id\s*=\s*"sequence-menu"/.test(html), 'sequence menus missing');
		assert.ok(/id\s*=\s*"if-menu"/.test(html), 'activity if-menu missing');
	});

	test('the colour selects survived Jinja rendering', () => {
		// sequence_menus.html calls a color_select macro; a plain copy instead
		// of a render would leave the call as literal text and the dropdowns
		// would not exist.
		const html = render();

		assert.ok(/id\s*=\s*"seq-note-color-select"/.test(html));
		assert.doesNotMatch(html, /color_select/, 'unrendered Jinja macro call');
	});
});
