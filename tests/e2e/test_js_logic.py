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

    def test_indents_sequence_blocks(self, app_url, page):
        """Boxes and groups nest, else sits at its group's level, end closes it."""
        puml = "\n".join(
            [
                "@startuml",
                "participant A",
                'box "B" #LightBlue',
                "participant B",
                "end box",
                "group outer",
                "A -> B: one",
                "alt inner",
                "B -> A: two",
                "else other",
                "B -> A: three",
                "end",
                "end",
                "activate A",
                "A -> A: self",
                "deactivate A",
                "@enduml",
            ]
        )
        result = page.evaluate("puml => indentPuml(puml)", puml)
        assert result.split("\n") == [
            "@startuml",
            "participant A",
            'box "B" #LightBlue',
            "    participant B",
            "end box",
            "group outer",
            "    A -> B: one",
            "    alt inner",
            "        B -> A: two",
            "    else other",
            "        B -> A: three",
            "    end",
            "end",
            "activate A",
            "A -> A: self",
            "deactivate A",
            "@enduml",
        ]

    def test_activity_end_is_not_a_block_close(self, app_url, page):
        """In an activity diagram 'end' is a stop marker, so the activity rules still apply."""
        puml = "@startuml\nstart\nif (a) then (yes)\n:b;\nend\nendif\n@enduml"
        result = page.evaluate("puml => indentPuml(puml)", puml)
        assert result.split("\n") == [
            "@startuml",
            "start",
            "if (a) then (yes)",
            "    :b;",
            "    end",
            "endif",
            "@enduml",
        ]

    def test_keywords_match_whole_words(self, app_url, page):
        """'elseif' is still a branch, while a participant named 'boxer' opens nothing."""
        activity = "@startuml\nstart\nif (a) then (yes)\n:b;\nelseif (c) then (yes)\n:d;\nendif\n@enduml"
        assert page.evaluate("puml => indentPuml(puml)", activity).split("\n") == [
            "@startuml",
            "start",
            "if (a) then (yes)",
            "    :b;",
            "elseif (c) then (yes)",
            "    :d;",
            "endif",
            "@enduml",
        ]
        sequence = "@startuml\nparticipant boxer\nboxer -> boxer: hi\nboxer -> boxer: again\n@enduml"
        assert page.evaluate("puml => indentPuml(puml)", sequence) == sequence

    def test_sequence_demo_keeps_its_indentation(self, app_url, page):
        """The demo is written already indented; loading it must not change that."""
        result = page.evaluate("""() => {
            setSequence();
            return editor.getValue();
        }""")
        lines = result.split("\n")
        assert "    participant Participant3" in lines
        assert "        Participant2 -> Participant3: message" in lines
        assert "    else Right-click a group label to add an else" in lines
        assert lines[-1] == "@enduml"


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
