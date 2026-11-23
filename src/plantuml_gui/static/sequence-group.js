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
    groupModalMode = 'add';
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

// --- Else-add mode: a dashed ghost line inside the clicked group snaps to the
// group's else slots (from the backend's elseSlots); a click picks one and
// opens the group label modal. ---

let isAddElseActive = false;
let elseTarget = null; // {groupRect, slots: [{lineIndex, y}]}
let pendingElse = null; // {groupRect, beforeLineIndex}, kept for submitGroup
let ghostElseLine = null;

// Height of a group header tab when it can't be measured.
const GROUP_TAB_FALLBACK_HEIGHT = 17;

function isElseAddMode() {
    return isAddElseActive;
}

function cancelElseAddMode() {
    isAddElseActive = false;
    elseTarget = null;
    hideGhostElseLine();
}

// Bottom edge of the group's header tab, the topmost y a branch can start at.
function groupContentTop(groupRect) {
    const tab = groupRect.previousElementSibling;
    if (tab && tab.tagName.toLowerCase() === 'path' && tab.getBBox) {
        const box = tab.getBBox();
        if (box.height > 0) return box.y + box.height;
    }
    return parseFloat(groupRect.getAttribute('y')) + GROUP_TAB_FALLBACK_HEIGHT;
}

// Y for each else slot: midway between the slot's line and whatever is drawn
// just above it inside the group (the previous message, or the header tab).
// A message slot sits at that message's cy, the 'end' slot at the box bottom.
// Messages of nested groups count as "above" too, so the line is drawn below
// a nested group's last message rather than above it.
function computeElseSlotYs(groupRect, group, messages) {
    const top = groupContentTop(groupRect);
    const bottom = parseFloat(groupRect.getAttribute('y')) +
        parseFloat(groupRect.getAttribute('height'));
    const inGroup = messages
        .filter((m) => m.index > group.headerIndex && m.index < group.endIndex)
        .sort((a, b) => a.index - b.index);
    return group.elseSlots.map((lineIndex) => {
        const own = inGroup.find((m) => m.index === lineIndex);
        const slotY = own ? own.cy : bottom;
        const above = inGroup.filter((m) => m.index < lineIndex);
        const aboveY = above.length ? above[above.length - 1].cy : top;
        return {lineIndex: lineIndex, y: (aboveY + slotY) / 2};
    });
}

function nearestElseSlot(y) {
    if (!elseTarget || elseTarget.slots.length === 0) return null;
    return elseTarget.slots.reduce((best, slot) =>
        Math.abs(slot.y - y) < Math.abs(best.y - y) ? slot : best);
}

function showGhostElseLine(svgElement, groupRect, y) {
    const g = svgElement.querySelector('g');
    if (!g) return;
    if (!ghostElseLine) {
        ghostElseLine = document.createElementNS('http://www.w3.org/2000/svg', 'line');
        ghostElseLine.setAttribute('stroke', '#888');
        ghostElseLine.setAttribute('stroke-width', '1.5');
        ghostElseLine.setAttribute('stroke-dasharray', '5,3');
        ghostElseLine.setAttribute('pointer-events', 'none');
    }
    const x = parseFloat(groupRect.getAttribute('x'));
    ghostElseLine.setAttribute('x1', x);
    ghostElseLine.setAttribute('x2', x + parseFloat(groupRect.getAttribute('width')));
    ghostElseLine.setAttribute('y1', y);
    ghostElseLine.setAttribute('y2', y);
    if (!ghostElseLine.parentNode) g.appendChild(ghostElseLine);
}

function hideGhostElseLine() {
    if (ghostElseLine && ghostElseLine.parentNode) {
        ghostElseLine.parentNode.removeChild(ghostElseLine);
    }
}

// Entered from the group context menu's "Add else" item.
function startElseAddMode(groupRect, group) {
    cancelElseAddMode();
    if (!groupRect || !group || !group.elseSlots || group.elseSlots.length === 0) {
        return false;
    }
    elseTarget = {
        groupRect: groupRect,
        slots: computeElseSlotYs(groupRect, group, messagePositions)
    };
    isAddElseActive = true;
    hideIndicatorCircle();
    const svgContainer = getLiveGroupSvg();
    if (svgContainer) {
        showGhostElseLine(svgContainer, groupRect, elseTarget.slots[0].y);
    }
    return true;
}

// Coordinator hooks (called from setupLifelineInteraction in sequence-message.js)

function handleElseMouseMove(svgContainer, y) {
    const slot = nearestElseSlot(y);
    if (slot) showGhostElseLine(svgContainer, elseTarget.groupRect, slot.y);
}

function handleElseClick(e, y) {
    const slot = nearestElseSlot(y);
    if (!slot) return;
    pendingElse = {groupRect: elseTarget.groupRect, beforeLineIndex: slot.lineIndex};
    cancelElseAddMode();

    groupModalMode = 'else';
    document.querySelector('#seq-group-modalForm .modal-title').textContent = 'Add else';
    document.getElementById('seq-group-label-text').value = '';
    $('#seq-group-modalForm').modal('show');
    $('#seq-group-modalForm').on('shown.bs.modal', function () {
        $('#seq-group-label-text').trigger('focus');
    });
}

// Route and body for the group modal's submit, by groupModalMode.
function groupRequest(plantuml, svg, label) {
    if (groupModalMode === 'rename') {
        return ['renameSeqGroup', {
            page: currentPage,
            plantuml: plantuml,
            svg: svg.innerHTML,
            svgelement: lastclickedsvgelement.outerHTML,
            label: label
        }];
    }
    if (groupModalMode === 'else') {
        return ['addSeqElse', {
            page: currentPage,
            plantuml: plantuml,
            svg: svg.innerHTML,
            svgelement: pendingElse.groupRect.outerHTML,
            beforeLineIndex: pendingElse.beforeLineIndex,
            label: label
        }];
    }
    var submitBtn = document.getElementById('seq-submit-group');
    return ['addGroup', {
        plantuml: plantuml,
        groupType: selectedGroupType,
        label: label,
        startMessageIndex: parseInt(submitBtn.dataset.startIndex, 10),
        endMessageIndex: parseInt(submitBtn.dataset.endIndex, 10)
    }];
}

// Global function called by onclick on the submit-group button.
// The modal is shared by add group, rename group and add else (groupModalMode).
async function submitGroup() {
    var label = document.getElementById('seq-group-label-text').value;

    var element = document.getElementById('colb');
    var svg = element.querySelector('g');

    try {
        var plantuml = trimlines(editor.session.getValue());
        var [route, body] = groupRequest(plantuml, svg, label);
        var response = await fetch(route, {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(body)
        });
        var data = await response.json();
        if (data.error) {
            // The modal stays open; keep its state so Submit retries the
            // same request.
            displayErrorMessage(data.error);
            return;
        }
        groupModalMode = 'add';
        pendingElse = null;
        $('#seq-group-modalForm').modal('hide');
        setPuml(data.plantuml);
    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }
    selectedGroupType = '';
}
