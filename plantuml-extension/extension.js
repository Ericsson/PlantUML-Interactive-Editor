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
// No rendering happens in Node. The extension runs the existing Flask app as a
// child process (src/sidecar.js) and POSTs to its /render route
// (src/renderClient.js); webview markup lives in src/webviewContent.js.
const vscode = require('vscode');
const { startSidecar, SidecarStartError } = require('./src/sidecar');
const { resolvePlantUmlJarPath, PlantUmlConfigError } = require('./src/plantumlJar');
const { renderPlantUmlToSvg, PlantUmlRenderError } = require('./src/renderClient');
const { getWebviewContent } = require('./src/webviewContent');

const LIVE_UPDATE_DEBOUNCE_MS = 300;

/** @type {import('./src/sidecar').Sidecar | undefined} */
let sidecar;
/** @type {Promise<import('./src/sidecar').Sidecar> | undefined} */
let sidecarStarting;
/** @type {vscode.OutputChannel | undefined} */
let outputChannel;

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
function activate(context) {
	// Python tracebacks and werkzeug's log land here. Without it a backend
	// that starts but misbehaves is invisible.
	outputChannel = vscode.window.createOutputChannel('PlantUML Interactive');
	context.subscriptions.push(outputChannel);

	// The child outlives every panel, so it is tied to the extension instead.
	context.subscriptions.push({ dispose: disposeSidecar });

	const disposable = vscode.commands.registerCommand(
		'plantuml-interactive-editor.openDiagram',
		() => openDiagramPanel()
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
				// A crash mid-session would otherwise leave every later render
				// failing against a dead process; clear our handle so the next
				// open retries instead.
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
 */
async function openDiagramPanel() {
	const editor = vscode.window.activeTextEditor;

	if (!editor) {
		vscode.window.showErrorMessage('Open a PlantUML file first.');
		return;
	}

	const document = editor.document;

	// Before spawning anything: a missing jar is the most common
	// misconfiguration, and serve.py only warns about it on stderr. Checking
	// here turns it into a notification naming the setting, and avoids
	// starting a backend that could not render anyway.
	//
	// The path is read into the child's environment at spawn time, so changing
	// the setting takes effect on the next backend start, not the next render.
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
			enableScripts: true
		}
	);

	panel.webview.html = getWebviewContent();

	let debounceTimer;

	const renderAndPost = () => {
		renderPlantUmlToSvg(active, document.getText()).then(
			(svg) => {
				panel.webview.postMessage({ type: 'updateDiagram', svg });
			},
			(err) => {
				const message = describeRenderError(err);
				panel.webview.postMessage({ type: 'renderError', message });
				outputChannel?.appendLine(`render failed: ${message}`);
			}
		);
	};

	// Initial render of the document as it is when the panel opens.
	renderAndPost();

	const changeListener = vscode.workspace.onDidChangeTextDocument((event) => {
		if (event.document !== document) {
			return;
		}

		clearTimeout(debounceTimer);
		debounceTimer = setTimeout(renderAndPost, LIVE_UPDATE_DEBOUNCE_MS);
	});

	panel.onDidDispose(() => {
		clearTimeout(debounceTimer);
		changeListener.dispose();
	});
}

/**
 * @param {Error} err
 * @returns {string} a user-facing message for a rendering failure.
 */
function describeRenderError(err) {
	if (err instanceof PlantUmlConfigError || err instanceof PlantUmlRenderError) {
		return err.message;
	}
	return `Unexpected error rendering PlantUML diagram: ${err.message}`;
}

// This method is called when your extension is deactivated
function deactivate() {
	disposeSidecar();
}

module.exports = {
	activate,
	deactivate
};
