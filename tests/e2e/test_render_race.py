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

"""Regression test for the render-clobber race.

On load the app renders the activity demo; its SVG fetch is async. Switching
to the sequence demo starts a second render. If the (slower) activity render's
`.then` resolves after the sequence render has populated #colb, an unguarded
handler would write the stale activity SVG over the sequence diagram - leaving
#colb showing activity even though currentDiagramType is 'sequence'. This bit
CI on a cold PlantUML JAR (slow first render). renderPlantUml now tags each
render and the handlers drop a superseded result.

Here we force the race deterministically by delaying the activity /render
response (the one whose puml has no 'participant') so it always resolves after
the fast sequence render.
"""

import textwrap

# Injected before any app script runs: wrap window.fetch so the activity
# diagram's /render (the demo puml has no "participant") resolves ~1.5s late,
# while every other request - crucially the sequence /render - proceeds
# immediately. This delays in the browser via setTimeout (non-blocking), so it
# creates genuine concurrency: the sequence render finishes first and the stale
# activity render resolves afterwards, exactly the ordering that clobbered #colb
# in CI on a cold JAR. (A Playwright route handler with a blocking sleep cannot
# reproduce this - it serializes requests on the driver thread.)
_DELAY_ACTIVITY_RENDER = textwrap.dedent(
    """
    () => {
        const origFetch = window.fetch;
        window.fetch = function(url, opts) {
            const body = opts && opts.body ? String(opts.body) : '';
            const isRender = typeof url === 'string' && url.includes('render');
            if (isRender && !body.includes('participant')) {
                return new Promise((resolve) => {
                    setTimeout(() => resolve(origFetch(url, opts)), 1500);
                });
            }
            return origFetch(url, opts);
        };
    }
    """
)


def test_switching_to_sequence_is_not_clobbered_by_slow_activity_render(
    live_server, page
):
    page.add_init_script(_DELAY_ACTIVITY_RENDER)

    page.goto(live_server)
    # Switch to the sequence demo while the delayed activity render is still
    # in flight.
    page.click(".toolbar-btn.dropdown-toggle")
    page.wait_for_selector("#sequence", state="visible", timeout=15000)
    page.click("#sequence")

    # Wait past the induced activity-render delay so a stale, unguarded render
    # would have had time to overwrite #colb.
    page.wait_for_function(
        "() => participantLifelines && participantLifelines.length === 4",
        timeout=15000,
    )
    page.wait_for_timeout(2500)

    result = page.evaluate(
        """() => {
            const svg = document.querySelector('#colb svg');
            const participantRects = svg
                ? Array.from(svg.querySelectorAll('rect')).filter(r => {
                    const style = r.getAttribute('style') || '';
                    return r.hasAttribute('rx') && r.hasAttribute('ry') &&
                        style.includes('stroke-width:0.5');
                  }).length
                : 0;
            return {
                diagramType: currentDiagramType,
                participantRects,
                // Activity diagrams render an ellipse (start/stop); a clean
                // sequence diagram does not.
                hasEllipse: svg ? svg.querySelector('ellipse') !== null : false,
            };
        }"""
    )

    assert result["diagramType"] == "sequence"
    # The sequence demo has three participants (rounded header/footer rects);
    # if the activity render had clobbered #colb there would be none.
    assert result["participantRects"] > 0
    assert result["hasEllipse"] is False
