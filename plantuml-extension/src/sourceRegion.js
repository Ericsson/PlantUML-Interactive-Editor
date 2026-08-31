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

// Which part of the document is the diagram.
//
// Everything downstream of the host -- the webview, the shim, the sidecar's 79
// routes -- deals in one complete PlantUML source and nothing else. For a
// `.puml` file that is the whole document, and the extension was written on
// that assumption: read it all, send it all, replace it all. A diagram in a
// Markdown code fence breaks the assumption, because only a slice of the file
// is the diagram and the rest is prose that must come out untouched.
//
// A region is that slice: a line range, plus the indentation its lines carry
// inside the document. The whole document is simply the region that covers it,
// which is what keeps `.puml` on the same code path as Markdown rather than
// beside it.
//
// This module is where the boundary is crossed, in all four directions:
//
//     region -> source    regionSource,  for the webview and the renderer
//     source -> region    indentSource,  for the write-back
//     region -> document  toDocumentRow, for the editor decorations
//     document -> region  toRegionRow,   for the caret
//
// Sign errors in those translations are the whole risk of the feature -- an
// off-by-one paints the wrong line, an inverted subtraction writes a diagram
// into the prose -- so each direction is named rather than open-coded at the
// call sites, and each is unit-tested.
//
// Requires nothing from vscode, which is what makes it testable in plain Node,
// and takes text rather than a TextDocument for the same reason. Line numbers
// are zero-based throughout, matching both vscode and Ace.

/**
 * The part of a document that holds one diagram.
 *
 * `endLine` is inclusive: the region is a set of whole lines, and the last one
 * belongs to it. `indent` is what every line of the region carries on account
 * of where it sits in the document -- a Markdown fence inside a list item --
 * and never anything the diagram itself is written with.
 *
 * @typedef {object} SourceRegion
 * @property {number} startLine zero-based, inclusive
 * @property {number} endLine zero-based, inclusive
 * @property {string} indent leading whitespace shared by the region's lines
 */

/**
 * The region covering all of `text`.
 *
 * What every file that is a diagram in its own right gets, so that the read,
 * the write and the two row translations have one implementation rather than a
 * region case and a whole-file case. `regionSource` against this region returns
 * `text` unchanged, byte for byte, whatever line endings it uses.
 *
 * Derived from the text on each use rather than stored, because the answer
 * changes with every edit that adds or removes a line, and a remembered one
 * would be a stale range to write into.
 *
 * @param {string} text the whole document
 * @returns {SourceRegion}
 */
function wholeDocumentRegion(text) {
	return { startLine: 0, endLine: text.split('\n').length - 1, indent: '' };
}

/**
 * The diagram held by `region`, ready for the renderer.
 *
 * Split on '\n' alone, and rejoined the same way, so a CRLF document keeps its
 * carriage returns exactly where they were: this is a slice of the user's file,
 * not a rewrite of it, and the whole-document case has to come back identical.
 *
 * A region reaching past the end of the text yields what is there. The caller
 * that let it go stale is the one that has to notice; see the region tracking
 * in extension.js.
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
 * Remove a region's indentation from one of its lines.
 *
 * The diagram handed to the renderer must not carry the document's
 * indentation. Rendering would survive it -- PlantUML ignores leading space --
 * but every rewrite comes back without it, and writing that into an indented
 * fence takes the block out of the list item it was in and quietly breaks the
 * Markdown.
 *
 * Lines are not required to match the region exactly. Editors leave blank lines
 * empty rather than padded, and hand-written blocks are not always uniform, so
 * a line carrying less than the region's indentation gives up what it has.
 * Anything beyond that indentation is the diagram's own and is kept: PlantUML's
 * nesting is written with leading space, and the app's own indentPuml()
 * produces it.
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
 * Put a region's indentation back on a diagram about to be written into it.
 *
 * The inverse of the strip above, and next to it because the pair has to
 * agree: a change to one is a change to both.
 *
 * Blank lines are left alone. Indenting them would put trailing whitespace
 * into the user's file, which many editors strip on save -- making the file
 * dirty again just after a diagram edit, for a change nobody made.
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
 * Where a row of the diagram is in the document.
 *
 * The direction the highlights travel: the app marks a row of the source it was
 * given, and the decoration has to land on that line of the file.
 *
 * @param {SourceRegion} region
 * @param {number} row zero-based, relative to the region
 * @returns {number} zero-based, relative to the document
 */
function toDocumentRow(region, row) {
	return region.startLine + row;
}

/**
 * Where a line of the document is in the diagram.
 *
 * The direction the caret travels. The result is outside the diagram -- past
 * its end, or negative -- for a line outside the region, which the caller is
 * expected to check rather than post; `containsLine` is that check.
 *
 * @param {SourceRegion} region
 * @param {number} line zero-based, relative to the document
 * @returns {number} zero-based, relative to the region
 */
function toRegionRow(region, line) {
	return line - region.startLine;
}

/**
 * Whether `line` is one of the region's.
 *
 * The question the caret raises: a line outside the region has no row in the
 * diagram, so there is nothing to say about it rather than a row to clamp it
 * to. Both ends inclusive, `endLine` being part of the region.
 *
 * @param {SourceRegion} region
 * @param {number} line zero-based, relative to the document
 * @returns {boolean}
 */
function containsLine(region, line) {
	return line >= region.startLine && line <= region.endLine;
}

module.exports = {
	wholeDocumentRegion,
	regionSource,
	stripIndent,
	indentSource,
	toDocumentRow,
	toRegionRow,
	containsLine
};
