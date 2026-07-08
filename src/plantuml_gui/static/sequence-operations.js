// Shared state
let currentContextMenuHandler = null;
let participantLifelines = [];
const LIFELINE_TOLERANCE = 15;

// Note/group positions fetched from backend (refreshed each render)
let notePositions = []; // [{cy, index}, ...]
let groupPositions = []; // [{headerIndex, endIndex}, ...]

// Elements highlighted from the editor side, with how to restore them
let sequenceHighlighted = []; // [{el, kind, old}, ...]

// --- Utilities ---

// Convert mouse event screen coordinates to SVG coordinate space
function svgPointFromEvent(e, svgElement) {
    let point = svgElement.createSVGPoint();
    point.x = e.clientX;
    point.y = e.clientY;
    return point.matrixTransform(svgElement.getScreenCTM().inverse());
}

// Fetch participant lifeline positions from backend (called once per render)
async function extractLifelinePositions() {
    participantLifelines = [];
    const element = document.getElementById('colb');
    const svg = element.querySelector('g');
    if (!svg) return;
    try {
        const plantuml = trimlines(editor.session.getValue());
        const response = await fetch("getParticipantPositions", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({plantuml: plantuml, svg: svg.innerHTML})
        });
        const data = await response.json();
        participantLifelines = data.positions;
    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }
}

// Fetch note positions from backend (called once per render)
async function fetchNotePositions() {
    notePositions = [];
    const element = document.getElementById('colb');
    const svg = element.querySelector('g');
    if (!svg) return;
    try {
        const plantuml = trimlines(editor.session.getValue());
        const response = await fetch("getSeqNotePositions", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({plantuml: plantuml, svg: svg.innerHTML})
        });
        const data = await response.json();
        notePositions = data.positions;
    } catch (error) {
        notePositions = [];
    }
}

// Fetch group positions from backend (called once per render)
async function fetchGroupPositions() {
    groupPositions = [];
    const element = document.getElementById('colb');
    const svg = element.querySelector('g');
    if (!svg) return;
    try {
        const plantuml = trimlines(editor.session.getValue());
        const response = await fetch("getSeqGroupPositions", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({plantuml: plantuml, svg: svg.innerHTML})
        });
        const data = await response.json();
        groupPositions = data.positions;
    } catch (error) {
        groupPositions = [];
    }
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

// Restore the literal style attribute. Mutating el.style re-serializes the
// attribute and loses the exact "stroke-width:1.0" string that the element
// classifiers (e.g. checkIfMessageElement) match on, so unhighlighting must
// put back the original attribute rather than clear style properties.
function restoreStyleAttribute(el, old) {
    if (old) {
        el.setAttribute('style', old);
    } else {
        el.removeAttribute('style');
    }
}

function resetSequenceHighlight() {
    for (const entry of sequenceHighlighted) {
        if (entry.kind === 'message' || entry.kind === 'group') {
            restoreStyleAttribute(entry.el, entry.old);
        } else { // participant or note fill
            entry.el.setAttribute('fill', entry.old);
        }
    }
    sequenceHighlighted = [];
}

// Highlight the diagram element(s) defined on the given editor row
function highlightSequenceForRow(row) {
    if (isSequenceAddMode()) return;
    const element = document.getElementById('colb');
    const svg = element ? element.querySelector('g') : null;
    if (!svg) return;
    const svgelements = svg.querySelectorAll('*');

    const message = messagePositions.find(m => m.index === row);
    if (message) {
        // Assign each message element to its nearest message (same rule as
        // hover in the other direction) so tolerances never overlap neighbors.
        for (const el of svgelements) {
            if (!checkIfMessageElement(el)) continue;
            const nearest = findNearestMessage(messageElementCy(el));
            if (nearest && nearest.index === row) {
                const old = el.getAttribute('style');
                el.style.fontWeight = 'bold';
                el.style.strokeWidth = '2.0';
                sequenceHighlighted.push({el: el, kind: 'message', old: old});
            }
        }
        return;
    }

    const participant = participantLifelines.find(p => p.index === row);
    if (participant) {
        for (let i = 0; i < svgelements.length; i++) {
            if (!checkIfParticipant(svgelements, i)) continue;
            const el = svgelements[i];
            const cx = parseFloat(el.getAttribute('x')) + parseFloat(el.getAttribute('width')) / 2;
            if (Math.abs(cx - participant.cx) <= 1) {
                sequenceHighlighted.push({el: el, kind: 'participant', old: el.getAttribute('fill')});
                el.setAttribute('fill', '#d8d8d8');
            }
        }
        return;
    }

    const noteOrdinal = notePositions.findIndex(n => n.index === row);
    if (noteOrdinal !== -1) {
        // Each note renders two #FEFFDD paths (body + fold) in document order
        let pathCount = 0;
        for (const el of svgelements) {
            if (el.tagName.toLowerCase() !== 'path' || el.getAttribute('fill') !== '#FEFFDD') continue;
            if (Math.floor(pathCount / 2) === noteOrdinal) {
                sequenceHighlighted.push({el: el, kind: 'note', old: el.getAttribute('fill')});
                el.setAttribute('fill', '#d8d8d8');
            }
            pathCount++;
        }
        return;
    }

    const groupOrdinal = groupPositions.findIndex(g => g.headerIndex === row || g.endIndex === row);
    if (groupOrdinal !== -1) {
        // Group boxes (rect fill "none") appear in document order matching
        // puml source order; the #EEEEEE tab path precedes its box.
        let boxCount = 0;
        let lastTabPath = null;
        for (const el of svgelements) {
            if (el.tagName.toLowerCase() === 'path' && el.getAttribute('fill') === '#EEEEEE') {
                lastTabPath = el;
                continue;
            }
            if (!checkIfGroupBox(el)) continue;
            // Skip PlantUML's invisible layout rect (fill="none" with no
            // preceding tab path). Only real boxes advance the ordinal, matching
            // the backend get_group_positions / _count_group_boxes count.
            if (!lastTabPath) continue;
            if (boxCount === groupOrdinal) {
                const oldBox = el.getAttribute('style');
                el.style.strokeWidth = '2.0';
                sequenceHighlighted.push({el: el, kind: 'group', old: oldBox});
                const oldTab = lastTabPath.getAttribute('style');
                lastTabPath.style.strokeWidth = '2.0';
                sequenceHighlighted.push({el: lastTabPath, kind: 'group', old: oldTab});
                break;
            }
            boxCount++;
            lastTabPath = null;
        }
    }
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
            const highlighted = sequenceHighlighted.find(h => h.el === svgelement);
            rectcolor = highlighted ? highlighted.old : svgelement.getAttribute('fill');
            svgelement.setAttribute('fill', '#d8d8d8');
            const cx = parseFloat(svgelement.getAttribute('x')) + parseFloat(svgelement.getAttribute('width')) / 2;
            const lifeline = participantLifelines.find(p => Math.abs(p.cx - cx) <= 1);
            if (lifeline && lifeline.index >= 0) setEditorMarkers(lifeline.index);
        });

        svgelement.addEventListener('mouseout', function() {
            clearMarkers();
            if (sequenceHighlighted.some(h => h.el === svgelement)) return;
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
        const svgContainer = element.querySelector('svg');
        const svg = element.querySelector('g');
        if (!svg) {
            toggleLoadingOverlay();
            return;
        }

        await extractLifelinePositions();
        await fetchMessagePositions();
        await fetchNotePositions();
        await fetchGroupPositions();
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

// Identifies participant header rects by their PlantUML-specific style
function checkIfParticipant(svgelements, index) {
    return (svgelements[index].tagName.toLowerCase() === 'rect') &&
        (svgelements[index].getAttribute('style') == "stroke:#181818;stroke-width:0.5;");
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
        // Exclude note text (preceded by a #FEFFDD path)
        let prev = svgelement.previousElementSibling;
        if (prev && prev.tagName.toLowerCase() === 'path' &&
            prev.getAttribute('fill') === '#FEFFDD') {
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

        let originalstyle; // undefined while no hover is in progress
        svgelement.addEventListener('mouseover', function() {
            if (isSequenceAddMode()) return;
            // If already highlighted from the editor side, keep the original style
            const highlighted = sequenceHighlighted.find(h => h.el === svgelement);
            originalstyle = highlighted ? highlighted.old : svgelement.getAttribute('style');
            svgelement.style.fontWeight = 'bold';
            svgelement.style.strokeWidth = '2.0';
            const nearest = findNearestMessage(messageElementCy(svgelement));
            if (nearest) setEditorMarkers(nearest.index);
        });

        svgelement.addEventListener('mouseout', function() {
            clearMarkers();
            if (originalstyle === undefined) return;
            // Keep styles if the element is highlighted from the editor side
            if (sequenceHighlighted.some(h => h.el === svgelement)) return;
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

function setupNoteHandlers(svgelements) {
    // Each note renders two #FEFFDD paths (body + fold) in document order
    let notePathCount = 0;
    for (let index = 0; index < svgelements.length; index++) {
        let svgelement = svgelements[index];
        const tag = svgelement.tagName.toLowerCase();

        // Note body paths have fill #FEFFDD
        if (tag === 'path' && svgelement.getAttribute('fill') === '#FEFFDD') {
            const noteOrdinal = Math.floor(notePathCount / 2);
            notePathCount++;

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
                const highlighted = sequenceHighlighted.find(h => h.el === svgelement);
                notecolor = highlighted ? highlighted.old : svgelement.getAttribute('fill');
                svgelement.setAttribute('fill', '#d8d8d8');
                const note = notePositions[noteOrdinal];
                if (note && note.index >= 0) setEditorMarkers(note.index);
            });

            svgelement.addEventListener('mouseout', function() {
                clearMarkers();
                if (sequenceHighlighted.some(h => h.el === svgelement)) return;
                svgelement.setAttribute('fill', notecolor);
            });
        }

        // Note text should not be hoverable
        if (tag === 'text' && svgelement.getAttribute('font-size') === '13') {
            let prev = svgelement.previousElementSibling;
            if (prev && prev.tagName.toLowerCase() === 'path' &&
                prev.getAttribute('fill') === '#FEFFDD') {
                svgelement.style.pointerEvents = 'none';
            }
        }
    }
}

// --- Note operation event listeners ---

let notePlacement = '';
let noteEditMode = false;
let isAddNoteActive = false;

function isNoteAddMode() {
    return isAddNoteActive;
}

function cancelNoteAddMode() {
    isAddNoteActive = false;
}

function noteOperationEventListeners() {
    // "Add Note" in sequence-menu shows the placement menu
    document.getElementById('seq-addNote').addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
        isAddNoteActive = true;
        var seqMenu = document.getElementById('sequence-menu');
        var placementMenu = document.getElementById('seq-note-placement-menu');
        placementMenu.style.display = 'block';
        placementMenu.style.left = seqMenu.style.left;
        placementMenu.style.top = seqMenu.style.top;
        seqMenu.style.display = 'none';
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
            var text = (await response.json()).text;
            noteEditMode = true;
            isAddNoteActive = false;
            document.querySelector('#seq-note-modalForm .modal-title').textContent = 'Edit Note';
            document.getElementById('seq-note-text').value = text;
            document.getElementById('seq-note-second-participant-group').style.display = 'none';
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
                    text: text
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
                xPosition: firstClickCoordinates[0]
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
