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

const assert = require('assert');
const vscode = require('vscode');

const extension = require('../extension');

const COMMAND_ID = 'plantuml-interactive-editor.openDiagram';

suite('extension: activation', () => {
	suiteSetup(async () => {
		// Contributed commands are not in getCommands() until the extension
		// has been activated, and nothing in a test run triggers that. Find it
		// by manifest name: there is no publisher field, so the extension id is
		// not stable enough to look up directly.
		const self = vscode.extensions.all.find(
			(candidate) => candidate.packageJSON.name === 'plantuml-editor'
		);
		assert.ok(self, 'the extension under test was not loaded');
		await self.activate();
	});

	test('exports the lifecycle hooks VS Code calls', () => {
		assert.strictEqual(typeof extension.activate, 'function');
		assert.strictEqual(typeof extension.deactivate, 'function');
	});

	test('registers the declared command', async () => {
		// The manifest promises it; a rename on one side and not the other
		// leaves an entry in the palette that does nothing.
		const declared = require('../package.json').contributes.commands.map((c) => c.command);
		assert.ok(declared.includes(COMMAND_ID), `not in package.json: ${declared}`);

		const registered = await vscode.commands.getCommands(true);
		assert.ok(registered.includes(COMMAND_ID), 'command was not registered');
	});

	test('can dispatch the action offered on configuration errors', async () => {
		// The Open Settings button runs a built-in command by name; a rename or
		// a typo would leave a button that does nothing.
		const registered = await vscode.commands.getCommands(true);

		assert.ok(
			registered.includes('workbench.action.openSettings'),
			'workbench.action.openSettings is not available'
		);
	});

	test('does not render in Node', () => {
		// The single-renderer invariant: rendering happens in the sidecar, via
		// shared/render.py. A second java invocation on this side would drift
		// from the one whose SVG the backend's ~71 routes parse.
		for (const [relative, source] of readSources()) {
			assert.ok(!/spawn\(\s*['"]java['"]/.test(source), `${relative} spawns java`);
		}
	});

	test('does not build the webview page in Node', () => {
		// The single-page invariant, and the reason this extension carries no
		// copy of the frontend: serve.py renders the whole document from the
		// same templates and static files the web app uses. A document built
		// here is a document that can go stale against them.
		const fs = require('fs');
		const path = require('path');
		const root = path.join(__dirname, '..');

		for (const [relative, source] of readSources()) {
			assert.ok(!/<!DOCTYPE|<\/html>/i.test(source), `${relative} builds a document`);
		}

		const templates = fs
			.readdirSync(path.join(root, 'src'))
			.filter((name) => name.endsWith('.html'));
		assert.deepStrictEqual(templates, [], 'src/ should hold no HTML template');
	});
});

suite('extension: message protocol', () => {
	test('handles every message type the webview posts', () => {
		// The two ends live in different packages and are kept in step by
		// hand; this is the check that they still are. See "Cross-runtime
		// contracts" in docs/extension.md. It matters because the channel has
		// no acks and both handlers are if/else-if chains, so a type the page
		// posts and the host misses is dropped in silence -- the button simply
		// does nothing.
		const posted = new Set();

		for (const source of readWebviewShims()) {
			for (const [, type] of source.matchAll(/post(?:Message)?\(\{\s*type:\s*'([^']+)'/g)) {
				posted.add(type);
			}
		}

		const [, extensionSource] = readSources().find(([relative]) => relative === 'extension.js');
		const handled = new Set(
			[...extensionSource.matchAll(/message\.type === '([^']+)'/g)].map(([, type]) => type)
		);

		assert.ok(posted.has('savePng'), 'the shims no longer post savePng');
		assert.deepStrictEqual(
			[...posted].filter((type) => !handled.has(type)),
			[],
			'posted by the webview, not handled by the host'
		);
	});

	test('reports a backend that stops on its own', () => {
		// Regression: the exit handler only dropped the sidecar handle, so
		// killing the Python process left no trace anywhere -- the open panel
		// kept accepting gestures, the output channel simply stopped growing,
		// and the user had nothing to go on.
		//
		// Source-checked because the host end needs a running sidecar, a panel
		// and a real webview to exercise. What reportBackendExit then does with
		// the exit is covered for real in sidecar.test.js, through dispose() and
		// an emitted exit event.
		const [, source] = readSources().find(([relative]) => relative === 'extension.js');

		const exitIndex = source.indexOf("process.on('exit'");
		assert.notStrictEqual(exitIndex, -1, 'nothing listens for the backend exiting');
		assert.notStrictEqual(
			source.indexOf('reportBackendExit', exitIndex),
			-1,
			'the backend can exit without anything being reported'
		);

		assert.ok(
			readWebviewShims().some((shim) => shim.includes('backendUnreachable')),
			'the webview no longer reports requests that did not reach the backend'
		);
	});

	test('sends the first document only once the webview says it is ready', () => {
		// Regression: the initial documentChanged was posted immediately after
		// panel.webview.html was set, before the page had registered its
		// `message` listener. A message posted then is dropped in silence, so
		// the panel opened with a toolbar and no diagram, and stayed that way
		// until the next document change happened to post again.
		//
		// Checked in the source because the host end of this is unreachable
		// from a test: it needs a running sidecar, a panel and a real webview.
		const [, source] = readSources().find(([relative]) => relative === 'extension.js');

		const listenerIndex = source.indexOf('panel.webview.onDidReceiveMessage');
		assert.notStrictEqual(listenerIndex, -1, 'the webview message listener is gone');

		// Only a post at the top level of the open could beat `ready`: the
		// calls inside the listener callbacks -- the active-editor switch, the
		// document change -- cannot run until the page is up and gesturing.
		assert.doesNotMatch(
			source,
			/\n\tpostDocument\(\)/,
			'the document is posted before the webview can listen for it'
		);

		const readyIndex = source.indexOf("message.type === 'ready'");
		assert.notStrictEqual(readyIndex, -1, 'the host no longer handles ready');
		assert.notStrictEqual(
			source.indexOf('postDocument()', readyIndex),
			-1,
			'nothing sends the first document once the webview is ready'
		);
	});
});

suite('extension: which document the panel shows', () => {
	// The panel follows the active editor, so these decide what it switches to
	// and what it leaves it on. A document is stood in for by the fields the
	// rules read; getText ignores the range it is given, the real one clamping
	// it to the document.
	const doc = (filePath, { languageId = 'plaintext', text = '' } = {}) => ({
		languageId,
		uri: vscode.Uri.file(filePath),
		fileName: filePath,
		getText: () => text
	});

	const DIAGRAM = '@startuml\nBob -> Alice: hi\n@enduml\n';

	test('follows the PlantUML file extensions', () => {
		// Taken at their word: an empty one is a diagram being started.
		for (const name of ['a.puml', 'a.plantuml', 'a.pu', 'a.iuml', 'a.wsd', 'a.uml']) {
			assert.ok(
				extension.isPlantUmlDocument(doc(`/w/${name}`)),
				`${name} is not followed`
			);
		}
	});

	test('follows an extension whatever its case', () => {
		// The extensions come from the filesystem, which on Windows and macOS
		// preserves whatever the author typed.
		assert.ok(extension.isPlantUmlDocument(doc('/w/A.PUML')));
	});

	test('follows a document the editor calls plantuml', () => {
		// VS Code registers no language for PlantUML, so the id depends on
		// which other extension the user has; when one does set it, honour it
		// even for a name this would not otherwise recognise.
		assert.ok(extension.isPlantUmlDocument(doc('/w/diagram.dat', 'plantuml')));
	});

	test('follows a plain-text file that opens a diagram', () => {
		// Diagrams kept in .txt, and any other extension VS Code hands to
		// plaintext, are recognised by their content.
		assert.ok(extension.isPlantUmlDocument(doc('/w/notes.txt', { text: DIAGRAM })));
		assert.ok(
			extension.isPlantUmlDocument(doc('/w/mind.txt', { text: '@startmindmap\n* a\n' })),
			'only @startuml is recognised'
		);
		assert.ok(
			extension.isPlantUmlDocument(doc('/w/indented.txt', { text: `  ${DIAGRAM}` })),
			'a leading blank is not tolerated'
		);
	});

	test('leaves the panel alone for plain text that is not a diagram', () => {
		// The reason .txt is decided on content: a notes or log file is not a
		// request to render it.
		assert.ok(!extension.isPlantUmlDocument(doc('/w/todo.txt', { text: 'buy milk\n' })));
		assert.ok(!extension.isPlantUmlDocument(doc('/w/empty.txt')));
	});

	test('leaves the panel alone for another language quoting a diagram', () => {
		// The whole document is the source, so rendering a .py that documents
		// a diagram would render the Python around it too.
		const python = doc('/w/model.py', {
			languageId: 'python',
			text: `"""\n${DIAGRAM}"""\n`
		});

		assert.ok(!extension.isPlantUmlDocument(python));
	});

	test('names the file it is showing', () => {
		// The one place a user can see which of several open diagrams the panel
		// is pointed at.
		assert.strictEqual(extension.panelTitle(doc('/w/test2.puml')), 'PlantUML: test2.puml');
	});
});

suite('extension: running the command a second time', () => {
	// Regression: every invocation called createWebviewPanel, so running the
	// command again -- the natural thing to do when the diagram is not in front
	// of you -- stacked up a second panel on the same file, each with its own
	// listeners writing to the same document.
	const panelFor = (sidecar) => ({
		panel: { reveal() {}, dispose() {} },
		sidecar,
		show() {}
	});

	test('opens a panel when the window has none', () => {
		assert.strictEqual(extension.panelAction(undefined), 'open');
	});

	test('reveals the open panel instead of opening another', () => {
		assert.strictEqual(extension.panelAction(panelFor({ isRunning: true })), 'reveal');
	});

	test('replaces a panel whose backend has died', () => {
		// The recovery reportBackendExit tells the user about: the page holds
		// the dead child's address and token, so revealing it would bring
		// forward a diagram that cannot render anything.
		assert.strictEqual(extension.panelAction(panelFor({ isRunning: false })), 'replace');
	});

	test('opens through the guard that keeps two invocations to one panel', () => {
		// The window's handle is only set once the page has loaded, several
		// awaits into the open, so without this two runs in quick succession
		// both get past the reuse check. Source-checked because the open it
		// guards needs a backend, a panel and a real webview.
		const [, source] = readSources().find(([relative]) => relative === 'extension.js');

		const guardIndex = source.indexOf('if (!diagramPanelOpening)');
		const callIndex = source.indexOf('createDiagramPanel(context)');

		assert.notStrictEqual(callIndex, -1, 'nothing opens the panel');
		assert.notStrictEqual(guardIndex, -1, 'the open in flight is not tracked');
		assert.ok(
			guardIndex < callIndex,
			'a second invocation can open a second panel while the first is opening'
		);
	});
});

suite('extension: reinstalling the backend', () => {
	// The repair command for a venv that exists and does not work. Its two
	// hazards are the same one seen twice: install() treats an existing
	// target as a finished install, so anything that leaves the old directory
	// standing turns "reinstalled" into a claim that is simply untrue.
	const fs = require('fs');
	const os = require('os');
	const path = require('path');

	/** @type {string} */
	let temp;

	setup(() => {
		temp = fs.mkdtempSync(path.join(os.tmpdir(), 'plantuml-reinstall-'));
	});

	teardown(() => {
		fs.rmSync(temp, { recursive: true, force: true });
	});

	/** @returns {string} a venv directory, with something in it */
	const venvWithContents = () => {
		const dir = path.join(temp, 'venv-0.31');
		fs.mkdirSync(path.join(dir, 'bin'), { recursive: true });
		fs.writeFileSync(path.join(dir, 'bin', 'python'), '');
		return dir;
	};

	test('removes the venv, contents and all', async () => {
		const venv = venvWithContents();

		await extension.removeManagedVenv(venv);

		assert.ok(!fs.existsSync(venv), 'the venv is still there');
	});

	test('a venv that was never there is not a failure', async () => {
		// The first-run case, and the state the caller wanted anyway.
		await extension.removeManagedVenv(path.join(temp, 'venv-0.31'));
	});

	test('retries a delete that fails while the interpreter is still going', async () => {
		// Why the retry: Windows will not unlink a running executable's image,
		// and the child's exit event is not a promise that its handles have
		// been released. Locking a directory is not something a test can do on
		// every platform this runs on, hence the injected delete.
		const venv = venvWithContents();
		let attempts = 0;

		await extension.removeManagedVenv(venv, {
			remove: async (uri) => {
				attempts += 1;
				if (attempts < 3) {
					throw Object.assign(new Error('EBUSY: resource busy'), { code: 'EBUSY' });
				}
				fs.rmSync(uri.fsPath, { recursive: true });
			}
		});

		assert.strictEqual(attempts, 3, 'gave up on the first failure');
		assert.ok(!fs.existsSync(venv));
	});

	test('reports a venv it could not remove, rather than installing over it', async () => {
		// The regression that matters: swallowing this failure meant an install
		// that did nothing -- install() leaves an existing target alone --
		// followed by "The PlantUML backend was reinstalled".
		const venv = venvWithContents();

		await assert.rejects(
			() =>
				extension.removeManagedVenv(venv, {
					timeoutMs: 50,
					remove: async () => {
						throw new Error('EBUSY: resource busy');
					}
				}),
			(err) => {
				assert.ok(err.message.includes(venv), err.message);
				assert.ok(err.message.includes('EBUSY'), err.message);
				return true;
			}
		);

		assert.ok(fs.existsSync(venv), 'the venv should have been left alone');
	});

	test('a delete that reports success but leaves the venv is not believed', async () => {
		// Existence is what the removal waits on, not the delete's own answer:
		// a partial removal that resolves would otherwise pass for a clean one.
		const venv = venvWithContents();

		await assert.rejects(
			() => extension.removeManagedVenv(venv, { timeoutMs: 50, remove: async () => {} }),
			(err) => {
				assert.ok(err.message.includes(venv), err.message);
				return true;
			}
		);
	});

	test('refuses to run while an install is already in flight', () => {
		// installBackendOnce latches the install behind a promise, so awaiting
		// it after the delete would join the install that started *before* it
		// -- one that may already have decided the venv was fine and returned.
		// The reinstall would then report success having deleted the backend
		// and installed nothing.
		//
		// Source-checked, as with the other host-only paths in this file:
		// reinstallBackend needs a bundled wheel, a global storage directory
		// and a user answering notifications to exercise for real.
		const body = reinstallSource();

		assert.ok(/if \(backendInstalling\)/.test(body), 'an install in flight is not checked');
		assert.ok(
			body.indexOf('backendInstalling') < body.indexOf('removeManagedVenv'),
			'the check comes after the venv has already been deleted'
		);
	});

	test('waits for the backend to stop before deleting its directory', () => {
		// Not disposeSidecar(): that returns as soon as the signal is sent, and
		// reaches nothing at all while a start is in flight, since `sidecar` is
		// assigned only once startSidecar resolves. The child would then arrive
		// running out of a directory that had since been deleted, with no
		// handle left anywhere to stop it.
		const body = reinstallSource();

		assert.ok(
			body.includes('await stopSidecarForReinstall()'),
			'the reinstall no longer waits for the backend to stop'
		);
		assert.ok(
			body.indexOf('stopSidecarForReinstall') < body.indexOf('removeManagedVenv'),
			'the venv is deleted before the backend has been stopped'
		);

		const [, source] = readSources().find(([relative]) => relative === 'extension.js');
		const stop = source.slice(source.indexOf('async function stopSidecarForReinstall'));

		assert.ok(
			/await sidecarStarting/.test(stop),
			'a start in flight is neither awaited nor refused'
		);
		assert.ok(
			/\.stop\(SIDECAR_STOP_TIMEOUT_MS\)/.test(stop),
			'the wait for the child to exit is unbounded'
		);
	});

	/** @returns {string} the body of reinstallBackend, up to its closing brace */
	function reinstallSource() {
		const [, source] = readSources().find(([relative]) => relative === 'extension.js');
		const start = source.indexOf('async function reinstallBackend(');
		assert.notStrictEqual(start, -1, 'reinstallBackend is gone');

		const end = source.indexOf('\n}\n', start);
		assert.notStrictEqual(end, -1, 'could not find the end of reinstallBackend');

		return source.slice(start, end);
	}
});

/**
 * @returns {string[]} the contents of the webview-side shims, which live in
 *   the Python package rather than here; see the header of fetchShim.js.
 */
function readWebviewShims() {
	const fs = require('fs');
	const path = require('path');
	const shims = path.join(__dirname, '..', '..', 'src', 'plantuml_gui', 'static', 'vscode');

	return fs
		.readdirSync(shims)
		.filter((name) => name.endsWith('.js'))
		.map((name) => fs.readFileSync(path.join(shims, name), 'utf-8'));
}

/**
 * @returns {[string, string][]} every source file the extension ships, as
 *   [path relative to the extension root, contents].
 */
function readSources() {
	const fs = require('fs');
	const path = require('path');
	const root = path.join(__dirname, '..');

	return ['extension.js']
		.concat(
			fs
				.readdirSync(path.join(root, 'src'))
				.filter((name) => name.endsWith('.js'))
				.map((name) => path.join('src', name))
		)
		.map((relative) => [relative, fs.readFileSync(path.join(root, relative), 'utf-8')]);
}
