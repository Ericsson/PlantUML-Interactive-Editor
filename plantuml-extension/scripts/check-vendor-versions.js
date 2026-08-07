#!/usr/bin/env node
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

// Pre-commit hook (see .pre-commit-config.yaml) guarding an assumption
// webviewPage.js documents but cannot check at runtime: that the browser
// libraries loaded from node_modules (this package's `dependencies`) are the
// same versions the web app loads from CDNs in index.html. The two never
// talk to each other -- the extension vendors its own copies so the
// webview's CSP does not have to allow those CDNs -- so nothing else notices
// if one is bumped without the other.
//
// Plain `node`, not a test framework: pre-commit runs this on every commit
// that touches either file, and pulling in vscode-test's Electron download
// (this extension's `npm test`) would be a lot of weight for comparing two
// strings. Nothing else in this repo's pre-commit hooks (ruff, mypy,
// js-beautify) runs through a test runner either -- pre-commit is itself the
// only place they run, locally and in CI (see .github/workflows/pre-commit.yml).

const fs = require('fs');
const path = require('path');

const EXTENSION_PATH = path.join(__dirname, '..');
const INDEX_HTML_PATH = path.join(EXTENSION_PATH, '..', 'src', 'plantuml_gui', 'templates', 'index.html');

// dependency name in package.json -> regex extracting its version from
// index.html's CDN URLs. Deliberately excludes popper.js and ace, which
// index.html loads but package.json does not vendor (not needed inside the
// webview's context menus/editor, which use VS Code's own equivalents).
const CDN_VERSION_PATTERNS = {
	jquery: /code\.jquery\.com\/jquery-([0-9]+\.[0-9]+\.[0-9]+)/,
	bootstrap: /cdn\.jsdelivr\.net\/npm\/bootstrap@([0-9.]+)/,
	diff: /cdnjs\.cloudflare\.com\/ajax\/libs\/jsdiff\/([0-9.]+)/,
	panzoom: /unpkg\.com\/panzoom@([0-9.]+)/
};

/**
 * @param {string} range a package.json version specifier
 * @returns {string} the version with any leading range operator (^, ~, etc.)
 *   stripped, so it can be compared against an exact CDN version.
 */
function stripRangeOperator(range) {
	return range.replace(/^[^\d]*/, '');
}

function main() {
	const packageJson = JSON.parse(
		fs.readFileSync(path.join(EXTENSION_PATH, 'package.json'), 'utf8')
	);
	const dependencies = packageJson.dependencies || {};
	const indexHtml = fs.readFileSync(INDEX_HTML_PATH, 'utf8');

	let failures = 0;

	for (const [name, pattern] of Object.entries(CDN_VERSION_PATTERNS)) {
		if (!dependencies[name]) {
			console.error(`FAIL ${name} is checked against index.html's CDN but is missing from package.json dependencies`);
			failures++;
			continue;
		}

		const match = indexHtml.match(pattern);
		if (!match) {
			console.error(
				`FAIL could not find a ${name} CDN URL in index.html matching ${pattern}; ` +
					'update CDN_VERSION_PATTERNS if the URL changed'
			);
			failures++;
			continue;
		}

		const packageVersion = stripRangeOperator(dependencies[name]);
		const cdnVersion = match[1];
		if (packageVersion !== cdnVersion) {
			console.error(
				`FAIL package.json pins ${name}@${dependencies[name]}, but index.html's CDN URL is ` +
					`for ${cdnVersion} - the webview and the web app would render with different ` +
					'library versions. Bump whichever one is stale.'
			);
			failures++;
			continue;
		}

		console.log(`OK ${name}@${packageVersion} matches`);
	}

	if (failures > 0) {
		console.error(
			`\n${failures} vendor library version mismatch(es) between ` +
				'plantuml-extension/package.json and src/plantuml_gui/templates/index.html.'
		);
		process.exitCode = 1;
	}
}

main();
