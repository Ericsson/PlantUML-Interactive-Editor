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

// Locates PlantUML diagrams in a Markdown document.
//
// Diagrams are fenced code blocks tagged `plantuml`:
//
//     ```plantuml
//     @startuml
//     a -> b
//     @enduml
//     ```
//
// This module scans document text and reports the line ranges of these
// blocks. It has no VS Code dependency, so it can be unit tested as plain
// string/line-number logic.
//
// The scan walks lines while tracking the currently open fence (if any), so
// that fence markers found inside another code block are treated as content
// rather than as a new block boundary. Only fences opened with backticks and
// the exact `plantuml` info string are reported as diagrams.

const { containsLine } = require('./sourceRegion');

/**
 * Matches a fence opening line: leading whitespace, a run of 3+ backticks or
 * tildes, and an info string.
 */
const FENCE = /^([ \t]*)(`{3,}|~{3,})[ \t]*(.*?)[ \t]*$/;

/** The info string that marks a diagram block. Compared case-insensitively. */
const PLANTUML_INFO = 'plantuml';

/** Matches a PlantUML diagram's opening tag (`@startuml`, `@startmindmap`, etc.). */
const DIAGRAM_START = /^[ \t]*@start\w+/;

/**
 * A PlantUML diagram block found in a Markdown document.
 *
 * The line range covers the block's content only, not its fences.
 *
 * @typedef {object} MarkdownBlock
 * @property {number} fenceLine zero-based line of the opening fence
 * @property {number} startLine zero-based first content line
 * @property {number} endLine zero-based last content line, inclusive
 * @property {string} indent the opening fence's leading whitespace
 */

/**
 * Finds all PlantUML blocks in `text`, in document order.
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
 * Whether the current line's fence closes the given open fence.
 *
 * A closing fence uses the same character type, is at least as long, and has
 * an empty info string.
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
 * Whether an opening fence marks a PlantUML diagram block (backtick fence with
 * `plantuml` info string).
 *
 * @param {{ marker: string, info: string }} open
 * @returns {boolean}
 */
function isPlantUml(open) {
	return open.marker[0] === '`' && open.info.toLowerCase() === PLANTUML_INFO;
}

/**
 * Builds the block descriptor for a closed ```plantuml fence.
 *
 * @param {string[]} lines the document
 * @param {{ line: number, indent: string }} open the opening fence
 * @param {number} closingLine
 * @returns {MarkdownBlock | undefined} the block, or undefined if its content
 *   contains no `@start…` line
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
 * Finds the block whose content range contains `line`.
 *
 * @param {MarkdownBlock[]} blocks
 * @param {number} line zero-based
 * @returns {MarkdownBlock | undefined}
 */
function blockAtLine(blocks, line) {
	return blocks.find((block) => containsLine(block, line));
}

/**
 * Picks the block a newly opened panel should display: the block containing
 * the caret, or the first block in the document if the caret is outside any
 * block or not given.
 *
 * @param {string} text the whole document
 * @param {number} [caretLine] zero-based, where the caret is
 * @returns {MarkdownBlock | undefined}
 */
function blockToShow(text, caretLine) {
	const blocks = findPlantUmlBlocks(text);

	if (caretLine === undefined) {
		return blocks[0];
	}

	return blockAtLine(blocks, caretLine) ?? blocks[0];
}

/**
 * Picks the block an already-open panel should switch to when the caret
 * moves, for following the caret between diagrams in a multi-diagram
 * document.
 *
 * @param {string} text the whole document
 * @param {number} caretLine zero-based
 * @param {MarkdownBlock} [showing] the block currently displayed
 * @returns {MarkdownBlock | undefined} the block to switch to, or undefined
 *   to keep showing the current block (caret is in prose, on a fence, or
 *   still inside `showing`)
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
