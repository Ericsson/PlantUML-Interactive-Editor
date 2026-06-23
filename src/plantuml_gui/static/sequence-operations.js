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
