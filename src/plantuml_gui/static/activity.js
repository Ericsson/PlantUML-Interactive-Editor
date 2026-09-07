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

// --- Editor -> diagram highlighting ---
// Hover targets registered during the setHandlersForSvg walk, in SVG document
// order per type. The backend's getActivityPositions counts elements of each
// type in the same document order, so entries match by ordinal - the same
// invariant the per-element get*Line endpoints rely on.
let activityHoverTargets = null;
let activityRowMap = new Map(); // editor row -> [{el, style}, ...] (see hover-highlight.js)
let activityHighlighted = []; // [{el, style, token}, ...] active highlights to restore
let activityElementRows = new Map(); // el -> [rows] for diagram->editor hover markers

function newActivityHoverTargets() {
    return {
        activities: [],
        polys: [],
        whiles: [],
        notes: [],
        groups: [],
        ellipses: [],
        connectors: [],
        merges: [],
        arrows: [], // each entry is the array of label text elements of one arrow
        forks: [], // each entry is {el, row}; rows come from labelForks, not the backend
        title: []
    };
}

async function fetchActivityPositions() {
    const data = await fetchDiagramData("getActivityPositions");
    activityRowMap = new Map();
    if (data) buildActivityRowMap(data);
}

// Highlight treatments per element type (see hover-highlight.js). Fills match
// what each type's diagram-side mouseover uses; label texts (groups, arrows)
// turn bold like sequence messages do.
const FILL_HIGHLIGHT = attributeHighlight('fill', '#d8d8d8');
const BOLD_HIGHLIGHT = attributeHighlight('font-weight', 'bold');
const ELLIPSE_HIGHLIGHT = attributeHighlight('fill', '#818181');
const CONNECTOR_HIGHLIGHT = attributeHighlight('fill', '#c2c2c2');
const TITLE_HIGHLIGHT = attributeHighlight('fill', '#e5e5e5');

function buildActivityRowMap(positions) {
    activityRowMap = new Map();
    activityElementRows = new Map();
    // An arrow's target is an array of its label text elements; register each
    // element separately so the shared row map holds one element per entry.
    const register = (row, target, style) => {
        const els = Array.isArray(target) ? target : [target];
        for (const el of els) {
            registerHoverRow(activityRowMap, row, el, style);
            registerElementRows(activityElementRows, el, row);
        }
    };
    const add = (rowsPerElement, targets, style) => {
        for (let i = 0; i < targets.length && i < rowsPerElement.length; i++) {
            for (const row of rowsPerElement[i]) {
                register(row, targets[i], style);
            }
        }
    };
    add(positions.activities, activityHoverTargets.activities, FILL_HIGHLIGHT);
    add(positions.polys, activityHoverTargets.polys, FILL_HIGHLIGHT);
    add(positions.whiles, activityHoverTargets.whiles, FILL_HIGHLIGHT);
    add(positions.notes, activityHoverTargets.notes, FILL_HIGHLIGHT);
    add(positions.merges, activityHoverTargets.merges, FILL_HIGHLIGHT);
    add(positions.groups, activityHoverTargets.groups, BOLD_HIGHLIGHT);
    add(positions.arrows, activityHoverTargets.arrows, BOLD_HIGHLIGHT);
    add(positions.ellipses, activityHoverTargets.ellipses, ELLIPSE_HIGHLIGHT);
    add(positions.connectors, activityHoverTargets.connectors, CONNECTOR_HIGHLIGHT);
    if (activityHoverTargets.title.length > 0) {
        add([positions.title], activityHoverTargets.title, TITLE_HIGHLIGHT);
    }
    for (const fork of activityHoverTargets.forks) {
        register(fork.row, fork.el, FILL_HIGHLIGHT);
    }
}

function highlightActivityForRow(row) {
    highlightHoverRow(activityRowMap, row, activityHighlighted);
}

function resetActivityHighlight() {
    activityHighlighted = clearHoverHighlight(activityHighlighted);
}

async function setHandlersForActivityDiagram(pumlcontent, element, renderId) {
    removeBackgroundMenuListener();

    fetchSvgFromPlantUml().then(async (svgContent) => {
        // A newer render started while this SVG was being fetched (e.g. the
        // user switched diagrams); drop this result so it can't clobber the
        // current diagram. Balance the loading overlay toggle that
        // renderPlantUml did for this render before bailing.
        if (renderId !== renderGeneration) {
            hideLoadingOverlay();
            return;
        }
        element.innerHTML = svgContent;
        activityHoverTargets = newActivityHoverTargets();
        activityHighlighted = []; // old DOM discarded with innerHTML
        activityRowMap = new Map();
        const svg = element.querySelector('g');
        if (!svg) {
            hideLoadingOverlay()
            return
        }
        // Clear the editor hover marker when the pointer leaves a diagram
        // element (mouseout bubbles from the elements up to this <g>), so the
        // last hovered element's line doesn't stay highlighted in the editor.
        // The <g> is recreated on every render, so this listener doesn't stack.
        svg.addEventListener('mouseout', clearMarkers);
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
                activityHoverTargets.activities.push(svgelement);
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
                    markEditorForElement(activityElementRows, svgelement)
                    rectcolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', rectcolor)
                });
            }

            if (checkIfFork(svgelements, index)) {
                let forkobj = forkqueue.shift();
                activityHoverTargets.forks.push({
                    el: svgelement,
                    row: forkobj.index
                });
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
                    setEditorMarkers(parseInt(svgelement.getAttribute('fline'), 10))
                    rectcolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', rectcolor)
                });
            }

            if (checkIfWhile(svgelements, index)) {
                activityHoverTargets.whiles.push(svgelement);
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
                    markEditorForElement(activityElementRows, svgelement)
                    color = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', color)
                });

            }

            if (checkIfCorrectPoly(svgelements, index) && !checkIfWhile(svgelements, index) && !checkIfMergePoly(svgelements, index)) { // checks if its an actual if polygon with text or and endif
                activityHoverTargets.polys.push(svgelement);
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
                    markEditorForElement(activityElementRows, svgelement)
                    polycolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', polycolor)
                });
            }

            if (checkIfNote(svgelements, index)) {
                // Mirror the backend's note_count skip rule: paths flagged
                // pointer-events none (connector glyphs) are not notes
                if (svgelement.style.pointerEvents !== 'none') {
                    activityHoverTargets.notes.push(svgelement);
                }
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
                    markEditorForElement(activityElementRows, svgelement)
                    rectcolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', rectcolor)
                });
            }

            if (checkIfMergePoly(svgelements, index)) {
                activityHoverTargets.merges.push(svgelement);
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
                    markEditorForElement(activityElementRows, svgelement)
                    rectcolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#d8d8d8')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', rectcolor)
                });

            }

            if (checkIfGroup(svgelements, index)) {
                activityHoverTargets.groups.push(svgelement);
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

                let groupweight = null
                svgelement.addEventListener('mouseenter', function() {
                    markEditorForElement(activityElementRows, svgelement)
                    groupweight = svgelement.getAttribute('font-weight')
                    svgelement.setAttribute('font-weight', 'bold')
                });

                svgelement.addEventListener('mouseleave', function() {
                    if (groupweight === null) {
                        svgelement.removeAttribute('font-weight')
                    } else {
                        svgelement.setAttribute('font-weight', groupweight)
                    }
                });
            }


            if (checkIfEllipse(svgelements, index)) {
                // Mirror svgtochunklistellipse: an "end" marker draws two
                // concentric ellipses; the backend skips the first of the
                // pair, so registration must too
                const nextEllipse = svgelements[index + 1];
                const isFirstOfEndPair = nextEllipse &&
                    nextEllipse.tagName.toLowerCase() === 'ellipse' &&
                    nextEllipse.getAttribute('cx') === svgelement.getAttribute('cx') &&
                    nextEllipse.getAttribute('cy') === svgelement.getAttribute('cy');
                if (!isFirstOfEndPair) {
                    activityHoverTargets.ellipses.push(svgelement);
                }
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
                    markEditorForElement(activityElementRows, svgelement)
                    ellipsecolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#818181')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', ellipsecolor)
                });

            }

            if (checkIfConnector(svgelements, index)) {
                activityHoverTargets.connectors.push(svgelement);
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
                    markEditorForElement(activityElementRows, svgelement)
                    ellipsecolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#c2c2c2')
                });

                svgelement.addEventListener('mouseout', function() {
                    svgelement.setAttribute('fill', ellipsecolor)
                });

            }

            if (checkIfArrowLabel(svgelements, index)) {
                let arrow = svgelements[index - 1]
                let arrowLabelTexts = [];
                activityHoverTargets.arrows.push(arrowLabelTexts);
                while (index < svgelements.length && svgelements[index].tagName.toLowerCase() === 'text') {
                    arrowLabelTexts.push(svgelements[index]);
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

                    let arrowweight = null
                    let svgelement = svgelements[index]
                    svgelement.addEventListener('mouseenter', function() {
                        markEditorForElement(activityElementRows, svgelement)
                        arrowweight = svgelement.getAttribute('font-weight')
                        svgelement.setAttribute('font-weight', 'bold')
                    });

                    svgelement.addEventListener('mouseleave', function() {
                        if (arrowweight === null) {
                            svgelement.removeAttribute('font-weight')
                        } else {
                            svgelement.setAttribute('font-weight', arrowweight)
                        }
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
                activityHoverTargets.title.push(svgelement);

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
                    markEditorForElement(activityElementRows, svgelement)
                    rectcolor = svgelement.getAttribute('fill')
                    svgelement.setAttribute('fill', '#e5e5e5')
                });

                svgelement.addEventListener('mouseleave', function() {
                    svgelement.setAttribute('fill', rectcolor)
                });

            }
            index++
        }
        // Make the diagram title double-click editable. Runs after the element
        // walk so it can re-enable pointer events on the title text (the walk
        // sets font-size text to pointer-events:none) and so it sees the final
        // SVG. Handles both the old bounding-rect title and newer PlantUML's
        // bold text-only title (see title.js).
        setupTitleHandler(svgelements, svg, pumlcontent);
        // After the walk so the svg sent reflects its mutations (e.g. the
        // pointer-events flags note counting depends on)
        await fetchActivityPositions();
        hideLoadingOverlay()

    }).catch((error) => {
        // Balance the showLoadingOverlay() from renderPlantUml on the error
        // path too; otherwise the ref count leaks and wedges the overlay
        // visible. Mutually exclusive with the success hide above.
        hideLoadingOverlay();
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


function processForkAndSwitch(text)  {
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
