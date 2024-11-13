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
