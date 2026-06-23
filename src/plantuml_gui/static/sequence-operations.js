let currentContextMenuHandler = null;
let participantLifelines = [];
const LIFELINE_TOLERANCE = 15;

function svgPointFromEvent(e, svgElement) {
    let point = svgElement.createSVGPoint();
    point.x = e.clientX;
    point.y = e.clientY;
    return point.matrixTransform(svgElement.getScreenCTM().inverse());
}

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

function removeBackgroundMenuListener() {
    const background = document.getElementById('colb-container');
    if (currentContextMenuHandler) {
        background.removeEventListener('contextmenu', currentContextMenuHandler);
        currentContextMenuHandler = null;
    }
}

function backgroundContextMenu(e, svgElement) {
    e.preventDefault();

    const transformed = svgPointFromEvent(e, svgElement);
    const cx = transformed.x;
    const cy = transformed.y;

    // If in message-add mode, ignore right-click on background
    if (isAddMessageActive) return;

    const lifeline = findNearestLifeline(cx, cy);
    const addMessageItem = document.getElementById("addMessage");
    addMessageItem.style.display = lifeline ? "block" : "none";

    if (lifeline) {
        // Store origin for message-add mode
        firstClickCoordinates = [lifeline.cx, cy];
        messageOrigin = {cx: lifeline.cx, y: cy, name: lifeline.name};
    }

    var contextMenu = document.getElementById('sequence-menu');
    contextMenu.style.display = 'block';
    contextMenu.style.left = e.pageX + 'px';
    contextMenu.style.top = e.pageY + 'px';
}

function handleContextMenuBackground(svgElement) {
    const background = document.getElementById('colb-container');
    removeBackgroundMenuListener();
    currentContextMenuHandler = (e) => backgroundContextMenu(e, svgElement);
    background.addEventListener('contextmenu', currentContextMenuHandler);
}

function participantEventListeners() {
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

function sequenceEventListeners() {
    participantEventListeners();
    messageEventListeners();
}

async function setHandlersForSequenceDiagram(pumlcontent, element) {
    fetchSvgFromPlantUml().then((svgContent) => {
        element.innerHTML = svgContent;
        const svgContainer = element.querySelector('svg');
        const svg = element.querySelector('g')
        if (!svg) {
            toggleLoadingOverlay();
            return
        }

        extractLifelinePositions();
        cancelMessageAddMode();

        const svgelements = svg.querySelectorAll('*');
        handleContextMenuBackground(svgContainer);
        setupLifelineInteraction(svgContainer);

        for (let index = 0; index < svgelements.length;) {
            let svgelement = svgelements[index]
            if (svgelement.tagName.toLowerCase() === 'text') {
                svgelement.style.pointerEvents = 'none';
            }

            if (checkIfParticipant(svgelements, index)) {
                svgelement.addEventListener('dblclick', async () => {
                    lastclickedsvgelement = svgelement
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
                        $('#participant-name-modalForm').on('shown.bs.modal', function () {
                            $('#participant-name-text').trigger('focus');
                        });


                    } catch (error) {
                        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
                    }
                });

                let rectcolor = ""
                svgelement.addEventListener('mouseover', function() {
                    const svg = element.querySelector('g');
                    resetHighlight(svg);

                    rectcolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', rectcolor)
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
            index++
        }
        toggleLoadingOverlay();

    }).catch((error) => {
        displayErrorMessage(`Error rendering SVG: ${error.message}`, error);
    });
}

function checkIfParticipant(svgelements, index) {
    return (svgelements[index].tagName.toLowerCase() === 'rect') && (svgelements[index].getAttribute('style') == "stroke:#181818;stroke-width:0.5;")
}
