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
    editor.getSession().on('change', function() {
        debouncedRenderPlantUml(); // Using the debounced version avoids unnecessary API calls
    });

    editor.session.selection.on('changeCursor', function(e) {
        clearMarkers()
        // Add the changeCursor event listener when the editor is clicked
        cursorChangeListener()
    });
    console.log("Editor initialization done.")
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
    addEventListeners();
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

function activityEventListeners() {
    $('#submit').on('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');

        var newname = $('#message-text').val();
        try {

            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("editText", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'newname': newname,
                    'oldname': lastclickedsvgelement.textContent,
                    'svgelement': lastclickedsvgelement.outerHTML
                }),
            });
            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })

    activitylist = [{
            id: 'addConnectorActivityBelow',
            endpoint: 'addToActivity',
            arguments: {
                type: 'connector'
            }
        }, {
            id: 'addNoteActivity',
            endpoint: 'addNoteActivity',
            arguments: {
                type: 'note'
            }
        }, {
            id: 'addBelowWhile',
            endpoint: 'addToActivity',
            arguments: {
                type: 'while'
            }
        }, {
            id: 'addBelowRepeat',
            endpoint: 'addToActivity',
            arguments: {
                type: 'repeat'
            }
        }, {
            id: 'addBelowFork',
            endpoint: 'addToActivity',
            arguments: {
                type: 'fork'
            }
        }, {
            id: 'addBelowSwitch',
            endpoint: 'addToActivity',
            arguments: {
                type: 'switch'
            }
        }, {
            id: 'addBelowActivity',
            endpoint: 'addToActivity',
            arguments: {
                type: 'activity'
            }
        }, {
            id: 'addIfBelow',
            endpoint: 'addToActivity',
            arguments: {
                type: 'if'
            }
        }, {
            id: 'addStopBelow',
            endpoint: 'addToActivity',
            arguments: {
                type: 'stop'
            }
        }, {
            id: 'addStartBelow',
            endpoint: 'addToActivity',
            arguments: {
                type: 'start'
            }
        }, {
            id: 'addEndBelow',
            endpoint: 'addToActivity',
            arguments: {
                type: 'end'
            }
        }, {
            id: 'detachActivity',
            endpoint: 'detachActivity',
            arguments: {}
        }, {
            id: 'breakActivity',
            endpoint: 'breakActivity',
            arguments: {}
        }, {
            id: 'delete',
            endpoint: 'deleteActivity',
            arguments: {}
        }, {
            id: 'deletebackward',
            endpoint: 'deleteActivity',
            arguments: {}
        }, {
            id: 'addArrowLabelAbove',
            endpoint: 'addArrowLabel',
            arguments: {
                where: 'above'
            }
        }, {
            id: 'addArrowLabelBelow',
            endpoint: 'addArrowLabel',
            arguments: {
                where: 'below'
            }
        },

    ]

    activitylist.forEach(item => {
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

    document.getElementById('editactivityinmenu').addEventListener('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        try {

            const response = await fetch("getText", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });
            $('#message-text').val(await response.text());
            $('#modalForm').modal('show');
            $('#modalForm').on('shown.bs.modal', function() {
                $('#message-text').trigger('focus')
            })

        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    document.getElementById('editactivityinmenubackward').addEventListener('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        try {

            const response = await fetch("getText", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });
            $('#message-text').val(await response.text());
            $('#modalForm').modal('show');
            $('#modalForm').on('shown.bs.modal', function() {
                $('#message-text').trigger('focus')
            })

        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

}

function ifEventListeners() {
    $('#submitif').on('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');

        var statement = $('#statement').val();
        var branch1 = $('#branch1').val();
        var branch2 = $('#branch2').val();
        try {

            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("editTextIf", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'statement': statement,
                    'branch1': branch1,
                    'branch2': branch2,
                    'svgelement': lastclickedsvgelement.outerHTML
                }),
            });

            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })

    document.getElementById('editiftextmenu').addEventListener('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        const pumlcontent = trimlines(editor.session.getValue());
        try {

            const response = await fetch("getTextPoly", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': pumlcontent,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });
            const texts = await response.json();

            $('#statement').val(texts[0]);
            $('#branch1').val(texts[1]);
            $('#branch2').val(texts[2]);
            $('#modalFormif').modal('show');
            $('#modalFormif').on('shown.bs.modal', function() {
                $('#statement').trigger('focus')
            })



        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    document.getElementById('editiftextmenurepeat').addEventListener('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        const pumlcontent = trimlines(editor.session.getValue());
        try {

            const response = await fetch("getTextPoly", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': pumlcontent,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });
            const texts = await response.json();

            $('#statement').val(texts[0]);
            $('#branch1').val(texts[1]);
            $('#branch2').val(texts[2]);
            $('#modalFormif').modal('show');
            $('#modalFormif').on('shown.bs.modal', function() {
                $('#statement').trigger('focus')
            })



        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });


    const iflist = [{
        id: 'detachIf',
        endpoint: 'detachIf',
        arguments: {}
    }, {
        id: 'delIf',
        endpoint: 'delIf',
        arguments: {}
    }, {
        id: 'delIfrepeat',
        endpoint: 'delIf',
        arguments: {}
    }, {
        id: 'addbackwards',
        endpoint: 'addBackwards',
        arguments: {}
    }, {
        id: 'addleft',
        endpoint: 'addToIf',
        arguments: {
            where: 'left',
            type: 'activity'
        }
    }, {
        id: 'addright',
        endpoint: 'addToIf',
        arguments: {
            where: 'right',
            type: 'activity'
        }
    }, {
        id: 'addactivityrightrepeat',
        endpoint: 'addToIf',
        arguments: {
            where: 'right',
            type: 'activity'
        }
    }, {
        id: 'addleftif',
        endpoint: 'addToIf',
        arguments: {
            where: 'left',
            type: 'if'
        }
    }, {
        id: 'addrightif',
        endpoint: 'addToIf',
        arguments: {
            where: 'right',
            type: 'if'
        }
    }, {
        id: 'addrightifrepeat',
        endpoint: 'addToIf',
        arguments: {
            where: 'right',
            type: 'if'
        }
    }, {
        id: 'addrightforkrepeat',
        endpoint: 'addToIf',
        arguments: {
            where: 'right',
            type: 'fork'
        }
    }, {
        id: 'addrightswitchrepeat',
        endpoint: 'addToIf',
        arguments: {
            where: 'right',
            type: 'switch'
        }
    }, {
        id: 'addrightfork',
        endpoint: 'addToIf',
        arguments: {
            where: 'right',
            type: 'fork'
        }
    }, {
        id: 'addleftfork',
        endpoint: 'addToIf',
        arguments: {
            where: 'left',
            type: 'fork'
        }
    }, {
        id: 'addrightswitch',
        endpoint: 'addToIf',
        arguments: {
            where: 'right',
            type: 'switch'
        }
    }, {
        id: 'addleftswitch',
        endpoint: 'addToIf',
        arguments: {
            where: 'left',
            type: 'switch'
        }
    }, {
        id: 'addrightwhile',
        endpoint: 'addToIf',
        arguments: {
            where: 'right',
            type: 'while'
        }
    }, {
        id: 'addrightrepeat',
        endpoint: 'addToIf',
        arguments: {
            where: 'right',
            type: 'repeat'
        }
    }, {
        id: 'addrightwhilerepeat',
        endpoint: 'addToIf',
        arguments: {
            where: 'right',
            type: 'while'
        }
    }, {
        id: 'addleftwhile',
        endpoint: 'addToIf',
        arguments: {
            where: 'left',
            type: 'while'
        }
    }, {
        id: 'addleftrepeat',
        endpoint: 'addToIf',
        arguments: {
            where: 'left',
            type: 'repeat'
        }
    }, {
        id: 'addrightconnectorrepeat',
        endpoint: 'addToIf',
        arguments: {
            where: 'right',
            type: 'connector'
        }
    }];

    iflist.forEach(item => {
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

function ellipseEventListeners() {
    const ellipselist = [{
        id: 'addwhilebelowellipse',
        endpoint: 'addToEllipse',
        arguments: {
            where: 'below',
            type: 'while'
        }
    }, {
        id: 'addrepeatbelowellipse',
        endpoint: 'addToEllipse',
        arguments: {
            where: 'below',
            type: 'repeat'
        }
    }, {
        id: 'addconnectorbelowellipse',
        endpoint: 'addToEllipse',
        arguments: {
            where: 'below',
            type: 'connector'
        }
    }, {
        id: 'addforkbelowellipse',
        endpoint: 'addToEllipse',
        arguments: {
            where: 'below',
            type: 'fork'
        }
    }, {
        id: 'addswitchbelowellipse',
        endpoint: 'addToEllipse',
        arguments: {
            where: 'below',
            type: 'switch'
        }
    }, {
        id: 'ellipsedelete',
        endpoint: 'deleteEllipse',
        arguments: {}
    }, {
        id: 'addactivitybelowellipse',
        endpoint: 'addToEllipse',
        arguments: {
            where: 'below',
            type: 'activity'
        }
    }, {
        id: 'addifbelowellipse',
        endpoint: 'addToEllipse',
        arguments: {
            where: 'below',
            type: 'if'
        }
    }];

    ellipselist.forEach(item => {
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

function buttonEventListeners() {

    document.getElementById('demo').addEventListener('click', function() {
    setDemo()
    });


    document.getElementById('clear').addEventListener('click', function() {
        puml = "@startuml\nstart\n@enduml"
        setPuml(puml)
    });

    document.getElementById('undo').addEventListener('click', function() {
        undoeditor();

    });

    document.getElementById('restore').addEventListener('click', function() {
        restoreeditor();

    });

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

function forkEventListeners() {

    const forklist = [{
        id: 'deleteFork',
        endpoint: 'deleteFork',
        arguments: {}
    }, {
        id: 'forkAgain',
        endpoint: 'forkAgain',
        arguments: {}
    }, {
        id: 'forkToggle',
        endpoint: 'forkToggle',
        arguments: {}
    }, ];

    forklist.forEach(item => {
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

function switchEventListeners() {

    const forklist = [{
        id: 'delIfswitch',
        endpoint: 'delIf',
        arguments: {}
    }, {
        id: 'switchagain',
        endpoint: 'switchAgain',
        arguments: {}
    }];

    forklist.forEach(item => {
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

    document.getElementById('editiftextmenuswitch').addEventListener('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        const pumlcontent = trimlines(editor.session.getValue());
        try {

            const response = await fetch("getTextPoly", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': pumlcontent,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });
            const texts = await response.json();

            $('#switch-text').val(texts[0]);
            $('#modalFormswitch').modal('show');
            $('#modalFormswitch').on('shown.bs.modal', function() {
                $('#switch-text').trigger('focus')
            })



        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    });

    $('#submitswitch').on('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');

        var statement = $('#switch-text').val();
        try {

            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("editTextIf", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'statement': statement,
                    'branch1': "",
                    'branch2': "",
                    'svgelement': lastclickedsvgelement.outerHTML
                }),
            });

            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })

}


function bottomForkEventListeners() {
    const forklist = [{
        id: 'forkbottomtoggle',
        endpoint: 'forkToggle2',
        line: fline,
        arguments: {}
    }, {
        id: 'deletefork2',
        endpoint: 'deleteFork2',
        line: fline,
        arguments: {}
    }, {
        id: 'activityfork',
        endpoint: 'addToFork',
        line: fline,
        arguments: {
            type: 'activity'
        }
    }, {
        id: 'iffork',
        endpoint: 'addToFork',
        line: fline,
        arguments: {
            type: 'if'
        }
    }, {
        id: 'forkfork',
        endpoint: 'addToFork',
        line: fline,
        arguments: {
            type: 'fork'
        }
    }, {
        id: 'switchfork',
        endpoint: 'addToFork',
        line: fline,
        arguments: {
            type: 'switch'
        }
    }, {
        id: 'whilefork',
        endpoint: 'addToFork',
        line: fline,
        arguments: {
            type: 'while'
        }
    }, {
        id: 'repeatfork',
        endpoint: 'addToFork',
        line: fline,
        arguments: {
            type: 'repeat'
        }
    }, {
        id: 'connectorfork',
        endpoint: 'addToFork',
        line: fline,
        arguments: {
            type: 'connector'
        }
    }, {
        id: 'startfork',
        endpoint: 'addToFork',
        line: fline,
        arguments: {
            type: 'start'
        }
    }, {
        id: 'stopfork',
        endpoint: 'addToFork',
        line: fline,
        arguments: {
            type: 'stop'
        }
    }, {
        id: 'endfork',
        endpoint: 'addToFork',
        line: fline,
        arguments: {
            type: 'end'
        }
    }];


    forklist.forEach(item => {
        document.getElementById(item.id).addEventListener('click', async () => {
            const element = document.getElementById('colb');
            const svg = element.querySelector('g');
            try {
                const plantuml = trimlines(editor.session.getValue());
                const toBeStringified = {
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML,
                    'line': Number(lastclickedsvgelement.getAttribute('fline')),
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

function noteEventListeners() {
    $('#submit-note').on('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        var text = $('#note-text').val();
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("editNote", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML,
                    'text': text
                }),
            });
            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })

    const notelist = [{
        id: 'deleteNote',
        endpoint: 'deleteNote',
        arguments: {}
    }, {
        id: 'noteToggle',
        endpoint: 'noteToggle',
        arguments: {}
    }, ];

    notelist.forEach(item => {
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

    document.getElementById('noteEdit').addEventListener('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        try {
            const plantuml = trimlines(editor.session.getValue());

            const response = await fetch("getNoteText", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });
            $('#note-text').val(await response.text());
            $('#modalFormNote').modal('show');
            $('#modalFormNote').on('shown.bs.modal', function() {
                $('#note-text').trigger('focus')
            })


        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }

    })
}

function groupEventListeners() {

    $('#submit-group').on('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        var text = $('#group-text').val();
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("editGroup", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML,
                    'text': text
                }),
            });
            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })


    document.getElementById('deleteGroup').addEventListener('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');

        try {

            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("deleteGroup", {
                method: "POST",
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });
            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })

    document.getElementById('groupEdit').addEventListener('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        pumlcontent = trimlines(editor.session.getValue());
        try {

            const response = await fetch("getGroupText", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': pumlcontent,
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });
            $('#group-text').val(await response.text());
            $('#modalFormGroup').modal('show');
            $('#modalFormGroup').on('shown.bs.modal', function() {
                $('#group-text').trigger('focus')
            })


        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })
}

function mergeEventListeners() {
    const mergelist = [{
        id: 'addwhilemerge',
        endpoint: 'addToMerge',
        arguments: {
            type: 'while'
        }
    }, {
        id: 'addrepeatmerge',
        endpoint: 'addToMerge',
        arguments: {
            type: 'repeat'
        }
    }, {
        id: 'addactivitymerge',
        endpoint: 'addToMerge',
        arguments: {
            type: 'activity'
        }
    }, {
        id: 'addifmerge',
        endpoint: 'addToMerge',
        arguments: {
            type: 'if'
        }
    }, {
        id: 'addforkmerge',
        endpoint: 'addToMerge',
        arguments: {
            type: 'fork'
        }
    }, {
        id: 'addswitchmerge',
        endpoint: 'addToMerge',
        arguments: {
            type: 'switch'
        }
    }, {
        id: 'addstartmerge',
        endpoint: 'addToMerge',
        arguments: {
            type: 'start'
        }
    }, {
        id: 'addstopmerge',
        endpoint: 'addToMerge',
        arguments: {
            type: 'stop'
        }
    }, {
        id: 'addendmerge',
        endpoint: 'addToMerge',
        arguments: {
            type: 'end'
        }
    }];

    mergelist.forEach(item => {
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

function whileEventListeners() {
    $('#submitwhile').on('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');

        var statement = $('#whilestatement').val();
        var branch1 = $('#break').val();
        var branch2 = $('#loop').val();
        try {

            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("editTextWhile", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'whilestatement': statement,
                    'break': branch1,
                    'loop': branch2,
                    'svgelement': lastclickedsvgelement.outerHTML
                }),
            });

            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })


    const whilelist = [{
        id: 'delwhile',
        endpoint: 'delWhile',
        arguments: {}
    }, {
        id: 'addactivityloop',
        endpoint: 'addToWhile',
        arguments: {
            type: 'activity',
            where: 'loop'
        }
    }, {
        id: 'addactivitybreak',
        endpoint: 'addToWhile',
        arguments: {
            type: 'activity',
            where: 'break'
        }
    }, {
        id: 'addifloop',
        endpoint: 'addToWhile',
        arguments: {
            type: 'if',
            where: 'loop'
        }
    }, {
        id: 'addifbreak',
        endpoint: 'addToWhile',
        arguments: {
            type: 'if',
            where: 'break'
        }
    }, {
        id: 'addforkloop',
        endpoint: 'addToWhile',
        arguments: {
            type: 'fork',
            where: 'loop'
        }
    }, {
        id: 'addforkbreak',
        endpoint: 'addToWhile',
        arguments: {
            type: 'fork',
            where: 'break'
        }
    }, {
        id: 'addswitchloop',
        endpoint: 'addToWhile',
        arguments: {
            type: 'switch',
            where: 'loop'
        }
    }, {
        id: 'addswitchbreak',
        endpoint: 'addToWhile',
        arguments: {
            type: 'switch',
            where: 'break'
        }
    }, {
        id: 'addwhileloop',
        endpoint: 'addToWhile',
        arguments: {
            type: 'while',
            where: 'loop'
        }
    }, {
        id: 'addrepeatloop',
        endpoint: 'addToWhile',
        arguments: {
            type: 'repeat',
            where: 'loop'
        }
    }, {
        id: 'addwhilebreak',
        endpoint: 'addToWhile',
        arguments: {
            type: 'while',
            where: 'break'
        }
    }, {
        id: 'addrepeatbreak',
        endpoint: 'addToWhile',
        arguments: {
            type: 'repeat',
            where: 'break'
        }
    }, {
        id: 'addstartloop',
        endpoint: 'addToWhile',
        arguments: {
            type: 'start',
            where: 'loop'
        }
    }, {
        id: 'addendloop',
        endpoint: 'addToWhile',
        arguments: {
            type: 'end',
            where: 'loop'
        }
    }, {
        id: 'addstoploop',
        endpoint: 'addToWhile',
        arguments: {
            type: 'stop',
            where: 'loop'
        }
    }, {
        id: 'addstartbreak',
        endpoint: 'addToWhile',
        arguments: {
            type: 'start',
            where: 'break'
        }
    }, {
        id: 'addendbreak',
        endpoint: 'addToWhile',
        arguments: {
            type: 'end',
            where: 'break'
        }
    }, {
        id: 'addstopbreak',
        endpoint: 'addToWhile',
        arguments: {
            type: 'stop',
            where: 'break'
        }
    }];


    whilelist.forEach(item => {
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





    document.getElementById('editwhilemenu').addEventListener('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        try {

            const response = await fetch("getTextWhile", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });
            const texts = await response.json();

            $('#whilestatement').val(texts[0]);
            $('#break').val(texts[1]);
            $('#loop').val(texts[2]);
            $('#modalFormWhile').modal('show');
            $('#modalFormWhile').on('shown.bs.modal', function() {
                $('#whilestatement').trigger('focus')
            })




        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })

}

function connectorEventListeners() {
    $('#submit-connector').on('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        var text = $('#connector-text').val();
        try {

            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("editCharConnector", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'text': text,
                    'svgelement': lastclickedsvgelement.outerHTML
                }),
            });

            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })

    const connectorlist = [{
        id: 'connectordelete',
        endpoint: 'connectorDelete',
        arguments: {}
    }, {
        id: 'toggledetachconnector',
        endpoint: 'detachConnector',
        arguments: {}
    }, {
        id: 'noteconnector',
        endpoint: 'addToConnector',
        arguments: {
            where: 'below',
            type: 'note'
        }
    }, {
        id: 'addactivitybelowconnector',
        endpoint: 'addToConnector',
        arguments: {
            where: 'below',
            type: 'activity'
        }
    }, {
        id: 'addifbelowconnector',
        endpoint: 'addToConnector',
        arguments: {
            where: 'below',
            type: 'if'
        }
    }, {
        id: 'addwhilebelowconnector',
        endpoint: 'addToConnector',
        arguments: {
            where: 'below',
            type: 'while'
        }
    }, {
        id: 'addrepeatbelowconnector',
        endpoint: 'addToConnector',
        arguments: {
            where: 'below',
            type: 'repeat'
        }
    }, {
        id: 'addforkbelowconnector',
        endpoint: 'addToConnector',
        arguments: {
            where: 'below',
            type: 'fork'
        }
    }, {
        id: 'addswitchbelowconnector',
        endpoint: 'addToConnector',
        arguments: {
            where: 'below',
            type: 'switch'
        }
    }];

    connectorlist.forEach(item => {
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

function arrowLabelEventListeners() {
    const arrowlist = [{
        id: 'arrowlabeldelete',
        endpoint: 'delArrow',
        arguments: {}
    }, ];


    arrowlist.forEach(item => {
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

    $('#submit-arrow').on('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        var text = $('#arrow-text').val();
        try {
            const plantuml = trimlines(editor.session.getValue());
            const response = await fetch("editArrow", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': plantuml,
                    'svg': svg.innerHTML,
                    'text': text,
                    'svgelement': lastclickedsvgelement.outerHTML
                }),
            });
            const pumlcontentcode = await response.text()
            setPuml(pumlcontentcode)
        } catch (error) {
            displayErrorMessage(`Error with fetch API: ${error.message}`, error);
        }
    })

    document.getElementById('arrowlabeledit').addEventListener('click', async () => {
        const element = document.getElementById('colb')
        const svg = element.querySelector('g');
        try {
            // First fetch to check for duplicates
            const checkDuplicateResponse = await fetch("checkDuplicateArrow", {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({
                    'plantuml': editor.session.getValue(),
                    'svg': svg.innerHTML,
                    'svgelement': lastclickedsvgelement.outerHTML
                })
            });

            const checkDuplicateData = await checkDuplicateResponse.json();
            const isDuplicate = checkDuplicateData.result;
            const arrowType = checkDuplicateData.type

            // Only fetch ArrowText if the duplicate check returns false
            if (!isDuplicate) {
                try {
                    const arrowTextResponse = await fetch("getArrowText", {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json'
                        },
                        body: JSON.stringify({
                            'svg': svg.innerHTML,
                            'svgelement': lastclickedsvgelement.outerHTML
                        })
                    });

                    const arrowText = await arrowTextResponse.text();
                    $('#arrow-text').val(arrowText);
                    $('#modalFormArrow').modal('show');
                    $('#modalFormArrow').on('shown.bs.modal', function() {
                        $('#arrow-text').trigger('focus');
                    });
                } catch (error) {
                    console.error('Error with fetch API when fetching ArrowText', error);
                }
            } else if (arrowType == "arrow") {
                $('#duplicateArrowModal').modal('show');
            } else {
                $('#duplicateCaseModal').modal('show');
            }
        } catch (error) {
            console.error('Error with fetch API during duplicate check', error);
        }
    });


}

function commandEventListeners() {
    document.addEventListener('keydown', function(event) {
        if (event.ctrlKey && event.key === "z") {
            console.log("hej")
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
        }
    });
}

function addEventListeners() {
    activityEventListeners();
    ifEventListeners();
    ellipseEventListeners();
    buttonEventListeners();
    titleEventListeners();
    forkEventListeners();
    noteEventListeners();
    groupEventListeners();
    mergeEventListeners();
    whileEventListeners();
    connectorEventListeners();
    bottomForkEventListeners();
    arrowLabelEventListeners();
    commandEventListeners();
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

const debouncedRenderPlantUml = debounce(renderPlantUml, 200);

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
    const element = document.getElementById('colb')
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

    if (checkIfStateDiagram(pumlcontent)) { // If state diagram render without interactivity (not supported)
        fetchSvgFromPlantUml().then((svgContent) => {
            element.innerHTML = svgContent;
        })
        toggleLoadingOverlay();
    }
    else {
        setHandlersForActivityDiagram(pumlcontent, element);
    }

}

async function setHandlersForActivityDiagram(pumlcontent, element) {
    fetchSvgFromPlantUml().then((svgContent) => {
        element.innerHTML = svgContent;
        const svg = element.querySelector('g');
        if (!svg) {
            toggleLoadingOverlay()
            return
        }
        const svgelements = svg.querySelectorAll('*');

        let onlytextelements = true
        forkqueue = labelForks(pumlcontent)

        for (let index = 0; index < svgelements.length;) {
            let svgelement = svgelements[index]
            if (svgelement.tagName.toLowerCase() != 'text') {
                onlytextelements = false
            }
            if (svgelement.tagName.toLowerCase() === 'line') {
                svgelement.style.pointerEvents = 'none';
            }
            if (checkIfActivity(svgelements, index)) {
                svgelement.addEventListener('dblclick', async () => {
                    lastclickedsvgelement = svgelement;
                    try {

                        const response = await fetch("getText", {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                'svg': svg.innerHTML,
                                'svgelement': svgelement.outerHTML
                            })
                        });
                        $('#message-text').val(await response.text());
                        $('#modalForm').modal('show');
                        $('#modalForm').on('shown.bs.modal', function() {
                            $('#message-text').trigger('focus')
                        })



                    } catch (error) {
                        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
                    }
                });

                handleContextMenuActivity(pumlcontent, svg, svgelement);

                let rectcolor = ""
                svgelement.addEventListener('mouseover', function() {
                    const svg = element.querySelector('g');
                    resetHighlight(svg);

                    processActivityLine(pumlcontent, svg, svgelement)
                    rectcolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', rectcolor)
                });
            }

            if (checkIfFork(svgelements, index)) {
                let forkobj = forkqueue.shift();
                svgelement.setAttribute('fline', forkobj.index)
                if (forkobj.line == "top") {
                    svgelement.addEventListener('contextmenu', function(e) {
                        lastclickedsvgelement = svgelement
                        e.preventDefault();
                        var contextMenu = document.getElementById('fork-menu');
                        contextMenu.style.display = 'block';
                        contextMenu.style.left = e.pageX + 'px';
                        contextMenu.style.top = e.pageY + 'px';
                    });
                } else {
                    svgelement.addEventListener('contextmenu', function(e) {
                        lastclickedsvgelement = svgelement
                        e.preventDefault();
                        var contextMenu = document.getElementById('forkbottom-menu');
                        contextMenu.style.display = 'block';
                        contextMenu.style.left = e.pageX + 'px';
                        contextMenu.style.top = e.pageY + 'px';
                    });
                }
                let rectcolor = ""
                svgelement.addEventListener('mouseover', function() {
                    getmarkersinglelines(parseInt(svgelement.getAttribute('fline'), 10))
                    rectcolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', rectcolor)
                });
            }

            if (checkIfWhile(svgelements, index)) {
                svgelement.addEventListener('dblclick', async () => {
                    lastclickedsvgelement = svgelement;
                    try {

                        const response = await fetch("getTextWhile", {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                'svg': svg.innerHTML,
                                'svgelement': svgelement.outerHTML
                            })
                        });
                        const texts = await response.json();

                        $('#whilestatement').val(texts[0]);
                        $('#break').val(texts[1]);
                        $('#loop').val(texts[2]);
                        $('#modalFormWhile').modal('show');
                        $('#modalFormWhile').on('shown.bs.modal', function() {
                            $('#whilestatement').trigger('focus')
                        })




                    } catch (error) {
                        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
                    }
                });

                svgelement.addEventListener('contextmenu', function(e) {
                    lastclickedsvgelement = svgelement
                    e.preventDefault();
                    var contextMenu = document.getElementById('while-menu');
                    contextMenu.style.display = 'block';
                    contextMenu.style.left = e.pageX + 'px';
                    contextMenu.style.top = e.pageY + 'px';
                });

                let color = ""
                svgelement.addEventListener('mouseover', function() {
                    processWhileLine(pumlcontent, svg, svgelement)
                    color = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', color)
                });

            }

            if (checkIfCorrectPoly(svgelements, index) && !checkIfWhile(svgelements, index) && !checkIfMergePoly(svgelements, index)) { // checks if its an actual if polygon with text or and endif
                svgelement.addEventListener('dblclick', async () => {
                    lastclickedsvgelement = svgelement;
                    try {

                        const response = await fetch("getTextPoly", {
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
                        const texts = await response.json();
                        const isSwitch = await checkSwitch(pumlcontent, svg, lastclickedsvgelement)
                        if (isSwitch) {
                            $('#switch-text').val(texts[0]);
                            $('#modalFormswitch').modal('show');
                            $('#modalFormswitch').on('shown.bs.modal', function() {
                                $('#switch-text').trigger('focus')
                            })
                        } else {
                            $('#statement').val(texts[0]);
                            $('#branch1').val(texts[1]);
                            $('#branch2').val(texts[2]);
                            $('#modalFormif').modal('show');
                            $('#modalFormif').on('shown.bs.modal', function() {
                                $('#statement').trigger('focus')
                            })
                        }

                    } catch (error) {
                        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
                    }
                });

                handleContextMenuPoly(pumlcontent, svg, svgelement) // adds the correct context menu depending on if its an if or repeat


                let polycolor = ""
                svgelement.addEventListener('mouseover', function() {
                    processIfLine(pumlcontent, svg, svgelement)
                    polycolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', polycolor)
                });
            }

            if (checkIfNote(svgelements, index)) {
                svgelement.addEventListener('dblclick', async () => {
                    lastclickedsvgelement = svgelement;
                    try {

                        const response = await fetch("getNoteText", {
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
                        $('#note-text').val(await response.text());
                        $('#modalFormNote').modal('show');
                        $('#modalFormNote').on('shown.bs.modal', function() {
                            $('#note-text').trigger('focus')
                        })



                    } catch (error) {
                        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
                    }
                });

                svgelement.addEventListener('contextmenu', function(e) {
                    lastclickedsvgelement = svgelement
                    e.preventDefault();
                    var contextMenu = document.getElementById('note-menu');
                    contextMenu.style.display = 'block';
                    contextMenu.style.left = e.pageX + 'px';
                    contextMenu.style.top = e.pageY + 'px';
                });

                let rectcolor = ""
                svgelement.addEventListener('mouseover', function() {
                    processNoteLine(pumlcontent, svg, svgelement)
                    rectcolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', rectcolor)
                });
            }

            if (checkIfMergePoly(svgelements, index)) {
                svgelement.addEventListener('contextmenu', function(e) {
                    lastclickedsvgelement = svgelement
                    e.preventDefault()
                    var contextMenu = document.getElementById('merge-menu');
                    contextMenu.style.display = 'block';
                    contextMenu.style.left = e.pageX + 'px';
                    contextMenu.style.top = e.pageY + 'px';
                });

                let rectcolor = ""
                svgelement.addEventListener('mouseover', function() {
                    processMergeLine(pumlcontent, svg, svgelement)
                    rectcolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', rectcolor)
                });

            }

            if (checkIfGroup(svgelements, index)) {
                //svgelement.setAttribute('fill', 'transparent') // on click works poorly if fill is 'none'
                svgelement.addEventListener('dblclick', async () => {
                    lastclickedsvgelement = svgelements[index - 2];
                    try {


                        const response = await fetch("getGroupText", {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json'
                            },
                            body: JSON.stringify({
                                'plantuml': pumlcontent,
                                'svg': svg.innerHTML,
                                'svgelement': lastclickedsvgelement.outerHTML
                            })
                        });
                        $('#group-text').val(await response.text());
                        $('#modalFormGroup').modal('show');
                        $('#modalFormGroup').on('shown.bs.modal', function() {
                            $('#group-text').trigger('focus')
                        })



                    } catch (error) {
                        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
                    }
                });

                svgelement.addEventListener('contextmenu', function(e) {
                    lastclickedsvgelement = svgelements[index - 2];
                    e.preventDefault();
                    var contextMenu = document.getElementById('group-menu');
                    contextMenu.style.display = 'block';
                    contextMenu.style.left = e.pageX + 'px';
                    contextMenu.style.top = e.pageY + 'px';
                });

                let rectcolor = ""
                svgelement.addEventListener('mouseenter', function() {
                    processGroupLine(pumlcontent, svg, svgelements[index - 2])
                    rectcolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseleave', function() {
                    svgelement.setAttribute('fill', rectcolor)
                });
            }


            if (checkIfEllipse(svgelements, index)) {
                if (svgelement.getAttribute('fill') === 'none') {
                    svgelement.setAttribute('fill', 'transparent'); // changes background from none to make it clickable
                }
                svgelement.addEventListener('contextmenu', function(e) {
                    lastclickedsvgelement = svgelement
                    e.preventDefault();
                    var contextMenu = document.getElementById('ellipse-menu');
                    contextMenu.style.display = 'block';
                    contextMenu.style.left = e.pageX + 'px';
                    contextMenu.style.top = e.pageY + 'px';
                });

                let ellipsecolor = ""
                svgelement.addEventListener('mouseover', function() {
                    processEllipseLine(pumlcontent, svg, svgelement)
                    ellipsecolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#818181 ')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', ellipsecolor)
                });

            }

            if (checkIfConnector(svgelements, index)) {
                svgelement.addEventListener('dblclick', async () => {
                    lastclickedsvgelement = svgelement;
                    try {
                        const response = await fetch("getCharConnector", {
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
                        $('#connector-text').val(await response.text());
                        $('#modalFormConnector').modal('show');
                        $('#modalFormConnector').on('shown.bs.modal', function() {
                            $('#connector-text').trigger('focus')
                        })



                    } catch (error) {
                        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
                    }
                });


                svgelements[index + 1].style.pointerEvents = 'none';
                svgelement.addEventListener('contextmenu', function(e) {
                    lastclickedsvgelement = svgelement
                    e.preventDefault();
                    var contextMenu = document.getElementById('connector-menu');
                    contextMenu.style.display = 'block';
                    contextMenu.style.left = e.pageX + 'px';
                    contextMenu.style.top = e.pageY + 'px';
                });

                let ellipsecolor = ""
                svgelement.addEventListener('mouseover', function() {
                    processConnectorLine(pumlcontent, svg, svgelement)
                    ellipsecolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#c2c2c2')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', ellipsecolor)
                });

            }

            if (checkIfArrowLabel(svgelements, index)) {
                let arrow = svgelements[index - 1]
                while (index < svgelements.length && svgelements[index].tagName.toLowerCase() === 'text') {
                    svgelements[index].addEventListener('dblclick', async () => {
                        lastclickedsvgelement = arrow;

                        try {
                            // First fetch to check for duplicates
                            const checkDuplicateResponse = await fetch("checkDuplicateArrow", {
                                method: 'POST',
                                headers: {
                                    'Content-Type': 'application/json'
                                },
                                body: JSON.stringify({
                                    'plantuml': editor.session.getValue(),
                                    'svg': svg.innerHTML,
                                    'svgelement': lastclickedsvgelement.outerHTML
                                })
                            });

                            const checkDuplicateData = await checkDuplicateResponse.json();
                            const isDuplicate = checkDuplicateData.result;
                            const arrowType = checkDuplicateData.type

                            // Only fetch ArrowText if the duplicate check returns false
                            if (!isDuplicate) {
                                try {
                                    const arrowTextResponse = await fetch("getArrowText", {
                                        method: 'POST',
                                        headers: {
                                            'Content-Type': 'application/json'
                                        },
                                        body: JSON.stringify({
                                            'svg': svg.innerHTML,
                                            'svgelement': lastclickedsvgelement.outerHTML
                                        })
                                    });

                                    const arrowText = await arrowTextResponse.text();
                                    $('#arrow-text').val(arrowText);
                                    $('#modalFormArrow').modal('show');
                                    $('#modalFormArrow').on('shown.bs.modal', function() {
                                        $('#arrow-text').trigger('focus');
                                    });
                                } catch (error) {
                                    console.error('Error with fetch API when fetching ArrowText', error);
                                }
                            } else if (arrowType == "arrow") {
                                $('#duplicateArrowModal').modal('show');
                            } else {
                                $('#duplicateCaseModal').modal('show');
                            }
                        } catch (error) {
                            console.error('Error with fetch API during duplicate check', error);
                        }
                    });

                    svgelements[index].addEventListener('contextmenu', function(e) {
                        lastclickedsvgelement = arrow
                        e.preventDefault();
                        var contextMenu = document.getElementById('arrowlabel-menu');
                        contextMenu.style.display = 'block';
                        contextMenu.style.left = e.pageX + 'px';
                        contextMenu.style.top = e.pageY + 'px';
                    });

                    let rectcolor = ""
                    let svgelement = svgelements[index]
                    svgelement.addEventListener('mouseenter', function() {
                        processArrowLine(pumlcontent, svg, arrow)
                        rectcolor = svgelement.getAttribute('fill')
                        svgelement.setAttribute('fill', '#d8d8d8')
                    });

                    svgelement.addEventListener('mouseleave', function() {
                        svgelement.setAttribute('fill', rectcolor)
                    });

                    index++
                }
            }

            if (
                !onlytextelements &&
                svgelements[index] &&
                (svgelements[index].tagName.toLowerCase() === 'text')
            ) {
                const previousElement = svgelements[index].parentElement;
                if (
                    (!previousElement || previousElement.tagName.toLowerCase() !== 'a') &&
                    (svgelements[index - 1].getAttribute('style') !== "stroke:#000000;stroke-width:1.5;") &&
                    (svgelements[index - 1].getAttribute('style') !== "stroke:#181818;stroke-width:1.0;")
                ) {
                    // We remove the pointer event for text elements unless its an arrow label, clickable link, group label or the title
                    svgelements[index].style.pointerEvents = 'none';
                }
            }

            if (svgelements[index] && svgelements[index].tagName.toLowerCase() === 'a') {
                svgelements[index].setAttribute('target', '_blank')
            }


            if (checkIfTitleRect(svgelements, index)) {
                svgelement.setAttribute('fill', 'transparent')
                svgelement.setAttribute('style', '"stroke:#00000000;stroke-width:1.0;fill:transparent;"')

                svgelement.addEventListener('dblclick', async () => {
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

                svgelement.addEventListener('contextmenu', function(e) {
                    lastclickedsvgelement = svgelement
                    e.preventDefault();
                    var contextMenu = document.getElementById('title-menu');
                    contextMenu.style.display = 'block';
                    contextMenu.style.left = e.pageX + 'px';
                    contextMenu.style.top = e.pageY + 'px';
                });


                let rectcolor = ""
                svgelement.addEventListener('mouseenter', function() {
                    processTitleLine(pumlcontent)
                    rectcolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#e5e5e5')
                });

                svgelement.addEventListener('mouseleave', function() {
                    svgelement.setAttribute('fill', rectcolor)
                });

            }
            index++
        }
        toggleLoadingOverlay()

    }).catch((error) => {
        displayErrorMessage(`Error rendering SVG: ${error.message}`, error);
    });
}

function checkIfEllipse(svgelements, index) {
    if (svgelements[index].tagName.toLowerCase() !== 'ellipse') {
        return false
    }
    if (svgelements[index + 1] && svgelements[index + 1].tagName.toLowerCase() === 'path') {
        return svgelements[index + 1].getAttribute('fill') !== '#000000'
    }
    if (svgelements[index + 1] && svgelements[index + 1].tagName.toLowerCase() === 'line') {
        svgelements[index].setAttribute('fill', 'transparent')
        svgelements[index].setAttribute('style', 'stroke:#222222;stroke-width:1.5;fill:transparent;')
    }
    return true
}

function checkIfConnector(svgelements, index) {
    if (svgelements[index].tagName.toLowerCase() !== 'ellipse') {
        return false
    }
    if (svgelements[index + 1] && svgelements[index + 1].tagName.toLowerCase() === 'path') {
        return svgelements[index + 1].getAttribute('fill') == '#000000'
    }
    return false

}

function checkIfCorrectPoly(svgelements, index) {
    return (
        svgelements[index].tagName.toLowerCase() === 'polygon' &&
        svgelements[index + 1] &&
        ['text', 'a'].includes(svgelements[index + 1].tagName.toLowerCase()) && // Corrected this line
        svgelements[index].getAttribute('style') === "stroke:#181818;stroke-width:0.5;" // Ensure the style matches exactly
    );
}


function checkIfMergePoly(svgelements, index) {
    points = []
    let uniqueTuples = [];
    if (svgelements[index].tagName.toLowerCase() === 'polygon') {
        points = svgelements[index].getAttribute('points').split(",")
        let tuples = [];
        for (let i = 0; i < points.length - 1; i += 2) {
            tuples.push([points[i], points[i + 1]]);
        }
        let seen = new Set();

        for (let tuple of tuples) {
            // Create a unique identifier for each tuple by joining its elements
            let identifier = tuple.join('|');

            if (!seen.has(identifier)) {
                seen.add(identifier);
                uniqueTuples.push(tuple);
            }
        }
    }


    return (svgelements[index].tagName.toLowerCase() === 'polygon' && uniqueTuples.length != 6 &&
        svgelements[index].getAttribute('style') == "stroke:#181818;stroke-width:0.5;")
    // match on style and length of points to only match on the cube polygon at end of merge
}

function checkIfActivity(svgelements, index) {
    return (svgelements[index].tagName.toLowerCase() === 'rect') && parseFloat(svgelements[index].getAttribute('height')) > 6 &&
        (svgelements[index].getAttribute('style') == "stroke:#181818;stroke-width:0.5;")
}

function checkIfTitleRect(svgelements, index) {
    if (svgelements[index]) {
        return (svgelements[index].tagName.toLowerCase() === 'rect') && parseFloat(svgelements[index].getAttribute('height')) > 6 &&
            (svgelements[index].getAttribute('style') == "stroke:#00000000;stroke-width:1.0;fill:none;")
    }
}

function checkIfFork(svgelements, index) {
    return (svgelements[index].tagName.toLowerCase() === 'rect') && parseFloat(svgelements[index].getAttribute('height')) == 6
}

function checkIfNote(svgelements, index) {
    return (svgelements[index].tagName.toLowerCase() === 'path' && svgelements[index + 1].tagName.toLowerCase() === 'path')
}

function checkIfGroup(svgelements, index) {
    if (index > 0 && (svgelements[index].tagName.toLowerCase() === 'text')) {
        if (svgelements[index - 1].getAttribute('style') == "stroke:#000000;stroke-width:1.5;")
            return true
        return false
    }
    return false
}

function checkIfWhile(svgelements, index) {
    if (!svgelements[index + 3]) { // solves bug where last 2 svg elements are polygon and text from an arrow label
        return false
    }

    let points = [];
    let yValues = [];
    let xValues = [];
    let text_y = "";
    let text_x = "";

    // Check if there is a text element at index + 3
    if (svgelements[index + 3] && svgelements[index + 3].tagName.toLowerCase() !== 'text') {
        return false;
    }

    // Check if there is a polygon at index and text at index + 1
    if (svgelements[index + 1] && svgelements[index].tagName.toLowerCase() === 'polygon' && svgelements[index + 1].tagName.toLowerCase() === 'text') {
        points = svgelements[index].getAttribute('points').split(",");

        // Extract y values from points
        for (let i = 1; i < points.length; i += 2) {
            yValues.push(parseFloat(points[i]));
        }

        // Extract x values from points
        for (let i = 0; i < points.length; i += 2) {
            xValues.push(parseFloat(points[i]));
        }

        // Get the text element y and x values and convert to float
        text_y = parseFloat(svgelements[index + 1].getAttribute('y')); // the first text element following while polygon always has a higher y value
        text_x = parseFloat(svgelements[index + 3].getAttribute('x')); // the 3rd text element following while polygon always has smaller x value

        // Check y values
        for (const y of yValues) {
            if (y > text_y) {
                return false;
            }
        }

        // Check x values
        for (const x of xValues) {
            if (x < text_x) {
                return false;
            }
        }

        return true;
    }

    return false;
}

function checkIfArrowLabel(svgelements, index) {
    if (index > 0 && svgelements[index].tagName.toLowerCase() === 'text') {
        let previousElement = svgelements[index - 1];
        if (previousElement.tagName.toLowerCase() === 'polygon' &&
            (previousElement.getAttribute('style')?.includes('stroke-width:1.0'))) {
            return true;
        }
    }
    return false;
}

async function checkRepeat(puml, svgfile, svgelem) {
    const pumlcontent = puml
    const svg = svgfile
    const svgelement = svgelem
    try {
        const response = await fetch("checkWhatPoly", {
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
        const text = await response.text()
        return (text == "repeat")

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }


}

async function checkSwitch(puml, svgfile, svgelem) {
    const pumlcontent = puml
    const svg = svgfile
    const svgelement = svgelem
    try {
        const response = await fetch("checkWhatPoly", {
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
        const text = await response.text()
        return (text.startsWith("switch"))

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }

}



async function checkIfRepeatHasBackward(puml, svg, svgelem) {
    const pumlcontent = puml
    const svgelement = svgelem
    try {
        const response = await fetch("checkIfRepeatHasBackward", {
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
        const text = await response.text()
        return (text == "backward")

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }



}
async function checkBackward(puml, svgfile, svgelem) {
    const pumlcontent = puml
    const svg = svgfile
    const svgelement = svgelem
    try {
        const response = await fetch("checkBackward", {
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
        const text = await response.text()
        return (text.startsWith("backward"))

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }


}


async function handleContextMenuActivity(pumlcontent, svg, svgelement) {
    const isBackward = await checkBackward(pumlcontent, svg, svgelement);
    if (isBackward) {
        svgelement.addEventListener('contextmenu', function(e) {
            lastclickedsvgelement = svgelement;
            e.preventDefault();
            var contextMenu = document.getElementById('backward-menu');
            contextMenu.style.display = 'block';
            contextMenu.style.left = e.pageX + 'px';
            contextMenu.style.top = e.pageY + 'px';
        });
    } else {
        svgelement.addEventListener('contextmenu', function(e) {
            lastclickedsvgelement = svgelement;
            e.preventDefault();
            var contextMenu = document.getElementById('activity-menu');
            contextMenu.style.display = 'block';
            contextMenu.style.left = e.pageX + 'px';
            contextMenu.style.top = e.pageY + 'px';
        });
    }
}


async function handleContextMenuPoly(pumlcontent, svg, svgelement) {
    const isSwitch = await checkSwitch(pumlcontent, svg, svgelement)
    const isRepeat = await checkRepeat(pumlcontent, svg, svgelement)
    const hasBackward = await checkIfRepeatHasBackward(pumlcontent, svg, svgelement)
    if (isRepeat) {
        svgelement.addEventListener('contextmenu', function(e) {
            lastclickedsvgelement = svgelement;
            e.preventDefault();
            var contextMenu = document.getElementById('repeat-menu');
            var backwardButton = document.getElementById('addbackwards');
            if (hasBackward) {
                backwardButton.classList.add('disabled');
            } else {
                backwardButton.classList.remove('disabled');
            }
            contextMenu.style.display = 'block';
            contextMenu.style.left = e.pageX + 'px';
            contextMenu.style.top = e.pageY + 'px';
        });
    } else if (isSwitch) {
        svgelement.addEventListener('contextmenu', function(e) {
            lastclickedsvgelement = svgelement;
            e.preventDefault();
            var contextMenu = document.getElementById('switch-menu');
            contextMenu.style.display = 'block';
            contextMenu.style.left = e.pageX + 'px';
            contextMenu.style.top = e.pageY + 'px';
        });



    } else {
        svgelement.addEventListener('contextmenu', function(e) {
            lastclickedsvgelement = svgelement;
            e.preventDefault();
            var contextMenu = document.getElementById('if-menu');
            contextMenu.style.display = 'block';
            contextMenu.style.left = e.pageX + 'px';
            contextMenu.style.top = e.pageY + 'px';
        });
    }
}


function process(text) {
    const lines = text.split('\n');
    let i = 0;

    while (i < lines.length) {
        if (lines[i].trim() === 'fork again') {
            // Check if there's a "fork" above it OR an "end fork" or "end merge" below it OR another "fork again" above it
            if ((i > 0 && lines[i - 1].trim() === 'fork') ||
                (i < lines.length - 1 && (lines[i + 1].trim() === 'end fork' || lines[i + 1].trim() === 'end merge')) ||
                (i > 0 && lines[i - 1].trim() === 'fork again')) {
                lines.splice(i, 1); // Delete the current "fork again" line
            }
        }
        i++;
    }

    i = 0;
    while (i < lines.length) {
        if (lines[i].trim().startsWith("case")) {
            if ((i < lines.length - 1 && (lines[i + 1].trim().startsWith("case") || lines[i + 1].trim() === 'endswitch')) ||
                (i > 0 && lines[i - 1].trim().startsWith("case"))) {
                lines.splice(i, 1); // Delete the current "case" line
            }
        }
        i++;
    }
    return lines.join('\n');
}



function labelForks(puml) {
    const queue = [];
    const lines = puml.split('\n');

    for (let index = 0; index < lines.length; index++) {
        const line = lines[index];
        const trimmedLine = line.trim();
        if (trimmedLine.startsWith('fork') && !trimmedLine.startsWith('fork again')){
            queue.push({
                index,
                line: 'top'
            });
        } else if (trimmedLine.startsWith("end fork") || trimmedLine.startsWith("endfork")) {
            queue.push({
                index,
                line: 'bottom'
            });
        }
    }

    return queue;

}

function setPuml(pumlcontent) {
    text = process(pumlcontent)
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
            indentedLines.push('    '.repeat(level) + trimmedLine);
            level++;
            return
        }


        // Adjust indentation before appending the line if it is an end statement
        if (decreaseIndentKeywords.some(keyword => trimmedLine.startsWith(keyword))) {
            level--;
        }

        if (sameIndentKeywords.some(keyword => trimmedLine.startsWith(keyword))) {
            indentedLines.push('    '.repeat(level - 1) + trimmedLine);
            return

        } else {
            indentedLines.push('    '.repeat(level) + trimmedLine);
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

async function processActivityLine(pumlcontent, svg, svgelement) {
    try {
        const response = await fetch("getActivityLine", {
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
        const data = await response.json();
        number = data.result
        getmarker(number)

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }


}

async function processNoteLine(pumlcontent, svg, svgelement) {
    try {
        const response = await fetch("getNoteLine", {
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
        const data = await response.json();
        number = data.result
        getmarker(number)

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }


}

async function processEllipseLine(pumlcontent, svg, svgelement) {
    try {
        const response = await fetch("getEllipseLine", {
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

        const data = await response.json();
        number = data.result - 1
        getmarkersinglelines(number)

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }


}

async function processConnectorLine(pumlcontent, svg, svgelement) {
    try {
        const response = await fetch("getConnectorLine", {
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

        const data = await response.json();
        number = data.result - 1
        getmarkersinglelines(number)

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }


}

async function processGroupLine(pumlcontent, svg, svgelement) {
    try {
        const response = await fetch("getGroupLine", {
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

        const data = await response.json();
        number = data.result
        getmarkersinglelines(number)

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }


}

async function processIfLine(pumlcontent, svg, svgelement) {
    try {
        const response = await fetch("getIfLine", {
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

        const data = await response.json();
        number = data.result
        getmarkersinglelines(number)

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }


}

async function processMergeLine(pumlcontent, svg, svgelement) {
    try {
        const response = await fetch("getMergeLine", {
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

        const data = await response.json();
        number = data.result
        getmarkersinglelines(number)

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }


}

async function processWhileLine(pumlcontent, svg, svgelement) {
    try {
        const response = await fetch("getWhileLine", {
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

        const data = await response.json();
        number = data.result
        getmarkersinglelines(number)

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }


}

async function processArrowLine(pumlcontent, svg, svgelement) {
    try {
        const response = await fetch("getArrowLine", {
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

        const data = await response.json();
        number = data.result
        getmarkersinglelines(number)

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }

}

async function processTitleLine(pumlcontent) {
    try {
        const response = await fetch("getTitleLine", {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({
                'plantuml': pumlcontent
            })
        });

        const data = await response.json();
        number = data.result
        getmarker(number)

    } catch (error) {
        displayErrorMessage(`Error with fetch API: ${error.message}`, error);
    }

}

function highlightActivity(svg, text) {
    const rects = svg.getElementsByTagName("rect");

    for (let i = 0; i < rects.length; i++) {
        const rect = rects[i];

        // Check if this is an "activity" rect using the check function
        if (checkIfActivity(rects, i)) {
            let combinedText = "";
            let nextSibling = rect.nextElementSibling;

            // Collect all subsequent nodes that are either <text> or <a> elements
            while (nextSibling && (nextSibling.tagName === "text" || nextSibling.tagName === "a")) {
                if (nextSibling.tagName === "text") {
                    // If it's a text node, simply collect its text content
                    combinedText += nextSibling.textContent + "\n";
                } else if (nextSibling.tagName === "a") {
                    // If it's an <a> tag, collect the link href and text content
                    const href = nextSibling.getAttribute("href");
                    const linkTextElement = nextSibling.querySelector("text");
                    if (linkTextElement) {
                        const linkText = linkTextElement.textContent;
                        combinedText += `[[${href} ${linkText}]]`;
                    }
                }

                // Move to the next sibling element
                nextSibling = nextSibling.nextElementSibling;
            }

            // Compare the normalized text
            if (combinedText.replace(/\s+/g, "") === text.replace(/\s+/g, "")) {
                colorqueue.push(rect.getAttribute('fill'));
                rect.setAttribute('fill', "#d8d8d8");
            }
        }
    }
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

function checkIfStateDiagram(puml) {
    const lines = puml.split('\n');
    for (let index = 0; index < lines.length; index++) {
        const line = lines[index];
        const trimmedLine = line.trim();
        if (trimmedLine.startsWith('state')) {
            return true
        }
    }
    return false
}