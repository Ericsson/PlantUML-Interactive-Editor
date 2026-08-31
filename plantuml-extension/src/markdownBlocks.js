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
// A Markdown file holds diagrams, in fenced code blocks:
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
// extension.js's business; this file reads text and reports line numbers.
//
// It depends on Node alone, and works on a string and line numbers, which is
// what makes it testable outside the VS Code host.
//
// The scan is a line walk carrying one bit of state, the fence it is inside,
// because a fence has to be read in context. Inside a code block, ```plantuml
// is a line of text:
//
//     ```text
//     ```plantuml        <- content of the text block, a closing fence being
//     @startuml             the one with an empty info string
//     @enduml
//     ```
//
// So every fence is tracked, of either kind, and the ones opened with backticks
// and the exact info string are reported. That keeps a diagram quoted inside
// somebody's example out of the panel, which would otherwise write an edit into
// their example.
//
// A fence indented four spaces or more is read as an ordinary block. CommonMark
// reads it as an indented code block holding literal text, which would take the
// list structure to tell from a fence indented inside a list item, and that
// takes a Markdown parser; a fence in a list item is the case worth serving.

const { containsLine } = require('./sourceRegion');

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
 * Required of a block's content, so that what the panel offers is what the
 * renderer accepts: java takes a source that opens a `@start…` block.
 */
const DIAGRAM_START = /^[ \t]*@start\w+/;

/**
 * A PlantUML diagram found in a Markdown document.
 *
 * A `SourceRegion` -- see sourceRegion.js -- with the fence it came from, so a
 * block found here can be handed straight to `regionSource` and the rest of the
 * translation as it is. The diagram's text comes from `regionSource` reading the
 * document, which keeps one function in charge of what a region says.
 *
 * The range covers the *content*. The fences are the document's, and stay as
 * the author wrote them; `fenceLine` is kept for the places that name the block
 * to the user, a fence being what they see.
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
 * A block is reported once its closing fence is there, that fence being the line
 * the diagram ends at and the end of the range an edit is written back into. So
 * a block being typed joins the list as soon as it is closed.
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
 * A closing fence uses the same character, is at least as long, and carries an
 * empty info string. So ```plantuml inside a ``` block reads as content, and a
 * longer fence holds shorter ones.
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
 *   block the scan tracks so that it reads the lines inside as content
 */
function isPlantUml(open) {
	return open.marker[0] === '`' && open.info.toLowerCase() === PLANTUML_INFO;
}

/**
 * Build the block for a closed ```plantuml fence.
 *
 * @param {string[]} lines the document
 * @param {{ line: number, indent: string }} open the opening fence
 * @param {number} closingLine
 * @returns {MarkdownBlock | undefined} a block once the content opens a
 *   `@start…` block; see DIAGRAM_START
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
 * The block whose content covers `line`.
 *
 * Content lines, the fences being the document's: a fence is where the caret
 * sits while the block is still being typed, and clicking one is a move about
 * the document rather than a request for the diagram it wraps.
 *
 * Answers about the caret's line alone, which is what makes it right for
 * deciding whether the caret has moved into a *different* diagram, where prose
 * means the panel stays where it is.
 *
 * @param {MarkdownBlock[]} blocks
 * @param {number} line zero-based
 * @returns {MarkdownBlock | undefined}
 */
function blockAtLine(blocks, line) {
	return blocks.find((block) => containsLine(block, line));
}

/**
 * The block a panel opening on this document should show.
 *
 * The caret's, so that running the command on a diagram shows that diagram;
 * else the first in the file, so that running it anywhere in a document that
 * has one shows something. A caret in prose falls back that way, and so does a
 * panel pointed at a document from outside an editor.
 *
 * @param {string} text the whole document
 * @param {number} [caretLine] zero-based, where the caret is
 * @returns {MarkdownBlock | undefined} a block for a document that holds one
 */
function blockToShow(text, caretLine) {
	const blocks = findPlantUmlBlocks(text);

	if (caretLine === undefined) {
		return blocks[0];
	}

	return blockAtLine(blocks, caretLine) ?? blocks[0];
}

/**
 * The block the caret has moved into, when the panel should follow it there.
 *
 * How a Markdown file's several diagrams are chosen between: put the caret in
 * one and the panel shows it, which is the gesture VS Code offers for text and
 * what a reader reaches for anyway.
 *
 * The panel stays on the diagram it is showing in the other three cases -- the
 * caret in prose, on a fence, or already in that diagram -- so that reading
 * around a diagram keeps it on screen. That is also why the caret's own block is
 * the whole answer here, where blockToShow falls back to the first: falling back
 * would send the panel to the top of the file as soon as the caret left a
 * diagram.
 *
 * @param {string} text the whole document
 * @param {number} caretLine zero-based
 * @param {MarkdownBlock} [showing] the block on screen
 * @returns {MarkdownBlock | undefined} the block to switch to, or undefined to
 *   stay on the one being shown
 */
function blockToFollow(text, caretLine, showing) {
	const next = blockAtLine(findPlantUmlBlocks(text), caretLine);

	if (!next || next.fenceLine === showing?.fenceLine) {
		return undefined;
	}

	return next;
}

module.exports = {
	findPlantUmlBlocks,
	blockAtLine,
	blockToShow,
	blockToFollow
};
