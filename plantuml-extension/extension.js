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

// VS Code extension lifecycle, commands, document listeners, and webview
// communication.
//
// The diagram is interactive: editing something in it rewrites the PlantUML
// source in the VS Code document. The rewriting is done by the Python backend,
// which this file runs as a child process (src/sidecar.js) and which the
// webview calls directly; this file owns the document and is its only writer.
// The webview's page is rendered by that same backend and fetched by
// src/webviewPage.js.
const path = require('path');
const vscode = require('vscode');
const { startSidecar, SidecarStartError, TOKEN_HEADER } = require('./src/sidecar');
const { resolvePlantUmlJarPath, PlantUmlConfigError } = require('./src/plantumlJar');
const { fetchWebviewPage, vendorRoot, WebviewPageError } = require('./src/webviewPage');

const LIVE_UPDATE_DEBOUNCE_MS = 300;

/** Generous because rendering shells out to java, once per request. */
const RENDER_PNG_TIMEOUT_MS = 60000;

/**
 * Line highlight for the diagram -> editor direction: hovering an element in
 * the diagram paints the puml line that produced it. Created once, since each
 * decoration type is a resource VS Code tracks.
 */
const hoverDecoration = vscode.window.createTextEditorDecorationType({
	backgroundColor: new vscode.ThemeColor('editor.wordHighlightBackground'),
	isWholeLine: true
});

/** @type {import('./src/sidecar').Sidecar | undefined} */
let sidecar;
/** @type {Promise<import('./src/sidecar').Sidecar> | undefined} */
let sidecarStarting;
/** @type {vscode.OutputChannel | undefined} */
let outputChannel;

/**
 * Entry point, run the first time the command is invoked.
 *
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {
	// Where the backend's stderr goes: Python tracebacks and werkzeug's request
	// log. The only window into a child that starts but then misbehaves.
	outputChannel = vscode.window.createOutputChannel('PlantUML Interactive');
	context.subscriptions.push(outputChannel);

	// The child outlives every panel, so its disposal belongs to the extension.
	context.subscriptions.push({ dispose: disposeSidecar });

	const disposable = vscode.commands.registerCommand(
		'plantuml-interactive-editor.openDiagram',
		() => openDiagramPanel(context)
	);

	context.subscriptions.push(disposable);
}

/**
 * Start the sidecar if it is not already running, reusing one instance across
 * panels. Concurrent callers await the same start rather than racing to spawn
 * two servers.
 *
 * @param {string} jarPath validated by the caller, passed to the child's env
 * @returns {Promise<import('./src/sidecar').Sidecar>}
 */
function ensureSidecar(jarPath) {
	if (sidecar && sidecar.isRunning) {
		return Promise.resolve(sidecar);
	}

	if (!sidecarStarting) {
		sidecarStarting = startSidecar({ jarPath, output: outputChannel })
			.then((started) => {
				sidecar = started;
				// Drop the handle when the child dies, so the next open starts a
				// fresh one instead of rendering against a dead process forever.
				started.process.on('exit', () => {
					if (sidecar === started) {
						sidecar = undefined;
					}
				});
				return started;
			})
			.finally(() => {
				sidecarStarting = undefined;
			});
	}

	return sidecarStarting;
}

function disposeSidecar() {
	sidecar?.dispose();
	sidecar = undefined;
}

/**
 * Open a diagram webview panel for the active editor's document, render its
 * current content, and keep the diagram in sync as the document changes.
 *
 * @param {vscode.ExtensionContext} context
 */
async function openDiagramPanel(context) {
	const editor = vscode.window.activeTextEditor;

	if (!editor) {
		vscode.window.showErrorMessage('Open a PlantUML file first.');
		return;
	}

	const document = editor.document;

	// Checked before anything is spawned: serve.py only warns about a bad jar
	// on stderr, so catching it here makes it a notification naming the setting,
	// and skips starting a backend that could not render.
	//
	// The path enters the child's environment at spawn time, so a change to the
	// setting takes effect on the next backend start, not the next render.
	let jarPath;
	try {
		jarPath = resolvePlantUmlJarPath();
	} catch (err) {
		vscode.window.showErrorMessage(
			err instanceof PlantUmlConfigError
				? err.message
				: `Unexpected error resolving the PlantUML jar: ${err.message}`
		);
		return;
	}

	let active;
	try {
		active = await ensureSidecar(jarPath);
	} catch (err) {
		vscode.window.showErrorMessage(
			err instanceof SidecarStartError
				? err.message
				: `Unexpected error starting the PlantUML backend: ${err.message}`
		);
		return;
	}

	const panel = vscode.window.createWebviewPanel(
		'plantumlInteractiveDiagram',
		'PlantUML Interactive Diagram',
		vscode.ViewColumn.Beside,
		{
			enableScripts: true,
			// Only the browser libraries are loaded off disk; the page itself
			// and the rest of the frontend come over HTTP from the sidecar.
			localResourceRoots: [vendorRoot(context.extensionPath)],
			// Rebuilding a hidden panel costs a full render plus a rewalk of
			// every handler the frontend attached.
			retainContextWhenHidden: true
		}
	);

	// Fetched fresh on every panel open, which is what makes editing the
	// frontend a matter of reopening the panel.
	try {
		panel.webview.html = await fetchWebviewPage({
			sidecar: active,
			webview: panel.webview,
			extensionPath: context.extensionPath
		});
	} catch (err) {
		panel.dispose();
		vscode.window.showErrorMessage(
			err instanceof WebviewPageError
				? err.message
				: `Unexpected error loading the diagram frontend: ${err.message}`
		);
		return;
	}

	let debounceTimer;

	// Reentrancy guard for applyEdit only. The text comparisons on both sides
	// are what actually terminate the write-back loop.
	let applyingEdit = false;

	const postDocument = () => {
		panel.webview.postMessage({ type: 'documentChanged', text: document.getText() });
	};

	// The frontend renders itself from this, through the app's own
	// renderPlantUml(); the first message also primes its cached text.
	postDocument();

	const changeListener = vscode.workspace.onDidChangeTextDocument((event) => {
		if (event.document !== document) {
			return;
		}

		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(postDocument, LIVE_UPDATE_DEBOUNCE_MS);
	});

	const messageListener = panel.webview.onDidReceiveMessage(async (message) => {
		if (message.type === 'applyPuml') {
			if (applyingEdit) {
				return;
			}
			applyingEdit = true;
			try {
				await applyPuml(document, message.text);
			} finally {
				applyingEdit = false;
			}
		} else if (message.type === 'setHighlight') {
			applyHighlight(document, message.rows);
		} else if (message.type === 'savePng') {
			await savePng(document, active);
		} else if (message.type === 'ready') {
			outputChannel?.appendLine('[webview] frontend loaded');
		}
	});

	// Cursor -> diagram highlighting. VS Code exposes no per-line mouse-hover
	// event for text editors, so the web app's editor-to-diagram hover
	// direction degrades to following the caret.
	const selectionListener = vscode.window.onDidChangeTextEditorSelection((event) => {
		if (event.textEditor.document !== document) {
			return;
		}
		const position = event.selections[0].active;
		panel.webview.postMessage({
			type: 'cursorMoved',
			row: position.line,
			column: position.character
		});
	});

	panel.onDidDispose(() => {
		clearTimeout(debounceTimer);
		changeListener.dispose();
		messageListener.dispose();
		selectionListener.dispose();
		clearHighlight(document);
	});

	context.subscriptions.push(panel);
}

/**
 * Write `text` into `document` as a single undoable edit.
 *
 * The equality check is the primary defence against the write-back loop: an
 * edit we apply fires onDidChangeTextDocument, which posts documentChanged back
 * to the webview, whose own equality check stops there. Comparing values rather
 * than tracking whose turn it is means a genuine edit can never be swallowed.
 *
 * @param {vscode.TextDocument} document
 * @param {string} text
 */
async function applyPuml(document, text) {
	if (typeof text !== 'string' || text === document.getText()) {
		return;
	}

	const edit = new vscode.WorkspaceEdit();
	edit.replace(document.uri, fullRange(document), text);

	if (!(await vscode.workspace.applyEdit(edit))) {
		vscode.window.showErrorMessage('Could not write the diagram change into the document.');
	}
}

/**
 * Render the document as a PNG and write it wherever the user chooses.
 *
 * The webview posts a bare `savePng`; the source comes from the document,
 * which this process owns and which every diagram edit is written into before
 * a render can be asked for.
 *
 * @param {vscode.TextDocument} document
 * @param {import('./src/sidecar').Sidecar} sidecar a running sidecar
 */
async function savePng(document, sidecar) {
	let response;

	try {
		response = await fetch(`${sidecar.baseUrl}renderPNG`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				[TOKEN_HEADER]: sidecar.token
			},
			body: JSON.stringify({ plantuml: document.getText() }),
			signal: AbortSignal.timeout(RENDER_PNG_TIMEOUT_MS)
		});
	} catch (err) {
		vscode.window.showErrorMessage(`Could not render the diagram as a PNG: ${err.message}`);
		return;
	}

	if (!response.ok) {
		vscode.window.showErrorMessage(
			`The PlantUML backend returned ${response.status} for the PNG render.`
		);
		return;
	}

	// An empty body is a *successful* response here: the backend renders with
	// check=False and returns java's stdout whatever happened, so a jar that
	// failed to run arrives as 200 with nothing in it. Hence the length check
	// below, which keeps a zero-byte .png off disk.
	const png = new Uint8Array(await response.arrayBuffer());

	if (png.byteLength === 0) {
		vscode.window.showErrorMessage(
			'The PlantUML backend produced an empty PNG. Check the PlantUML Interactive output for the renderer error.'
		);
		return;
	}

	const target = await vscode.window.showSaveDialog({
		defaultUri: defaultPngUri(document),
		filters: { 'PNG image': ['png'] }
	});

	// Undefined when the dialog was cancelled, which is not a failure.
	if (!target) {
		return;
	}

	try {
		await vscode.workspace.fs.writeFile(target, png);
	} catch (err) {
		vscode.window.showErrorMessage(`Could not write ${target.fsPath}: ${err.message}`);
	}
}

/**
 * Where the save dialog should open: beside the document, under its own name.
 *
 * An unsaved document has no directory to sit beside -- its uri is
 * `untitled:Untitled-1` -- so it falls back to the workspace root, and then to
 * VS Code's own choice.
 *
 * @param {vscode.TextDocument} document
 * @returns {vscode.Uri | undefined}
 */
function defaultPngUri(document) {
	if (document.uri.scheme === 'file') {
		const { dir, name } = path.parse(document.uri.fsPath);
		return vscode.Uri.file(path.join(dir, `${name}.png`));
	}

	const folder = vscode.workspace.workspaceFolders?.[0];
	return folder && vscode.Uri.joinPath(folder.uri, 'diagram.png');
}

/**
 * Paint the given puml lines in every editor showing `document`.
 *
 * The diagram -> editor direction: the editor shim turns the app's Ace
 * addMarker calls into a row list and posts it here.
 *
 * @param {vscode.TextDocument} document
 * @param {number[]} rows zero-based line numbers
 */
function applyHighlight(document, rows) {
	const ranges = (rows ?? [])
		.filter((row) => row >= 0 && row < document.lineCount)
		.map((row) => document.lineAt(row).range);

	for (const editor of vscode.window.visibleTextEditors) {
		if (editor.document === document) {
			editor.setDecorations(hoverDecoration, ranges);
		}
	}
}

/** @param {vscode.TextDocument} document */
function clearHighlight(document) {
	applyHighlight(document, []);
}

/**
 * @param {vscode.TextDocument} document
 * @returns {vscode.Range} a range covering the whole document.
 */
function fullRange(document) {
	const lastLine = document.lineAt(document.lineCount - 1);
	return new vscode.Range(0, 0, lastLine.lineNumber, lastLine.text.length);
}

/** Called when VS Code shuts the extension down; stops the backend with it. */
function deactivate() {
	disposeSidecar();
}

module.exports = {
	activate,
	deactivate
};
