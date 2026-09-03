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
	containsLine,
	trackLine,
	LINE_GONE
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
		// document.lineCount is 2 for "a\n": the empty last line is real, and the
		// region covers it, so a write-back keeps it.
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
		// This is a slice of the user's file. The renderer has always been given
		// whatever line endings the document uses.
		const crlf = '# Notes\r\n```plantuml\r\n@startuml\r\na -> b\r\n@enduml\r\n```\r\n';

		assert.strictEqual(
			regionSource(crlf, { startLine: 2, endLine: 4, indent: '' }),
			'@startuml\r\na -> b\r\n@enduml\r'
		);
	});

	test('yields what is there when the region has gone stale', () => {
		// Total, so a document-change handler stays on its feet; noticing is the
		// caller's job.
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
		// Editors leave blank lines unpadded, and hand-written blocks vary.
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
		// Blank lines stay blank, which keeps trailing whitespace out of a file
		// whose editor strips it on save -- that would make the file dirty again
		// just after a diagram edit, for a change nobody made.
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
		// The arithmetic reports the row as it falls, and containsLine is the
		// check the caller makes: a clamp here would paint the diagram's first
		// line whenever the caret sat above the block.
		assert.strictEqual(toRegionRow(region, 9), -1);
		assert.strictEqual(toRegionRow(region, 15), 5);
	});

	test('answers whether a line belongs to the region at all', () => {
		// The check the caret needs before its line is translated: the region's
		// own lines are the ones with rows to send.
		assert.ok(containsLine(region, 10), 'the first line');
		assert.ok(containsLine(region, 12), 'a line within');
		assert.ok(containsLine(region, 14), 'the last line, endLine being inclusive');
		assert.ok(!containsLine(region, 9), 'the line above');
		assert.ok(!containsLine(region, 15), 'the line below');
	});
});

suite('sourceRegion: following a line through an edit', () => {
	/**
	 * One content change, in the shape vscode reports.
	 *
	 * @param {number} startLine
	 * @param {number} startCharacter
	 * @param {number} endLine
	 * @param {number} endCharacter
	 * @param {string} text what replaced the range
	 */
	const change = (startLine, startCharacter, endLine, endCharacter, text) => ({
		range: {
			start: { line: startLine, character: startCharacter },
			end: { line: endLine, character: endCharacter }
		},
		text
	});

	test('moves the line down when lines are added above it', () => {
		// Writing a paragraph above a diagram: the panel has to follow it there
		// or it loses the diagram on the next thing the author types.
		assert.strictEqual(trackLine(10, [change(0, 0, 0, 0, 'A new line.\n')]), 11);
		assert.strictEqual(trackLine(10, [change(3, 0, 3, 0, 'one\ntwo\nthree\n')]), 13);
	});

	test('moves the line up when lines are removed above it', () => {
		// A whole line deleted above.
		assert.strictEqual(trackLine(10, [change(2, 0, 3, 0, '')]), 9);
		// Two lines joined into one.
		assert.strictEqual(trackLine(10, [change(2, 4, 3, 2, '')]), 9);
	});

	test('leaves the line alone for an edit above that adds no lines', () => {
		assert.strictEqual(trackLine(10, [change(4, 2, 4, 7, 'reworded')]), 10);
	});

	test('leaves the line alone for edits below it', () => {
		// The ordinary case: every rewrite the diagram makes is inside its own
		// block, which is below the fence.
		assert.strictEqual(trackLine(10, [change(12, 0, 12, 5, ':a;\n:b;')]), 10);
		assert.strictEqual(trackLine(10, [change(20, 0, 24, 0, '')]), 10);
	});

	test('follows a newline inserted immediately before the line', () => {
		// Enter pressed with the caret at the start of the fence: the change
		// ends where the line begins, so the text of the line is untouched and
		// only its number moves.
		assert.strictEqual(trackLine(10, [change(10, 0, 10, 0, '\n')]), 11);
	});

	test('reports a line whose own text was replaced as gone', () => {
		// Typing in the fence itself, or deleting a span that covers it. The
		// fence this line was has gone, and a line number carried over could land
		// on a different diagram -- which the panel would then show and write
		// into.
		assert.strictEqual(trackLine(10, [change(10, 3, 10, 8, 'x')]), LINE_GONE, 'edited');
		assert.strictEqual(trackLine(10, [change(9, 0, 11, 0, '')]), LINE_GONE, 'deleted with');
		assert.strictEqual(trackLine(10, [change(10, 0, 12, 0, '')]), LINE_GONE, 'deleted from');
	});

	test('sums every change of one event, in any order', () => {
		// Multi-cursor edits and reformatting arrive as several changes. Each is
		// measured against the line's position before the event, which leaves the
		// order they arrive in free.
		const above = change(1, 0, 1, 0, 'x\n');
		const alsoAbove = change(5, 0, 6, 0, '');
		const below = change(30, 0, 30, 0, 'y\n');

		assert.strictEqual(trackLine(10, [above, alsoAbove, below]), 10);
		assert.strictEqual(trackLine(10, [below, alsoAbove, above]), 10);
		assert.strictEqual(trackLine(10, [above, above]), 12);
	});

	test('leaves the line alone when nothing changed', () => {
		assert.strictEqual(trackLine(10, []), 10);
	});

	test('can follow a line to the top of the document', () => {
		assert.strictEqual(trackLine(3, [change(0, 0, 3, 0, '')]), 0);
	});
});
