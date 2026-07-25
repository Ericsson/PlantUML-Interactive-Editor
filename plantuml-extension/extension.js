// VS Code extension lifecycle, commands, document listeners, and webview
// communication.
//
// The diagram is interactive: editing something in the webview rewrites the
// PlantUML source in the VS Code document. The rewriting itself is done by the
// existing Python backend, run as a sidecar (src/sidecar.js); webview markup
// lives in src/webviewContent.js.
//
// See docs/vscode_extension_interactivity.md for the overall design, in
// particular "The dangerous part - the echo loop" for why the document write
// path is guarded the way it is.
const path = require('path');
const vscode = require('vscode');
const { startSidecar, SidecarStartError } = require('./src/sidecar');
const { getWebviewContent } = require('./src/webviewContent');

const LIVE_UPDATE_DEBOUNCE_MS = 300;

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
 * The last text document the user was editing, so the command still works when
 * focus has moved to the diagram webview. @type {vscode.TextDocument | undefined}
 */
let lastActiveDocument;

function activate(context) {
	outputChannel = vscode.window.createOutputChannel('PlantUML Interactive');
	context.subscriptions.push(outputChannel);

	trackActiveDocument(context);

	const disposable = vscode.commands.registerCommand(
		'plantuml-interactive-editor.openDiagram',
		() => openDiagramPanel(context)
	);

	context.subscriptions.push(disposable);
	context.subscriptions.push({ dispose: disposeSidecar });
}

/**
 * Remember the most recent text document the user was editing.
 *
 * `vscode.window.activeTextEditor` is undefined whenever the focused tab is not
 * a text editor -- which includes our own diagram webview. Without this, the
 * command stops working as soon as the panel has focus.
 *
 * @param {vscode.ExtensionContext} context
 */
function trackActiveDocument(context) {
	const remember = (editor) => {
		if (editor && isEditableTextDocument(editor.document)) {
			lastActiveDocument = editor.document;
		}
	};

	remember(vscode.window.activeTextEditor);
	context.subscriptions.push(
		vscode.window.onDidChangeActiveTextEditor(remember)
	);
}

/**
 * Whether a document is one we can render and write back to.
 *
 * Deliberately not filtered by file extension or language: PlantUML source
 * lives in .puml, .plantuml, .iuml, .wsd, and plain .txt, and guessing wrong
 * is more annoying than rendering something that is not a diagram. Read-only
 * schemes are excluded because the whole point is writing edits back.
 *
 * @param {vscode.TextDocument} document
 * @returns {boolean}
 */
function isEditableTextDocument(document) {
	return document.uri.scheme === 'file' || document.uri.scheme === 'untitled';
}

/**
 * Pick the document the diagram should be opened for.
 *
 * @returns {vscode.TextDocument | undefined}
 */
function resolveTargetDocument() {
	const active = vscode.window.activeTextEditor?.document;

	if (active && isEditableTextDocument(active)) {
		return active;
	}

	if (lastActiveDocument && !lastActiveDocument.isClosed) {
		return lastActiveDocument;
	}

	return undefined;
}

/**
 * Start the sidecar if it is not already running, reusing one instance across
 * panels. Concurrent callers await the same start rather than racing to spawn
 * two servers.
 *
 * @returns {Promise<import('./src/sidecar').Sidecar>}
 */
function ensureSidecar() {
	if (sidecar && sidecar.isRunning) {
		return Promise.resolve(sidecar);
	}

	if (!sidecarStarting) {
		const jarPath =
			vscode.workspace.getConfiguration('plantumlInteractive').get('plantumlJar') ||
			process.env.PLANTUML_JAR;

		sidecarStarting = startSidecar({ jarPath, output: outputChannel })
			.then((started) => {
				sidecar = started;
				// A crash mid-session leaves every interaction silently failing;
				// clear our handle so the next open retries instead.
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
 * Open the diagram webview for the active editor's document, render it, and
 * keep document and diagram in sync in both directions.
 *
 * @param {vscode.ExtensionContext} context
 */
async function openDiagramPanel(context) {
	const document = resolveTargetDocument();

	if (!document) {
		// Says what is actually wrong. The old wording ("Open a PlantUML file
		// first") implied a file-type check that has never existed, and sent
		// people looking at their file extension instead of at focus.
		vscode.window.showErrorMessage(
			'No open file to render. Open a file containing PlantUML source — any ' +
				'extension works, including .txt — click into it, then run this command again.'
		);
		return;
	}

	let active;
	try {
		active = await ensureSidecar();
	} catch (err) {
		vscode.window.showErrorMessage(
			err instanceof SidecarStartError
				? err.message
				: `Unexpected error starting the PlantUML backend: ${err.message}`
		);
		return;
	}

	const mediaRoot = path.join(context.extensionPath, 'media');

	const panel = vscode.window.createWebviewPanel(
		'plantumlInteractiveDiagram',
		'PlantUML Interactive Diagram',
		vscode.ViewColumn.Beside,
		{
			enableScripts: true,
			// The reused frontend is loaded from disk as webview resources.
			localResourceRoots: [vscode.Uri.file(mediaRoot)],
			// Keep the diagram and its handlers alive when the tab is hidden;
			// rebuilding costs a full render plus a handler rewalk.
			retainContextWhenHidden: true
		}
	);

	panel.webview.html = getWebviewContent({
		apiBase: active.baseUrl,
		token: active.token,
		webview: panel.webview,
		mediaRoot
	});

	let debounceTimer;

	// Guard against reentrancy inside applyEdit. This is belt-and-braces: the
	// text-equality checks on both sides are what actually terminate the loop.
	let applyingEdit = false;

	const postDocument = () => {
		panel.webview.postMessage({
			type: 'documentChanged',
			text: document.getText()
		});
	};

	// Initial state, so the webview can render and cache the current text.
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
			await applyPuml(document, message.text, () => applyingEdit, (v) => {
				applyingEdit = v;
			});
		} else if (message.type === 'setHighlight') {
			applyHighlight(document, message.rows);
		} else if (message.type === 'log') {
			outputChannel?.appendLine(`[webview] ${message.message}`);
		} else if (message.type === 'ready') {
			outputChannel?.appendLine('[webview] frontend loaded');
		}
	});

	// Cursor -> diagram highlighting. VS Code has no per-line mouse-hover event
	// for text editors, so the web app's hover direction degrades to following
	// the caret. See the design doc, Phase 7.
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
 * The equality check is the primary defence against the write-back loop
 * described in the design doc: a document change caused by us posts
 * `documentChanged` back to the webview, whose own equality check stops there.
 * Comparing values rather than tracking whose turn it is means a genuine edit
 * can never be swallowed.
 *
 * @param {vscode.TextDocument} document
 * @param {string} text
 * @param {() => boolean} isApplying
 * @param {(value: boolean) => void} setApplying
 */
async function applyPuml(document, text, isApplying, setApplying) {
	if (typeof text !== 'string' || isApplying()) {
		return;
	}

	if (text === document.getText()) {
		return;
	}

	setApplying(true);
	try {
		const edit = new vscode.WorkspaceEdit();
		edit.replace(document.uri, fullRange(document), text);
		const applied = await vscode.workspace.applyEdit(edit);
		if (!applied) {
			vscode.window.showErrorMessage(
				'Could not write the diagram change into the document.'
			);
		}
	} finally {
		setApplying(false);
	}
}

/**
 * Paint the given puml lines in every editor showing `document`.
 *
 * This is the diagram -> editor direction: the webview's editor shim turns the
 * app code's Ace `addMarker` calls into a row list and posts it here.
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

/**
 * @param {vscode.TextDocument} document
 */
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

function deactivate() {
	disposeSidecar();
}

module.exports = {
	activate,
	deactivate,
	fullRange,
	isEditableTextDocument,
	resolveTargetDocument,
	trackActiveDocument
};
