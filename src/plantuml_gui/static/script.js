// SPDX-License-Identifier: MIT

// MIT License

// Copyright (c) 2024 Ericsson

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

let lastclickedsvgelement = "";
let fline = -1;
let history = [];
let historyPointer = -1;
let editor;
let colorqueue = [];
var Range = ace.require("ace/range").Range

async function initeditor() {
    editor = ace.edit("editor")
    editor.setTheme("ace/theme/dracula")
    ace.config.setModuleUrl(
        "ace/mode/plantuml",
        "/static/mode-plantuml.js" // Adjust to the correct path where your file is hosted
      );
    editor.session.setMode("ace/mode/plantuml")
    editor.session.setOption("useWorker", false); // disables syntax validation
    hash = getHashParameter();
    if (hash) {
        try {
            const response = await fetch("decode", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'hash': hash
                })
            })
            const res = await response.text()
            setPuml(res)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }

    } else {
        setDemo();
    }

    document.getElementById('editor').style.visibility = 'visible';
    editor.session.on('change', function() {
        debouncedRenderPlantUml(); // Using the debounced version avoids unnecessary API calls
    });

    editor.session.selection.on('changeCursor', function(e) {
        clearMarkers()
        // Add the changeCursor event listener when the editor is clicked
        cursorChangeListener()
    });
    console.log("Editor initialization done.")
}

function findChangedLines() {
    if (history.length < 2) return; // No previous version to compare

    const prevText = history[historyPointer - 1];
    const currText = history[historyPointer];

    let changes = Diff.diffLines(prevText, currText);
    let changedIndexes = [];
    let currIndex = 0;

    changes.forEach(part => {
        if (part.added) {
            // Newly added lines - mark as changed
            let newLines = part.value.split('\n').filter(line => line !== "");
            for (let i = 0; i < newLines.length; i++) {
                changedIndexes.push(currIndex + i);
            }
        }
        if (!part.removed) {
            // Unchanged lines still affect the index tracking
            let removedLines = part.value.split('\n').filter(line => line !== "");
            currIndex += removedLines.length;
        }
    });

    getmarkersinglelines(changedIndexes);
}

const cursorChangeListener = async function(e) {
    const svg = element.querySelector('g');
    resetHighlight(svg);

    let start = editor.getCursorPosition().row;
    const line = editor.session.getLine(start).trimStart();
    if (!line.startsWith(':') && !line.startsWith('#')) {
        return;
    }
    let end = start;
    const lastRow = editor.session.getLength() - 1;

    // Make sure we don't go out of bounds
    while (end <= lastRow && !editor.session.getLine(end).trim().endsWith(';')) {
        end++;
    }

    const lines = editor.session.getLines(start, end);
    let text = lines.join('\n');
    text = (text.match(/:(.*?);/s) || [])[1]?.trim(); // get text between : and ;

    highlightActivity(svg, text);
};

function initialize() {
    indentPuml(editor.session.getValue())
    renderPlantUml();
    addUtilEventListeners();
    console.log("PlantUML initialization done.")
}



function displayErrorMessage(message, error) {
    console.error(error);
    const errorDisplay = document.getElementById('popup');
    errorDisplay.innerText = message; // Display only the error message
    document.getElementById('popup').style.visibility = "visible";
}

// Catch errors and display only the error message text
window.onerror = function(message, source, lineno, colno, error) {
    displayErrorMessage(message, error);
    return false;
};

window.onunhandledrejection = function(event) {
    displayErrorMessage(`Unhandled rejection: ${event.reason}`, event);
    event.preventDefault(); // Prevent default browser behavior
};

function setDemo() {
    puml = `@startuml
title
This is not an ordinary PlantUML editor!
Try double-click me to change the title!
endtitle
start
#lightyellow:Right-click to open the menu and choose
"Add Below" to add new activities below;
if (Right-click me to add elements\\nto the different branches) then (yes)
:To delete this Activity, either delete all the text
or choose "Delete" in the menu!;
switch (Right-click me\\nand choose "switch again"\\nto add another process)
case ( condition 1)
:Activity;
case ( Double-click me to edit the text!)
:Activity;
endswitch
#red:Activity;
(C)
else (no)
:To edit the activity either double-click
or press "Edit Text" in the menu;
group group
if (Statement) then (yes)
:Activity;
else (no)
#lightgreen:[[https://ericsson.com Link to Ericsson]] Try clicking the
link inside this activity!;
fork
:To add an arrow-label to
this activity, open the menu!;
stop
fork again
:Try deleting me and
pressing CTRL + Z to undo!;
fork again
:action;
note right
You can press CTRL + ENTER
to submit text when editing!
end note
end merge
endif
end group
endif
detach
:To add a note choose "Add Note" in the menu;
detach
(C)
:Activity;
note right
Try toggling the side of the
note by using the menu!
end note
stop
@enduml`;
        setPuml(puml)
}

function setSequence() {
    puml = `@startuml
participant bob
participant fred
participant participant3
bob -> fred: hello
bob -> participant3: hello!
participant3 -> participant3: test
@enduml`;
        setPuml(puml)
}

function buttonEventListeners() {

    document.getElementById('demo').addEventListener('click', function() {
    setDemo()
    });

    document.getElementById('clear').addEventListener('click', function() {
        puml = "@startuml\nstart\n@enduml"
        setPuml(puml)
    });

    document.getElementById('sequence').addEventListener('click', function() {
        setSequence()
        });

    document.getElementById('undo').addEventListener('click', function() {
        undoeditor();

    });

    document.getElementById('restore').addEventListener('click', function() {
        restoreeditor();

    });

    document.getElementById('load').addEventListener('click', function() {
        document.getElementById('file-input').click()
    });

    document.getElementById('file-input').addEventListener('change', function(event) {
        const file = event.target.files[0];
        const reader = new FileReader();
        reader.onload = () => editor.session.setValue(reader.result);
        reader.readAsText(file);
    });

    document.getElementById('save').addEventListener('click', async function() {
        // Open the "Save As" dialog
        const handle = await window.showSaveFilePicker({
          suggestedName: "untitled.txt",
          types: [
            {
              description: "Text Files",
              accept: { "text/plain": [".txt"] },
            },
          ],
        });

        // Create a writable stream
        const writable = await handle.createWritable();

        // Get editor content (Ace Editor example)
        const content = editor.session.getValue();

        // Write the content
        await writable.write(content);

        // Close the file
        await writable.close();
    });

    function download(filename, text) {
    //   var element = document.createElement('a');
    //   element.setAttribute('href', 'data:text/plain;charset=utf-8,' + encodeURIComponent(text));
    //   element.setAttribute('download', filename);

    //   element.style.display = 'none';
    //   document.body.appendChild(element);

    //   element.click();

    //   document.body.removeChild(element);
    }

    document.getElementById('addTitleButton').addEventListener('click', async () => {
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("addTitle", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml
                })
            });
            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })

    document.getElementById('png').addEventListener('click', async () => {
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("/renderPNG", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml
                })
            });

            const blob = await response.blob();
            const imageUrl = URL.createObjectURL(blob);
            const newTab = window.open('', '_blank');

            const img = newTab.document.createElement('img');
            img.src = imageUrl;
            newTab.document.body.appendChild(img);
            newTab.document.body.style.textAlign = 'center';
            newTab.document.close();

        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });






    document.getElementById('copybutton').addEventListener('click', function() {
        navigator.clipboard.writeText(editor.session.getValue())

    });


    document.getElementById('pastebutton').addEventListener('click', function() {
        navigator.clipboard.readText().then(function(text) {
            setPuml(text)
        }).catch(function(err) {
            console.error('Failed to read clipboard contents: ', err);
        });
    });

}

function commandEventListeners() {
    document.addEventListener('keydown', function(event) {
        if (event.ctrlKey && event.key === "z") {
            event.preventDefault();
            undoeditor();
        }

        if (event.ctrlKey && event.key === "y") {
            event.preventDefault();
            restoreeditor();
        }


        if (event.ctrlKey && event.key === 'Enter') {
            event.preventDefault();

            var activityModal = document.getElementById('modalForm');
            if ($(activityModal).hasClass('show')) {
                document.getElementById('submit').click();
            }

            var arrowModal = document.getElementById('modalFormArrow');
            if ($(arrowModal).hasClass('show')) {
                document.getElementById('submit-arrow').click();
            }
            var ifModal = document.getElementById('modalFormif');
            if ($(ifModal).hasClass('show')) {
                document.getElementById('submitif').click();
            }

            var switchModal = document.getElementById('modalFormswitch');
            if ($(switchModal).hasClass('show')) {
                document.getElementById('submitswitch').click();
            }

            var titleModal = document.getElementById('modalFormTitle');
            if ($(titleModal).hasClass('show')) {
                document.getElementById('submit-title').click();
            }

            var noteModal = document.getElementById('modalFormNote');
            if ($(noteModal).hasClass('show')) {
                document.getElementById('submit-note').click();
            }

            var groupModal = document.getElementById('modalFormGroup');
            if ($(groupModal).hasClass('show')) {
                document.getElementById('submit-group').click();
            }

            var whileModal = document.getElementById('modalFormWhile');
            if ($(whileModal).hasClass('show')) {
                document.getElementById('submitwhile').click();
            }

            var connectorModal = document.getElementById('modalFormConnector');
            if ($(connectorModal).hasClass('show')) {
                document.getElementById('submit-connector').click();
            }

            var participantModal = document.getElementById('participant-modalForm');
            if ($(participantModal).hasClass('show')) {
                document.getElementById('submit-participant-message').click();
            }

            var participantModal = document.getElementById('participant-name-modalForm');
            if ($(participantModal).hasClass('show')) {
                document.getElementById('submit-participant-name').click();
            }
        }
    });
}


function addUtilEventListeners() {
    buttonEventListeners();
    commandEventListeners();

}

function addActivityEventListeners() {
    activityEventListeners();
    ifEventListeners();
    ellipseEventListeners();
    titleEventListeners();
    forkEventListeners();
    noteEventListeners();
    groupEventListeners();
    mergeEventListeners();
    whileEventListeners();
    connectorEventListeners();
    bottomForkEventListeners();
    arrowLabelEventListeners();
    switchEventListeners();

    // turn of menus when clicking anywhere.
    document.addEventListener('click', function(e) {
        var menuIds = [
            'activity-menu',
            'ellipse-menu',
            'if-menu',
            'fork-menu',
            'note-menu',
            'group-menu',
            'merge-menu',
            'while-menu',
            'connector-menu',
            'arrowlabel-menu',
            'repeat-menu',
            'backward-menu',
            'forkbottom-menu',
            'switch-menu',
            'title-menu'
        ];

        menuIds.forEach(function(id) {
            var menu = document.getElementById(id);
            if (menu) {
                menu.style.display = 'none';
            }
        });
    });

}


function addSequenceEventListeners() {
    sequenceEventListeners()

    document.addEventListener('click', function(e) {
        var menuIds = [
            'sequence-menu'
        ];

        menuIds.forEach(function(id) {
            var menu = document.getElementById(id);
            if (menu) {
                menu.style.display = 'none';
            }
        });
    });
}

function saveToHistory(puml) {
    if (puml === "") {
        return; // Avoid saving empty strings
    }

    if (historyPointer >= 0 && history[historyPointer] === puml) {
        return
    }

    history = history.slice(0, historyPointer + 1);
    history.push(puml);
    historyPointer++
}

function debounce(func, wait) {
    let timeout;
    return function(...args) {
        clearTimeout(timeout);
        timeout = setTimeout(() => func.apply(this, args), wait);
    };
}

const debouncedRenderPlantUml = debounce(async () => {
    await renderPlantUml();
    findChangedLines(); // Ensure this runs only after rendering is finished
}, 200);

async function fetchSvgFromPlantUml() {
    try {
        const plantuml = editor.session.getValue();
        const response = await fetch("render", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'plantuml': plantuml
            })
        });
        const svg = await response.text()
        return svg
    } catch (error) {
        console.error('Error with render fetch api?', error);
    }
}

function toggleLoadingOverlay() {
    const overlay = document.getElementById('loading-overlay');
    if (overlay.style.display === 'none' || overlay.style.display === '') {
        overlay.style.display = 'block';
    } else {
        overlay.style.display = 'none';
    }
}



async function renderPlantUml() {
    if (document.getElementById('popup').style.visibility = "visible") {
        document.getElementById('popup').style.visibility = "hidden"; // Hide the error popup when rendering again.
    }
    toggleLoadingOverlay();
    let element = document.getElementById('colb')
    const pumlcontent = trimlines(editor.session.getValue());
    saveToHistory(pumlcontent);
    try {
        const plantuml = trimlines(editor.session.getValue());
        const response = await fetch("encode", {
            method: "POST",
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'plantuml': plantuml
            })
        });
        const res = await response.text()
        var url = window.location.href;
        var x = url.indexOf("?");
        if (x == -1)
            url = url + "?" + res;
        else
            url = url.substr(0, x) + "?" + res;
        window.history.replaceState(null, '', url);
    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }

    switch (checkDiagramType(pumlcontent)) {
        case "activity":
            setHandlersForActivityDiagram(pumlcontent, element);
            break;
        case "sequence":
            setHandlersForSequenceDiagram(pumlcontent, element);
            break;
        default:
            fetchSvgFromPlantUml().then((svgContent) => {
                element.innerHTML = svgContent;
            });
            toggleLoadingOverlay();
    }
}

function setPuml(pumlcontent) {
    text = processForkAndSwitch(pumlcontent)
    text = indentPuml(text)
    editor.session.setValue(text)
}

function indentPuml(pumlcontent) {
    const lines = pumlcontent.split('\n');
    let indentedLines = [];
    let level = 0;

    // Keywords that increase indentation level
    const increaseIndentKeywords = ["If", "if", "while", "group", "partition", "fork", "repeat", "switch"]
    // Keywords that should go back one level and then keep same level
    const sameIndentKeywords = ["else", "fork again", "case"]
    // Keywords that decrease indentation level
    const decreaseIndentKeywords = ["endif", "endwhile", "end group", "}", "end fork", "endfork", "end merge", "repeat while", "repeatwhile", "endswitch"]

    lines.forEach(line => {
        const trimmedLine = line.trim();

        if (trimmedLine.startsWith("repeat while") || trimmedLine.startsWith("repeatwhile")) {
            level--;
            indentedLines.push('    '.repeat(level) + trimmedLine);
            return
        }

        if ((trimmedLine.startsWith('fork') && !trimmedLine.startsWith('fork again')) || trimmedLine == "repeat") {
            indentedLines.push('    '.repeat(Math.max(0, level)) + trimmedLine);
            level++;
            return
        }


        // Adjust indentation before appending the line if it is an end statement
        if (decreaseIndentKeywords.some(keyword => trimmedLine.startsWith(keyword))) {
            level--;
        }

        if (sameIndentKeywords.some(keyword => trimmedLine.startsWith(keyword))) {
            indentedLines.push('    '.repeat(Math.max(0, level - 1)) + trimmedLine);
            return

        } else {
            indentedLines.push('    '.repeat(Math.max(0, level)) + trimmedLine);
        }

        // Adjust indentation after appending the line if it is a start statement
        if (increaseIndentKeywords.some(keyword => trimmedLine.startsWith(keyword))) {
            level++;
        }
    });

    return indentedLines.join('\n');
}

function getHashParameter() {
    const query = window.location.search.substring(1); // Remove the leading "?"
    return query ? query : null;
}

function resetHighlight(svg) {
    if (svg) {
        const rects = svg.getElementsByTagName("rect");

        for (let i = 0; i < rects.length; i++) {
            const rect = rects[i];
            if (checkIfActivity(rects, i)) {
                if (rect.getAttribute('fill') == "#d8d8d8") {
                    rect.setAttribute('fill', colorqueue.shift())
                }
            }
        }
        colorqueue = []
    }
}

function trimlines(pumlcontent) {

    return pumlcontent.split('\n').map(line => line.trim()).join('\n');

}

function getmarker(bounds) {
    clearMarkers()
    editor.session.addMarker(new Range(bounds[0], 0, bounds[1], 200), "hover", "fullLine");

}

function getmarkersinglelines(bounds) {
    clearMarkers()
    if (typeof bounds === 'number') {
        editor.session.addMarker(new Range(bounds, 0, bounds, 200), "hover", "fullLine");
    } else {
        for (let bound of bounds) {
            editor.session.addMarker(new Range(bound, 0, bound, 200), "hover", "fullLine");
        }
    }
}

function clearMarkers() {
    const prevMarkers = editor.session.getMarkers();

    if (prevMarkers) {
        const prevMarkersArr = Object.keys(prevMarkers);

        for (let item of prevMarkersArr) {
            const marker = prevMarkers[item];

            // Remove marker if it isnt the active line
            if (marker.clazz == "hover") {
                editor.session.removeMarker(marker.id);
            }
        }
    }
}

function undoeditor() {
    if (historyPointer > 0) {
        historyPointer--;
        setPuml(history[historyPointer])
    }
}

function restoreeditor() {
    if (historyPointer < history.length - 1) {
        historyPointer++;
        setPuml(history[historyPointer])
    }
}


function checkDiagramType(puml) {
    const activityKeywords = ["if", "while", "fork", "repeat", "switch", "start", "stop", ":"];
    const sequenceKeywords = ["state", "actor", "boundary", "control", "entity", "database", "collections", "queue", "participant"];

    // Configurable ignored block definitions
    const ignoreBlocks = [
        { start: /^note\b/, end: /^end\s*note\b/ },
    ];

    const lines = puml.split('\n');
    const filteredLines = [];

    let ignoring = false;
    let currentBlock = null;
    let inMultilineActivity = false;

    for (let i = 0; i < lines.length; i++) {
        const trimmed = lines[i].trim().toLowerCase();

        // Handle end of ignore blocks
        if (ignoring && currentBlock?.end.test(trimmed)) {
            ignoring = false;
            currentBlock = null;
            filteredLines.push(trimmed); // include end line
            continue;
        }

        // Handle start of ignore blocks
        if (!ignoring) {
            const block = ignoreBlocks.find(b => b.start.test(trimmed));
            if (block) {
                ignoring = true;
                currentBlock = block;
                filteredLines.push(trimmed); // include the start line
                continue;
            }
        }

        // Handle multiline activity block
        if (!inMultilineActivity && /^:.*/.test(trimmed) && !/;/.test(trimmed)) {
            inMultilineActivity = true;
            filteredLines.push(trimmed); // include the start line
            continue;
        }

        if (inMultilineActivity) {
            if (/.*;/.test(trimmed)) {
                inMultilineActivity = false;
                continue;
            }
            continue; // skip lines that are inside a multiline activity
        }

        if (!ignoring) {
            filteredLines.push(trimmed);
        }
    }

    // Analyze filtered lines
    let foundSequence = false;

    for (const line of filteredLines) {
        if (sequenceKeywords.some(keyword => line.startsWith(keyword))) {
            foundSequence = true;
        }
        if (/\b\w+\s*(->|-->|<--|<-)\s*\w+/.test(line)) { // message arrows in sequence diagrams
            foundSequence = true;
        }
    }

    if (foundSequence) {
        addSequenceEventListeners();
        return "sequence";
    }

    for (const line of filteredLines) {
        if (activityKeywords.some(keyword => line.startsWith(keyword))) {
            addActivityEventListeners();
            return "activity";
        }
    }

    return "unknown";
}
