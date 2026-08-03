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

// PlantUML -> SVG, via the sidecar's /render route.
//
// The extension used to shell out to `java -jar plantuml.jar -pipe -tsvg`
// itself, duplicating shared/render.py's invocation flag for flag. There is
// now one renderer: the Python one, reached over HTTP. That matters beyond
// deduplication -- the webview will eventually drive the same backend for the
// ~71 puml-rewriting routes, and a diagram rendered by a second, subtly
// different code path would not match the SVG those routes are parsing.

const { TOKEN_HEADER } = require('./sidecar');

// Generous: PlantUML on a cold JVM is slow, and the sidecar is single-threaded
// per request. Short enough that a wedged java process does not hang the panel
// forever, which is what the old spawn-based renderer did (it had no timeout).
const RENDER_TIMEOUT_MS = 20000;

/** Thrown when the backend cannot be reached, or reports a failure. */
class PlantUmlRenderError extends Error {}

/**
 * Render PlantUML source to SVG on the sidecar.
 *
 * @param {import('./sidecar').Sidecar} sidecar a started, healthy sidecar
 * @param {string} plantUmlSource
 * @param {object} [options]
 * @param {number} [options.timeoutMs] overrides RENDER_TIMEOUT_MS; tests use a
 *   short value so the abort path can be exercised in milliseconds
 * @returns {Promise<string>} the rendered SVG markup
 * @throws {PlantUmlRenderError}
 */
async function renderPlantUmlToSvg(sidecar, plantUmlSource, options = {}) {
	const timeoutMs = options.timeoutMs ?? RENDER_TIMEOUT_MS;
	let response;

	try {
		response = await fetch(`${sidecar.baseUrl}render`, {
			method: 'POST',
			headers: {
				'Content-Type': 'application/json',
				[TOKEN_HEADER]: sidecar.token
			},
			body: JSON.stringify({ plantuml: plantUmlSource }),
			signal: AbortSignal.timeout(timeoutMs)
		});
	} catch (err) {
		throw new PlantUmlRenderError(describeTransportFailure(err, timeoutMs));
	}

	if (!response.ok) {
		throw new PlantUmlRenderError(await describeErrorResponse(response));
	}

	// /render returns a bare string, so Flask labels it text/html rather than
	// image/svg+xml. Read it as text and do not trust the content type.
	const svg = await response.text();

	if (!svg.trim()) {
		throw new PlantUmlRenderError(
			'The PlantUML backend returned an empty diagram. Check that PLANTUML_JAR ' +
				'points at a usable plantuml.jar and that Java is on the PATH of the ' +
				'interpreter running the backend.'
		);
	}

	return svg;
}

/**
 * Explain a request that never produced a response.
 *
 * @param {Error & { cause?: { code?: string } }} err
 * @param {number} timeoutMs
 * @returns {string}
 */
function describeTransportFailure(err, timeoutMs) {
	if (err.name === 'TimeoutError' || err.name === 'AbortError') {
		return (
			`The PlantUML backend did not answer within ${timeoutMs}ms. The ` +
			'diagram may be too large, or Java may be wedged.'
		);
	}

	// The sidecar died between the health check and now; the next open restarts
	// it, so say what happened rather than showing a bare "fetch failed".
	if (err.cause?.code === 'ECONNREFUSED') {
		return 'The PlantUML backend is no longer running. Reopen the diagram to restart it.';
	}

	return `Could not reach the PlantUML backend: ${err.message}`;
}

/**
 * Turn a non-2xx response into a message, preferring the server's own wording.
 *
 * @param {Response} response
 * @returns {Promise<string>}
 */
async function describeErrorResponse(response) {
	let detail = '';

	try {
		const body = (await response.text()).trim();
		// Errors raised by serve.py are jsonify({"error": ...}); a Flask
		// traceback page is HTML and far too long to put in a notification.
		try {
			const parsed = JSON.parse(body);
			detail = (parsed && parsed.error) || '';
		} catch {
			detail = body.startsWith('<') ? '' : body.slice(0, 500);
		}
	} catch {
		detail = '';
	}

	return (
		`The PlantUML backend returned ${response.status} rendering the diagram.` +
		(detail ? ` ${detail}` : '')
	);
}

module.exports = {
	renderPlantUmlToSvg,
	PlantUmlRenderError,
	RENDER_TIMEOUT_MS
};
