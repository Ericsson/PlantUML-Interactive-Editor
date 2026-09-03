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

// Represents the part of a document that holds a PlantUML diagram, and
// converts between document coordinates and diagram-source coordinates.
//
// For a `.puml` file, the diagram is the whole document. For a diagram in a
// Markdown fenced code block, it's a line-range slice of the file, with the
// prose around it left untouched.
//
// A SourceRegion describes that slice: a line range plus the indentation its
// lines share. The whole document is represented as the region that covers
// all of it, so `.puml` files and Markdown fences share the same code path.
//
// Conversions in this module:
//
//     region -> source    regionSource,  diagram text for the webview/renderer
//     source -> region    indentSource,  diagram text for write-back
//     region -> document  toDocumentRow, document line for editor decorations
//     document -> region  toRegionRow,   diagram row for the caret position
//
// trackLine tracks where a line moves to after a document edit, used to keep
// a diagram's region correct as text is typed around it.
//
// Depends only on Node; works on plain text and line numbers. Line numbers
// are zero-based throughout, matching both vscode and Ace.

/**
 * A line range within a document that holds one diagram.
 *
 * @typedef {object} SourceRegion
 * @property {number} startLine zero-based, inclusive
 * @property {number} endLine zero-based, inclusive
 * @property {string} indent leading whitespace shared by the region's lines,
 *   distinct from the diagram's own indentation
 */

/**
 * Builds the region covering the entire document.
 *
 * @param {string} text the whole document
 * @returns {SourceRegion}
 */
function wholeDocumentRegion(text) {
	return { startLine: 0, endLine: text.split('\n').length - 1, indent: '' };
}

/**
 * Extracts the diagram text covered by `region`, with the region's shared
 * indentation stripped from each line.
 *
 * Splits and rejoins on '\n' only, so CRLF line endings within the region are
 * preserved.
 *
 * @param {string} text the whole document
 * @param {SourceRegion} region
 * @returns {string}
 */
function regionSource(text, region) {
	return text
		.split('\n')
		.slice(region.startLine, region.endLine + 1)
		.map((line) => stripIndent(line, region.indent))
		.join('\n');
}

/**
 * Removes up to `indent` worth of leading whitespace from `line`.
 *
 * A line with less leading whitespace than `indent` has all of its
 * whitespace removed instead. Whitespace beyond `indent` is left in place,
 * since that's the diagram's own indentation (e.g. from nesting), not the
 * document's.
 *
 * @param {string} line
 * @param {string} indent
 * @returns {string}
 */
function stripIndent(line, indent) {
	if (!indent) {
		return line;
	}

	if (line.startsWith(indent)) {
		return line.slice(indent.length);
	}

	const whitespace = /^[ \t]*/.exec(line)[0];

	return line.slice(Math.min(whitespace.length, indent.length));
}

/**
 * Prepends `indent` to each non-blank line of `source`. The inverse of
 * `stripIndent`. Blank lines are left as-is to avoid introducing trailing
 * whitespace.
 *
 * @param {string} source the diagram, as the renderer returned it
 * @param {string} indent
 * @returns {string}
 */
function indentSource(source, indent) {
	if (!indent) {
		return source;
	}

	return source
		.split('\n')
		.map((line) => (line.trim() === '' ? line : `${indent}${line}`))
		.join('\n');
}

/**
 * Converts a diagram-relative row to a document line number.
 *
 * @param {SourceRegion} region
 * @param {number} row zero-based, relative to the region
 * @returns {number} zero-based, relative to the document
 */
function toDocumentRow(region, row) {
	return region.startLine + row;
}

/**
 * Converts a document line number to a diagram-relative row.
 *
 * @param {SourceRegion} region
 * @param {number} line zero-based, relative to the document
 * @returns {number} zero-based, relative to the region
 */
function toRegionRow(region, line) {
	return line - region.startLine;
}

/**
 * Whether `line` falls within `region` (inclusive on both ends).
 *
 * @param {SourceRegion} region
 * @param {number} line zero-based, relative to the document
 * @returns {boolean}
 */
function containsLine(region, line) {
	return line >= region.startLine && line <= region.endLine;
}

/** Return value of trackLine for a line that was rewritten by an edit. */
const LINE_GONE = -1;

/**
 * Computes where `line` ends up after a set of document content changes, or
 * returns LINE_GONE if the change rewrote that line's own text.
 *
 * For each change, `line` is classified as:
 *
 *   - entirely above it: `line` shifts by the number of lines added or
 *     removed. A change ending exactly at the start of `line` counts as
 *     above (e.g. pressing Enter with the caret right before the line).
 *   - entirely below it: `line` is unaffected.
 *   - containing it: `line`'s text was replaced, so LINE_GONE is returned
 *     regardless of any later changes.
 *
 * Change ranges are given in before-edit document coordinates and are each
 * measured against `line`'s original position, so changes from a single
 * edit event can be processed in any order.
 *
 * @param {number} line zero-based
 * @param {readonly {range: {start: {line: number}, end: {line: number,
 *   character: number}}, text: string}[]} changes content changes from a
 *   single vscode change event
 * @returns {number} the line's new number, or LINE_GONE
 */
function trackLine(line, changes) {
	let shifted = line;

	for (const change of changes) {
		const { start, end } = change.range;

		if (start.line > line) {
			continue;
		}

		if (end.line < line || (end.line === line && end.character === 0)) {
			const added = change.text.split('\n').length - 1;
			shifted += added - (end.line - start.line);
			continue;
		}

		return LINE_GONE;
	}

	return shifted;
}

module.exports = {
	wholeDocumentRegion,
	regionSource,
	stripIndent,
	indentSource,
	toDocumentRow,
	toRegionRow,
	containsLine,
	trackLine,
	LINE_GONE
};
