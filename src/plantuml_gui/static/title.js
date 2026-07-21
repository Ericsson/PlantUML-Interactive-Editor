// MIT License

// Copyright (c) 2026 Ericsson

// Permission is hereby granted, free of charge, to any person obtaining a copy
// of this software and associated documentation files (the "Software"), to deal
// in the Software without restriction, including without limitation the rights
// to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
// copies of the Software, and to permit persons to whom the Software is
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in all
// copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
// OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
// SOFTWARE.

// Shared diagram-title editing, used by both activity and sequence diagrams.
// PlantUML renders a title as text inside an invisible bounding <rect>. This
// module owns detecting that rect (checkIfTitleRect), making it double-click
// editable (makeTitleDoubleClickable / setupTitleHandler), and wiring the shared
// title modal + context-menu actions (titleEventListeners). The backend
// getTextTitle/editTitle/deleteTitle routes are diagram-agnostic (see
// shared/routes.py), so nothing here is specific to a diagram type.

// Identify PlantUML's invisible title bounding rect. It is the only rect with
// this exact transparent-stroke / no-fill style; height > 6 excludes hairline
// rects. Shared verbatim by the activity and sequence handlers.
function checkIfTitleRect(svgelements, index) {
    if (svgelements[index]) {
        return (svgelements[index].tagName.toLowerCase() === 'rect') && parseFloat(svgelements[index].getAttribute('height')) > 6 &&
            (svgelements[index].getAttribute('style') == "stroke:#00000000;stroke-width:1.0;fill:none;")
    }
}

// Make a title bounding rect open the shared title modal on double-click.
// PlantUML gives the rect fill:none (whose interior does not capture pointer
// events) and the title text drawn on top is set pointer-events:none by the
// diagram handlers. Set a transparent fill via the fill *attribute* (and drop
// fill from the style) so the whole rect area becomes a click target while a
// caller can still recolor it on hover by changing the fill attribute.
function makeTitleDoubleClickable(svgelement, svg, pumlcontent) {
    svgelement.setAttribute('fill', 'transparent');
    svgelement.setAttribute('style', 'stroke:#00000000;stroke-width:1.0;');
    svgelement.addEventListener('dblclick', async () => {
        lastclickedsvgelement = svgelement;
        try {
            const response = await fetch("getTextTitle", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': pumlcontent,
                    'svg': svg.innerHTML,
                    'svgelement': svgelement.outerHTML
                })
            });
            const text = await response.text();
            $('#title-text').val(text);
            $('#modalFormTitle').modal('show');
            $('#modalFormTitle').on('shown.bs.modal', function() {
                $('#title-text').trigger('focus')
            })
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });
}

// Find the title rect among svgelements and make it double-click editable.
// Used by the sequence handler (which has no single element-walk of its own for
// the title); the activity handler calls makeTitleDoubleClickable directly from
// its existing element walk so it can also attach its context menu and hover.
function setupTitleHandler(svgelements, svg, pumlcontent) {
    for (let index = 0; index < svgelements.length; index++) {
        if (checkIfTitleRect(svgelements, index)) {
            makeTitleDoubleClickable(svgelements[index], svg, pumlcontent);
        }
    }
}

// Wire the shared title modal submit and the title context-menu edit/delete
// items. Called once (see addUtilEventListeners) so it serves both diagram
// types without double-binding the handlers.
function titleEventListeners() {
    $('#submit-title').on('click', async () => {
        var text = $('#title-text').val();
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("editTitle", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'title': text
                }),
            });
            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })

    document.getElementById('editTitle').addEventListener('click', async () => {
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("getTextTitle", {

                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                })
            });
            const text = await response.text();

            $('#title-text').val(text);
            $('#modalFormTitle').modal('show');
            $('#modalFormTitle').on('shown.bs.modal', function() {
                $('#title-text').trigger('focus')
            })

        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }

    });

    document.getElementById('deleteTitle').addEventListener('click', async () => {
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("deleteTitle", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                }),
            });
            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })

}
