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
	findPlantUmlBlocks,
	blockAtLine,
	blockToShow,
	blockToFollow
} = require('../src/markdownBlocks');
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
		// A diagram is what java takes and what the panel offers: content that
		// opens a @start block.
		assert.deepStrictEqual(
			findPlantUmlBlocks(md('```plantuml', 'a -> b', '```')),
			[]
		);
	});

	test('accepts any @start flavour', () => {
		// Any flavour counts; which one a diagram is belongs to the renderer.
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
		// A closing fence is the line the diagram ends at, and the end of the
		// range an edit is written back into, so a block joins the list once it
		// is closed. CommonMark reads an open fence as running to the end of the
		// file, which is the whole of the rest of the document.
		assert.deepStrictEqual(findPlantUmlBlocks(md('```plantuml', ...DIAGRAM)), []);
	});

	test('finds nothing in a document without blocks', () => {
		assert.deepStrictEqual(findPlantUmlBlocks(md('# Title', '', 'Prose.')), []);
		assert.deepStrictEqual(findPlantUmlBlocks(''), []);
	});

	test('does not read a diagram quoted inside another code block', () => {
		// Why the scan tracks every fence: a closing fence is the one carrying an
		// empty info string, so the ```plantuml line here is content of the
		// ```text block, and stays somebody's example of how to write one.
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
		// The state is per block, so a fence consumed as content leaves the scan
		// knowing which fence is still open.
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
		// diagram carries its own: every rewrite comes back at column zero, and
		// the write-back puts the fence's share back so the block stays in the
		// list. Stripping it is sourceRegion's job; reporting it is this
		// module's.
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
		// The fence says how far in the block sits, which is what hand-written
		// blocks vary against.
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
		// A fence belongs to the document, and is where the caret sits while the
		// block is still being typed.
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
		// A caret in prose leaves the choice open, and a panel can be pointed at
		// a document whose editor has the focus of nothing. Both show the first
		// diagram in the file.
		assert.strictEqual(blockToShow(text, 6).fenceLine, 1, 'caret in prose');
		assert.strictEqual(blockToShow(text, 0).fenceLine, 1, 'caret above every block');
		assert.strictEqual(blockToShow(text).fenceLine, 1, 'no caret at all');
	});

	test('has nothing to show for a document without blocks', () => {
		// What the caller reports to the user, a panel opening on a diagram.
		assert.strictEqual(blockToShow(md('# Notes', 'Prose.'), 0), undefined);
		assert.strictEqual(blockToShow(md('```text', 'not a diagram', '```')), undefined);
	});
});

suite('markdownBlocks: the diagram the caret moves into', () => {
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
	const [first, second] = findPlantUmlBlocks(text);

	test('follows the caret into another diagram', () => {
		// The only gesture available for choosing between a file's diagrams:
		// put the caret in one and the panel shows it. Compared by value, each
		// scan of the text producing its own objects.
		assert.deepStrictEqual(blockToFollow(text, 9, first), second);
		assert.deepStrictEqual(blockToFollow(text, 3, second), first);
	});

	test('stays on the diagram already shown', () => {
		// Moving about inside the diagram on screen keeps it there, which spares
		// a resend and a retitle.
		for (const line of [2, 3, 4]) {
			assert.strictEqual(blockToFollow(text, line, first), undefined, `line ${line}`);
		}
	});

	test('stays put for a caret in prose or on a fence', () => {
		// The sticky rule: reading around a diagram keeps it on screen, which is
		// why the caret's own block is the whole answer here.
		assert.strictEqual(blockToFollow(text, 0, first), undefined, 'the heading');
		assert.strictEqual(blockToFollow(text, 6, first), undefined, 'the prose between');
		assert.strictEqual(blockToFollow(text, 1, first), undefined, 'an opening fence');
		assert.strictEqual(blockToFollow(text, 5, first), undefined, 'a closing fence');
		// Including another diagram's fence, which is the caret on its way in.
		assert.strictEqual(blockToFollow(text, 7, first), undefined, "another's fence");
	});

	test('adopts the block when the panel is on none', () => {
		assert.deepStrictEqual(blockToFollow(text, 3, undefined), first);
	});

	test('adopts the same diagram again once its fence has moved', () => {
		// How the panel recovers after an edit above it moved the fence out from
		// under the block being shown: the caret coming back in finds it at its
		// new line, which is a different block by the only identity there is.
		const shifted = md('# Notes', 'A new line.', ...text.split('\n').slice(1));

		const adopted = blockToFollow(shifted, 4, first);

		assert.ok(adopted, 'the moved block was not adopted');
		assert.strictEqual(adopted.fenceLine, first.fenceLine + 1);
	});
});
