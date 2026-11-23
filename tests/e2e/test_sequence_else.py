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
