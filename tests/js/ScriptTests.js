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


describe("saveToHistory", function () {
    beforeEach(function () {
        history = [];
        historyPointer = -1;
    });

    it("should not save an empty string", function () {
        saveToHistory("");
        expect(history).toEqual([]);
        expect(historyPointer).toBe(-1);
    });

    it("should save a non-empty string", function () {
        saveToHistory("test1");
        expect(history).toEqual(["test1"]);
        expect(historyPointer).toBe(0);
    });

    it("should not save a duplicate of the current entry", function () {
        saveToHistory("test1");
        saveToHistory("test1");
        expect(history).toEqual(["test1"]);
        expect(historyPointer).toBe(0);
    });

    it("should save a different entry", function () {
        saveToHistory("test1");
        saveToHistory("test2");
        expect(history).toEqual(["test1", "test2"]);
        expect(historyPointer).toBe(1);
    });
});


describe("displayErrorMessage", function () {
    var popup;

    beforeEach(function () {
        // Set up the DOM element
        popup = document.createElement('div');
        popup.id = 'popup';
        popup.style.visibility = "hidden";
        document.body.appendChild(popup);
    });

    afterEach(function () {
        // Clean up the DOM
        popup.remove();
    });

    it("should display the error message in the popup", function () {
        const message = "An error occurred";
        displayErrorMessage(message);

        expect(popup.innerText).toBe(message);
        expect(popup.style.visibility).toBe("visible");
    });
});

describe("window.onerror handler", function () {
    var popup;

    beforeEach(function () {
        // Set up the DOM element
        popup = document.createElement('div');
        popup.id = 'popup';
        popup.style.visibility = "hidden";
        document.body.appendChild(popup);
    });

    afterEach(function () {
        popup.remove();
    });

    it("should call displayErrorMessage with the error message", function () {
        const errorMessage = "Script error";

        // Trigger the onerror event
        window.onerror(errorMessage, "random.js", 42, 21, new Error(errorMessage));

        expect(popup.innerText).toBe(errorMessage);
        expect(popup.style.visibility).toBe("visible");
    });
});

describe("indentPuml", function () {
    it("should not throw RangeError: Invalid count value: -1", function () {
        const examplePuml = `@startuml
title title
'objects diagram
object obj1
object obj2{
name
}
object list{
name
}
map map_title{
placeholder1 =>enum()
placeholder2 => [type]
placeholde3 => type2
placeholder4 *-> obj2
}
@enduml`;

        expect(function () {
            indentPuml(examplePuml);
        }).not.toThrowError(RangeError, /Invalid count value/);
    });
});

describe("checkDiagramType", function () {
    beforeEach(function () { // return activity even though sequence keywords are in the activity text
        spyOn(window, "addActivityEventListeners").and.stub(); // Disable real execution for this test
    });

    it("should return 'activity' without running addActivityEventListeners", function () {
        const activityPuml = `@startuml\nstart\n:activity\nparticipant 23;\n@enduml`;

        const result = window.checkDiagramType(activityPuml);

        expect(result).toBe("activity");
        expect(window.addActivityEventListeners).toHaveBeenCalled();
    });

    beforeEach(function () {
        spyOn(window, "addSequenceEventListeners").and.stub(); // Disable real execution for this test
    });
    it("should return 'sequence'", function () { // return sequence even though activity keywords are in the note text
        const sequencePuml = `@startuml
participant Alice
participant Bob
Alice -> Bob
note right
if
:
fork
end note
@enduml`;
        const result = window.checkDiagramType(sequencePuml);
        expect(result).toBe("sequence")
    })

});
