# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2026 Ericsson

"""Regression test: the activity note context menu ('note-menu') must close
on an outside click, same as the other activity context menus. It was
previously mixed up with the sequence note menu id ('seq-note-menu') in the
activity outside-click handler, so it never closed."""


def test_activity_note_menu_closes_on_outside_click(app_url, page):
    page.wait_for_timeout(1000)

    menu_display_after_open, menu_display_after_outside_click = page.evaluate(
        """() => {
            const menu = document.getElementById('note-menu');
            menu.style.display = 'block';
            menu.style.left = '10px';
            menu.style.top = '10px';
            const afterOpen = menu.style.display;

            document.dispatchEvent(new MouseEvent('click', {bubbles: true}));

            const afterOutsideClick = menu.style.display;
            return [afterOpen, afterOutsideClick];
        }"""
    )

    assert menu_display_after_open == "block"
    assert menu_display_after_outside_click == "none"
