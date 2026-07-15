# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2026 Ericsson
#
# Permission is hereby granted, free of charge, to any person obtaining a copy
# of this software and associated documentation files (the "Software"), to deal
# in the Software without restriction, including without limitation the rights
# to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
# copies of the Software, and to permit persons to whom the Software is
# furnished to do so, subject to the following conditions:
#
# The above copyright notice and this permission notice shall be included in all
# copies or substantial portions of the Software.
#
# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
# OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
# SOFTWARE.

"""End-to-end tests for sequence diagram participant-box JS logic."""

# Builds a synthetic sequence SVG (three participant header rects) inside #colb
# and a matching participantLifelines table. Returns {svg, rects}. Mirrors how
# the other sequence e2e tests drive interaction logic without a full render.
SETUP_SVG = """() => {
    const NS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(NS, 'svg');
    const g = document.createElementNS(NS, 'g');
    svg.appendChild(g);
    const specs = [
        {x: 10, w: 40, cx: 30, index: 1},
        {x: 60, w: 40, cx: 80, index: 2},
        {x: 110, w: 40, cx: 130, index: 3},
    ];
    const rects = specs.map((s) => {
        const r = document.createElementNS(NS, 'rect');
        r.setAttribute('x', s.x);
        r.setAttribute('y', 6);
        r.setAttribute('width', s.w);
        r.setAttribute('height', 30);
        r.setAttribute('rx', 2.5);
        r.setAttribute('ry', 2.5);
        r.setAttribute('style', 'stroke:#181818;stroke-width:0.5;');
        g.appendChild(r);
        return r;
    });
    const colb = document.getElementById('colb');
    colb.innerHTML = '';
    colb.appendChild(svg);
    participantLifelines = specs.map((s, i) => ({
        name: 'A' + (i + 1), cx: s.cx, yTop: 40, yBottom: 100, index: s.index,
    }));
    return {svg, rects};
}"""


class TestBoxMenus:
    def test_box_menu_item_exists(self, app_url, page):
        """The Box item exists in the participant context menu."""
        result = page.evaluate("() => document.getElementById('seq-addBox') !== null")
        assert result is True

    def test_box_menu_items_exist_in_sequence_menu(self, app_url, page):
        """Edit/Delete Box items live in the lifeline (sequence) menu and are
        hidden by default (shown only when the right-click is inside a box)."""
        result = page.evaluate("""() => {
            const edit = document.getElementById('seq-editBox');
            const del = document.getElementById('seq-deleteBox');
            const menu = document.getElementById('sequence-menu');
            return {
                exist: edit !== null && del !== null,
                insideSequenceMenu: menu.contains(edit) && menu.contains(del),
                hiddenByDefault:
                    document.getElementById('seq-editBox-item').style.display === 'none'
                    && document.getElementById('seq-deleteBox-item').style.display === 'none',
                noSeparateBoxMenu: document.getElementById('seq-box-menu') === null,
            };
        }""")
        assert result["exist"] is True
        assert result["insideSequenceMenu"] is True
        assert result["hiddenByDefault"] is True
        assert result["noSeparateBoxMenu"] is True


class TestBoxAddMode:
    def test_ghost_box_grows_when_hovering_further_participant(self, app_url, page):
        """Ghost box widens as the hover moves from the origin to a further
        participant."""
        result = page.evaluate(
            """(setup) => {
                const {svg, rects} = eval('(' + setup + ')')();
                lastclickedsvgelement = rects[0];

                const started = startBoxAddModeFromContext();
                const w0 = ghostBox ? parseFloat(ghostBox.getAttribute('width')) : -1;

                // Move the hover to the right-most participant.
                const far = participantLifelines.reduce((a, b) => b.cx > a.cx ? b : a);
                handleBoxMouseMove(svg, far.cx);
                const w1 = ghostBox ? parseFloat(ghostBox.getAttribute('width')) : -1;

                return {started, w0, w1, addMode: isBoxAddMode()};
            }""",
            SETUP_SVG,
        )

        assert result["started"] is True
        assert result["addMode"] is True
        assert result["w0"] > 0
        assert result["w1"] > result["w0"]

    def test_click_submits_addbox_with_participant_range(self, app_url, page):
        """Confirming the range posts the origin/destination participant line
        indexes to /addBox."""
        result = page.evaluate(
            """(setup) => {
                const {rects} = eval('(' + setup + ')')();
                lastclickedsvgelement = rects[0];
                startBoxAddModeFromContext();

                // Capture the request instead of hitting the backend.
                let captured = null;
                const realFetch = window.fetch;
                window.fetch = (url, opts) => {
                    captured = {url, body: JSON.parse(opts.body)};
                    return Promise.resolve({json: () => Promise.resolve(
                        {plantuml: '@startuml\\n@enduml'})});
                };
                const realSetPuml = window.setPuml;
                window.setPuml = () => {};

                const far = participantLifelines.reduce((a, b) => b.cx > a.cx ? b : a);
                handleBoxClick({stopPropagation() {}}, far.cx);

                // The fetch body is captured synchronously at call time; wait a
                // tick so the async submit has issued it, then restore.
                return new Promise((resolve) => {
                    setTimeout(() => {
                        window.fetch = realFetch;
                        window.setPuml = realSetPuml;
                        resolve(captured);
                    }, 50);
                });
            }""",
            SETUP_SVG,
        )

        assert result is not None
        assert result["url"].endswith("addBox")
        assert result["body"]["startParticipantIndex"] == 1
        assert result["body"]["endParticipantIndex"] == 3

    def test_escape_cancels_box_add_mode(self, app_url, page):
        result = page.evaluate(
            """(setup) => {
                // Ensure the box listeners (incl. the Escape handler) are wired;
                // they are normally attached when a sequence diagram is detected.
                boxEventListeners();
                const {rects} = eval('(' + setup + ')')();
                lastclickedsvgelement = rects[0];
                startBoxAddModeFromContext();
                const before = isBoxAddMode();
                document.dispatchEvent(new KeyboardEvent('keydown', {key: 'Escape'}));
                return {before, after: isBoxAddMode()};
            }""",
            SETUP_SVG,
        )

        assert result["before"] is True
        assert result["after"] is False


# Builds a synthetic SVG inside #colb containing one box rect enclosing a single
# participant header, plus a matching boxPositions table. Returns {boxRect}.
SETUP_BOX = """() => {
    const NS = 'http://www.w3.org/2000/svg';
    const svg = document.createElementNS(NS, 'svg');
    const g = document.createElementNS(NS, 'g');
    svg.appendChild(g);

    const box = document.createElementNS(NS, 'rect');
    box.setAttribute('x', 10);
    box.setAttribute('y', 6);
    box.setAttribute('width', 60);
    box.setAttribute('height', 120);
    box.setAttribute('fill', '#DDDDDD');
    box.setAttribute('style', 'stroke:#181818;stroke-width:0.5;');
    g.appendChild(box);

    const participant = document.createElementNS(NS, 'rect');
    participant.setAttribute('x', 20);
    participant.setAttribute('y', 25);
    participant.setAttribute('width', 40);
    participant.setAttribute('height', 30);
    participant.setAttribute('rx', 2.5);
    participant.setAttribute('ry', 2.5);
    participant.setAttribute('style', 'stroke:#181818;stroke-width:0.5;');
    g.appendChild(participant);

    const colb = document.getElementById('colb');
    colb.innerHTML = '';
    colb.appendChild(svg);
    boxPositions = [{headerIndex: 1, endIndex: 4}];
    return {svg, boxRect: box};
}"""


class TestBoxContextDetection:
    def test_findenclosingbox_inside_and_outside(self, app_url, page):
        result = page.evaluate(
            """(setup) => {
                eval('(' + setup + ')')();
                setupBoxHandlers(document.querySelectorAll('#colb svg *'));
                // Box spans x[10..70], y[6..126].
                return {
                    inside: findEnclosingBox(40, 60) !== null,
                    outsideX: findEnclosingBox(200, 60),
                    outsideY: findEnclosingBox(40, 300),
                };
            }""",
            SETUP_BOX,
        )
        assert result["inside"] is True
        assert result["outsideX"] is None
        assert result["outsideY"] is None

    def test_findenclosingbox_picks_innermost(self, app_url, page):
        result = page.evaluate("""() => {
            const NS = 'http://www.w3.org/2000/svg';
            const svg = document.createElementNS(NS, 'svg');
            const g = document.createElementNS(NS, 'g');
            svg.appendChild(g);
            function box(x, y, w, h) {
                const r = document.createElementNS(NS, 'rect');
                r.setAttribute('x', x); r.setAttribute('y', y);
                r.setAttribute('width', w); r.setAttribute('height', h);
                r.setAttribute('fill', '#DDDDDD');
                r.setAttribute('style', 'stroke:#181818;stroke-width:0.5;');
                g.appendChild(r);
                return r;
            }
            function participant(x) {
                const r = document.createElementNS(NS, 'rect');
                r.setAttribute('x', x); r.setAttribute('y', 25);
                r.setAttribute('width', 20); r.setAttribute('height', 30);
                r.setAttribute('rx', 2.5); r.setAttribute('ry', 2.5);
                r.setAttribute('style', 'stroke:#181818;stroke-width:0.5;');
                g.appendChild(r);
            }
            const outer = box(10, 6, 200, 120);   // outer, larger
            participant(20);
            const inner = box(60, 10, 80, 110);   // inner, smaller
            participant(70);
            const colb = document.getElementById('colb');
            colb.innerHTML = ''; colb.appendChild(svg);
            boxPositions = [{headerIndex: 1, endIndex: 6}, {headerIndex: 3, endIndex: 5}];
            setupBoxHandlers(document.querySelectorAll('#colb svg *'));
            // Point inside both boxes -> innermost (inner) wins.
            return findEnclosingBox(100, 60) === inner;
        }""")
        assert result is True

    def test_inside_box_off_lifeline_shows_only_box_items(self, app_url, page):
        """Right-clicking inside a box but not on a lifeline shows the Edit/Delete
        Box items and hides the lifeline-only actions."""
        result = page.evaluate(
            """(setup) => {
                const {svg, boxRect} = eval('(' + setup + ')')();
                setupBoxHandlers(document.querySelectorAll('#colb svg *'));
                participantLifelines = [];  // no lifeline near the click

                // Drive the background context menu with a point inside the box
                // (x[10..70], y[6..126]); stub the screen->svg transform.
                const realTransform = svgPointFromEvent;
                svgPointFromEvent = () => ({x: 40, y: 60});
                try {
                    backgroundContextMenu(
                        {preventDefault() {}, target: boxRect, pageX: 5, pageY: 5},
                        svg);
                } finally {
                    svgPointFromEvent = realTransform;
                }

                const disp = (id) => document.getElementById(id).style.display;
                const liDisp = (id) =>
                    document.getElementById(id).closest('li').style.display;
                return {
                    menu: document.getElementById('sequence-menu').style.display,
                    editBox: disp('seq-editBox-item'),
                    deleteBox: disp('seq-deleteBox-item'),
                    addMessageHidden: liDisp('addMessageSolid') === 'none',
                    addGroupHidden: liDisp('seq-addGroup') === 'none',
                    contextBoxIsBox: contextBoxRect === boxRect,
                };
            }""",
            SETUP_BOX,
        )
        assert result["menu"] == "block"
        assert result["editBox"] == ""
        assert result["deleteBox"] == ""
        assert result["addMessageHidden"] is True
        assert result["addGroupHidden"] is True
        assert result["contextBoxIsBox"] is True

    def test_outside_box_and_lifeline_shows_no_menu(self, app_url, page):
        """Right-clicking empty space (no lifeline, no box) shows nothing."""
        result = page.evaluate(
            """(setup) => {
                const {svg} = eval('(' + setup + ')')();
                setupBoxHandlers(document.querySelectorAll('#colb svg *'));
                participantLifelines = [];
                document.getElementById('sequence-menu').style.display = 'none';

                const realTransform = svgPointFromEvent;
                svgPointFromEvent = () => ({x: 500, y: 500});  // far outside the box
                try {
                    backgroundContextMenu(
                        {preventDefault() {}, target: svg, pageX: 5, pageY: 5}, svg);
                } finally {
                    svgPointFromEvent = realTransform;
                }
                return document.getElementById('sequence-menu').style.display;
            }""",
            SETUP_BOX,
        )
        assert result == "none"

    def test_delete_box_posts_to_deleteseqbox(self, app_url, page):
        result = page.evaluate(
            """(setup) => {
                boxEventListeners();
                const {boxRect} = eval('(' + setup + ')')();
                setupBoxHandlers(document.querySelectorAll('#colb svg *'));
                // The lifeline menu sets contextBoxRect when inside a box.
                contextBoxRect = boxRect;

                let captured = null;
                const realFetch = window.fetch;
                window.fetch = (url, opts) => {
                    captured = {url, body: JSON.parse(opts.body)};
                    return Promise.resolve({json: () => Promise.resolve(
                        {plantuml: '@startuml\\n@enduml'})});
                };
                const realSetPuml = window.setPuml;
                window.setPuml = () => {};

                document.getElementById('seq-deleteBox').click();

                return new Promise((resolve) => {
                    setTimeout(() => {
                        window.fetch = realFetch;
                        window.setPuml = realSetPuml;
                        resolve(captured);
                    }, 50);
                });
            }""",
            SETUP_BOX,
        )
        assert result is not None
        assert result["url"].endswith("deleteSeqBox")
        assert 'fill="#DDDDDD"' in result["body"]["svgelement"]

    def test_box_rect_has_no_note_menu(self, app_url, page):
        """A box rect must not be handled as a note: setupNoteHandlers skips box
        rects (they enclose a participant), so right-clicking one never opens the
        note menu."""
        result = page.evaluate(
            """(setup) => {
                const {boxRect} = eval('(' + setup + ')')();
                const nodes = document.querySelectorAll('#colb svg *');
                setupNoteHandlers(nodes);
                setupBoxHandlers(nodes);
                document.getElementById('seq-note-menu').style.display = 'none';
                boxRect.dispatchEvent(new MouseEvent('contextmenu', {
                    bubbles: true, cancelable: true, clientX: 30, clientY: 40}));
                return document.getElementById('seq-note-menu').style.display;
            }""",
            SETUP_BOX,
        )
        assert result == "none"


class TestBoxEdit:
    def test_edit_menu_item_and_modal_exist(self, app_url, page):
        result = page.evaluate("""() => {
            return document.getElementById('seq-editBox') !== null
                && document.getElementById('seq-box-modalForm') !== null
                && document.getElementById('seq-box-title-text') !== null
                && document.getElementById('seq-box-color-select') !== null;
        }""")
        assert result is True

    def test_color_options_none_first_and_tinted(self, app_url, page):
        result = page.evaluate("""() => {
            const opts = document.getElementById('seq-box-color-select').options;
            // Every non-None option carries a background-color tint.
            let allTinted = true;
            for (let i = 1; i < opts.length; i++) {
                if (!(opts[i].style.backgroundColor)) allTinted = false;
            }
            return {count: opts.length, first: opts[0].value, allTinted};
        }""")
        assert result["first"] == "none"
        assert result["count"] > 1
        assert result["allTinted"] is True

    def test_edit_click_populates_modal_from_label(self, app_url, page):
        result = page.evaluate(
            """(setup) => {
                boxEventListeners();
                const {boxRect} = eval('(' + setup + ')')();
                setupBoxHandlers(document.querySelectorAll('#colb svg *'));
                contextBoxRect = boxRect;  // set by the lifeline menu when in a box

                const realFetch = window.fetch;
                window.fetch = () => Promise.resolve({json: () => Promise.resolve(
                    {title: 'Hello', color: 'Wheat'})});

                document.getElementById('seq-editBox').click();

                return new Promise((resolve) => {
                    setTimeout(() => {
                        window.fetch = realFetch;
                        resolve({
                            title: document.getElementById('seq-box-title-text').value,
                            color: document.getElementById('seq-box-color-select').value,
                        });
                    }, 60);
                });
            }""",
            SETUP_BOX,
        )
        assert result["title"] == "Hello"
        assert result["color"] == "Wheat"

    def test_edit_click_falls_back_to_none_for_unknown_color(self, app_url, page):
        result = page.evaluate(
            """(setup) => {
                boxEventListeners();
                const {boxRect} = eval('(' + setup + ')')();
                setupBoxHandlers(document.querySelectorAll('#colb svg *'));
                contextBoxRect = boxRect;

                const realFetch = window.fetch;
                window.fetch = () => Promise.resolve({json: () => Promise.resolve(
                    {title: '', color: '00FF00'})});  // not in the palette

                document.getElementById('seq-editBox').click();

                return new Promise((resolve) => {
                    setTimeout(() => {
                        window.fetch = realFetch;
                        resolve(document.getElementById('seq-box-color-select').value);
                    }, 60);
                });
            }""",
            SETUP_BOX,
        )
        assert result == "none"

    def test_submit_posts_title_and_color_to_editseqbox(self, app_url, page):
        result = page.evaluate(
            """(setup) => {
                const {boxRect} = eval('(' + setup + ')')();
                contextBoxRect = boxRect;
                document.getElementById('seq-box-title-text').value = 'My Box';
                document.getElementById('seq-box-color-select').value = 'LightGreen';

                let captured = null;
                const realFetch = window.fetch;
                window.fetch = (url, opts) => {
                    captured = {url, body: JSON.parse(opts.body)};
                    return Promise.resolve({json: () => Promise.resolve(
                        {plantuml: '@startuml\\n@enduml'})});
                };
                const realSetPuml = window.setPuml;
                window.setPuml = () => {};

                submitBoxEdit();

                return new Promise((resolve) => {
                    setTimeout(() => {
                        window.fetch = realFetch;
                        window.setPuml = realSetPuml;
                        resolve(captured);
                    }, 60);
                });
            }""",
            SETUP_BOX,
        )
        assert result is not None
        assert result["url"].endswith("editSeqBox")
        assert result["body"]["title"] == "My Box"
        assert result["body"]["color"] == "LightGreen"


class TestBoxHoverHighlight:
    def test_hovering_box_marks_editor_rows(self, app_url, page):
        result = page.evaluate(
            """(setup) => {
                const {boxRect} = eval('(' + setup + ')')();
                setupBoxHandlers(document.querySelectorAll('#colb svg *'));

                let markedWith = null;
                const realGetmarker = window.getmarker;
                window.getmarker = (rows) => { markedWith = rows; };

                boxRect.dispatchEvent(new MouseEvent('mouseover', {bubbles: true}));
                window.getmarker = realGetmarker;
                return markedWith;
            }""",
            SETUP_BOX,
        )
        assert result == [1, 4]
