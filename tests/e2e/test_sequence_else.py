# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2026 Ericsson

"""End-to-end probes for else branches inside sequence alt groups: the dashed
else separator and its [label] must not be picked up as message elements."""

import json

import pytest

# m2 is a black dashed message: its line style is identical to an else
# separator's (stroke:#000000;stroke-width:1.0;stroke-dasharray:2.0,2.0), so
# only geometry can tell them apart.
ALT_ELSE_PUML = """@startuml
participant alice
participant bob
alt success
alice -> bob: m1
else failure
bob -[#black]-> alice: m2
else
alice --> bob: m3
end
@enduml"""

# Classifies every dashed line in the rendered diagram. Separators are the
# full-box-width lines; the rest are dashed message arrows.
_PROBE = """() => {
    const g = document.querySelector('#colb svg g');
    const all = g.querySelectorAll('*');
    const bounds = groupBoxBounds(all);
    const dashed = Array.from(g.querySelectorAll('line')).filter(l =>
        (l.getAttribute('style') || '').includes('stroke-width:1.0;stroke-dasharray'));
    const box = bounds[0];
    const isFullWidth = l =>
        parseFloat(l.getAttribute('x1')) === box.x &&
        parseFloat(l.getAttribute('x2')) === box.right;
    const separators = dashed.filter(isFullWidth);
    const dashedMessages = dashed.filter(l => !isFullWidth(l));
    const elseLabel = Array.from(g.querySelectorAll('text'))
        .find(t => t.textContent === '[failure]');
    const registered = new Set();
    for (const entries of sequenceRowMap.values()) {
        for (const entry of entries) registered.add(entry.el);
    }
    return {
        separatorCount: separators.length,
        separatorsAsMessage: separators.map(s => checkIfMessageElement(s, bounds)),
        separatorsRegistered: separators.map(s => registered.has(s)),
        dashedMessageStyles: dashedMessages.map(l => l.getAttribute('style')),
        dashedMessagesAsMessage: dashedMessages.map(l => checkIfMessageElement(l, bounds)),
        dashedMessagesRegistered: dashedMessages.map(l => registered.has(l)),
        labelAsMessage: elseLabel ? checkIfMessageElement(elseLabel, bounds) : null,
    };
}"""


def _load_alt_else(page):
    page.evaluate(f"setPuml({json.dumps(ALT_ELSE_PUML)})")
    page.wait_for_function(
        "() => messagePositions.length === 3 && "
        "document.querySelector('#colb svg g') !== null",
        timeout=15000,
    )
    return page.evaluate(_PROBE)


class TestElseSeparatorDetection:
    def test_separator_is_not_a_message_element(self, app_url, page):
        result = _load_alt_else(page)

        assert result["separatorCount"] == 2
        assert result["separatorsAsMessage"] == [False, False]

    def test_separator_is_not_registered_for_highlighting(self, app_url, page):
        result = _load_alt_else(page)

        assert result["separatorsRegistered"] == [False, False]

    def test_black_dashed_message_is_still_a_message(self, app_url, page):
        result = _load_alt_else(page)

        # Guards the premise: the black message really is styled like a separator.
        assert (
            "stroke:#000000;stroke-width:1.0;stroke-dasharray:2.0,2.0;"
            in (result["dashedMessageStyles"])
        )
        assert result["dashedMessagesAsMessage"] == [True, True]
        assert result["dashedMessagesRegistered"] == [True, True]

    def test_else_label_is_not_a_message_element(self, app_url, page):
        result = _load_alt_else(page)

        assert result["labelAsMessage"] is False


class TestIsElseSeparatorPredicate:
    """isElseSeparator is pure over the bounds it is given - no DOM lookups."""

    _CASES = """() => {
        const ns = 'http://www.w3.org/2000/svg';
        const line = (x1, x2, y) => {
            const l = document.createElementNS(ns, 'line');
            l.setAttribute('style', 'stroke:#000000;stroke-width:1.0;stroke-dasharray:2.0,2.0;');
            l.setAttribute('x1', x1); l.setAttribute('x2', x2);
            l.setAttribute('y1', y); l.setAttribute('y2', y);
            return l;
        };
        const bounds = [{x: 10, y: 50, right: 155, bottom: 175}];
        const solid = line(10, 155, 100);
        solid.setAttribute('style', 'stroke:#000000;stroke-width:1.0;');
        return {
            fullWidth: isElseSeparator(line(10, 155, 100), bounds),
            noBounds: isElseSeparator(line(10, 155, 100), []),
            lifelineToLifeline: isElseSeparator(line(42.5, 89.5, 100), bounds),
            outsideBoxVertically: isElseSeparator(line(10, 155, 200), bounds),
            solidFullWidth: isElseSeparator(solid, bounds),
        };
    }"""

    def test_predicate_cases(self, app_url, page):
        result = page.evaluate(self._CASES)

        assert result == {
            "fullWidth": True,
            "noBounds": False,
            "lifelineToLifeline": False,
            "outsideBoxVertically": False,
            "solidFullWidth": False,
        }


def _alt(keyword, *messages):
    """A two-participant diagram with one group wrapping the given messages."""
    return "\n".join(
        ["@startuml", "participant alice", "participant bob", f"{keyword} g"]
        + [f"alice -> bob: {m}" for m in messages]
        + ["end", "@enduml"]
    )


# Opens the group menu by right-clicking the nth group's tab (or its header
# text) and reports whether "Add else" is shown.
_OPEN_GROUP_MENU = """([ordinal, target]) => {
    const g = document.querySelector('#colb svg g');
    const tabs = Array.from(g.querySelectorAll('path'))
        .filter(p => p.getAttribute('fill') === '#EEEEEE');
    let el = tabs[ordinal];
    if (target === 'keyword') {
        // the bold keyword text follows the tab and its box
        el = el.nextElementSibling.nextElementSibling;
    }
    el.dispatchEvent(new MouseEvent('contextmenu', {bubbles: true, cancelable: true}));
    const menu = document.getElementById('seq-group-menu');
    const item = document.getElementById('seq-addElse-item');
    return {
        menuShown: menu.style.display === 'block',
        addElseShown: item.style.display !== 'none',
        ordinal: contextGroupOrdinal,
    };
}"""


def _load(page, puml, groups):
    page.evaluate(f"setPuml({json.dumps(puml)})")
    page.wait_for_function(
        f"() => groupPositions.length === {groups} && "
        "document.querySelector('#colb svg g') !== null",
        timeout=15000,
    )


def _open_group_menu(page, ordinal=0, target="tab"):
    return page.evaluate(_OPEN_GROUP_MENU, [ordinal, target])


class TestAddElseMenuItem:
    def test_shown_for_group_with_an_else_position(self, app_url, page):
        _load(page, _alt("alt", "m1", "m2"), 1)
        result = _open_group_menu(page)
        assert result["menuShown"] is True
        assert result["addElseShown"] is True

    @pytest.mark.parametrize("keyword", ["group", "opt", "loop"])
    def test_shown_for_every_group_type(self, app_url, page, keyword):
        _load(page, _alt(keyword, "m1", "m2"), 1)
        assert _open_group_menu(page)["addElseShown"] is True

    def test_shown_for_single_message_group(self, app_url, page):
        # The manually reported case: alt success / Alice -> Bob: granted / end
        _load(page, _alt("alt", "m1"), 1)
        result = _open_group_menu(page)
        assert result["menuShown"] is True
        assert result["addElseShown"] is True

    def test_shown_for_empty_group(self, app_url, page):
        _load(page, _alt("alt"), 1)
        assert _open_group_menu(page)["addElseShown"] is True

    def test_shown_for_group_that_already_has_else_branches(self, app_url, page):
        _load(page, ALT_ELSE_PUML, 1)
        assert _open_group_menu(page)["addElseShown"] is True

    def test_hidden_when_the_group_has_no_else_slots(self, app_url, page):
        # Every rendered group has at least its 'end' slot; an unmatched
        # group (headerIndex -1) comes back with none.
        _load(page, _alt("alt", "m1"), 1)
        page.evaluate("groupPositions[0].elseSlots = []")
        assert _open_group_menu(page)["addElseShown"] is False

    def test_right_clicking_the_keyword_text_also_toggles_it(self, app_url, page):
        _load(page, _alt("alt", "m1", "m2"), 1)
        assert _open_group_menu(page, target="keyword")["addElseShown"] is True

    def test_follows_the_clicked_group(self, app_url, page):
        puml = "\n".join(
            [
                "@startuml",
                "participant alice",
                "participant bob",
                "alt outer",
                "alice -> bob: m1",
                "loop inner",
                "bob -> alice: m2",
                "end",
                "end",
                "@enduml",
            ]
        )
        _load(page, puml, 2)
        page.evaluate("groupPositions[1].elseSlots = []")
        outer = _open_group_menu(page, 0)
        inner = _open_group_menu(page, 1)
        assert (outer["ordinal"], outer["addElseShown"]) == (0, True)
        assert (inner["ordinal"], inner["addElseShown"]) == (1, False)


# The manually reported diagram: one message in an alt.
# Line indexes: 3 alt success | 4 granted | 5 end
SINGLE_MESSAGE_ALT = """@startuml
participant Alice
participant Bob
alt success
Alice -> Bob: granted
end
@enduml"""

# Screen point of an SVG-space coordinate in the live diagram.
_TO_SCREEN = """([x, y]) => {
    const svg = document.querySelector('#colb svg');
    const p = svg.createSVGPoint();
    p.x = x; p.y = y;
    const s = p.matrixTransform(svg.getScreenCTM());
    return [s.x, s.y];
}"""

_GHOST = """() => {
    const line = ghostElseLine && ghostElseLine.parentNode ? ghostElseLine : null;
    return line ? parseFloat(line.getAttribute('y1')) : null;
}"""


def _start_else_mode(page, puml, groups=1, ordinal=0):
    """Load the diagram, right-click the group's tab and click "Add else"."""
    _load(page, puml, groups)
    assert _open_group_menu(page, ordinal)["addElseShown"] is True
    page.click("#seq-addElse")
    assert page.evaluate("isElseAddMode()") is True


def _slots(page):
    return page.evaluate("elseTarget.slots")


def _move_to(page, y):
    """Move the mouse to SVG-space y, horizontally inside the group box."""
    x = page.evaluate(
        "parseFloat(elseTarget.groupRect.getAttribute('x')) + "
        "parseFloat(elseTarget.groupRect.getAttribute('width')) / 2"
    )
    sx, sy = page.evaluate(_TO_SCREEN, [x, y])
    page.mouse.move(sx, sy)


class TestElseAddMode:
    def test_add_else_shows_the_ghost_line(self, app_url, page):
        _start_else_mode(page, SINGLE_MESSAGE_ALT)
        slots = _slots(page)
        assert [s["lineIndex"] for s in slots] == [4, 5]
        assert page.evaluate(_GHOST) == slots[0]["y"]

    def test_ghost_line_spans_the_group_box(self, app_url, page):
        _start_else_mode(page, SINGLE_MESSAGE_ALT)
        span = page.evaluate(
            """() => [
                ghostElseLine.getAttribute('x1') ===
                    elseTarget.groupRect.getAttribute('x'),
                parseFloat(ghostElseLine.getAttribute('x2')) ===
                    parseFloat(elseTarget.groupRect.getAttribute('x')) +
                    parseFloat(elseTarget.groupRect.getAttribute('width')),
            ]"""
        )
        assert span == [True, True]

    def test_ghost_line_snaps_to_the_nearest_slot(self, app_url, page):
        _start_else_mode(page, SINGLE_MESSAGE_ALT)
        before_msg, before_end = _slots(page)
        _move_to(page, before_end["y"] + 3)
        assert page.evaluate(_GHOST) == before_end["y"]
        _move_to(page, before_msg["y"] - 3)
        assert page.evaluate(_GHOST) == before_msg["y"]

    def test_slots_are_ordered_inside_the_box(self, app_url, page):
        _start_else_mode(page, _alt("alt", "m1", "m2"))
        ys = [s["y"] for s in _slots(page)]
        box = page.evaluate(
            "[parseFloat(elseTarget.groupRect.getAttribute('y')), "
            "parseFloat(elseTarget.groupRect.getAttribute('y')) + "
            "parseFloat(elseTarget.groupRect.getAttribute('height'))]"
        )
        assert ys == sorted(ys)
        assert all(box[0] < y < box[1] for y in ys)

    def test_escape_cancels(self, app_url, page):
        _start_else_mode(page, SINGLE_MESSAGE_ALT)
        page.keyboard.press("Escape")
        assert page.evaluate("isElseAddMode()") is False
        assert page.evaluate(_GHOST) is None

    def test_click_opens_the_label_modal(self, app_url, page):
        _start_else_mode(page, SINGLE_MESSAGE_ALT)
        _move_to(page, _slots(page)[1]["y"])
        page.mouse.down()
        page.mouse.up()
        page.wait_for_selector("#seq-group-modalForm.show")
        assert page.text_content("#seq-group-modalForm .modal-title") == "Add else"
        assert page.input_value("#seq-group-label-text") == ""
        assert page.evaluate("isElseAddMode()") is False
        assert page.evaluate(_GHOST) is None

    def _add_via_ui(self, page, puml, slot, label):
        _start_else_mode(page, puml)
        _move_to(page, _slots(page)[slot]["y"])
        page.mouse.down()
        page.mouse.up()
        page.wait_for_selector("#seq-group-modalForm.show")
        page.fill("#seq-group-label-text", label)
        page.click("#seq-submit-group")
        page.wait_for_function("() => editor.session.getValue().includes('else')")
        return page.evaluate("editor.session.getValue()").splitlines()

    def test_adds_labeled_else_before_end(self, app_url, page):
        lines = self._add_via_ui(page, SINGLE_MESSAGE_ALT, 1, "failure")
        assert lines[3:7] == [
            "alt success",
            "Alice -> Bob: granted",
            "else failure",
            "end",
        ]

    def test_empty_label_adds_bare_else(self, app_url, page):
        lines = self._add_via_ui(page, SINGLE_MESSAGE_ALT, 0, "")
        assert lines[3:6] == ["alt success", "else", "Alice -> Bob: granted"]

    def test_diagram_rerenders_with_the_new_branch(self, app_url, page):
        self._add_via_ui(page, SINGLE_MESSAGE_ALT, 1, "failure")
        page.wait_for_function(
            "() => Array.from(document.querySelectorAll('#colb svg text'))"
            ".some(t => t.textContent === '[failure]')",
            timeout=15000,
        )

    def test_message_hover_is_suppressed_in_else_mode(self, app_url, page):
        _start_else_mode(page, SINGLE_MESSAGE_ALT)
        assert page.evaluate("isSequenceAddMode()") is True


class TestElseSlotYs:
    """computeElseSlotYs on hand-built inputs (no tab -> header fallback height)."""

    _CASE = """([slots, messages]) => {
        const rect = document.createElementNS('http://www.w3.org/2000/svg', 'rect');
        rect.setAttribute('x', '10'); rect.setAttribute('y', '50');
        rect.setAttribute('width', '100'); rect.setAttribute('height', '150');
        const group = {headerIndex: 3, endIndex: 10, elseSlots: slots};
        return computeElseSlotYs(rect, group, messages).map(s => [s.lineIndex, s.y]);
    }"""

    def test_message_and_end_slots(self, app_url, page):
        # tab bottom = 50 + 17 = 67, box bottom = 200
        messages = [{"index": 4, "cy": 90}, {"index": 6, "cy": 130}]
        result = page.evaluate(self._CASE, [[4, 6, 10], messages])
        assert result == [
            [4, (67 + 90) / 2],
            [6, (90 + 130) / 2],
            [10, (130 + 200) / 2],
        ]

    def test_empty_group_end_slot(self, app_url, page):
        assert page.evaluate(self._CASE, [[10], []]) == [[10, (67 + 200) / 2]]

    def test_messages_outside_the_group_are_ignored(self, app_url, page):
        messages = [
            {"index": 1, "cy": 20},
            {"index": 4, "cy": 90},
            {"index": 12, "cy": 300},
        ]
        result = page.evaluate(self._CASE, [[4, 10], messages])
        assert result == [[4, (67 + 90) / 2], [10, (90 + 200) / 2]]


class TestGroupModalRouting:
    """submitGroup sends the request for the current groupModalMode."""

    _SUBMIT = """async (mode) => {
        groupOperationEventListeners();
        document.getElementById('colb').innerHTML =
            '<svg><g><rect fill="none" x="1" y="2"></rect></g></svg>';
        const rect = document.querySelector('#colb rect');
        lastclickedsvgelement = rect;
        pendingElse = {groupRect: rect, beforeLineIndex: 5};
        groupModalMode = mode;
        const calls = [];
        const realFetch = window.fetch;
        window.fetch = (url, opts) => {
            calls.push([String(url), JSON.parse(opts.body)]);
            return Promise.resolve({json: () => Promise.resolve({error: 'stub'})});
        };
        await submitGroup();
        window.fetch = realFetch;
        return {calls, modeAfter: groupModalMode};
    }"""

    def test_else_mode_posts_add_seq_else(self, app_url, page):
        result = page.evaluate(self._SUBMIT, "else")
        route, body = result["calls"][0]
        assert route == "addSeqElse"
        assert body["beforeLineIndex"] == 5
        assert body["svgelement"].startswith("<rect")

    def test_rename_mode_posts_rename(self, app_url, page):
        assert page.evaluate(self._SUBMIT, "rename")["calls"][0][0] == "renameSeqGroup"

    def test_add_mode_posts_add_group(self, app_url, page):
        assert page.evaluate(self._SUBMIT, "add")["calls"][0][0] == "addGroup"

    # The server rejects the first submit, so the modal stays open; the user
    # presses Submit again. The second request must be the same kind.
    _RESUBMIT = """async ([mode, responses]) => {
        groupOperationEventListeners();
        document.getElementById('colb').innerHTML =
            '<svg><g><rect fill="none" x="1" y="2"></rect></g></svg>';
        const rect = document.querySelector('#colb rect');
        lastclickedsvgelement = rect;
        pendingElse = {groupRect: rect, beforeLineIndex: 5};
        groupModalMode = mode;
        const calls = [];
        const realFetch = window.fetch;
        window.fetch = (url, opts) => {
            calls.push([String(url), JSON.parse(opts.body)]);
            const data = responses[calls.length - 1];
            return Promise.resolve({json: () => Promise.resolve(data)});
        };
        await submitGroup();
        await submitGroup();
        window.fetch = realFetch;
        return {calls, modeAfter: groupModalMode, pendingAfter: pendingElse};
    }"""

    @pytest.mark.parametrize(
        ("mode", "route"), [("else", "addSeqElse"), ("rename", "renameSeqGroup")]
    )
    def test_resubmit_after_error_repeats_the_request(self, app_url, page, mode, route):
        errors = [{"error": "rejected"}, {"error": "rejected"}]
        result = page.evaluate(self._RESUBMIT, [mode, errors])
        assert [c[0] for c in result["calls"]] == [route, route]
        assert result["calls"][0][1] == result["calls"][1][1]

    def test_success_resets_the_modal_state(self, app_url, page):
        responses = [{"error": "rejected"}, {"plantuml": "@startuml\n@enduml"}]
        result = page.evaluate(self._RESUBMIT, ["else", responses])
        assert [c[0] for c in result["calls"]] == ["addSeqElse", "addSeqElse"]
        assert result["modeAfter"] == "add"
        assert result["pendingAfter"] is None
