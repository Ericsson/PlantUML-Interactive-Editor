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

// Pan and zoom for the diagram, and the three zoom buttons that drive it.
//
// Loaded by both pages that render partials/diagram_toolbar.html: index.html
// and the extension's webview.html, which needs the behaviour in a file
// because its CSP allows no inline script.
//
// Reads the DOM as it runs, so it loads at the end of <body>.
//
// The toolbar's fourth button, #png, is wired by each page separately:
// script.js's buttonEventListeners() for index.html, static/vscode/
// webviewInit.js for the webview.

(function () {
	const MAX_ZOOM = 3;
	const MIN_ZOOM = 0.25;
	const ZOOM_STEP = 1.1;

	const diagram = document.getElementById('colb');

	if (!window.panzoom || !diagram) {
		return;
	}

	const instance = panzoom(diagram, {
		maxZoom: MAX_ZOOM,
		minZoom: MIN_ZOOM,
		bounds: true
	});

	// Read by the e2e tests, which assert on the scale after a button click.
	// See tests/e2e/test_ribbon.py.
	window.panzoomInstance = instance;

	// Double-click is an editing gesture on both pages (it opens the text for
	// the element under the cursor), so stop panzoom treating it as
	// zoom-to-point.
	diagram.addEventListener('dblclick', (event) => event.stopImmediatePropagation());

	// Zoom about the current pan origin, so repeated clicks stay on the same
	// part of the diagram. zoomAbs applies the scale verbatim, so the bounds
	// panzoom enforces on wheel input are reapplied here.
	function zoomBy(factor) {
		const { x, y, scale } = instance.getTransform();
		const next = Math.min(Math.max(scale * factor, MIN_ZOOM), MAX_ZOOM);
		instance.zoomAbs(x, y, next);
	}

	document.getElementById('zoom-in').addEventListener('click', () => zoomBy(ZOOM_STEP));
	document.getElementById('zoom-out').addEventListener('click', () => zoomBy(1 / ZOOM_STEP));
	document.getElementById('zoom-fit').addEventListener('click', () => {
		instance.moveTo(0, 0);
		instance.zoomAbs(0, 0, 1);
	});
})();
