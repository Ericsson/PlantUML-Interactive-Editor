# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2026 Ericsson

"""End-to-end probes for sequence message hover and context-menu behavior."""


def _probe_message_interaction(page, mode):
    return page.evaluate(
        """(mode) => {
            isAddMessageActive = false;
            isAddActivationActive = false;
            isAddGroupActive = false;
            isAddNoteActive = false;
            lastclickedsvgelement = 'unchanged';
            document.getElementById('message-menu').style.display = 'none';

            if (mode === 'message') {
                isAddMessageActive = true;
            } else if (mode === 'activation') {
                isAddActivationActive = true;
            } else if (mode === 'group') {
                isAddGroupActive = true;
            } else if (mode === 'note') {
                isAddNoteActive = true;
            }

            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            const message = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            message.setAttribute('style', 'stroke:#181818;stroke-width:1.0;');
            svg.appendChild(message);
            setupMessageHandlers([message], svg);

            const initialState = {
                fontWeight: message.style.fontWeight,
                strokeWidth: message.style.strokeWidth
            };

            message.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            const hoverState = {
                fontWeight: message.style.fontWeight,
                strokeWidth: message.style.strokeWidth
            };

            message.dispatchEvent(new MouseEvent('contextmenu', {
                bubbles: true,
                cancelable: true,
                pageX: 10,
                pageY: 20
            }));

            const menuDisplay = document.getElementById('message-menu').style.display;
            const lastClickedChanged = lastclickedsvgelement === message;

            message.dispatchEvent(new MouseEvent('mouseout', {bubbles: true}));
            const afterMouseout = {
                fontWeight: message.style.fontWeight,
                strokeWidth: message.style.strokeWidth
            };

            isAddMessageActive = false;
            isAddActivationActive = false;
            isAddGroupActive = false;
            isAddNoteActive = false;

            return {
                sequenceAddMode: isSequenceAddMode(),
                initialState,
                hoverState,
                afterMouseout,
                menuDisplay,
                lastClickedChanged
            };
        }""",
        mode,
    )


class TestSequenceMessageInteractions:
    def test_normal_mode_enables_hover_and_context_menu(self, app_url, page):
        result = _probe_message_interaction(page, "normal")

        assert result["hoverState"]["fontWeight"] == "bold"
        assert result["hoverState"]["strokeWidth"] == "2"
        assert result["menuDisplay"] == "block"
        assert result["lastClickedChanged"] is True
        assert result["afterMouseout"]["fontWeight"] == ""
        assert result["afterMouseout"]["strokeWidth"] == ""

    def test_message_add_mode_disables_message_hover_and_context_menu(
        self, app_url, page
    ):
        result = _probe_message_interaction(page, "message")

        assert result["hoverState"] == result["initialState"]
        assert result["menuDisplay"] == "none"
        assert result["lastClickedChanged"] is False

    def test_activation_add_mode_disables_message_hover_and_context_menu(
        self, app_url, page
    ):
        result = _probe_message_interaction(page, "activation")

        assert result["hoverState"] == result["initialState"]
        assert result["menuDisplay"] == "none"
        assert result["lastClickedChanged"] is False

    def test_group_add_mode_disables_message_hover_and_context_menu(
        self, app_url, page
    ):
        result = _probe_message_interaction(page, "group")

        assert result["hoverState"] == result["initialState"]
        assert result["menuDisplay"] == "none"
        assert result["lastClickedChanged"] is False

    def test_note_add_mode_disables_message_hover_and_context_menu(self, app_url, page):
        result = _probe_message_interaction(page, "note")

        assert result["hoverState"] == result["initialState"]
        assert result["menuDisplay"] == "none"
        assert result["lastClickedChanged"] is False

    def test_context_menu_returns_after_add_mode_is_cancelled(self, app_url, page):
        result = page.evaluate("""() => {
            isAddMessageActive = true;
            lastclickedsvgelement = 'unchanged';
            document.getElementById('message-menu').style.display = 'none';

            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            const message = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            message.setAttribute('style', 'stroke:#181818;stroke-width:1.0;');
            svg.appendChild(message);
            setupMessageHandlers([message], svg);

            cancelMessageAddMode();
            message.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            message.dispatchEvent(new MouseEvent('contextmenu', {
                bubbles: true,
                cancelable: true,
                pageX: 10,
                pageY: 20
            }));

            return {
                fontWeight: message.style.fontWeight,
                strokeWidth: message.style.strokeWidth,
                menuDisplay: document.getElementById('message-menu').style.display,
                lastClickedChanged: lastclickedsvgelement === message
            };
        }""")

        assert result["fontWeight"] == "bold"
        assert result["strokeWidth"] == "2"
        assert result["menuDisplay"] == "block"
        assert result["lastClickedChanged"] is True


class TestSequenceGroupLockedY:
    def test_group_type_selection_immediately_locks_start_and_shows_ghost(
        self, app_url, page
    ):
        result = page.evaluate("""() => {
            groupOperationEventListeners();
            document.getElementById('colb').innerHTML =
                '<svg viewBox="0 0 300 200"><g></g></svg>';
            messagePositions = [
                {cy: 40, index: 3, text: 'm1'},
                {cy: 80, index: 4, text: 'm2'},
                {cy: 120, index: 5, text: 'm3'}
            ];
            firstClickCoordinates = [100, 76];
            messageOrigin = {cx: 100, y: 76, name: 'Alice'};
            cancelGroupAddMode();

            document.querySelector('#seq-group-type-menu [data-group-type="loop"]')
                .dispatchEvent(new MouseEvent('click', {bubbles: true, cancelable: true}));

            return {
                active: isAddGroupActive,
                origin: groupOrigin,
                type: selectedGroupType,
                ghostAttached: Boolean(ghostGroupBox && ghostGroupBox.parentNode),
                ghostY: ghostGroupBox && ghostGroupBox.getAttribute('y'),
                ghostHeight: ghostGroupBox && ghostGroupBox.getAttribute('height')
            };
        }""")

        assert result["active"] is True
        assert result["origin"] == {"startMessageIndex": 4, "startCy": 80}
        assert result["type"] == "loop"
        assert result["ghostAttached"] is True
        assert result["ghostY"] == "70"
        assert result["ghostHeight"] == "20"

    def test_group_mousemove_keeps_start_locked_and_updates_current_end(
        self, app_url, page
    ):
        result = page.evaluate("""() => {
            document.getElementById('colb').innerHTML =
                '<svg viewBox="0 0 300 200"><g></g></svg>';
            const svg = document.querySelector('#colb svg');
            messagePositions = [
                {cy: 40, index: 3, text: 'm1'},
                {cy: 80, index: 4, text: 'm2'},
                {cy: 120, index: 5, text: 'm3'}
            ];
            firstClickCoordinates = [100, 76];
            messageOrigin = {cx: 100, y: 76, name: 'Alice'};
            cancelGroupAddMode();
            startGroupAddModeFromContext('alt');

            handleGroupMouseMove(svg, 122);
            const expanded = {
                origin: groupOrigin,
                y: ghostGroupBox.getAttribute('y'),
                height: ghostGroupBox.getAttribute('height')
            };

            handleGroupMouseMove(svg, 42);
            const shrunkBack = {
                origin: groupOrigin,
                y: ghostGroupBox.getAttribute('y'),
                height: ghostGroupBox.getAttribute('height')
            };
            cancelGroupAddMode();
            return {expanded, shrunkBack};
        }""")

        assert result["expanded"]["origin"] == {"startMessageIndex": 4, "startCy": 80}
        assert result["expanded"]["y"] == "70"
        assert result["expanded"]["height"] == "60"
        assert result["shrunkBack"]["origin"] == {"startMessageIndex": 4, "startCy": 80}
        assert result["shrunkBack"]["y"] == "30"
        assert result["shrunkBack"]["height"] == "60"

    def test_group_click_confirms_current_range_and_opens_label_modal(
        self, app_url, page
    ):
        result = page.evaluate("""() => {
            document.getElementById('colb').innerHTML =
                '<svg viewBox="0 0 300 200"><g></g></svg>';
            messagePositions = [
                {cy: 40, index: 3, text: 'm1'},
                {cy: 80, index: 4, text: 'm2'},
                {cy: 120, index: 5, text: 'm3'}
            ];
            firstClickCoordinates = [100, 76];
            messageOrigin = {cx: 100, y: 76, name: 'Alice'};
            cancelGroupAddMode();
            startGroupAddModeFromContext('alt');

            handleGroupClick(new MouseEvent('click'), 122);
            const submit = document.getElementById('seq-submit-group');
            const state = {
                active: isAddGroupActive,
                origin: groupOrigin,
                ghostAttached: Boolean(ghostGroupBox && ghostGroupBox.parentNode),
                title: document.querySelector('#seq-group-modalForm .modal-title').textContent,
                startIndex: submit.dataset.startIndex,
                endIndex: submit.dataset.endIndex,
                type: selectedGroupType
            };
            $('#seq-group-modalForm').modal('hide');
            selectedGroupType = '';
            return state;
        }""")

        assert result["active"] is False
        assert result["origin"] is None
        assert result["ghostAttached"] is False
        assert result["title"] == "Add alt"
        assert result["startIndex"] == "4"
        assert result["endIndex"] == "5"
        assert result["type"] == "alt"

    def test_escape_clears_group_add_mode_and_ghost(self, app_url, page):
        result = page.evaluate("""() => {
            groupOperationEventListeners();
            document.getElementById('colb').innerHTML =
                '<svg viewBox="0 0 300 200"><g></g></svg>';
            messagePositions = [{cy: 80, index: 4, text: 'm2'}];
            firstClickCoordinates = [100, 76];
            messageOrigin = {cx: 100, y: 76, name: 'Alice'};
            cancelGroupAddMode();
            startGroupAddModeFromContext('group');

            document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));

            return {
                active: isAddGroupActive,
                origin: groupOrigin,
                type: selectedGroupType,
                ghostAttached: Boolean(ghostGroupBox && ghostGroupBox.parentNode)
            };
        }""")

        assert result["active"] is False
        assert result["origin"] is None
        assert result["type"] == ""
        assert result["ghostAttached"] is False

    def test_group_type_selection_without_context_does_not_enter_add_mode(
        self, app_url, page
    ):
        result = page.evaluate("""() => {
            document.getElementById('colb').innerHTML =
                '<svg viewBox="0 0 300 200"><g></g></svg>';
            messagePositions = [{cy: 80, index: 4, text: 'm2'}];
            firstClickCoordinates = null;
            messageOrigin = null;
            cancelGroupAddMode();

            const started = startGroupAddModeFromContext('opt');

            return {
                started: started,
                active: isAddGroupActive,
                origin: groupOrigin,
                type: selectedGroupType,
                ghostAttached: Boolean(ghostGroupBox && ghostGroupBox.parentNode)
            };
        }""")

        assert result["started"] is False
        assert result["active"] is False
        assert result["origin"] is None
        assert result["type"] == ""
        assert result["ghostAttached"] is False
