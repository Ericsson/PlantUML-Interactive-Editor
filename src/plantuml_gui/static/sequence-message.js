let isAddMessageActive = false;
let firstClickCoordinates = null;
let secondClickCoordinates = null;
let messageOrigin = null;

let indicatorBox = null;
let ghostLine = null;
let ghostArrow = null;
let ghostSelfPath = null;

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
        indicatorBox = document.createElementNS('http://www.w3.org/2000/svg', 'circle');
        indicatorBox.setAttribute('r', '5');
        indicatorBox.setAttribute('fill', '#5b9bd5');
        indicatorBox.setAttribute('opacity', '0.7');
        indicatorBox.setAttribute('pointer-events', 'none');
    }
    indicatorBox.setAttribute('cx', cx);
    indicatorBox.setAttribute('cy', y);
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

    if (fromCx === toCx) {
        // Self-message: draw a loop going right, down, and back
        hideGhostLine();
        if (!ghostSelfPath) {
            ghostSelfPath = document.createElementNS('http://www.w3.org/2000/svg', 'polyline');
            ghostSelfPath.setAttribute('stroke', '#888');
            ghostSelfPath.setAttribute('stroke-width', '1.5');
            ghostSelfPath.setAttribute('stroke-dasharray', '4,4');
            ghostSelfPath.setAttribute('opacity', '0.7');
            ghostSelfPath.setAttribute('fill', 'none');
            ghostSelfPath.setAttribute('pointer-events', 'none');
        }
        const loopWidth = 30;
        const loopHeight = 20;
        ghostSelfPath.setAttribute('points',
            `${fromCx},${y} ${fromCx + loopWidth},${y} ${fromCx + loopWidth},${y + loopHeight} ${fromCx},${y + loopHeight}`);
        if (!ghostSelfPath.parentNode) g.appendChild(ghostSelfPath);

        // Arrowhead pointing left at the return
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

    // Normal message: straight line
    hideGhostSelfPath();
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

function cancelMessageAddMode() {
    isAddMessageActive = false;
    messageOrigin = null;
    hideGhostArrow();
}

function setupLifelineInteraction(svgContainer) {
    const container = document.getElementById('colb-container');

    container.addEventListener('mousemove', (e) => {
        if (!svgContainer || !svgContainer.getScreenCTM()) return;
        const transformed = svgPointFromEvent(e, svgContainer);
        const x = transformed.x;
        const y = transformed.y;

        if (isAddMessageActive) {
            const dest = findNearestLifeline(x, y);
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

        const dest = findNearestLifeline(x, y);
        if (!dest) return;

        // Store coordinates and show label dialog
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

function messageEventListeners() {
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

    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isAddMessageActive) {
            cancelMessageAddMode();
        }
    });
}
