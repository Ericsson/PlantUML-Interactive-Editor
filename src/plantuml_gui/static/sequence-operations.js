// Shared state
let currentContextMenuHandler = null;
let participantLifelines = [];
const LIFELINE_TOLERANCE = 15;

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
            const svg = element.querySelector('g');
            resetHighlight(svg);
            rectcolor = svgelement.getAttribute('fill');
            svgelement.setAttribute('fill', '#d8d8d8');
        });

        svgelement.addEventListener('mouseout', function() {
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
}

// Called on every render when diagram type is sequence
async function setHandlersForSequenceDiagram(pumlcontent, element) {
    fetchSvgFromPlantUml().then((svgContent) => {
        element.innerHTML = svgContent;
        const svgContainer = element.querySelector('svg');
        const svg = element.querySelector('g');
        if (!svg) {
            toggleLoadingOverlay();
            return;
        }

        extractLifelinePositions();
        cancelMessageAddMode();

        handleContextMenuBackground(svgContainer);
        setupLifelineInteraction(svgContainer);
        setupParticipantHandlers(svg.querySelectorAll('*'), svg, element);
        setupMessageHandlers(svg.querySelectorAll('*'), svg);
        setupNoteHandlers(svg.querySelectorAll('*'));

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

// --- Message element handlers (hover, contextmenu) ---

function setupMessageHandlers(svgelements, svg) {
    for (let index = 0; index < svgelements.length; index++) {
        let svgelement = svgelements[index];
        if (!checkIfMessageElement(svgelement)) continue;

        svgelement.addEventListener('mouseover', function() {
            svgelement.style.fontWeight = 'bold';
            svgelement.style.strokeWidth = '2.0';
        });

        svgelement.addEventListener('mouseout', function() {
            svgelement.style.fontWeight = '';
            svgelement.style.strokeWidth = '';
        });

        svgelement.addEventListener('contextmenu', function(e) {
            lastclickedsvgelement = svgelement;
            e.preventDefault();
            e.stopPropagation();
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
    for (let index = 0; index < svgelements.length; index++) {
        let svgelement = svgelements[index];
        const tag = svgelement.tagName.toLowerCase();

        // Note body paths have fill #FEFFDD
        if (tag === 'path' && svgelement.getAttribute('fill') === '#FEFFDD') {
            svgelement.addEventListener('contextmenu', function(e) {
                lastclickedsvgelement = svgelement;
                e.preventDefault();
                e.stopPropagation();
                var contextMenu = document.getElementById('seq-note-menu');
                contextMenu.style.display = 'block';
                contextMenu.style.left = e.pageX + 'px';
                contextMenu.style.top = e.pageY + 'px';
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

function noteOperationEventListeners() {
    // "Add Note" in sequence-menu shows the placement menu
    document.getElementById('seq-addNote').addEventListener('click', function(e) {
        e.preventDefault();
        e.stopPropagation();
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
}

// Global function called by onclick on the submit-note button
async function submitNote() {
    var textarea = document.getElementById('seq-note-text');
    console.log('textarea element:', textarea);
    console.log('textarea.value:', JSON.stringify(textarea.value));
    console.log('textarea.textContent:', JSON.stringify(textarea.textContent));
    console.log('textarea.innerHTML:', JSON.stringify(textarea.innerHTML));
    console.log('all textareas on page:', document.querySelectorAll('textarea').length);
    document.querySelectorAll('textarea').forEach(function(t) {
        console.log('  textarea id=' + t.id + ' value=' + JSON.stringify(t.value));
    });
    var element = document.getElementById('colb');
    var svg = element.querySelector('g');
    var text = document.getElementById('seq-note-text').value;
    console.log('note text:', text);
    console.log('noteEditMode:', noteEditMode);
    console.log('messageOrigin:', messageOrigin);
    console.log('notePlacement:', notePlacement);
    console.log('firstClickCoordinates:', firstClickCoordinates);
    if (!text) {
        console.log('text is empty, returning');
        return;
    }

    try {
        var plantuml = trimlines(editor.session.getValue());
        console.log('plantuml length:', plantuml.length);
        console.log('svg innerHTML length:', svg.innerHTML.length);
        var response;
        if (noteEditMode) {
            noteEditMode = false;
            console.log('editing note...');
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
                yPosition: firstClickCoordinates[1]
            };
            if (notePlacement === 'spanning') {
                body.secondParticipant = document.getElementById('seq-note-second-participant').value;
            }
            console.log('adding note, body:', JSON.stringify(body).substring(0, 200));
            response = await fetch("addNote", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify(body)
            });
        }
        console.log('response status:', response.status);
        var data = await response.json();
        console.log('response data plantuml:', data.plantuml.substring(0, 100));
        $('#seq-note-modalForm').modal('hide');
        setPuml(data.plantuml);
        console.log('setPuml done');
    } catch (error) {
        console.error('submitNote error:', error);
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }
}
