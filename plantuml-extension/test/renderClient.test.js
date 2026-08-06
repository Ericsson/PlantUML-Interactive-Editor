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
const http = require('http');

const { renderPlantUmlToSvg, PlantUmlRenderError } = require('../src/renderClient');
const { TOKEN_HEADER } = require('../src/sidecar');

const TOKEN = 'a-per-launch-token';
const PUML = '@startuml\nBob -> Alice : hello\n@enduml';
const SVG = '<svg xmlns="http://www.w3.org/2000/svg"><text>hello</text></svg>';

/**
 * An HTTP server standing in for the sidecar, so the client can be tested
 * without Python, Java or a jar. Real sockets rather than a stubbed fetch:
 * the interesting failures here are transport-level.
 *
 * @param {(req: http.IncomingMessage, res: http.ServerResponse) => void} handler
 */
async function startFakeSidecar(handler) {
	const requests = [];

	const server = http.createServer((req, res) => {
		let body = '';
		req.setEncoding('utf-8');
		req.on('data', (chunk) => {
			body += chunk;
		});
		req.on('end', () => {
			requests.push({ method: req.method, url: req.url, headers: req.headers, body });
			handler(req, res);
		});
	});

	await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
	const { port } = server.address();

	return {
		sidecar: { baseUrl: `http://127.0.0.1:${port}/`, token: TOKEN },
		requests,
		port,
		async close() {
			// Drop anything still in flight; server.close() alone waits for
			// the deliberately-unanswered request in the timeout test.
			server.closeAllConnections();
			await new Promise((resolve) => server.close(resolve));
		}
	};
}

/** Answers /render the way the real route does, once the token checks out. */
function respondLikeFlask(req, res) {
	if (req.headers[TOKEN_HEADER.toLowerCase()] !== TOKEN) {
		res.writeHead(403, { 'Content-Type': 'application/json' });
		res.end(JSON.stringify({ error: 'invalid or missing token' }));
		return;
	}
	// shared/routes.py returns a bare str, so Flask labels the SVG text/html.
	res.writeHead(200, { 'Content-Type': 'text/html; charset=utf-8' });
	res.end(SVG);
}

suite('renderClient: the request', () => {
	let fake;

	teardown(async () => {
		await fake?.close();
		fake = undefined;
	});

	test('returns the SVG the backend rendered', async () => {
		fake = await startFakeSidecar(respondLikeFlask);

		assert.strictEqual(await renderPlantUmlToSvg(fake.sidecar, PUML), SVG);
	});

	test('POSTs the source to /render as JSON, with the token', async () => {
		fake = await startFakeSidecar(respondLikeFlask);

		await renderPlantUmlToSvg(fake.sidecar, PUML);

		assert.strictEqual(fake.requests.length, 1);
		const [request] = fake.requests;
		assert.strictEqual(request.method, 'POST');
		assert.strictEqual(request.url, '/render');
		assert.strictEqual(request.headers['content-type'], 'application/json');
		assert.strictEqual(request.headers[TOKEN_HEADER.toLowerCase()], TOKEN);
		// The key must be "plantuml": shared/routes.py subscripts it directly,
		// so a rename here is a 500, not a 400.
		assert.deepStrictEqual(JSON.parse(request.body), { plantuml: PUML });
	});
});

suite('renderClient: failures', () => {
	let fake;

	teardown(async () => {
		await fake?.close();
		fake = undefined;
	});

	test('a rejected token surfaces the status and the reason', async () => {
		fake = await startFakeSidecar(respondLikeFlask);
		fake.sidecar.token = 'wrong';

		await assert.rejects(() => renderPlantUmlToSvg(fake.sidecar, PUML), (err) => {
			assert.ok(err instanceof PlantUmlRenderError, err.constructor.name);
			assert.ok(err.message.includes('403'), err.message);
			assert.ok(err.message.includes('invalid or missing token'), err.message);
			return true;
		});
	});

	test('a 500 is reported without dumping the traceback page', async () => {
		// A missing PLANTUML_JAR is a KeyError in render.py, and Flask answers
		// with an HTML debug page. Showing that in a notification is useless.
		fake = await startFakeSidecar((req, res) => {
			res.writeHead(500, { 'Content-Type': 'text/html' });
			res.end('<!DOCTYPE html><html><body>a very long traceback page</body></html>');
		});

		await assert.rejects(() => renderPlantUmlToSvg(fake.sidecar, PUML), (err) => {
			assert.ok(err.message.includes('500'), err.message);
			assert.ok(!err.message.includes('<'), err.message);
			return true;
		});
	});

	test('an empty 200 is a failure, not an empty diagram', async () => {
		// render.py runs java with check=False and discards stderr, so a jar
		// that cannot run produces exactly this: 200 with nothing in it.
		fake = await startFakeSidecar((req, res) => {
			res.writeHead(200, { 'Content-Type': 'text/html' });
			res.end('   \n');
		});

		await assert.rejects(
			() => renderPlantUmlToSvg(fake.sidecar, PUML),
			(err) => {
				assert.ok(err instanceof PlantUmlRenderError);
				assert.ok(err.message.includes('PLANTUML_JAR'), err.message);
				return true;
			}
		);
	});

	test('a backend that never answers times out instead of hanging', async () => {
		// A wedged java process must fail the panel with a message; nothing
		// else cancels the request, so the timeout is the only way out.
		fake = await startFakeSidecar(() => {
			/* deliberately no response */
		});

		await assert.rejects(
			() => renderPlantUmlToSvg(fake.sidecar, PUML, { timeoutMs: 50 }),
			(err) => {
				assert.ok(err instanceof PlantUmlRenderError);
				assert.ok(err.message.includes('50ms'), err.message);
				return true;
			}
		);
	});

	test('a dead backend says so rather than "fetch failed"', async () => {
		fake = await startFakeSidecar(respondLikeFlask);
		const { sidecar } = fake;
		await fake.close();
		fake = undefined;

		await assert.rejects(() => renderPlantUmlToSvg(sidecar, PUML), (err) => {
			assert.ok(err instanceof PlantUmlRenderError);
			assert.ok(err.message.includes('no longer running'), err.message);
			return true;
		});
	});
});
