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
