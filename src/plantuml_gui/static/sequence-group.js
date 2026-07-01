// State for the add-group interaction flow
let isAddGroupActive = false;
let groupOrigin = null; // {startMessageIndex, startCy}
let selectedGroupType = '';

// Reusable ghost box overlay element (created once, moved on each frame)
let ghostGroupBox = null;

// Padding above/below messages for the ghost box
const GROUP_BOX_PADDING = 25;

// --- Ghost box rendering ---

function showGhostGroupBox(svgElement, startCy, endCy) {
    const g = svgElement.querySelector('g');
    if (!g) return;

    if (!ghostGroupBox) {
        ghostGroupBox = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        ghostGroupBox.setAttribute('fill', 'rgba(200, 200, 200, 0.3)');
        ghostGroupBox.setAttribute('stroke', '#888');
        ghostGroupBox.setAttribute('stroke-width', '1.5');
        ghostGroupBox.setAttribute('stroke-dasharray', '5,3');
        ghostGroupBox.setAttribute('pointer-events', 'none');
    }

    const top = Math.min(startCy, endCy) - GROUP_BOX_PADDING;
    const bottom = Math.max(startCy, endCy) + GROUP_BOX_PADDING;
    const height = bottom - top;

    // Span a reasonable width across the diagram (use SVG viewBox or a fixed width)
    const viewBox = svgElement.getAttribute('viewBox');
    let boxX = 10;
    let boxWidth = 200;
    if (viewBox) {
        const parts = viewBox.split(/[\s,]+/);
        boxX = parseFloat(parts[0]) + 5;
        boxWidth = parseFloat(parts[2]) - 10;
    } else {
        const svgWidth = svgElement.getBBox ? svgElement.getBBox().width : 300;
        boxX = 5;
        boxWidth = svgWidth - 10;
    }

    ghostGroupBox.setAttribute('x', boxX);
    ghostGroupBox.setAttribute('y', top);
    ghostGroupBox.setAttribute('width', boxWidth);
    ghostGroupBox.setAttribute('height', height);
    if (!ghostGroupBox.parentNode) g.appendChild(ghostGroupBox);
}

function hideGhostGroupBox() {
    if (ghostGroupBox && ghostGroupBox.parentNode) {
        ghostGroupBox.parentNode.removeChild(ghostGroupBox);
    }
}

// --- Group-add mode lifecycle ---

function isGroupAddMode() {
    return isAddGroupActive;
}

function cancelGroupAddMode() {
    isAddGroupActive = false;
    groupOrigin = null;
    selectedGroupType = '';
    hideGhostGroupBox();
}

function getLiveGroupSvg() {
    if (typeof getLiveSequenceSvg === 'function') {
        return getLiveSequenceSvg();
    }
    const element = document.getElementById('colb');
    return element ? element.querySelector('svg') : null;
}

function startGroupAddModeFromContext(groupType) {
    cancelGroupAddMode();

    if (messagePositions.length === 0) return false;
    if (!messageOrigin || !firstClickCoordinates) return false;

    const startMsg = findNearestMessage(firstClickCoordinates[1]);
    if (!startMsg) return false;

    selectedGroupType = groupType;
    groupOrigin = {
        startMessageIndex: startMsg.index,
        startCy: startMsg.cy
    };
    isAddGroupActive = true;
    hideIndicatorCircle();

    const svgContainer = getLiveGroupSvg();
    if (svgContainer) {
        showGhostGroupBox(svgContainer, startMsg.cy, startMsg.cy);
    }
    return true;
}

// --- Coordinator hooks (called from setupLifelineInteraction in sequence-message.js) ---

function handleGroupMouseMove(svgContainer, y) {
    if (!groupOrigin) return;

    // Snap to nearest message
    const msg = findNearestMessage(y);
    if (!msg) return;

    showGhostGroupBox(svgContainer, groupOrigin.startCy, msg.cy);
}

function handleGroupClick(e, y) {
    if (!groupOrigin) return;

    // Confirm the locked-start range and show the label modal.
    const endMsg = findNearestMessage(y);
    if (!endMsg) return;

    const startIndex = groupOrigin.startMessageIndex;
    const endIndex = endMsg.index;

    // Reset interaction state
    isAddGroupActive = false;
    hideGhostGroupBox();

    // Store for submission
    groupOrigin = null;

    // Show the label modal
    document.querySelector('#seq-group-modalForm .modal-title').textContent =
        'Add ' + selectedGroupType;
    document.getElementById('seq-group-label-text').value = '';
    $('#seq-group-modalForm').modal('show');
    $('#seq-group-modalForm').on('shown.bs.modal', function () {
        $('#seq-group-label-text').trigger('focus');
    });

    // Store indexes for submission
    document.getElementById('seq-submit-group').dataset.startIndex = startIndex;
    document.getElementById('seq-submit-group').dataset.endIndex = endIndex;
}

// Global function called by onclick on the submit-group button
async function submitGroup() {
    var label = document.getElementById('seq-group-label-text').value;
    var submitBtn = document.getElementById('seq-submit-group');
    var startIndex = parseInt(submitBtn.dataset.startIndex, 10);
    var endIndex = parseInt(submitBtn.dataset.endIndex, 10);

    var element = document.getElementById('colb');
    var svg = element.querySelector('g');

    try {
        var plantuml = trimlines(editor.session.getValue());
        var response = await fetch("addGroup", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                plantuml: plantuml,
                groupType: selectedGroupType,
                label: label,
                startMessageIndex: startIndex,
                endMessageIndex: endIndex
            })
        });
        var data = await response.json();
        if (data.error) {
            displayErrorMessage(data.error);
            return;
        }
        $('#seq-group-modalForm').modal('hide');
        setPuml(data.plantuml);
    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }
    selectedGroupType = '';
}
