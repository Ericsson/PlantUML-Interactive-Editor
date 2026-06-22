let currentContextMenuHandler = null;
let firstClickCoordinates = null;
let secondClickCoordinates = null;
let isAddMessageActive = false;

let participantLifelines = [];
const LIFELINE_TOLERANCE = 15;

// Ghost arrow and indicator overlay elements
let indicatorBox = null;
let ghostLine = null;
let ghostArrow = null;
let messageOrigin = null;

function sequenceEventListeners() {
    document.getElementById('addMessage').addEventListener('click', () => {
        isAddMessageActive = true;
        hideIndicatorBox();
        document.getElementById('sequence-menu').style.display = 'none';
    });

    $('#submit-participant-message').on('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');

        var newmessage = $('#participant-message-text').val();
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("addMessage", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'message': newmessage,
                    'svgelement': lastclickedsvgelement.outerHTML,
                    'firstcoordinates': firstClickCoordinates,
                    'secondcoordinates': secondClickCoordinates,
                }),
            });
            const data = await response.json();
            setPuml(data.plantuml)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

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

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isAddMessageActive) {
            cancelMessageAddMode();
        }
    });
}

function extractLifelinePositions(svg) {
    participantLifelines = [];
    const lines = svg.querySelectorAll('line');
    for (const line of lines) {
        const style = line.getAttribute('style') || '';
        if (style.includes('stroke-dasharray:5.0,5.0')) {
            participantLifelines.push({
                cx: parseFloat(line.getAttribute('x1')),
                yTop: parseFloat(line.getAttribute('y1')),
                yBottom: parseFloat(line.getAttribute('y2'))
            });
        }
    }
}

function findNearestLifeline(x, y, excludeCx) {
    for (const lifeline of participantLifelines) {
        if (excludeCx !== undefined && lifeline.cx === excludeCx) continue;
        if (Math.abs(x - lifeline.cx) <= LIFELINE_TOLERANCE &&
            y >= lifeline.yTop && y <= lifeline.yBottom) {
            return lifeline;
        }
    }
    return null;
}

function showIndicatorBox(svgElement, cx, y) {
    if (!indicatorBox) {
        indicatorBox = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        indicatorBox.setAttribute('width', '10');
        indicatorBox.setAttribute('height', '10');
        indicatorBox.setAttribute('fill', '#5b9bd5');
        indicatorBox.setAttribute('opacity', '0.7');
        indicatorBox.setAttribute('pointer-events', 'none');
    }
    indicatorBox.setAttribute('x', cx - 5);
    indicatorBox.setAttribute('y', y - 5);
    const g = svgElement.querySelector('g');
    if (g && !indicatorBox.parentNode) {
        g.appendChild(indicatorBox);
    }
}

function hideIndicatorBox() {
    if (indicatorBox && indicatorBox.parentNode) {
        indicatorBox.parentNode.removeChild(indicatorBox);
    }
}

function showGhostArrow(svgElement, fromCx, toCx, y) {
    const g = svgElement.querySelector('g');
    if (!g) return;

    if (!ghostLine) {
        ghostLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        ghostLine.setAttribute('stroke', '#888');
        ghostLine.setAttribute('stroke-width', '1.5');
        ghostLine.setAttribute('stroke-dasharray', '4,4');
        ghostLine.setAttribute('opacity', '0.7');
        ghostLine.setAttribute('pointer-events', 'none');
    }
    ghostLine.setAttribute('x1', fromCx);
    ghostLine.setAttribute('y1', y);
    ghostLine.setAttribute('x2', toCx);
    ghostLine.setAttribute('y2', y);
    if (!ghostLine.parentNode) g.appendChild(ghostLine);

    // Arrowhead polygon pointing at toCx
    if (!ghostArrow) {
        ghostArrow = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
        ghostArrow.setAttribute('fill', '#888');
        ghostArrow.setAttribute('opacity', '0.7');
        ghostArrow.setAttribute('pointer-events', 'none');
    }
    const dir = toCx > fromCx ? 1 : -1;
    const tipX = toCx;
    const baseX = toCx - dir * 8;
    ghostArrow.setAttribute('points',
        `${tipX},${y} ${baseX},${y - 4} ${baseX},${y + 4}`);
    if (!ghostArrow.parentNode) g.appendChild(ghostArrow);
}

function hideGhostArrow() {
    if (ghostLine && ghostLine.parentNode) ghostLine.parentNode.removeChild(ghostLine);
    if (ghostArrow && ghostArrow.parentNode) ghostArrow.parentNode.removeChild(ghostArrow);
}

function cancelMessageAddMode() {
    isAddMessageActive = false;
    messageOrigin = null;
    hideGhostArrow();
}

function removeBackgroundMenuListener() {
    const background = document.getElementById('colb-container');
    if (currentContextMenuHandler) {
        background.removeEventListener('contextmenu', currentContextMenuHandler);
        currentContextMenuHandler = null;
    }
}

function svgPointFromEvent(e, svgElement) {
    let point = svgElement.createSVGPoint();
    point.x = e.clientX;
    point.y = e.clientY;
    return point.matrixTransform(svgElement.getScreenCTM().inverse());
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
        messageOrigin = {cx: lifeline.cx, y: cy};
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

function setupLifelineInteraction(svgContainer) {
    const container = document.getElementById('colb-container');

    container.addEventListener('mousemove', (e) => {
        if (!svgContainer || !svgContainer.getScreenCTM()) return;
        const transformed = svgPointFromEvent(e, svgContainer);
        const x = transformed.x;
        const y = transformed.y;

        if (isAddMessageActive) {
            const dest = findNearestLifeline(x, y, messageOrigin.cx);
            if (dest) {
                showGhostArrow(svgContainer, messageOrigin.cx, dest.cx, y);
            } else {
                hideGhostArrow();
            }
            hideIndicatorBox();
        } else {
            hideGhostArrow();
            const lifeline = findNearestLifeline(x, y);
            if (lifeline) {
                showIndicatorBox(svgContainer, lifeline.cx, y);
            } else {
                hideIndicatorBox();
            }
        }
    });

    container.addEventListener('click', (e) => {
        if (!isAddMessageActive || !messageOrigin) return;
        if (!svgContainer || !svgContainer.getScreenCTM()) return;

        const transformed = svgPointFromEvent(e, svgContainer);
        const x = transformed.x;
        const y = transformed.y;

        const dest = findNearestLifeline(x, y, messageOrigin.cx);
        if (!dest) return;

        // Store coordinates and show label dialog
        secondClickCoordinates = [dest.cx, y];
        firstClickCoordinates = [messageOrigin.cx, y];

        cancelMessageAddMode();

        $('#participant-message-text').val("");
        $('#participant-modalForm').modal('show');
        $('#participant-modalForm').on('shown.bs.modal', function() {
            $('#participant-message-text').trigger('focus');
        });
    });
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

        extractLifelinePositions(svg);
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
