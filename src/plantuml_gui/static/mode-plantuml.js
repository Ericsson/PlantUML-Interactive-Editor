// SPDX-License-Identifier: MIT

// MIT License

// Copyright (c) 2025 Ericsson

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

ace.define("ace/mode/plantuml", [
    "require", "exports", "module", "ace/lib/oop", "ace/mode/text", "ace/tokenizer", "ace/mode/plantuml_highlight_rules", "ace/range"
], function(require, exports) {
    "use strict";

    var oop = require("../lib/oop");
    var TextMode = require("./text").Mode;
    var PlantUMLHighlightRules = require("./plantuml_highlight_rules").PlantUmlHighlightRules;

    var PlantUMLMode = function() {
        this.HighlightRules = PlantUMLHighlightRules;
    };

    oop.inherits(PlantUMLMode, TextMode);

    (function() {
        this.lineCommentStart = "--";
        this.$id = "ace/mode/plantuml";
    }).call(PlantUMLMode.prototype);

    exports.Mode = PlantUMLMode;
});

ace.define("ace/mode/plantuml_highlight_rules", [
    "require", "exports", "ace/lib/oop", "ace/mode/text_highlight_rules"
], function(require, exports) {
    "use strict";

    var oop = require("../lib/oop");
    var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

    var PlantUMLHighlightRules = function() {
        var langKeywords = "(?:autonumber|skinparam|include|ifdef|define|endif)" +
            "|top to bottom|direction|left to right|width|height" +
            "|title|endtitle|note|end note|hide footbox|header|endheader|legend|endlegend|newpage" +
            "|center|footer|scale|autonumber";

        var activityDiagramStyles = [
            "activityArrowColor", "activityArrowFontColor", "activityArrowFontName", "activityArrowFontSize", "activityArrowFontStyle",
            "activityBackgroundColor", "activityBarColor", "activityBorderColor", "activityEndColor", "activityFontColor",
            "activityFontName", "activityFontSize", "activityFontStyle", "activityStartColor"
        ].join("|");

        var classDiagramStyles = [
            "classArrowColor", "classArrowFontColor", "classArrowFontName", "classArrowFontSize", "classArrowFontStyle",
            "classAttributeFontColor", "classAttributeFontName", "classAttributeFontSize", "classAttributeFontStyle", "classAttributeIconSize",
            "classBackgroundColor", "classBorderColor", "classFontColor", "classFontName", "classFontSize", "classFontStyle",
            "classStereotypeFontColor", "classStereotypeFontName", "classStereotypeFontSize", "classStereotypeFontStyle"
        ].join("|");

        var componentDiagramStyles = [
            "componentArrowColor", "componentArrowFontColor", "componentArrowFontName", "componentArrowFontSize", "componentArrowFontStyle",
            "componentBackgroundColor", "componentBorderColor", "componentFontColor", "componentFontName", "componentFontSize", "componentFontStyle",
            "componentInterfaceBackgroundColor", "componentInterfaceBorderColor",
            "componentStereotypeFontColor", "componentStereotypeFontName", "componentStereotypeFontSize", "componentStereotypeFontStyle"
        ].join("|");

        var sequenceDiagramStyles = [
            "sequenceActorBackgroundColor", "sequenceActorBorderColor", "sequenceActorFontColor", "sequenceActorFontName", "sequenceActorFontSize", "sequenceActorFontStyle",
            "sequenceArrowColor", "sequenceArrowFontColor", "sequenceArrowFontName", "sequenceArrowFontSize", "sequenceArrowFontStyle",
            "sequenceDividerBackgroundColor", "sequenceDividerFontColor", "sequenceDividerFontName", "sequenceDividerFontSize", "sequenceDividerFontStyle",
            "sequenceGroupBackgroundColor", "sequenceGroupingFontColor", "sequenceGroupingFontName", "sequenceGroupingFontSize", "sequenceGroupingFontStyle",
            "sequenceGroupingHeaderFontColor", "sequenceGroupingHeaderFontName", "sequenceGroupingHeaderFontSize", "sequenceGroupingHeaderFontStyle",
            "sequenceLifeLineBackgroundColor", "sequenceLifeLineBorderColor",
            "sequenceParticipantBackgroundColor", "sequenceParticipantBorderColor",
            "sequenceParticipantFontColor", "sequenceParticipantFontName", "sequenceParticipantFontSize", "sequenceParticipantFontStyle",
            "sequenceTitleFontColor", "sequenceTitleFontName", "sequenceTitleFontSize", "sequenceTitleFontStyle"
        ].join("|");

        var stateDiagramStyles = [
            "stateArrowColor", "stateArrowFontColor", "stateArrowFontName", "stateArrowFontSize", "stateArrowFontStyle",
            "stateAttributeFontColor", "stateAttributeFontName", "stateAttributeFontSize", "stateAttributeFontStyle",
            "stateBackgroundColor", "stateBorderColor", "stateEndColor",
            "stateFontColor", "stateFontName", "stateFontSize", "stateFontStyle",
            "stateStartColor"
        ].join("|");

        var usecaseDiagramStyles = [
            "usecaseActorBackgroundColor", "usecaseActorBorderColor", "usecaseActorFontColor", "usecaseActorFontName", "usecaseActorFontSize", "usecaseActorFontStyle",
            "usecaseActorStereotypeFontColor", "usecaseActorStereotypeFontName", "usecaseActorStereotypeFontSize", "usecaseActorStereotypeFontStyle",
            "usecaseArrowColor", "usecaseArrowFontColor", "usecaseArrowFontName", "usecaseArrowFontSize", "usecaseArrowFontStyle",
            "usecaseBackgroundColor", "usecaseBorderColor", "usecaseFontColor", "usecaseFontName", "usecaseFontSize", "usecaseFontStyle",
            "usecaseStereotypeFontColor", "usecaseStereotypeFontName", "usecaseStereotypeFontSize", "usecaseStereotypeFontStyle"
        ].join("|");

        var generalStyles = [
            "ActorBackgroundColor", "ActorBorderColor", "ActorFontColor", "ActorFontName", "ActorFontSize", "ActorFontStyle",
            "ArrowColor", "ArrowFontColor", "ArrowFontName", "ArrowFontSize", "ArrowFontStyle",
            "AttributeFontColor", "AttributeFontName", "AttributeFontSize", "AttributeFontStyle", "AttributeIconSize",
            "BackgroundColor", "Color", "BarColor", "BorderColor", "EndColor", "StartColor",
            "FontColor", "FontName", "FontSize", "FontStyle",
            "GroupingFontColor", "GroupingFontName", "GroupingFontSize", "GroupingFontStyle",
            "StereotypeFontColor", "StereotypeFontName", "StereotypeFontSize", "StereotypeFontStyle",
            "TitleFontColor", "TitleFontName", "TitleFontSize", "TitleFontStyle",
            "packageBackgroundColor", "packageBorderColor", "packageFontColor", "packageFontName", "packageFontSize", "packageFontStyle",
            "footerFontColor", "footerFontName", "footerFontSize", "footerFontStyle",
            "headerFontColor", "headerFontName", "headerFontSize", "headerFontStyle",
            "stereotypeABackgroundColor", "stereotypeCBackgroundColor", "stereotypeEBackgroundColor", "stereotypeIBackgroundColor"
        ].join("|");


        var plantFunctions = [
            "actor", "boundary", "control", "entity", "database", "participant", "queue", "collections",
            "alt", "else", "opt", "loop", "par", "break", "critical", "group", "box", "merge",
            "rnote", "hnote", "right", "left", "top", "bottom", "over", "of", "end",
            "activate", "create", "deactivate", "destroy",
            "usecase", "rectangle",
            "start", "stop", "if", "then", "else", "endif", "repeat", "while", "endwhile",
            "fork", "switch", "case", "endswitch", "forkagain", "endfork", "partition", "\\|Swimlane\\w+\\|", "detach",
            "class", "\\{(?:abstract|static|classifier)\\}",
            "abstract", "interface", "annotation", "enum", "hide",
            "hide empty (?:members|attributes|methods|circle|stereotype|fields)",
            "show (?:members|attributes|methods|circle|stereotype|fields)",
            "package(?:<<(?:Node|Rect|Folder|Frame|Cloud|Database)>>)?",
            "namespace", "set\\snamespaceSeparator",
            "package", "node", "folder", "frame", "cloud", "database",
            "\\[\\*\\]", "state", "object"
        ].join("|");

        var constants = "right|left|up|down|over|of|as|is";

        var keywordMapper = this.createKeywordMapper({
            "variable.language": langKeywords,
            "variable.parameter": [
                activityDiagramStyles,
                classDiagramStyles,
                componentDiagramStyles,
                sequenceDiagramStyles,
                stateDiagramStyles,
                usecaseDiagramStyles,
                generalStyles
            ].join("|"),
            "keyword.function": plantFunctions,
            "keyword.constant": constants,
            "support.type": "bool(?:ean)?|string|int(?:eger)?|float|double|(?:var)?char|" +
                "decimal|date|time|timestamp|array|void|none"
        }, "text", true, "|");

        this.$rules = {
            "start": [{
                    token: "string",
                    regex: '"',
                    next: "string"
                },
                {
                    token: "string",
                    regex: ': .*$',
                    next: "start"
                },
                {
                    token: "language.constant",
                    regex: "@startuml|@enduml",
                    next: "start"
                },
                {
                    token: keywordMapper,
                    regex: "\\b\\w+\\b"
                },
                {
                    token: "keyword",
                    regex: /^\\s*:[^\\/;|}{\\n]+[}{;\\\|\\/]$/mi
                },
                {
                    token: "doc.comment",
                    regex: /^'.+/
                },
                {
                    token: "keyword.operator",
                    regex: /(:?[-\/o<]{1,2})?-(:?[-\/o>]{1,2})|(?:<\|--?-?(?:\|>)?)|(?:\.\.?\.?\|?>)/
                },
                {
                    token: "paren.lparen",
                    regex: "[:\\[({]"
                },
                {
                    token: "paren.rparen",
                    regex: "[:\\])}]"
                },
                {
                    caseInsensitive: true
                }
            ],
            "string": [{
                    token: "constant.language.escape",
                    regex: "\\\\"
                },
                {
                    token: "string",
                    regex: '"',
                    next: "start"
                },
                {
                    defaultToken: "string"
                }
            ]
        };
    };

    oop.inherits(PlantUMLHighlightRules, TextHighlightRules);
    exports.PlantUmlHighlightRules = PlantUMLHighlightRules;
});
