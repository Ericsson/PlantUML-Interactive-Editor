// State for the add-activation interaction flow
let isAddActivationActive = false;
let activationOrigin = null; // {cx, name, startY}
let activationEndY = null;

// Reusable ghost bar overlay element (created once, moved on each frame)
let ghostActivationBar = null;

const ACTIVATION_BAR_WIDTH = 10;

// --- Ghost activation bar (translucent preview rect on the lifeline) ---

function showGhostActivationBar(svgElement, cx, startY, endY) {
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
    const top = Math.min(startY, endY);
    const height = Math.abs(endY - startY);
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
    activationEndY = null;
    hideGhostActivationBar();
}

// --- Coordinator hooks (called from setupLifelineInteraction) ---

// Stretch the ghost bar from the start Y down to the cursor Y on the origin lifeline.
function handleActivationMouseMove(svgContainer, y) {
    if (!activationOrigin) return;
    const endY = Math.max(y, activationOrigin.startY);
    showGhostActivationBar(svgContainer, activationOrigin.cx, activationOrigin.startY, endY);
}

// Confirm the end of the bar and open the Deactivate/Destroy chooser.
function handleActivationClick(e, y) {
    if (!activationOrigin) return;
    activationEndY = Math.max(y, activationOrigin.startY);
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
        cancelMessageAddMode();
        activationOrigin = {
            cx: messageOrigin.cx,
            name: messageOrigin.name,
            startY: firstClickCoordinates[1]
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

    // Escape cancels activation-add mode.
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isAddActivationActive) {
            cancelActivationAddMode();
        }
    });
}

async function submitActivation(endType) {
    document.getElementById('activation-end-menu').style.display = 'none';
    if (!activationOrigin || activationEndY === null) return;

    const element = document.getElementById('colb');
    const svg = element.querySelector('g');
    const origin = activationOrigin;
    const endY = activationEndY;
    activationOrigin = null;
    activationEndY = null;

    try {
        const plantuml = trimlines(editor.session.getValue());
        const response = await fetch("addActivation", {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                plantuml: plantuml,
                svg: svg.innerHTML,
                participant: origin.name,
                startY: origin.startY,
                endY: endY,
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
