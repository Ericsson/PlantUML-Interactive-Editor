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

// Makes the VS Code document look like an Ace editor.
//
// Extension-only, like the rest of static/vscode/; see fetchShim.js for why
// these files live in this package rather than in plantuml-extension/.
//
// The web app's interaction code (script.js, activity.js,
// sequence-*.js) is loaded into this webview unmodified. It reaches the
// source through exactly one object -- Ace's `editor` -- and through a
// surprisingly small slice of its API: 58 session.getValue() calls, two
// session.setValue(), a few markers, and a cursor read. This file supplies an
// object with that shape, backed by the VS Code document instead of Ace.
//
// The single most important line is session.setValue(): every one of the ~71
// diagram operations ends by calling setPuml(), which calls setValue(). Point
// it at the document and all of them write to the file.
//
(function () {
	/** Ace's Range, reduced to the four numbers the app code actually uses. */
	class Range {
		constructor(startRow, startColumn, endRow, endColumn) {
			this.start = { row: startRow, column: startColumn };
			this.end = { row: endRow, column: endColumn };
		}
	}

	// script.js runs `ace.require("ace/range").Range` at load time, before
	// any function is called, so this global must exist before it is loaded --
	// defining only `editor` would throw while parsing.
	window.ace = {
		require: (module) => (module === 'ace/range' ? { Range } : {}),
		edit: () => window.PlantumlEditorShim.current,
		define: () => {},
		config: { setModuleUrl: () => {} }
	};

	/**
	 * @param {(message: object) => void} postMessage channel to the extension host
	 * @returns {object} an Ace-shaped editor backed by the VS Code document
	 */
	function create(postMessage) {
		let text = '';
		let cursor = { row: 0, column: 0 };
		const changeHandlers = [];
		const cursorHandlers = [];

		/** Ace marker table. script.js's clearMarkers() iterates this and
		 *  removes entries whose clazz is "hover", so the shape matters. */
		let markers = {};
		let nextMarkerId = 1;

		const fire = (handlers) => handlers.forEach((handler) => handler({}));

		/** Push the currently marked rows to the host, which turns them into
		 *  editor decorations. Only "hover" markers are line highlights. */
		function syncDecorations() {
			const rows = new Set();
			for (const marker of Object.values(markers)) {
				if (marker.clazz !== 'hover') continue;
				for (let row = marker.range.start.row; row <= marker.range.end.row; row++) {
					rows.add(row);
				}
			}
			postMessage({ type: 'setHighlight', rows: [...rows] });
		}

		const session = {
			getValue: () => text,

			/**
			 * The door every diagram operation walks through. Instead of
			 * mutating an Ace buffer, ask the host to edit the document, then
			 * fire `change` so the app code re-renders as it expects to.
			 */
			setValue(next) {
				if (next === text) {
					return;
				}
				text = next;
				postMessage({ type: 'applyPuml', text: next });
				fire(changeHandlers);
			},

			on(event, handler) {
				if (event === 'change') {
					changeHandlers.push(handler);
				}
			},

			addMarker(range, clazz) {
				const id = nextMarkerId++;
				markers[id] = { id, range, clazz };
				syncDecorations();
				return id;
			},

			removeMarker(id) {
				delete markers[id];
				syncDecorations();
			},

			getMarkers: () => markers,

			selection: {
				on(event, handler) {
					if (event === 'changeCursor') {
						cursorHandlers.push(handler);
					}
				}
			},

			// Ace-only concerns with no VS Code equivalent.
			setMode() {},
			setOption() {}
		};

		const editor = {
			session,
			getCursorPosition: () => cursor,

			// Ace's own mouse events over the text. VS Code exposes no
			// per-line hover for text editors, so hover-highlight.js's
			// initEditorHoverHighlighting() binds to nothing and the
			// editor->diagram *hover* direction stays inactive. The cursor
			// direction still works, through changeCursor below.
			on() {},
			container: document.getElementById('editor'),

			setTheme() {},
			resize() {},

			/** Called by the host when the document changed.
			 *  @returns {boolean} whether this was new text. */
			applyDocumentText(next) {
				// The equality check that terminates the write-back loop: a
				// change we caused arrives back with text we already have.
				if (next === text) {
					return false;
				}
				text = next;
				fire(changeHandlers);
				return true;
			},

			/** Seed the initial text without triggering a render. */
			primeDocumentText(next) {
				text = next;
			},

			/** Called by the host when the cursor moved in the real editor. */
			applyCursor(position) {
				cursor = position;
				fire(cursorHandlers);
			}
		};

		window.PlantumlEditorShim.current = editor;
		return editor;
	}

	window.PlantumlEditorShim = { create, current: null };

	// script.js's renderPlantUml() mirrors the diagram into the page URL as
	// a shareable hash. A webview has no address bar and rewriting its URL can
	// throw, so make it a no-op rather than patching the shared file.
	if (window.history) {
		window.history.replaceState = () => {};
	}
})();
