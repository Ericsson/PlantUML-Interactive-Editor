# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2026 Ericsson

"""End-to-end probes for editor->diagram hover highlighting in activity
diagrams: moving the cursor/mouse onto an editor row recolors the diagram
element(s) whose puml lines own that row."""

SETUP_HELPERS = """
    function freshTargets() {
        activityHoverTargets = newActivityHoverTargets();
        activityHighlighted = [];
        activityRowMap = new Map();
    }
    function emptyPositions() {
        return {activities: [], polys: [], whiles: [], notes: [], groups: [],
                ellipses: [], connectors: [], merges: [], arrows: [], title: []};
    }
    function svgRect(fill) {
        const el = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        if (fill !== undefined) el.setAttribute('fill', fill);
        return el;
    }
"""


class TestEditorToActivityHighlight:
    def test_activity_row_highlights_rect_and_reset_restores(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + SETUP_HELPERS
            + """
            freshTargets();
            const rect = svgRect('#F1F1F1');
            activityHoverTargets.activities.push(rect);
            const positions = emptyPositions();
            positions.activities = [[3, 4]]; // multiline activity
            buildActivityRowMap(positions);

            highlightActivityForRow(3);
            const duringRow3 = rect.getAttribute('fill');
            resetActivityHighlight();
            const afterReset = rect.getAttribute('fill');
            highlightActivityForRow(4);
            const duringRow4 = rect.getAttribute('fill');
            resetActivityHighlight();

            return {duringRow3, afterReset, duringRow4};
        }"""
        )

        assert result["duringRow3"] == "#d8d8d8"
        assert result["afterReset"] == "#F1F1F1"
        assert result["duringRow4"] == "#d8d8d8"

    def test_unmapped_row_highlights_nothing(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + SETUP_HELPERS
            + """
            freshTargets();
            const rect = svgRect('#F1F1F1');
            activityHoverTargets.activities.push(rect);
            const positions = emptyPositions();
            positions.activities = [[3]];
            buildActivityRowMap(positions);

            highlightActivityForRow(0); // @startuml row owns nothing
            return {fill: rect.getAttribute('fill'), highlighted: activityHighlighted.length};
        }"""
        )

        assert result["fill"] == "#F1F1F1"
        assert result["highlighted"] == 0

    def test_type_specific_highlight_colors(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + SETUP_HELPERS
            + """
            freshTargets();
            const ellipse = svgRect('#222222');
            const connector = svgRect('#F1F1F1');
            const title = svgRect('transparent');
            activityHoverTargets.ellipses.push(ellipse);
            activityHoverTargets.connectors.push(connector);
            activityHoverTargets.title.push(title);
            const positions = emptyPositions();
            positions.ellipses = [[1]];
            positions.connectors = [[2]];
            positions.title = [3];
            buildActivityRowMap(positions);

            highlightActivityForRow(1);
            const ellipseFill = ellipse.getAttribute('fill');
            resetActivityHighlight();
            highlightActivityForRow(2);
            const connectorFill = connector.getAttribute('fill');
            resetActivityHighlight();
            highlightActivityForRow(3);
            const titleFill = title.getAttribute('fill');
            resetActivityHighlight();

            return {ellipseFill, connectorFill, titleFill,
                    restored: [ellipse.getAttribute('fill'), connector.getAttribute('fill'), title.getAttribute('fill')]};
        }"""
        )

        assert result["ellipseFill"] == "#818181"
        assert result["connectorFill"] == "#c2c2c2"
        assert result["titleFill"] == "#e5e5e5"
        assert result["restored"] == ["#222222", "#F1F1F1", "transparent"]

    def test_group_rows_bold_label_and_reset_removes_missing_weight(
        self, app_url, page
    ):
        result = page.evaluate(
            """() => {"""
            + SETUP_HELPERS
            + """
            freshTargets();
            const label = svgRect(); // group label text has no font-weight attribute
            activityHoverTargets.groups.push(label);
            const positions = emptyPositions();
            positions.groups = [[2, 7]]; // header and closing brace rows only
            buildActivityRowMap(positions);

            highlightActivityForRow(7);
            const duringEndRow = label.getAttribute('font-weight');
            resetActivityHighlight();
            const afterReset = label.hasAttribute('font-weight');
            highlightActivityForRow(4); // row inside the partition owns nothing
            const insideRow = label.getAttribute('font-weight');

            return {duringEndRow, afterReset, insideRow};
        }"""
        )

        assert result["duringEndRow"] == "bold"
        assert result["afterReset"] is False
        assert result["insideRow"] is None

    def test_arrow_entry_bolds_all_label_texts(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + SETUP_HELPERS
            + """
            freshTargets();
            const text1 = svgRect('#000000');
            const text2 = svgRect('#000000');
            activityHoverTargets.arrows.push([text1, text2]);
            const positions = emptyPositions();
            positions.arrows = [[5, 6]];
            buildActivityRowMap(positions);

            highlightActivityForRow(5);
            const during = [text1.getAttribute('font-weight'), text2.getAttribute('font-weight')];
            const fillsUntouched = [text1.getAttribute('fill'), text2.getAttribute('fill')];
            resetActivityHighlight();
            const after = [text1.hasAttribute('font-weight'), text2.hasAttribute('font-weight')];

            return {during, fillsUntouched, after};
        }"""
        )

        assert result["during"] == ["bold", "bold"]
        assert result["fillsUntouched"] == ["#000000", "#000000"]
        assert result["after"] == [False, False]

    def test_fork_rows_come_from_client_side_registration(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + SETUP_HELPERS
            + """
            freshTargets();
            const bar = svgRect('#555555');
            activityHoverTargets.forks.push({el: bar, row: 9});
            buildActivityRowMap(emptyPositions());

            highlightActivityForRow(9);
            const during = bar.getAttribute('fill');
            resetActivityHighlight();
            return {during, after: bar.getAttribute('fill')};
        }"""
        )

        assert result["during"] == "#d8d8d8"
        assert result["after"] == "#555555"

    def test_element_already_showing_highlight_color_is_not_captured(
        self, app_url, page
    ):
        # Simulates the diagram-hover interplay: if a mouseover already turned
        # the element grey, the editor highlight must not save grey as the
        # "original" fill, or the true color would be lost on reset.
        result = page.evaluate(
            """() => {"""
            + SETUP_HELPERS
            + """
            freshTargets();
            const rect = svgRect('#d8d8d8'); // diagram hover in progress
            activityHoverTargets.activities.push(rect);
            const positions = emptyPositions();
            positions.activities = [[3]];
            buildActivityRowMap(positions);

            highlightActivityForRow(3);
            const captured = activityHighlighted.length;
            resetActivityHighlight();
            return {captured, fill: rect.getAttribute('fill')};
        }"""
        )

        assert result["captured"] == 0
        assert result["fill"] == "#d8d8d8"

    def test_cursor_listener_routes_to_activity_highlight(self, app_url, page):
        result = page.evaluate(
            """() => {"""
            + SETUP_HELPERS
            + """
            freshTargets();
            const rect = svgRect('#F1F1F1');
            activityHoverTargets.activities.push(rect);
            const positions = emptyPositions();
            positions.activities = [[1]];
            buildActivityRowMap(positions);

            const previousType = currentDiagramType;
            currentDiagramType = 'activity';
            editor.moveCursorTo(1, 0);
            cursorChangeListener();
            const during = rect.getAttribute('fill');
            resetActivityHighlight();
            currentDiagramType = previousType;
            return {during, after: rect.getAttribute('fill')};
        }"""
        )

        assert result["during"] == "#d8d8d8"
        assert result["after"] == "#F1F1F1"

    def test_multiple_elements_on_same_row_all_highlight(self, app_url, page):
        # e.g. an "endif" row is owned by both the if polygon and its merge
        result = page.evaluate(
            """() => {"""
            + SETUP_HELPERS
            + """
            freshTargets();
            const poly = svgRect('#F1F1F1');
            const merge = svgRect('#F1F1F1');
            activityHoverTargets.polys.push(poly);
            activityHoverTargets.merges.push(merge);
            const positions = emptyPositions();
            positions.polys = [[2, 4, 6]];
            positions.merges = [[6]];
            buildActivityRowMap(positions);

            highlightActivityForRow(6);
            const during = [poly.getAttribute('fill'), merge.getAttribute('fill')];
            resetActivityHighlight();
            const after = [poly.getAttribute('fill'), merge.getAttribute('fill')];
            return {during, after};
        }"""
        )

        assert result["during"] == ["#d8d8d8", "#d8d8d8"]
        assert result["after"] == ["#F1F1F1", "#F1F1F1"]

    def test_leaving_editor_clears_lingering_highlight(self, app_url, page):
        # Activity used to clear a lingering editor-side highlight in each
        # element's diagram-side mouseover; that was removed as redundant, so
        # clearing now relies on the shared editor mouseleave handler (leaving
        # the editor resets the highlight for the active diagram type).
        result = page.evaluate(
            """() => {"""
            + SETUP_HELPERS
            + """
            freshTargets();
            const rect = svgRect('#F1F1F1');
            activityHoverTargets.activities.push(rect);
            const positions = emptyPositions();
            positions.activities = [[3]];
            buildActivityRowMap(positions);

            const previousType = currentDiagramType;
            currentDiagramType = 'activity';
            highlightActivityForRow(3);
            const whileHovering = rect.getAttribute('fill');

            editor.container.dispatchEvent(new MouseEvent('mouseleave', {bubbles: true}));
            const afterLeaving = rect.getAttribute('fill');
            currentDiagramType = previousType;
            return {whileHovering, afterLeaving, count: activityHighlighted.length};
        }"""
        )

        assert result["whileHovering"] == "#d8d8d8"
        assert result["afterLeaving"] == "#F1F1F1"
        assert result["count"] == 0


class TestActivityToEditorMarkers:
    """Diagram->editor markers: hovering a diagram element marks its editor
    line, and leaving the element clears the marker (so the last hovered
    element does not stay highlighted in the editor)."""

    _PUML = "@startuml\\nstart\\n:Hello;\\nstop\\n@enduml"

    def _load_activity(self, page, retries=12, wait_ms=1500):
        # The page renders its demo once on load; that late async render can
        # clobber #colb after our setValue, so retry until the activity diagram
        # is stably rendered (matches the retry approach in the sequence tests).
        for _ in range(retries):
            page.evaluate(f"() => editor.session.setValue('{self._PUML}')")
            page.wait_for_timeout(wait_ms)
            ok = page.evaluate(
                "() => currentDiagramType === 'activity' "
                "&& !!document.querySelector('#colb g')"
            )
            if ok:
                return
        raise AssertionError("activity diagram did not render")

    def test_leaving_diagram_element_clears_editor_marker(self, app_url, page):
        self._load_activity(page)
        result = page.evaluate(
            """() => {
            const g = document.querySelector('#colb g');
            // Simulate the "hover" marker a diagram-element mouseover sets.
            setEditorMarkers(2);
            const countHover = () => Object.values(editor.session.getMarkers())
                .filter(m => m.clazz === 'hover').length;
            const before = countHover();
            g.dispatchEvent(new MouseEvent('mouseout', {bubbles: true}));
            const after = countHover();
            return {before, after};
        }"""
        )

        assert result["before"] >= 1
        assert result["after"] == 0
