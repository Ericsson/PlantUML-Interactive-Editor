const assert = require('assert');
const fs = require('fs');
const path = require('path');
const vm = require('vm');

const SHIM = path.join(__dirname, '..', 'media', 'fetchShim.js');

/**
 * Run media/fetchShim.js in a sandbox and return the installed fetch plus a log
 * of the calls it forwarded.
 *
 * Exercises the real file rather than a copy of its logic, since this shim is
 * what all ~150 of the reused app code's fetch() call sites go through.
 *
 * @returns {{fetch: Function, calls: Array<{url: string, options: object}>}}
 */
function loadShim() {
	const calls = [];
	const sandbox = {
		__PLANTUML_API__: 'http://127.0.0.1:53421/',
		__PLANTUML_TOKEN__: 'test-token',
		fetch: (url, options) => {
			calls.push({ url, options });
			return Promise.resolve({ ok: true });
		},
		String,
		Promise
	};
	sandbox.window = sandbox;

	vm.createContext(sandbox);
	new vm.Script(fs.readFileSync(SHIM, 'utf-8')).runInContext(sandbox);

	return { fetch: sandbox.fetch, calls };
}

suite('fetch shim', () => {
	test('resolves a relative URL against the sidecar', () => {
		const { fetch, calls } = loadShim();

		fetch('editMessageText', { method: 'POST' });

		assert.strictEqual(calls[0].url, 'http://127.0.0.1:53421/editMessageText');
	});

	test('does not double up a leading slash', () => {
		const { fetch, calls } = loadShim();

		fetch('/render');

		assert.strictEqual(calls[0].url, 'http://127.0.0.1:53421/render');
	});

	test('leaves an absolute URL alone', () => {
		const { fetch, calls } = loadShim();

		fetch('https://example.com/x');

		assert.strictEqual(calls[0].url, 'https://example.com/x');
	});

	test('attaches the auth token', () => {
		// The sidecar rejects unauthenticated requests, so a lost header shows
		// up as a blanket 403 rather than anything specific.
		const { fetch, calls } = loadShim();

		fetch('render');

		assert.strictEqual(calls[0].options.headers['X-PlantUML-Token'], 'test-token');
	});

	test('preserves caller headers', () => {
		const { fetch, calls } = loadShim();

		fetch('render', { headers: { 'Content-Type': 'application/json' } });

		assert.strictEqual(
			calls[0].options.headers['Content-Type'],
			'application/json'
		);
		assert.strictEqual(calls[0].options.headers['X-PlantUML-Token'], 'test-token');
	});

	test('preserves the request body and method', () => {
		const { fetch, calls } = loadShim();

		fetch('render', { method: 'POST', body: '{"plantuml":"x"}' });

		assert.strictEqual(calls[0].options.method, 'POST');
		assert.strictEqual(calls[0].options.body, '{"plantuml":"x"}');
	});
});
