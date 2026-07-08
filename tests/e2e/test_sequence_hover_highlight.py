# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2026 Ericsson

"""End-to-end probes for two-way hover highlighting in sequence diagrams:
hovering a diagram element marks the matching editor line, and moving the
cursor/mouse onto an editor line highlights the matching diagram element."""

HOVER_MARKER_HELPERS = """
    function hoverMarkers() {
        const markers = editor.session.getMarkers() || {};
        return Object.values(markers)
            .filter(m => m.clazz === 'hover')
            .map(m => ({start: m.range.start.row, end: m.range.end.row}));
    }
    function resetAddModes() {
        isAddMessageActive = false;
        isAddActivationActive = false;
        isAddGroupActive = false;
        isAddNoteActive = false;
    }
"""


class TestSvgToEditorMarkers:
    def test_message_hover_marks_its_editor_line(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            clearMarkers();
            messagePositions = [
                {cy: 40, index: 3, text: 'm1'},
                {cy: 80, index: 4, text: 'm2'}
            ];
            sequenceHighlighted = [];

            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            const message = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            message.setAttribute('style', 'stroke:#181818;stroke-width:1.0;');
            message.setAttribute('y1', '80');
            svg.appendChild(message);
            setupMessageHandlers([message], svg);

            message.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            const duringHover = hoverMarkers();
            message.dispatchEvent(new MouseEvent('mouseout', {bubbles: true}));
            const afterMouseout = hoverMarkers();

            return {duringHover, afterMouseout};
        }"""
        )

        assert result["duringHover"] == [{"start": 4, "end": 4}]
        assert result["afterMouseout"] == []

    def test_message_hover_in_add_mode_sets_no_marker(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            clearMarkers();
            isAddMessageActive = true;
            messagePositions = [{cy: 40, index: 3, text: 'm1'}];

            const svg = document.createElementNS('http://www.w3.org/2000/svg', 'svg');
            const message = document.createElementNS('http://www.w3.org/2000/svg', 'line');
            message.setAttribute('style', 'stroke:#181818;stroke-width:1.0;');
            message.setAttribute('y1', '40');
            svg.appendChild(message);
            setupMessageHandlers([message], svg);

            message.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            const duringHover = hoverMarkers();
            resetAddModes();
            return {duringHover};
        }"""
        )

        assert result["duringHover"] == []

    def test_participant_hover_marks_its_editor_line(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            clearMarkers();
            participantLifelines = [{name: 'Alice', cx: 50, yTop: 0, yBottom: 100, index: 2}];
            sequenceHighlighted = [];
            const colb = document.getElementById('colb');
            colb.innerHTML = '<svg><g></g></svg>';

            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('style', 'stroke:#181818;stroke-width:0.5;');
            rect.setAttribute('x', '25');
            rect.setAttribute('width', '50');
            rect.setAttribute('fill', '#E2E2F0');
            colb.querySelector('g').appendChild(rect);
            setupParticipantHandlers([rect], colb.querySelector('g'), colb);

            rect.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            const duringHover = {
                markers: hoverMarkers(),
                fill: rect.getAttribute('fill')
            };
            rect.dispatchEvent(new MouseEvent('mouseout', {bubbles: true}));
            const afterMouseout = {
                markers: hoverMarkers(),
                fill: rect.getAttribute('fill')
            };
            return {duringHover, afterMouseout};
        }"""
        )

        assert result["duringHover"]["markers"] == [{"start": 2, "end": 2}]
        assert result["duringHover"]["fill"] == "#d8d8d8"
        assert result["afterMouseout"]["markers"] == []
        assert result["afterMouseout"]["fill"] == "#E2E2F0"

    def test_implicit_participant_hover_sets_no_marker(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            clearMarkers();
            participantLifelines = [{name: 'Alice', cx: 50, yTop: 0, yBottom: 100, index: -1}];
            sequenceHighlighted = [];
            const colb = document.getElementById('colb');
            colb.innerHTML = '<svg><g></g></svg>';

            const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            rect.setAttribute('style', 'stroke:#181818;stroke-width:0.5;');
            rect.setAttribute('x', '25');
            rect.setAttribute('width', '50');
            rect.setAttribute('fill', '#E2E2F0');
            colb.querySelector('g').appendChild(rect);
            setupParticipantHandlers([rect], colb.querySelector('g'), colb);

            rect.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            return {markers: hoverMarkers()};
        }"""
        )

        assert result["markers"] == []

    def test_note_hover_marks_its_editor_line(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            clearMarkers();
            notePositions = [{cy: 40, index: 4}];
            sequenceHighlighted = [];

            const body = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            body.setAttribute('fill', '#FEFFDD');
            const fold = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            fold.setAttribute('fill', '#FEFFDD');
            setupNoteHandlers([body, fold]);

            body.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            const duringHover = {
                markers: hoverMarkers(),
                fill: body.getAttribute('fill')
            };
            body.dispatchEvent(new MouseEvent('mouseout', {bubbles: true}));
            const afterMouseout = {
                markers: hoverMarkers(),
                fill: body.getAttribute('fill')
            };
            return {duringHover, afterMouseout};
        }"""
        )

        assert result["duringHover"]["markers"] == [{"start": 4, "end": 4}]
        assert result["duringHover"]["fill"] == "#d8d8d8"
        assert result["afterMouseout"]["markers"] == []
        assert result["afterMouseout"]["fill"] == "#FEFFDD"

    def test_second_note_maps_to_second_position(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            clearMarkers();
            notePositions = [{cy: 40, index: 3}, {cy: 90, index: 5}];
            sequenceHighlighted = [];

            const paths = [];
            for (let i = 0; i < 4; i++) {
                const p = document.createElementNS('http://www.w3.org/2000/svg', 'path');
                p.setAttribute('fill', '#FEFFDD');
                paths.push(p);
            }
            setupNoteHandlers(paths);

            paths[2].dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            const markers = hoverMarkers();
            paths[2].dispatchEvent(new MouseEvent('mouseout', {bubbles: true}));
            return {markers};
        }"""
        )

        assert result["markers"] == [{"start": 5, "end": 5}]

    def test_group_header_hover_marks_header_to_end_range(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            clearMarkers();
            groupPositions = [{headerIndex: 3, endIndex: 8}];
            sequenceHighlighted = [];

            const tab = document.createElementNS('http://www.w3.org/2000/svg', 'path');
            tab.setAttribute('fill', '#EEEEEE');
            const box = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
            box.setAttribute('fill', 'none');
            const label = document.createElementNS('http://www.w3.org/2000/svg', 'text');
            label.setAttribute('font-weight', 'bold');
            label.setAttribute('font-size', '13');
            setupGroupHandlers([tab, box, label]);

            tab.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            const tabHover = hoverMarkers();
            tab.dispatchEvent(new MouseEvent('mouseout', {bubbles: true}));

            label.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            const labelHover = hoverMarkers();
            label.dispatchEvent(new MouseEvent('mouseout', {bubbles: true}));
            const afterMouseout = hoverMarkers();

            return {tabHover, labelHover, afterMouseout};
        }"""
        )

        assert result["tabHover"] == [{"start": 3, "end": 8}]
        assert result["labelHover"] == [{"start": 3, "end": 8}]
        assert result["afterMouseout"] == []


class TestEditorToSvgHighlight:
    def test_message_row_bolds_its_svg_elements(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            messagePositions = [
                {cy: 40, index: 3, text: 'm1'},
                {cy: 80, index: 4, text: 'm2'}
            ];
            sequenceHighlighted = [];
            const colb = document.getElementById('colb');
            colb.innerHTML = '<svg><g>' +
                '<polygon fill="#181818" points="70,38,80,42,70,46" style="stroke:#181818;stroke-width:1.0;"></polygon>' +
                '<line style="stroke:#181818;stroke-width:1.0;" x1="25" x2="76" y1="40" y2="40"></line>' +
                '<text font-size="13" x="32" y="36">m1</text>' +
                '<line style="stroke:#181818;stroke-width:1.0;" x1="25" x2="76" y1="80" y2="80"></line>' +
                '<text font-size="13" x="32" y="76">m2</text>' +
                '</g></svg>';
            const els = colb.querySelectorAll('g *');
            sequenceRowMap = new Map();
            setupMessageHandlers(els, colb.querySelector('g'));

            highlightSequenceForRow(3);
            const highlighted = Array.from(els).map(el => el.style.fontWeight === 'bold');
            resetSequenceHighlight();
            const afterReset = Array.from(els).map(el => el.style.fontWeight === 'bold');

            return {highlighted, afterReset};
        }"""
        )

        # Only the three elements of message m1 (row 3) are bolded
        assert result["highlighted"] == [True, True, True, False, False]
        assert result["afterReset"] == [False, False, False, False, False]

    def test_participant_row_recolors_header_rects(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            messagePositions = [];
            participantLifelines = [{name: 'Alice', cx: 50, yTop: 0, yBottom: 100, index: 2}];
            sequenceHighlighted = [];
            const colb = document.getElementById('colb');
            colb.innerHTML = '<svg><g>' +
                '<rect fill="#E2E2F0" style="stroke:#181818;stroke-width:0.5;" x="25" width="50" y="5"></rect>' +
                '<rect fill="#E2E2F0" style="stroke:#181818;stroke-width:0.5;" x="25" width="50" y="120"></rect>' +
                '<rect fill="#E2E2F0" style="stroke:#181818;stroke-width:0.5;" x="100" width="50" y="5"></rect>' +
                '</g></svg>';
            const rects = colb.querySelectorAll('rect');
            sequenceRowMap = new Map();
            setupParticipantHandlers(colb.querySelectorAll('g *'), colb.querySelector('g'), colb);

            highlightSequenceForRow(2);
            const highlighted = Array.from(rects).map(r => r.getAttribute('fill'));
            resetSequenceHighlight();
            const afterReset = Array.from(rects).map(r => r.getAttribute('fill'));

            return {highlighted, afterReset};
        }"""
        )

        # Both header rects of Alice (top and bottom) recolored, other participant untouched
        assert result["highlighted"] == ["#d8d8d8", "#d8d8d8", "#E2E2F0"]
        assert result["afterReset"] == ["#E2E2F0", "#E2E2F0", "#E2E2F0"]

    def test_group_header_and_end_rows_thicken_box_and_tab(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            messagePositions = [];
            participantLifelines = [];
            notePositions = [];
            groupPositions = [{headerIndex: 3, endIndex: 8}];
            sequenceHighlighted = [];
            const colb = document.getElementById('colb');
            colb.innerHTML = '<svg><g>' +
                '<path fill="#EEEEEE" d="M0,0"></path>' +
                '<rect fill="none" style="stroke:#000000;stroke-width:1.5;" x="10" y="10" width="100" height="50"></rect>' +
                '</g></svg>';
            const tab = colb.querySelector('path');
            const box = colb.querySelector('rect');
            sequenceRowMap = new Map();
            setupGroupHandlers(colb.querySelectorAll('g *'));

            highlightSequenceForRow(3);
            const headerRow = {box: box.style.strokeWidth, tab: tab.style.strokeWidth};
            resetSequenceHighlight();

            highlightSequenceForRow(8);
            const endRow = {box: box.style.strokeWidth, tab: tab.style.strokeWidth};
            resetSequenceHighlight();
            const afterReset = {box: box.style.strokeWidth, tab: tab.style.strokeWidth};

            return {headerRow, endRow, afterReset};
        }"""
        )

        assert result["headerRow"] == {"box": "2", "tab": "2"}
        assert result["endRow"] == {"box": "2", "tab": "2"}
        # Reset restores the original style attributes: the box had
        # stroke-width:1.5 in its style, the tab had no style attribute
        assert result["afterReset"] == {"box": "1.5", "tab": ""}

    def test_note_row_recolors_note_body(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            messagePositions = [];
            participantLifelines = [];
            groupPositions = [];
            notePositions = [{cy: 40, index: 4}];
            sequenceHighlighted = [];
            const colb = document.getElementById('colb');
            colb.innerHTML = '<svg><g>' +
                '<path fill="#FEFFDD" d="M0,0"></path>' +
                '<path fill="#FEFFDD" d="M1,1"></path>' +
                '</g></svg>';
            const paths = colb.querySelectorAll('path');
            sequenceRowMap = new Map();
            setupNoteHandlers(colb.querySelectorAll('g *'));

            highlightSequenceForRow(4);
            const highlighted = Array.from(paths).map(p => p.getAttribute('fill'));
            resetSequenceHighlight();
            const afterReset = Array.from(paths).map(p => p.getAttribute('fill'));

            return {highlighted, afterReset};
        }"""
        )

        assert result["highlighted"] == ["#d8d8d8", "#d8d8d8"]
        assert result["afterReset"] == ["#FEFFDD", "#FEFFDD"]

    def test_unmapped_row_highlights_nothing(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            messagePositions = [{cy: 40, index: 3, text: 'm1'}];
            participantLifelines = [];
            notePositions = [];
            groupPositions = [];
            sequenceHighlighted = [];
            const colb = document.getElementById('colb');
            colb.innerHTML = '<svg><g>' +
                '<line style="stroke:#181818;stroke-width:1.0;" x1="25" x2="76" y1="40" y2="40"></line>' +
                '</g></svg>';

            highlightSequenceForRow(0); // @startuml row
            return {count: sequenceHighlighted.length};
        }"""
        )

        assert result["count"] == 0

    def test_add_mode_disables_editor_highlight(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            isAddMessageActive = true;
            messagePositions = [{cy: 40, index: 3, text: 'm1'}];
            sequenceHighlighted = [];
            const colb = document.getElementById('colb');
            colb.innerHTML = '<svg><g>' +
                '<line style="stroke:#181818;stroke-width:1.0;" x1="25" x2="76" y1="40" y2="40"></line>' +
                '</g></svg>';

            highlightSequenceForRow(3);
            const count = sequenceHighlighted.length;
            resetAddModes();
            return {count};
        }"""
        )

        assert result["count"] == 0

    def test_mouseout_keeps_editor_side_highlight(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            messagePositions = [{cy: 40, index: 3, text: 'm1'}];
            sequenceHighlighted = [];
            const colb = document.getElementById('colb');
            colb.innerHTML = '<svg><g>' +
                '<line style="stroke:#181818;stroke-width:1.0;" x1="25" x2="76" y1="40" y2="40"></line>' +
                '</g></svg>';
            const message = colb.querySelector('line');
            setupMessageHandlers([message], colb.querySelector('g'));

            highlightSequenceForRow(3);
            message.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
            message.dispatchEvent(new MouseEvent('mouseout', {bubbles: true}));
            const stillBold = message.style.fontWeight === 'bold';
            resetSequenceHighlight();
            const afterReset = message.style.fontWeight === 'bold';

            return {stillBold, afterReset};
        }"""
        )

        assert result["stillBold"] is True
        assert result["afterReset"] is False

    def test_cursor_listener_routes_to_sequence_highlight(self, app_url, page):
        result = page.evaluate(
            """async () => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            currentDiagramType = 'sequence';
            messagePositions = [{cy: 40, index: 1, text: 'm1'}];
            participantLifelines = [];
            notePositions = [];
            groupPositions = [];
            sequenceHighlighted = [];
            const colb = document.getElementById('colb');
            colb.innerHTML = '<svg><g>' +
                '<line style="stroke:#181818;stroke-width:1.0;" x1="25" x2="76" y1="40" y2="40"></line>' +
                '</g></svg>';
            const message = colb.querySelector('line');
            sequenceRowMap = new Map();
            setupMessageHandlers([message], colb.querySelector('g'));

            editor.moveCursorTo(1, 0);
            await cursorChangeListener();
            const highlighted = message.style.fontWeight === 'bold';
            resetSequenceHighlight();
            currentDiagramType = 'unknown';
            return {highlighted};
        }"""
        )

        assert result["highlighted"] is True

    def test_leaving_editor_clears_lingering_highlight(self, app_url, page):
        # Hovering an editor row highlights the matching element; when the
        # pointer then leaves the editor (mouseleave on the Ace container) the
        # highlight must be cleared so it does not linger on the diagram. The
        # sequence diagram-side hover preserves highlights and never resets, so
        # this relies on the editor mouseleave handler in script.js.
        result = page.evaluate(
            """() => {"""
            + HOVER_MARKER_HELPERS
            + """
            resetAddModes();
            currentDiagramType = 'sequence';
            messagePositions = [{cy: 40, index: 3, text: 'm1'}];
            participantLifelines = [];
            notePositions = [];
            groupPositions = [];
            sequenceHighlighted = [];
            const colb = document.getElementById('colb');
            colb.innerHTML = '<svg><g>' +
                '<line style="stroke:#181818;stroke-width:1.0;" x1="25" x2="76" y1="40" y2="40"></line>' +
                '</g></svg>';
            const message = colb.querySelector('line');
            sequenceRowMap = new Map();
            setupMessageHandlers([message], colb.querySelector('g'));

            highlightSequenceForRow(3);
            const whileHovering = message.style.fontWeight === 'bold';

            editor.container.dispatchEvent(new MouseEvent('mouseleave', {bubbles: true}));
            const afterLeaving = message.style.fontWeight === 'bold';
            currentDiagramType = 'unknown';
            return {whileHovering, afterLeaving, count: sequenceHighlighted.length};
        }"""
        )

        assert result["whileHovering"] is True
        assert result["afterLeaving"] is False
        assert result["count"] == 0
