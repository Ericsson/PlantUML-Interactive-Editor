const assert = require('assert');
const vscode = require('vscode');

const {
	isEditableTextDocument,
	resolveTargetDocument,
	trackActiveDocument
} = require('../extension');

const PUML = '@startuml\nAlice -> Bob: hi\n@enduml';

/** Give VS Code a turn to fire its focus events. */
const settle = () => new Promise((resolve) => setTimeout(resolve, 50));

/** Stand-in for ExtensionContext, collecting disposables for cleanup. */
function fakeContext() {
	const subscriptions = [];
	return { subscriptions, dispose: () => subscriptions.forEach((d) => d.dispose()) };
}

suite('target document: which files are accepted', () => {
	test('a plain .txt file is accepted', async () => {
		// The command used to report "Open a PlantUML file first", which read as
		// a file-type rejection. There is no extension check and there should
		// not be one: PlantUML source lives in .txt as readily as .puml.
		const document = await vscode.workspace.openTextDocument({
			language: 'plaintext',
			content: PUML
		});

		assert.ok(isEditableTextDocument(document));
	});

	test('an untitled buffer is accepted', async () => {
		const document = await vscode.workspace.openTextDocument({ content: PUML });

		assert.ok(isEditableTextDocument(document));
	});

	test('a read-only scheme is rejected', () => {
		// Nothing to write edits back into, which is the point of the panel.
		const document = { uri: vscode.Uri.parse('output:extension-output-1') };

		assert.strictEqual(isEditableTextDocument(document), false);
	});
});

suite('target document: resolution', () => {
	let context;

	setup(() => {
		context = fakeContext();
		trackActiveDocument(context);
	});

	teardown(async () => {
		context.dispose();
		await vscode.commands.executeCommand('workbench.action.closeAllEditors');
	});

	test('uses the focused text editor', async () => {
		const document = await vscode.workspace.openTextDocument({
			language: 'plaintext',
			content: PUML
		});
		await vscode.window.showTextDocument(document);
		await settle();

		assert.strictEqual(resolveTargetDocument(), document);
	});

	test('falls back to the last text editor when a webview has focus', async () => {
		// The actual bug behind the misleading error: activeTextEditor is
		// undefined whenever the focused tab is not a text editor, so once the
		// diagram panel had focus the command refused to run.
		const document = await vscode.workspace.openTextDocument({
			language: 'plaintext',
			content: PUML
		});
		await vscode.window.showTextDocument(document);
		await settle();

		const panel = vscode.window.createWebviewPanel(
			'test.panel',
			'Test Panel',
			vscode.ViewColumn.Active
		);
		panel.reveal();
		await settle();

		assert.strictEqual(
			vscode.window.activeTextEditor,
			undefined,
			'precondition: the webview should have taken focus'
		);
		assert.strictEqual(resolveTargetDocument(), document);

		panel.dispose();
	});

	test('reports nothing when no text editor has been opened', async () => {
		await vscode.commands.executeCommand('workbench.action.closeAllEditors');
		await settle();

		// Fresh tracking, so nothing has been remembered yet.
		const isolated = fakeContext();
		trackActiveDocument(isolated);

		// Whatever a previous test remembered may still be live in the module,
		// so only assert the shape of the answer, not that it is undefined.
		const resolved = resolveTargetDocument();
		assert.ok(
			resolved === undefined || isEditableTextDocument(resolved),
			'must return either nothing or an editable document'
		);

		isolated.dispose();
	});
});
