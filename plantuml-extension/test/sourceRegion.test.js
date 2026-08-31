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

const {
	wholeDocumentRegion,
	regionSource,
	stripIndent,
	indentSource,
	toDocumentRow,
	toRegionRow,
	containsLine
} = require('../src/sourceRegion');

/** @param {string[]} lines */
const doc = (...lines) => lines.join('\n');

suite('sourceRegion: the whole document as a region', () => {
	test('covers every line', () => {
		const text = doc('@startuml', 'a -> b', '@enduml');

		assert.deepStrictEqual(wholeDocumentRegion(text), {
			startLine: 0,
			endLine: 2,
			indent: ''
		});
	});

	test('returns the text unchanged', () => {
		// The invariant that keeps .puml files on the same code path as
		// Markdown: what the webview and the renderer are given must be the
		// document, byte for byte, as it was before regions existed.
		for (const text of [
			doc('@startuml', 'a -> b', '@enduml'),
			doc('@startuml', 'a -> b', '@enduml', ''),
			doc('  @startuml', '    indented', '@enduml'),
			'',
			'@startuml\r\na -> b\r\n@enduml\r\n'
		]) {
			assert.strictEqual(regionSource(text, wholeDocumentRegion(text)), text);
		}
	});

	test('counts a trailing newline as a line, as vscode does', () => {
		// document.lineCount is 2 for "a\n": the empty last line is real, and a
		// region that left it out would drop it on the next write-back.
		assert.strictEqual(wholeDocumentRegion('a\n').endLine, 1);
		assert.strictEqual(wholeDocumentRegion('').endLine, 0);
	});

	test('translates rows to itself', () => {
		const region = wholeDocumentRegion(doc('a', 'b', 'c'));

		assert.strictEqual(toDocumentRow(region, 2), 2);
		assert.strictEqual(toRegionRow(region, 2), 2);
	});
});

suite('sourceRegion: reading part of a document', () => {
	const text = doc('# Notes', '```plantuml', '@startuml', 'a -> b', '@enduml', '```', 'After.');

	test('reads the region and nothing around it', () => {
		const source = regionSource(text, { startLine: 2, endLine: 4, indent: '' });

		assert.strictEqual(source, '@startuml\na -> b\n@enduml');
	});

	test('includes both ends of the range', () => {
		// endLine is inclusive: a region is a set of whole lines.
		assert.strictEqual(regionSource(text, { startLine: 3, endLine: 3, indent: '' }), 'a -> b');
	});

	test('keeps the carriage returns of a CRLF document', () => {
		// This is a slice of the user's file, not a rewrite of it. The renderer
		// has always been given whatever line endings the document uses.
		const crlf = '# Notes\r\n```plantuml\r\n@startuml\r\na -> b\r\n@enduml\r\n```\r\n';

		assert.strictEqual(
			regionSource(crlf, { startLine: 2, endLine: 4, indent: '' }),
			'@startuml\r\na -> b\r\n@enduml\r'
		);
	});

	test('yields what is there when the region has gone stale', () => {
		// Total rather than throwing: noticing is the caller's job, and a
		// throw here would take down a document-change handler.
		assert.strictEqual(regionSource('a\nb', { startLine: 1, endLine: 9, indent: '' }), 'b');
		assert.strictEqual(regionSource('a\nb', { startLine: 5, endLine: 9, indent: '' }), '');
	});
});

suite('sourceRegion: indentation', () => {
	test('strips the region indentation as it reads', () => {
		const text = doc('- The flow:', '  ```plantuml', '  @startuml', '  a -> b', '  @enduml', '  ```');

		const source = regionSource(text, { startLine: 2, endLine: 4, indent: '  ' });

		assert.strictEqual(source, '@startuml\na -> b\n@enduml');
	});

	test('keeps indentation the diagram itself has', () => {
		// PlantUML's nesting is written with leading space, and the app's own
		// indentPuml() produces it. Only the region's share comes off.
		const text = doc('  ```plantuml', '  @startuml', '  if (a) then', '    :b;', '  @enduml', '  ```');

		assert.strictEqual(
			regionSource(text, { startLine: 1, endLine: 4, indent: '  ' }),
			'@startuml\nif (a) then\n  :b;\n@enduml'
		);
	});

	test('strips what a short line has rather than mangling it', () => {
		// Blank lines are left unpadded by most editors, and hand-written
		// blocks are not always uniform.
		assert.strictEqual(stripIndent('', '  '), '');
		assert.strictEqual(stripIndent(' a', '  '), 'a');
		assert.strictEqual(stripIndent('  a', '  '), 'a');
		assert.strictEqual(stripIndent('   a', '  '), ' a');
		assert.strictEqual(stripIndent('a', ''), 'a');
	});

	test('restores the indentation on the way back', () => {
		assert.strictEqual(indentSource('@startuml\na -> b', '  '), '  @startuml\n  a -> b');
		assert.strictEqual(indentSource('@startuml', ''), '@startuml');
	});

	test('does not indent blank lines on the way back', () => {
		// Trailing whitespace many editors strip on save, which would make the
		// file dirty again just after a diagram edit, for a change nobody made.
		assert.strictEqual(indentSource('a\n\nb', '  '), '  a\n\n  b');
		assert.strictEqual(indentSource('a\n   \nb', '  '), '  a\n   \n  b');
	});

	test('round-trips a source through the region indentation', () => {
		// The pair has to agree: this is the write-then-read the user sees as
		// "my diagram still looks like my diagram".
		const source = '@startuml\nif (a) then\n  :b;\n\n@enduml';

		const stripped = indentSource(source, '   ')
			.split('\n')
			.map((line) => stripIndent(line, '   '))
			.join('\n');

		assert.strictEqual(stripped, source);
	});
});

suite('sourceRegion: row translation', () => {
	const region = { startLine: 10, endLine: 14, indent: '' };

	test('moves a diagram row to its document line', () => {
		// The highlight direction: the app marks a row of the source it was
		// given, and the decoration lands on that line of the file.
		assert.strictEqual(toDocumentRow(region, 0), 10);
		assert.strictEqual(toDocumentRow(region, 4), 14);
	});

	test('moves a document line to its diagram row', () => {
		// The caret direction.
		assert.strictEqual(toRegionRow(region, 10), 0);
		assert.strictEqual(toRegionRow(region, 14), 4);
	});

	test('is its own inverse', () => {
		// The sign errors this module exists to prevent.
		for (const row of [0, 1, 4]) {
			assert.strictEqual(toRegionRow(region, toDocumentRow(region, row)), row);
		}
	});

	test('reports lines outside the region as outside', () => {
		// Left to the caller to check rather than clamped: a clamp would paint
		// the diagram's first line whenever the caret sat above the block.
		assert.strictEqual(toRegionRow(region, 9), -1);
		assert.strictEqual(toRegionRow(region, 15), 5);
	});

	test('answers whether a line belongs to the region at all', () => {
		// The check the caret needs before its line is translated: outside the
		// region there is no row to send, not a row to clamp to.
		assert.ok(containsLine(region, 10), 'the first line');
		assert.ok(containsLine(region, 12), 'a line within');
		assert.ok(containsLine(region, 14), 'the last line, endLine being inclusive');
		assert.ok(!containsLine(region, 9), 'the line above');
		assert.ok(!containsLine(region, 15), 'the line below');
	});
});
