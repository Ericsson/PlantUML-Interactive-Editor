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

// Shared core for editor->diagram hover highlighting, used by both the activity
// and sequence diagram modules. It maps editor rows to the diagram elements they
// own and applies/undoes a per-element highlight style.
//
// Composition over inheritance: the row-map plus apply/restore machinery lives
// here, while each diagram supplies its own highlight styles and its own render
// walk that registers elements. The functions are pure over the state passed in
// (a `rowMap` Map and an `active` array), so each diagram keeps owning its own
// state rather than this module holding hidden globals.
//
// A "highlight style" is an object {apply(el) -> token, restore(el, token)}:
// apply() puts the element into its highlighted state and returns a token
// capturing what restore() needs to undo it, or null to decline (see below).

// Toggle a single attribute (e.g. fill, font-weight) to a fixed value. If the
// element already shows that value - a diagram-side hover is active, or it was
// registered twice for one row - apply declines (returns null) so the
// highlighted value is never captured and later restored as the "original".
function attributeHighlight(attr, value) {
    return {
        apply(el) {
            const old = el.getAttribute(attr);
            if (old === value) return null;
            el.setAttribute(attr, value);
            return {old: old};
        },
        restore(el, token) {
            if (token.old === null) {
                el.removeAttribute(attr);
            } else {
                el.setAttribute(attr, token.old);
            }
        }
    };
}

// Set one or more style *properties* (el.style.x) and restore by putting back
// the literal style *attribute* string. Mutating el.style re-serializes the
// attribute, which would drop exact substrings (e.g. "stroke-width:1.0") that
// the element classifiers match on, so the original attribute is restored
// verbatim rather than clearing individual style properties.
function stylePropertyHighlight(properties) {
    return {
        apply(el) {
            const old = el.getAttribute('style');
            for (const name in properties) {
                el.style[name] = properties[name];
            }
            return {old: old};
        },
        restore(el, token) {
            if (token.old) {
                el.setAttribute('style', token.old);
            } else {
                el.removeAttribute('style');
            }
        }
    };
}

// Register `el` to be highlighted with `style` when `row` is hovered in the
// editor. Negative rows (an unresolved backend line index) are ignored.
function registerHoverRow(rowMap, row, el, style) {
    if (row < 0) return;
    if (!rowMap.has(row)) {
        rowMap.set(row, []);
    }
    rowMap.get(row).push({el: el, style: style});
}

// Highlight every element registered on `row`, recording undo info onto the
// `active` array. A style that declines (apply returns null) is skipped, so
// `active` only ever holds entries with a real restore token.
function highlightHoverRow(rowMap, row, active) {
    const entries = rowMap.get(row);
    if (!entries) return;
    for (const entry of entries) {
        const token = entry.style.apply(entry.el);
        if (token === null) continue;
        active.push({el: entry.el, style: entry.style, token: token});
    }
}

// Undo every highlight recorded in `active`. Returns a fresh empty array for the
// caller to reassign to its state variable.
function clearHoverHighlight(active) {
    for (const entry of active) {
        entry.style.restore(entry.el, entry.token);
    }
    return [];
}

// Return the active-highlight entry for `el` (or null). Lets diagram-side hover
// handlers detect an editor-side highlight and read the element's pre-highlight
// value (entry.token.old) so they neither clobber it nor restore it wrongly.
function findActiveHighlight(active, el) {
    for (const entry of active) {
        if (entry.el === el) return entry;
    }
    return null;
}

// --- Diagram -> editor direction ---
// Inverse of the row map: which editor rows a diagram element owns. Built during
// the same registration pass so a diagram-side hover can mark the editor line(s)
// from cached data instead of a per-hover backend fetch.
function registerElementRows(elementRows, el, row) {
    if (row < 0) return;
    if (!elementRows.has(el)) elementRows.set(el, []);
    elementRows.get(el).push(row);
}

// Mark the editor line(s) for a hovered diagram element (no-op if it owns none).
function markEditorForElement(elementRows, el) {
    const rows = elementRows.get(el);
    if (rows && rows.length) setEditorMarkers(rows);
}

// --- Positions fetch ---

// POST the current puml + rendered SVG to a positions endpoint and return the
// parsed JSON, or null if there is no rendered diagram or the request fails.
// Hover highlighting is non-critical, so a failure simply disables it for that
// render (callers default their state to empty) instead of surfacing an error.
async function fetchDiagramData(endpoint) {
    const colb = document.getElementById('colb');
    const svg = colb ? colb.querySelector('g') : null;
    if (!svg) return null;
    try {
        const plantuml = trimlines(editor.session.getValue());
        const response = await fetch(endpoint, {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({plantuml: plantuml, svg: svg.innerHTML})
        });
        return await response.json();
    } catch (error) {
        return null;
    }
}

// --- Editor-side dispatch ---
// Routes an editor hover/cursor row to the active diagram's highlight, so the
// mousemove, mouseleave and cursor-change paths all funnel through one place.
// Relies on currentDiagramType and the per-diagram highlight/reset functions
// defined in script.js, activity.js and sequence-operations.js.

let lastEditorHoverRow = -1;

// Clear the editor-side highlight for whichever diagram type is active.
function resetEditorHighlight() {
    if (currentDiagramType === 'sequence') {
        resetSequenceHighlight();
    } else if (currentDiagramType === 'activity') {
        resetActivityHighlight();
    }
}

// Highlight the diagram element(s) owning the given editor row.
function highlightEditorRow(row) {
    if (currentDiagramType === 'sequence') {
        highlightSequenceForRow(row);
    } else if (currentDiagramType === 'activity') {
        highlightActivityForRow(row);
    }
}

// Wire the editor's hover and leave listeners (called once from initeditor).
// Hovering a line highlights the matching diagram element; leaving the editor
// clears it so it does not linger on the diagram (the sequence diagram-side
// hover preserves highlights and never resets). lastEditorHoverRow is reset on
// leave so re-entering on the same row re-highlights.
function initEditorHoverHighlighting(editor) {
    editor.on('mousemove', function(e) {
        if (currentDiagramType !== 'sequence' && currentDiagramType !== 'activity') return;
        const row = e.getDocumentPosition().row;
        if (row === lastEditorHoverRow) return;
        lastEditorHoverRow = row;
        resetEditorHighlight();
        highlightEditorRow(row);
    });
    editor.container.addEventListener('mouseleave', function() {
        lastEditorHoverRow = -1;
        resetEditorHighlight();
    });
}
