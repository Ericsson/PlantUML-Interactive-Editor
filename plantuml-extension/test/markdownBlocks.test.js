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

const { findPlantUmlBlocks, blockAtLine, blockToShow } = require('../src/markdownBlocks');
const { regionSource } = require('../src/sourceRegion');

/** @param {string[]} lines */
const md = (...lines) => lines.join('\n');

const DIAGRAM = ['@startuml', 'a -> b', '@enduml'];

suite('markdownBlocks: what counts as a diagram', () => {
	test('finds a fenced block', () => {
		const text = md('# Notes', '', '```plantuml', ...DIAGRAM, '```', '', 'After.');

		const [block, ...rest] = findPlantUmlBlocks(text);

		assert.deepStrictEqual(rest, [], 'found more than the one block');
		// The range covers the content: the fences are the document's.
		assert.strictEqual(block.fenceLine, 2);
		assert.strictEqual(block.startLine, 3);
		assert.strictEqual(block.endLine, 5);
		assert.strictEqual(block.indent, '');
		// A block is a region, so this is how its text is read -- there is no
		// second copy of it on the block to disagree with the document.
		assert.strictEqual(regionSource(text, block), DIAGRAM.join('\n'));
	});

	test('finds every block, in order', () => {
		// Which one the panel shows is decided by the caret, so the order here
		// is the document's and the caller relies on it.
		const text = md(
			'```plantuml',
			'@startuml',
			'first',
			'@enduml',
			'```',
			'prose',
			'```plantuml',
			'@startuml',
			'second',
			'@enduml',
			'```'
		);

		const blocks = findPlantUmlBlocks(text);

		assert.strictEqual(blocks.length, 2);
		assert.match(regionSource(text, blocks[0]), /first/);
		assert.match(regionSource(text, blocks[1]), /second/);
		assert.strictEqual(blocks[1].startLine, 7);
	});

	test('accepts the info string in any case', () => {
		// Markdown info strings are not case sensitive to any renderer, and
		// PlantUML's own documentation writes it both ways.
		assert.strictEqual(
			findPlantUmlBlocks(md('```PlantUML', ...DIAGRAM, '```')).length,
			1
		);
	});

	test('tolerates whitespace around the info string', () => {
		// What an editor leaves behind, not a different syntax.
		assert.strictEqual(
			findPlantUmlBlocks(md('  ```plantuml  ', ...DIAGRAM, '  ```')).length,
			1
		);
	});

	test('ignores an info string that only starts with plantuml', () => {
		// `plantuml-svg` and friends belong to other extensions' renderers, and
		// may not mean a diagram this one can edit.
		for (const info of ['plantuml-svg', 'plantumlx', 'plantuml png']) {
			assert.deepStrictEqual(
				findPlantUmlBlocks(md('```' + info, ...DIAGRAM, '```')),
				[],
				`${info} was treated as a diagram`
			);
		}
	});

	test('ignores the aliases and tilde fences', () => {
		// Deliberately narrow: exactly ```plantuml, per the feature's spec.
		for (const opening of ['```puml', '```uml', '~~~plantuml', '```']) {
			assert.deepStrictEqual(
				findPlantUmlBlocks(md(opening, ...DIAGRAM, opening.replace(/\w+$/, ''))),
				[],
				`${opening} was treated as a diagram`
			);
		}
	});

	test('ignores a block with no @start line', () => {
		// Nothing java could be given: it would come back as a failed render
		// rather than as a diagram, so it is not offered as one.
		assert.deepStrictEqual(
			findPlantUmlBlocks(md('```plantuml', 'a -> b', '```')),
			[]
		);
	});

	test('accepts any @start flavour', () => {
		// Which flavour a diagram is is not this module's business.
		for (const start of ['@startuml', '@startmindmap', '@startgantt', '@startjson']) {
			assert.strictEqual(
				findPlantUmlBlocks(md('```plantuml', start, 'x', '@end', '```')).length,
				1,
				`${start} was not recognised`
			);
		}
	});

	test('ignores an empty block', () => {
		assert.deepStrictEqual(findPlantUmlBlocks(md('```plantuml', '```')), []);
	});

	test('ignores an unterminated fence', () => {
		// It swallows the rest of the file by CommonMark's reading, so there is
		// no line at which the diagram ends -- and no range an edit could be
		// written back into. A block being typed becomes available once its
		// closing fence is there.
		assert.deepStrictEqual(findPlantUmlBlocks(md('```plantuml', ...DIAGRAM)), []);
	});

	test('finds nothing in a document without blocks', () => {
		assert.deepStrictEqual(findPlantUmlBlocks(md('# Title', '', 'Prose.')), []);
		assert.deepStrictEqual(findPlantUmlBlocks(''), []);
	});

	test('does not read a diagram quoted inside another code block', () => {
		// The reason the scan tracks every fence rather than matching openings:
		// a closing fence may carry no info string, so the ```plantuml line
		// here is content of the ```text block. Reported as a diagram, a panel
		// edit would rewrite somebody's example of how to write one.
		const text = md(
			'How to write one:',
			'',
			'```text',
			'```plantuml',
			...DIAGRAM,
			'```',
			'',
			'Prose.'
		);

		assert.deepStrictEqual(findPlantUmlBlocks(text), []);
	});

	test('reads a diagram after a code block that quoted one', () => {
		// The state is per block, not per document: a fence consumed as content
		// must not leave the scan confused about what is open.
		const text = md(
			'```text',
			'```plantuml',
			'@startuml',
			'quoted',
			'@enduml',
			'```',
			'',
			'```plantuml',
			'@startuml',
			'real',
			'@enduml',
			'```'
		);

		const blocks = findPlantUmlBlocks(text);

		assert.strictEqual(blocks.length, 1);
		assert.match(regionSource(text, blocks[0]), /real/);
	});

	test('lets a longer fence hold shorter ones', () => {
		// CommonMark: a closing fence must be at least as long as its opener,
		// which is how a documentation example nests fences at all.
		const text = md('````plantuml', ...DIAGRAM, '```', 'still inside', '````');

		const [block] = findPlantUmlBlocks(text);

		assert.strictEqual(block.endLine, 5);
		assert.match(regionSource(text, block), /still inside/);
	});

	test('closes a block on a longer fence', () => {
		const text = md('```plantuml', ...DIAGRAM, '`````');

		assert.strictEqual(findPlantUmlBlocks(text)[0].endLine, 3);
	});
});

suite('markdownBlocks: indented fences', () => {
	test('reports the fence indentation', () => {
		// A fence inside a list item carries the item's indentation, and the
		// diagram must not: every rewrite comes back without it, and writing
		// that back would take the block out of the list. Stripping it is
		// sourceRegion's job; reporting it is this module's.
		const text = md(
			'- The flow:',
			'',
			'  ```plantuml',
			'  @startuml',
			'  a -> b',
			'  @enduml',
			'  ```'
		);

		const [block] = findPlantUmlBlocks(text);

		assert.strictEqual(block.indent, '  ');
		assert.strictEqual(block.startLine, 3);
		assert.strictEqual(block.endLine, 5);
		assert.strictEqual(regionSource(text, block), DIAGRAM.join('\n'));
	});

	test('does not require the content to match the fence', () => {
		// Hand-written blocks are not uniform, and the fence is what says how
		// far in the block sits.
		const text = md('  ```plantuml', '@startuml', '  a -> b', '  ```');

		const [block] = findPlantUmlBlocks(text);

		assert.strictEqual(block.indent, '  ');
		assert.strictEqual(regionSource(text, block), '@startuml\na -> b');
	});
});

suite('markdownBlocks: the block at a line', () => {
	const text = md(
		'# Notes',
		'```plantuml',
		'@startuml',
		'a -> b',
		'@enduml',
		'```',
		'prose',
		'```plantuml',
		'@startuml',
		'c -> d',
		'@enduml',
		'```'
	);
	const blocks = findPlantUmlBlocks(text);

	test('finds the block the caret is in', () => {
		assert.strictEqual(blockAtLine(blocks, 3), blocks[0]);
		assert.strictEqual(blockAtLine(blocks, 9), blocks[1]);
	});

	test('includes the first and last content lines', () => {
		assert.strictEqual(blockAtLine(blocks, 2), blocks[0]);
		assert.strictEqual(blockAtLine(blocks, 4), blocks[0]);
	});

	test('finds nothing on a fence or in prose', () => {
		// A fence belongs to the document, not to the diagram it wraps, and is
		// also where the caret sits while the block is still being typed.
		assert.strictEqual(blockAtLine(blocks, 1), undefined, 'the opening fence');
		assert.strictEqual(blockAtLine(blocks, 5), undefined, 'the closing fence');
		assert.strictEqual(blockAtLine(blocks, 0), undefined, 'the heading');
		assert.strictEqual(blockAtLine(blocks, 6), undefined, 'the prose between');
	});

	test('finds nothing when there are no blocks', () => {
		assert.strictEqual(blockAtLine([], 0), undefined);
	});
});

suite('markdownBlocks: the block a panel opens on', () => {
	const text = md(
		'# Notes',
		'```plantuml',
		'@startuml',
		'first',
		'@enduml',
		'```',
		'prose',
		'```plantuml',
		'@startuml',
		'second',
		'@enduml',
		'```'
	);

	test('shows the diagram the caret is in', () => {
		// Running the command on a diagram means that diagram, which is the
		// whole point of the caret deciding.
		assert.strictEqual(blockToShow(text, 9).fenceLine, 7);
		assert.strictEqual(blockToShow(text, 3).fenceLine, 1);
	});

	test('falls back to the first diagram', () => {
		// A caret in prose is not a choice between diagrams, and a panel can be
		// pointed at a document no editor has the focus of. Both still show
		// something rather than nothing.
		assert.strictEqual(blockToShow(text, 6).fenceLine, 1, 'caret in prose');
		assert.strictEqual(blockToShow(text, 0).fenceLine, 1, 'caret above every block');
		assert.strictEqual(blockToShow(text).fenceLine, 1, 'no caret at all');
	});

	test('has nothing to show for a document without blocks', () => {
		// What the caller reports rather than opening a panel on prose.
		assert.strictEqual(blockToShow(md('# Notes', 'Prose.'), 0), undefined);
		assert.strictEqual(blockToShow(md('```text', 'not a diagram', '```')), undefined);
	});
});
