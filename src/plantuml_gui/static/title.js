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

// Identify PlantUML's title, across renderer versions.
//
// Older PlantUML wrapped the title in an invisible bounding <rect>
// (stroke:#00000000;...;fill:none;). Newer PlantUML (>= ~1.2024) dropped that
// rect and renders the title only as bold, font-size-14 <text> element(s) at
// the top of the diagram. Both detectors are used so the title stays editable
// regardless of the installed PlantUML version.

// Old-PlantUML title bounding rect. It is the only rect with this exact
// transparent-stroke / no-fill style; height > 6 excludes hairline rects.
function checkIfTitleRect(svgelements, index) {
    if (svgelements[index]) {
        return (svgelements[index].tagName.toLowerCase() === 'rect') && parseFloat(svgelements[index].getAttribute('height')) > 6 &&
            (svgelements[index].getAttribute('style') == "stroke:#00000000;stroke-width:1.0;fill:none;")
    }
}

// New-PlantUML title text. Title lines are bold and font-size 14; participant
// names are font-size 14 but not bold, and group labels / messages use
// font-size 13/11, so bold + size 14 uniquely identifies title text in both
// activity and sequence diagrams. (Old PlantUML also emits the title this way,
// so this matches there too - the rect and the text both map to the title.)
function isTitleText(svgelement) {
    return !!svgelement && svgelement.tagName.toLowerCase() === 'text' &&
        svgelement.getAttribute('font-size') === '14' &&
        svgelement.getAttribute('font-weight') === 'bold';
}

// Make a title element open the shared title modal on double-click.
//
// For the old bounding rect: PlantUML gives it fill:none (whose interior does
// not capture pointer events), so set a transparent fill via the fill
// *attribute* (dropping fill from the style) - the whole rect area becomes a
// click target while a caller can still recolor it on hover.
//
// For the title text: diagram handlers set font-size-14 text to
// pointer-events:none (participant names), so re-enable pointer events on the
// title text explicitly and show a pointer cursor.
function makeTitleDoubleClickable(svgelement, svg, pumlcontent) {
    if (svgelement.tagName.toLowerCase() === 'rect') {
        svgelement.setAttribute('fill', 'transparent');
        svgelement.setAttribute('style', 'stroke:#00000000;stroke-width:1.0;');
    } else {
        svgelement.style.pointerEvents = 'auto';
        svgelement.style.cursor = 'pointer';
    }
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

// Find the title (bounding rect on old PlantUML, or bold font-size-14 text on
// newer PlantUML) among svgelements and make it double-click editable. A
// multi-line title yields one text element per line, all of which become
// editable. Used by both the activity and sequence render handlers.
function setupTitleHandler(svgelements, svg, pumlcontent) {
    for (let index = 0; index < svgelements.length; index++) {
        if (checkIfTitleRect(svgelements, index) || isTitleText(svgelements[index])) {
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
