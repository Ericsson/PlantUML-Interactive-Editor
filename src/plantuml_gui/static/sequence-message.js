// State for the add-message interaction flow
let isAddMessageActive = false;
let firstClickCoordinates = null;
let secondClickCoordinates = null;
let messageOrigin = null;
let messageArrowType = '->';

// Reusable SVG overlay elements (created once, moved on each frame)
let indicatorCircle = null;
let ghostLine = null;
let ghostArrow = null;
let ghostSelfPath = null;

// --- Lifeline detection ---

function findNearestLifeline(x, y, participantLifelines) {
    for (const lifeline of participantLifelines) {
        if (Math.abs(x - lifeline.cx) <= LIFELINE_TOLERANCE &&
            y >= lifeline.yTop && y <= lifeline.yBottom) {
            return lifeline;
        }
    }
    return null;
}

// --- Hover indicator (blue circle on lifeline) ---

function showIndicatorCircle(svgElement, cx, y) {
    if (!indicatorCircle) {
        indicatorCircle = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        indicatorCircle.setAttribute('r', '5');
        indicatorCircle.setAttribute('fill', '#5b9bd5');
        indicatorCircle.setAttribute('opacity', '0.7');
        indicatorCircle.setAttribute('pointer-events', 'none');
    }
    indicatorCircle.setAttribute('cx', cx);
    indicatorCircle.setAttribute('cy', y);
    const g = svgElement.querySelector('g');
    if (g && !indicatorCircle.parentNode) {
        g.appendChild(indicatorCircle);
    }
}

function hideIndicatorCircle() {
    if (indicatorCircle && indicatorCircle.parentNode) {
        indicatorCircle.parentNode.removeChild(indicatorCircle);
    }
}

// --- Ghost arrow (dashed preview of the message being added) ---

function showGhostArrow(svgElement, fromCx, toCx, y) {
    const g = svgElement.querySelector('g');
    if (!g) return;

    if (fromCx === toCx) {
        // Self-message: draw a loop going right, down, and back
        hideGhostLine();
        if (!ghostSelfPath) {
            ghostSelfPath = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
            ghostSelfPath.setAttribute('stroke', '#888');
            ghostSelfPath.setAttribute('stroke-width', '1.5');
            ghostSelfPath.setAttribute('opacity', '0.7');
            ghostSelfPath.setAttribute('fill', 'none');
            ghostSelfPath.setAttribute('pointer-events', 'none');
        }
        ghostSelfPath.setAttribute('stroke-dasharray', messageArrowType === '-->' ? '4,4' : 'none');
        const loopWidth = 30;
        const loopHeight = 20;
        ghostSelfPath.setAttribute('points',
            `${fromCx},${y} ${fromCx + loopWidth},${y} ${fromCx + loopWidth},${y + loopHeight} ${fromCx},${y + loopHeight}`);
        if (!ghostSelfPath.parentNode) g.appendChild(ghostSelfPath);

        if (!ghostArrow) {
            ghostArrow = document.createElementNS('http://www.w3.org/2000/svg', 'polygon');
            ghostArrow.setAttribute('fill', '#888');
            ghostArrow.setAttribute('opacity', '0.7');
            ghostArrow.setAttribute('pointer-events', 'none');
        }
        ghostArrow.setAttribute('points',
            `${fromCx},${y + loopHeight} ${fromCx + 8},${y + loopHeight - 4} ${fromCx + 8},${y + loopHeight + 4}`);
        if (!ghostArrow.parentNode) g.appendChild(ghostArrow);
        return;
    }

    // Normal message: straight dashed line with arrowhead
    hideGhostSelfPath();
    if (!ghostLine) {
        ghostLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        ghostLine.setAttribute('stroke', '#888');
        ghostLine.setAttribute('stroke-width', '1.5');
        ghostLine.setAttribute('opacity', '0.7');
        ghostLine.setAttribute('pointer-events', 'none');
    }
    ghostLine.setAttribute('stroke-dasharray', messageArrowType === '-->' ? '4,4' : 'none');
    ghostLine.setAttribute('x1', fromCx);
    ghostLine.setAttribute('y1', y);
    ghostLine.setAttribute('x2', toCx);
    ghostLine.setAttribute('y2', y);
    if (!ghostLine.parentNode) g.appendChild(ghostLine);

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

function hideGhostLine() {
    if (ghostLine && ghostLine.parentNode) ghostLine.parentNode.removeChild(ghostLine);
}

function hideGhostSelfPath() {
    if (ghostSelfPath && ghostSelfPath.parentNode) ghostSelfPath.parentNode.removeChild(ghostSelfPath);
}

function hideGhostArrow() {
    hideGhostLine();
    hideGhostSelfPath();
    if (ghostArrow && ghostArrow.parentNode) ghostArrow.parentNode.removeChild(ghostArrow);
}

// --- Message-add mode lifecycle ---

function cancelMessageAddMode() {
    isAddMessageActive = false;
    messageOrigin = null;
    hideGhostArrow();
}

function isSequenceAddMode() {
    return isAddMessageActive ||
        (typeof isActivationAddMode === 'function' && isActivationAddMode()) ||
        (typeof isGroupAddMode === 'function' && isGroupAddMode()) ||
        (typeof isNoteAddMode === 'function' && isNoteAddMode());
}

// --- Background context menu (right-click on diagram) ---

function backgroundContextMenu(e, svgElement) {
    e.preventDefault();

    const transformed = svgPointFromEvent(e, svgElement);
    const cx = transformed.x;
    const cy = transformed.y;

    if (isSequenceAddMode()) return;

    const lifeline = findNearestLifeline(cx, cy, participantLifelines);

    if (!lifeline) return;

    firstClickCoordinates = [lifeline.cx, cy];
    messageOrigin = {cx: lifeline.cx, y: cy, name: lifeline.name};

    // If the right-click landed on an activation bar (a rect with the
    // stroke:#181818;stroke-width:1.0 style; participant headers use 0.5 and the
    // SVG background uses a transparent stroke), show the "Delete activation
    // bar" item and remember the clicked bar for the delete request.
    const target = e.target;
    const onBar = target && target.tagName &&
        target.tagName.toLowerCase() === 'rect' &&
        (target.getAttribute('style') || '').includes('stroke:#181818;stroke-width:1.0');
    const deleteItem = document.getElementById('seq-deleteActivation-item');
    const deleteDivider = document.getElementById('seq-deleteActivation-divider');
    if (onBar) {
        lastclickedsvgelement = target;
        deleteItem.style.display = '';
        deleteDivider.style.display = '';
    } else {
        deleteItem.style.display = 'none';
        deleteDivider.style.display = 'none';
    }

    var contextMenu = document.getElementById('sequence-menu');
    contextMenu.style.display = 'block';
    contextMenu.style.left = e.pageX + 'px';
    contextMenu.style.top = e.pageY + 'px';
}

// --- Mouse interaction handlers ---

// Guards against attaching the container listeners more than once. The
// listeners read the live svg on each event, so they survive re-renders and
// must NOT be re-added per render (doing so stacked stale-closure handlers
// that computed conflicting coordinates).
let lifelineInteractionAttached = false;

// Returns the current diagram svg element (replaced on every render).
function getLiveSequenceSvg() {
    const colb = document.getElementById('colb');
    return colb ? colb.querySelector('svg') : null;
}

function setupLifelineInteraction() {
    if (lifelineInteractionAttached) return;
    lifelineInteractionAttached = true;
    const container = document.getElementById('colb-container');

    // Mousemove: show indicator in normal mode, ghost arrow in message-add mode
    container.addEventListener('mousemove', (e) => {
        const svgContainer = getLiveSequenceSvg();
        if (!svgContainer || !svgContainer.getScreenCTM()) return;
        const transformed = svgPointFromEvent(e, svgContainer);
        const x = transformed.x;
        const y = transformed.y;

        if (isAddMessageActive) {
            const dest = findNearestLifeline(x, y, participantLifelines);
            if (dest) {
                showGhostArrow(svgContainer, messageOrigin.cx, dest.cx, y);
            } else {
                hideGhostArrow();
            }
            hideIndicatorCircle();
        } else if (isActivationAddMode()) {
            handleActivationMouseMove(svgContainer, y);
            hideIndicatorCircle();
        } else if (isGroupAddMode()) {
            handleGroupMouseMove(svgContainer, y);
            hideIndicatorCircle();
        } else {
            hideGhostArrow();
            const lifeline = findNearestLifeline(x, y, participantLifelines);
            if (lifeline) {
                showIndicatorCircle(svgContainer, lifeline.cx, y);
            } else {
                hideIndicatorCircle();
            }
        }
    });

    // Click: confirm destination and open label dialog
    container.addEventListener('click', (e) => {
        const svgContainer = getLiveSequenceSvg();
        if (!svgContainer || !svgContainer.getScreenCTM()) return;

        // Activation-add mode: confirm the bar end and open the end-type chooser.
        if (isActivationAddMode()) {
            const transformed = svgPointFromEvent(e, svgContainer);
            // Stop propagation so the global menu-dismiss handler does not
            // immediately hide the chooser we are about to show.
            e.stopPropagation();
            handleActivationClick(e, transformed.y);
            return;
        }

        // Group-add mode: click confirms the range from the locked right-click Y.
        if (isGroupAddMode()) {
            const transformed = svgPointFromEvent(e, svgContainer);
            e.stopPropagation();
            handleGroupClick(e, transformed.y);
            return;
        }

        if (!isAddMessageActive || !messageOrigin) return;

        const transformed = svgPointFromEvent(e, svgContainer);
        const x = transformed.x;
        const y = transformed.y;

        const dest = findNearestLifeline(x, y, participantLifelines);
        if (!dest) return;

        secondClickCoordinates = [dest.cx, y];
        firstClickCoordinates = [messageOrigin.cx, y];
        const originName = messageOrigin.name;

        cancelMessageAddMode();

        $('#participant-modalForm .modal-title').text(
            'Add message from ' + originName + ' to ' + dest.name);
        $('#participant-message-text').val("");
        $('#participant-modalForm').modal('show');
        $('#participant-modalForm').on('shown.bs.modal', function() {
            $('#participant-message-text').trigger('focus');
        });
    });
}

// --- Event listener registration ---

function messageEventListeners() {
    // "Add Message" context menu items enter message-add mode
    document.getElementById('addMessageSolid').addEventListener('click', () => {
        messageArrowType = '->';
        isAddMessageActive = true;
        hideIndicatorCircle();
        document.getElementById('sequence-menu').style.display = 'none';
    });

    document.getElementById('addMessageDashed').addEventListener('click', () => {
        messageArrowType = '-->';
        isAddMessageActive = true;
        hideIndicatorCircle();
        document.getElementById('sequence-menu').style.display = 'none';
    });

    // Submit button in the message label modal sends the message to backend
    $('#submit-participant-message').on('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');

        var newmessage = $('#participant-message-text').val();
        try {
            const plantuml = trimlines(editor.session.getValue());
            let response;
            if (messageEditMode) {
                messageEditMode = false;
                response = await fetch("editMessageText", {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        'plantuml': plantuml,
                        'svg': svg.innerHTML,
                        'svgelement': lastclickedsvgelement.outerHTML,
                        'text': newmessage
                    }),
                });
            } else {
                response = await fetch("addMessage", {
                    method: 'POST',
                    headers: {'Content-Type': 'application/json'},
                    body: JSON.stringify({
                        'plantuml': plantuml,
                        'svg': svg.innerHTML,
                        'message': newmessage,
                        'svgelement': lastclickedsvgelement.outerHTML,
                        'firstcoordinates': firstClickCoordinates,
                        'secondcoordinates': secondClickCoordinates,
                        'arrowtype': messageArrowType,
                    }),
                });
            }
            const data = await response.json();
            setPuml(data.plantuml)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    // Escape cancels message-add mode
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isAddMessageActive) {
            cancelMessageAddMode();
        }
    });
}
