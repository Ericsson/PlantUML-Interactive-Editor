
function sequenceEventListeners() {

    const sequenceList = [{
        id: 'addParticipant',
        endpoint: 'addParticipant',
        arguments: {}
    }];

    sequenceList.forEach(item => {
        document.getElementById(item.id).addEventListener('click', async () => {
            const element = document.getElementById('colb');
            const svg = element.querySelector('g');
            try {
                const plantuml = trimlines(editor.session.getValue());
                const toBeStringified = {
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML,
                }
                if (item.arguments) {
                    for (let [key, value] of Object.entries(item.arguments)) {
                        toBeStringified[key] = value;
                    }
                }
                const response = await fetch(item.endpoint, {
                    method: 'POST',
                    headers: {
                        'Content-Type': 'application/json'
                    },
                    body: JSON.stringify(toBeStringified)
                });
                const pumlcontentcode = await response.text();
                setPuml(pumlcontentcode);
            } catch (error) {
                displayErrorMessage(`Error with fetch API: ${error.message}`, error);
            }
        });
    });
}

async function handleContextMenuBackground(svgelement) {
    const background = document.getElementById('colb-container')
    background.addEventListener('contextmenu', function (e) {

        e.preventDefault();

        // Get coordinates of click relative to the svg
        let point = svgelement.createSVGPoint();
        point.x = e.clientX;
        point.y = e.clientY;
        let transformedPoint = point.matrixTransform(svgelement.getScreenCTM().inverse());

        console.log("Click Coordinates relative to <g> - X:", transformedPoint.x, "Y:", transformedPoint.y);

        var contextMenu = document.getElementById('sequence-menu');
        contextMenu.style.display = 'block';
        contextMenu.style.left = e.pageX + 'px';
        contextMenu.style.top = e.pageY + 'px';
    });
}



async function setHandlersForSequenceDiagram(pumlcontent, element) {
    fetchSvgFromPlantUml().then((svgContent) => {
        element.innerHTML = svgContent;
        const svgContainer = element.querySelector('svg');
        const svg = element.querySelector('g')
        if (!svg) {
            toggleLoadingOverlay();
            return
        }
        const svgelements = svg.querySelectorAll('*');
        handleContextMenuBackground(svgContainer);


        toggleLoadingOverlay();

    }).catch((error) => {
        displayErrorMessage(`Error rendering SVG: ${error.message}`, error);
    });
}
