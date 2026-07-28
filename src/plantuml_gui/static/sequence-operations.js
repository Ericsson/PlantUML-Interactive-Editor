// Shared state
let currentContextMenuHandler = null;
let participantLifelines = [];
const LIFELINE_TOLERANCE = 15;

// Note/group positions fetched from backend (refreshed each render)
let notePositions = []; // [{cy, index}, ...]
let groupPositions = []; // [{headerIndex, endIndex}, ...]
let boxPositions = []; // [{headerIndex, endIndex}, ...]

// Elements highlighted from the editor side, with how to restore them
let sequenceHighlighted = []; // [{el, style, token}, ...] (see hover-highlight.js)

// Elements highlighted by a diagram-side message hover, kept separate from the
// editor-side state so a diagram hover-out only undoes what the hover applied
// and never clears an editor-owned highlight (see setupMessageHandlers).
let sequenceDiagramHover = []; // [{el, style, token}, ...] (see hover-highlight.js)

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
    group: stylePropertyHighlight({strokeWidth: '2.0'}),
    box: stylePropertyHighlight({strokeWidth: '2.0'})
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
// yields every table empty, disabling hover/gesture snapping for that render.
//
// Returns the tables rather than assigning the shared globals directly: the
// caller assigns them only after re-checking the render generation, so a stale
// render whose fetch resolves late can't overwrite the current diagram's
// positions (see setHandlersForSequenceDiagram).
async function fetchSequencePositions() {
    const data = await fetchDiagramData("getSequencePositions");
    return {
        participants: data ? data.participants : [],
        messages: data ? data.messages : [],
        notes: data ? data.notes : [],
        groups: data ? data.groups : [],
        boxes: data ? data.boxes : [],
    };
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
        // pass through to the rect beneath. Message text (font-size 13) stays
        // clickable, and title text (font-size 14 but bold) stays clickable so it
        // remains double-click editable (see setupTitleHandler).
        if (svgelement.tagName.toLowerCase() === 'text' &&
            svgelement.getAttribute('font-size') === '14' &&
            !isTitleText(svgelement)) {
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
    boxEventListeners();
}

// Called on every render when diagram type is sequence
async function setHandlersForSequenceDiagram(pumlcontent, element, renderId) {
    fetchSvgFromPlantUml().then(async (svgContent) => {
        // A newer render started while this SVG was being fetched (e.g. the
        // user switched diagrams); drop this result so it can't clobber the
        // current diagram. Balance the loading overlay toggle that
        // renderPlantUml did for this render before bailing.
        if (renderId !== renderGeneration) {
            hideLoadingOverlay();
            return;
        }
        element.innerHTML = svgContent;
        sequenceHighlighted = []; // old SVG is gone; drop stale references
        sequenceDiagramHover = []; // old SVG is gone; drop stale references
        sequenceRowMap = new Map(); // rebuilt below by the setup*Handlers walk
        const svgContainer = element.querySelector('svg');
        const svg = element.querySelector('g');
        if (!svg) {
            hideLoadingOverlay();
            return;
        }

        const positions = await fetchSequencePositions();
        // fetchSequencePositions is a second async hop: a newer render can
        // complete during it, replacing #colb's SVG and the shared position
        // state. Re-check before we publish these positions and bind handlers,
        // so a stale render can't clobber the current diagram's positions or
        // stack a duplicate set of handlers onto the newer SVG.
        if (renderId !== renderGeneration) {
            hideLoadingOverlay();
            return;
        }
        participantLifelines = positions.participants;
        messagePositions = positions.messages;
        notePositions = positions.notes;
        groupPositions = positions.groups;
        boxPositions = positions.boxes;

        cancelMessageAddMode();
        cancelActivationAddMode();
        cancelGroupAddMode();
        cancelBoxAddMode();
        cancelNoteAddMode();

        handleContextMenuBackground(svgContainer);
        setupLifelineInteraction();
        setupTitleHandler(svg.querySelectorAll('*'), svg, pumlcontent);
        setupParticipantHandlers(svg.querySelectorAll('*'), svg, element);
        setupMessageHandlers(svg.querySelectorAll('*'), svg);
        setupNoteHandlers(svg.querySelectorAll('*'));
        setupGroupHandlers(svg.querySelectorAll('*'));
        setupBoxHandlers(svg.querySelectorAll('*'));

        hideLoadingOverlay();
    }).catch((error) => {
        // Balance the showLoadingOverlay() from renderPlantUml on the error
        // path too; otherwise the ref count leaks and wedges the overlay
        // visible. Mutually exclusive with the success hide above.
        hideLoadingOverlay();
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
        // Exclude note text. Each note line is a separate <text> element;
        // only the first line's previous sibling is the note shape, so
        // isNoteText walks back over earlier lines to find the anchor.
        if (isNoteText(svgelement)) {
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

        svgelement.addEventListener('mouseover', function() {
            if (isSequenceAddMode()) return;
            // Highlight the WHOLE message, not just the hovered shape, so it
            // reads as one entity. Every element of a message was registered in
            // sequenceRowMap under the same message index during setup (the same
            // grouping the editor-side hover uses), so bold/thicken all of them.
            const nearest = findNearestMessage(messageElementCy(svgelement));
            if (!nearest) return;
            const entries = sequenceRowMap.get(nearest.index) || [];
            for (const entry of entries) {
                // Leave editor-owned highlights alone (they restore the true
                // original on their own) and skip anything this hover already
                // applied, so tokens capture the real pre-hover style.
                if (findActiveHighlight(sequenceHighlighted, entry.el)) continue;
                if (findActiveHighlight(sequenceDiagramHover, entry.el)) continue;
                const token = entry.style.apply(entry.el);
                if (token === null) continue;
                sequenceDiagramHover.push({el: entry.el, style: entry.style, token: token});
            }
            setEditorMarkers(nearest.index);
        });

        svgelement.addEventListener('mouseout', function() {
            clearMarkers();
            // Undo only what this diagram-side hover applied; editor-owned
            // highlights were skipped above and stay untouched.
            sequenceDiagramHover = clearHoverHighlight(sequenceDiagramHover);
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
            const data = await response.json();
            messageEditMode = true;
            $('#participant-modalForm .modal-title').text('Edit Message');
            $('#participant-message-text').val(data.text);
            document.getElementById('participant-message-color-group').style.display = 'block';
            setColorSelect(document.getElementById('participant-message-color-select'), data.color);
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

// Determines whether a font-size-13 <text> element is a line of a note's
// body. PlantUML renders each note line as a separate <text> element in
// sequence after the note's shape (path/polygon/rect). Only the first
// line's previous sibling is the note shape; each later line follows the
// preceding line's text, so a single previousElementSibling check misses
// lines 2+. Walk back over the earlier (non-bold, font-size-13) note-line
// texts to find the shape that anchors them. A message label's text is
// always preceded by its arrow line/polygon (never a note candidate), so
// this never misclassifies message text as note text.
function isNoteText(svgelement) {
    if (svgelement.tagName.toLowerCase() !== 'text') return false;
    if (svgelement.getAttribute('font-size') !== '13') return false;
    let prev = svgelement.previousElementSibling;
    while (prev && prev.tagName.toLowerCase() === 'text' &&
           prev.getAttribute('font-size') === '13' &&
           prev.getAttribute('font-weight') !== 'bold') {
        prev = prev.previousElementSibling;
    }
    if (!prev) return false;
    const prevTag = prev.tagName.toLowerCase();
    return (prevTag === 'path' || prevTag === 'polygon' || prevTag === 'rect') &&
        isNoteCandidate(prev);
}

function setupNoteHandlers(svgelements) {
    let noteOrdinal = -1;
    // Box rects share the exact rnote signature (rect, stroke-width:0.5, no
    // rx/ry) and are told apart only by enclosing a participant header. Collect
    // participant bounds so box rects can be skipped here (they get their own
    // context menu / hover via setupBoxHandlers); otherwise a box would also
    // open the note menu and be miscounted in the note ordinal.
    const participantBounds = participantHeaderBounds(svgelements);

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
            // Mirror the mouseover guard: during an add-mode gesture (e.g. the
            // group ghost box) mouseover bails out before capturing the
            // original fill, leaving notecolor "". Restoring that empty fill
            // would blank the paint attribute and render the note black, so
            // skip the restore entirely while an add-mode gesture is active.
            if (isSequenceAddMode()) return;
            if (findActiveHighlight(sequenceHighlighted, svgelement)) return;
            svgelement.setAttribute('fill', notecolor);
        });
    }

    for (let index = 0; index < svgelements.length; index++) {
        let svgelement = svgelements[index];
        const tag = svgelement.tagName.toLowerCase();

        if ((tag === 'path' || tag === 'polygon' || tag === 'rect') && isNoteCandidate(svgelement)) {
            // A box rect looks exactly like an rnote; skip it so it isn't
            // handled/counted as a note (setupBoxHandlers owns it).
            if (tag === 'rect' && checkIfBoxRect(svgelement, participantBounds)) continue;
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

        // Note text should not be hoverable. Each note line is a separate
        // <text> element; only the first line's previous sibling is the
        // note's shape (fold-corner path for "note", or the single shape
        // for "hnote"/"rnote"), so isNoteText walks back over earlier lines
        // to find the anchoring shape and disable pointer events on every
        // line - not just the first.
        if (isNoteText(svgelement)) {
            svgelement.style.pointerEvents = 'none';
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

// Set a palette <select> to a stored color, shared by the Box/Note/Message
// edit modals. An empty/missing color selects "None". Palette options are
// matched case-insensitively (PlantUML color names are case-insensitive), so a
// color like "red" selects the canonical "Red" option. A color that is not in
// the palette at all (e.g. a hex value, or a name we don't list) is preserved
// by injecting it as a temporary option, so editing round-trips the color
// instead of silently resetting it to None (which would then clear it on save).
// Only one such custom option is kept at a time.
function setColorSelect(select, color) {
    const existingCustom = select.querySelector('option[data-custom-color]');
    if (existingCustom) existingCustom.remove();

    if (!color) {
        select.value = 'none';
        return;
    }

    const match = Array.from(select.options).find(
        (opt) => opt.value.toLowerCase() === color.toLowerCase()
    );
    if (match) {
        select.value = match.value;
        return;
    }

    const option = document.createElement('option');
    option.setAttribute('data-custom-color', '');
    option.value = color;
    option.textContent = color;
    // Colors are stored without the leading '#', so a hex value needs it
    // re-added to be valid CSS for the swatch; named colors are valid as-is.
    option.style.backgroundColor = cssColorValue(color);
    select.appendChild(option);
    select.value = color;
}

// Return a value usable as a CSS color: hex codes (3/6/8 hex digits, stored
// without '#') get the '#' re-added; anything else (a named color) is returned
// unchanged.
function cssColorValue(color) {
    return /^[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{3}(?:[0-9A-Fa-f]{2})?)?$/.test(color)
        ? '#' + color
        : color;
}

function noteOperationEventListeners() {
    // Submit button in the note modal (Add / Edit)
    $('#seq-submit-note').on('click', submitNote);

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
        document.getElementById('seq-note-color-group').style.display = 'none';
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
            document.getElementById('seq-note-color-group').style.display = 'block';
            setColorSelect(document.getElementById('seq-note-color-select'), responseData.color);
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
    // Submit button in the group label modal (Add / Rename)
    $('#seq-submit-group').on('click', submitGroup);

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
                    noteType: noteType,
                    color: document.getElementById('seq-note-color-select').value
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


// --- Box handlers (contextmenu + hover on participant boxes) ---

// Collect participant header rect bounds (rounded corners + the shared 0.5
// stroke), used to identify box rects by geometric enclosure.
function participantHeaderBounds(svgelements) {
    const bounds = [];
    for (const el of svgelements) {
        if (el.tagName.toLowerCase() !== 'rect') continue;
        const style = el.getAttribute('style') || '';
        if (el.hasAttribute('rx') && el.hasAttribute('ry') &&
            style.includes('stroke-width:0.5')) {
            bounds.push({
                x: parseFloat(el.getAttribute('x')),
                y: parseFloat(el.getAttribute('y')),
                width: parseFloat(el.getAttribute('width')),
                height: parseFloat(el.getAttribute('height'))
            });
        }
    }
    return bounds;
}

// A box rect shares the participant header style but has no rounded corners and
// a solid fill, and encloses at least one participant header. That enclosure is
// what separates it from an rnote (identical style/fill). Mirrors is_box_rect
// in sequence/box.py.
function checkIfBoxRect(svgelement, participantBounds) {
    if (svgelement.tagName.toLowerCase() !== 'rect') return false;
    if ((svgelement.getAttribute('style') || '') !== 'stroke:#181818;stroke-width:0.5;') {
        return false;
    }
    if (svgelement.hasAttribute('rx') || svgelement.hasAttribute('ry')) return false;
    const fill = svgelement.getAttribute('fill');
    if (!fill || fill === 'none') return false;

    const x = parseFloat(svgelement.getAttribute('x'));
    const y = parseFloat(svgelement.getAttribute('y'));
    const w = parseFloat(svgelement.getAttribute('width'));
    const h = parseFloat(svgelement.getAttribute('height'));
    return participantBounds.some(b =>
        x <= b.x && b.x + b.width <= x + w &&
        y <= b.y && b.y + b.height <= y + h);
}

// Opens the box context menu, identifying the box by its rect (the backend
// matches boxes by the rect's x/y).
// Box rects recorded during the last setup walk, with their bounds, so the
// background context menu can hit-test a right-click against them.
let boxElements = []; // [{rect, x, y, w, h}, ...]

// Return the innermost box enclosing the given point, or null. "Innermost" =
// smallest-area enclosing box, so a right-click inside a nested box targets the
// inner box rather than its container.
function findEnclosingBox(cx, cy) {
    let best = null;
    let bestArea = Infinity;
    for (const b of boxElements) {
        if (cx >= b.x && cx <= b.x + b.w && cy >= b.y && cy <= b.y + b.h) {
            const area = b.w * b.h;
            if (area < bestArea) {
                bestArea = area;
                best = b.rect;
            }
        }
    }
    return best;
}

// Attaches hover highlighting to each box rect and records its bounds. The box
// context menu is not attached here: the box rect covers the lifeline area, so
// a dedicated handler would hijack the lifeline right-click. Instead the
// background (lifeline) context menu detects an enclosing box via
// findEnclosingBox and appends Edit Box / Delete Box items. Boxes appear in
// document order matching puml source order (outer before inner), so the
// ordinal indexes boxPositions.
function setupBoxHandlers(svgelements) {
    const participantBounds = participantHeaderBounds(svgelements);
    boxElements = [];
    let boxOrdinal = -1;

    for (let index = 0; index < svgelements.length; index++) {
        const svgelement = svgelements[index];
        if (!checkIfBoxRect(svgelement, participantBounds)) continue;

        boxOrdinal++;
        const box = boxPositions[boxOrdinal];

        boxElements.push({
            rect: svgelement,
            x: parseFloat(svgelement.getAttribute('x')),
            y: parseFloat(svgelement.getAttribute('y')),
            w: parseFloat(svgelement.getAttribute('width')),
            h: parseFloat(svgelement.getAttribute('height')),
        });

        // Register for editor->diagram highlighting on both the box header and
        // its end box line (registerSequenceRow drops any -1 line).
        if (box) {
            registerSequenceRow(box.headerIndex, svgelement, 'box');
            registerSequenceRow(box.endIndex, svgelement, 'box');
        }

        const thisOrdinal = boxOrdinal;
        svgelement.addEventListener('mouseover', function() {
            if (isSequenceAddMode()) return;
            const b = boxPositions[thisOrdinal];
            if (b && b.headerIndex >= 0) {
                getmarker([b.headerIndex, b.endIndex >= 0 ? b.endIndex : b.headerIndex]);
            }
        });
        svgelement.addEventListener('mouseout', function() {
            clearMarkers();
        });
    }
}
