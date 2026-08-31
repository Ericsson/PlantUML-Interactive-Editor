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
// routes -- deals in one complete PlantUML source. For a `.puml` file that is
// the whole document, and the extension was written on that assumption: read it
// all, send it all, replace it all. A diagram in a Markdown code fence is a
// slice of the file, and the prose around it comes out untouched.
//
// A region is that slice: a line range, plus the indentation its lines carry
// inside the document. The whole document is the region that covers it, which is
// what keeps `.puml` on the same code path as Markdown.
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
// into the prose -- so each direction is named at the call sites, and each is
// unit-tested.
//
// One more piece of line arithmetic lives here for the same reason: trackLine,
// which says where a line has moved to after an edit. That is what keeps a
// diagram findable while the prose around it is being written.
//
// It depends on Node alone, and works on text and line numbers, which is what
// makes it testable outside the VS Code host. Line numbers are zero-based
// throughout, matching both vscode and Ace.

/**
 * The part of a document that holds one diagram.
 *
 * `endLine` is inclusive: the region is a set of whole lines, and the last one
 * belongs to it. `indent` is what every line of the region carries on account of
 * where it sits in the document -- a Markdown fence inside a list item -- as
 * distinct from the indentation the diagram itself is written with.
 *
 * @typedef {object} SourceRegion
 * @property {number} startLine zero-based, inclusive
 * @property {number} endLine zero-based, inclusive
 * @property {string} indent leading whitespace shared by the region's lines
 */

/**
 * The region covering all of `text`.
 *
 * What every file that is a diagram in its own right gets, so that the read, the
 * write and the two row translations have one implementation between them.
 * `regionSource` against this region returns `text` unchanged, byte for byte,
 * whatever line endings it uses.
 *
 * Derived from the text on each use, because the answer changes with every edit
 * that adds or removes a line, and a write goes to the range as it is now.
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
 * and the whole-document case comes back identical.
 *
 * A region reaching past the end of the text yields what is there, leaving it to
 * the caller to notice; see the region tracking in extension.js.
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
 * The diagram handed to the renderer carries the diagram's own indentation and
 * none of the document's. PlantUML ignores leading space either way, but every
 * rewrite comes back at column zero, and writing that into an indented fence
 * would move the block out of the list item it was in.
 *
 * A line carrying less than the region's indentation gives up what it has, which
 * is how the blank lines editors leave unpadded and the odd hand-written block
 * come through. What a line carries beyond that indentation is the diagram's own
 * and is kept: PlantUML's nesting is written with leading space, and the app's
 * own indentPuml() produces it.
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
 * Blank lines are left as they are, which keeps trailing whitespace out of the
 * user's file -- many editors strip it on save, and that would make the file
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
 * The direction the caret travels. For a line the region covers this is a row of
 * the diagram; `containsLine` is the check that says so, and the caller makes it
 * before sending a row.
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
 * The question the caret raises: a row of the diagram exists for the lines the
 * region covers, so this is what the caller asks before translating one. Both
 * ends inclusive, `endLine` being part of the region.
 *
 * @param {SourceRegion} region
 * @param {number} line zero-based, relative to the document
 * @returns {boolean}
 */
function containsLine(region, line) {
	return line >= region.startLine && line <= region.endLine;
}

/** What trackLine reports for a line an edit rewrote. */
const LINE_GONE = -1;

/**
 * Where `line` is after a document change, or LINE_GONE if it was rewritten.
 *
 * What keeps a diagram in a Markdown file findable while the prose around it is
 * written. The panel remembers a diagram by the line its fence is on, and typing
 * anywhere above moves that line; this is what follows it there, so the diagram
 * survives the next paragraph the author adds.
 *
 * Three kinds of change, of which one moves the line:
 *
 *   - entirely above it: the line moves by whatever the change added or
 *     removed. An insertion that *ends* at the start of the line counts as
 *     above, since it pushes the line down and leaves its text as it was --
 *     that is the newline you get from pressing Enter with the caret before a
 *     fence.
 *   - below it: the line stays. This is the ordinary case, every rewrite the
 *     diagram itself makes being inside the block.
 *   - containing it: the line's own text was replaced, so the fence this line
 *     was has gone, whatever ends up at that number. Reported as gone, since a
 *     line number carried over could land on a *different* diagram and have the
 *     panel show, and write into, the wrong one.
 *
 * Ranges are the document's before the change, and each is measured against the
 * line's own before-position, so the changes of one event may arrive in any
 * order.
 *
 * @param {number} line zero-based
 * @param {readonly {range: {start: {line: number}, end: {line: number,
 *   character: number}}, text: string}[]} changes one event's content changes,
 *   in vscode's shape, read for these three numbers and the text
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
