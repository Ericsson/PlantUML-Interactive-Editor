# Routes

All routes are organized into Blueprints: `shared_bp` (in `shared/routes.py`) for general/render/encode routes, `sequence_bp` (in `sequence/routes.py`) for sequence diagram routes, and `activity_bp` (in `activity/routes.py`) for activity diagram routes. All are mounted at `/`. Unless stated otherwise, every route accepts `Content-Type: application/json` and returns plain text (the modified puml). Routes returning JSON are noted.

## General

- **GET /** — Serves `index.html`. No input. Returns HTML.
- **GET /changelog** — No input. Returns: JSON array of version objects with `version`, `date`, and `entries` (list of strings). Only includes External changelog entries.

## Render

- **POST /render** — Input: `plantuml`. Returns: SVG string.
- **POST /renderPNG** — Input: `plantuml`. Returns: PNG file download (`image/png`).

## Encode / Decode

- **POST /encode** — Input: `plantuml`. Returns: URL-encoded string.
- **POST /decode** — Input: `hash`. Returns: decoded puml text.

## Activity

- **POST /editText** — Input: `plantuml`, `svg`, `newname`, `svgelement`. Returns: modified puml.
- **POST /getText** — Input: `svg`, `svgelement`. Returns: activity text content.
- **POST /deleteActivity** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /addNoteActivity** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /addToActivity** — Input: `plantuml`, `svg`, `type`, `svgelement`. Returns: modified puml.
- **POST /detachActivity** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /breakActivity** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /checkBackward** — Input: `plantuml`, `svg`, `svgelement`. Returns: result text.
- **POST /getActivityPositions** — Input: `plantuml`, `svg`. Returns: JSON with per-type row lists (`activities`, `polys`, `whiles`, `notes`, `groups`, `ellipses`, `connectors`, `merges`, `arrows` — each a list of row-index lists in SVG document order — plus `title`, a single row list). Called once per render so the frontend can highlight the matching diagram element when the editor cursor/hover lands on a line.
- **POST /addArrowLabel** — Input: `plantuml`, `svg`, `where`, `svgelement`. Returns: modified puml.

## If Statements

- **POST /checkWhatPoly** — Input: `plantuml`, `svg`, `svgelement`. Returns: result indicating polygon type.
- **POST /checkIfRepeatHasBackward** — Input: `plantuml`, `svg`, `svgelement`. Returns: result.
- **POST /addBackwards** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /editTextIf** — Input: `plantuml`, `svg`, `statement`, `branch1`, `branch2`, `svgelement`. Returns: modified puml.
- **POST /getTextPoly** — Input: `plantuml`, `svg`, `svgelement`. Returns: polygon text content.
- **POST /delIf** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /switchAgain** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /addToIf** — Input: `plantuml`, `svg`, `svgelement`, `where`, `type`. Returns: modified puml.
- **POST /detachIf** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.

## Ellipses (Start/Stop/End)

- **POST /addToEllipse** — Input: `plantuml`, `svg`, `where`, `type`, `svgelement`. Returns: modified puml.
- **POST /deleteEllipse** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.

## Title

- **POST /addTitle** — Input: `plantuml`. Returns: modified puml.
- **POST /getTextTitle** — Input: `plantuml`. Returns: title text.
- **POST /editTitle** — Input: `plantuml`, `title`. Returns: modified puml.
- **POST /deleteTitle** — Input: `plantuml`. Returns: modified puml.

## Fork

- **POST /deleteFork** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /forkAgain** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /forkToggle** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /forkToggle2** — Input: `plantuml`, `line` (int). Returns: modified puml.
- **POST /deleteFork2** — Input: `plantuml`, `line` (int). Returns: modified puml.
- **POST /addToFork** — Input: `plantuml`, `line` (int), `type`. Returns: modified puml.

## Note

- **POST /getNoteText** — Input: `plantuml`, `svg`, `svgelement`. Returns: note text.
- **POST /editNote** — Input: `plantuml`, `svg`, `text`, `svgelement`. Returns: modified puml.
- **POST /deleteNote** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /noteToggle** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.

## Group

- **POST /getGroupText** — Input: `plantuml`, `svg`, `svgelement`. Returns: group text.
- **POST /editGroup** — Input: `plantuml`, `svg`, `svgelement`, `text`. Returns: modified puml.
- **POST /deleteGroup** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.

## Merge

- **POST /addToMerge** — Input: `plantuml`, `svg`, `svgelement`, `type`. Returns: modified puml.

## While

- **POST /getTextWhile** — Input: `svg`, `svgelement`. Returns: while text.
- **POST /editTextWhile** — Input: `plantuml`, `svg`, `svgelement`, `whilestatement`, `break`, `loop`. Returns: modified puml.
- **POST /delWhile** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /addToWhile** — Input: `plantuml`, `svg`, `svgelement`, `type`, `where`. Returns: modified puml.

## Connector

- **POST /editCharConnector** — Input: `plantuml`, `svg`, `text`, `svgelement`. Returns: modified puml.
- **POST /getCharConnector** — Input: `plantuml`, `svg`, `svgelement`. Returns: connector character.
- **POST /connectorDelete** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /detachConnector** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /addToConnector** — Input: `plantuml`, `svg`, `svgelement`, `where`, `type`. Returns: modified puml.

## Arrow

- **POST /delArrow** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.
- **POST /checkDuplicateArrow** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"result": bool, "type": str}`.
- **POST /getArrowText** — Input: `svg`, `svgelement`. Returns: arrow text.
- **POST /editArrow** — Input: `plantuml`, `svg`, `text`, `svgelement`. Returns: modified puml.

## Sequence Diagram (Participants)

- **POST /addParticipant** — Input: `plantuml`, `svg`, `svgelement`, `direction` ('left'/'right'). Returns: modified puml.
- **POST /addMessage** — Input: `plantuml`, `svg`, `message`, `firstcoordinates` ([x,y]), `secondcoordinates` ([x,y]). Returns: modified puml. Y-coordinate determines insertion position between existing messages.
- **POST /getSequencePositions** — Input: `plantuml`, `svg`. Returns: JSON `{"participants": [{name, cx, yTop, yBottom, index}, ...], "messages": [{cy, index, text}, ...], "notes": [{cy, index}, ...], "groups": [{headerIndex, endIndex}, ...]}`. Called once per render: bundles every sequence element type's position table into a single response so a render costs one round-trip instead of one per type. Each sub-table keeps its own shape (participants carry lifeline bounds, messages/notes carry SVG Y-coordinates) because sequence elements are matched spatially. Powers hover highlighting and the activation/group gestures (which snap to the nearest message and send its line index).
- **POST /getParticipantName** — Input: `plantuml`, `svg`, `svgelement`. Returns: participant name string.
- **POST /editParticipantName** — Input: `plantuml`, `svg`, `name`, `svgelement`. Returns: modified puml.
- **POST /deleteParticipant** — Input: `plantuml`, `svg`, `svgelement`. Returns: modified puml.

## Sequence Diagram (Messages)

- **POST /getMessageText** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"text": message_label}`.
- **POST /editMessageText** — Input: `plantuml`, `svg`, `svgelement`, `text`. Returns: JSON `{"plantuml": modified_puml}`.
- **POST /deleteMessage** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"plantuml": modified_puml}`.

`message`/`text` may contain real newlines (multi-line textarea input); since a message is a single-line puml statement, `addMessage`/`editMessageText` escape newlines to a literal `\n`, and `getMessageText`/`getMessagePositions` unescape `\n` back to real newlines.

## Sequence Diagram (Activation Bars)

- **POST /addActivation** — Input: `plantuml`, `participant`, `startMessageIndex` (int), `endMessageIndex` (int), `endType` ('deactivate'/'destroy'). Returns: JSON `{"plantuml": modified_puml}`. Inserts a matched `activate <participant>` line just after the message at `startMessageIndex` and a closing `deactivate <participant>` (or `destroy <participant>`) line just after the message at `endMessageIndex`. The indexes are puml line numbers; the frontend obtains them from the `messages` table of `/getSequencePositions`. `endType` defaults to 'deactivate' for any value other than 'destroy'.
- **POST /deleteActivation** — Input: `plantuml`, `svg`, `svgelement` (the clicked activation-bar rect). Returns: JSON `{"plantuml": modified_puml}`. Matches the clicked bar to its `activate`/`deactivate`(or `destroy`) pair — by participant, the message above the `activate` line, and nesting level — and removes both lines, leaving nested or sibling bars intact.

## Sequence Diagram (Notes)

- **POST /addNote** — Input: `plantuml`, `svg`, `participant`, `placement` ('over'/'left'/'right'/'spanning'), `text`, `yPosition`, optional `secondParticipant`, optional `noteType` ('note'/'hnote'/'rnote', defaults to 'note' if missing or unrecognized). Returns: JSON `{"plantuml": modified_puml}`. Y-coordinate determines insertion position. All three note types support the same placement grammar identically.
- **POST /getSeqNoteText** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"text": note_text}`.
- **POST /editSeqNote** — Input: `plantuml`, `svg`, `svgelement`, `text`. Returns: JSON `{"plantuml": modified_puml}`.
- **POST /deleteSeqNote** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"plantuml": modified_puml}`.

`text` may contain real newlines (multi-line textarea input); since a note is a single-line puml statement, `addNote`/`editSeqNote` escape newlines to a literal `\n`, and `getSeqNoteText` unescapes `\n` back to real newlines.

## Sequence Diagram (Groups)

- **POST /addGroup** — Input: `plantuml`, `groupType` ('group'/'alt'/'opt'/'loop'), `label`, `startMessageIndex` (int), `endMessageIndex` (int). Returns: JSON `{"plantuml": modified_puml}`. Inserts a `<groupType> <label>` line before the message at the earlier index and an `end` line after the message at the later index. Indexes are puml line numbers obtained from the `messages` table of `/getSequencePositions`. The range is normalized so the order of start/end does not matter. Returns 400 with `{"error": message}` if the group type is invalid.
- **POST /getSeqGroupLabel** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"type": keyword, "label": label_text}`. `svgelement` is the clicked group's box rect (`fill="none"`); named with a `Seq` prefix to avoid colliding with the activity diagram's `/getGroupText`-style routes.
- **POST /renameSeqGroup** — Input: `plantuml`, `svg`, `svgelement`, `label`. Returns: JSON `{"plantuml": modified_puml}`. Replaces only the text after the keyword on the header line; the keyword itself is never changed.
- **POST /deleteSeqGroup** — Input: `plantuml`, `svg`, `svgelement`. Returns: JSON `{"plantuml": modified_puml}`. Unwraps the block: removes the header line and its matching `end` line (nesting-depth tracked), leaving the block's contents in place.
