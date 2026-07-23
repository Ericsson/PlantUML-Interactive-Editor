// VS Code extension lifecycle, commands, document listeners, and webview
// communication. PlantUML -> SVG rendering itself lives in
// src/plantumlRenderer.js; webview markup lives in src/webviewContent.js.
const vscode = require('vscode');
const {
	renderPlantUmlToSvg,
	PlantUmlConfigError,
	PlantUmlRenderError
} = require('./src/plantumlRenderer');
const { getWebviewContent } = require('./src/webviewContent');

const LIVE_UPDATE_DEBOUNCE_MS = 300;

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed
function activate(context) {
	const disposable = vscode.commands.registerCommand(
		'plantuml-interactive-editor.openDiagram',
		() => openDiagramPanel()
	);

	context.subscriptions.push(disposable);
}

/**
 * Open (or focus) the diagram webview panel for the active editor's
 * document, render its current content, and keep the diagram in sync as
 * the document changes.
 */
function openDiagramPanel() {
	const editor = vscode.window.activeTextEditor;

	if (!editor) {
		vscode.window.showErrorMessage('Open a PlantUML file first.');
		return;
	}

	const document = editor.document;

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
		renderPlantUmlToSvg(document.getText()).then(
			(svg) => {
				panel.webview.postMessage({ type: 'updateDiagram', svg });
			},
			(err) => {
				panel.webview.postMessage({
					type: 'renderError',
					message: describeRenderError(err)
				});
				if (err instanceof PlantUmlConfigError) {
					// Configuration problems are actionable and easy to miss
					// inside the webview, so also surface them as a
					// notification rather than failing silently.
					vscode.window.showErrorMessage(err.message);
				}
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
function deactivate() {}

module.exports = {
	activate,
	deactivate
};
