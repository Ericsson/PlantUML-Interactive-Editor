# SPDX-License-Identifier: MIT
#
# MIT License
#
# Copyright (c) 2026 Ericsson

"""Regression probes for the sequence modal submit buttons.

The group/note/box submit buttons used to carry inline ``onclick`` attributes.
A browser runs those, but a strict Content-Security-Policy (the VS Code webview
the frontend is reused in) refuses inline event handlers, so the buttons did
nothing there. They are now wired with JavaScript-attached listeners, like the
message/participant submit buttons already were. These tests lock that in:
no inline handler survives, and a click actually reaches the backend.
"""


class TestSequenceSubmitButtons:
    def test_submit_buttons_have_no_inline_onclick(self, app_url, page):
        result = page.evaluate(
            """() => ({
                group: document.getElementById('seq-submit-group').getAttribute('onclick'),
                note: document.getElementById('seq-submit-note').getAttribute('onclick'),
                box: document.getElementById('seq-submit-box').getAttribute('onclick'),
            })"""
        )
        assert result == {"group": None, "note": None, "box": None}

    def test_clicking_group_submit_reaches_the_backend(self, app_url, page):
        # Wire the listeners (as sequenceEventListeners does on a real render),
        # stub fetch to capture the call, then click the button natively.
        called = page.evaluate(
            """async () => {
                groupOperationEventListeners();
                document.getElementById('colb').innerHTML =
                    '<svg viewBox="0 0 300 200"><g></g></svg>';

                const calls = [];
                const realFetch = window.fetch;
                window.fetch = (url, opts) => {
                    calls.push(String(url));
                    return Promise.resolve({
                        json: () => Promise.resolve({ plantuml: editor.session.getValue() })
                    });
                };

                groupEditMode = false;
                selectedGroupType = 'group';
                const submit = document.getElementById('seq-submit-group');
                submit.dataset.startIndex = '2';
                submit.dataset.endIndex = '3';

                submit.dispatchEvent(new MouseEvent('click', { bubbles: true }));
                await new Promise((r) => setTimeout(r, 50));

                window.fetch = realFetch;
                return calls;
            }"""
        )
        assert any("addGroup" in url for url in called)
