// The module 'vscode' contains the VS Code extensibility API
// Import the module and reference it with the alias vscode in your code below
const vscode = require('vscode');

// This method is called when your extension is activated
// Your extension is activated the very first time the command is executed

/**
 * @param {vscode.ExtensionContext} context
 */
function activate(context) {

	const disposable = vscode.commands.registerCommand(
		'plantuml-interactive-editor.openDiagram',
		() => {

			// Get the currently active VS Code editor
			const editor = vscode.window.activeTextEditor;

			if (!editor) {
				vscode.window.showErrorMessage(
					'Open a PlantUML file first.'
				);
				return;
			}

			const document = editor.document;

			// Get PlantUML source from VS Code itself
			const plantUmlCode = document.getText();

			// Open ONLY the diagram beside the normal VS Code editor
			const panel = vscode.window.createWebviewPanel(
				'plantumlInteractiveDiagram',
				'PlantUML Interactive Diagram',
				vscode.ViewColumn.Beside,
				{
					enableScripts: true
				}
			);

			panel.webview.html = getWebviewContent(
				plantUmlCode
			);
		}
	);

	context.subscriptions.push(disposable);
}


function getWebviewContent(plantUmlCode) {

	return `
		<!DOCTYPE html>

		<html lang="en">

		<head>
			<meta charset="UTF-8">

			<meta
				name="viewport"
				content="width=device-width, initial-scale=1.0"
			>

			<title>PlantUML Interactive Diagram</title>
		</head>

		<body>

			<h2>Interactive Diagram</h2>

			<div id="diagram">
				Diagram will go here.
			</div>

			<!-- Temporary: proves that we received
				 code from the VS Code editor -->

			<pre>
${escapeHtml(plantUmlCode)}
			</pre>

		</body>

		</html>
	`;
}


function escapeHtml(text) {
	return text
		.replace(/&/g, '&amp;')
		.replace(/</g, '&lt;')
		.replace(/>/g, '&gt;');
}


// This method is called when your extension is deactivated
function deactivate() {}


module.exports = {
	activate,
	deactivate
};
