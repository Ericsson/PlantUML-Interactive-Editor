// State for the add-activation interaction flow
let isAddActivationActive = false;
let activationOrigin = null; // {cx, name, startMessageIndex, startCy}
let activationEndMessage = null; // {index, cy}

// Message positions fetched from backend (refreshed each render)
let messagePositions = []; // [{cy, index, text}, ...]

// Reusable ghost bar overlay element (created once, moved on each frame)
let ghostActivationBar = null;

const ACTIVATION_BAR_WIDTH = 10;

// --- Message position management ---

async function fetchMessagePositions() {
    const element = document.getElementById('colb');
    const svg = element.querySelector('g');
    if (!svg) {
        messagePositions = [];
        return;
    }
    try {
        const plantuml = trimlines(editor.session.getValue());
        const response = await fetch("getMessagePositions", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({plantuml: plantuml, svg: svg.innerHTML})
        });
        const data = await response.json();
        messagePositions = data.positions;
    } catch (error) {
        messagePositions = [];
    }
}

function findNearestMessage(y) {
    if (messagePositions.length === 0) return null;
    let nearest = messagePositions[0];
    let minDist = Math.abs(y - nearest.cy);
    for (let i = 1; i < messagePositions.length; i++) {
        const dist = Math.abs(y - messagePositions[i].cy);
        if (dist < minDist) {
            minDist = dist;
            nearest = messagePositions[i];
        }
    }
    return nearest;
}

function findNearestMessageAtOrBelow(y, startCy) {
    // Find the nearest message whose cy >= startCy (so the bar can't go above start)
    let nearest = null;
    let minDist = Infinity;
    for (const msg of messagePositions) {
        if (msg.cy < startCy) continue;
        const dist = Math.abs(y - msg.cy);
        if (dist < minDist) {
            minDist = dist;
            nearest = msg;
        }
    }
    return nearest;
}

// --- Ghost activation bar (translucent preview rect on the lifeline) ---

function showGhostActivationBar(svgElement, cx, startCy, endCy) {
    const g = svgElement.querySelector('g');
    if (!g) return;

    if (!ghostActivationBar) {
        ghostActivationBar = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        ghostActivationBar.setAttribute('fill', '#b8cce4');
        ghostActivationBar.setAttribute('stroke', '#5b9bd5');
        ghostActivationBar.setAttribute('stroke-width', '1');
        ghostActivationBar.setAttribute('opacity', '0.7');
        ghostActivationBar.setAttribute('pointer-events', 'none');
    }
    const top = Math.min(startCy, endCy);
    const height = Math.max(Math.abs(endCy - startCy), 4); // minimum 4px height
    ghostActivationBar.setAttribute('x', cx - ACTIVATION_BAR_WIDTH / 2);
    ghostActivationBar.setAttribute('y', top);
    ghostActivationBar.setAttribute('width', ACTIVATION_BAR_WIDTH);
    ghostActivationBar.setAttribute('height', height);
    if (!ghostActivationBar.parentNode) g.appendChild(ghostActivationBar);
}

function hideGhostActivationBar() {
    if (ghostActivationBar && ghostActivationBar.parentNode) {
        ghostActivationBar.parentNode.removeChild(ghostActivationBar);
    }
}

// --- Activation-add mode lifecycle ---

function isActivationAddMode() {
    return isAddActivationActive;
}

function cancelActivationAddMode() {
    isAddActivationActive = false;
    activationOrigin = null;
    activationEndMessage = null;
    hideGhostActivationBar();
}

// --- Coordinator hooks (called from setupLifelineInteraction) ---

function handleActivationMouseMove(svgContainer, y) {
    if (!activationOrigin) return;

    // Snap end to nearest message at or below start
    const endMsg = findNearestMessageAtOrBelow(y, activationOrigin.startCy);
    if (!endMsg) return;

    showGhostActivationBar(
        svgContainer,
        activationOrigin.cx,
        activationOrigin.startCy,
        endMsg.cy
    );
}

function handleActivationClick(e, y) {
    if (!activationOrigin) return;

    // Snap to nearest message at or below start
    const endMsg = findNearestMessageAtOrBelow(y, activationOrigin.startCy);
    if (!endMsg) return;
    activationEndMessage = endMsg;
    isAddActivationActive = false;
    hideGhostActivationBar();

    const menu = document.getElementById('activation-end-menu');
    menu.style.display = 'block';
    menu.style.left = e.pageX + 'px';
    menu.style.top = e.pageY + 'px';
}

// --- Event listener registration (called from sequenceEventListeners) ---

function activationEventListeners() {
    // "Activate" context menu item enters activation-add mode.
    document.getElementById('seq-addActivation').addEventListener('click', () => {
        if (messagePositions.length === 0) return; // No messages to anchor to
        if (!messageOrigin || !firstClickCoordinates) return; // No lifeline context

        // Snap start to nearest message from the right-click Y
        const startMsg = findNearestMessage(firstClickCoordinates[1]);
        if (!startMsg) return;

        activationOrigin = {
            cx: messageOrigin.cx,
            name: messageOrigin.name,
            startMessageIndex: startMsg.index,
            startCy: startMsg.cy
        };
        isAddActivationActive = true;
        hideIndicatorCircle();
        document.getElementById('sequence-menu').style.display = 'none';
    });

    // Chooser items submit the activation with the chosen end type.
    document.getElementById('activation-deactivate').addEventListener('click', () => {
        submitActivation('deactivate');
    });
    document.getElementById('activation-destroy').addEventListener('click', () => {
        submitActivation('destroy');
    });

    // "Delete" on an existing bar removes its activate + close pair.
    document.getElementById('seq-deleteActivation').addEventListener('click', async () => {
        const element = document.getElementById('colb');
        const svg = element.querySelector('g');
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("deleteActivation", {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    plantuml: plantuml,
                    svg: svg.innerHTML,
                    svgelement: lastclickedsvgelement.outerHTML
                })
            });
            const data = await response.json();
            setPuml(data.plantuml);
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    // Escape cancels activation flow (both drag and end-type chooser).
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && (isAddActivationActive || activationOrigin)) {
            document.getElementById('activation-end-menu').style.display = 'none';
            cancelActivationAddMode();
        }
    });
}

async function submitActivation(endType) {
    document.getElementById('activation-end-menu').style.display = 'none';
    if (!activationOrigin || !activationEndMessage) return;

    const origin = activationOrigin;
    const endMsg = activationEndMessage;
    activationOrigin = null;
    activationEndMessage = null;

    try {
        const plantuml = trimlines(editor.session.getValue());
        const response = await fetch("addActivation", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                plantuml: plantuml,
                participant: origin.name,
                startMessageIndex: origin.startMessageIndex,
                endMessageIndex: endMsg.index,
                endType: endType
            })
        });
        const data = await response.json();
        if (data.error) {
            displayErrorMessage(data.error);
            return;
        }
        setPuml(data.plantuml);
    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }
}
