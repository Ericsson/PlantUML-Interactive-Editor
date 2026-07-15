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

    def test_box_context_menu_exists(self, app_url, page):
        """The box context menu and its Delete Box item exist in the DOM."""
        result = page.evaluate("""() => {
            return document.getElementById('seq-box-menu') !== null
                && document.getElementById('seq-deleteBox') !== null;
        }""")
        assert result is True


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
    return {boxRect: box};
}"""


class TestBoxDelete:
    def test_contextmenu_opens_box_menu(self, app_url, page):
        result = page.evaluate(
            """(setup) => {
                const {boxRect} = eval('(' + setup + ')')();
                setupBoxHandlers(document.querySelectorAll('#colb svg *'));
                boxRect.dispatchEvent(new MouseEvent('contextmenu', {
                    bubbles: true, cancelable: true, clientX: 30, clientY: 40}));
                return {
                    menuDisplay: document.getElementById('seq-box-menu').style.display,
                    lastClickedIsBox: lastclickedsvgelement === boxRect,
                };
            }""",
            SETUP_BOX,
        )
        assert result["menuDisplay"] == "block"
        assert result["lastClickedIsBox"] is True

    def test_delete_box_posts_to_deleteseqbox(self, app_url, page):
        result = page.evaluate(
            """(setup) => {
                boxEventListeners();
                const {boxRect} = eval('(' + setup + ')')();
                setupBoxHandlers(document.querySelectorAll('#colb svg *'));
                boxRect.dispatchEvent(new MouseEvent('contextmenu', {
                    bubbles: true, cancelable: true, clientX: 30, clientY: 40}));

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
