// Boots the reused web app code inside the webview.
//
// Loaded LAST, after app/script.js and friends. That order matters: script.js
// declares `let editor;` at top level, which creates a global *lexical*
// binding rather than a property of window. Only another classic script
// sharing that global scope can assign it -- which is what this file does.
//
// This replaces index.html's inline bootstrap. It deliberately does not call
// the web app's initeditor() or addUtilEventListeners():
//   - initeditor() builds an Ace instance and, finding no ?hash in the URL,
//     calls setDemo() -- which would overwrite the user's file with the demo.
//   - addUtilEventListeners() calls buttonEventListeners(), which binds the web
//     app's toolbar (New/Undo/Save/PNG...). Those buttons do not exist here, and
//     getElementById(...).addEventListener on null throws.
// The context menus themselves are wired by checkDiagramType() during
// renderPlantUml(), which is why every diagram interaction works without us
// touching it.

(function () {
	const vscodeApi = acquireVsCodeApi();

	const post = (message) => vscodeApi.postMessage(message);

	// Assigns app/script.js's `let editor` binding, not a new global.
	editor = window.PlantumlEditorShim.create(post);

	// The listeners initeditor() would have registered. Skipping initeditor()
	// (see the note above) also skipped these, which meant nothing was
	// subscribed to changes: the diagram rendered once at boot and then never
	// again, whether the change came from a diagram interaction or from typing
	// in the editor. Re-register them explicitly.
	editor.session.on('change', () => debouncedRenderPlantUml());

	editor.session.selection.on('changeCursor', () => {
		clearMarkers();
		cursorChangeListener();
	});

	// Inert here -- the shim's editor.on() is a no-op because VS Code exposes no
	// per-line hover for text editors. Called anyway so that the wiring is
	// complete if that ever changes. See the design doc, Phase 7.
	initEditorHoverHighlighting(editor);

	// Diagram-agnostic title editing (double-click the title block). The web app
	// wires this from addUtilEventListeners(), which we skip, so call it here.
	titleEventListeners();

	// Ctrl+Enter to submit the focused modal. The web app gets this from
	// commandEventListeners(), which also binds Ctrl+Z/Ctrl+Y to its own
	// history array -- we want VS Code's native undo instead, since every edit
	// goes through a WorkspaceEdit and is already on its undo stack.
	document.addEventListener('keydown', (event) => {
		if (!(event.ctrlKey && event.key === 'Enter')) {
			return;
		}
		const open = document.querySelector('.modal.show');
		if (!open) {
			return;
		}
		const submit = open.querySelector(
			'[id^="submit"], [id$="submit"], .btn-primary'
		);
		if (submit) {
			event.preventDefault();
			submit.click();
		}
	});

	let booted = false;

	window.addEventListener('message', (event) => {
		const message = event.data;

		if (message.type === 'documentChanged') {
			if (!booted) {
				// First message: seed the text without firing `change`, then
				// render once explicitly. Going through applyDocumentText here
				// would render via the debounce and race the handler setup.
				booted = true;
				editor.primeDocumentText(message.text);
				renderPlantUml();
				return;
			}
			// Returns false when this is the echo of an edit we just made, in
			// which case the diagram is already correct and re-rendering would
			// only cause a flicker.
			editor.applyDocumentText(message.text);
		} else if (message.type === 'cursorMoved') {
			editor.applyCursor({ row: message.row, column: message.column });
		}
	});

	// Pan and zoom the diagram, as the web app's index.html does.
	const diagram = document.getElementById('colb');
	if (window.panzoom && diagram) {
		const instance = panzoom(diagram, { maxZoom: 3, minZoom: 0.25, bounds: true });
		// Double-click is an editing gesture here (edit text), so stop panzoom
		// treating it as zoom-to-point.
		diagram.addEventListener('dblclick', (event) => event.stopImmediatePropagation());
		window.panzoomInstance = instance;
	}

	post({ type: 'ready' });
})();
