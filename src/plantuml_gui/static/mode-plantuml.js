ace.define("ace/mode/plantuml", [
    "require", "exports", "module", "ace/lib/oop", "ace/mode/text", "ace/tokenizer", "ace/mode/plantuml_highlight_rules", "ace/range"
], function(require, exports, module) {
    "use strict";

    var oop = require("../lib/oop");
    var TextMode = require("./text").Mode;
    var Tokenizer = require("../tokenizer").Tokenizer;
    var PlantUMLHighlightRules = require("./plantuml_highlight_rules").PlantUmlHighlightRules;
    var Range = require("../range").Range;

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
    "require", "exports", "module", "ace/lib/oop", "ace/mode/text_highlight_rules"
], function(require, exports, module) {
    "use strict";

    var oop = require("../lib/oop");
    var TextHighlightRules = require("./text_highlight_rules").TextHighlightRules;

    var PlantUMLHighlightRules = function() {
        var langKeywords = "(?:autonumber|skinparam|include|ifdef|define|endif)" +
            "|top to bottom|direction|left to right|width|height" +
            "|title|endtitle|note|end note|hide footbox|header|endheader|legend|endlegend|newpage" +
            "|center|footer|scale|autonumber";

        var skinKeywords = [
            "activityArrowColor", "activityArrowFontColor", "activityArrowFontName",
            "activityArrowFontSize", "activityArrowFontStyle", "activityBackgroundColor",
            "activityBarColor", "activityBorderColor", "activityEndColor", "activityFontColor",
            "activityFontName", "activityFontSize", "activityFontStyle", "activityStartColor",
            "backgroundColor", "circledCharacterFontColor", "circledCharacterFontName",
            "circledCharacterFontSize", "circledCharacterFontStyle", "circledCharacterRadius",
            "classArrowColor", "classArrowFontColor", "classArrowFontName", "classArrowFontSize",
            "classArrowFontStyle", "classAttributeFontColor", "classAttributeFontName",
            "classAttributeFontSize", "classAttributeFontStyle", "classAttributeIconSize",
            "classBackgroundColor", "classBorderColor", "classFontColor", "classFontName",
            "classFontSize", "classFontStyle", "classStereotypeFontColor", "classStereotypeFontName",
            "classStereotypeFontSize", "classStereotypeFontStyle", "componentArrowColor",
            "componentArrowFontColor", "componentArrowFontName", "componentArrowFontSize",
            "componentArrowFontStyle", "componentBackgroundColor", "componentBorderColor",
            "componentFontColor", "componentFontName", "componentFontSize", "componentFontStyle",
            "componentInterfaceBackgroundColor", "componentInterfaceBorderColor",
            "componentStereotypeFontColor", "componentStereotypeFontName",
            "componentStereotypeFontSize", "componentStereotypeFontStyle", "footerFontColor",
            "footerFontName", "footerFontSize", "footerFontStyle", "headerFontColor", "headerFontName",
            "headerFontSize", "headerFontStyle", "noteBackgroundColor", "noteBorderColor",
            "noteFontColor", "noteFontName", "noteFontSize", "noteFontStyle", "packageBackgroundColor",
            "packageBorderColor", "packageFontColor", "packageFontName", "packageFontSize",
            "packageFontStyle", "sequenceActorBackgroundColor", "sequenceActorBorderColor",
            "sequenceActorFontColor", "sequenceActorFontName", "sequenceActorFontSize",
            "sequenceActorFontStyle", "sequenceArrowColor", "sequenceArrowFontColor",
            "sequenceArrowFontName", "sequenceArrowFontSize", "sequenceArrowFontStyle",
            "sequenceDividerBackgroundColor", "sequenceDividerFontColor", "sequenceDividerFontName",
            "sequenceDividerFontSize", "sequenceDividerFontStyle", "sequenceGroupBackgroundColor",
            "sequenceGroupingFontColor", "sequenceGroupingFontName", "sequenceGroupingFontSize",
            "sequenceGroupingFontStyle", "sequenceGroupingHeaderFontColor",
            "sequenceGroupingHeaderFontName", "sequenceGroupingHeaderFontSize",
            "sequenceGroupingHeaderFontStyle", "sequenceLifeLineBackgroundColor",
            "sequenceLifeLineBorderColor", "sequenceParticipantBackgroundColor",
            "sequenceParticipantBorderColor", "sequenceParticipantFontColor",
            "sequenceParticipantFontName", "sequenceParticipantFontSize",
            "sequenceParticipantFontStyle", "sequenceTitleFontColor", "sequenceTitleFontName",
            "sequenceTitleFontSize", "sequenceTitleFontStyle", "stateArrowColor",
            "stateArrowFontColor", "stateArrowFontName", "stateArrowFontSize", "stateArrowFontStyle",
            "stateAttributeFontColor", "stateAttributeFontName", "stateAttributeFontSize",
            "stateAttributeFontStyle", "stateBackgroundColor", "stateBorderColor", "stateEndColor",
            "stateFontColor", "stateFontName", "stateFontSize", "stateFontStyle", "stateStartColor",
            "stereotypeABackgroundColor", "stereotypeCBackgroundColor",
            "stereotypeEBackgroundColor", "stereotypeIBackgroundColor", "titleFontColor",
            "titleFontName", "titleFontSize", "titleFontStyle", "usecaseActorBackgroundColor",
            "usecaseActorBorderColor", "usecaseActorFontColor", "usecaseActorFontName",
            "usecaseActorFontSize", "usecaseActorFontStyle", "usecaseActorStereotypeFontColor",
            "usecaseActorStereotypeFontName", "usecaseActorStereotypeFontSize",
            "usecaseActorStereotypeFontStyle", "usecaseArrowColor", "usecaseArrowFontColor",
            "usecaseArrowFontName", "usecaseArrowFontSize", "usecaseArrowFontStyle",
            "usecaseBackgroundColor", "usecaseBorderColor", "usecaseFontColor", "usecaseFontName",
            "usecaseFontSize", "usecaseFontStyle", "usecaseStereotypeFontColor",
            "usecaseStereotypeFontName", "usecaseStereotypeFontSize", "usecaseStereotypeFontStyle",
            "ActorBackgroundColor", "ActorBorderColor", "ActorFontColor", "ActorFontName",
            "ActorFontSize", "ActorFontStyle", "ActorStereotypeFontColor", "ActorStereotypeFontName",
            "ActorStereotypeFontSize", "ActorStereotypeFontStyle", "ArrowColor", "ArrowFontColor",
            "ArrowFontName", "ArrowFontSize", "ArrowFontStyle", "AttributeFontColor", "AttributeFontName",
            "AttributeFontSize", "AttributeFontStyle", "AttributeIconSize", "BackgroundColor", "BarColor",
            "BorderColor", "CharacterFontColor", "CharacterFontName", "CharacterFontSize",
            "CharacterFontStyle", "CharacterRadius", "Color", "DividerBackgroundColor",
            "DividerFontColor", "DividerFontName", "DividerFontSize", "DividerFontStyle", "EndColor",
            "FontColor", "FontName", "FontSize", "FontStyle", "GroupBackgroundColor", "GroupingFontColor",
            "GroupingFontName", "GroupingFontSize", "GroupingFontStyle", "GroupingHeaderFontColor",
            "GroupingHeaderFontName", "GroupingHeaderFontSize", "GroupingHeaderFontStyle",
            "InterfaceBackgroundColor", "InterfaceBorderColor", "LifeLineBackgroundColor",
            "LifeLineBorderColor", "ParticipantBackgroundColor", "ParticipantBorderColor",
            "ParticipantFontColor", "ParticipantFontName", "ParticipantFontSize",
            "ParticipantFontStyle", "StartColor", "stateArrowColor", "stereotypeABackgroundColor",
            "stereotypeCBackgroundColor", "stereotypeEBackgroundColor", "StereotypeFontColor",
            "StereotypeFontName", "StereotypeFontSize", "StereotypeFontStyle",
            "stereotypeIBackgroundColor", "TitleFontColor", "TitleFontName", "TitleFontSize", "TitleFontStyle"
        ].join("|");

        var plantFunctions = [
            "actor", "boundary", "control", "entity", "database", "participant",
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
            "variable.parameter": skinKeywords,
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
