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

// Finds the PlantUML diagrams inside a Markdown document.
//
// A Markdown file is not a diagram; it *contains* diagrams, in fenced code
// blocks:
//
//     Some prose.
//
//     ```plantuml
//     @startuml
//     a -> b
//     @enduml
//     ```
//
// This module answers where those blocks are. Everything else about the
// feature -- which one the panel shows, how an edit is written back -- is
// extension.js's business; this file only reads text and reports line numbers.
//
// Requires nothing from vscode, which is what makes it testable in plain Node.
// It takes a string rather than a TextDocument for the same reason.
//
// The scan is a line walk with one bit of state -- the fence we are inside --
// rather than a set of regex matches over the whole text, because a fence found
// in isolation cannot be trusted. Inside a code block, ```plantuml is just a
// line of text:
//
//     ```text
//     ```plantuml        <- content of the text block, not an opening fence:
//     @startuml             a closing fence may carry no info string
//     @enduml
//     ```
//
// So every fence is tracked, of either kind, and only the ones opened with
// backticks and the exact info string are reported. Missing a diagram is a
// feature that did not fire; reporting one that is quoted inside another block
// would have the panel write a diagram edit into somebody's example.
//
// Deliberately not handled: a fence indented four spaces or more, which
// CommonMark reads as an indented code block holding literal text. Telling that
// from a fence legitimately indented inside a list item needs the list
// structure, which needs a Markdown parser, and the failure it would prevent --
// rendering a diagram somebody wrote as an example of how to write one -- is
// rarer than the list-item case it would break.

/**
 * Opening fence: indentation, the run of fence characters, and the info string.
 *
 * Any indentation is allowed, because a fence inside a list item carries the
 * item's; see indent on the returned block for what that costs the caller.
 */
const FENCE = /^([ \t]*)(`{3,}|~{3,})[ \t]*(.*?)[ \t]*$/;

/** The one info string that marks a diagram. Compared case-insensitively. */
const PLANTUML_INFO = 'plantuml';

/**
 * A diagram's opening line, in any of PlantUML's flavours.
 *
 * Required of a block's content: a ```plantuml fence holding a fragment with no
 * `@start…` is not something the renderer can be given -- java would reject it
 * -- so it is passed over rather than offered as a diagram.
 */
const DIAGRAM_START = /^[ \t]*@start\w+/;

/**
 * A PlantUML diagram found in a Markdown document.
 *
 * A `SourceRegion` -- see sourceRegion.js -- with the fence it came from, so a
 * block found here can be handed straight to `regionSource` and the rest of the
 * translation without being converted into anything. The diagram's own text is
 * deliberately not carried along: one function reads the text of a region, and
 * two copies of it could disagree.
 *
 * The range covers the *content* only. The fences are the document's, not the
 * diagram's, and neither one is ever rewritten; `fenceLine` is kept for the
 * places that name the block to the user, a fence being what they see.
 *
 * @typedef {object} MarkdownBlock
 * @property {number} fenceLine zero-based line of the opening fence
 * @property {number} startLine zero-based first content line
 * @property {number} endLine zero-based last content line, inclusive
 * @property {string} indent the opening fence's leading whitespace, which the
 *   content lines carry and a write-back has to restore
 */

/**
 * The PlantUML blocks in `text`, in the order they appear.
 *
 * A block must be closed to be reported. An unterminated fence swallows the
 * rest of the file by CommonMark's reading, so there is no line at which the
 * diagram ends -- and a range that ends at the end of the document is not one
 * an edit can be written back into safely. The practical effect is that a block
 * being typed becomes available once its closing fence is there.
 *
 * @param {string} text the whole document
 * @returns {MarkdownBlock[]}
 */
function findPlantUmlBlocks(text) {
	const lines = text.split('\n');
	/** @type {MarkdownBlock[]} */
	const blocks = [];

	/** The fence we are inside, or null between blocks. */
	let open = null;

	for (let line = 0; line < lines.length; line++) {
		const match = FENCE.exec(lines[line]);

		if (!open) {
			if (match) {
				const [, indent, marker, info] = match;
				open = { line, indent, marker, info };
			}
			continue;
		}

		if (!closes(open, match)) {
			continue;
		}

		if (isPlantUml(open)) {
			const block = describe(lines, open, line);

			if (block) {
				blocks.push(block);
			}
		}

		open = null;
	}

	return blocks;
}

/**
 * Whether a fence line ends the block that is open.
 *
 * A closing fence must use the same character, be at least as long, and carry
 * no info string -- so ```plantuml inside a ``` block is content rather than
 * the end of it, and a longer fence can hold shorter ones.
 *
 * @param {{ marker: string }} open the fence that is open
 * @param {RegExpExecArray | null} match the current line, if it is a fence
 * @returns {boolean}
 */
function closes(open, match) {
	if (!match) {
		return false;
	}

	const [, , marker, info] = match;

	return (
		info === '' &&
		marker[0] === open.marker[0] &&
		marker.length >= open.marker.length
	);
}

/**
 * @param {{ marker: string, info: string }} open
 * @returns {boolean} whether this fence opens a diagram, as opposed to a code
 *   block this module only tracks so as not to read inside it
 */
function isPlantUml(open) {
	return open.marker[0] === '`' && open.info.toLowerCase() === PLANTUML_INFO;
}

/**
 * Build the block for a closed ```plantuml fence, or reject it.
 *
 * @param {string[]} lines the document
 * @param {{ line: number, indent: string }} open the opening fence
 * @param {number} closingLine
 * @returns {MarkdownBlock | undefined} undefined when the content is not a
 *   diagram; see DIAGRAM_START
 */
function describe(lines, open, closingLine) {
	const startLine = open.line + 1;
	const endLine = closingLine - 1;
	const content = lines.slice(startLine, endLine + 1);

	if (!content.some((line) => DIAGRAM_START.test(line))) {
		return undefined;
	}

	return {
		fenceLine: open.line,
		startLine,
		endLine,
		indent: open.indent
	};
}

/**
 * The block containing `line`, if any.
 *
 * A line inside the content, not on a fence: the fences belong to the document.
 * Clicking one is not a request to edit the diagram it wraps, and it is also
 * where the caret sits just after typing the fence, before the diagram exists.
 *
 * @param {MarkdownBlock[]} blocks
 * @param {number} line zero-based
 * @returns {MarkdownBlock | undefined}
 */
function blockAtLine(blocks, line) {
	return blocks.find((block) => line >= block.startLine && line <= block.endLine);
}

module.exports = {
	findPlantUmlBlocks,
	blockAtLine
};
