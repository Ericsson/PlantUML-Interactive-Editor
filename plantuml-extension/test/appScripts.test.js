const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const { APP_SCRIPTS } = require('../src/webviewContent');

const MEDIA_ROOT = path.join(__dirname, '..', 'media');

/** Let script.js's 200ms render debounce fire and its fetches settle. */
const settle = () => new Promise((resolve) => setTimeout(resolve, 400));

/** Minimal DOM, enough for the app scripts' load-time work. */
function stubElement() {
	return {
		style: {},
		innerHTML: '',
		textContent: '',
		classList: { contains: () => false, add() {}, remove() {} },
		addEventListener() {},
		setAttribute() {},
		getAttribute: () => null,
		appendChild() {},
		contains: () => false,
		querySelector: () => null,
		querySelectorAll: () => []
	};
}

function makeSandbox() {
	const sandbox = {
		document: {
			getElementById: stubElement,
			createElement: stubElement,
			querySelector: stubElement,
			querySelectorAll: () => [],
			addEventListener() {},
			body: stubElement()
		},
		console,
		setTimeout,
		clearTimeout,
		fetch: () => Promise.resolve({ text: () => Promise.resolve('') }),
		history: { replaceState() {} },
		location: { href: 'vscode-webview://test/', search: '' },
		Promise,
		Map,
		Set,
		JSON,
		String,
		Object,
		Array,
		Math,
		Date,
		RegExp,
		Error
	};
	sandbox.window = sandbox;
	vm.createContext(sandbox);
	return sandbox;
}

function load(sandbox, relative) {
	const file = path.join(MEDIA_ROOT, ...relative.split('/'));
	const source = fs.readFileSync(file, 'utf-8');
	new vm.Script(source, { filename: relative }).runInContext(sandbox);
}

/**
 * Load the whole webview script stack the way the page does, with the browser
 * and VS Code APIs stubbed, and return handles for driving it.
 *
 * @returns {{
 *   sandbox: object,
 *   fetches: string[],
 *   posted: object[],
 *   dispatch: (message: object) => void
 * }}
 */
function bootWebview() {
	const sandbox = makeSandbox();
	const fetches = [];
	const posted = [];
	const messageHandlers = [];

	sandbox.addEventListener = (type, handler) => {
		if (type === 'message') {
			messageHandlers.push(handler);
		}
	};
	sandbox.acquireVsCodeApi = () => ({ postMessage: (m) => posted.push(m) });
	// Record the body, not just the URL: a render is only proof of anything if
	// it carried the *new* puml. Counting requests instead lets the boot
	// render's own trailing fetches masquerade as a re-render.
	sandbox.fetch = (url, options = {}) => {
		fetches.push({ url: String(url), body: String(options.body ?? '') });
		return Promise.resolve({
			ok: true,
			status: 200,
			text: () => Promise.resolve('<svg><g></g></svg>'),
			json: () => Promise.resolve({})
		});
	};
	// jQuery, used by the app code's modal handling. Only the shape needed at
	// registration time; the tests here never open a modal.
	sandbox.$ = () => ({ modal() {}, hasClass: () => false, on() {}, val() {} });
	sandbox.jQuery = sandbox.$;

	load(sandbox, 'editorShim.js');
	for (const relative of APP_SCRIPTS) {
		load(sandbox, relative);
	}
	load(sandbox, 'webviewInit.js');

	return {
		sandbox,
		fetches,
		posted,
		dispatch: (message) => messageHandlers.forEach((h) => h({ data: message }))
	};
}

suite('reused app scripts run against the editor shim', () => {
	test('the shim satisfies the load-time ace contract', () => {
		// app/script.js does `ace.require("ace/range").Range` at top level, so a
		// shim that only provides `editor` would throw while script.js parses.
		const sandbox = makeSandbox();
		load(sandbox, 'editorShim.js');

		assert.strictEqual(typeof sandbox.ace, 'object');
		assert.strictEqual(typeof sandbox.ace.require('ace/range').Range, 'function');
	});

	test('every app script loads without throwing', () => {
		// The single most valuable check here: these files are the web app's
		// real interaction code, loaded unmodified. If any of them throws during
		// load, the diagram still renders but nothing is interactive -- which is
		// hard to diagnose from the UI.
		const sandbox = makeSandbox();
		load(sandbox, 'editorShim.js');

		for (const relative of APP_SCRIPTS) {
			assert.doesNotThrow(
				() => load(sandbox, relative),
				`${relative} threw while loading against the shim`
			);
		}
	});

	test('setValue routes an edit to the extension host', () => {
		// setPuml() -> session.setValue() is the one door all ~71 diagram
		// operations exit through, so this is what makes them write to the file.
		const sandbox = makeSandbox();
		load(sandbox, 'editorShim.js');

		const posted = [];
		const editor = sandbox.window.PlantumlEditorShim.create((m) => posted.push(m));
		editor.session.setValue('@startuml\nA -> B: x\n@enduml');

		assert.strictEqual(posted.length, 1);
		assert.strictEqual(posted[0].type, 'applyPuml');
		assert.strictEqual(posted[0].text, '@startuml\nA -> B: x\n@enduml');
		assert.strictEqual(editor.session.getValue(), '@startuml\nA -> B: x\n@enduml');
	});

	test('an echoed document update does not re-fire change', () => {
		// The write-back loop terminates here: text we already have must be
		// recognised as our own edit coming back.
		const sandbox = makeSandbox();
		load(sandbox, 'editorShim.js');

		const editor = sandbox.window.PlantumlEditorShim.create(() => {});
		let changes = 0;
		editor.session.on('change', () => changes++);

		editor.session.setValue('text-a');
		assert.strictEqual(changes, 1, 'our own edit should fire change once');

		assert.strictEqual(editor.applyDocumentText('text-a'), false, 'echo ignored');
		assert.strictEqual(changes, 1, 'echo must not fire change again');

		assert.strictEqual(editor.applyDocumentText('text-b'), true, 'real edit applied');
		assert.strictEqual(changes, 2, 'a genuine external edit must fire change');
	});

	test('markers become a row list for the host to decorate', () => {
		const sandbox = makeSandbox();
		load(sandbox, 'editorShim.js');

		const posted = [];
		const editor = sandbox.window.PlantumlEditorShim.create((m) => posted.push(m));
		const { Range } = sandbox.ace.require('ace/range');

		// Array.from: the rows array is built inside the vm realm, so its
		// prototype differs from this realm's and deepStrictEqual would compare
		// prototypes rather than contents.
		const rowsOf = (message) => Array.from(message.rows);
		const lastHighlight = () =>
			rowsOf(posted.filter((m) => m.type === 'setHighlight').pop());

		const id = editor.session.addMarker(new Range(3, 0, 5, 200), 'hover', 'fullLine');
		assert.deepStrictEqual(lastHighlight(), [3, 4, 5]);

		editor.session.removeMarker(id);
		assert.deepStrictEqual(lastHighlight(), []);
	});

	test('a document change triggers a re-render', async () => {
		// Regression: webviewInit.js deliberately skips the web app's
		// initeditor() (it would call setDemo() and overwrite the user's file),
		// but initeditor() is also where `session.on('change', ...)` is
		// registered. Without re-registering it, nothing subscribed to changes:
		// the diagram rendered once at boot and never updated again, from either
		// a diagram interaction or typing in the editor.
		const { fetches, dispatch } = bootWebview();

		dispatch({ type: 'documentChanged', text: '@startuml\nA -> B: one\n@enduml' });
		await settle();
		assert.ok(
			fetches.some((f) => f.body.includes('one')),
			'boot should render the initial document'
		);

		dispatch({ type: 'documentChanged', text: '@startuml\nA -> B: two\n@enduml' });
		// renderPlantUml is reached through script.js's 200ms debounce.
		await settle();

		assert.ok(
			fetches.some((f) => f.body.includes('two')),
			'the changed document was never sent to the backend, so the diagram ' +
				'would still show the old text'
		);
	});

	test('a diagram-side edit triggers a re-render', async () => {
		// Same wiring, exercised from the other direction: setPuml() ->
		// setValue() must both write to the document and refresh the diagram.
		const { fetches, posted, sandbox, dispatch } = bootWebview();

		dispatch({ type: 'documentChanged', text: '@startuml\nA -> B: one\n@enduml' });
		await settle();

		sandbox.window.PlantumlEditorShim.current.session.setValue(
			'@startuml\nA -> B: edited\n@enduml'
		);

		assert.ok(
			posted.some((m) => m.type === 'applyPuml' && m.text.includes('edited')),
			'the edit must be sent to the extension host'
		);

		await settle();

		assert.ok(
			fetches.some((f) => f.body.includes('edited')),
			'the diagram must re-render with the edited text'
		);
	});

	test('clearMarkers only removes hover markers', () => {
		// app/script.js's clearMarkers() iterates getMarkers() and filters on
		// clazz === 'hover', so the table it reads must have that shape.
		const sandbox = makeSandbox();
		load(sandbox, 'editorShim.js');

		const editor = sandbox.window.PlantumlEditorShim.create(() => {});
		const { Range } = sandbox.ace.require('ace/range');

		editor.session.addMarker(new Range(1, 0, 1, 200), 'hover');
		editor.session.addMarker(new Range(2, 0, 2, 200), 'active-line');

		const markers = Object.values(editor.session.getMarkers());
		assert.strictEqual(markers.length, 2);
		assert.strictEqual(markers.filter((m) => m.clazz === 'hover').length, 1);
	});
});
