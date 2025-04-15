let currentContextMenuHandler = null;
let firstClickCoordinates = null;
let secondClickCoordinates = null;
let isAddMessageActive = null;

function sequenceEventListeners() {
    document.getElementById('addMessage').addEventListener('click', async () => {
        isAddMessageActive = true;
        console.log("addMessage selected, waiting for second click")
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
            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    $('#submit-participant-name').on('click', async () => {
        const element = document.getElementById('colb');
        const svg = element.querySelector('g');

        var newname = $('#participant-name-text').val()
        participant_cx = parseFloat(lastclickedsvgelement.getAttribute('x'))
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
                    'cx': participant_cx
                }),
            });
            const pumlcontentcode = await response.text();
            setPuml(pumlcontentcode);
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });


    const sequenceList = [{
        id: 'addParticipant',
        endpoint: 'addParticipant',
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
                    'cx' : firstClickCoordinates[0]
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
                const pumlcontentcode = await response.text();
                setPuml(pumlcontentcode);
            } catch (error) {
                displayErrorMessage(`Error with fetch API: ${error.message}`, error);
            }
        });
    });
}

function removeBackgroundMenuListener() {
    const background = document.getElementById('colb-container');
    if (currentContextMenuHandler) {
        background.removeEventListener('contextmenu', currentContextMenuHandler);
        currentContextMenuHandler = null; // Reset the handler reference after removal
    }
}

async function backgroundContextMenu(e, svgelement) {
    e.preventDefault();

    // Get coordinates of click relative to the svg
    let point = svgelement.createSVGPoint();
    point.x = e.clientX;
    point.y = e.clientY;
    let transformedPoint = point.matrixTransform(svgelement.getScreenCTM().inverse());
    cx = transformedPoint.x
    cy = transformedPoint.y

    if (isAddMessageActive) {
        secondClickCoordinates = [cx, cy];
        console.log(secondClickCoordinates)

        // Show the modal for message input
        $('#participant-message-text').val("");
        $('#participant-modalForm').modal('show');
        $('#participant-modalForm').on('shown.bs.modal', function() {
            $('#participant-message-text').trigger('focus');
        });

        // Deactivate addMessage mode after the second click
        isAddMessageActive = false;
        return;
    }

    firstClickCoordinates = [cx, cy]
    console.log(firstClickCoordinates)

    const isInValidArea = await checkIfInsideParticipant(firstClickCoordinates);

    // If click is inside a participant, display addMessage option
    const addMessageItem = document.getElementById("addMessage");
    addMessageItem.style.display = isInValidArea ? "block" : "none";

    var contextMenu = document.getElementById('sequence-menu');
    contextMenu.style.display = 'block';
    contextMenu.style.left = e.pageX + 'px';
    contextMenu.style.top = e.pageY + 'px';
}

async function checkIfInsideParticipant(clickCoordinates) {
    const svg = element.querySelector('g');
    try {
        const plantuml = trimlines(editor.session.getValue());
        const toBeStringified = {
            'plantuml': plantuml,
            'svg': svg.innerHTML,
            'coordinates': clickCoordinates
        }

        const response = await fetch('checkIfInsideParticipant', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify(toBeStringified)
        });

        const data = await response.json();
        return data.isValid;
    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }
}

async function handleContextMenuBackground(svgelement) {
    const background = document.getElementById('colb-container');

    // Remove any existing context menu handler before adding a new one
    removeBackgroundMenuListener();

    // Create and store the new context menu handler
    currentContextMenuHandler = (e) => backgroundContextMenu(e, svgelement);

    // Attach the new context menu event listener
    background.addEventListener('contextmenu', currentContextMenuHandler);
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
        const svgelements = svg.querySelectorAll('*');
        handleContextMenuBackground(svgContainer);
        for (let index = 0; index < svgelements.length;) {
            let svgelement = svgelements[index]
            if (svgelement.tagName.toLowerCase() === 'text') {
                svgelement.style.pointerEvents = 'none';
            }

            if (checkIfParticipant(svgelements, index)) {
                svgelement.addEventListener('dblclick', async () => {
                    lastclickedsvgelement = svgelement
                    participant_cx = parseFloat(lastclickedsvgelement.getAttribute('x'))
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
                                'cx': participant_cx
                            })
                        });
                        $('#participant-name-text').val(await response.text());
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
