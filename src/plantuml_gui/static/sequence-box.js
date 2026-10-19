// Sequence participant-box interaction: right-click a participant -> Box, then
// hover another participant to grow a horizontal ghost box across the range and
// click to create it. Mirrors sequence-group.js but operates horizontally over
// participants (by center-x) instead of vertically over messages.
//
// The add flow currently creates a bare `box` (no title/color prompt), so a
// click submits straight to /addBox with no modal.

// State for the add-box interaction flow
let isAddBoxActive = false;
let boxOrigin = null; // {startParticipantIndex, startCx}

// The box whose Edit/Delete Box menu item is currently actionable. Set by the
// lifeline (background) context menu when the right-click lands inside a box.
let contextBoxRect = null;

// Reusable ghost box overlay element (created once, moved on each frame)
let ghostBox = null;

// Padding around the participant headers for the ghost box
const BOX_PADDING = 8;

// --- Participant geometry helpers ---

// Nearest participant lifeline to an x coordinate (by center-x).
function findNearestParticipantByX(x) {
    let best = null;
    let bestDist = Infinity;
    for (const p of participantLifelines) {
        const dist = Math.abs(p.cx - x);
        if (dist < bestDist) {
            bestDist = dist;
            best = p;
        }
    }
    return best;
}

// Iterate participant header rects (rounded corners + the shared 0.5 stroke).
function forEachParticipantHeaderRect(svgElement, callback) {
    svgElement.querySelectorAll('rect').forEach((rect) => {
        const style = rect.getAttribute('style') || '';
        if (rect.hasAttribute('rx') && rect.hasAttribute('ry') &&
            style.includes('stroke-width:0.5')) {
            callback(rect);
        }
    });
}

// Vertical band the ghost box spans: from just above the top header row down to
// just below the bottom header row (PlantUML repeats participant headers at the
// bottom of the lifelines), so the ghost fully contains both header rows like
// the real box, rather than cutting through the lower headers.
function ghostVerticalExtent(svgElement) {
    let top = Infinity;
    let bottom = -Infinity;
    forEachParticipantHeaderRect(svgElement, (rect) => {
        const y = parseFloat(rect.getAttribute('y'));
        const h = parseFloat(rect.getAttribute('height'));
        top = Math.min(top, y);
        bottom = Math.max(bottom, y + h);
    });
    // Fall back to the lifeline extent if no header rects were found.
    if (!isFinite(top)) {
        top = 0;
        for (const p of participantLifelines) {
            bottom = Math.max(bottom, p.yBottom);
        }
    }
    if (!isFinite(bottom)) bottom = top;
    return {top: top - BOX_PADDING, bottom: bottom + BOX_PADDING};
}

// Horizontal extent bounding every participant whose center-x falls in
// [minCx, maxCx], using their header rects' left/right edges.
function ghostHorizontalExtent(svgElement, minCx, maxCx) {
    let left = Infinity;
    let right = -Infinity;
    forEachParticipantHeaderRect(svgElement, (rect) => {
        const x = parseFloat(rect.getAttribute('x'));
        const w = parseFloat(rect.getAttribute('width'));
        const cx = x + w / 2;
        if (cx >= minCx - 1 && cx <= maxCx + 1) {
            left = Math.min(left, x);
            right = Math.max(right, x + w);
        }
    });
    if (!isFinite(left)) {
        left = minCx;
        right = maxCx;
    }
    return {left: left - BOX_PADDING, right: right + BOX_PADDING};
}

// --- Ghost box rendering ---

function showGhostBox(svgElement, startCx, endCx) {
    const g = svgElement.querySelector('g');
    if (!g) return;

    if (!ghostBox) {
        ghostBox = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        ghostBox.setAttribute('fill', 'rgba(200, 200, 200, 0.3)');
        ghostBox.setAttribute('stroke', '#888');
        ghostBox.setAttribute('stroke-width', '1.5');
        ghostBox.setAttribute('stroke-dasharray', '5,3');
        ghostBox.setAttribute('pointer-events', 'none');
    }

    const minCx = Math.min(startCx, endCx);
    const maxCx = Math.max(startCx, endCx);
    const {left, right} = ghostHorizontalExtent(svgElement, minCx, maxCx);
    const {top, bottom} = ghostVerticalExtent(svgElement);

    ghostBox.setAttribute('x', left);
    ghostBox.setAttribute('y', top);
    ghostBox.setAttribute('width', right - left);
    ghostBox.setAttribute('height', bottom - top);
    if (!ghostBox.parentNode) g.appendChild(ghostBox);
}

function hideGhostBox() {
    if (ghostBox && ghostBox.parentNode) {
        ghostBox.parentNode.removeChild(ghostBox);
    }
}

// --- Box-add mode lifecycle ---

function isBoxAddMode() {
    return isAddBoxActive;
}

function cancelBoxAddMode() {
    isAddBoxActive = false;
    boxOrigin = null;
    hideGhostBox();
}

function getLiveBoxSvg() {
    if (typeof getLiveSequenceSvg === 'function') {
        return getLiveSequenceSvg();
    }
    const element = document.getElementById('colb');
    return element ? element.querySelector('svg') : null;
}

// Enter box-add mode anchored to the right-clicked participant. The clicked
// participant rect is in lastclickedsvgelement; its center-x maps to a lifeline
// (and thus the participant's puml line index).
function startBoxAddModeFromContext() {
    cancelBoxAddMode();

    if (!lastclickedsvgelement || participantLifelines.length === 0) return false;

    const x = parseFloat(lastclickedsvgelement.getAttribute('x'));
    const w = parseFloat(lastclickedsvgelement.getAttribute('width'));
    if (isNaN(x) || isNaN(w)) return false;
    const originCx = x + w / 2;

    const origin = participantLifelines.find((p) => Math.abs(p.cx - originCx) <= 1);
    if (!origin) return false;

    boxOrigin = {startParticipantIndex: origin.index, startCx: origin.cx};
    isAddBoxActive = true;

    const svgContainer = getLiveBoxSvg();
    if (svgContainer) {
        showGhostBox(svgContainer, origin.cx, origin.cx);
    }
    return true;
}

// --- Coordinator hooks (called from setupLifelineInteraction) ---

function handleBoxMouseMove(svgContainer, x) {
    if (!boxOrigin) return;
    const dest = findNearestParticipantByX(x);
    if (!dest) return;
    showGhostBox(svgContainer, boxOrigin.startCx, dest.cx);
}

function handleBoxClick(e, x) {
    if (!boxOrigin) return;

    const dest = findNearestParticipantByX(x);
    if (!dest) return;

    const startIndex = boxOrigin.startParticipantIndex;
    const endIndex = dest.index;

    cancelBoxAddMode();
    submitBox(startIndex, endIndex);
}

// POST the participant range to /addBox and apply the returned puml. No modal:
// the box is created bare (no title/color).
async function submitBox(startIndex, endIndex) {
    try {
        const plantuml = trimlines(editor.session.getValue());
        const response = await fetch('addBox', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                plantuml: plantuml,
                startParticipantIndex: startIndex,
                endParticipantIndex: endIndex,
            }),
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

// --- Event listener registration ---

function boxEventListeners() {
    // Submit button in the box edit modal
    $('#seq-submit-box').on('click', submitBoxEdit);

    // "Box" item in the participant context menu enters box-add mode.
    document.getElementById('seq-addBox').addEventListener('click', (e) => {
        e.preventDefault();
        e.stopPropagation();
        document.getElementById('participant-menu').style.display = 'none';
        startBoxAddModeFromContext();
    });

    // "Edit Box" in the box context menu opens the title/color modal.
    document.getElementById('seq-editBox').addEventListener('click', async () => {
        if (!contextBoxRect) return;
        const element = document.getElementById('colb');
        const svg = element.querySelector('g');
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch('getSeqBoxLabel', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    plantuml: plantuml,
                    svg: svg.innerHTML,
                    svgelement: contextBoxRect.outerHTML,
                }),
            });
            const data = await response.json();
            document.getElementById('seq-box-title-text').value = data.title || '';
            setColorSelect(document.getElementById('seq-box-color-select'), data.color);
            $('#seq-box-modalForm').modal('show');
            $('#seq-box-modalForm').on('shown.bs.modal', function () {
                $('#seq-box-title-text').trigger('focus');
            });
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    // "Delete Box" in the box context menu unwraps the clicked box.
    document.getElementById('seq-deleteBox').addEventListener('click', async () => {
        if (!contextBoxRect) return;
        const element = document.getElementById('colb');
        const svg = element.querySelector('g');
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch('deleteSeqBox', {
                method: 'POST',
                headers: {'Content-Type': 'application/json'},
                body: JSON.stringify({
                    plantuml: plantuml,
                    svg: svg.innerHTML,
                    svgelement: contextBoxRect.outerHTML,
                }),
            });
            const data = await response.json();
            setPuml(data.plantuml);
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    // Escape cancels box-add mode.
    document.addEventListener('keydown', (e) => {
        if (e.key === 'Escape' && isAddBoxActive) {
            cancelBoxAddMode();
        }
    });
}


// Global function called by onclick on the submit-box button. Sends the new
// title and color for the clicked box to /editSeqBox.
async function submitBoxEdit() {
    if (!contextBoxRect) return;
    const element = document.getElementById('colb');
    const svg = element.querySelector('g');
    const title = document.getElementById('seq-box-title-text').value;
    const color = document.getElementById('seq-box-color-select').value;

    try {
        const plantuml = trimlines(editor.session.getValue());
        const response = await fetch('editSeqBox', {
            method: 'POST',
            headers: {'Content-Type': 'application/json'},
            body: JSON.stringify({
                plantuml: plantuml,
                svg: svg.innerHTML,
                svgelement: contextBoxRect.outerHTML,
                title: title,
                color: color,
            }),
        });
        const data = await response.json();
        if (data.error) {
            displayErrorMessage(data.error);
            return;
        }
        $('#seq-box-modalForm').modal('hide');
        setPuml(data.plantuml);
    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }
}
