// Shared state
let currentContextMenuHandler = null;
let participantLifelines = [];
const LIFELINE_TOLERANCE = 15;

// Note/group positions fetched from backend (refreshed each render)
let notePositions = []; // [{cy, index}, ...]
let groupPositions = []; // [{headerIndex, endIndex}, ...]

// Elements highlighted from the editor side, with how to restore them
let sequenceHighlighted = []; // [{el, style, token}, ...] (see hover-highlight.js)

// Editor-row -> diagram elements to highlight, built once per render during the
// setup walk (mirrors the activity diagram's activityRowMap). Lets
// highlightSequenceForRow be a map lookup instead of re-walking the whole SVG
// and re-deriving each element's ordinal on every hover.
let sequenceRowMap = new Map(); // Map<row, [{el, style}, ...]> (see hover-highlight.js)

// Highlight treatment per sequence element type (see hover-highlight.js).
// Participants and notes recolor their fill; messages bold and thicken and group
// boxes/tabs thicken, both via style properties that restore the literal style
// attribute the element classifiers match on.
const SEQ_HIGHLIGHTS = {
    participant: attributeHighlight('fill', '#d8d8d8'),
    note: attributeHighlight('fill', '#d8d8d8'),
    message: stylePropertyHighlight({fontWeight: 'bold', strokeWidth: '2.0'}),
    group: stylePropertyHighlight({strokeWidth: '2.0'})
};

// Register a diagram element to highlight when the given editor row is hovered.
// kind picks the element's highlight treatment from SEQ_HIGHLIGHTS.
function registerSequenceRow(row, el, kind) {
    registerHoverRow(sequenceRowMap, row, el, SEQ_HIGHLIGHTS[kind]);
}

// --- Utilities ---

// Convert mouse event screen coordinates to SVG coordinate space
function svgPointFromEvent(e, svgElement) {
    let point = svgElement.createSVGPoint();
    point.x = e.clientX;
    point.y = e.clientY;
    return point.matrixTransform(svgElement.getScreenCTM().inverse());
}

// Fetch every element type's positions in one round-trip (called once per
// render). The backend bundles participant lifelines, messages, notes and
// groups into a single response so a render costs one request instead of four;
// each sub-table keeps its own shape (see getSequencePositions). A failed fetch
// leaves every table empty, disabling hover/gesture snapping for that render.
async function fetchSequencePositions() {
    const data = await fetchDiagramData("getSequencePositions");
    participantLifelines = data ? data.participants : [];
    messagePositions = data ? data.messages : [];
    notePositions = data ? data.notes : [];
    groupPositions = data ? data.groups : [];
}

// Vertical position of a message SVG element, comparable to messagePositions cy
function messageElementCy(svgelement) {
    const tag = svgelement.tagName.toLowerCase();
    if (tag === 'line') {
        return parseFloat(svgelement.getAttribute('y1'));
    }
    if (tag === 'text') {
        return parseFloat(svgelement.getAttribute('y'));
    }
    if (tag === 'polygon') {
        const points = (svgelement.getAttribute('points') || '').trim().split(/[\s,]+/);
        let sum = 0;
        let count = 0;
        for (let i = 1; i < points.length; i += 2) {
            sum += parseFloat(points[i]);
            count++;
        }
        return count > 0 ? sum / count : 0;
    }
    return 0;
}

// --- Editor -> diagram highlighting ---

// Restore the literal style attribute (used by the message diagram-side
// mouseout). Mutating el.style re-serializes the attribute and loses the exact
// "stroke-width:1.0" string that the element classifiers (e.g.
// checkIfMessageElement) match on, so unhighlighting must put back the original
// attribute rather than clear style properties.
function restoreStyleAttribute(el, old) {
    if (old) {
        el.setAttribute('style', old);
    } else {
        el.removeAttribute('style');
    }
}

function resetSequenceHighlight() {
    sequenceHighlighted = clearHoverHighlight(sequenceHighlighted);
}

// Highlight the diagram element(s) registered for the given editor row.
// The element->row mapping is precomputed in sequenceRowMap during the render
// walk, so this is a shared map lookup; resetSequenceHighlight undoes it.
function highlightSequenceForRow(row) {
    if (isSequenceAddMode()) return;
    highlightHoverRow(sequenceRowMap, row, sequenceHighlighted);
}

// --- Background context menu management ---

function removeBackgroundMenuListener() {
    const background = document.getElementById('colb-container');
    if (currentContextMenuHandler) {
        background.removeEventListener('contextmenu', currentContextMenuHandler);
        currentContextMenuHandler = null;
    }
}

function handleContextMenuBackground(svgElement) {
    const background = document.getElementById('colb-container');
    removeBackgroundMenuListener();
    currentContextMenuHandler = (e) => backgroundContextMenu(e, svgElement);
    background.addEventListener('contextmenu', currentContextMenuHandler);
}

// --- Participant operation event listeners (rename, add, delete) ---

function participantEventListeners() {
    // Submit renamed participant name
    $('#submit-participant-name').on('click', async () => {
        const element = document.getElementById('colb');
        const svg = element.querySelector('g');

        var newname = $('#participant-name-text').val()
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("editParticipantName", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'name': newname,
                    'svgelement': lastclickedsvgelement.outerHTML
                }),
            });
            const data = await response.json();
            setPuml(data.plantuml);
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    // "Rename" context menu item: fetch current name and show rename modal
    document.getElementById('renameParticipant').addEventListener('click', async () => {
        const element = document.getElementById('colb');
        const svg = element.querySelector('g');
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("getParticipantName", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });
            const name = (await response.json()).name;
            $('#participant-name-modalForm .modal-title').text('Rename ' + name);
            $('#participant-name-text').val(name);
            $('#participant-name-modalForm').modal('show');
            $('#participant-name-modalForm').on('shown.bs.modal', function() {
                $('#participant-name-text').trigger('focus');
            });
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    // Add/Delete participant operations (data-driven to avoid repetition)
    const sequenceList = [{
        id: 'addParticipantLeft',
        endpoint: 'addParticipant',
        arguments: {direction: 'left'}
    }, {
        id: 'addParticipantRight',
        endpoint: 'addParticipant',
        arguments: {direction: 'right'}
    }, {
        id: 'deleteParticipant',
        endpoint: 'deleteParticipant',
        arguments: {}
    }];

    sequenceList.forEach(item => {
        document.getElementById(item.id).addEventListener('click', async () => {
            const element = document.getElementById('colb');
            const svg = element.querySelector('g');
            try {
                const plantuml = trimlines(editor.session.getValue());
                const toBeStringified = {
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML,
                }
                if (item.arguments) {
                    for (let [key, value] of Object.entries(item.arguments)) {
                        toBeStringified[key] = value;
                    }
                }
                const response = await fetch(item.endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(toBeStringified)
                });
                const data = await response.json();
                setPuml(data.plantuml);
            } catch (error) {
                displayErrorMessage(`Error with fetch API: ${error.message}`, error);
            }
        });
    });
}

// --- Participant rect handlers (dblclick, hover, contextmenu) ---

function setupParticipantHandlers(svgelements, svg, element) {
    for (let index = 0; index < svgelements.length; index++) {
        let svgelement = svgelements[index];
        // Disable pointer events only on participant text (font-size 14) so clicks
        // pass through to the rect beneath. Message text (font-size 13) stays clickable.
        if (svgelement.tagName.toLowerCase() === 'text' &&
            svgelement.getAttribute('font-size') === '14') {
            svgelement.style.pointerEvents = 'none';
        }

        if (!checkIfParticipant(svgelements, index)) continue;

        // Register this rect for editor->diagram highlighting on its lifeline's row.
        const participantCx = parseFloat(svgelement.getAttribute('x')) + parseFloat(svgelement.getAttribute('width')) / 2;
        const participantLifeline = participantLifelines.find(p => Math.abs(p.cx - participantCx) <= 1);
        if (participantLifeline) registerSequenceRow(participantLifeline.index, svgelement, 'participant');

        svgelement.addEventListener('dblclick', async () => {
            lastclickedsvgelement = svgelement;
            try {
                const plantuml = trimlines(editor.session.getValue());
                const response = await fetch("getParticipantName", {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify({
                        'plantuml': plantuml,
                        'svg': svg.innerHTML,
                        'svgelement': svgelement.outerHTML
                    })
                });
                $('#participant-name-text').val((await response.json()).name);
                $('#participant-name-modalForm').modal('show');
                $('#participant-name-modalForm').on('shown.bs.modal', function() {
                    $('#participant-name-text').trigger('focus');
                });
            } catch (error) {
                displayErrorMessage(`Error with fetch API: ${error.message}`, error);
            }
        });

        let rectcolor = "";
        svgelement.addEventListener('mouseover', function() {
            // If already highlighted from the editor side, keep the original fill
            const highlighted = findActiveHighlight(sequenceHighlighted, svgelement);
            rectcolor = highlighted ? highlighted.token.old : svgelement.getAttribute('fill');
            svgelement.setAttribute('fill', '#d8d8d8');
            const cx = parseFloat(svgelement.getAttribute('x')) + parseFloat(svgelement.getAttribute('width')) / 2;
            const lifeline = participantLifelines.find(p => Math.abs(p.cx - cx) <= 1);
            if (lifeline && lifeline.index >= 0) setEditorMarkers(lifeline.index);
        });

        svgelement.addEventListener('mouseout', function() {
            clearMarkers();
            if (findActiveHighlight(sequenceHighlighted, svgelement)) return;
            svgelement.setAttribute('fill', rectcolor);
        });

        svgelement.addEventListener('contextmenu', function(e) {
            lastclickedsvgelement = svgelement;
            e.preventDefault();
            e.stopPropagation();
            var contextMenu = document.getElementById('participant-menu');
            contextMenu.style.display = 'block';
            contextMenu.style.left = e.pageX + 'px';
            contextMenu.style.top = e.pageY + 'px';
        });
    }
}

// --- Entry point and orchestration ---

// Called once when a sequence diagram is detected
function sequenceEventListeners() {
    participantEventListeners();
    messageEventListeners();
    messageOperationEventListeners();
    noteOperationEventListeners();
    activationEventListeners();
    groupOperationEventListeners();
}

// Called on every render when diagram type is sequence
async function setHandlersForSequenceDiagram(pumlcontent, element) {
    fetchSvgFromPlantUml().then(async (svgContent) => {
        element.innerHTML = svgContent;
        sequenceHighlighted = []; // old SVG is gone; drop stale references
        sequenceRowMap = new Map(); // rebuilt below by the setup*Handlers walk
        const svgContainer = element.querySelector('svg');
        const svg = element.querySelector('g');
        if (!svg) {
            toggleLoadingOverlay();
            return;
        }

        await fetchSequencePositions();
        cancelMessageAddMode();
        cancelActivationAddMode();
        cancelGroupAddMode();
        cancelNoteAddMode();

        handleContextMenuBackground(svgContainer);
        setupLifelineInteraction();
        setupParticipantHandlers(svg.querySelectorAll('*'), svg, element);
        setupMessageHandlers(svg.querySelectorAll('*'), svg);
        setupNoteHandlers(svg.querySelectorAll('*'));
        setupGroupHandlers(svg.querySelectorAll('*'));

        toggleLoadingOverlay();
    }).catch((error) => {
        displayErrorMessage(`Error rendering SVG: ${error.message}`, error);
    });
}

// Identifies participant header rects by their PlantUML-specific style.
// rx/ry (rounded corners) are required to exclude rnote, which shares the
// same stroke-width:0.5 style but is never rounded.
function checkIfParticipant(svgelements, index) {
    const el = svgelements[index];
    return (el.tagName.toLowerCase() === 'rect') &&
        (el.getAttribute('style') == "stroke:#181818;stroke-width:0.5;") &&
        el.hasAttribute('rx') && el.hasAttribute('ry');
}

// Identifies message elements (polygons and lines with stroke-width:1.0, and message text)
function checkIfMessageElement(svgelement) {
    const tag = svgelement.tagName.toLowerCase();
    const style = svgelement.getAttribute('style') || '';
    if ((tag === 'polygon' || tag === 'line') && style.includes('stroke-width:1.0')) {
        return true;
    }
    if (tag === 'text' && svgelement.getAttribute('font-size') === '13') {
        // Exclude bold text: it's a group keyword/label, not a message
        if (svgelement.getAttribute('font-weight') === 'bold') {
            return false;
        }
        // Exclude note text (preceded by a note/hnote/rnote shape, or by
        // the fold-corner path for "note" specifically)
        let prev = svgelement.previousElementSibling;
        if (prev && (prev.tagName.toLowerCase() === 'path' ||
                     prev.tagName.toLowerCase() === 'polygon' ||
                     prev.tagName.toLowerCase() === 'rect') &&
            isNoteCandidate(prev)) {
            return false;
        }
        return true;
    }
    return false;
}

// Identifies group block boxes by their PlantUML-specific fill
function checkIfGroupBox(svgelement) {
    return (svgelement.tagName.toLowerCase() === 'rect') &&
        (svgelement.getAttribute('fill') === 'none');
}

// Identifies the group's keyword/label text (e.g. "alt", "loop", "[Label]")
function checkIfGroupHeaderText(svgelement) {
    return (svgelement.tagName.toLowerCase() === 'text') &&
        (svgelement.getAttribute('font-weight') === 'bold') &&
        (svgelement.getAttribute('font-size') === '13' || svgelement.getAttribute('font-size') === '11');
}

// Opens the group context menu, identifying the group by its box rect
// (the backend matches groups by the box's x/y, regardless of which part
// of the header - tab or label text - was actually right-clicked).
function openGroupContextMenu(groupRect, e) {
    lastclickedsvgelement = groupRect;
    e.preventDefault();
    e.stopPropagation();
    var contextMenu = document.getElementById('seq-group-menu');
    contextMenu.style.display = 'block';
    contextMenu.style.left = e.pageX + 'px';
    contextMenu.style.top = e.pageY + 'px';
}

// --- Group header handlers (contextmenu on the keyword tab and its label text only) ---

function setupGroupHandlers(svgelements) {
    // The keyword tab (path) precedes its box (rect), which precedes its
    // header text (keyword, then an optional bracketed label) in the SVG.
    let pendingTabPath = null;
    let currentGroupRect = null;
    let headerTextsRemaining = 0;
    // Group boxes appear in document order matching puml source order
    let groupOrdinal = -1;

    function addGroupHoverMarkers(el, ordinal) {
        el.addEventListener('mouseover', function() {
            if (isSequenceAddMode()) return;
            const group = groupPositions[ordinal];
            if (group && group.headerIndex >= 0) {
                getmarker([group.headerIndex, group.endIndex >= 0 ? group.endIndex : group.headerIndex]);
            }
        });
        el.addEventListener('mouseout', function() {
            clearMarkers();
        });
    }

    for (let index = 0; index < svgelements.length; index++) {
        let svgelement = svgelements[index];
        const tag = svgelement.tagName.toLowerCase();

        if (tag === 'path' && svgelement.getAttribute('fill') === '#EEEEEE') {
            pendingTabPath = svgelement;
            continue;
        }

        if (checkIfGroupBox(svgelement)) {
            // Only a real box - one immediately following its #EEEEEE tab path -
            // advances the ordinal. PlantUML also emits an invisible layout rect
            // with fill="none" but no preceding tab; it must not shift the
            // ordinal, or lookups into groupPositions (built by the backend's
            // _count_group_boxes, which applies this same tab-pairing rule)
            // misalign.
            if (pendingTabPath) {
                groupOrdinal++;
                currentGroupRect = svgelement;
                let tabPath = pendingTabPath;
                let groupRectForTab = currentGroupRect;
                tabPath.addEventListener('contextmenu', (e) => openGroupContextMenu(groupRectForTab, e));
                addGroupHoverMarkers(tabPath, groupOrdinal);
                // Register the box and its tab for editor->diagram highlighting
                // under both the group's header and end lines (mirrors the
                // backend group's headerIndex/endIndex; registerSequenceRow drops
                // any -1 line).
                const group = groupPositions[groupOrdinal];
                if (group) {
                    registerSequenceRow(group.headerIndex, currentGroupRect, 'group');
                    registerSequenceRow(group.headerIndex, tabPath, 'group');
                    registerSequenceRow(group.endIndex, currentGroupRect, 'group');
                    registerSequenceRow(group.endIndex, tabPath, 'group');
                }
                pendingTabPath = null;
                headerTextsRemaining = 2; // keyword text + optional bracketed label
            }
            continue;
        }

        if (checkIfGroupHeaderText(svgelement)) {
            if (headerTextsRemaining > 0 && currentGroupRect) {
                let groupRect = currentGroupRect;
                svgelement.addEventListener('contextmenu', (e) => openGroupContextMenu(groupRect, e));
                addGroupHoverMarkers(svgelement, groupOrdinal);
                headerTextsRemaining--;
            }
            continue;
        }

        // Any other element ends this group's clickable header window
        headerTextsRemaining = 0;
    }
}

// --- Message element handlers (hover, contextmenu) ---

function setupMessageHandlers(svgelements, svg) {
    for (let index = 0; index < svgelements.length; index++) {
        let svgelement = svgelements[index];
        if (!checkIfMessageElement(svgelement)) continue;

        // Register this element for editor->diagram highlighting on its message's
        // row, assigning it to the nearest message (same rule the mouseover uses).
        const nearestMessage = findNearestMessage(messageElementCy(svgelement));
        if (nearestMessage) registerSequenceRow(nearestMessage.index, svgelement, 'message');

        let originalstyle; // undefined while no hover is in progress
        svgelement.addEventListener('mouseover', function() {
            if (isSequenceAddMode()) return;
            // If already highlighted from the editor side, keep the original style
            const highlighted = findActiveHighlight(sequenceHighlighted, svgelement);
            originalstyle = highlighted ? highlighted.token.old : svgelement.getAttribute('style');
            svgelement.style.fontWeight = 'bold';
            svgelement.style.strokeWidth = '2.0';
            const nearest = findNearestMessage(messageElementCy(svgelement));
            if (nearest) setEditorMarkers(nearest.index);
        });

        svgelement.addEventListener('mouseout', function() {
            clearMarkers();
            if (originalstyle === undefined) return;
            // Keep styles if the element is highlighted from the editor side
            if (findActiveHighlight(sequenceHighlighted, svgelement)) return;
            restoreStyleAttribute(svgelement, originalstyle);
            originalstyle = undefined;
        });

        svgelement.addEventListener('contextmenu', function(e) {
            e.preventDefault();
            e.stopPropagation();
            if (isSequenceAddMode()) return;

            lastclickedsvgelement = svgelement;
            var contextMenu = document.getElementById('message-menu');
            contextMenu.style.display = 'block';
            contextMenu.style.left = e.pageX + 'px';
            contextMenu.style.top = e.pageY + 'px';
        });
    }
}

// --- Message operation event listeners (edit, delete) ---

let messageEditMode = false;

function messageOperationEventListeners() {
    // "Edit Message" context menu item
    document.getElementById('editMessage').addEventListener('click', async () => {
        const element = document.getElementById('colb');
        const svg = element.querySelector('g');
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("getMessageText", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });
            const text = (await response.json()).text;
            messageEditMode = true;
            $('#participant-modalForm .modal-title').text('Edit Message');
            $('#participant-message-text').val(text);
            $('#participant-modalForm').modal('show');
            $('#participant-modalForm').on('shown.bs.modal', function() {
                $('#participant-message-text').trigger('focus');
            });
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    // "Delete Message" context menu item
    document.getElementById('deleteMessage').addEventListener('click', async () => {
        const element = document.getElementById('colb');
        const svg = element.querySelector('g');
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("deleteMessage", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });
            const data = await response.json();
            setPuml(data.plantuml);
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });
}

// --- Note element handlers ---

// Classifies a single SVG shape as a note type ("note"/"hnote"/"rnote"),
// or null, by tag + shape structure only - never fill color - mirroring
// classify_note_shape() in sequence/util.py. For "note", the element must
// be the first of the two-path pair (the folded rectangle body); the
// caller skips the second (fold corner) path.
function classifyNoteShape(svgelement) {
    const tag = svgelement.tagName.toLowerCase();

    if (tag === 'rect') {
        return 'rnote';
    }
    if (tag === 'polygon') {
        const points = (svgelement.getAttribute('points') || '').trim();
        if (!points) return null;
        const pointCount = points.split(',').filter(p => p.trim() !== '').length / 2;
        return pointCount === 7 ? 'hnote' : null;
    }
    if (tag === 'path') {
        const d = svgelement.getAttribute('d') || '';
        const pointCount = (d.match(/L/g) || []).length + 1;
        return pointCount === 6 ? 'note' : null;
    }
    return null;
}

// Excludes shapes that would otherwise collide with a note's tag/shape
// signature, mirroring _is_note_candidate() in sequence/util.py:
// participant header rects (rx/ry, which notes never have), and
// activation bars / group borders/tabs (different stroke-width - notes
// always use 0.5, regardless of fill color).
function isNoteCandidate(svgelement) {
    const style = svgelement.getAttribute('style') || '';
    if (!style.includes('stroke-width:0.5')) return false;
    if (svgelement.hasAttribute('rx') || svgelement.hasAttribute('ry')) return false;
    return true;
}

function setupNoteHandlers(svgelements) {
    let noteOrdinal = -1;

    // Attaches the shared context-menu/hover/highlight behavior to one
    // shape belonging to note number thisNoteOrdinal. Called once for
    // "hnote"/"rnote" (single shape), and twice for "note" (body path +
    // fold corner path both map to the same note, matching how PlantUML
    // renders it as two elements).
    function attachNoteShapeHandlers(svgelement, thisNoteOrdinal) {
        const noteInfo = notePositions[thisNoteOrdinal];
        if (noteInfo) registerSequenceRow(noteInfo.index, svgelement, 'note');

        svgelement.addEventListener('contextmenu', function(e) {
            lastclickedsvgelement = svgelement;
            e.preventDefault();
            e.stopPropagation();
            var contextMenu = document.getElementById('seq-note-menu');
            contextMenu.style.display = 'block';
            contextMenu.style.left = e.pageX + 'px';
            contextMenu.style.top = e.pageY + 'px';
        });

        let notecolor = "";
        svgelement.addEventListener('mouseover', function() {
            if (isSequenceAddMode()) return;
            const highlighted = findActiveHighlight(sequenceHighlighted, svgelement);
            notecolor = highlighted ? highlighted.token.old : svgelement.getAttribute('fill');
            svgelement.setAttribute('fill', '#d8d8d8');
            const note = notePositions[thisNoteOrdinal];
            if (note && note.index >= 0) setEditorMarkers(note.index);
        });

        svgelement.addEventListener('mouseout', function() {
            clearMarkers();
            if (findActiveHighlight(sequenceHighlighted, svgelement)) return;
            svgelement.setAttribute('fill', notecolor);
        });
    }

    for (let index = 0; index < svgelements.length; index++) {
        let svgelement = svgelements[index];
        const tag = svgelement.tagName.toLowerCase();

        if ((tag === 'path' || tag === 'polygon' || tag === 'rect') && isNoteCandidate(svgelement)) {
            const noteType = classifyNoteShape(svgelement);
            if (noteType === null) continue;

            noteOrdinal++;
            attachNoteShapeHandlers(svgelement, noteOrdinal);

            // "note" renders as two elements (body path + fold corner
            // path); both must recolor/highlight together, matching how
            // a single note is one visual unit. The fold corner itself
            // is not independently classifiable (4 points), so it is
            // attached here explicitly rather than via the main loop.
            if (noteType === 'note') {
                const next = svgelements[index + 1];
                if (next && next.tagName.toLowerCase() === 'path' && isNoteCandidate(next)) {
                    attachNoteShapeHandlers(next, noteOrdinal);
                    index++;
                }
            }
        }

        // Note text should not be hoverable. previousElementSibling is
        // the note's fold-corner path for "note" (which is note-styled
        // but not independently classifiable as a full note shape - a
        // path with 4 points), or the single shape itself for "hnote"/
        // "rnote". isNoteCandidate alone (tag + stroke-width:0.5, no
        // rx/ry) correctly matches both cases.
        if (tag === 'text' && svgelement.getAttribute('font-size') === '13') {
            let prev = svgelement.previousElementSibling;
            if (prev && (prev.tagName.toLowerCase() === 'path' ||
                         prev.tagName.toLowerCase() === 'polygon' ||
                         prev.tagName.toLowerCase() === 'rect') &&
                isNoteCandidate(prev)) {
                svgelement.style.pointerEvents = 'none';
            }
        }
    }
}

// --- Note operation event listeners ---

let notePlacement = '';
let selectedNoteType = 'note';
let noteEditMode = false;
let isAddNoteActive = false;

function isNoteAddMode() {
    return isAddNoteActive;
}

function cancelNoteAddMode() {
    isAddNoteActive = false;
    selectedNoteType = 'note';
}

// Reads the checked radio in the note modal's type selector. This is the
// single source of truth for the type sent on submit, for both add and
// edit modes.
function getModalNoteType() {
    var checked = document.querySelector('input[name="seq-note-type-radio"]:checked');
    return checked ? checked.value : 'note';
}

// Preselects the modal's type radio to match a given type, defaulting to
// "note" for an unrecognized value.
function setModalNoteType(noteType) {
    var radio = document.getElementById('seq-note-type-' + noteType);
    if (!radio) {
        radio = document.getElementById('seq-note-type-note');
    }
    radio.checked = true;
}

function noteOperationEventListeners() {
    // "Add Note" in sequence-menu shows the note type submenu
    document.getElementById('seq-addNote').addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        var seqMenu = document.getElementById('sequence-menu');
        var typeMenu = document.getElementById('seq-note-type-menu');
        typeMenu.style.display = 'block';
        typeMenu.style.left = seqMenu.style.left;
        typeMenu.style.top = seqMenu.style.top;
        seqMenu.style.display = 'none';
    });

    // Note type submenu items show the placement menu
    document.getElementById('seq-note-type-menu').addEventListener('click', function(e) {
        var item = e.target.closest('[data-note-type]');
        if (!item) return;
        e.preventDefault();
        // Stop the click from bubbling to document, where Bootstrap's
        // dropdown auto-close listener would otherwise immediately hide
        // the placement menu we are about to show (it treats any
        // document click as "close open dropdown-menus", including this
        // one, since our menus aren't managed by Bootstrap's JS).
        e.stopPropagation();
        selectedNoteType = item.getAttribute('data-note-type');
        var typeMenu = document.getElementById('seq-note-type-menu');
        var placementMenu = document.getElementById('seq-note-placement-menu');
        placementMenu.style.display = 'block';
        placementMenu.style.left = typeMenu.style.left;
        placementMenu.style.top = typeMenu.style.top;
        typeMenu.style.display = 'none';
        isAddNoteActive = true;
    });

    // Placement menu items
    document.getElementById('seq-note-placement-menu').addEventListener('click', function(e) {
        var item = e.target.closest('[data-placement]');
        if (!item) return;
        e.preventDefault();
        notePlacement = item.getAttribute('data-placement');
        document.getElementById('seq-note-placement-menu').style.display = 'none';

        // Show/hide second participant dropdown
        var group = document.getElementById('seq-note-second-participant-group');
        if (notePlacement === 'spanning') {
            var select = document.getElementById('seq-note-second-participant');
            select.innerHTML = '';
            participantLifelines.forEach(function(p) {
                if (p.name !== messageOrigin.name) {
                    var opt = document.createElement('option');
                    opt.value = p.name;
                    opt.textContent = p.name;
                    select.appendChild(opt);
                }
            });
            group.style.display = 'block';
        } else {
            group.style.display = 'none';
        }

        noteEditMode = false;
        isAddNoteActive = true;
        document.querySelector('#seq-note-modalForm .modal-title').textContent = 'Add Note';
        document.getElementById('seq-note-text').value = '';
        document.getElementById('seq-note-type-group').style.display = 'none';
        setModalNoteType(selectedNoteType);
        $('#seq-note-modalForm').modal('show');
    });

    // Submit note - uses global submitNote() called via onclick in HTML
    // (see submitNote function below)

    // Edit Note
    document.getElementById('seq-editNote').addEventListener('click', async function() {
        var element = document.getElementById('colb');
        var svg = element.querySelector('g');
        try {
            var plantuml = trimlines(editor.session.getValue());
            var response = await fetch("getSeqNoteText", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    plantuml: plantuml,
                    svg: svg.innerHTML,
                    svgelement: lastclickedsvgelement.outerHTML
                })
            });
            var responseData = await response.json();
            noteEditMode = true;
            isAddNoteActive = false;
            document.querySelector('#seq-note-modalForm .modal-title').textContent = 'Edit Note';
            document.getElementById('seq-note-text').value = responseData.text;
            document.getElementById('seq-note-second-participant-group').style.display = 'none';
            document.getElementById('seq-note-type-group').style.display = 'block';
            setModalNoteType(responseData.noteType);
            $('#seq-note-modalForm').modal('show');
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    // Delete Note
    document.getElementById('seq-deleteNote').addEventListener('click', async function() {
        var element = document.getElementById('colb');
        var svg = element.querySelector('g');
        try {
            var plantuml = trimlines(editor.session.getValue());
            var response = await fetch("deleteSeqNote", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    plantuml: plantuml,
                    svg: svg.innerHTML,
                    svgelement: lastclickedsvgelement.outerHTML
                })
            });
            var data = await response.json();
            setPuml(data.plantuml);
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    $('#seq-note-modalForm').on('hidden.bs.modal', function() {
        if (!noteEditMode) {
            cancelNoteAddMode();
        }
    });
}

// --- Group operation event listeners ---

let groupEditMode = false;

function groupOperationEventListeners() {
    // "Rename" context menu item: fetch current label and show the group modal
    document.getElementById('seq-renameGroup').addEventListener('click', async function() {
        var element = document.getElementById('colb');
        var svg = element.querySelector('g');
        try {
            var plantuml = trimlines(editor.session.getValue());
            var response = await fetch("getSeqGroupLabel", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    plantuml: plantuml,
                    svg: svg.innerHTML,
                    svgelement: lastclickedsvgelement.outerHTML
                })
            });
            var data = await response.json();
            groupEditMode = true;
            document.querySelector('#seq-group-modalForm .modal-title').textContent = 'Rename ' + data.type;
            document.getElementById('seq-group-label-text').value = data.label;
            $('#seq-group-modalForm').modal('show');
            $('#seq-group-modalForm').on('shown.bs.modal', function() {
                $('#seq-group-label-text').trigger('focus');
            });
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    // "Delete Group" context menu item
    document.getElementById('seq-deleteGroup').addEventListener('click', async function() {
        var element = document.getElementById('colb');
        var svg = element.querySelector('g');
        try {
            var plantuml = trimlines(editor.session.getValue());
            var response = await fetch("deleteSeqGroup", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    plantuml: plantuml,
                    svg: svg.innerHTML,
                    svgelement: lastclickedsvgelement.outerHTML
                })
            });
            var data = await response.json();
            setPuml(data.plantuml);
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    // "Add Group" in sequence-menu shows the type submenu
    document.getElementById('seq-addGroup').addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        var seqMenu = document.getElementById('sequence-menu');
        var typeMenu = document.getElementById('seq-group-type-menu');
        typeMenu.style.display = 'block';
        typeMenu.style.left = seqMenu.style.left;
        typeMenu.style.top = seqMenu.style.top;
        seqMenu.style.display = 'none';
    });

    // Type submenu items enter group-add mode
    document.getElementById('seq-group-type-menu').addEventListener('click', function(e) {
        var item = e.target.closest('[data-group-type]');
        if (!item) return;
        e.preventDefault();
        document.getElementById('seq-group-type-menu').style.display = 'none';

        startGroupAddModeFromContext(item.getAttribute('data-group-type'));
    });

    // Escape cancels group-add mode
    document.addEventListener('keydown', function(e) {
        if (e.key === 'Escape' && isAddGroupActive) {
            cancelGroupAddMode();
        }
    });

}

// Global function called by onclick on the submit-note button
async function submitNote() {
    var text = document.getElementById('seq-note-text').value;
    if (!text) return;

    var noteType = getModalNoteType();
    var element = document.getElementById('colb');
    var svg = element.querySelector('g');

    try {
        var plantuml = trimlines(editor.session.getValue());
        var response;
        if (noteEditMode) {
            noteEditMode = false;
            response = await fetch("editSeqNote", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    plantuml: plantuml,
                    svg: svg.innerHTML,
                    svgelement: lastclickedsvgelement.outerHTML,
                    text: text,
                    noteType: noteType
                })
            });
        } else {
            var body = {
                plantuml: plantuml,
                svg: svg.innerHTML,
                participant: messageOrigin.name,
                placement: notePlacement,
                text: text,
                yPosition: firstClickCoordinates[1],
                xPosition: firstClickCoordinates[0],
                noteType: noteType
            };
            if (notePlacement === 'spanning') {
                body.secondParticipant = document.getElementById('seq-note-second-participant').value;
            }
            response = await fetch("addNote", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            });
        }
        var data = await response.json();
        $('#seq-note-modalForm').modal('hide');
        cancelNoteAddMode();
        setPuml(data.plantuml);
    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }
}
