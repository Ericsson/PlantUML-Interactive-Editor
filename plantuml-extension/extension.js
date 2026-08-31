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
//
// What the panel shows is not the document but a *region* of it -- a line range
// plus the indentation it carries; see src/sourceRegion.js. For a `.puml` file
// that region covers the whole document, which is why one code path serves both
// it and a diagram sitting in a Markdown code fence. Everything crossing the
// boundary is translated: the source sent out, the rewrite written back, the
// highlighted rows, the caret's row.
//
// That backend is installed on first use, out of a wheel inside the vsix, into
// a virtual environment under this extension's global storage; see
// src/backendInstall.js.
const fs = require('fs');
const path = require('path');
const vscode = require('vscode');
const settings = require('./src/settings');
const {
	startSidecar,
	resolvePythonPath,
	SidecarStartError,
	PythonConfigError,
	BackendMissingError,
	EXPECTED_BACKEND_VERSION,
	TOKEN_HEADER
} = require('./src/sidecar');
const {
	bundledWheel,
	managedVenv,
	installBackend,
	BundledWheelError,
	BackendInstallError
} = require('./src/backendInstall');
const { resolvePlantUmlJarPath, PlantUmlConfigError } = require('./src/plantumlJar');
const { fetchWebviewPage, vendorRoot, WebviewPageError } = require('./src/webviewPage');
const {
	wholeDocumentRegion,
	regionSource,
	indentSource,
	toDocumentRow,
	toRegionRow,
	containsLine
} = require('./src/sourceRegion');
const { findPlantUmlBlocks, blockToShow, blockToFollow } = require('./src/markdownBlocks');

const LIVE_UPDATE_DEBOUNCE_MS = 300;

/** Generous because rendering shells out to java, once per request. */
const RENDER_PNG_TIMEOUT_MS = 60000;

/**
 * How long to wait for the backend to actually exit when its directory is
 * about to be taken away from underneath it. See stopSidecarForReinstall.
 */
const SIDECAR_STOP_TIMEOUT_MS = 5000;

/** How long to keep trying to remove the managed venv before giving up. */
const VENV_DELETE_TIMEOUT_MS = 5000;

/** How long to wait between those attempts. */
const VENV_DELETE_RETRY_MS = 200;

/** Label of the action offered on errors the user fixes in Settings. */
const OPEN_SETTINGS = 'Open Settings';

/** Label of the action offered when the answer is in the output channel. */
const SHOW_OUTPUT = 'Show Output';

/** This command's title in the palette, as contributed in package.json. */
const OPEN_DIAGRAM_TITLE = 'PlantUML: Open Interactive Diagram';

/** The reinstall command's title, as contributed in package.json. */
const REINSTALL_TITLE = 'PlantUML: Reinstall Backend';

/** The file extensions the diagram panel follows; see isPlantUmlDocument. */
const PLANTUML_EXTENSIONS = new Set(['.puml', '.plantuml', '.pu', '.iuml', '.wsd', '.uml']);

/** How far into a plain-text file to look for a `@start…` block. */
const DIAGRAM_SNIFF_LINES = 200;

/**
 * The row posted for a caret that is not in the diagram on screen.
 *
 * Reading the prose around a diagram, or a different diagram in the same file,
 * leaves the caret on a line the diagram has no row for. A row no element can
 * own says exactly that: the frontend's cursor handler clears the highlight and
 * then looks this row up, finds nothing, and lights nothing -- so the diagram
 * stops pointing at a line the caret has left, instead of keeping the last one
 * lit. Nothing else in the app reads the cursor.
 */
const NO_DIAGRAM_ROW = -1;

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
/** @type {Promise<string> | undefined} */
let backendInstalling;
/** @type {vscode.OutputChannel | undefined} */
let outputChannel;
/**
 * The diagram panel this window has open, while it has one.
 *
 * One per window: the panel follows the active editor, so it serves every
 * diagram the window opens, and the command reveals it rather than opening
 * another.
 *
 * It also tells a backend death the user is waiting on from one they will never
 * see -- the sidecar outlives the panel, being disposed with the extension --
 * which is what reportBackendExit reads it for.
 *
 * @type {DiagramPanel | undefined}
 */
let diagramPanel;

/**
 * The panel being opened, while one is being opened.
 *
 * diagramPanel is only set once the page has loaded, several awaits in, so this
 * is what a second invocation made in the meantime sees. It awaits the open
 * already in flight, as in ensureSidecar and installBackendOnce.
 *
 * @type {Promise<void> | undefined}
 */
let diagramPanelOpening;

/**
 * The open diagram panel, and what the command needs of it.
 *
 * @typedef {object} DiagramPanel
 * @property {vscode.WebviewPanel} panel the panel itself, to reveal or dispose
 * @property {import('./src/sidecar').Sidecar} sidecar the backend its page was
 *   built against; a dead one leaves the panel unusable, see panelAction
 * @property {(document: vscode.TextDocument, caretLine?: number) => void} show
 *   point it at a file, resending the text and retitling the tab; the caret
 *   line, where one is known, chooses which diagram in a Markdown file
 */

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

	context.subscriptions.push(
		vscode.commands.registerCommand(
			'plantuml-interactive-editor.reinstallBackend',
			() => reinstallBackend(context)
		)
	);
}

/**
 * The interpreter the backend will be run with, installed if it is not there.
 *
 * @param {vscode.ExtensionContext} context
 * @returns {Promise<string | undefined>} the managed venv's interpreter, for
 *   startSidecar to resolve against, or undefined when this build ships no
 *   wheel to install
 */
async function ensureBackendPython(context) {
	const managedPython = managedPythonPath(context);

	try {
		await resolvePythonPath({ managedPython });
	} catch (err) {
		if (!(err instanceof BackendMissingError) || !managedPython) {
			throw err;
		}
		await installBackendOnce(context);
	}

	return managedPython;
}

/**
 * Where this build's backend would live, if it ships one.
 *
 * Undefined in a development checkout, where `backend/` has never been built:
 * resolution then falls back to the setting or PLANTUML_GUI_PYTHON, which is
 * what .vscode/launch.json sets for the Extension Development Host.
 *
 * @param {vscode.ExtensionContext} context
 * @returns {string | undefined}
 */
function managedPythonPath(context) {
	try {
		const wheel = bundledWheel(context.extensionPath);
		return managedVenv(context.globalStorageUri.fsPath, wheel.version).python;
	} catch (err) {
		if (err instanceof BundledWheelError) {
			outputChannel?.appendLine(`[backend] no bundled wheel: ${err.message}`);
			return undefined;
		}
		throw err;
	}
}

/**
 * Install the managed backend, showing progress, once per window.
 *
 * Concurrent callers await the same install, as with ensureSidecar: two
 * commands run in quick succession would otherwise put two progress
 * notifications on screen for the one directory. Windows racing each other is
 * settled by the rename in claim(), which is the only place that can settle it.
 *
 * @param {vscode.ExtensionContext} context
 * @returns {Promise<string>} the installed interpreter
 */
function installBackendOnce(context) {
	if (!backendInstalling) {
		backendInstalling = vscode.window
			.withProgress(
				{
					location: vscode.ProgressLocation.Notification,
					title: 'Setting up the PlantUML backend…'
				},
				() =>
					installBackend({
						extensionPath: context.extensionPath,
						globalStoragePath: context.globalStorageUri.fsPath,
						output: outputChannel
					})
			)
			.finally(() => {
				backendInstalling = undefined;
			});
	}

	return backendInstalling;
}

/**
 * Delete the managed backend and install it again.
 *
 * The recovery for a venv that is present but broken -- a disk that filled
 * during the first install, an interpreter upgraded out from under it, a
 * half-removed package. The running backend is stopped first, because it is the
 * process living in the directory about to be deleted.
 *
 * Everything unusual here comes from install() leaving an existing target
 * alone: any directory that survives means an install that does nothing, so a
 * step this cannot carry out must stop it rather than be worked around.
 *
 * @param {vscode.ExtensionContext} context
 */
async function reinstallBackend(context) {
	// Refused rather than queued behind an install already in flight, because
	// joining that one would be worse than doing nothing: installBackendOnce
	// hands back the promise of an install that started *before* the delete
	// below, and install() treats an existing target as a finished
	// install and returns success. So the await could resolve on a decision
	// made about the directory this is about to remove, and this would report a
	// reinstall while leaving no backend installed at all.
	if (backendInstalling) {
		vscode.window.showInformationMessage(
			`${REINSTALL_TITLE} cannot run while the backend is being installed. ` +
				'Wait for that to finish, then run it again.'
		);
		return;
	}

	let wheel;

	try {
		wheel = bundledWheel(context.extensionPath);
	} catch (err) {
		vscode.window.showErrorMessage(
			err instanceof BundledWheelError
				? `${REINSTALL_TITLE} is not available: ${err.message}`
				: `Unexpected error finding the bundled backend: ${err.message}`
		);
		return;
	}

	const venv = managedVenv(context.globalStorageUri.fsPath, wheel.version);

	await stopSidecarForReinstall();

	try {
		await removeManagedVenv(venv.dir);
	} catch (err) {
		outputChannel?.appendLine(`[backend] ${err.message}`);
		vscode.window.showErrorMessage(
			`${REINSTALL_TITLE} could not remove ${err.message}. Close any other ` +
				'window using the backend, or restart VS Code, and try again.'
		);
		return;
	}

	// An install started elsewhere in the meantime is a different install from
	// the one refused above: the venv is gone, so it is building the same fresh
	// directory this wants, and joining it is the right answer.
	try {
		await installBackendOnce(context);
	} catch (err) {
		await showInstallError(err);
		return;
	}

	vscode.window.showInformationMessage(
		`The PlantUML backend was reinstalled. Run "${OPEN_DIAGRAM_TITLE}" to use it.`
	);
}

/**
 * Stop the backend, and wait for it to be gone, before its directory goes.
 *
 * A start in flight is awaited rather than refused: `sidecar` is assigned only
 * once startSidecar resolves, so disposing during a start reaches nothing and
 * the child arrives moments later -- running out of a directory that has since
 * been deleted, serving open panels, with nothing holding a handle on it to
 * stop it. That wait is bounded on the other side by STARTUP_TIMEOUT_MS.
 *
 * @returns {Promise<boolean>} whether no backend is running any more
 */
async function stopSidecarForReinstall() {
	if (sidecarStarting) {
		try {
			await sidecarStarting;
		} catch {
			// startSidecar reports its own failures, and a start that failed
			// handed out no child that would need stopping.
		}
	}

	const running = sidecar;
	// Dropped here rather than left to stop(), so that a child which outlives
	// the wait below is at least no longer a backend anything can be given.
	sidecar = undefined;

	if (!running) {
		return true;
	}

	const stopped = await running.stop(SIDECAR_STOP_TIMEOUT_MS);

	if (!stopped) {
		outputChannel?.appendLine(
			`[backend] did not stop within ${SIDECAR_STOP_TIMEOUT_MS}ms; ` +
				'trying to remove its virtual environment anyway'
		);
	}

	return stopped;
}

/**
 * Remove the managed venv, or say why it is still there.
 *
 * Retried, because the interpreter just killed can hold the directory for a
 * moment longer: Windows will not unlink a running executable's image, and the
 * child's exit event is not a promise that its handles have been released.
 *
 * Reported rather than swallowed, because install() leaves an existing
 * target alone. A delete that quietly failed would be followed by an install
 * that does nothing, and by a notification saying the backend was reinstalled
 * -- the one lie a repair command cannot afford, since the user would have no
 * reason to look any further.
 *
 * @param {string} dir the venv directory
 * @param {object} [options] seams for the tests, which have no way to lock a
 *   directory on every platform this runs on
 * @param {(uri: vscode.Uri) => Thenable<void>} [options.remove] the delete to call
 * @param {number} [options.timeoutMs] how long to keep trying it
 * @throws {Error} when the directory is still there once the time is up; the
 *   message names the directory and is written for a notification
 */
async function removeManagedVenv(dir, options = {}) {
	const { remove = deleteRecursively, timeoutMs = VENV_DELETE_TIMEOUT_MS } = options;
	const deadline = Date.now() + timeoutMs;
	let lastError;

	// Nothing there is the normal case for a first run, and is also the goal,
	// so existence -- not the delete's own answer -- is what this waits on.
	while (fs.existsSync(dir)) {
		try {
			await remove(vscode.Uri.file(dir));
		} catch (err) {
			lastError = err;
		}

		if (!fs.existsSync(dir)) {
			return;
		}

		if (Date.now() >= deadline) {
			throw new Error(
				`the virtual environment at "${dir}": ` +
					`${lastError ? lastError.message : 'it is still there'}`
			);
		}

		await new Promise((resolve) => setTimeout(resolve, VENV_DELETE_RETRY_MS));
	}
}

/**
 * @param {vscode.Uri} uri
 * @returns {Thenable<void>}
 */
function deleteRecursively(uri) {
	return vscode.workspace.fs.delete(uri, { recursive: true, useTrash: false });
}

/**
 * Start the sidecar if it is not already running, reusing one instance across
 * panels. Concurrent callers await the same start rather than racing to spawn
 * two servers.
 *
 * @param {string} jarPath validated by the caller, passed to the child's env
 * @param {string | undefined} managedPython the interpreter ensureBackendPython
 *   made sure of, offered to resolvePythonPath as one of its sources
 * @returns {Promise<import('./src/sidecar').Sidecar>}
 */
function ensureSidecar(jarPath, managedPython) {
	if (sidecar && sidecar.isRunning) {
		return Promise.resolve(sidecar);
	}

	if (!sidecarStarting) {
		sidecarStarting = startSidecar({ jarPath, managedPython, output: outputChannel })
			.then((started) => {
				warnOnBackendVersionMismatch(started);
				sidecar = started;
				// Drop the handle when the child dies, so the next open starts a
				// fresh one instead of rendering against a dead process forever.
				started.process.on('exit', (code, signal) => {
					if (sidecar === started) {
						sidecar = undefined;
					}
					reportBackendExit(started, code, signal);
				});
				return started;
			})
			.finally(() => {
				sidecarStarting = undefined;
			});
	}

	return sidecarStarting;
}

/**
 * Announce a backend that went away on its own.
 *
 * Always logged; only raised as a notification when the panel is open. The
 * sidecar outlives the panel, so without that gate, closing the diagram and
 * carrying on with the day would still be interrupted by an error about a
 * diagram that is not there -- and the recovery this offers, reopening the
 * panel, is not something the user asked to be told about.
 *
 * The notification says only what to do. Reopening the panel is the whole
 * remedy: ensureSidecar spawns a fresh child, since the handle was dropped when
 * this one died. The old panel cannot be salvaged either way -- its page holds
 * the dead child's address and token -- so there is nothing to choose between.
 *
 * Silent either way when we asked for the stop (dispose on deactivate), and
 * when the child never got as far as being handed out -- startSidecar reports
 * its own failures, with a message that says what to install.
 *
 * @param {import('./src/sidecar').Sidecar} stopped
 * @param {number | null} code
 * @param {string | null} signal
 */
async function reportBackendExit(stopped, code, signal) {
	if (stopped.disposing) {
		return;
	}

	const cause = signal ? `signal ${signal}` : `exit code ${code}`;
	outputChannel?.appendLine(`[backend] the PlantUML backend stopped (${cause})`);

	if (!diagramPanel) {
		return;
	}

	// The cause stays out of the notification: a signal number tells the user
	// nothing they can act on, and the only action is the same either way. It is
	// on the line just logged, which Show Output goes to.
	const choice = await vscode.window.showErrorMessage(
		`The PlantUML backend stopped. Run "${OPEN_DIAGRAM_TITLE}" again to restart it.`,
		SHOW_OUTPUT
	);

	if (choice === SHOW_OUTPUT) {
		outputChannel?.show();
	}
}

/**
 * Log a request from the webview that never reached the sidecar.
 *
 * The webview talks to the sidecar directly, so this process sees none of that
 * traffic and werkzeug's request log -- the output channel's record of the
 * requests that did arrive -- stops dead when the backend does. The frontend's
 * fetch shim posts the failures so that the channel shows those too, instead of
 * simply going quiet while the panel stops responding.
 *
 * Output only, no notification: one diagram gesture fires several requests, and
 * the diagnosis worth interrupting the user for is the child's exit, which
 * reportBackendExit announces once.
 *
 * @param {{ route?: string, detail?: string }} message
 */
function reportBackendUnreachable({ route, detail }) {
	outputChannel?.appendLine(
		`[webview] request to ${route ?? '<unknown>'} did not reach the backend: ` +
			`${detail ?? 'no detail given'}`
	);
}

function disposeSidecar() {
	sidecar?.dispose();
	sidecar = undefined;
}

/**
 * Report a configuration problem, with a way to go and fix it.
 *
 * The message names the setting, but this extension is installed from a vsix by
 * coworkers who have no particular reason to know where the Settings UI is, so
 * the notification carries them there. Reserved for failures whose answer is a
 * setting; see the call sites.
 *
 * @param {string} message
 */
async function showConfigError(message) {
	const choice = await vscode.window.showErrorMessage(message, OPEN_SETTINGS);

	if (choice === OPEN_SETTINGS) {
		// Opens the Settings UI with the search box pre-filled, so both of this
		// extension's settings are on screen and nothing else is.
		await vscode.commands.executeCommand('workbench.action.openSettings', settings.SECTION);
	}
}

/**
 * Report a failed install, with the log that says what pip made of it.
 *
 * @param {Error} err
 */
async function showInstallError(err) {
	const choice = await vscode.window.showErrorMessage(
		err instanceof BackendInstallError || err instanceof BundledWheelError
			? err.message
			: `Unexpected error installing the PlantUML backend: ${err.message}`,
		SHOW_OUTPUT
	);

	if (choice === SHOW_OUTPUT) {
		outputChannel?.show();
	}
}

/**
 * Warn, once per sidecar start, when the running backend is not the version
 * this extension was built against.
 *
 * The build-time pairing (scripts/check_app_versions.py) holds for the wheel
 * inside this vsix, so the backend the extension installs for itself always
 * matches. This catches one that came from somewhere else: an interpreter named
 * by the setting or by PLANTUML_GUI_PYTHON, carrying whichever version of the
 * package happens to be installed in it.
 *
 * A mismatch still runs -- the routes this extension calls have generally not
 * gone away across a minor version -- so this warns rather than blocking.
 *
 * @param {import('./src/sidecar').Sidecar} activeSidecar
 */
function warnOnBackendVersionMismatch(activeSidecar) {
	const backendVersion = activeSidecar.backendVersion;

	if (backendVersion === EXPECTED_BACKEND_VERSION) {
		return;
	}

	vscode.window.showWarningMessage(
		`PlantUML backend ${backendVersion ?? 'of unknown version'} does not match ` +
			`this extension (expects ${EXPECTED_BACKEND_VERSION}). It is not the one ` +
			'this extension installs: update the interpreter it came from, or clear ' +
			`"${settings.SECTION}.pythonPath" to use the bundled backend.`
	);
}

/**
 * Show the diagram for the active editor's document: reveal the open panel, or
 * open one.
 *
 * @param {vscode.ExtensionContext} context
 * @returns {Promise<void>}
 */
function openDiagramPanel(context) {
	const open = diagramPanel;
	const action = panelAction(open);

	if (open && action === 'reveal') {
		// The panel follows the active editor on its own, but only for the
		// files isPlantUmlDocument accepts. Run on any other file, the command
		// means *that* file -- it "opens whatever the user ran it on" -- so it
		// is pointed at it here.
		const editor = vscode.window.activeTextEditor;

		if (editor) {
			open.show(editor.document, editor.selection.active.line);
		}

		open.panel.reveal();
		return Promise.resolve();
	}

	if (open && action === 'replace') {
		// Disposal clears diagramPanel, leaving the open below to build a fresh
		// panel against a live backend.
		open.panel.dispose();
	}

	if (!diagramPanelOpening) {
		diagramPanelOpening = createDiagramPanel(context).finally(() => {
			diagramPanelOpening = undefined;
		});
	}

	return diagramPanelOpening;
}

/**
 * What the command should do about the panel that is already open.
 *
 * A panel is revealed unless the backend its page was built against has since
 * died: the page holds that child's address and token, so nothing it posts can
 * render, and it is replaced instead. That is the recovery reportBackendExit
 * points the user at -- run the command again.
 *
 * @param {DiagramPanel | undefined} open
 * @returns {'open' | 'reveal' | 'replace'}
 */
function panelAction(open) {
	if (!open) {
		return 'open';
	}

	return open.sidecar.isRunning ? 'reveal' : 'replace';
}

/**
 * Open a diagram webview panel for the active editor's document, render its
 * current content, and keep the diagram in sync as the document changes.
 *
 * @param {vscode.ExtensionContext} context
 */
async function createDiagramPanel(context) {
	const editor = vscode.window.activeTextEditor;

	if (!editor) {
		vscode.window.showErrorMessage('Open a PlantUML file first.');
		return;
	}

	// The document this panel shows, and the one every listener below reads:
	// the writer in applyPuml, the PNG source, the highlight target. It moves
	// when the user switches to another PlantUML file (see the active-editor
	// listener), so it is read at use rather than captured.
	let document = editor.document;

	// Which diagram in it, when the document holds diagrams rather than being
	// one. Undefined for a PlantUML file, whose diagram is the whole of it.
	//
	// Resolved here, before anything is spawned: a Markdown file with no block
	// is nothing to open a panel for, and starting a backend first would be a
	// slow way to say so.
	/** @type {import('./src/markdownBlocks').MarkdownBlock | undefined} */
	let activeBlock = isMarkdownDocument(document)
		? blockToShow(document.getText(), editor.selection.active.line)
		: undefined;

	if (isMarkdownDocument(document) && !activeBlock) {
		vscode.window.showErrorMessage(
			`${path.basename(document.fileName)} has no \`\`\`plantuml block to show. ` +
				'Add one, or run this on a PlantUML file.'
		);
		return;
	}

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
		if (err instanceof PlantUmlConfigError) {
			await showConfigError(err.message);
		} else {
			vscode.window.showErrorMessage(
				`Unexpected error resolving the PlantUML jar: ${err.message}`
			);
		}
		return;
	}

	let active;
	try {
		const managedPython = await ensureBackendPython(context);
		active = await ensureSidecar(jarPath, managedPython);
	} catch (err) {
		// A generic SidecarStartError is a backend that failed to boot -- a
		// missing package, a traceback, a port that never answered -- and
		// describeStartFailure has already said what to do about it, which is
		// not to visit Settings.
		if (err instanceof BackendInstallError || err instanceof BundledWheelError) {
			await showInstallError(err);
		} else if (err instanceof PythonConfigError) {
			await showConfigError(err.message);
		} else {
			vscode.window.showErrorMessage(
				err instanceof SidecarStartError
					? err.message
					: `Unexpected error starting the PlantUML backend: ${err.message}`
			);
		}
		return;
	}

	const panel = vscode.window.createWebviewPanel(
		'plantumlInteractiveDiagram',
		panelTitle(document, activeBlock),
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
	panel.iconPath = vscode.Uri.joinPath(context.extensionUri, 'icon.png');

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

	/**
	 * The part of the document to act on, located afresh.
	 *
	 * Deliberately not a remembered range. A block's lines move under every
	 * edit -- its own rewrites change how many it has, and typing above it
	 * moves all of them -- so the range is found in the text as it is now,
	 * every time it is needed. Nothing downstream can then write into a span
	 * that has stopped being the block.
	 *
	 * The block is recognised by its opening fence, which stays put under any
	 * edit inside it. An edit *above* it moves the fence too, and this stops
	 * finding it; see the undefined case at each call site, which is why they
	 * all have one.
	 *
	 * @returns {import('./src/sourceRegion').SourceRegion | undefined} undefined
	 *   when the block the panel is on is no longer in the document
	 */
	const currentRegion = () => {
		const text = document.getText();

		if (!activeBlock) {
			return wholeDocumentRegion(text);
		}

		return findPlantUmlBlocks(text).find(
			(block) => block.fenceLine === activeBlock.fenceLine
		);
	};

	// Hands the diagram over; the frontend renders itself from it through the
	// app's own renderPlantUml(). The text is read at call time, so whatever the
	// document holds when this runs is what the diagram shows. Called from the
	// `ready` handler for the first render, from the change listener for every
	// edit, and on a switch to another file.
	const postDocument = () => {
		const region = currentRegion();

		// Nothing to send: the panel keeps the diagram it is showing rather
		// than being blanked, which is what the user asked for -- the last
		// diagram stays until another one is chosen.
		if (!region) {
			return;
		}

		panel.webview.postMessage({
			type: 'documentChanged',
			text: regionSource(document.getText(), region)
		});
	};

	// Point the panel at a diagram of the document it is already on: retitle,
	// resend, and drop what belonged to the diagram being left. The one way the
	// shown block changes, called by the caret listener and by showDocument.
	/** @param {import('./src/markdownBlocks').MarkdownBlock} [block] */
	const showBlock = (block) => {
		// Painted for the diagram being left, and about to mean nothing.
		clearHighlight(document);
		// A post left pending by the previous diagram would fire just after
		// this one and resend what it is about to send.
		clearTimeout(debounceTimer);

		activeBlock = block;
		panel.title = panelTitle(document, block);
		outputChannel?.appendLine(`[panel] now showing ${panelSubject(document, block)}`);
		postDocument();
	};

	/**
	 * Switch to the diagram the caret has moved into, if it moved into another.
	 *
	 * The whole of the caret-picks-the-diagram behaviour. Everything about when
	 * *not* to switch is in blockToFollow, which is where it can be tested: the
	 * caret in prose, on a fence, or in the diagram already on screen all leave
	 * the panel where it is.
	 *
	 * This is also how the panel recovers after an edit above the block moved
	 * its fence out from under `activeBlock`: the caret coming back into the
	 * block finds it at its new line and adopts it.
	 *
	 * @param {number} caretLine zero-based
	 */
	const followCaretIntoBlock = (caretLine) => {
		if (!isMarkdownDocument(document)) {
			return;
		}

		const next = blockToFollow(document.getText(), caretLine, activeBlock);

		if (next) {
			showBlock(next);
		}
	};

	// The one way onto another file: retitle, resend, and drop what belonged to
	// the file being left. Called by the active-editor listener below, and by
	// the command when it reveals this panel.
	/**
	 * @param {vscode.TextDocument} next
	 * @param {number} [caretLine] where the caret is in `next`, when it is known
	 */
	const showDocument = (next, caretLine) => {
		if (next === document) {
			return;
		}

		const nextBlock = isMarkdownDocument(next)
			? blockToShow(next.getText(), caretLine)
			: undefined;

		if (isMarkdownDocument(next) && !nextBlock) {
			// Only the command reaches this: the active-editor listener follows
			// nothing isPlantUmlDocument rejects, and it rejects Markdown with
			// no block. So it is an explicit request, and it gets an answer
			// rather than a panel that quietly did nothing.
			vscode.window.showInformationMessage(
				`${path.basename(next.fileName)} has no \`\`\`plantuml block. The diagram ` +
					`panel is still showing ${path.basename(document.fileName)}.`
			);
			return;
		}

		// Painted for the file the panel is leaving, and cleared before
		// `document` moves on, since that is the handle the decorations are on.
		clearHighlight(document);

		document = next;
		showBlock(nextBlock);
	};

	// Handed to the window from here, not from createWebviewPanel: the early
	// returns above dispose the panel before onDidDispose is registered, so a
	// handle taken there would outlive the panel it names.
	diagramPanel = { panel, sidecar: active, show: showDocument };

	// One panel serves every diagram in the window: opening another PlantUML
	// file points it at that file, the way the Markdown preview follows the
	// editor. The command is invoked once and the panel keeps up from there.
	//
	// Only PlantUML files take it over, by isPlantUmlDocument's reading; the
	// panel stays on its current file while the user is in a .py or a settings
	// tab, and while the panel itself has focus, which leaves no active text
	// editor at all.
	const activeEditorListener = vscode.window.onDidChangeActiveTextEditor((next) => {
		if (!next || !isPlantUmlDocument(next.document)) {
			return;
		}

		showDocument(next.document, next.selection.active.line);
	});

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
				await applyPuml(document, currentRegion(), message.text);
			} finally {
				applyingEdit = false;
			}
		} else if (message.type === 'setHighlight') {
			applyHighlight(document, currentRegion(), message.rows);
		} else if (message.type === 'savePng') {
			await savePng(document, active);
		} else if (message.type === 'backendUnreachable') {
			reportBackendUnreachable(message);
		} else if (message.type === 'ready') {
			outputChannel?.appendLine('[webview] frontend loaded');
			// `ready` is the frontend's word that its `message` listener is
			// live, which makes this the first moment a post reaches it: the
			// channel delivers only to a listening page, and drops the rest in
			// silence. So the first document goes out from here, priming the
			// page's cached text and triggering its initial render.
			postDocument();
		}
	});

	// Cursor -> diagram highlighting, and -- in a Markdown file -- which diagram
	// the panel is on. VS Code exposes no per-line mouse-hover event for text
	// editors, so the web app's editor-to-diagram hover direction degrades to
	// following the caret, and the caret is also the only gesture available for
	// choosing between the diagrams a document holds.
	const selectionListener = vscode.window.onDidChangeTextEditorSelection((event) => {
		if (event.textEditor.document !== document) {
			return;
		}

		const position = event.selections[0].active;

		followCaretIntoBlock(position.line);

		const region = currentRegion();

		panel.webview.postMessage({
			type: 'cursorMoved',
			row:
				region && containsLine(region, position.line)
					? toRegionRow(region, position.line)
					: NO_DIAGRAM_ROW,
			column: position.character
		});
	});

	panel.onDidDispose(() => {
		// Only while this is still the window's panel: a replaced one is
		// disposed alongside its successor, and must not clear its handle.
		if (diagramPanel?.panel === panel) {
			diagramPanel = undefined;
		}
		clearTimeout(debounceTimer);
		activeEditorListener.dispose();
		changeListener.dispose();
		messageListener.dispose();
		selectionListener.dispose();
		clearHighlight(document);
	});

	context.subscriptions.push(panel);
}

/**
 * Write `source` into `region` of `document` as a single undoable edit.
 *
 * The region is the only part of the file the diagram speaks for. Replacing it
 * rather than the whole document is what lets a diagram live in a Markdown
 * fence: the prose around it is not in the edit at all, so it cannot be
 * reformatted, and the fences themselves stay as the author wrote them.
 *
 * The equality check is the primary defence against the write-back loop: an
 * edit we apply fires onDidChangeTextDocument, which posts documentChanged back
 * to the webview, whose own equality check stops there. Comparing values rather
 * than tracking whose turn it is means a genuine edit can never be swallowed.
 * It compares the *region's* text, since that is what the webview was given.
 *
 * @param {vscode.TextDocument} document
 * @param {import('./src/sourceRegion').SourceRegion | undefined} region where
 *   the diagram lives now, or undefined if it could not be found
 * @param {string} source the diagram, without the region's indentation
 */
async function applyPuml(document, region, source) {
	if (typeof source !== 'string') {
		return;
	}

	// Refused rather than aimed at where the block used to be. The panel can
	// outlive the block it is showing -- an edit above it moves it, a deletion
	// takes it away -- and a diagram gesture arriving then would otherwise
	// overwrite whatever lines now sit at those numbers, which is prose.
	if (!region) {
		outputChannel?.appendLine(
			'[panel] a diagram change was not written: the block it belongs to was ' +
				'not found in the document'
		);
		return;
	}

	if (source === regionSource(document.getText(), region)) {
		return;
	}

	const edit = new vscode.WorkspaceEdit();
	edit.replace(document.uri, regionRange(document, region), indentSource(source, region.indent));

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
 * Which file the panel is showing, in its tab.
 *
 * The panel follows the active editor, so its title names the file it is
 * currently pointed at. One Markdown file can hold several diagrams, so it
 * names the block too, by its opening fence -- the line the reader can see, and
 * one-based as the editor's own gutter is.
 *
 * @param {vscode.TextDocument} document
 * @param {import('./src/markdownBlocks').MarkdownBlock} [block] the diagram
 *   being shown, when the document holds more than the one
 * @returns {string}
 */
function panelTitle(document, block) {
	const name = path.basename(document.fileName);

	return block ? `PlantUML: ${name}:${block.fenceLine + 1}` : `PlantUML: ${name}`;
}

/**
 * What the panel is showing, for the output channel.
 *
 * The full path, as the log has always carried, plus the fence for a block --
 * in the `file:line` shape terminals and editors make clickable.
 *
 * @param {vscode.TextDocument} document
 * @param {import('./src/markdownBlocks').MarkdownBlock} [block]
 * @returns {string}
 */
function panelSubject(document, block) {
	return block ? `${document.fileName}:${block.fenceLine + 1}` : document.fileName;
}

/**
 * Whether `document` holds diagrams rather than being one.
 *
 * The language id alone, unlike the PlantUML case below: VS Code ships the
 * Markdown language itself, so every `.md` and `.markdown` file arrives with
 * this id and nothing else claims it. There is no zoo of extensions to enumerate
 * and no other extension's choice to honour.
 *
 * @param {vscode.TextDocument} document
 * @returns {boolean}
 */
function isMarkdownDocument(document) {
	return document.languageId === 'markdown';
}

/**
 * Whether the panel should follow `document` when it becomes active.
 *
 * No single signal identifies a PlantUML source: VS Code registers no language
 * for one, the id a `.puml` file ends up with depends on which other PlantUML
 * extension is installed, and plenty of diagrams live in `.txt`. So:
 *
 *   - a PlantUML file extension, or a `plantuml` language id, is followed
 *     whatever the file holds. An empty `.puml` is a diagram being started.
 *   - a Markdown file is followed once it holds a ```plantuml block. The panel
 *     shows one block of it rather than the file, so a document with none is
 *     one it has nothing to show for.
 *   - a plain-text file is followed once it opens a `@start…` block. The name
 *     says nothing, so the content decides, which is what lets `.txt` work and
 *     what leaves a notes file alone.
 *   - any other language is left alone. The whole document is the source, so a
 *     diagram quoted in a docstring would be rendered with the code around it.
 *
 * This gates the automatic following only; the command opens whatever the user
 * ran it on.
 *
 * @param {vscode.TextDocument} document
 * @returns {boolean}
 */
function isPlantUmlDocument(document) {
	if (document.languageId === 'plantuml') {
		return true;
	}

	if (PLANTUML_EXTENSIONS.has(path.extname(document.uri.path).toLowerCase())) {
		return true;
	}

	if (isMarkdownDocument(document)) {
		// Read whole, with no equivalent of DIAGRAM_SNIFF_LINES: a diagram
		// belongs wherever the prose put it, and prose is what the top of a
		// documentation file is for.
		return findPlantUmlBlocks(document.getText()).length > 0;
	}

	return document.languageId === 'plaintext' && opensDiagramBlock(document);
}

/**
 * Whether the document's opening lines start a PlantUML block.
 *
 * Any `@start…` counts, not just `@startuml`: which flavour a file holds is not
 * this function's business.
 *
 * Only the head is read. A file that begins with something other than its
 * diagram is prose that mentions one, and a plain-text file can be a log of any
 * size.
 *
 * @param {vscode.TextDocument} document
 * @returns {boolean}
 */
function opensDiagramBlock(document) {
	// The range is clamped to the document, so a short file reads whole.
	const head = document.getText(new vscode.Range(0, 0, DIAGRAM_SNIFF_LINES, 0));

	return /^[ \t]*@start\w+/m.test(head);
}

/**
 * Paint the given diagram rows in every editor showing `document`.
 *
 * The diagram -> editor direction: the editor shim turns the app's Ace
 * addMarker calls into a row list and posts it here. Those rows are the
 * diagram's, so they are translated into the document's before anything is
 * painted -- a diagram in a Markdown fence starts at line 1 of itself and
 * somewhere else entirely in the file.
 *
 * @param {vscode.TextDocument} document
 * @param {import('./src/sourceRegion').SourceRegion | undefined} region where
 *   the diagram lives now, or undefined if it could not be found
 * @param {number[]} rows zero-based, relative to the region
 */
function applyHighlight(document, region, rows) {
	// Without a region there is no line these rows could name, so the highlight
	// comes off rather than being left where the diagram used to be.
	const lines = !region
		? []
		: (rows ?? [])
				.map((row) => toDocumentRow(region, row))
				// A row the diagram has and the document does not: a marker on a
				// line an edit has just removed.
				.filter((line) => line >= 0 && line < document.lineCount);

	paintHighlight(
		document,
		lines.map((line) => document.lineAt(line).range)
	);
}

/**
 * Drop the highlight from every editor showing `document`.
 *
 * Not expressed as an empty row list through applyHighlight, because clearing
 * is the one case with no rows to translate and so no region to translate them
 * against -- which is exactly when it is called, on the way off a file.
 *
 * @param {vscode.TextDocument} document
 */
function clearHighlight(document) {
	paintHighlight(document, []);
}

/**
 * @param {vscode.TextDocument} document
 * @param {vscode.Range[]} ranges
 */
function paintHighlight(document, ranges) {
	for (const editor of vscode.window.visibleTextEditors) {
		if (editor.document === document) {
			editor.setDecorations(hoverDecoration, ranges);
		}
	}
}

/**
 * @param {vscode.TextDocument} document
 * @param {import('./src/sourceRegion').SourceRegion} region
 * @returns {vscode.Range} a range covering the region's whole lines.
 */
function regionRange(document, region) {
	// Clamped so that lineAt cannot throw inside a message handler. The clamp
	// is not a correctness measure: a region that no longer matches the document
	// must not be written into at all, rather than aimed at whatever is there
	// now, so that guard belongs with the region and not here.
	const endLine = Math.min(region.endLine, document.lineCount - 1);

	return new vscode.Range(region.startLine, 0, endLine, document.lineAt(endLine).text.length);
}

/** Called when VS Code shuts the extension down; stops the backend with it. */
function deactivate() {
	disposeSidecar();
}

module.exports = {
	activate,
	deactivate,
	// The panel's targeting rules, exported for the tests: which files it
	// follows and what it calls itself once it has.
	isPlantUmlDocument,
	panelTitle,
	// Exported for the tests: what a second run of the command does with the
	// panel the first one opened.
	panelAction,
	// Exported for the tests: which interpreter a window ends up using, and
	// whether it had to install one to get there.
	ensureBackendPython,
	// Exported for the tests: the reinstall's one step whose failure must not
	// pass for success, since an install over a surviving venv does nothing.
	removeManagedVenv
};
