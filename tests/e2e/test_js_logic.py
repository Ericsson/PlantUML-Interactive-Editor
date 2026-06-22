"""Tests for JavaScript logic functions (migrated from Jasmine tests/js/ScriptTests.js).

These tests use page.evaluate() to call JS functions directly in the running app
and verify their return values. They test pure logic, not UI interactions.
"""


# Tests the undo/redo history stack: adding entries, deduplication, pointer tracking.
class TestSaveToHistory:
    def test_should_not_save_empty_string(self, app_url, page):
        result = page.evaluate("""() => {
            history = [];
            historyPointer = -1;
            saveToHistory("");
            return { history, historyPointer };
        }""")
        assert result["history"] == []
        assert result["historyPointer"] == -1

    def test_should_save_non_empty_string(self, app_url, page):
        result = page.evaluate("""() => {
            history = [];
            historyPointer = -1;
            saveToHistory("test1");
            return { history, historyPointer };
        }""")
        assert result["history"] == ["test1"]
        assert result["historyPointer"] == 0

    def test_should_not_save_duplicate(self, app_url, page):
        result = page.evaluate("""() => {
            history = [];
            historyPointer = -1;
            saveToHistory("test1");
            saveToHistory("test1");
            return { history, historyPointer };
        }""")
        assert result["history"] == ["test1"]
        assert result["historyPointer"] == 0

    def test_should_save_different_entry(self, app_url, page):
        result = page.evaluate("""() => {
            history = [];
            historyPointer = -1;
            saveToHistory("test1");
            saveToHistory("test2");
            return { history, historyPointer };
        }""")
        assert result["history"] == ["test1", "test2"]
        assert result["historyPointer"] == 1


# Tests that error messages are shown in the popup element.
class TestDisplayErrorMessage:
    def test_should_display_error_in_popup(self, app_url, page):
        result = page.evaluate("""() => {
            const popup = document.getElementById('popup');
            displayErrorMessage("An error occurred");
            return { text: popup.innerText, visibility: popup.style.visibility };
        }""")
        assert result["text"] == "An error occurred"
        assert result["visibility"] == "visible"


# Tests the global error handler (window.onerror) displays errors in the popup.
class TestWindowOnerror:
    def test_should_display_error_message(self, app_url, page):
        result = page.evaluate("""() => {
            const popup = document.getElementById('popup');
            window.onerror("Script error", "random.js", 42, 21, new Error("Script error"));
            return { text: popup.innerText, visibility: popup.style.visibility };
        }""")
        assert result["text"] == "Script error"
        assert result["visibility"] == "visible"


# Tests that the PlantUML indentation function handles edge cases without crashing.
class TestIndentPuml:
    def test_should_not_throw_range_error(self, app_url, page):
        result = page.evaluate("""() => {
            const puml = `@startuml
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
            try {
                indentPuml(puml);
                return { success: true };
            } catch (e) {
                return { success: false, error: e.message };
            }
        }""")
        assert result["success"] is True


# Tests diagram type detection (activity vs sequence) from PlantUML source text.
class TestCheckDiagramType:
    def test_should_return_activity(self, app_url, page):
        result = page.evaluate("""() => {
            const puml = `@startuml\\nstart\\n:activity\\nparticipant 23;\\n@enduml`;
            return checkDiagramType(puml);
        }""")
        assert result == "activity"

    def test_should_return_sequence(self, app_url, page):
        result = page.evaluate("""() => {
            const puml = `@startuml
participant Alice
participant Bob
Alice -> Bob
note right
if
:
fork
end note
@enduml`;
            return checkDiagramType(puml);
        }""")
        assert result == "sequence"


# Tests the diff logic that finds changed lines between history entries.
class TestFindChangedLines:
    def test_should_not_throw_when_pointer_is_zero(self, app_url, page):
        result = page.evaluate("""() => {
            history = ["initial", "change1", "change2"];
            historyPointer = 0;
            try {
                findChangedLines();
                return { success: true };
            } catch (e) {
                return { success: false, error: e.message };
            }
        }""")
        assert result["success"] is True
